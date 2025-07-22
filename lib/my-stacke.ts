import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { join } from 'path';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as iam from 'aws-cdk-lib/aws-iam';

export class Ec2LaunchMonitoringStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // Define resources here

    const myLambda = new lambda.Function(this, 'MyLambdaFunction', {
      runtime: lambda.Runtime.PYTHON_3_11,
      code: lambda.Code.fromAsset('lambda'),
      handler: 'index.handler',
    });

    const ec2_launch_rule = new events.Rule(this, 'MyRule', {
      eventPattern: {
        source: ['aws.ec2'],
        detailType: ['AWS API Call via CloudTrail'],
        detail: {
          eventName: ['RunInstances'],
          eventSource: ['ec2.amazonaws.com']
        }
      }
    });

    ec2_launch_rule.addTarget(new targets.LambdaFunction(myLambda));
    myLambda.addToRolePolicy(new iam.PolicyStatement({
      actions: ['ec2:RunInstances'],
      resources: ['*'],
    }));
    

    myLambda.addToRolePolicy(new iam.PolicyStatement({
      actions: ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
      resources: ['*']
    }));

    myLambda.addToRolePolicy(new iam.PolicyStatement({
      actions: [
        'ec2:DescribeInstances',
        'ec2:DescribeInstanceStatus',
        'ec2:DescribeRegions',
        'ec2:DescribeAvailabilityZones'
      ],
      resources: ['*']
    }));
  }
}