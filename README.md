# EC2 Launch Monitor

> ⚠️ **Work in Progress** - This is an MVP implementation for monitoring EC2 instance launches with specific tags.

## Overview

The EC2 Launch Monitor is a serverless solution that automatically detects when EC2 instances are launched in your AWS account and processes instances that have specific tags (`adhoc=true`). This is designed for platform engineering teams to track and monitor adhoc infrastructure deployments.

## Architecture

```
EC2 Launch → CloudTrail → EventBridge → Lambda Function → Data Processing
                                            ↓
                                    CloudWatch Logs + CSV Export
```

- **CloudTrail**: Captures EC2 `RunInstances` API calls
- **EventBridge**: Filters and routes EC2 launch events
- **Lambda Function**: Processes events and extracts tagged instance details
- **Data Export**: Comprehensive instance information for reporting

## What This Solution Does

1. **Detects EC2 Launches**: Automatically triggers when new EC2 instances are launched
2. **Filters by Tags**: Only processes instances with `adhoc=true` tag
3. **Collects Metadata**: Gathers comprehensive instance information including:
   - Instance details (ID, type, state, launch time)
   - Network configuration (VPC, subnet, IPs, security groups)
   - All instance tags for compliance tracking
4. **Exports Data**: Converts instance data to CSV format for reporting
5. **Logging**: Provides structured logging for monitoring and debugging

## Repository Structure

```
ec2-launch-monitor/
├── cloudformation-clean.yaml       # Infrastructure as Code template
├── lambda/
│   └── index.py                   # Main Lambda function code
├── convertcsv.py                  # Utility for CSV data export
├── deploy.sh                      # Deployment automation script
├── update-lambda-code.sh          # Quick Lambda code updates
├── create_ec2.sh                  # Test instance creation script
├── cleanup_ec2.sh                 # Test instance cleanup script
├── .vscode/
│   └── tasks.json                 # VS Code development tasks
└── mock_response_data.json        # Sample response data for development
```

## Current Status

### ✅ Completed
- [x] CloudFormation template with Lambda, IAM, EventBridge configuration
- [x] Lambda function with comprehensive instance data collection
- [x] Event filtering for `adhoc=true` tagged instances
- [x] CSV export functionality for data analysis
- [x] Development and testing automation scripts
- [x] VS Code task integration for streamlined workflow
- [x] Refactored architecture with reusable business logic


## Quick Start

### Prerequisites
- AWS CLI configured with appropriate permissions
- Bash shell (macOS/Linux)
- Python 3.x for local development

### Deployment

1. **Deploy Infrastructure**:
   ```bash
   ./deploy.sh
   ```

2. **Test the System**:
   ```bash
   # Create a test EC2 instance with adhoc=true tag
   ./create_ec2.sh
   
   # Check Lambda logs
   # Clean up test resources
   ./cleanup_ec2.sh
   ```

3. **Update Lambda Code** (during development):
   ```bash
   ./update-lambda-code.sh
   ```

### Development Workflow

Using VS Code tasks (Ctrl/Cmd + Shift + P → "Tasks: Run Task"):

1. **Full Development Cycle**: Deploy → Test → Monitor → Cleanup
2. **Quick Deploy**: Fast infrastructure deployment
3. **Lambda Update**: Update only Lambda code
4. **Test Instance**: Create tagged test instance
5. **Monitor Logs**: Watch Lambda execution logs
6. **Cleanup**: Remove test resources

## Configuration

### Environment Variables
- `LAMBDA_FUNCTION_NAME`: Name of the Lambda function (set in CloudFormation)
- `TAG_KEY`: Tag key to filter instances (default: "adhoc")
- `TAG_VALUE`: Tag value to match (default: "true")

### CloudFormation Parameters
- `LambdaBucketName`: S3 bucket for Lambda deployment package
- `LambdaKey`: S3 object key for Lambda code zip file

## Data Format

The Lambda function returns structured data for each tagged instance:

```json
{
  "status": "success",
  "summary": {
    "total_processed": 3,
    "tagged_count": 2,
    "untagged_count": 1
  },
  "tagged_instances": {
    "i-1234567890abcdef0": {
      "instance_id": "i-1234567890abcdef0",
      "private_ip": "10.0.1.100",
      "public_ip": "54.123.45.67",
      "instance_type": "t3.micro",
      "state": "running",
      "launch_time": "2025-08-04T15:30:00+00:00",
      "availability_zone": "us-east-1a",
      "vpc_id": "vpc-12345678",
      "subnet_id": "subnet-87654321",
      "security_groups": ["default", "web-server"],
      "key_name": "my-key-pair",
      "tags": {
        "adhoc": "true",
        "Name": "Development Server",
        "Environment": "dev",
        "Owner": "user@company.com"
      }
    }
  }
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

