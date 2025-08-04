#!/bin/bash

bucket_name="ec2-launch-monitor-code"
region="us-east-2"
path_to_lambda="lambda/index.py"

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
cd ..

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


