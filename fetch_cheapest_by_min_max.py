import boto3
import yaml
import os
from datetime import datetime

def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)

def get_instance_types_in_cpu_range(ec2, min_cpu, max_cpu, include_burstable):
    matching_types = []
    next_token = None

    burstable_prefixes = ['t2.', 't3.', 't3a.', 't4g.']

    while True:
        kwargs = {"MaxResults": 100}
        if next_token:
            kwargs["NextToken"] = next_token

        response = ec2.describe_instance_types(**kwargs)

        for itype in response["InstanceTypes"]:
            instance_type = itype["InstanceType"]
            vcpus = itype["VCpuInfo"]["DefaultVCpus"]

            if not include_burstable and any(instance_type.startswith(prefix) for prefix in burstable_prefixes):
                continue

            if min_cpu <= vcpus <= max_cpu:
                matching_types.append(instance_type)

        next_token = response.get("NextToken")
        if not next_token:
            break

    return matching_types

def fetch_cheapest_instance(region, profile, min_cpu, max_cpu, include_burstable):
    session = boto3.Session(profile_name=profile)
    ec2 = session.client('ec2', region_name=region)
    now = datetime.utcnow()

    if config.get("preferred_instance_types"):
        print("[WARN] 'preferred_instance_types' is defined but ignored in fetch_by_cpu.py")

    print(f"[INFO] Fetching instance types in CPU range: {min_cpu}-{max_cpu} | Include burstable: {include_burstable}")
    instance_types = get_instance_types_in_cpu_range(ec2, min_cpu, max_cpu, include_burstable)

    if not instance_types:
        print("[WARN] No matching instance types found")
        return

    print(f"[INFO] Found {len(instance_types)} instance types, checking Spot prices...")

    prices = ec2.describe_spot_price_history(
        InstanceTypes=instance_types,
        ProductDescriptions=["Linux/UNIX"],
        StartTime=now,
        MaxResults=200
    )

    price_map = {}
    for entry in prices["SpotPriceHistory"]:
        itype = entry["InstanceType"]
        price = float(entry["SpotPrice"])
        if itype not in price_map or price < price_map[itype]:
            price_map[itype] = price

    if not price_map:
        print("[WARN] No spot price data found")
        return

    cheapest = min(price_map.items(), key=lambda x: x[1])
    print(f"[RESULT] Cheapest instance: {cheapest[0]} with {min_cpu}-{max_cpu} vCPUs at ${cheapest[1]}")
    return cheapest

if __name__ == "__main__":
    config = load_config()
    region = config.get("region", "us-east-1")
    min_cpu = config.get("min_cpu", 2)
    max_cpu = config.get("max_cpu", 4)
    include_burstable = config.get("include_burstable", False)
    profile = os.getenv("AWS_PROFILE", "personal")

    fetch_cheapest_instance(region, profile, min_cpu, max_cpu, include_burstable)
