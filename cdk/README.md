# AgentX AWS CDK Deployment

This project contains AWS CDK code to deploy the AgentX application to AWS ECS.

## Prerequisites

- AWS CLI installed and configured
- Node.js 18.x or later
- AWS CDK v2 installed (`npm install -g aws-cdk`)

## Project Structure

- `bin/cdk.ts` - Entry point for the CDK application
- `lib/agentx-stack.ts` - Main stack definition with all AWS resources

## Components

The deployment includes the following components:

1. **Backend (BE)** - FastAPI Python application
2. **Frontend (FE)** - React/TypeScript application
3. **MCP MySQL** - MySQL MCP server
4. **MCP Redshift** - Redshift MCP server

## Deployment Instructions

### 1. Build Docker Images

First, build and push Docker images for each component:

```bash
# Login to ECR
aws ecr get-login-password --region <your-region> | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.<your-region>.amazonaws.com

# Build and push backend image
cd ../be
docker build -t agentx-be .
docker tag agentx-be:latest <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/agentx-be:latest
docker push <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/agentx-be:latest

# Build and push frontend image
cd ../fe
docker build -t agentx-fe .
docker tag agentx-fe:latest <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/agentx-fe:latest
docker push <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/agentx-fe:latest

# Build and push MCP MySQL image
cd ../mcp/mysql
docker build -t agentx-mcp-mysql .
docker tag agentx-mcp-mysql:latest <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/agentx-mcp-mysql:latest
docker push <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/agentx-mcp-mysql:latest

# Build and push MCP Redshift image
cd ../mcp/redshift
docker build -t agentx-mcp-redshift .
docker tag agentx-mcp-redshift:latest <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/agentx-mcp-redshift:latest
docker push <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/agentx-mcp-redshift:latest
```

### 2. Deploy with CDK

```bash
# Install dependencies
npm install

# Bootstrap CDK (if not already done)
cdk bootstrap

# Deploy the stack with default VPC (creates a new VPC)
cdk deploy

# OR deploy using an existing VPC (specify VPC ID)
cdk deploy -c vpcId=vpc-12345678

# OR deploy using an existing VPC via environment variable
VPC_ID=vpc-12345678 cdk deploy
```

### 3. Configuration

After deployment, you'll need to configure the following:

1. **SSL Certificate**: For production, create and attach an SSL certificate to the HTTPS listener.
2. **Environment Variables**: Update environment variables in the CDK stack for each service as needed.
3. **Database Configuration**: Configure database connection strings for the services.

## Useful CDK Commands

* `npm run build` - Compile TypeScript to JavaScript
* `npm run watch` - Watch for changes and compile
* `cdk deploy` - Deploy this stack to your default AWS account/region
* `cdk diff` - Compare deployed stack with current state
* `cdk synth` - Emit the synthesized CloudFormation template

## Security Considerations

- The CDK stack creates security groups that allow traffic between services.
- For production, you should review and tighten security settings.
- Consider using AWS Secrets Manager for sensitive environment variables.

## Cost Optimization

- The stack uses Fargate for simplicity, but you could use EC2 instances for cost savings.
- Consider adjusting the desired count of services based on your traffic needs.
- NAT Gateways incur costs; consider using VPC endpoints for AWS services.

## VPC Configuration

The stack supports two VPC deployment options:

### Option 1: Create a New VPC (Default)

If you don't specify a VPC ID, the stack will create a new VPC with:
- 2 Availability Zones
- 1 NAT Gateway
- Public and private subnets

This is suitable for testing or when you need a dedicated VPC for the application.

### Option 2: Use an Existing VPC

You can deploy the stack into an existing VPC by providing the VPC ID:

```bash
# Using CDK context parameter
cdk deploy -c vpcId=vpc-12345678

# OR using environment variable
VPC_ID=vpc-12345678 cdk deploy
```

Requirements for the existing VPC:
- Must have both public and private subnets
- Private subnets must have outbound internet connectivity (via NAT Gateway or similar)
- Subnets must be properly tagged for ECS and ALB resource placement

Using an existing VPC is recommended for:
- Integration with existing resources
- Cost optimization by sharing NAT Gateways
- Compliance with organizational network policies
