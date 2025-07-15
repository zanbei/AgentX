#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { AgentXStack } from '../lib/agentx-stack';
import { AgentScheduleStack } from '../lib/agent-schedule-stack';

const app = new cdk.App();

// Get parameters from context or environment variables
// Users can provide parameters using:
// 1. CDK context: cdk deploy -c vpcId=vpc-12345 -c deployMysqlMcpServer=false
// 2. Environment variables: VPC_ID=vpc-12345 DEPLOY_MYSQL_MCP=false cdk deploy
const vpcId = app.node.tryGetContext('vpcId') || process.env.VPC_ID;
const deployMysqlMcpServer = app.node.tryGetContext('deployMysqlMcpServer') !== 'false' && process.env.DEPLOY_MYSQL_MCP !== 'false';
const deployRedshiftMcpServer = app.node.tryGetContext('deployRedshiftMcpServer') !== 'false' && process.env.DEPLOY_REDSHIFT_MCP !== 'false';
const createDynamoDBTables = app.node.tryGetContext('createDynamoDBTables') !== 'false' && process.env.CREATE_DYNAMODB_TABLES !== 'false';
const deployAgentXStack = app.node.tryGetContext('deployAgentXStack') !== 'false' && process.env.DEPLOY_AGENTX_STACK !== 'false';
const deployScheduleStack = app.node.tryGetContext('deployScheduleStack') !== 'false' && process.env.DEPLOY_SCHEDULE_STACK !== 'false';

// Create AgentX stack if enabled
let agentXStack: AgentXStack | undefined;
if (deployAgentXStack) {
  agentXStack = new AgentXStack(app, 'AgentXStack', {
    env: { 
      account: process.env.CDK_DEFAULT_ACCOUNT, 
      region: process.env.CDK_DEFAULT_REGION || 'us-west-2' 
    },
    description: 'AgentX application stack with backend, frontend, and MCP services',
    // Pass the parameters
    vpcId: vpcId,
    deployMysqlMcpServer: deployMysqlMcpServer,
    deployRedshiftMcpServer: deployRedshiftMcpServer,
    createDynamoDBTables: createDynamoDBTables,
  });
}

// Log configuration
console.log(vpcId 
  ? `Using existing VPC with ID: ${vpcId}` 
  : 'No VPC ID provided. A new VPC will be created.');
console.log(`MySQL MCP server deployment: ${deployMysqlMcpServer ? 'Enabled' : 'Disabled'}`);
console.log(`Redshift MCP server deployment: ${deployRedshiftMcpServer ? 'Enabled' : 'Disabled'}`);
console.log(`DynamoDB tables creation: ${createDynamoDBTables ? 'Enabled' : 'Disabled'}`);
console.log(`AgentX stack deployment: ${deployAgentXStack ? 'Enabled' : 'Disabled'}`);
console.log(`Agent Schedule stack deployment: ${deployScheduleStack ? 'Enabled' : 'Disabled'}`);

// Deploy the Schedule stack if enabled
if (deployScheduleStack) {
  new AgentScheduleStack(app, 'AgentScheduleStack', {
    env: { 
      account: process.env.CDK_DEFAULT_ACCOUNT, 
      region: process.env.CDK_DEFAULT_REGION || 'us-west-2' 
    },
    description: 'AgentX schedule stack with Lambda function and EventBridge scheduler',
    // Pass the AgentX stack if it was deployed
    agentXStack: deployAgentXStack ? agentXStack : undefined,
  });
}
