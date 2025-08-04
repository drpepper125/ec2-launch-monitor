#!/bin/bash

echo 'Cleaning up test EC2 instance...'

# Check if instance ID file exists
if [ ! -f "test-instance-id.txt" ]; then
    echo "Error: test-instance-id.txt not found. No instance to delete."
    echo "Make sure you've run ./create_ec2.sh first."
    exit 1
fi

# Read instance ID from file
instance_id=$(cat test-instance-id.txt)

if [ -z "$instance_id" ]; then
    echo "Error: Instance ID file is empty."
    exit 1
fi

echo "Terminating instance: $instance_id"

# Terminate the EC2 instance
aws ec2 terminate-instances \
    --instance-ids "$instance_id" \
    --region us-east-2 \
    --query 'TerminatingInstances[0].CurrentState.Name' \
    --output text

if [ $? -eq 0 ]; then
    echo "Instance $instance_id termination initiated successfully."
    echo "The instance will be terminated shortly."
    
    # Remove the instance ID file since we're done with it
    rm test-instance-id.txt
    echo "Cleaned up test-instance-id.txt file."
else
    echo "Failed to terminate instance $instance_id."
    echo "You may need to terminate it manually in the AWS Console."
    exit 1
fi
