import boto3
import json
import logging
import requests

client = boto3.client('ec2')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_account_id():
    try:
        sts_client = boto3.client('sts')
        account_id = sts_client.get_caller_identity().get('Account')
        return account_id
    except Exception as e:
        logger.error(f"Error retrieving account ID: {e}")
        return None

def extract_event_details(event):
    try:
        instances: list[dict] = event['detail']['responseElements']['instancesSet']['items']
        instance_ids: list[str] = [instance['instanceId'] for instance in instances]
        return instance_ids
    except KeyError:
        logger.error("Error extracting instance IDs from event")
        return []

def get_instance_details(instance_ids):
    if not instance_ids:
        return []

    try:
        response: dict = client.describe_instances(InstanceIds=instance_ids)
        instances: dict[str, str] = {}
        for reservation in response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                instances[instance['InstanceId']] = instance.get('PrivateIpAddress', 'N/A')
        return instances
    except Exception as e:
        logger.error(f"Error retrieving instance details: {e}")
        return []

def send_post(instances):
    payload: dict = {'account_id': get_account_id(), 'instanceID': [instance['InstanceId'] for instance in instances]}
    # Send the POST request
    response = requests.post("https://your-api-endpoint.com", json=payload)
    return response

def handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    instance_ids = extract_event_details(event)
    logger.info(f"Extracted instance IDs: {instance_ids}")

    instances = get_instance_details(instance_ids)
    logger.info(f"Fetched instance details: {instances}")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'instance_ids': instance_ids,
            'instances': instances
        })
    }
