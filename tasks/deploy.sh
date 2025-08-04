#!/bin/bash
#deploy script for Ec2 Launch Monitor

# Load configuration
if [ -f "config.env" ]; then
    source config.env
    echo "Loaded configuration from config.env"
else
    echo "Warning: config.env not found. Using default values."
    AWS_REGION="us-east-2"
    LAMBDA_CODE_BUCKET="ec2-launch-monitor-code"
    ALLOWED_IP_ADDRESS="0.0.0.0/0"
    STACK_NAME="ec2-launch-monitor"
fi

CODE_KEY="lambda-code.zip"

echo "Deploying CloudFormation stack with the following configuration:"
echo "Region: $AWS_REGION"
echo "Lambda Code Bucket: $LAMBDA_CODE_BUCKET"
echo "Allowed IP: $ALLOWED_IP_ADDRESS"
echo "Stack Name: $STACK_NAME"

#aws cloudformation deploy command
aws cloudformation deploy \
    --template-file cf-template/cloudformation-clean.yaml \
    --stack-name $STACK_NAME \
    --capabilities CAPABILITY_IAM \
    --region $AWS_REGION \
    --parameter-overrides \
        LambdaCodeBucket="$LAMBDA_CODE_BUCKET" \
        LambdaCodeKey="$CODE_KEY" \
        AllowedIPAddress="$ALLOWED_IP_ADDRESS"