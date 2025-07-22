import boto3
import json
import logging
from typing import Dict, List, Optional, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients outside handler for connection reuse
ec2_client = boto3.client('ec2')
sts_client = boto3.client('sts')

def get_account_id() -> Optional[str]:
    """Retrieve the current AWS account ID."""
    try:
        account_id = sts_client.get_caller_identity().get('Account')
        return account_id
    except Exception as e:
        logger.error(f"Error retrieving account ID: {e}")
        return None

def extract_event_details(event: Dict[str, Any]) -> List[str]:
    """Extract instance IDs from CloudWatch Events."""
    try:
        instances = event['detail']['responseElements']['instancesSet']['items']
        instance_ids = [instance['instanceId'] for instance in instances]
        logger.info(f"Successfully extracted {len(instance_ids)} instance IDs")
        return instance_ids
    except KeyError as e:
        logger.error(f"Error extracting instance IDs from event - missing key: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error extracting instance IDs: {e}")
        return []

def get_instance_details(instance_ids: List[str]) -> Dict[str, str]:
    """Fetch detailed information for given instance IDs."""
    if not instance_ids:
        logger.warning("No instance IDs provided")
        return {}

    try:
        response = ec2_client.describe_instances(InstanceIds=instance_ids)
        instances = {}
        
        for reservation in response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                instance_id = instance['InstanceId']
                private_ip = instance.get('PrivateIpAddress', 'N/A')
                instances[instance_id] = private_ip
                
        logger.info(f"Successfully fetched details for {len(instances)} instances")
        return instances
        
    except Exception as e:
        logger.error(f"Error retrieving instance details: {e}")
        return {}

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for processing EC2 launch events.
    
    Args:
        event: CloudWatch Events data containing EC2 launch information
        context: Lambda runtime context (unused)
        
    Returns:
        Dict containing status code and response body with instance details
    """
    logger.info(f"Processing EC2 launch event from account: {get_account_id()}")
    
    # Extract instance IDs from the event
    instance_ids = extract_event_details(event)
    if not instance_ids:
        logger.warning("No instance IDs found in event")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'No instance IDs found in event',
                'instance_ids': [],
                'instances': {}
            })
        }
    
    logger.info(f"Processing {len(instance_ids)} instances: {instance_ids}")
    
    # Fetch detailed instance information
    instances = get_instance_details(instance_ids)
    
    # Prepare response
    response_body = {
        'message': f'Successfully processed {len(instance_ids)} EC2 instances',
        'account_id': get_account_id(),
        'instance_ids': instance_ids,
        'instances': instances,
        'processed_count': len(instances)
    }
    
    logger.info(f"Successfully processed event: {json.dumps(response_body)}")
    
    return {
        'statusCode': 200,
        'body': json.dumps(response_body)
    }
