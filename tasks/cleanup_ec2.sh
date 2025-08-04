#!/bin/bash

# Load configuration
if [ -f "config.env" ]; then
    source config.env
    echo "Loaded configuration from config.env"
else
    echo "Warning: config.env not found. Using default values."
    AWS_REGION="us-east-2"
fi

echo 'Cleaning up test EC2 instances...'

# Look for any instance ID files
instance_files=(test-instance-id*.txt)

# Check if any instance ID files exist
if [ ! -e "${instance_files[0]}" ]; then
    echo "No instance ID files found (test-instance-id*.txt)."
    echo "Make sure you've run ./create_ec2.sh first."
    exit 1
fi

# Collect all instance IDs
instance_ids=()
files_to_cleanup=()

for file in "${instance_files[@]}"; do
    if [ -f "$file" ]; then
        files_to_cleanup+=("$file")
        while IFS= read -r line; do
            if [ -n "$line" ]; then
                # Split line by tabs and spaces to handle multiple IDs per line
                for instance_id in $line; do
                    if [ -n "$instance_id" ] && [[ "$instance_id" =~ ^i-[0-9a-f]{8,17}$ ]]; then
                        instance_ids+=("$instance_id")
                    fi
                done
            fi
        done < "$file"
    fi
done

if [ ${#instance_ids[@]} -eq 0 ]; then
    echo "No valid instance IDs found in files."
    exit 1
fi

echo "Found ${#instance_ids[@]} instance(s) to terminate:"
for id in "${instance_ids[@]}"; do
    echo "  - $id"
done

# Terminate all instances
echo ""
echo "Terminating instances..."
aws ec2 terminate-instances \
    --instance-ids "${instance_ids[@]}" \
    --region $AWS_REGION \
    --query 'TerminatingInstances[].{Instance:InstanceId,State:CurrentState.Name}' \
    --output table

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All instances termination initiated successfully."
    echo "The instances will be terminated shortly."
    
    # Remove all instance ID files
    for file in "${files_to_cleanup[@]}"; do
        if [ -f "$file" ]; then
            rm "$file"
            echo "Cleaned up $file"
        fi
    done
    
    echo ""
    echo "Next steps:"
    echo "1. Check CloudWatch Logs for Lambda execution logs"
    echo "2. Run ./check_s3.sh to verify CSV report generation"
    echo "3. Monitor instances in AWS Console to confirm termination"
else
    echo ""
    echo "❌ Failed to terminate some instances."
    echo "You may need to terminate them manually in the AWS Console."
    echo "Instance IDs: ${instance_ids[*]}"
    exit 1
fi
