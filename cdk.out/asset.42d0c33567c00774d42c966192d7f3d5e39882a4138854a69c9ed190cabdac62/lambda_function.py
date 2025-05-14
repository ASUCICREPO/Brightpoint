import json
import boto3
from datetime import datetime
import logging
from boto3.dynamodb.types import TypeSerializer

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
dynamodb_client = boto3.client('dynamodb')
user_table = dynamodb.Table('user_data')

def lambda_handler(event, context):
    """
    Backfill analytics data from existing user_data table.
    """
    logger.info("Starting backfill process")
    
    # Scan the user_data table
    response = user_table.scan()
    items = response.get('Items', [])
    
    # Handle pagination if there are more items
    while 'LastEvaluatedKey' in response:
        response = user_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
    
    logger.info(f"Found {len(items)} user records to process")
    
    processed_count = 0
    query_count = 0
    
    # Process each user
    for user in items:
        processed_count += 1
        user_id = None
        
        # Extract user_id if available
        if 'user_id' in user:
            if isinstance(user['user_id'], dict) and 'S' in user['user_id']:
                user_id = user['user_id']['S']
            else:
                user_id = str(user['user_id'])
        else:
            user_id = f"unknown-{processed_count}"
            
        logger.info(f"Processing user {processed_count}: {user_id}")
        
        # Skip if user doesn't have queries
        if 'queries' not in user:
            logger.info(f"User {user_id} has no queries field")
            continue
            
        queries = user['queries']
        
        # Check for DynamoDB format
        if isinstance(queries, dict):
            if 'M' in queries:
                # Handle DynamoDB native format
                queries = queries['M']
        
        if not isinstance(queries, dict):
            logger.info(f"Queries is not a dict for user {user_id}, type: {type(queries).__name__}")
            continue
        
        # Process each query entry in the user's queries map
        for query_id, query_data in queries.items():
            logger.info(f"Processing query {query_id}, type: {type(query_data).__name__}")
            
            if not isinstance(query_data, dict):
                logger.info(f"Query data is not a dict, skipping")
                continue
            
            # Handle the nested M structure if present
            query_details = query_data
            if 'M' in query_data:
                query_details = query_data['M']
            
            # Log the keys in the query details to understand structure
            if isinstance(query_details, dict):
                logger.info(f"Query details keys: {list(query_details.keys())}")
            
            # Extract query text from either 'query' or 'english_query'
            query_text = None
            if 'query' in query_details:
                if isinstance(query_details['query'], dict) and 'S' in query_details['query']:
                    query_text = query_details['query']['S']
                else:
                    query_text = str(query_details['query'])
            elif 'english_query' in query_details:
                if isinstance(query_details['english_query'], dict) and 'S' in query_details['english_query']:
                    query_text = query_details['english_query']['S']
                else:
                    query_text = str(query_details['english_query'])
            
            # Extract zipcode (handle both 'Zipcode' and 'zipcode')
            zipcode = None
            if 'Zipcode' in query_details:
                if isinstance(query_details['Zipcode'], dict) and 'S' in query_details['Zipcode']:
                    zipcode = query_details['Zipcode']['S']
                else:
                    zipcode = str(query_details['Zipcode'])
            elif 'zipcode' in query_details:
                if isinstance(query_details['zipcode'], dict) and 'S' in query_details['zipcode']:
                    zipcode = query_details['zipcode']['S']
                else:
                    zipcode = str(query_details['zipcode'])
            
            # Extract timestamp
            timestamp = None
            if 'timestamp' in query_details:
                if isinstance(query_details['timestamp'], dict) and 'S' in query_details['timestamp']:
                    timestamp = query_details['timestamp']['S']
                else:
                    timestamp = str(query_details['timestamp'])
            
            logger.info(f"Extracted - Query: {query_text}, Zipcode: {zipcode}, Timestamp: {timestamp}")
            
            # Skip if we don't have query text or zipcode
            if not query_text or not zipcode:
                logger.info(f"Missing query text or zipcode, skipping")
                continue
            
            # Update the analytics table - use the extracted values
            try:
                update_query_count(query_text, zipcode, timestamp)
                query_count += 1
                logger.info(f"Updated analytics for query: {query_text}, zipcode: {zipcode}")
            except Exception as e:
                logger.error(f"Error updating query count: {str(e)}")
                continue
        
        # Log progress
        if processed_count % 5 == 0:
            logger.info(f"Processed {processed_count} users, {query_count} queries so far")
    
    logger.info(f"Backfill complete. Processed {processed_count} users and {query_count} queries")
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Backfill complete. Processed {processed_count} users and {query_count} queries')
    }

def update_query_count(query_text, zipcode, timestamp=None):
    """
    Update the query count in the analytics table using low-level DynamoDB client
    to match the expected attribute type format.
    """
    current_time = datetime.now().isoformat()
    if not timestamp:
        timestamp = current_time
    
    # First get the current count if it exists
    try:
        response = dynamodb_client.get_item(
            TableName='query_analytics',
            Key={
                'query_text': {'S': query_text},
                'Zipcode': {'S': zipcode}
            }
        )
        
        count = 1
        first_seen = timestamp
        
        # If the item exists, increment the count
        if 'Item' in response:
            item = response['Item']
            if 'count' in item and 'N' in item['count']:
                count = int(item['count']['N']) + 1
            if 'first_seen' in item and 'S' in item['first_seen']:
                first_seen = item['first_seen']['S']
        
        # Update the item with proper DynamoDB attribute type format
        dynamodb_client.put_item(
            TableName='query_analytics',
            Item={
                'query_text': {'S': query_text},
                'Zipcode': {'S': zipcode},
                'count': {'N': str(count)},
                'first_seen': {'S': first_seen},
                'last_updated': {'S': current_time}
            }
        )
        
        logger.info(f"Updated count for query '{query_text}' in Zipcode '{zipcode}' to {count}")
        
    except Exception as e:
        logger.error(f"Error updating query count: {str(e)}")
        raise