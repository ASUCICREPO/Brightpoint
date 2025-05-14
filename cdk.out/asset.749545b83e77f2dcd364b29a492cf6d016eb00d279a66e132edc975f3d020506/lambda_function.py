import json
import boto3
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb_client = boto3.client('dynamodb')

def lambda_handler(event, context):
    """
    Process DynamoDB Stream records from user_data table and update analytics.
    """
    logger.info(f"Processing {len(event.get('Records', []))} records")
    
    for record in event.get('Records', []):
        # Only process INSERT and MODIFY events
        if record['eventName'] not in ['INSERT', 'MODIFY']:
            continue
            
        # Get the new image (the updated state of the item)
        if 'NewImage' not in record['dynamodb']:
            continue
            
        try:
            # Process the user data record
            process_user_record(record['dynamodb']['NewImage'])
        except Exception as e:
            logger.error(f"Error processing record: {str(e)}")
            logger.error(f"Record: {json.dumps(record, default=str)}")
            # Continue processing other records even if one fails
            continue
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Processed {len(event.get("Records", []))} records')
    }

def process_user_record(new_image):
    """
    Process a user record from the stream and update analytics.
    """
    # Check if the record has queries
    if 'queries' not in new_image:
        return
        
    queries = new_image['queries']
    
    # Handle DynamoDB format
    if 'M' in queries:
        queries = queries['M']
    
    if not isinstance(queries, dict):
        logger.info(f"Queries is not a dict, type: {type(queries).__name__}")
        return
    
    # Process each query entry
    for query_id, query_data in queries.items():
        # Log the query ID and type for debugging
        logger.info(f"Processing query {query_id}, type: {type(query_data).__name__}")
        
        if not isinstance(query_data, dict):
            logger.info(f"Query data is not a dict, skipping")
            continue
        
        # Handle the nested M structure if present
        query_details = query_data
        if 'M' in query_data:
            query_details = query_data['M']
        
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
        timestamp_str = None
        if 'timestamp' in query_details:
            if isinstance(query_details['timestamp'], dict) and 'S' in query_details['timestamp']:
                timestamp_str = query_details['timestamp']['S']
            else:
                timestamp_str = str(query_details['timestamp'])
        
        logger.info(f"Extracted - Query: {query_text}, Zipcode: {zipcode}, Timestamp: {timestamp_str}")
        
        # Skip if we don't have query text or zipcode
        if not query_text or not zipcode:
            logger.info(f"Missing query text or zipcode, skipping")
            continue
            
        # Update the analytics table
        update_query_count(query_text, zipcode, timestamp_str)

def update_query_count(query_text, zipcode, timestamp_str=None):
    """
    Update the query count in the analytics table using the low-level DynamoDB API
    to match the expected attribute type format.
    """
    current_time = datetime.now().isoformat()
    if not timestamp_str:
        timestamp_str = current_time
    
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
        first_seen = timestamp_str
        
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