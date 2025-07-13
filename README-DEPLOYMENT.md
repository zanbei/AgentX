# AgentX Deployment Guide

A comprehensive guide for deploying the AgentX platform to AWS using Docker and AWS CDK.

## 🏗️ Architecture Overview

The AgentX deployment architecture consists of:

- **AWS ECS Cluster**: Container orchestration service
- **AWS ECR Repositories**: Docker image storage
- **Application Load Balancer**: Traffic distribution
- **DynamoDB Tables**: Data storage
- **EventBridge Scheduler**: Task scheduling
- **Lambda Functions**: Serverless execution

## 🧩 Components

The project consists of the following deployable components:

1. **Backend (BE)**: FastAPI Python application
   - Container: `agentx/be`
   - Port: 8000
   - Path: `/api/*`

2. **Frontend (FE)**: React/TypeScript application
   - Container: `agentx/fe`
   - Port: 80
   - Path: `/` (default)

3. **MySQL MCP Server**: MySQL Model Context Protocol server
   - Container: `agentx/mcp-mysql`
   - Port: 3000
   - Path: `/mcp-server/mysql/*`

4. **Redshift MCP Server**: Redshift Model Context Protocol server
   - Container: `agentx/mcp-redshift`
   - Port: 3000
   - Path: `/mcp-server/redshift/*`

## 🚀 Deployment Steps

### 1. Prerequisites

- AWS CLI installed and configured
- Docker installed
- Node.js 18.x or later
- AWS CDK v2 installed (`npm install -g aws-cdk`)

### 2. Build and Push Docker Images

#### Using the Automated Script

```bash
# Make the script executable
chmod +x build-and-push.sh

# Run the script with your AWS region
./build-and-push.sh us-west-2
```

This script will:
1. Log in to your AWS ECR registry
2. Create ECR repositories if they don't exist
3. Build Docker images for all components
4. Tag and push the images to ECR

#### Manual Build and Push

```bash
# Set your AWS account ID and region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=us-west-2

# Log in to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Create repositories if they don't exist
aws ecr describe-repositories --repository-names agentx/be --region $AWS_REGION || aws ecr create-repository --repository-name agentx/be --region $AWS_REGION
aws ecr describe-repositories --repository-names agentx/fe --region $AWS_REGION || aws ecr create-repository --repository-name agentx/fe --region $AWS_REGION
aws ecr describe-repositories --repository-names agentx/mcp-mysql --region $AWS_REGION || aws ecr create-repository --repository-name agentx/mcp-mysql --region $AWS_REGION
aws ecr describe-repositories --repository-names agentx/mcp-redshift --region $AWS_REGION || aws ecr create-repository --repository-name agentx/mcp-redshift --region $AWS_REGION

# Build and push backend
cd be
docker build -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/agentx/be:latest .
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/agentx/be:latest

# Build and push frontend
cd ../fe
docker build -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/agentx/fe:latest .
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/agentx/fe:latest

# Build and push MySQL MCP server
cd ../mcp/mysql
docker build -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/agentx/mcp-mysql:latest .
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/agentx/mcp-mysql:latest

# Build and push Redshift MCP server
cd ../redshift
docker build -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/agentx/mcp-redshift:latest .
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/agentx/mcp-redshift:latest
```

### 3. Deploy with CDK

#### Using the Automated Script

```bash
# Make the script executable
chmod +x cdk/deploy.sh

# Navigate to the CDK directory
cd cdk

# Run the deployment script with options
./deploy.sh --region us-west-2
```

Available options:
- `--region REGION`: AWS region to deploy to
- `--vpc-id VPC_ID`: Use existing VPC ID instead of creating a new one
- `--no-mysql-mcp`: Disable MySQL MCP server deployment
- `--no-redshift-mcp`: Disable Redshift MCP server deployment
- `--no-agentx-stack`: Disable AgentX stack deployment
- `--only-schedule-stack`: Deploy only the Schedule stack

#### Manual CDK Deployment

```bash
# Navigate to the CDK directory
cd cdk

# Install dependencies
npm install

# Bootstrap CDK (if not already done)
cdk bootstrap aws://ACCOUNT-NUMBER/REGION

# Deploy the stacks
cdk deploy --all
```

## ⚙️ Configuration

### Environment Variables

Update the environment variables in the CDK stack (`cdk/lib/agentx-stack.ts`):

#### Backend Environment Variables

```typescript
const beContainer = beTaskDefinition.addContainer('BeContainer', {
  // ...
  environment: {
    APP_ENV: 'production',
    AWS_REGION: this.region,
    // Add other environment variables as needed
  },
});
```

#### Frontend Environment Variables

```typescript
const feContainer = feTaskDefinition.addContainer('FeContainer', {
  // ...
  environment: {
    NODE_ENV: 'production',
    AWS_REGION: this.region,
    // Add other environment variables as needed
  },
});
```

#### MCP Server Environment Variables

```typescript
const mcpMysqlContainer = mcpMysqlTaskDefinition.addContainer('McpMysqlContainer', {
  // ...
  environment: {
    NODE_ENV: 'production',
    AWS_REGION: this.region,
    MYSQL_HOST: 'your-mysql-host',
    MYSQL_PORT: '3306',
    MYSQL_USER: 'your-mysql-user',
    MYSQL_PASSWORD: 'your-mysql-password',
    MYSQL_DATABASE: 'your-mysql-database',
  },
});

const mcpRedshiftContainer = mcpRedshiftTaskDefinition.addContainer('McpRedshiftContainer', {
  // ...
  environment: {
    PYTHON_ENV: 'production',
    AWS_REGION: this.region,
    RS_HOST: 'your-redshift-host',
    RS_PORT: '5439',
    RS_USER: 'your-redshift-user',
    RS_PASSWORD: 'your-redshift-password',
    RS_DATABASE: 'your-redshift-database',
    RS_SCHEMA: 'public',
  },
});
```

### Security Considerations

For production deployments, consider these security enhancements:

1. **Use AWS Secrets Manager** for sensitive environment variables:
   ```typescript
   const secret = secretsmanager.Secret.fromSecretNameV2(this, 'DbSecret', 'my-db-secret');
   container.addEnvironment('DB_PASSWORD', secret.secretValueFromJson('password').toString());
   ```

2. **Implement proper IAM roles and policies**:
   ```typescript
   const taskRole = new iam.Role(this, 'TaskRole', {
     assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
   });
   taskRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonDynamoDBFullAccess'));
   ```

3. **Enable HTTPS** with an SSL certificate:
   ```typescript
   const certificate = acm.Certificate.fromCertificateArn(this, 'Certificate', 'arn:aws:acm:region:account:certificate/certificate-id');
   const httpsListener = lb.addListener('HttpsListener', {
     port: 443,
     certificates: [certificate],
     sslPolicy: elbv2.SslPolicy.RECOMMENDED,
   });
   ```

## 📊 Monitoring and Logging

### CloudWatch Logs

All services are configured to send logs to CloudWatch Logs:

```typescript
const logGroup = new logs.LogGroup(this, 'LogGroup', {
  logGroupName: '/ecs/agentx-service',
  removalPolicy: cdk.RemovalPolicy.DESTROY,
  retention: logs.RetentionDays.ONE_WEEK,
});

container.addLogging(ecs.LogDrivers.awsLogs({
  streamPrefix: 'service',
  logGroup: logGroup,
}));
```

### CloudWatch Alarms

Add CloudWatch Alarms for monitoring:

```typescript
new cloudwatch.Alarm(this, 'HighCpuAlarm', {
  metric: service.metricCpuUtilization(),
  threshold: 90,
  evaluationPeriods: 3,
  datapointsToAlarm: 2,
});
```

### X-Ray Tracing

Enable X-Ray for distributed tracing:

```typescript
const taskDefinition = new ecs.FargateTaskDefinition(this, 'TaskDef');
taskDefinition.addContainer('XRayDaemon', {
  image: ecs.ContainerImage.fromRegistry('amazon/aws-xray-daemon'),
  essential: true,
  portMappings: [{ containerPort: 2000, protocol: ecs.Protocol.UDP }],
});
```

## 💰 Cost Optimization

### Use EC2 Instead of Fargate

For cost savings, consider using EC2 launch type instead of Fargate:

```typescript
const service = new ecs.Ec2Service(this, 'Service', {
  cluster,
  taskDefinition,
  desiredCount: 2,
});
```

### Auto Scaling

Implement auto scaling to adjust capacity based on demand:

```typescript
const scaling = service.autoScaleTaskCount({
  minCapacity: 2,
  maxCapacity: 10,
});

scaling.scaleOnCpuUtilization('CpuScaling', {
  targetUtilizationPercent: 70,
});
```

### VPC Endpoints

Use VPC endpoints to reduce NAT Gateway costs:

```typescript
new ec2.InterfaceVpcEndpoint(this, 'DynamoDBEndpoint', {
  vpc,
  service: ec2.InterfaceVpcEndpointAwsService.DYNAMODB,
});
```

## 🔄 Continuous Deployment

### GitHub Actions

Create a GitHub Actions workflow for continuous deployment:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2
      - name: Build and push Docker images
        run: ./build-and-push.sh us-west-2
      - name: Deploy with CDK
        run: |
          cd cdk
          npm install
          npm run cdk deploy -- --all --require-approval never
```

### AWS CodePipeline

Alternatively, set up AWS CodePipeline for continuous deployment:

```typescript
const pipeline = new codepipeline.Pipeline(this, 'Pipeline', {
  pipelineName: 'AgentXPipeline',
});

const sourceOutput = new codepipeline.Artifact();
const sourceAction = new codepipeline_actions.CodeStarConnectionsSourceAction({
  actionName: 'GitHub',
  owner: 'your-github-username',
  repo: 'agentx',
  branch: 'main',
  output: sourceOutput,
  connectionArn: 'arn:aws:codestar-connections:region:account:connection/connection-id',
});

pipeline.addStage({
  stageName: 'Source',
  actions: [sourceAction],
});

// Add build and deploy stages
```

## 🔍 Troubleshooting

### Common Issues

1. **Container fails to start**:
   - Check CloudWatch Logs for error messages
   - Verify environment variables are correctly set
   - Ensure IAM permissions are sufficient

2. **Load balancer health checks failing**:
   - Verify the health check path is correct
   - Check that the container is listening on the expected port
   - Ensure security groups allow traffic between the load balancer and containers

3. **CDK deployment errors**:
   - Check that AWS credentials are correctly configured
   - Verify that the CDK is bootstrapped in the target region
   - Check for syntax errors in CDK code

### Useful Commands

```bash
# View service logs
aws logs get-log-events --log-group-name /ecs/agentx-be --log-stream-name stream-name

# Check service status
aws ecs describe-services --cluster agentx-cluster --services agentx-be-service

# View task details
aws ecs describe-tasks --cluster agentx-cluster --tasks task-id

# SSH into EC2 instance (if using EC2 launch type)
aws ssm start-session --target instance-id
