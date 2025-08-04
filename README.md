# EC2 Launch Monitor

## Overview

The EC2 Launch Monitor is a serverless compliance monitoring system that automatically tracks and reports EC2 instances launched with specific tags in AWS environments. The system provides real-time visibility into adhoc infrastructure deployments through an automated dashboard that aggregates instance data into daily compliance reports.

## System Architecture

The solution employs a fully serverless architecture built on AWS services, providing cost-effective monitoring without requiring dedicated infrastructure management.

### Core Components

- **CloudWatch Events Rule**: Captures EC2 `RunInstances` API calls in real-time
- **Lambda Function**: Processes launch events and filters for tagged instances
- **S3 Static Website**: Hosts the compliance dashboard with automated data loading
- **S3 Report Storage**: Maintains daily CSV reports with structured instance data

## Operational Flow

![EC2 Launch Monitor Architecture](images/arch.png)

### Event Processing Pipeline

1. **Event Capture**: CloudWatch Events automatically detects EC2 instance launches across the AWS account
2. **Tag Filtering**: Lambda function examines each launched instance for the `adhoc=true` tag
3. **Data Collection**: Tagged instances have their metadata extracted and structured
4. **Report Generation**: Instance data is appended to daily CSV reports stored in S3
5. **Dashboard Display**: Static website dynamically loads and displays current day's compliance data

## Monitoring Scope

The system specifically tracks EC2 instances with the following tag configuration:
- **Tag Key**: `adhoc`
- **Tag Value**: `true`

### Captured Instance Metadata

- Instance ID and Type
- Private and Public IP Addresses
- Launch Time and Availability Zone
- VPC and Subnet Configuration
- Security Group Assignments
- Key Pair Associations
- Complete Tag Inventory
- Processing Timestamps

## Data Organization

Reports are organized in a hierarchical S3 structure:
```
ec2-launch-reports/
├── YYYY/
│   └── MM/
│       └── ec2-instances-YYYY-MM-DD.csv
```

Each daily report contains cumulative instance data, with new launches appended throughout the day to maintain a complete compliance record.

## Dashboard Features

The compliance dashboard provides:
- **Automated Data Loading**: Dynamically fetches current day's launch data
- **Fallback Reporting**: Displays static sample data when no launches have occurred
- **Status Visualization**: Color-coded instance states for quick assessment
- **Responsive Design**: Mobile-friendly interface for monitoring from any device

## Security Implementation

- **IP-Restricted Access**: Dashboard access limited to authorized IP addresses
- **Private S3 Bucket**: Report storage uses private bucket with restrictive policies
- **IAM Role Isolation**: Lambda function operates with minimal required permissions
- **No Public API Exposure**: All data access occurs through secure S3 website hosting

## Compliance Benefits

- **Real-time Monitoring**: Immediate visibility into adhoc instance deployments
- **Historical Tracking**: Persistent daily reports for audit and analysis
- **Automated Reporting**: No manual intervention required for compliance data collection
- **Cost Optimization**: Serverless architecture minimizes operational overhead

## Technical Implementation

### AWS Resources Deployed

| Resource | Purpose | Configuration |
|----------|---------|---------------|
| **Lambda Function** | Event processing and data extraction | Python 3.11, minimal memory footprint |
| **CloudWatch Events Rule** | EC2 launch event filtering | Filters `RunInstances` API calls |
| **S3 Unified Bucket** | Dashboard hosting and report storage | Static website configuration, lifecycle policies |
| **IAM Roles** | Secure service permissions | Least-privilege access patterns |

### Data Processing Logic

The Lambda function implements efficient batch processing:
- Single API call to retrieve instance metadata
- In-memory filtering and data transformation
- Atomic CSV file operations with append functionality
- Comprehensive error handling and retry mechanisms

### Frontend Architecture

The dashboard uses modern web technologies:
- **Dynamic Loading**: JavaScript fetches CSV data from S3 using relative paths
- **Graceful Degradation**: Automatic fallback to static sample data
- **Responsive Layout**: CSS Grid and Flexbox for cross-device compatibility
- **Status Indicators**: Visual styling for instance state recognition

## Project Structure

```
ec2-launch-monitor/
├── cf-template/
│   └── cloudformation-clean.yaml     # Complete infrastructure definition
├── lambda/
│   ├── index.py                      # Event processing logic
│   └── ec2_helper.py                 # Utility functions
├── src/
│   ├── index.html                    # Dashboard interface
│   ├── style.css                     # Responsive styling
│   └── script.js                     # Data loading and rendering
├── images/
│   └── dashboard.png                 # Dashboard screenshot for README
├── tasks/
│   ├── check_s3.sh                   # S3 report verification
│   ├── cleanup_ec2.sh                # Test resource cleanup
│   ├── create_ec2.sh                 # Test instance creation
│   ├── deploy.sh                     # Full stack deployment
│   ├── predeploy.sh                  # Update lambda/static site code
│   └── prereqs.sh                    # Initial setup and S3 bucket creation
└── README.md                         # This documentation
```

## Dashboard Screenshot

![EC2 Launch Monitor Dashboard](images/dashboard.png)

The dashboard displays:
- Real-time compliance data in tabular format
- Color-coded status indicators for quick assessment
- Mobile-responsive design for field access
- Automated refresh of current day's launch data

---

*This documentation reflects the current state of the feature/reviewboard branch implementation.*

## Setup Requirements

Before deploying this project, you must configure the following values for your environment:

### Prerequisites

#### S3 Bucket for Lambda Code
The system requires an S3 bucket to store the Lambda deployment package. The `prereqs.sh` script will automatically handle this setup:

1. **Run Prerequisites Script**: `./tasks/prereqs.sh` will create the S3 bucket and upload Lambda code
2. **Configuration Required**: Ensure `config.env` contains your `LAMBDA_CODE_BUCKET` name
3. **Automatic Packaging**: The script packages and uploads the Lambda function automatically

**Note**: The prereqs script must be run before deploying the CloudFormation stack, as it creates the S3 bucket and uploads the Lambda code that CloudFormation references.

### Configuration File Setup

1. **Copy Configuration Template**: 
   ```bash
   cp config.env config.env.local
   ```

2. **Update Variables**: Edit `config.env` with your environment-specific values:
   - `AWS_REGION`: Your target AWS region
   - `LAMBDA_CODE_BUCKET`: Your S3 bucket for Lambda code storage
   - `ALLOWED_IP_ADDRESS`: Your IP address for dashboard access
   - `STACK_NAME`: CloudFormation stack name (optional)

### 1. IP Address Configuration
- **Variable**: `ALLOWED_IP_ADDRESS` in `config.env`
- **Change**: Replace `0.0.0.0/0` with your actual IP address (e.g., `203.0.113.0/32`)
- **Purpose**: Restricts dashboard access to your IP only

### 2. S3 Bucket Names
- **Variable**: `LAMBDA_CODE_BUCKET` in `config.env`
- **Change**: Replace `ec2-launch-monitor-code` with your unique S3 bucket name
- **Purpose**: Stores Lambda deployment packages

### 3. AWS Region
- **Variable**: `AWS_REGION` in `config.env`
- **Change**: Replace `us-east-2` with your preferred AWS region
- **Purpose**: Ensures all resources deploy to your target region

### 4. AWS CLI Configuration
Ensure your AWS CLI is configured with appropriate permissions for:
- CloudFormation (create/update stacks)
- Lambda (create/update functions)
- S3 (create buckets, upload objects)
- EC2 (describe instances)
- IAM (create roles and policies)

### Deployment Steps

1. **Run Prerequisites Setup**:
   ```bash
   ./tasks/prereqs.sh
   ```
   This will:
   - Create the S3 bucket for Lambda code storage
   - Package the Lambda function code
   - Upload the Lambda package to S3

2. **Configure Environment** (if not done yet):
   ```bash
   cp config.env config.env.local
   # Edit config.env.local with your values
   ```

3. **Deploy Infrastructure**:
   ```bash
   ./tasks/deploy.sh
   ```

4. **Test the System**:
   ```bash
   ./tasks/create_ec2.sh    # Create test instances
   ./tasks/check_s3.sh      # Verify reports generated
   ```

### Updating Lambda Code

After initial deployment, use the predeploy script to update Lambda code:
```bash
./tasks/predeploy.sh      # Update Lambda function and static files
```

