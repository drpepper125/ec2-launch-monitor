#!/bin/bash

echo 'Launching EC2 instance with tags for testing the launch monitor...'

# Create EC2 instance with tags for testing the launch monitor
instance_id=$(aws ec2 run-instances \
    --image-id ami-08ca1d1e465fbfe0c \
    --instance-type t2.micro \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=ec2-launch-test2},{Key=adhoc,Value=true}]" \
    --region us-east-2 \
    --count 1 \
    --query 'Instances[0].InstanceId' \
    --output text)

if [ $? -eq 0 ] && [ -n "$instance_id" ]; then
    echo "EC2 instance launched successfully."
    echo "Instance ID: $instance_id"
    
    # Save instance ID to file for cleanup
    echo "$instance_id" > test-instance-id.txt
    echo "Instance ID saved to test-instance-id.txt"
    
    echo "You can check the instance in the AWS Management Console."
    echo "To delete this instance later, run: ./cleanup_ec2.sh"
else
    echo "Failed to launch EC2 instance."
    exit 1
fi
