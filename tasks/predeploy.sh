 #!/bin/bash

bucket_name="ec2-launch-monitor-code"
region="us-east-2"
path_to_lambda="lambda/index.py"
lambda_function_name="ec2-launch-monitor"

#compressing the lambda code to zip format
echo "Compressing Lambda code..."
cd lambda 
zip -r lambda-code.zip *.py
echo "Lambda code compressed to lambda-code.zip"

#uploading the zip file to S3
echo "Uploading Lambda code to S3..."
aws s3 cp lambda-code.zip s3://$bucket_name/lambda-code.zip --region $region
if [ $? -ne 0 ]; then
    echo "Failed to upload Lambda code to S3."
    exit 1
fi

#confirming the upload
aws s3 ls s3://$bucket_name/lambda-code.zip --region $region
if [ $? -ne 0 ]; then
    echo "Lambda code upload confirmation failed."
    exit 1
else
    echo "Lambda code uploaded successfully."
fi

# Update Lambda function to use new code from S3
echo "Updating Lambda function with new code..."
aws lambda update-function-code \
    --function-name $lambda_function_name \
    --s3-bucket $bucket_name \
    --s3-key lambda-code.zip \
    --region $region

if [ $? -ne 0 ]; then
    echo "Failed to update Lambda function code."
    cd ..
    exit 1
else
    echo "Lambda function code updated successfully."
fi

cd ..

# Upload static website files to S3
echo "Uploading static website files to StaticReviewBoardBucket..."

# Define the static website bucket name (this should match your CloudFormation template)
static_bucket_name="static-review-board-$(aws sts get-caller-identity --query Account --output text)-$region"

echo "Static bucket name: $static_bucket_name"

# Upload HTML, CSS, and JS files to root of bucket
echo "Uploading index.html..."
aws s3 cp src/index.html s3://$static_bucket_name/index.html --region $region --content-type "text/html"

echo "Uploading style.css..."
aws s3 cp src/style.css s3://$static_bucket_name/style.css --region $region --content-type "text/css"

echo "Uploading script.js..."
aws s3 cp src/script.js s3://$static_bucket_name/script.js --region $region --content-type "application/javascript"

# Verify uploads
echo "Verifying static website uploads..."
aws s3 ls s3://$static_bucket_name/ --region $region

echo "Static website files uploaded successfully!"

#clean up lambda code 
cd lambda
echo "Cleaning up Lambda code..."
rm -f lambda-code.zip
if lambda-code.zip; then
    echo "Lambda code cleanup successful."
else
    echo "No lambda-code.zip found to clean up."
fi
echo "Lambda code cleanup complete."


