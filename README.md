# TypeScript CDK Project

A serverless AWS infrastructure project built with AWS CDK (Cloud Development Kit) in TypeScript that monitors EC2 instance launches and responds with automated actions.

## 🏗️ Architecture Overview

This project creates an event-driven architecture that:

1. **Monitors EC2 Events**: Uses CloudWatch Events to detect when new EC2 instances are launched
2. **Triggers Lambda Function**: Automatically invokes a Python Lambda function when instances are created
3. **Automated Response**: The Lambda function can perform automated actions like logging, notifications, or compliance checks

## 📁 Project Structure

```
ts_cdk/
├── bin/
│   └── app.ts              # CDK app entry point
├── lib/
│   └── my-stacke.ts        # Main stack definition
├── lambda/
│   └── index.py            # Lambda function code (Python)
├── cdk.json                # CDK configuration
├── config.ts               # Environment configuration (gitignored)
├── event.json              # Sample event data
├── event-pattern.json      # CloudWatch event pattern
├── package.json            # Node.js dependencies
├── tsconfig.json           # TypeScript configuration
└── README.md               # This file
```

## 🚀 What This Project Does

### Infrastructure Components

- **Lambda Function**: Python-based serverless function that processes EC2 launch events with tag filtering
- **CloudWatch Event Rule**: Monitors AWS API calls for EC2 `RunInstances` events
- **IAM Roles & Policies**: Secure permissions for Lambda to access EC2 and CloudWatch Logs

### Lambda Function Details

The Python Lambda function (`lambda/index.py`) performs efficient, single-pass processing:

1. **Event Processing**: Receives CloudWatch Events containing EC2 launch details
2. **Instance ID Extraction**: Parses the event to extract launched instance IDs  
3. **Tag-Based Filtering**: Checks instances for the `adhoc=true` tag in a single AWS API call
4. **Selective Processing**: Only processes instances that have the required tag
5. **Structured Response**: Returns tagged instances with their private IP addresses
6. **Comprehensive Logging**: Detailed CloudWatch logs for monitoring and debugging

#### Lambda Function Capabilities:
- ✅ **Efficient Processing**: Single AWS API call with O(n) complexity
- ✅ **Tag-Based Filtering**: Only processes instances with `adhoc=true` tag
- ✅ **Instance Data**: Returns instance IDs mapped to private IP addresses
- ✅ **Account Context**: Identifies which AWS account triggered the event
- ✅ **Error Handling**: Graceful handling of malformed events or API failures
- ✅ **Performance Optimized**: AWS client reuse for faster Lambda execution
- ✅ **Comprehensive Metrics**: Processing summaries and counts

### Event Flow

1. User launches an EC2 instance via AWS Console, CLI, or API
2. CloudTrail captures the `RunInstances` API call
3. CloudWatch Events rule detects the event pattern
4. Lambda function is triggered automatically with event details
5. Function checks launched instances for the `adhoc=true` tag
6. Returns only tagged instances with their private IP addresses
7. Comprehensive logging in CloudWatch for monitoring and debugging

## 🛠️ Prerequisites

- **Node.js** (v18 or later)
- **AWS CLI** configured with appropriate credentials
- **AWS CDK** installed globally: `npm install -g aws-cdk`
- **Python 3.11** (for Lambda function)

## ⚙️ Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/drpepper125/ts_cdk.git
   cd ts_cdk
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Create configuration file**:
   ```bash
   cp config.ts.example config.ts
   # Edit config.ts with your AWS account details
   ```

4. **Bootstrap CDK** (first time only):
   ```bash
   cdk bootstrap
   ```

## 🚀 Deployment

### Deploy to Development Environment

```bash
# Synthesize CloudFormation template
cdk synth

# Deploy the stack
cdk deploy DevStack

# View deployed resources
cdk diff
```

### Useful CDK Commands

- `cdk ls` - List all stacks
- `cdk synth` - Emit synthesized CloudFormation template
- `cdk deploy` - Deploy stack to AWS
- `cdk diff` - Compare deployed stack with current state
- `cdk destroy` - Remove the stack

## 🧪 Testing

### Lambda Function Code Structure

The Lambda function is organized into efficient, single-purpose functions:

```python
# Core Functions:
- handler(event, context)              # Main entry point with error handling
- extract_event_details(event)         # Parses CloudWatch event for instance IDs
- process_tagged_instances(instance_ids) # Single-pass tag checking and data extraction
- get_account_id()                     # Retrieves current AWS account ID
```

**Sample Success Response:**
```json
{
  "statusCode": 200,
  "body": {
    "message": "Successfully processed 3 instances, found 2 with required tags",
    "account_id": "123456789012",
    "summary": {
      "total_processed": 3,
      "tagged_count": 2,
      "untagged_count": 1
    },
    "tagged_instances": {
      "i-1234567890abcdef0": "10.0.1.25",
      "i-0987654321fedcba0": "10.0.1.26"
    }
  }
}
```

**Sample No Tagged Instances Response:**
```json
{
  "statusCode": 404,
  "body": {
    "error": "No instances found with required adhoc=true tag",
    "summary": {
      "total_processed": 2,
      "tagged_count": 0,
      "untagged_count": 2
    }
  }
}
```
```

### Test Lambda Function Locally

```bash
# Navigate to lambda directory
cd lambda

# Test with sample event
python -c "
import json
from index import handler
with open('../event.json', 'r') as f:
    event = json.load(f)
result = handler(event, {})
print(json.dumps(result, indent=2))
"
```

## 📊 Monitoring & Logs

### CloudWatch Logs
Your Lambda function logs will appear in:
```
/aws/lambda/DevStack-MyLambdaFunction[random-suffix]
```

**Sample Log Output:**
```
[INFO] Processing EC2 launch event from account: 123456789012
[INFO] Successfully extracted 2 instance IDs
[INFO] Processing 2 instances: ['i-123', 'i-456']
[INFO] Found tagged instance i-123 with IP 10.0.1.25
[DEBUG] Skipped untagged instance i-456
[INFO] Processing complete: 1 tagged instances found
```

### What Gets Logged:
- ✅ **Event Processing**: Account ID and instance counts
- ✅ **Tag Checking**: Which instances have required tags
- ✅ **Results**: Summary of tagged vs untagged instances
- ✅ **Errors**: API failures or malformed events

## 🔧 Configuration

### Environment Configuration

The `config.ts` file (gitignored) should contain:

```typescript
export const environments = {
  dev: {
    account: 'YOUR_AWS_ACCOUNT_ID',
    region: 'us-east-1',
    name: 'development'
  },
  prod: {
    account: 'YOUR_AWS_ACCOUNT_ID', 
    region: 'us-east-1',
    name: 'production'
  }
};
```

### Required EC2 Tag

The Lambda function looks for instances with:
- **Tag Key**: `adhoc`
- **Tag Value**: `true`

Only instances with this exact tag will be processed and returned.

### Lambda Function Permissions

The Lambda function has the following permissions:
- `ec2:DescribeInstances` - Query instance details and tags
- `ec2:DescribeInstanceStatus` - Check instance health
- `ec2:DescribeRegions` - Regional information
- `ec2:DescribeAvailabilityZones` - AZ information
- `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` - CloudWatch Logs access

## 🔒 Security Considerations

- **Sensitive Configuration**: All sensitive files (`config.ts`, `event-pattern.json`) are excluded from version control
- **Least-Privilege Access**: Lambda has minimal required permissions for EC2 and CloudWatch
- **Tag-Based Processing**: Only processes instances with specific tags, reducing security exposure
- **Event-Driven**: Only triggers on specific EC2 launch actions, not all EC2 events
- **Resource Tagging**: All AWS resources are tagged for cost tracking and governance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a Pull Request

## 📝 License

This project is licensed under the ISC License - see the package.json file for details.

## 🆘 Troubleshooting

### Common Issues

1. **CDK Bootstrap Error**: Ensure AWS CLI is configured and you have admin permissions
2. **Lambda Permission Denied**: Check IAM roles and policies in the stack
3. **Event Not Triggering**: Verify CloudWatch Events rule pattern matches your use case

### Getting Help

- AWS CDK Documentation: https://docs.aws.amazon.com/cdk/
- AWS Lambda Documentation: https://docs.aws.amazon.com/lambda/
- CloudWatch Events: https://docs.aws.amazon.com/cloudwatch/

---

Built with ❤️ using AWS CDK and TypeScript
