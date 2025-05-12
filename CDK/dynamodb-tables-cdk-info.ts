import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as cdk from 'aws-cdk-lib';
import { RemovalPolicy } from 'aws-cdk-lib';

// DynamoDB Tables CDK Configuration
// Generated on Sun May 11 18:00:54 MST 2025


/**
 * Table: WebSocketConnections
 */
const WebSocketConnections = new dynamodb.Table(this, 'WebSocketConnectionsTable', {
  tableName: 'WebSocketConnections',
  partitionKey: { name: 'connectionId', type: dynamodb.AttributeType.STRING },
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
  removalPolicy: RemovalPolicy.RETAIN, // Change as needed
});
// ------------------------------------------------------


/**
 * Table: perplexity_query_cache
 */
const perplexity_query_cache = new dynamodb.Table(this, 'perplexity_query_cacheTable', {
  tableName: 'perplexity_query_cache',
  partitionKey: { name: 'query_id', type: dynamodb.AttributeType.STRING },
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
  removalPolicy: RemovalPolicy.RETAIN, // Change as needed
});
// ------------------------------------------------------


/**
 * Table: query_analytics
 */
const query_analytics = new dynamodb.Table(this, 'query_analyticsTable', {
  tableName: 'query_analytics',
  partitionKey: { name: 'query_text', type: dynamodb.AttributeType.STRING },
  sortKey: { name: 'Zipcode', type: dynamodb.AttributeType.STRING },
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
  removalPolicy: RemovalPolicy.RETAIN, // Change as needed
});
// ------------------------------------------------------


/**
 * Table: referral_data
 */
const referral_data = new dynamodb.Table(this, 'referral_dataTable', {
  tableName: 'referral_data',
  partitionKey: { name: 'referral_id', type: dynamodb.AttributeType.STRING },
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
  removalPolicy: RemovalPolicy.RETAIN, // Change as needed
});
// ------------------------------------------------------


/**
 * Table: user_data
 */
const user_data = new dynamodb.Table(this, 'user_dataTable', {
  tableName: 'user_data',
  partitionKey: { name: 'user_id', type: dynamodb.AttributeType.STRING },
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
  stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
  removalPolicy: RemovalPolicy.RETAIN, // Change as needed
});

// Global Secondary Indexes for user_data
user_data.addGlobalSecondaryIndex({
  indexName: 'Phone-index',
  partitionKey: { name: 'Phone', type: dynamodb.AttributeType.STRING },
  projectionType: dynamodb.ProjectionType.ALL,
});

// ------------------------------------------------------

