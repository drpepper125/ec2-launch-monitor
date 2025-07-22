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

- **Lambda Function**: Python-based serverless function that processes EC2 launch events
- **CloudWatch Event Rule**: Monitors AWS API calls for EC2 `RunInstances` events
- **IAM Roles & Policies**: Secure permissions for Lambda to access EC2 and CloudWatch Logs

### Lambda Function Details

The Python Lambda function (`lambda/index.py`) performs the following operations when triggered:

1. **Event Processing**: Receives CloudWatch Events containing EC2 launch details
2. **Instance ID Extraction**: Parses the event to extract launched instance IDs
3. **Instance Detail Retrieval**: Uses AWS EC2 API to fetch detailed information about the instances
4. **Account Context**: Retrieves the AWS account ID for context
5. **Structured Logging**: Logs all operations for monitoring and debugging
6. **Response Formation**: Returns structured data with instance IDs and details

#### Lambda Function Capabilities:
- ✅ **Event Parsing**: Extracts instance IDs from CloudWatch Events
- ✅ **EC2 API Integration**: Fetches instance details (IP addresses, metadata)
- ✅ **Account Identification**: Determines which AWS account triggered the event
- ✅ **Error Handling**: Graceful handling of malformed events or API failures
- ✅ **Structured Logging**: Comprehensive logging for troubleshooting
- ✅ **JSON Response**: Returns structured data for downstream processing

### Event Flow

1. User launches an EC2 instance via AWS Console, CLI, or API
2. CloudTrail captures the `RunInstances` API call
3. CloudWatch Events rule detects the event pattern
4. Lambda function is triggered automatically with event details
5. Function extracts instance IDs and fetches detailed information
6. Logs activity and returns structured response for monitoring

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

The Lambda function is organized into several helper functions:

```python
# Core Functions:
- handler(event, context)           # Main entry point
- extract_event_details(event)      # Parses CloudWatch event for instance IDs
- get_instance_details(instance_ids) # Fetches EC2 instance information
- get_account_id()                  # Retrieves current AWS account ID
```

**Sample Response Structure:**
```json
{
  "statusCode": 200,
  "body": {
    "instance_ids": ["i-1234567890abcdef0"],
    "instances": {
      "i-1234567890abcdef0": "10.0.1.25"
    }
  }
}
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

### Test Event Pattern

The `event-pattern.json` file contains the CloudWatch Events pattern used to filter EC2 launch events.

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

### Lambda Function Permissions

The Lambda function has the following permissions:
- `ec2:RunInstances` - Monitor instance launches
- `ec2:Describe*` - Query instance details
- `logs:*` - Write to CloudWatch Logs

## 📊 Monitoring & Logs

- **CloudWatch Logs**: Lambda execution logs available in `/aws/lambda/DevStack-MyLambdaFunction*`
- **CloudWatch Events**: Monitor event rule metrics in CloudWatch console
- **X-Ray Tracing**: Can be enabled for detailed Lambda performance insights

## 🔒 Security Considerations

- Sensitive configuration is excluded from version control
- Lambda follows least-privilege access principles
- CloudWatch Events only trigger on specific EC2 actions
- All resources are tagged for cost tracking and governance

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
