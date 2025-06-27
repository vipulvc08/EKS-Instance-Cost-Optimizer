import kopf
import boto3
import yaml
import logging
from datetime import datetime

# Load config
with open("config.yaml") as f:
    config = yaml.safe_load(f)

INSTANCE_TYPES = config['preferred_instance_types']
REGION = config['region']
aws_profile = os.getenv("AWS_PROFILE", "per")
ec2 = boto3.client('ec2', region_name=REGION)

@kopf.timer('eks.spot-controller', interval=300)  # every 5 minutes
def pick_cheapest_spot_instance(**kwargs):
    now = datetime.utcnow()

    print("Checking spot prices...")
    prices = ec2.describe_spot_price_history(
        InstanceTypes=INSTANCE_TYPES,
        ProductDescriptions=['Linux/UNIX'],
        StartTime=now,
        MaxResults=50
    )

    price_map = {}
    for entry in prices['SpotPriceHistory']:
        instance = entry['InstanceType']
        price = float(entry['SpotPrice'])
        if instance not in price_map or price < price_map[instance]:
            price_map[instance] = price

    if not price_map:
        logging.warning("No spot prices available")
        return

    cheapest = min(price_map.items(), key=lambda x: x[1])
    logging.info(f"Cheapest instance type: {cheapest[0]} at ${cheapest[1]}")

    # TODO: Provision EC2 or update ASG with this instance type
