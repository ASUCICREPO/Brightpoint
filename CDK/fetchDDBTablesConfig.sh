#!/bin/bash

# Colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Set AWS CLI profile
AWS_PROFILE="account-1087"  # Change if needed

# Output file for CDK-ready info
OUTPUT_FILE="dynamodb-tables-cdk-info.ts"

echo -e "${BLUE}==== DynamoDB Tables for CDK ====${NC}"

# Clear output file if it exists
> "$OUTPUT_FILE"

# Add imports to output file
echo "import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';" >> "$OUTPUT_FILE"
echo "import * as cdk from 'aws-cdk-lib';" >> "$OUTPUT_FILE"
echo "import { RemovalPolicy } from 'aws-cdk-lib';" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "// DynamoDB Tables CDK Configuration" >> "$OUTPUT_FILE"
echo "// Generated on $(date)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Get list of all DynamoDB tables
tables=$(aws dynamodb list-tables \
  --profile "$AWS_PROFILE" \
  --output json \
  --query 'TableNames')

# Check if result is not empty or null
if [[ "$tables" != "null" && "$tables" != "[]" ]]; then
  table_count=$(echo "$tables" | jq length)
  echo -e "Found ${GREEN}$table_count${NC} DynamoDB tables"
  
  echo "$tables" | jq -r '.[]' | while read -r table_name; do
    echo -e "\n${YELLOW}Table: $table_name${NC}"
    
    # Get detailed table description
    table_info=$(aws dynamodb describe-table \
      --table-name "$table_name" \
      --profile "$AWS_PROFILE" \
      --output json)
    
    # Extract key schema
    partition_key=$(echo "$table_info" | jq -r '.Table.KeySchema[] | select(.KeyType=="HASH") | .AttributeName')
    sort_key=$(echo "$table_info" | jq -r '.Table.KeySchema[] | select(.KeyType=="RANGE") | .AttributeName')
    
    # Extract attribute types
    partition_key_type=$(echo "$table_info" | jq -r --arg key "$partition_key" '.Table.AttributeDefinitions[] | select(.AttributeName==$key) | .AttributeType')
    sort_key_type=$(echo "$table_info" | jq -r --arg key "$sort_key" '.Table.AttributeDefinitions[] | select(.AttributeName==$key) | .AttributeType')
    
    # Convert DynamoDB attribute types to CDK types
    map_type() {
      local ddb_type="$1"
      case "$ddb_type" in
        S) echo "STRING" ;;
        N) echo "NUMBER" ;;
        B) echo "BINARY" ;;
        *) echo "STRING" ;; # Default
      esac
    }
    
    partition_key_cdk_type=$(map_type "$partition_key_type")
    sort_key_cdk_type=$(map_type "$sort_key_type")
    
    echo -e "  Partition Key: ${GREEN}$partition_key${NC} (${partition_key_cdk_type})"
    if [[ ! -z "$sort_key" && "$sort_key" != "null" ]]; then
      echo -e "  Sort Key: ${GREEN}$sort_key${NC} (${sort_key_cdk_type})"
    fi
    
    # Get billing mode
    billing_mode=$(echo "$table_info" | jq -r '.Table.BillingModeSummary.BillingMode // "PROVISIONED"')
    
    # Get provisioned throughput if applicable
    read_capacity=$(echo "$table_info" | jq -r '.Table.ProvisionedThroughput.ReadCapacityUnits // 0')
    write_capacity=$(echo "$table_info" | jq -r '.Table.ProvisionedThroughput.WriteCapacityUnits // 0')
    
    echo -e "  Billing Mode: ${GREEN}$billing_mode${NC}"
    if [[ "$billing_mode" == "PROVISIONED" ]]; then
      echo -e "  Read Capacity: $read_capacity"
      echo -e "  Write Capacity: $write_capacity"
    fi
    
    # Get Global Secondary Indexes
    gsi_count=$(echo "$table_info" | jq -r '.Table.GlobalSecondaryIndexes | length // 0')
    if [[ "$gsi_count" -gt 0 ]]; then
      echo -e "  ${BLUE}Global Secondary Indexes (${gsi_count}):${NC}"
      
      for ((i=0; i<gsi_count; i++)); do
        gsi_name=$(echo "$table_info" | jq -r ".Table.GlobalSecondaryIndexes[$i].IndexName")
        gsi_pk=$(echo "$table_info" | jq -r ".Table.GlobalSecondaryIndexes[$i].KeySchema[] | select(.KeyType==\"HASH\") | .AttributeName")
        gsi_sk=$(echo "$table_info" | jq -r ".Table.GlobalSecondaryIndexes[$i].KeySchema[] | select(.KeyType==\"RANGE\") | .AttributeName")
        
        # Get GSI attribute types
        gsi_pk_type=$(echo "$table_info" | jq -r --arg key "$gsi_pk" '.Table.AttributeDefinitions[] | select(.AttributeName==$key) | .AttributeType')
        gsi_sk_type=$(echo "$table_info" | jq -r --arg key "$gsi_sk" '.Table.AttributeDefinitions[] | select(.AttributeName==$key) | .AttributeType')
        
        gsi_pk_cdk_type=$(map_type "$gsi_pk_type")
        gsi_sk_cdk_type=$(map_type "$gsi_sk_type")
        
        # Get GSI throughput
        gsi_read=$(echo "$table_info" | jq -r ".Table.GlobalSecondaryIndexes[$i].ProvisionedThroughput.ReadCapacityUnits // 0")
        gsi_write=$(echo "$table_info" | jq -r ".Table.GlobalSecondaryIndexes[$i].ProvisionedThroughput.WriteCapacityUnits // 0")
        
        echo -e "    - $gsi_name"
        echo -e "      Partition Key: $gsi_pk (${gsi_pk_cdk_type})"
        if [[ ! -z "$gsi_sk" && "$gsi_sk" != "null" ]]; then
          echo -e "      Sort Key: $gsi_sk (${gsi_sk_cdk_type})"
        fi
        
        if [[ "$billing_mode" == "PROVISIONED" ]]; then
          echo -e "      Read Capacity: $gsi_read"
          echo -e "      Write Capacity: $gsi_write"
        fi
      done
    else
      echo -e "  ${BLUE}Global Secondary Indexes:${NC} None"
    fi
    
    # Get Local Secondary Indexes
    lsi_count=$(echo "$table_info" | jq -r '.Table.LocalSecondaryIndexes | length // 0')
    if [[ "$lsi_count" -gt 0 ]]; then
      echo -e "  ${BLUE}Local Secondary Indexes (${lsi_count}):${NC}"
      
      for ((i=0; i<lsi_count; i++)); do
        lsi_name=$(echo "$table_info" | jq -r ".Table.LocalSecondaryIndexes[$i].IndexName")
        lsi_sk=$(echo "$table_info" | jq -r ".Table.LocalSecondaryIndexes[$i].KeySchema[] | select(.KeyType==\"RANGE\") | .AttributeName")
        
        # Get LSI attribute type
        lsi_sk_type=$(echo "$table_info" | jq -r --arg key "$lsi_sk" '.Table.AttributeDefinitions[] | select(.AttributeName==$key) | .AttributeType')
        lsi_sk_cdk_type=$(map_type "$lsi_sk_type")
        
        echo -e "    - $lsi_name"
        echo -e "      Sort Key: $lsi_sk (${lsi_sk_cdk_type})"
      done
    else
      echo -e "  ${BLUE}Local Secondary Indexes:${NC} None"
    fi
    
    # Get Stream settings
    stream_enabled=$(echo "$table_info" | jq -r '.Table.StreamSpecification.StreamEnabled // false')
    if [[ "$stream_enabled" == "true" ]]; then
      stream_view_type=$(echo "$table_info" | jq -r '.Table.StreamSpecification.StreamViewType')
      echo -e "  ${BLUE}Stream:${NC} Enabled (${stream_view_type})"
    else
      echo -e "  ${BLUE}Stream:${NC} Disabled"
    fi
    
    # Get TTL settings
    ttl_info=$(aws dynamodb describe-time-to-live \
      --table-name "$table_name" \
      --profile "$AWS_PROFILE" \
      --output json)
    
    ttl_enabled=$(echo "$ttl_info" | jq -r '.TimeToLiveDescription.TimeToLiveStatus == "ENABLED"')
    if [[ "$ttl_enabled" == "true" ]]; then
      ttl_attribute=$(echo "$ttl_info" | jq -r '.TimeToLiveDescription.AttributeName')
      echo -e "  ${BLUE}TTL:${NC} Enabled (Attribute: $ttl_attribute)"
    else
      echo -e "  ${BLUE}TTL:${NC} Disabled"
    fi
    
    # Generate CDK code
    table_var_name=$(echo "$table_name" | tr '-' '_' | tr '.' '_')
    
    echo "" >> "$OUTPUT_FILE"
    echo "/**" >> "$OUTPUT_FILE"
    echo " * Table: $table_name" >> "$OUTPUT_FILE"
    echo " */" >> "$OUTPUT_FILE"
    echo "const $table_var_name = new dynamodb.Table(this, '${table_name}Table', {" >> "$OUTPUT_FILE"
    echo "  tableName: '$table_name'," >> "$OUTPUT_FILE"
    
    # Add partition key
    echo "  partitionKey: { name: '$partition_key', type: dynamodb.AttributeType.${partition_key_cdk_type} }," >> "$OUTPUT_FILE"
    
    # Add sort key if it exists
    if [[ ! -z "$sort_key" && "$sort_key" != "null" ]]; then
      echo "  sortKey: { name: '$sort_key', type: dynamodb.AttributeType.${sort_key_cdk_type} }," >> "$OUTPUT_FILE"
    fi
    
    # Add billing mode
    if [[ "$billing_mode" == "PAY_PER_REQUEST" ]]; then
      echo "  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST," >> "$OUTPUT_FILE"
    else
      echo "  billingMode: dynamodb.BillingMode.PROVISIONED," >> "$OUTPUT_FILE"
      echo "  readCapacity: $read_capacity," >> "$OUTPUT_FILE"
      echo "  writeCapacity: $write_capacity," >> "$OUTPUT_FILE"
    fi
    
    # Add stream if enabled
    if [[ "$stream_enabled" == "true" ]]; then
      echo "  stream: dynamodb.StreamViewType.${stream_view_type}," >> "$OUTPUT_FILE"
    fi
    
    # Add removal policy for CDK (this is not from the existing table)
    echo "  removalPolicy: RemovalPolicy.RETAIN, // Change as needed" >> "$OUTPUT_FILE"
    
    echo "});" >> "$OUTPUT_FILE"
    
    # Add global secondary indexes if they exist
    if [[ "$gsi_count" -gt 0 ]]; then
      echo "" >> "$OUTPUT_FILE"
      echo "// Global Secondary Indexes for $table_name" >> "$OUTPUT_FILE"
      
      for ((i=0; i<gsi_count; i++)); do
        gsi_name=$(echo "$table_info" | jq -r ".Table.GlobalSecondaryIndexes[$i].IndexName")
        gsi_pk=$(echo "$table_info" | jq -r ".Table.GlobalSecondaryIndexes[$i].KeySchema[] | select(.KeyType==\"HASH\") | .AttributeName")
        gsi_sk=$(echo "$table_info" | jq -r ".Table.GlobalSecondaryIndexes[$i].KeySchema[] | select(.KeyType==\"RANGE\") | .AttributeName")
        
        # Get GSI attribute types
        gsi_pk_type=$(echo "$table_info" | jq -r --arg key "$gsi_pk" '.Table.AttributeDefinitions[] | select(.AttributeName==$key) | .AttributeType')
        gsi_sk_type=$(echo "$table_info" | jq -r --arg key "$gsi_sk" '.Table.AttributeDefinitions[] | select(.AttributeName==$key) | .AttributeType')
        
        gsi_pk_cdk_type=$(map_type "$gsi_pk_type")
        gsi_sk_cdk_type=$(map_type "$gsi_sk_type")
        
        # Get GSI throughput
        gsi_read=$(echo "$table_info" | jq -r ".Table.GlobalSecondaryIndexes[$i].ProvisionedThroughput.ReadCapacityUnits // 0")
        gsi_write=$(echo "$table_info" | jq -r ".Table.GlobalSecondaryIndexes[$i].ProvisionedThroughput.WriteCapacityUnits // 0")
        
        gsi_var_name=$(echo "$gsi_name" | tr '-' '_' | tr '.' '_')
        
        echo "$table_var_name.addGlobalSecondaryIndex({" >> "$OUTPUT_FILE"
        echo "  indexName: '$gsi_name'," >> "$OUTPUT_FILE"
        echo "  partitionKey: { name: '$gsi_pk', type: dynamodb.AttributeType.${gsi_pk_cdk_type} }," >> "$OUTPUT_FILE"
        
        if [[ ! -z "$gsi_sk" && "$gsi_sk" != "null" ]]; then
          echo "  sortKey: { name: '$gsi_sk', type: dynamodb.AttributeType.${gsi_sk_cdk_type} }," >> "$OUTPUT_FILE"
        fi
        
        if [[ "$billing_mode" == "PROVISIONED" ]]; then
          echo "  readCapacity: $gsi_read," >> "$OUTPUT_FILE"
          echo "  writeCapacity: $gsi_write," >> "$OUTPUT_FILE"
        fi
        
        # Add projectionType - assuming ALL by default
        echo "  projectionType: dynamodb.ProjectionType.ALL," >> "$OUTPUT_FILE"
        
        echo "});" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
      done
    fi
    
    # Add local secondary indexes if they exist
    if [[ "$lsi_count" -gt 0 ]]; then
      echo "// Local Secondary Indexes for $table_name" >> "$OUTPUT_FILE"
      echo "// Note: LSIs must be added at table creation time, not afterwards" >> "$OUTPUT_FILE"
      echo "// Ensure your table definition includes:" >> "$OUTPUT_FILE"
      echo "// localSecondaryIndexes: [" >> "$OUTPUT_FILE"
      
      for ((i=0; i<lsi_count; i++)); do
        lsi_name=$(echo "$table_info" | jq -r ".Table.LocalSecondaryIndexes[$i].IndexName")
        lsi_sk=$(echo "$table_info" | jq -r ".Table.LocalSecondaryIndexes[$i].KeySchema[] | select(.KeyType==\"RANGE\") | .AttributeName")
        
        # Get LSI attribute type
        lsi_sk_type=$(echo "$table_info" | jq -r --arg key "$lsi_sk" '.Table.AttributeDefinitions[] | select(.AttributeName==$key) | .AttributeType')
        lsi_sk_cdk_type=$(map_type "$lsi_sk_type")
        
        echo "//   {" >> "$OUTPUT_FILE"
        echo "//     indexName: '$lsi_name'," >> "$OUTPUT_FILE"
        echo "//     sortKey: { name: '$lsi_sk', type: dynamodb.AttributeType.${lsi_sk_cdk_type} }," >> "$OUTPUT_FILE"
        echo "//     projectionType: dynamodb.ProjectionType.ALL," >> "$OUTPUT_FILE"
        echo "//   }," >> "$OUTPUT_FILE"
      done
      
      echo "// ]," >> "$OUTPUT_FILE"
      echo "" >> "$OUTPUT_FILE"
    fi
    
    # Add TTL if enabled
    if [[ "$ttl_enabled" == "true" ]]; then
      echo "// Time to Live (TTL) configuration" >> "$OUTPUT_FILE"
      echo "$table_var_name.addTimeToLiveAttribute('$ttl_attribute');" >> "$OUTPUT_FILE"
      echo "" >> "$OUTPUT_FILE"
    fi
    
    echo "// ------------------------------------------------------" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
  done
  
  echo -e "\n${GREEN}CDK-ready information has been saved to ${OUTPUT_FILE}${NC}"
else
  echo -e "${RED}No DynamoDB tables found.${NC}"
fi