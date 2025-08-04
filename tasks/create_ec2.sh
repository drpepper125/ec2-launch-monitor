#!/bin/bash

# Default count is 1, but can be overridden
COUNT=${1:-1}

echo "🚀 Launching $COUNT EC2 instance(s) with tags for testing the launch monitor..."
echo ""

# Generate timestamp for unique naming
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Create EC2 instances with dynamic naming
instance_ids=$(aws ec2 run-instances \
    --image-id ami-08ca1d1e465fbfe0c \
    --instance-type t2.micro \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=ec2-test-$TIMESTAMP},{Key=adhoc,Value=true},{Key=TestBatch,Value=$TIMESTAMP}]" \
    --region us-east-2 \
    --count $COUNT \
    --query 'Instances[].InstanceId' \
    --output text)

if [ $? -eq 0 ] && [ -n "$instance_ids" ]; then
    echo "✅ EC2 instance(s) launched successfully!"
    echo ""
    
    # Convert space-separated string to array for processing
    IFS=' ' read -ra INSTANCE_ARRAY <<< "$instance_ids"
    
    echo "📋 Instance Details:"
    for i in "${!INSTANCE_ARRAY[@]}"; do
        instance_id="${INSTANCE_ARRAY[$i]}"
        instance_name="ec2-test-$TIMESTAMP-$((i+1))"
        echo "  Instance $((i+1)): $instance_id (Name: $instance_name)"
    done
    
    # Save all instance IDs to file for cleanup (append mode for multiple runs)
    echo "$instance_ids" >> test-instance-ids.txt
    echo ""
    echo "💾 Instance ID(s) saved to test-instance-ids.txt"
    
    echo ""
    echo "🔍 Next Steps:"
    echo "  1. Check Lambda logs: ./tasks/check_lambda_logs.sh"
    echo "  2. Check S3 reports: ./tasks/check_s3.sh"
    echo "  3. Cleanup instances: ./tasks/cleanup_ec2.sh"
    echo ""
    echo "💡 You can view instances in AWS Console with tag 'TestBatch=$TIMESTAMP'"
else
    echo "❌ Failed to launch EC2 instance(s)."
    exit 1
fi
