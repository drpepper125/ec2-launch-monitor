// bin/app.ts

import { App } from 'aws-cdk-lib';
import { Ec2LaunchMonitoringStack } from '../lib/my-stacke';
import { environments } from '../config';

const app = new App();

new Ec2LaunchMonitoringStack(app, 'DevStack', {
  env: {
    account: environments.dev.account,
    region: environments.dev.region,
  },
  tags: {
    environment: environments.dev.name,
  },
});
