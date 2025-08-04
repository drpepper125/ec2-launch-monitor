#deploy script for Ec2 Launch Monitor
#!/bin/bash

# Configuration - Set these variables for your environment
BUCKET_NAME="ec2-launch-monitor-code"  # Replace with your actual S3 bucket name
CODE_KEY="lambda-code.zip"                  # Replace if you use a different file name

#aws cloudformation deploy command
aws cloudformation deploy \
    --template-file cf-template/cloudformation-clean.yaml \
    --stack-name ec2-launch-monitor \
    --capabilities CAPABILITY_IAM \
    --region us-east-2 \
    --parameter-overrides \
        LambdaCodeBucket="$BUCKET_NAME" \
        LambdaCodeKey="$CODE_KEY"