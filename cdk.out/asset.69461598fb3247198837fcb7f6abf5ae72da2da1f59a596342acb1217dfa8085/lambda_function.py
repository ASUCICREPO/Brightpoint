import json
import boto3
from datetime import datetime, timedelta
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb_client = boto3.client('dynamodb')

def lambda_handler(event, context):
    """
    Main handler that routes to appropriate function based on event type
    """
    try:
        # Check if this is a WebSocket event
        if 'requestContext' in event and 'routeKey' in event.get('requestContext', {}):
            return handle_websocket_event(event, context)

        # Otherwise, handle it as a REST API event
        else:
            return handle_rest_api_event(event, context)
    except Exception as e:
        logger.error(f"Error in main handler: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": str(e)
            })
        }

def handle_websocket_event(event, context):
    """
    Handle incoming WebSocket API events
    """
    try:
        # Get WebSocket connection info
        connection_id = event['requestContext']['connectionId']
        route_key = event['requestContext']['routeKey']
        domain_name = event['requestContext']['domainName']
        stage = event['requestContext']['stage']

        # Initialize API Gateway Management API client
        endpoint_url = f"https://{domain_name}/{stage}"
        api_gateway_client = boto3.client('apigatewaymanagementapi', endpoint_url=endpoint_url)

        # Handle different route keys
        if route_key == '$connect':
            # Handle connection event
            logger.info(f"New WebSocket connection: {connection_id}")
            return {"statusCode": 200}

        elif route_key == '$disconnect':
            # Handle disconnection event
            logger.info(f"WebSocket disconnected: {connection_id}")
            return {"statusCode": 200}

        elif route_key == '$default' or route_key == 'getAnalytics':
            # Process the analytics request
            message = json.loads(event.get('body', '{}'))

            # Set default parameters
            now = datetime.now()
            default_start_date = (now - timedelta(days=30)).isoformat()
            default_end_date = now.isoformat()

            # Extract parameters
            start_date = message.get('start_date', default_start_date)
            end_date = message.get('end_date', default_end_date)
            zipcodes = message.get('zipcodes', [])
            limit = int(message.get('limit', 10))

            # Load data from DynamoDB
            user_data = load_user_data()
            query_analytics_data = load_query_analytics_data()
            perplexity_cache_data = load_perplexity_query_cache_data()

            # Process analytics
            query_data = process_query_frequency(query_analytics_data, zipcodes, start_date, end_date, limit)
            user_count, referral_counts = process_user_and_referral_counts(user_data, zipcodes, start_date, end_date)
            feedback_stats = process_referral_feedback_statistics(user_data)
            perplexity_stats = process_perplexity_query_statistics(perplexity_cache_data, zipcodes, start_date, end_date, limit)

            # Prepare response
            response_body = {
                "filters": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "zipcodes": zipcodes,
                    "limit": limit
                },
                "query_frequency": query_data,
                "total_queries": len(query_data),
                "user_count": user_count,
                "referral_counts": referral_counts,
                "feedback_statistics": feedback_stats,
                "perplexity_queries": perplexity_stats,
                "total_perplexity_queries": len(perplexity_stats)
            }

            # Send response back via WebSocket
            api_gateway_client.post_to_connection(
                ConnectionId=connection_id,
                Data=json.dumps(response_body).encode('utf-8')
            )

            return {"statusCode": 200}

        else:
            # Unknown route
            logger.warning(f"Unknown WebSocket route: {route_key}")
            return {"statusCode": 400}

    except Exception as e:
        logger.error(f"Error in WebSocket handler: {str(e)}")

        # Try to send error message back to client
        try:
            if 'connection_id' in locals() and 'api_gateway_client' in locals():
                api_gateway_client.post_to_connection(
                    ConnectionId=connection_id,
                    Data=json.dumps({"error": str(e)}).encode('utf-8')
                )
        except Exception as post_error:
            logger.error(f"Error sending error message via WebSocket: {str(post_error)}")

        return {"statusCode": 500}

def handle_rest_api_event(event, context):
    """
    Handle incoming REST API events (original functionality)
    """
    try:
        # Parse request body
        if 'body' in event:
            try:
                body = json.loads(event['body'])
            except:
                body = {}
        else:
            body = event

        # Set default parameters
        now = datetime.now()
        default_start_date = (now - timedelta(days=30)).isoformat()
        default_end_date = now.isoformat()

        # Extract parameters from the JSON body
        start_date = body.get('start_date', default_start_date)
        end_date = body.get('end_date', default_end_date)
        zipcodes = body.get('zipcodes', [])
        limit = int(body.get('limit', 10))

        # Load all data upfront
        user_data = load_user_data()
        query_analytics_data = load_query_analytics_data()
        perplexity_cache_data = load_perplexity_query_cache_data()

        # Process all analytics
        # 1. Query frequency data
        query_data = process_query_frequency(query_analytics_data, zipcodes, start_date, end_date, limit)

        # 2. User and referral statistics
        user_count, referral_counts = process_user_and_referral_counts(user_data, zipcodes, start_date, end_date)

        # 3. Referral feedback statistics
        feedback_stats = process_referral_feedback_statistics(user_data)

        # 4. Perplexity query statistics
        perplexity_stats = process_perplexity_query_statistics(perplexity_cache_data, zipcodes, start_date, end_date, limit)

        # Return comprehensive results
        response_body = {
            "filters": {
                "start_date": start_date,
                "end_date": end_date,
                "zipcodes": zipcodes,
                "limit": limit
            },
            "query_frequency": query_data,
            "total_queries": len(query_data),
            "user_count": user_count,
            "referral_counts": referral_counts,
            "feedback_statistics": feedback_stats,
            "perplexity_queries": perplexity_stats,
            "total_perplexity_queries": len(perplexity_stats)
        }

        # Log the structure of the response for debugging
        logger.info(f"Response structure: {list(response_body.keys())}")

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(response_body)
        }

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": str(e)
            })
        }

# Helper functions to load data once
def load_user_data():
    """Load all user data from DynamoDB once to avoid multiple scans"""
    try:
        response = dynamodb_client.scan(TableName='user_data')
        items = response.get('Items', [])

        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = dynamodb_client.scan(
                TableName='user_data',
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response.get('Items', []))

        logger.info(f"Retrieved {len(items)} users from user_data table")
        return items
    except Exception as e:
        logger.error(f"Error loading user data: {str(e)}")
        return []

def load_query_analytics_data():
    """Load all query analytics data from DynamoDB once"""
    try:
        response = dynamodb_client.scan(TableName='query_analytics')
        items = response.get('Items', [])

        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = dynamodb_client.scan(
                TableName='query_analytics',
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response.get('Items', []))

        logger.info(f"Retrieved {len(items)} items from query_analytics table")
        return items
    except Exception as e:
        logger.error(f"Error loading query analytics data: {str(e)}")
        return []

def load_perplexity_query_cache_data():
    """Load all perplexity query cache data from DynamoDB once"""
    try:
        response = dynamodb_client.scan(TableName='perplexity_query_cache')
        items = response.get('Items', [])

        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = dynamodb_client.scan(
                TableName='perplexity_query_cache',
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response.get('Items', []))

        logger.info(f"Retrieved {len(items)} items from perplexity_query_cache table")
        return items
    except Exception as e:
        logger.error(f"Error loading perplexity query cache data: {str(e)}")
        return []

# Processing functions that work with the pre-loaded data
def process_query_frequency(items, zipcodes, start_date, end_date, limit):
    """Process query frequency data using pre-loaded data"""
    try:
        # Process and filter the items
        query_counts = {}

        for item in items:
            # Extract values from DynamoDB attribute type format
            query_text = None
            zipcode = None
            count = 0
            first_seen = None

            if 'query_text' in item and 'S' in item['query_text']:
                query_text = item['query_text']['S']

            if 'Zipcode' in item and 'S' in item['Zipcode']:
                zipcode = item['Zipcode']['S']

            if 'count' in item and 'N' in item['count']:
                count = int(item['count']['N'])

            if 'first_seen' in item and 'S' in item['first_seen']:
                first_seen = item['first_seen']['S']

            # Skip if missing essential data
            if not query_text or not zipcode:
                continue

            # Apply zipcode filter if provided
            if zipcodes and zipcode not in zipcodes:
                continue

            # Apply date filter if present
            if first_seen and start_date and end_date:
                if not (start_date <= first_seen <= end_date):
                    continue

            # Aggregate counts by query_text
            if query_text in query_counts:
                query_counts[query_text] += count
            else:
                query_counts[query_text] = count

        # Convert to list and sort by count (descending)
        sorted_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)

        # Limit the results
        result = []
        for query_text, count in sorted_queries[:limit]:
            result.append({
                'query': query_text,
                'count': count
            })

        logger.info(f"Processed {len(result)} filtered query results")
        return result
    except Exception as e:
        logger.error(f"Error processing query frequency: {str(e)}")
        return []

def process_referral_feedback_statistics(items):
    """Process referral feedback statistics using pre-loaded data"""
    try:
        # Initialize counters
        useful_count = 0
        not_useful_count = 0
        pending_count = 0

        # Process each user
        for user in items:
            # Check if user has referrals
            if 'referrals' in user and 'M' in user['referrals']:
                referrals = user['referrals']['M']
                for referral_id, referral_data in referrals.items():
                    if 'M' not in referral_data:
                        continue

                    referral_details = referral_data['M']

                    # Check if feedback exists
                    has_feedback = False
                    feedback_value = None

                    if 'feedback' in referral_details and 'S' in referral_details['feedback']:
                        has_feedback = True
                        feedback_value = referral_details['feedback']['S']

                    # Count based on feedback value
                    if has_feedback:
                        if feedback_value.lower() == 'yes':
                            useful_count += 1
                        elif feedback_value.lower() == 'no':
                            not_useful_count += 1
                        else:
                            # Any other feedback value is counted as pending
                            pending_count += 1
                    else:
                        # No feedback means pending
                        pending_count += 1

        total_referrals = useful_count + not_useful_count + pending_count

        logger.info(f"Processed feedback statistics: Useful: {useful_count}, Not Useful: {not_useful_count}, Pending: {pending_count}")

        return {
            "useful": useful_count,
            "not_useful": not_useful_count,
            "pending": pending_count,
            "total": total_referrals
        }
    except Exception as e:
        logger.error(f"Error processing referral feedback statistics: {str(e)}")
        return {
            "useful": 0,
            "not_useful": 0,
            "pending": 0,
            "total": 0
        }

def process_perplexity_query_statistics(items, zipcodes, start_date, end_date, limit):
    """Process perplexity query statistics using pre-loaded data"""
    try:
        # Filter items by zipcode and timeframe
        filtered_items = []
        for item in items:
            # Extract fields we need
            item_zipcode = None
            item_timestamp = None

            if 'zipcode' in item and 'S' in item['zipcode']:
                item_zipcode = item['zipcode']['S']

            if 'timestamp' in item and 'S' in item['timestamp']:
                item_timestamp = item['timestamp']['S']

            # Apply zipcode filter if provided
            if zipcodes and item_zipcode and item_zipcode not in zipcodes:
                continue

            # Apply date filter if provided
            if start_date and end_date and item_timestamp:
                if not (start_date <= item_timestamp <= end_date):
                    continue

            # If it passed all filters, add to our filtered list
            filtered_items.append(item)

        logger.info(f"Filtered to {len(filtered_items)} perplexity queries based on criteria")

        # Create a dictionary to aggregate queries
        query_aggregates = {}

        for item in filtered_items:
            # Extract all relevant fields
            original_query = None
            english_query = None
            language = None
            zipcode = None
            timestamp = None

            if 'original_query' in item and 'S' in item['original_query']:
                original_query = item['original_query']['S']

            if 'normalized_query' in item and 'S' in item['normalized_query']:
                english_query = item['normalized_query']['S']

            if 'language' in item and 'S' in item['language']:
                language = item['language']['S']

            if 'zipcode' in item and 'S' in item['zipcode']:
                zipcode = item['zipcode']['S']

            if 'timestamp' in item and 'S' in item['timestamp']:
                timestamp = item['timestamp']['S']

            # Skip if missing essential data
            if not original_query:
                continue

            # Use original_query as the key for aggregation
            query_key = original_query.lower()

            if query_key in query_aggregates:
                query_aggregates[query_key]['count'] += 1
            else:
                query_aggregates[query_key] = {
                    'original_query': original_query,
                    'english_query': english_query,
                    'language': language,
                    'zipcode': zipcode,
                    'timestamp': timestamp,
                    'count': 1
                }

        # Convert to a list and sort by count in descending order
        result = [query_data for query_data in query_aggregates.values()]
        result.sort(key=lambda x: x['count'], reverse=True)

        # Apply the limit
        result = result[:limit]

        logger.info(f"Processed {len(result)} aggregated perplexity query results")
        return result
    except Exception as e:
        logger.error(f"Error processing perplexity query statistics: {str(e)}")
        return []

def process_user_and_referral_counts(items, zipcodes, start_date, end_date):
    """Process user and referral counts using pre-loaded data"""
    try:
        user_count = 0
        service_category_counts = {}

        # Process each user
        for user in items:
            user_has_matching_zipcode = False
            user_has_matching_query = False

            # Check if user has Zipcode matching filter
            if 'Zipcode' in user and 'S' in user['Zipcode']:
                user_zipcode = user['Zipcode']['S']
                if not zipcodes or user_zipcode in zipcodes:
                    user_has_matching_zipcode = True

            # Check if user has queries matching date filter
            if 'queries' in user and 'M' in user['queries']:
                queries = user['queries']['M']
                for query_id, query_data in queries.items():
                    if 'M' not in query_data:
                        continue

                    query_details = query_data['M']

                    # Extract zipcode from query if present
                    query_zipcode = None
                    if 'zipcode' in query_details and 'S' in query_details['zipcode']:
                        query_zipcode = query_details['zipcode']['S']

                    # Check if query zipcode matches filter
                    if zipcodes and query_zipcode and query_zipcode not in zipcodes:
                        continue

                    # Extract timestamp if present
                    timestamp = None
                    if 'timestamp' in query_details and 'S' in query_details['timestamp']:
                        timestamp = query_details['timestamp']['S']

                    # Check if timestamp is within date range
                    if timestamp and start_date and end_date:
                        if start_date <= timestamp <= end_date:
                            user_has_matching_query = True
                            break

            # Count user if they match filters
            if (user_has_matching_zipcode or user_has_matching_query):
                user_count += 1

            # Process referrals if present
            if 'referrals' in user and 'M' in user['referrals']:
                referrals = user['referrals']['M']
                for referral_id, referral_data in referrals.items():
                    if 'M' not in referral_data:
                        continue

                    referral_details = referral_data['M']

                    # Extract service category
                    service_category = "Other"
                    if 'serviceCategory' in referral_details and 'S' in referral_details['serviceCategory']:
                        service_category = referral_details['serviceCategory']['S']

                    # Extract zipcode
                    referral_zipcode = None
                    if 'zipcode' in referral_details and 'S' in referral_details['zipcode']:
                        referral_zipcode = referral_details['zipcode']['S']

                    # Apply zipcode filter
                    if zipcodes and referral_zipcode and referral_zipcode not in zipcodes:
                        continue

                    # Extract timestamp
                    timestamp = None
                    if 'timestamp' in referral_details and 'S' in referral_details['timestamp']:
                        timestamp = referral_details['timestamp']['S']

                    # Apply date filter
                    if timestamp and start_date and end_date:
                        if not (start_date <= timestamp <= end_date):
                            continue

                    # Count referral by service category
                    if service_category in service_category_counts:
                        service_category_counts[service_category] += 1
                    else:
                        service_category_counts[service_category] = 1

        # Convert service category counts to list for result
        referral_counts = []
        for category, count in service_category_counts.items():
            referral_counts.append({
                "category": category,
                "count": count
            })

        # Sort referral counts by count (descending)
        referral_counts = sorted(referral_counts, key=lambda x: x["count"], reverse=True)

        logger.info(f"Processed {user_count} users and {sum(count['count'] for count in referral_counts if count.get('count'))} referrals matching filters")

        return user_count, referral_counts
    except Exception as e:
        logger.error(f"Error processing user and referral counts: {str(e)}")
        return 0, []