import json
import boto3
import os
import logging
import traceback
from decimal import Decimal
import bedrockAgent  # Import the bedrockAgent module
import uuid
from datetime import datetime

# Custom JSON encoder for Decimal types
class DecimalEncoder(json.JSONEncoder):
    """Helper class to convert a DynamoDB item to JSON."""
    def default(self, o):
        if isinstance(o, Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize the API Gateway Management API client outside the handler for reuse
api_gateway_management_client = None
# Initialize AWS Translate client
translate_client = boto3.client('translate')
# Initialize DynamoDB client
dynamodb_client = boto3.client('dynamodb')

# Initialize AWS Lambda client for calling Perplexity Lambda
lambda_client = boto3.client('lambda', region_name="us-east-1")
PERPLEXITY_LAMBDA_ARN = "arn:aws:lambda:us-east-1:108782065617:function:perplexityLambda"

def lambda_handler(event, context):
    """
    Lambda handler for both REST API and WebSocket API

    For REST API - Expected input:
    {
        "user_id": "unique-user-id",
        "zipcode": "60605",  (optional)
        "user_query": "Where can I find food pantries?",
        "language": "english"  (optional, defaults to english, supports "polish" and "spanish")
    }

    For WebSocket - Expected input varies by route:
    - $connect: Connection establishment
    - $disconnect: Connection termination
    - query: {action: "query", user_id: "unique-user-id", zipcode: "60605", user_query: "Where can I find food pantries?", language: "english"}
    """
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Determine if this is a WebSocket event or REST API event
        if 'requestContext' in event and 'connectionId' in event.get('requestContext', {}):
            return handle_websocket_event(event, context)
        else:
            return handle_rest_event(event, context)
    except Exception as e:
        logger.error(f"Unhandled error in lambda_handler: {str(e)}")
        logger.error(traceback.format_exc())
        return format_response(500, {
            'message': "An unexpected error occurred",
            'error': str(e)
        })

def update_user_query_history(user_id, user_query, original_query, response_data, zipcode=None, language='english'):
    """
    Update the user's query history in the user_data table

    Args:
        user_id (str): The ID of the user
        user_query (str): The query in English
        original_query (str): The original query in its original language
        response_data (dict): The response data
        zipcode (str, optional): User's zipcode
        language (str): Language of the query
    """
    try:
        timestamp = datetime.now().isoformat()
        query_id = str(uuid.uuid4())

        # Check if user exists
        response = dynamodb_client.get_item(
            TableName='user_data',
            Key={
                'user_id': {'S': user_id}
            }
        )

        user_exists = 'Item' in response

        if user_exists:
            # Check if queries map already exists
            check_response = dynamodb_client.get_item(
                TableName='user_data',
                Key={
                    'user_id': {'S': user_id}
                },
                ProjectionExpression='queries'
            )

            queries_exists = 'Item' in check_response and 'queries' in check_response['Item']

            if queries_exists:
                # Add to existing queries map
                dynamodb_client.update_item(
                    TableName='user_data',
                    Key={
                        'user_id': {'S': user_id}
                    },
                    UpdateExpression="SET queries.#qid = :qdata",
                    ExpressionAttributeNames={
                        '#qid': query_id
                    },
                    ExpressionAttributeValues={
                        ':qdata': {
                            'M': {
                                'query': {'S': original_query},  # Store original query
                                'english_query': {'S': user_query},  # Store English translation
                                'timestamp': {'S': timestamp},
                                'source': {'S': 'bedrock-agent'},
                                'zipcode': {'S': zipcode if zipcode else "none"},
                                'language': {'S': language},
                                'response': {'S': json.dumps(response_data, cls=DecimalEncoder)}
                            }
                        }
                    }
                )
            else:
                # Create queries map with this query
                dynamodb_client.update_item(
                    TableName='user_data',
                    Key={
                        'user_id': {'S': user_id}
                    },
                    UpdateExpression="SET queries = :qmap",
                    ExpressionAttributeValues={
                        ':qmap': {
                            'M': {
                                query_id: {
                                    'M': {
                                        'query': {'S': original_query},  # Store original query
                                        'english_query': {'S': user_query},  # Store English translation
                                        'timestamp': {'S': timestamp},
                                        'source': {'S': 'bedrock-agent'},
                                        'zipcode': {'S': zipcode if zipcode else "none"},
                                        'language': {'S': language},
                                        'response': {'S': json.dumps(response_data, cls=DecimalEncoder)}
                                    }
                                }
                            }
                        }
                    }
                )
        else:
            # Create new user with query history
            dynamodb_client.put_item(
                TableName='user_data',
                Item={
                    'user_id': {'S': user_id},
                    'queries': {
                        'M': {
                            query_id: {
                                'M': {
                                    'query': {'S': original_query},  # Store original query
                                    'english_query': {'S': user_query},  # Store English translation
                                    'timestamp': {'S': timestamp},
                                    'source': {'S': 'bedrock-agent'},
                                    'zipcode': {'S': zipcode if zipcode else "none"},
                                    'language': {'S': language},
                                    'response': {'S': json.dumps(response_data, cls=DecimalEncoder)}
                                }
                            }
                        }
                    }
                }
            )

        logger.info(f"Successfully updated query history for user {user_id}")

    except Exception as e:
        logger.error(f"Error updating user query history: {str(e)}")

def handle_websocket_event(event, context):
    """
    Handle WebSocket events
    """
    connection_id = event['requestContext']['connectionId']
    domain_name = event['requestContext']['domainName']
    stage = event['requestContext']['stage']
    route_key = event['requestContext']['routeKey']

    logger.info(f"WebSocket event: {route_key}, Connection ID: {connection_id}")

    try:
        # Handle standard WebSocket routes
        if route_key == '$connect':
            # Handle connection request
            logger.info(f"New WebSocket connection: {connection_id}")
            return {'statusCode': 200, 'body': 'Connected'}

        elif route_key == '$disconnect':
            # Handle disconnect
            logger.info(f"WebSocket disconnected: {connection_id}")
            return {'statusCode': 200, 'body': 'Disconnected'}

        elif route_key == 'query':
            # Process a query request similar to REST API
            return process_query_websocket(event, connection_id, domain_name, stage)

        else:
            # Unknown route
            logger.warning(f"Unknown WebSocket route: {route_key}")
            send_to_connection(connection_id, domain_name, stage, {
                'error': f'Unknown route: {route_key}'
            })
            return {'statusCode': 400, 'body': 'Unknown route'}

    except Exception as e:
        logger.error(f"Error handling WebSocket event: {str(e)}")
        logger.error(traceback.format_exc())

        try:
            # Try to send error to connection
            send_to_connection(connection_id, domain_name, stage, {
                'error': 'Internal server error',
                'message': str(e)
            })
        except Exception as send_error:
            logger.error(f"Error sending error message: {str(send_error)}")

        return {'statusCode': 500, 'body': 'Internal server error'}

def translate_text(text, source_language, target_language):
    """
    Translate text using AWS Translate

    Args:
        text (str): Text to translate
        source_language (str): Source language code
        target_language (str): Target language code

    Returns:
        str: Translated text
    """
    try:
        response = translate_client.translate_text(
            Text=text,
            SourceLanguageCode=source_language,
            TargetLanguageCode=target_language
        )
        return response['TranslatedText']
    except Exception as e:
        logger.error(f"Error translating text: {str(e)}")
        logger.error(traceback.format_exc())
        # Return original text if translation fails
        return text

def get_language_code(language):
    """
    Convert language name to AWS Translate language code

    Args:
        language (str): Language name (english, polish, spanish)

    Returns:
        str: Language code for AWS Translate
    """
    language_codes = {
        "english": "en",
        "polish": "pl",
        "spanish": "es"
    }
    return language_codes.get(language.lower(), "en")

def convert_decimal(obj):
    """
    Convert Decimal types to int or float recursively

    Args:
        obj: Any object that might contain Decimal values

    Returns:
        Object with Decimal values converted to int or float
    """
    if isinstance(obj, list):
        return [convert_decimal(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj

def translate_response_data(response_data, target_language_code):
    """
    Recursively translate all string values in a nested dictionary/list.
    Only the values are translated, keys remain in English.

    Args:
        response_data: Dictionary or list containing response data
        target_language_code: Target language code for translation

    Returns:
        A new structure with translated string values
    """
    # Skip translation for empty or None values
    if response_data is None:
        return None

    # First convert any Decimal types to int or float
    response_data = convert_decimal(response_data)

    # Handle dictionary objects
    if isinstance(response_data, dict):
        result = {}
        # Process each key-value pair
        for key, value in response_data.items():
            # Skip translation for technical fields that should stay in English
            if key in ['id', 'referral_id', 'service_area_zip_code', 'zipcode', 'phone', 'status', 'language'] or not value:
                result[key] = value
                continue

            # Translate string values
            if isinstance(value, str) and value.strip() and value != "-":
                try:
                    logger.debug(f"Translating '{key}': '{value}' to {target_language_code}")
                    result[key] = translate_text(value, "en", target_language_code)
                    logger.debug(f"Translated '{key}' result: '{result[key]}'")
                except Exception as e:
                    logger.error(f"Translation error for key '{key}': {str(e)}")
                    result[key] = value  # Keep original on error
            # Recursively process nested dictionaries and lists
            elif isinstance(value, (dict, list)):
                result[key] = translate_response_data(value, target_language_code)
            else:
                result[key] = value
        return result

    # Handle list objects
    elif isinstance(response_data, list):
        result = []
        for item in response_data:
            # Translate string values in the list
            if isinstance(item, str) and item.strip():
                try:
                    logger.debug(f"Translating list item: '{item}' to {target_language_code}")
                    translated_item = translate_text(item, "en", target_language_code)
                    result.append(translated_item)
                    logger.debug(f"Translated list item result: '{translated_item}'")
                except Exception as e:
                    logger.error(f"Translation error for list item: {str(e)}")
                    result.append(item)  # Keep original on error
            # Recursively process nested dictionaries and lists in the list
            elif isinstance(item, (dict, list)):
                result.append(translate_response_data(item, target_language_code))
            else:
                result.append(item)
        return result

    # Return primitive types unchanged
    else:
        return response_data

def call_perplexity_lambda(user_query, user_id, zipcode=None, language='english'):
    """
    Call the Perplexity Lambda function as a fallback when no services are found

    Args:
        user_query: The user's original query
        user_id: The ID of the user
        zipcode: Optional zipcode
        language: Language for the response

    Returns:
        Response from Perplexity Lambda
    """
    try:
        logger.info(f"Calling Perplexity Lambda for query: {user_query}")

        # Prepare payload for Perplexity Lambda
        payload = {
            "user_query": user_query,
            "user_id": user_id,
            "zipcode": zipcode,
            "language": language
        }

        # Invoke Perplexity Lambda
        response = lambda_client.invoke(
            FunctionName=PERPLEXITY_LAMBDA_ARN,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

        # Parse response and return it directly without additional processing
        return json.loads(response['Payload'].read().decode('utf-8'))

    except Exception as e:
        logger.error(f"Error calling Perplexity Lambda: {str(e)}")
        logger.error(traceback.format_exc())
        return {"statusCode": 500, "body": json.dumps({"status": "error", "message": f"Error calling Perplexity service: {str(e)}"})}

def process_query_websocket(event, connection_id, domain_name, stage):
    """
    Process a query from WebSocket and send the result back
    """
    try:
        # Parse body from the WebSocket message
        body = json.loads(event.get('body', '{}'))

        # Extract parameters
        user_id = body.get('user_id')
        user_query = body.get('user_query', '')
        original_query = user_query  # Save original query before any translation
        zipcode = body.get('zipcode')
        language = body.get('language', 'english').lower()  # Default to English

        logger.info(f"WebSocket query - User ID: {user_id}, Query: {user_query}, Language: {language}")

        # Validate input
        if not user_id:
            error_message = 'Missing required parameter: user_id'
            if language != 'english':
                target_lang = get_language_code(language)
                error_message = translate_text(error_message, "en", target_lang)

            send_to_connection(connection_id, domain_name, stage, {
                'error': error_message
            })
            return {'statusCode': 400, 'body': 'Missing user_id'}

        if not user_query:
            error_message = "I didn't receive a question. Please provide a query about services you're looking for."
            # Translate error message if needed
            if language != 'english':
                target_lang = get_language_code(language)
                error_message = translate_text(error_message, "en", target_lang)

            send_to_connection(connection_id, domain_name, stage, {
                'user_id': user_id,
                'zipcode': zipcode,
                'language': language,
                'message': error_message
            })
            return {'statusCode': 400, 'body': 'Missing user_query'}

        # Use bedrockAgent functions to get DynamoDB results
        extracted_data = bedrockAgent.extract_categories_and_zipcode(user_query)

        logger.info(f"Extracted data: {extracted_data}")

        service_categories = extracted_data.get('service_categories', [])
        detected_zipcode = extracted_data.get('zipcode')

        # Use provided zipcode if available, otherwise use detected zipcode
        actual_zipcode = zipcode if zipcode else detected_zipcode

        logger.info(f"Actual Zipcode: {actual_zipcode}")

        # Ensure zipcode is in the correct format for DynamoDB queries
        if actual_zipcode and actual_zipcode.isdigit():
            logger.info(f"Using numeric zipcode: {actual_zipcode}")
        else:
            logger.info(f"Zipcode format may not be numeric: {actual_zipcode}")

        # Query DynamoDB for matching services
        services = bedrockAgent.query_dynamodb_for_services(service_categories, actual_zipcode)
        logger.info(f"Found {len(services)} matching services in DynamoDB")

        # Log a sample service for debugging
        if services and len(services) > 0:
            logger.info(f"Service sample (first item): {json.dumps(services[0], cls=DecimalEncoder)}")

        # If services are found in DynamoDB, format and return them
        if services and len(services) > 0:
            logger.info("Returning results from DynamoDB")
            response_data = bedrockAgent.format_response(services, service_categories, actual_zipcode, user_id)

            # Update user query history
            update_user_query_history(
                user_id=user_id,
                user_query=user_query,
                original_query=original_query,
                response_data=response_data,
                zipcode=actual_zipcode,
                language=language
            )

            # Translate response if needed
            if language != 'english':
                target_lang = get_language_code(language)
                logger.info(f"Translating response to {language} ({target_lang})")
                response_data = translate_response_data(response_data, target_lang)

            # Send formatted response through WebSocket
            send_to_connection(connection_id, domain_name, stage, {
                'user_id': user_id,
                'zipcode': actual_zipcode,
                'language': language,
                'response_data': response_data
            })

            return {'statusCode': 200, 'body': 'Query processed successfully'}
        else:
            # No services found in DynamoDB, call Perplexity Lambda as fallback
            logger.info("No services found in DynamoDB, calling Perplexity Lambda")
            perplexity_response = call_perplexity_lambda(user_query, user_id, actual_zipcode, language)

            # Send Perplexity response through WebSocket
            send_to_connection(connection_id, domain_name, stage, perplexity_response)

            return {'statusCode': 200, 'body': 'Query processed successfully with Perplexity fallback'}

    except Exception as e:
        logger.error(f"Error processing WebSocket query: {str(e)}")
        logger.error(traceback.format_exc())

        error_message = 'Error processing query'
        # Translate error message if needed
        if 'language' in locals() and language != 'english':
            target_lang = get_language_code(language)
            error_message = translate_text(error_message, "en", target_lang)

        send_to_connection(connection_id, domain_name, stage, {
            'error': error_message,
            'message': str(e)
        })

        return {'statusCode': 500, 'body': 'Error processing query'}

def send_to_connection(connection_id, domain_name, stage, data):
    """
    Send a message to a WebSocket connection

    Args:
        connection_id (str): The connection ID
        domain_name (str): API Gateway domain name
        stage (str): API Gateway stage
        data (dict): Data to send
    """
    global api_gateway_management_client

    # Convert any Decimal values before serialization
    data = convert_decimal(data)

    # Initialize the client if needed
    if not api_gateway_management_client:
        endpoint_url = f"https://{domain_name}/{stage}"
        api_gateway_management_client = boto3.client(
            'apigatewaymanagementapi',
            endpoint_url=endpoint_url
        )

    # Send the message
    try:
        # Use DecimalEncoder for JSON serialization
        api_gateway_management_client.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(data, cls=DecimalEncoder).encode('utf-8')
        )
        logger.info(f"Message sent to connection {connection_id}")
    except Exception as e:
        # Connection might be stale
        if hasattr(e, 'response') and e.response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 410:
            logger.warning(f"Connection {connection_id} is gone")
        else:
            logger.error(f"Error sending message to connection {connection_id}: {str(e)}")
            raise e

def handle_rest_event(event, context):
    """
    Handle REST API events (original functionality)
    """
    try:
        # Parse input from API Gateway
        if event.get('body') and isinstance(event['body'], str):
            # Input from API Gateway
            body = json.loads(event['body'])
        else:
            # Direct Lambda invocation (for AWS Lambda console testing)
            body = event

        # Extract parameters
        user_id = body.get('user_id')
        user_query = body.get('user_query', '')
        original_query = user_query  # Save original query before any translation
        zipcode = body.get('zipcode')
        language = body.get('language', 'english').lower()  # Default to English

        logger.info(f"REST API query - User ID: {user_id}, Query: {user_query}, Language: {language}, zipcode: {zipcode}")

        # Validate input
        if not user_id:
            error_message = 'Missing required parameter: user_id'
            if language != 'english':
                target_lang = get_language_code(language)
                error_message = translate_text(error_message, "en", target_lang)

            return format_response(400, {
                'error': error_message,
                'language': language
            })

        if not user_query:
            error_message = "I didn't receive a question. Please provide a query about services you're looking for."
            # Translate error message if needed
            if language != 'english':
                target_lang = get_language_code(language)
                error_message = translate_text(error_message, "en", target_lang)

            return format_response(400, {
                'user_id': user_id,
                'zipcode': zipcode,
                'language': language,
                'message': error_message
            })

        # Use bedrockAgent functions to get DynamoDB results
        extracted_data = bedrockAgent.extract_categories_and_zipcode(user_query)

        logger.info(f"REST API query - Extracted data: {extracted_data}")

        service_categories = extracted_data.get('service_categories', [])
        detected_zipcode = extracted_data.get('zipcode')

        # Use provided zipcode if available, otherwise use detected zipcode
        actual_zipcode = zipcode if zipcode else detected_zipcode

        logger.info(f"Actual Zipcode is: {actual_zipcode}")

        # Ensure zipcode is in the correct format for DynamoDB queries
        if actual_zipcode and actual_zipcode.isdigit():
            logger.info(f"Using numeric zipcode: {actual_zipcode}")
        else:
            logger.info(f"Zipcode format may not be numeric: {actual_zipcode}")

        # Query DynamoDB for matching services
        services = bedrockAgent.query_dynamodb_for_services(service_categories, actual_zipcode)
        logger.info(f"Found {len(services)} matching services in DynamoDB")

        # Log a sample service for debugging
        if services and len(services) > 0:
            logger.info(f"Service sample (first item): {json.dumps(services[0], cls=DecimalEncoder)}")

        # If services are found in DynamoDB, format and return them
        if services and len(services) > 0:
            logger.info("Returning results from DynamoDB")
            response_data = bedrockAgent.format_response(services, service_categories, actual_zipcode, user_id)

            # Update user query history
            update_user_query_history(
                user_id=user_id,
                user_query=user_query,
                original_query=original_query,
                response_data=response_data,
                zipcode=actual_zipcode,
                language=language
            )

            # Translate response if needed
            if language != 'english':
                target_lang = get_language_code(language)
                logger.info(f"Translating response to {language} ({target_lang})")
                response_data = translate_response_data(response_data, target_lang)

            return format_response(200, {
                'user_id': user_id,
                'zipcode': actual_zipcode,
                'language': language,
                'response_data': response_data
            })
        else:
            # No services found in DynamoDB, call Perplexity Lambda as fallback
            logger.info("No services found in DynamoDB, calling Perplexity Lambda")
            return call_perplexity_lambda(user_query, user_id, actual_zipcode, language)

    except Exception as e:
        logger.error(f"Error in handle_rest_event: {str(e)}")
        logger.error(traceback.format_exc())

        error_message = "I encountered an error while processing your request. Please try again or rephrase your question."
        language = body.get('language', 'english').lower() if isinstance(body, dict) else 'english'

        # Translate error message if needed
        if language != 'english':
            target_lang = get_language_code(language)
            error_message = translate_text(error_message, "en", target_lang)

        error_response = {
            'user_id': body.get('user_id', 'unknown') if isinstance(body, dict) else 'unknown',
            'zipcode': body.get('zipcode') if isinstance(body, dict) else None,
            'language': language,
            'message': error_message,
            'error': str(e)
        }

        return format_response(500, error_response)

def format_response(status_code, body):
    """
    Format the response for API Gateway

    Args:
        status_code (int): HTTP status code
        body (dict): Response body

    Returns:
        dict: Formatted response for API Gateway
    """
    # Convert any Decimal values in the body to int or float
    body = convert_decimal(body)

    # API Gateway expects a specific format
    if isinstance(body, dict):
        try:
            # Try to serialize to catch any issues
            json_string = json.dumps(body, cls=DecimalEncoder)

            return {
                'statusCode': status_code,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json_string
            }
        except Exception as e:
            logger.error(f"Error serializing response body: {str(e)}")
            # Create a safe response
            safe_body = {
                'error': 'Error formatting response',
                'message': str(e)
            }
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(safe_body)
            }
    else:
        # For non-dict bodies (strings, etc.)
        return {
            'statusCode': status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': str(body)
            }, cls=DecimalEncoder)
        }