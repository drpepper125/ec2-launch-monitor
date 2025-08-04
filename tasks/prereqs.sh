#!/bin/bash

# Prerequisites Setup Script
# This script handles initial setup requirements before deployment:
# 1. Creates S3 bucket for Lambda code storage
# 2. Packages Lambda function code
# 3. Uploads Lambda package to S3

echo "Setting up deployment prerequisites..."
echo ""

# Load configuration
if [ -f "config.env" ]; then
    source config.env
    echo "Loaded configuration from config.env"
else
    echo "Error: config.env not found!"
    echo ""
    echo "Please create config.env with the following variables:"
    echo "  AWS_REGION=your-aws-region"
    echo "  LAMBDA_CODE_BUCKET=your-unique-bucket-name"
    echo "  ALLOWED_IP_ADDRESS=your.ip.address/32"
    echo "  STACK_NAME=ec2-launch-monitor"
    echo ""
    echo "You can copy from the template:"
    echo "   cp config.env config.env.local"
    exit 1
fi

# Validate required variables
if [ -z "$AWS_REGION" ] || [ -z "$LAMBDA_CODE_BUCKET" ]; then
    echo "Error: Missing required configuration variables"
    echo "Required: AWS_REGION, LAMBDA_CODE_BUCKET"
    exit 1
fi

echo "Configuration:"
echo "  AWS Region: $AWS_REGION"
echo "  Lambda Code Bucket: $LAMBDA_CODE_BUCKET"
echo ""

# Step 1: Create S3 bucket for Lambda code
echo "Creating S3 bucket for Lambda code..."
if aws s3 ls "s3://$LAMBDA_CODE_BUCKET" 2>/dev/null; then
    echo "Bucket '$LAMBDA_CODE_BUCKET' already exists"
else
    echo "Creating bucket '$LAMBDA_CODE_BUCKET' in region '$AWS_REGION'..."
    
    # Create bucket with region-specific configuration
    if [ "$AWS_REGION" = "us-east-1" ]; then
        # us-east-1 doesn't need LocationConstraint
        aws s3 mb "s3://$LAMBDA_CODE_BUCKET" --region "$AWS_REGION"
    else
        # Other regions need LocationConstraint
        aws s3api create-bucket \
            --bucket "$LAMBDA_CODE_BUCKET" \
            --region "$AWS_REGION" \
            --create-bucket-configuration LocationConstraint="$AWS_REGION"
    fi
    
    if [ $? -eq 0 ]; then
        echo "Successfully created bucket '$LAMBDA_CODE_BUCKET'"
    else
        echo "Failed to create bucket '$LAMBDA_CODE_BUCKET'"
        echo "Make sure the bucket name is globally unique and you have S3 permissions"
        exit 1
    fi
fi

echo ""

# Step 2: Package Lambda function code
echo "Packaging Lambda function..."

# Create temporary directory for packaging
TEMP_DIR=$(mktemp -d)
echo "Using temporary directory: $TEMP_DIR"

# Copy Lambda files to temp directory
cp lambda/index.py "$TEMP_DIR/"
cp lambda/ec2_helper.py "$TEMP_DIR/"

# Create ZIP package
cd "$TEMP_DIR"
zip -r lambda-code.zip index.py ec2_helper.py

if [ $? -eq 0 ]; then
    echo "Lambda function packaged successfully"
else
    echo "Failed to package Lambda function"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Return to original directory
cd - > /dev/null

echo ""

# Step 3: Upload Lambda package to S3
echo "Uploading Lambda package to S3..."

# Also upload with a standard name for CloudFormation
aws s3 cp "$TEMP_DIR/lambda-codqe.zip" "s3://$LAMBDA_CODE_BUCKET/lambda-codqe.zip" --region "$AWS_REGION"

if [ $? -eq 0 ]; then
    echo "Lambda package uploaded as lambda-codqe.zip (for CloudFormation)"
else
    echo "Failed to upload standard Lambda package"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Cleanup temp directory
rm -rf "$TEMP_DIR"
echo ""

# Step 4: Verify setup
echo "Verifying setup..."
echo ""

# Check bucket contents
echo "Lambda code bucket contents:"
aws s3 ls "s3://$LAMBDA_CODE_BUCKET/" --human-readable --region "$AWS_REGION"

echo ""
echo "Prerequisites setup complete!"
echo ""
echo "Next steps:"
echo "1. Review and update config.env if needed"
echo "2. Run: ./tasks/deploy.sh (to deploy infrastructure)"
echo "3. Run: ./tasks/create_ec2.sh (to test the system)"
echo ""
echo "To update Lambda code later, use: ./tasks/predeploy.sh"
