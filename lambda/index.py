import boto3
import json
import logging
import os
from datetime import datetime
from io import StringIO
import csv
from typing import Dict, List, Optional, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients outside handler for connection reuse
ec2_client = boto3.client('ec2')
sts_client = boto3.client('sts')
s3_client = boto3.client('s3')

# Configuration - get from environment variables
REPORTS_BUCKET = os.environ.get('REPORTS_BUCKET', 'ec2-launch-reports-default')

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
    Returns comprehensive instance information for instances with the required tag.
    """
    tag_key = 'adhoc'
    tag_value = 'true'
    
    result = {
        'tagged_instances': {},  # {instance_id: instance_details}
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
                tags = instance.get('Tags', [])
                
                result['summary']['total_processed'] += 1
                
                # Check if instance has the required tag
                has_required_tag = any(
                    tag['Key'] == tag_key and tag['Value'] == tag_value 
                    for tag in tags
                )
                
                if has_required_tag:
                    # Collect comprehensive instance information
                    instance_details = {
                        'instance_id': instance_id,
                        'private_ip': instance.get('PrivateIpAddress', 'N/A'),
                        'public_ip': instance.get('PublicIpAddress', 'N/A'),
                        'instance_type': instance.get('InstanceType', 'Unknown'),
                        'state': instance.get('State', {}).get('Name', 'Unknown'),
                        'launch_time': instance.get('LaunchTime').isoformat() if instance.get('LaunchTime') else 'N/A',
                        'availability_zone': instance.get('Placement', {}).get('AvailabilityZone', 'N/A'),
                        'vpc_id': instance.get('VpcId', 'N/A'),
                        'subnet_id': instance.get('SubnetId', 'N/A'),
                        'security_groups': [sg['GroupName'] for sg in instance.get('SecurityGroups', [])],
                        'key_name': instance.get('KeyName', 'N/A'),
                        'tags': {tag['Key']: tag['Value'] for tag in tags}
                    }
                    
                    result['tagged_instances'][instance_id] = instance_details
                    result['summary']['tagged_count'] += 1
                    
                    logger.info(f"Found tagged instance {instance_id} ({instance_details['instance_type']}) with IP {instance_details['private_ip']}")
                else:
                    result['summary']['untagged_count'] += 1
                    logger.debug(f"Skipped untagged instance {instance_id}")
        
        logger.info(f"Processing complete: {result['summary']['tagged_count']} tagged instances found")
        return result
        
    except Exception as e:
        logger.error(f"Error processing instances: {e}")
        return result

def store_to_s3_csv(response_data: Dict[str, Any]) -> Optional[str]:
    """Store instance data as CSV in S3 for daily reporting - one file per day."""
    if response_data.get('status') != 'success':
        logger.info("Skipping S3 storage - no successful data to store")
        return None
    
    tagged_instances = response_data.get('tagged_instances', {})
    if not tagged_instances:
        logger.info("Skipping S3 storage - no tagged instances found")
        return None
    
    try:
        # Flatten instance data for CSV
        instances_data = []
        for instance_id, instance_details in tagged_instances.items():
            # Flatten the data structure
            instance_record = instance_details.copy()
            instance_record['security_groups'] = ', '.join(instance_details.get('security_groups', []))
            
            # Flatten tags into separate columns
            tags = instance_details.get('tags', {})
            for tag_key, tag_value in tags.items():
                instance_record[f'tag_{tag_key}'] = tag_value
            
            # Remove nested tags dict and add processing timestamp
            instance_record.pop('tags', None)
            instance_record['processed_at'] = datetime.utcnow().isoformat()
            
            instances_data.append(instance_record)
        
        # Generate daily S3 key (one file per day)
        timestamp = datetime.utcnow()
        account_id = response_data.get('account_id', 'unknown')
        s3_key = f"ec2-launch-reports/{timestamp.year}/{timestamp.month:02d}/ec2-instances-{account_id}-{timestamp.strftime('%Y-%m-%d')}.csv"
        
        # Check if daily file already exists
        existing_csv_content = ""
        file_exists = False
        try:
            existing_object = s3_client.get_object(Bucket=REPORTS_BUCKET, Key=s3_key)
            existing_csv_content = existing_object['Body'].read().decode('utf-8')
            file_exists = True
            logger.info(f"Found existing daily CSV file: {s3_key}")
        except s3_client.exceptions.NoSuchKey:
            logger.info(f"Creating new daily CSV file: {s3_key}")
        except Exception as e:
            logger.warning(f"Error checking existing file: {e}, creating new file")
        
        # Determine fieldnames
        all_fieldnames = set()
        for row in instances_data:
            all_fieldnames.update(row.keys())
        
        # If file exists, extract existing headers to maintain consistency
        if file_exists and existing_csv_content:
            existing_lines = existing_csv_content.strip().split('\n')
            if existing_lines:
                existing_headers = existing_lines[0].split(',')
                # Clean headers (remove quotes if present)
                existing_headers = [h.strip('"') for h in existing_headers]
                all_fieldnames.update(existing_headers)
        
        fieldnames = sorted(list(all_fieldnames))
        
        # Create new CSV content
        csv_buffer = StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
        
        if file_exists and existing_csv_content:
            # Append mode: don't write header, just add the new rows
            csv_buffer.write(existing_csv_content.rstrip('\n') + '\n')  # Ensure no extra newline
            for row in instances_data:
                writer.writerow(row)
        else:
            # New file mode: write header and data
            writer.writeheader()
            for row in instances_data:
                writer.writerow(row)
        
        # Upload updated CSV to S3
        s3_client.put_object(
            Bucket=REPORTS_BUCKET,
            Key=s3_key,
            Body=csv_buffer.getvalue(),
            ContentType='text/csv',
            Metadata={
                'account_id': account_id,
                'report_type': 'ec2_launch_monitor_daily',
                'last_updated': timestamp.isoformat(),
                'total_instances_added': str(len(instances_data))
            }
        )
        
        action = "Appended to" if file_exists else "Created"
        logger.info(f"{action} daily CSV: s3://{REPORTS_BUCKET}/{s3_key} (+{len(instances_data)} instances)")
        return s3_key
        
    except Exception as e:
        logger.error(f"Error storing CSV to S3: {e}")
        return None

def process_ec2_launch_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Core business logic for processing EC2 launch events.
    This function can be reused by other components (future Lambda functions, tests, etc.)
    
    Args:
        event: CloudWatch Events data containing EC2 launch information
        
    Returns:
        Dict with status, message, and processed instance data
    """
    logger.info(f"Processing EC2 launch event from account: {get_account_id()}")
    
    # Extract instance IDs from the event
    instance_ids = extract_event_details(event)
    if not instance_ids:
        logger.warning("No instance IDs found in event")
        return {
            'status': 'error',
            'error': 'No instance IDs found in event',
            'instance_ids': [],
            'tagged_instances': {},
            'summary': {'total_processed': 0, 'tagged_count': 0, 'untagged_count': 0}
        }
    
    logger.info(f"Processing {len(instance_ids)} instances: {instance_ids}")
    
    # Process all instances in a single efficient pass
    processing_result = process_tagged_instances(instance_ids)
    
    # Check if we found any tagged instances
    if processing_result['summary']['tagged_count'] == 0:
        logger.warning("No instances found with required tags")
        return {
            'status': 'no_matches',
            'error': 'No instances found with required adhoc=true tag',
            'summary': processing_result['summary'],
            'tagged_instances': {}
        }
    
    # Prepare successful response with all the processed data
    response_data = {
        'status': 'success',
        'message': f"Successfully processed {processing_result['summary']['total_processed']} instances, found {processing_result['summary']['tagged_count']} with required tags",
        'account_id': get_account_id(),
        'summary': processing_result['summary'],
        'tagged_instances': processing_result['tagged_instances']
    }
    
    # Log summary instead of full response to avoid log bloat
    logger.info(f"Successfully processed event - Account: {response_data['account_id']}, "
               f"Found {processing_result['summary']['tagged_count']} tagged instances: "
               f"{list(processing_result['tagged_instances'].keys())}")
    
    # Store data to S3 for daily reporting
    s3_key = store_to_s3_csv(response_data)
    if s3_key:
        response_data['s3_report'] = s3_key
    
    return response_data

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler - thin wrapper around business logic.
    Handles Lambda-specific response formatting.
    
    Args:
        event: CloudWatch Events data containing EC2 launch information
        context: Lambda runtime context (unused)
        
    Returns:
        Dict containing status code and response body with instance details
    """
    # Call the core business logic
    result = process_ec2_launch_event(event)
    
    # Map business logic status to HTTP status codes
    status_code_map = {
        'success': 200,
        'error': 400,
        'no_matches': 404
    }
    
    status_code = status_code_map.get(result['status'], 500)
    
    return {
        'statusCode': status_code,
        'body': json.dumps(result)
    }
