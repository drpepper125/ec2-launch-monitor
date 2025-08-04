# EC2 Launch Monitor

> **Platform Engineering Solution** - Automated monitoring and reporting of EC2 instance launches with intelligent tagging and daily CSV exports.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [AWS Resources](#aws-resources)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Data Flow](#data-flow)
- [Configuration](#configuration)
- [Testing](#testing)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Overview

The EC2 Launch Monitor is a serverless platform engineering solution that automatically tracks EC2 instance launches across your AWS account. It provides real-time monitoring, comprehensive data collection, and daily CSV reporting for business stakeholders and compliance teams.

**Key Benefits:**
- **Zero Infrastructure Management**: Fully serverless architecture
- **Cost Effective**: Pay-per-execution with minimal resource usage
- **Business Intelligence**: Daily CSV reports for stakeholder visibility
- **Compliance Ready**: Comprehensive metadata collection and audit trails
- **Developer Friendly**: Complete development automation and testing suite

## Architecture

```
[PLACEHOLDER: AWS Architecture Diagram - To be created in Draw.io]

Components Flow:
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│   EC2 API   │───▶│ CloudTrail   │───▶│ EventBridge │───▶│   Lambda     │
│ RunInstances│    │   Events     │    │    Rule     │    │  Function    │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
                                                                   │
                   ┌─────────────┐    ┌──────────────┐            │
                   │ CloudWatch  │◀───│   S3 Bucket  │◀───────────┘
                   │    Logs     │    │ Daily CSV    │
                   └─────────────┘    │   Reports    │
                                      └──────────────┘

Data Pipeline:
1. EC2 Instance Launch → CloudTrail captures API call
2. EventBridge filters for EC2 launch events
3. Lambda processes event and extracts metadata
4. Instance tags filtered for monitoring scope
5. Comprehensive data collection and validation
6. Daily CSV export to S3 with append functionality
7. Structured logging to CloudWatch for monitoring
```

## Features

### Core Functionality
- **Real-time Detection**: Instant EC2 launch event processing
- **Intelligent Filtering**: Tag-based instance selection (`adhoc=true`)
- **Comprehensive Metadata**: Complete instance, network, and tag information
- **Daily Reporting**: Automated CSV exports to S3 with date-based organization
- **Error Handling**: Robust error handling with detailed logging

### Data Collection
The system captures extensive instance metadata:
- **Instance Details**: ID, type, state, launch time, AMI ID
- **Network Configuration**: VPC, subnet, public/private IPs, security groups
- **Infrastructure Context**: Availability zone, key pair, placement group
- **Complete Tag Inventory**: All instance tags for compliance and categorization
- **Timestamps**: Precise event timing for audit trails

### Business Intelligence
- **Daily CSV Reports**: Stakeholder-friendly data exports
- **S3 Storage**: Organized by date hierarchy (`YYYY/MM/DD/report.csv`)
- **Append Functionality**: Multiple events per day consolidated
- **Data Retention**: Configurable S3 lifecycle policies (default: 90 days)

## AWS Resources

This solution deploys the following AWS resources:

| Resource | Purpose | Configuration |
|----------|---------|---------------|
| **Lambda Function** | Event processing and data extraction | Python 3.11, 128MB memory, 30s timeout |
| **IAM Role** | Lambda execution permissions | EC2 describe, S3 write, CloudWatch logs |
| **EventBridge Rule** | EC2 launch event filtering | Filters `RunInstances` API calls |
| **S3 Bucket** | CSV report storage | Lifecycle policy, versioning enabled |
| **CloudWatch Logs** | Function logging and monitoring | 14-day retention, structured logging |

**Estimated Monthly Cost**: < $1 USD for typical usage (based on AWS Free Tier)

## Project Structure

```
ec2-launch-monitor/
├── cf-template/
│   └── cloudformation-clean.yaml     # Complete infrastructure template
├── lambda/
│   ├── index.py                      # Main Lambda function
│   └── ec2_helper.py                 # Business logic utilities
├── tasks/                            # Development automation
│   ├── deploy.sh                     # Full stack deployment
│   ├── update-lambda-code.sh         # Lambda code updates
│   ├── create_ec2.sh                 # Test instance creation
│   ├── cleanup_ec2.sh                # Test resource cleanup
│   └── check_s3.sh                   # S3 report verification
├── .vscode/
│   └── tasks.json                    # VS Code development tasks
├── mock_response_data.json           # Sample data for development
├── tsconfig.json                     # TypeScript configuration
└── README.md                         # Project documentation
```

## Getting Started

### Prerequisites
- **AWS CLI**: Configured with admin permissions
- **Bash**: macOS/Linux shell environment
- **Python 3.11+**: For local development and testing
- **VS Code**: Recommended for development workflow

### Installation

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd ec2-launch-monitor
   chmod +x tasks/*.sh
   ```

2. **Configure AWS**:
   ```bash
   aws configure
   # Ensure you have EC2, Lambda, S3, CloudFormation, and IAM permissions
   ```

3. **Deploy Infrastructure**:
   ```bash
   ./tasks/deploy.sh
   ```

4. **Verify Deployment**:
   ```bash
   # Check CloudFormation stack
   aws cloudformation describe-stacks --stack-name ec2-launch-monitor --region us-east-2
   
   # Verify Lambda function
   aws lambda get-function --function-name ec2-launch-monitor --region us-east-2
   ```

## Development Workflow

### VS Code Integration
The project includes comprehensive VS Code tasks for streamlined development:

**Access via**: `Ctrl/Cmd + Shift + P` → "Tasks: Run Task"

#### Deployment Tasks
- **Deploy CloudFormation Stack**: Complete infrastructure deployment
- **Update Lambda Code Only**: Fast code-only updates during development
- **Wait for Stack Completion**: CloudFormation deployment monitoring

#### Testing Tasks
- **Create Test EC2 Instance (Single)**: Launch one test instance
- **Create 3 Test EC2 Instances**: Batch testing
- **Create 5 Test EC2 Instances**: Load testing
- **Create Test EC2 Instances (Multiple)**: Interactive count selection
- **Cleanup All Test EC2 Instances**: Terminate all test resources

#### Monitoring Tasks
- **Check Lambda Logs**: Recent execution logs
- **Follow Lambda Logs Live**: Real-time log monitoring
- **Check S3 Reports**: Verify CSV generation
- **Download Latest CSV Report**: Local report inspection

#### Workflow Automation
- **Full Development Cycle**: Deploy → Test → Monitor → Cleanup
- **Batch Test Cycle (3 Instances)**: Automated batch testing
- **Load Test Cycle (5 Instances)**: Automated load testing

### Manual Development Commands

```bash
# Quick deployment (code changes only)
./tasks/update-lambda-code.sh

# Create test instances
./tasks/create_ec2.sh          # Single instance
./tasks/create_ec2.sh 5        # 5 instances

# Monitor and verify
./tasks/check_s3.sh            # Check CSV reports
aws logs tail /aws/lambda/ec2-launch-monitor --region us-east-2 --since 1h

# Cleanup
./tasks/cleanup_ec2.sh         # Remove all test instances
```

## Data Flow

### Event Processing Pipeline

1. **Event Trigger**:
   ```
   EC2 RunInstances API → CloudTrail → EventBridge Rule → Lambda
   ```

2. **Lambda Processing**:
   ```python
   def lambda_handler(event, context):
       # Parse EventBridge event
       # Extract instance IDs from CloudTrail
       # Call process_ec2_launch_event()
       # Store results to S3 CSV
       # Return structured response
   ```

3. **Data Collection** (`process_ec2_launch_event()`):
   - Validate instance existence
   - Collect comprehensive metadata
   - Filter by tags (`adhoc=true`)
   - Structure data for CSV export

4. **S3 Storage** (`store_to_s3_csv()`):
   - Generate daily CSV filename
   - Append new records to existing file
   - Organize by date hierarchy
   - Apply S3 lifecycle policies

### CSV Output Format

Daily reports (`YYYY/MM/DD/ec2-launch-report.csv`):
```csv
timestamp,instance_id,instance_type,state,launch_time,availability_zone,vpc_id,subnet_id,private_ip,public_ip,security_groups,key_name,ami_id,platform,architecture,tags
2025-08-04T15:30:00Z,i-1234567890abcdef0,t3.micro,running,2025-08-04T15:25:00Z,us-east-2a,vpc-12345678,subnet-87654321,10.0.1.100,54.123.45.67,"sg-web,sg-ssh",my-keypair,ami-0abcdef1234567890,linux,x86_64,"adhoc=true,Name=Test Instance"
```

## Configuration

### Environment Variables
The Lambda function uses these environment variables (set via CloudFormation):

```yaml
Environment:
  Variables:
    REPORTS_BUCKET_NAME: !Ref ReportsBucket
    AWS_REGION: !Ref AWS::Region
    LOG_LEVEL: INFO
```

### CloudFormation Parameters
Customizable deployment parameters:

```yaml
Parameters:
  LambdaFunctionName:
    Default: ec2-launch-monitor
  TagKey:
    Default: adhoc
  TagValue:
    Default: "true"
  ReportsRetentionDays:
    Default: 90
```

### Filtering Configuration
Modify the EventBridge rule pattern in `cloudformation-clean.yaml`:

```yaml
EventPattern:
  source: ["aws.ec2"]
  detail-type: ["AWS API Call via CloudTrail"]
  detail:
    eventSource: ["ec2.amazonaws.com"]
    eventName: ["RunInstances"]
```

## Testing

### Automated Testing Workflow

The project includes comprehensive testing automation:

#### Single Instance Testing
```bash
# Create test instance with timestamp naming
./tasks/create_ec2.sh

# Expected output:
# - Instance launched with adhoc=true tag
# - Unique name: ec2-test-YYYYMMDD-HHMMSS
# - Instance ID saved to test-instance-id-TIMESTAMP.txt

# Verify Lambda execution (after ~30 seconds)
aws logs tail /aws/lambda/ec2-launch-monitor --region us-east-2 --since 5m

# Check CSV generation
./tasks/check_s3.sh

# Cleanup
./tasks/cleanup_ec2.sh
```

#### Batch Testing
```bash
# Create multiple instances for load testing
./tasks/create_ec2.sh 5

# Expected behavior:
# - 5 instances launched simultaneously
# - Each triggers separate Lambda execution
# - All data consolidated in daily CSV
# - Batch cleanup handles all instances
```

#### Error Testing
```bash
# Test Lambda with invalid instance IDs
aws lambda invoke \
  --function-name ec2-launch-monitor \
  --payload '{"detail":{"responseElements":{"instancesSet":{"items":[{"instanceId":"i-invalid"}]}}}}' \
  --region us-east-2 \
  response.json

# Check error handling in logs
```

### Manual Testing

#### Create Tagged Test Instance
```bash
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --instance-type t2.micro \
  --key-name your-key-pair \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=adhoc,Value=true},{Key=Name,Value=Manual-Test}]' \
  --region us-east-2
```

#### Verify EventBridge Rule
```bash
aws events list-targets-by-rule \
  --rule ec2-launch-monitor-rule \
  --region us-east-2
```

## Monitoring

### CloudWatch Metrics
Monitor Lambda function performance:

```bash
# Function invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=ec2-launch-monitor \
  --start-time 2025-08-04T00:00:00Z \
  --end-time 2025-08-04T23:59:59Z \
  --period 3600 \
  --statistics Sum \
  --region us-east-2

# Error rate
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=ec2-launch-monitor \
  --start-time 2025-08-04T00:00:00Z \
  --end-time 2025-08-04T23:59:59Z \
  --period 3600 \
  --statistics Sum \
  --region us-east-2
```

### Log Analysis
Structured logging provides detailed execution information:

```bash
# Recent executions
aws logs tail /aws/lambda/ec2-launch-monitor --region us-east-2 --since 1h

# Filter for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/ec2-launch-monitor \
  --filter-pattern "ERROR" \
  --region us-east-2

# Performance monitoring
aws logs filter-log-events \
  --log-group-name /aws/lambda/ec2-launch-monitor \
  --filter-pattern "Duration" \
  --region us-east-2
```

### S3 Report Monitoring
```bash
# List today's reports
BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name ec2-launch-monitor \
  --query 'Stacks[0].Outputs[?OutputKey==`ReportsBucketName`].OutputValue' \
  --output text \
  --region us-east-2)

TODAY=$(date +%Y/%m/%d)
aws s3 ls s3://$BUCKET_NAME/ec2-launch-reports/$TODAY/ --recursive

# Download and inspect latest report
aws s3 cp s3://$BUCKET_NAME/ec2-launch-reports/$TODAY/ec2-launch-report.csv ./latest-report.csv
head -10 ./latest-report.csv
```

## Troubleshooting

### Common Issues

#### Lambda Function Not Triggering
**Symptoms**: No CloudWatch logs after EC2 launch
**Solutions**:
```bash
# Check EventBridge rule status
aws events describe-rule --name ec2-launch-monitor-rule --region us-east-2

# Verify rule targets
aws events list-targets-by-rule --rule ec2-launch-monitor-rule --region us-east-2

# Test manual Lambda invocation
aws lambda invoke \
  --function-name ec2-launch-monitor \
  --payload file://mock_response_data.json \
  --region us-east-2 \
  response.json
```

#### Permission Errors
**Symptoms**: AccessDenied errors in Lambda logs
**Solutions**:
```bash
# Verify IAM role permissions
aws iam get-role-policy \
  --role-name ec2-launch-monitor-role \
  --policy-name ec2-launch-monitor-policy \
  --region us-east-2

# Check Lambda execution role
aws lambda get-function-configuration \
  --function-name ec2-launch-monitor \
  --region us-east-2 \
  --query 'Role'
```

#### CSV Generation Issues
**Symptoms**: Lambda succeeds but no S3 files
**Solutions**:
```bash
# Check S3 bucket permissions
aws s3api get-bucket-policy --bucket $BUCKET_NAME

# Verify bucket exists and is accessible
aws s3 ls s3://$BUCKET_NAME/

# Check Lambda environment variables
aws lambda get-function-configuration \
  --function-name ec2-launch-monitor \
  --region us-east-2 \
  --query 'Environment'
```

#### Instance Not Found Errors
**Symptoms**: `Instance i-xxxxx not found` in logs
**Explanation**: EventBridge events can arrive before EC2 instances are fully registered
**Solutions**:
- Lambda includes retry logic with exponential backoff
- Check logs for retry attempts
- Instances should appear in subsequent processing

### Debug Commands

```bash
# Enable debug logging (redeploy required)
# Modify cloudformation-clean.yaml:
# LOG_LEVEL: DEBUG

# View detailed execution logs
aws logs tail /aws/lambda/ec2-launch-monitor --follow --region us-east-2

# Check CloudFormation stack events
aws cloudformation describe-stack-events \
  --stack-name ec2-launch-monitor \
  --region us-east-2 \
  --query 'StackEvents[?ResourceStatus!=`CREATE_COMPLETE`]'

# Validate EventBridge rule pattern
aws events test-event-pattern \
  --event-pattern file://eventbridge-pattern.json \
  --event file://sample-event.json
```

### Performance Optimization

- **Memory**: Default 128MB is sufficient for typical workloads
- **Timeout**: 30 seconds handles batch processing of up to 20 instances
- **Concurrency**: Default reserved concurrency prevents account limits
- **Cold Starts**: Minimal impact due to event-driven nature

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## Support

For issues and questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review CloudWatch logs for detailed error information
- Open an issue with detailed logs and steps to reproduce

---

**Built for Platform Engineering Teams** | **AWS Serverless** | **Production Ready**

