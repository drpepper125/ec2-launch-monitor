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

def process_tagged_instances(instance_ids: List[str]) -> Dict[str, Any]:
    """
    Process all instances in a single pass - check tags and return tagged instances.
    Returns instance IDs and private IPs for instances with the required tag.
    """
    tag_key = 'adhoc'
    tag_value = 'true'
    
    result = {
        'tagged_instances': {},  # {instance_id: private_ip}
        'summary': {
            'total_processed': 0,
            'tagged_count': 0,
            'untagged_count': 0
        }
    }
    
    if not instance_ids:
        logger.warning("No instance IDs provided")
        return result
    
    try:
        response = ec2_client.describe_instances(InstanceIds=instance_ids)
        
        for reservation in response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                instance_id = instance['InstanceId']
                private_ip = instance.get('PrivateIpAddress', 'N/A')
                tags = instance.get('Tags', [])
                
                result['summary']['total_processed'] += 1
                
                # Check if instance has the required tag
                has_required_tag = any(
                    tag['Key'] == tag_key and tag['Value'] == tag_value 
                    for tag in tags
                )
                
                if has_required_tag:
                    # Store tagged instance: ID -> Private IP
                    result['tagged_instances'][instance_id] = private_ip
                    result['summary']['tagged_count'] += 1
                    
                    logger.info(f"Found tagged instance {instance_id} with IP {private_ip}")
                else:
                    result['summary']['untagged_count'] += 1
                    logger.debug(f"Skipped untagged instance {instance_id}")
        
        logger.info(f"Processing complete: {result['summary']['tagged_count']} tagged instances found")
        return result
        
    except Exception as e:
        logger.error(f"Error processing instances: {e}")
        return result

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
                'tagged_instances': {}
            })
        }
    
    logger.info(f"Processing {len(instance_ids)} instances: {instance_ids}")
    
    # Process all instances in a single efficient pass
    processing_result = process_tagged_instances(instance_ids)
    
    # Check if we found any tagged instances
    if processing_result['summary']['tagged_count'] == 0:
        logger.warning("No instances found with required tags")
        return {
            'statusCode': 404,
            'body': json.dumps({
                'error': 'No instances found with required adhoc=true tag',
                'summary': processing_result['summary']
            })
        }
    
    # Prepare response with all the processed data
    response_body = {
        'message': f"Successfully processed {processing_result['summary']['total_processed']} instances, found {processing_result['summary']['tagged_count']} with required tags",
        'account_id': get_account_id(),
        'summary': processing_result['summary'],
        'tagged_instances': processing_result['tagged_instances']
    }
    
    logger.info(f"Successfully processed event: {json.dumps(response_body)}")
    
    return {
        'statusCode': 200,
        'body': json.dumps(response_body)
    }
