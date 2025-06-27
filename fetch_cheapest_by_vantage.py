import requests
import yaml

BURSTABLE_FAMILIES = ["t2", "t3", "t3a", "t4g"]

def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)

def fetch_vantage_data():
    url = "https://instances.vantage.sh/instances.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def is_burstable(instance_type):
    return any(instance_type.startswith(fam + ".") for fam in BURSTABLE_FAMILIES)

def find_cheapest_instance(data, region, min_cpu, max_cpu, include_burstable):
    filtered = []
    for instance in data:
        vcpus = instance.get("vCPU", 0)
        price = instance.get("pricing", {}).get(region, {}).get("linux", {}).get("ondemand", None)

        if price is None:
            continue

        if not include_burstable and is_burstable(instance["instance_type"]):
            continue

        if min_cpu <= vcpus <= max_cpu:
            filtered.append({
                "type": instance["instance_type"],
                "vcpus": vcpus,
                "price": float(price)
            })

    if not filtered:
        print("[WARN] No matching instances found.")
        return

    cheapest = sorted(filtered, key=lambda x: x["price"])[0]
    print(f"[RESULT] Cheapest instance: {cheapest['type']} with {cheapest['vcpus']} vCPUs at ${cheapest['price']}")
    return cheapest

if __name__ == "__main__":
    config = load_config()
    region = config.get("region", "us-east-1")
    min_cpu = config.get("min_cpu", 2)
    max_cpu = config.get("max_cpu", 4)
    include_burstable = config.get("include_burstable", False)

    print(f"[INFO] Fetching instance data from vantage.sh...")
    data = fetch_vantage_data()

    find_cheapest_instance(data, region, min_cpu, max_cpu, include_burstable)
