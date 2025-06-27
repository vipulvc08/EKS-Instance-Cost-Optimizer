import boto3
import yaml
import os
from datetime import datetime

def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)

def fetch_cheapest_instance(instance_types, region, profile):
    session = boto3.Session(profile_name=profile)
    ec2 = session.client('ec2', region_name=region)
    now = datetime.utcnow()

    print(f"[INFO] Fetching Spot prices in {region} using profile: {profile}")

    response = ec2.describe_spot_price_history(
        InstanceTypes=instance_types,
        ProductDescriptions=['Linux/UNIX'],
        StartTime=now,
        MaxResults=100
    )

    price_map = {}
    for entry in response['SpotPriceHistory']:
        inst = entry['InstanceType']
        price = float(entry['SpotPrice'])
        if inst not in price_map or price < price_map[inst]:
            price_map[inst] = price

    if not price_map:
        print("[WARN] No spot prices found.")
        return None

    cheapest = min(price_map.items(), key=lambda x: x[1])
    print(f"[RESULT] Cheapest instance: {cheapest[0]} at ${cheapest[1]}")
    return cheapest

if __name__ == "__main__":
    config = load_config()
    instance_types = config.get("preferred_instance_types", [])
    region = config.get("region", "us-east-1")
    profile = os.getenv("AWS_PROFILE", "personal")

    if not instance_types:
        print("[ERROR] No instance types specified in config under 'preferred_instance_types'.")
    else:
        fetch_cheapest_instance(instance_types, region, profile)
