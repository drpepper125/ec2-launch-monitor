#!/bin/bash

# Load configuration
if [ -f "config.env" ]; then
    source config.env
    echo "Loaded configuration from config.env"
else
    echo "Warning: config.env not found. Using default values."
    AWS_REGION="us-east-2"
    STACK_NAME="ec2-launch-monitor"
fi

# Check S3 bucket for CSV reports
# This script retrieves the S3 bucket name from CloudFormation outputs and lists CSV reports

echo "📊 Checking S3 bucket for CSV reports..."

# Get the bucket name from CloudFormation stack outputs
BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`ReportsBucketName`].OutputValue' \
    --output text 2>/dev/null)

if [ "$BUCKET_NAME" != "" ]; then
    echo "Bucket: $BUCKET_NAME"
    echo ""
    
    # Check for today's reports
    echo "--- Today's reports ---"
    TODAY_PATH="ec2-launch-reports/$(date +%Y)/$(date +%m)/"
    
    if aws s3 ls "s3://$BUCKET_NAME/$TODAY_PATH" --recursive --human-readable 2>/dev/null; then
        echo ""
        echo "✅ Found reports for today"
    else
        echo "No reports found for today"
        echo ""
        
        # Check for any reports at all
        echo "--- All reports ---"
        if aws s3 ls "s3://$BUCKET_NAME/ec2-launch-reports/" --recursive --human-readable 2>/dev/null; then
            echo ""
            echo "ℹ️  Reports exist for other dates"
        else
            echo "No reports found in bucket"
            echo ""
            echo "💡 Create a test EC2 instance to generate reports:"
            echo "   ./tasks/create_ec2.sh"
        fi
    fi
else
    echo "❌ Stack not deployed or bucket not found"
    echo ""
    echo "💡 Deploy the stack first:"
    echo "   ./tasks/deploy.sh"
fi