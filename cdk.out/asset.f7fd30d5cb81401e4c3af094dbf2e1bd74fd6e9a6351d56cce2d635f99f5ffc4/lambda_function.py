import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import os

# Initialize the DynamoDB client
dynamodb_client = boto3.client('dynamodb')
# Initialize AWS Translate client
translate_client = boto3.client('translate')
ENV = os.environ.get('ENVIRONMENT', 'dev')
USER_DATA_TABLE = f'user_data-{ENV}'

def get_cors_headers():
    """
    Return standard CORS headers for all responses
    """
    return {
        'Access-Control-Allow-Origin': '*',  # In production, specify your domain
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token, X-Amz-User-Agent',
        'Access-Control-Expose-Headers': 'Access-Control-Allow-Origin',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Max-Age': '3600'
    }

def create_response(status_code, body, additional_headers=None):
    """
    Create a standardized response with CORS headers

    Args:
        status_code: HTTP status code
        body: Response body (dict or string)
        additional_headers: Additional headers to include

    Returns:
        Formatted response with CORS headers
    """
    headers = get_cors_headers()

    if additional_headers:
        headers.update(additional_headers)

    # Ensure body is a string
    if isinstance(body, dict):
        body = json.dumps(body)

    return {
        'statusCode': status_code,
        'headers': headers,
        'body': body
    }

def validate_language(language):
    """
    Validate and normalize language input

    Args:
        language: The language string to validate

    Returns:
        Validated language string (english, spanish, polish) or 'english' as default
    """
    if not language:
        return 'english'

    language = language.lower().strip()
    valid_languages = ['english', 'spanish', 'polish']

    return language if language in valid_languages else 'english'

def lambda_handler(event, context):
    """
    Lambda handler to process both WebSocket and REST API events
    """
    try:
        # Handle OPTIONS preflight requests for CORS
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {'message': 'CORS preflight'})

        # Determine if this is a WebSocket or REST API event
        if 'requestContext' in event and 'connectionId' in event.get('requestContext', {}):
            # WebSocket event
            return handle_websocket_event(event, context)
        else:
            # REST API event (keep your original functionality)
            return handle_rest_event(event, context)
    except Exception as e:
        print(f"Unhandled error in lambda_handler: {str(e)}")
        return create_response(500, {
            'error': 'Internal server error',
            'details': str(e)
        })

def handle_websocket_event(event, context):
    """
    Handle WebSocket API events
    """
    connection_id = event['requestContext']['connectionId']
    domain_name = event['requestContext']['domainName']
    stage = event['requestContext']['stage']
    route_key = event['requestContext']['routeKey']

    print(f"WebSocket event: {route_key}, Connection ID: {connection_id}")

    try:
        # Handle WebSocket routes
        if route_key == '$connect':
            return {'statusCode': 200, 'body': 'Connected'}

        elif route_key == '$disconnect':
            return {'statusCode': 200, 'body': 'Disconnected'}

        # Parse the request body for action routes
        if event.get('body'):
            body = json.loads(event.get('body', '{}'))

            # Extract common parameters
            user_id = body.get('user_id')
            language = validate_language(body.get('language', 'english'))

            if not user_id:
                send_websocket_response(connection_id, domain_name, stage, {
                    'error': 'user_id is required'
                })
                return {'statusCode': 400, 'body': 'user_id is required'}

            # Handle different operations
            if route_key == 'getUser':
                # Get user with feedback questions
                result = get_user_with_feedback_questions(user_id, language)
                status_code = result.get('statusCode', 500)
                response_body = json.loads(result.get('body', '{}'))

                # Send the result to the client
                send_websocket_response(connection_id, domain_name, stage, response_body)
                return {'statusCode': status_code, 'body': 'User data sent'}

            elif route_key == 'updateUser':
                # Update user information
                zipcode = body.get('Zipcode')
                phone = body.get('Phone')
                email = body.get('Email')

                result = create_or_update_user(user_id, zipcode, phone, email, language)
                status_code = result.get('statusCode', 500)
                response_body = json.loads(result.get('body', '{}'))

                # Send the result to the client
                send_websocket_response(connection_id, domain_name, stage, response_body)
                return {'statusCode': status_code, 'body': 'User update processed'}

            elif route_key == 'sendFeedback':
                # Extract optional user profile data
                zipcode = body.get('Zipcode')
                phone = body.get('Phone')
                email = body.get('Email')

                # Check for multiple feedback format
                if 'feedback_list' in body and isinstance(body['feedback_list'], list):
                    result = store_multiple_feedbacks(user_id, body['feedback_list'], zipcode, phone, email, language)
                else:
                    # Legacy single feedback
                    referral_id = body.get('referral_id')
                    feedback = body.get('feedback')

                    # First update user info if provided
                    if zipcode or phone or email:
                        create_or_update_user(user_id, zipcode, phone, email, language)

                    result = store_referral_feedback(user_id, referral_id, feedback)

                status_code = result.get('statusCode', 500)
                response_body = json.loads(result.get('body', '{}'))

                # Send the result to the client
                send_websocket_response(connection_id, domain_name, stage, response_body)
                return {'statusCode': status_code, 'body': 'Feedback processed'}

            # Unknown route key
            send_websocket_response(connection_id, domain_name, stage, {
                'error': f'Unknown route: {route_key}'
            })
            return {'statusCode': 400, 'body': f'Unknown route: {route_key}'}

    except Exception as e:
        print(f"Error handling WebSocket event: {str(e)}")

        # Send error response to client
        send_websocket_response(connection_id, domain_name, stage, {
            'error': 'Error processing request',
            'details': str(e)
        })

        return {'statusCode': 500, 'body': f'Error: {str(e)}'}

def send_websocket_response(connection_id, domain_name, stage, data):
    """
    Send a response back through the WebSocket connection

    Args:
        connection_id: The WebSocket connection ID
        domain_name: The API Gateway domain name
        stage: The API Gateway stage
        data: The data to send (will be converted to JSON)
    """
    api_gateway_management = boto3.client(
        'apigatewaymanagementapi',
        endpoint_url=f'https://{domain_name}/{stage}'
    )

    try:
        api_gateway_management.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(data).encode('utf-8')
        )
        print(f"Response sent to connection {connection_id}")
    except ClientError as e:
        # The connection might be stale or closed
        if e.response.get('Error', {}).get('Code') == 'GoneException':
            print(f"Connection {connection_id} is gone")
        else:
            print(f"Error sending response: {str(e)}")
            raise e

def handle_rest_event(event, context):
    """
    Handle REST API events with proper CORS headers
    """
    try:
        # Handle different HTTP methods
        http_method = event.get('httpMethod', '').upper()

        # Parse the incoming JSON payload
        body = {}
        if event.get('body'):
            try:
                body = json.loads(event['body'])
            except json.JSONDecodeError:
                return create_response(400, {'error': 'Invalid JSON format'})

        # Extract user_id (required for most operations)
        user_id = body.get('user_id')

        # Handle different HTTP methods
        if http_method == 'GET':
            # For GET requests, user_id might be in query parameters
            if not user_id:
                query_params = event.get('queryStringParameters') or {}
                user_id = query_params.get('user_id')

            if not user_id:
                return create_response(400, {'error': 'user_id is required'})

            language = validate_language(body.get('language', 'english'))
            result = get_user_with_feedback_questions(user_id, language)
            return create_response(result['statusCode'], result['body'])

        elif http_method == 'POST':
            # Handle POST requests (create user or operations)
            if not user_id:
                return create_response(400, {'error': 'user_id is required'})

            # Extract common profile fields
            zipcode = body.get('Zipcode')
            phone = body.get('Phone')
            email = body.get('Email')
            language = validate_language(body.get('language', 'english'))

            # Determine which operation to perform based on body content
            if 'operation' in body:
                operation = body.get('operation', '').upper()

                if operation == 'GET':
                    result = get_user_with_feedback_questions(user_id, language)
                elif operation == 'PUT':
                    result = create_or_update_user(user_id, zipcode, phone, email, language)
                elif operation == 'FEEDBACK':
                    # Check for multiple feedback format
                    if 'feedback_list' in body and isinstance(body['feedback_list'], list):
                        result = store_multiple_feedbacks(user_id, body['feedback_list'], zipcode, phone, email, language)
                    else:
                        # Legacy single feedback
                        referral_id = body.get('referral_id')
                        feedback = body.get('feedback')

                        # First update user info if provided
                        if zipcode or phone or email:
                            create_or_update_user(user_id, zipcode, phone, email, language)

                        result = store_referral_feedback(user_id, referral_id, feedback)
                else:
                    return create_response(400, {'error': f'Unsupported operation: {operation}'})
            else:
                # Default POST behavior - create/update user
                result = create_or_update_user(user_id, zipcode, phone, email, language)

            return create_response(result['statusCode'], result['body'])

        elif http_method == 'PUT':
            # Handle PUT requests (update user)
            if not user_id:
                return create_response(400, {'error': 'user_id is required'})

            zipcode = body.get('Zipcode')
            phone = body.get('Phone')
            email = body.get('Email')
            language = validate_language(body.get('language', 'english'))

            result = create_or_update_user(user_id, zipcode, phone, email, language)
            return create_response(result['statusCode'], result['body'])

        else:
            return create_response(405, {'error': f'Method {http_method} not allowed'})

    except KeyError as e:
        return create_response(400, {'error': f'Missing required field: {str(e)}'})
    except ClientError as e:
        return create_response(500, {'error': 'Database error', 'details': str(e)})
    except Exception as e:
        return create_response(500, {'error': 'Internal server error', 'details': str(e)})

def translate_text(text, target_language):
    """
    Translate text using AWS Translate

    Args:
        text: Text to translate
        target_language: Target language code ('es' for Spanish, 'pl' for Polish)

    Returns:
        Translated text or original text if translation fails
    """
    try:
        if not text or target_language == 'en':
            return text

        response = translate_client.translate_text(
            Text=text,
            SourceLanguageCode='en',  # Source is English
            TargetLanguageCode=target_language
        )
        return response['TranslatedText']
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text  # Return original text if translation fails

def get_language_code(language):
    """
    Get language code for AWS Translate

    Args:
        language: Language name (english, spanish, polish)

    Returns:
        Language code ('en', 'es', 'pl')
    """
    language_map = {
        'english': 'en',
        'spanish': 'es',
        'polish': 'pl'
    }
    return language_map.get(language.lower(), 'en')

def store_multiple_feedbacks(user_id, feedback_list, zipcode=None, phone=None, email=None, language='english'):
    """
    Stores feedback for multiple referrals/services at once (up to 5) and updates user info if provided.

    Args:
        user_id: The ID of the user
        feedback_list: List of objects containing referral_id and feedback values
        zipcode: User's zipcode (optional)
        phone: User's phone number (optional)
        email: User's email (optional)
        language: User's preferred language (english, spanish, polish)

    Returns:
        Response indicating success or failure
    """
    # Validate and normalize language
    language = validate_language(language)

    # Limit to max 5 feedback entries
    feedback_list = feedback_list[:5]

    if not feedback_list:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'No feedback data provided'})
        }

    results = []
    success_count = 0

    try:
        # First update the user profile if any info is provided
        if zipcode or phone or email:
            update_result = create_or_update_user(user_id, zipcode, phone, email, language)
            if update_result.get('statusCode') not in [200, 201]:
                # If user update/creation failed, return the error
                return update_result

        # Get the user to verify existence
        response = dynamodb_client.get_item(
            TableName=USER_DATA_TABLE,
            Key={
                'user_id': {'S': user_id}
            }
        )

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'User not found'})
            }

        user_data = response['Item']
        current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        # Process each feedback entry
        for feedback_entry in feedback_list:
            referral_id = feedback_entry.get('referral_id')
            feedback = feedback_entry.get('feedback')

            # Validate feedback data
            if not referral_id:
                results.append({
                    'status': 'error',
                    'message': 'referral_id is required',
                    'referral_id': referral_id
                })
                continue

            if not feedback or feedback.lower() not in ['yes', 'no']:
                results.append({
                    'status': 'error',
                    'message': "feedback must be 'yes' or 'no'",
                    'referral_id': referral_id
                })
                continue

            # Check if referral exists in referrals OR if it's a service from queries
            feedback_stored = False

            # First, check in traditional referrals
            if 'referrals' in user_data and referral_id in user_data['referrals']['M']:
                dynamodb_client.update_item(
                    TableName=USER_DATA_TABLE,
                    Key={
                        'user_id': {'S': user_id}
                    },
                    UpdateExpression="SET referrals.#referral_id.feedback = :feedback, referrals.#referral_id.feedback_timestamp = :timestamp",
                    ExpressionAttributeNames={
                        '#referral_id': referral_id
                    },
                    ExpressionAttributeValues={
                        ':feedback': {'S': feedback.lower()},
                        ':timestamp': {'S': current_time}
                    }
                )
                feedback_stored = True

            # If not found in referrals, check in query services
            if not feedback_stored and 'queries' in user_data:
                service_found = False
                # Look through all queries to find the service
                for query_id, query_data in user_data['queries']['M'].items():
                    if 'response' in query_data['M']:
                        try:
                            response_json = json.loads(query_data['M']['response']['S'])
                            if 'services' in response_json:
                                for service in response_json['services']:
                                    service_id = service.get('details', {}).get('id') or service.get('id')
                                    if service_id == referral_id:
                                        # Store feedback in a special feedback structure for query services
                                        dynamodb_client.update_item(
                                            TableName=USER_DATA_TABLE,
                                            Key={
                                                'user_id': {'S': user_id}
                                            },
                                            UpdateExpression="SET service_feedback.#service_id = :feedback_data",
                                            ExpressionAttributeNames={
                                                '#service_id': referral_id
                                            },
                                            ExpressionAttributeValues={
                                                ':feedback_data': {
                                                    'M': {
                                                        'feedback': {'S': feedback.lower()},
                                                        'feedback_timestamp': {'S': current_time},
                                                        'query_id': {'S': query_id},
                                                        'agency': {'S': service.get('agency', '')},
                                                        'service_category': {'S': service.get('details', {}).get('service_category', '')}
                                                    }
                                                }
                                            }
                                        )
                                        feedback_stored = True
                                        service_found = True
                                        break
                                if service_found:
                                    break
                        except (json.JSONDecodeError, KeyError):
                            continue

            if feedback_stored:
                results.append({
                    'status': 'success',
                    'message': 'Feedback recorded successfully',
                    'referral_id': referral_id,
                    'feedback': feedback.lower()
                })
                success_count += 1
            else:
                results.append({
                    'status': 'error',
                    'message': 'Referral/Service not found for this user',
                    'referral_id': referral_id
                })

        # Get updated user data with feedback questions
        if success_count > 0:
            user_result = get_user_with_feedback_questions(user_id, language)
            updated_data = json.loads(user_result.get('body', '{}'))

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': f'Successfully recorded {success_count} feedback entries',
                    'results': results,
                    'user': updated_data.get('user', {}),
                    'feedback_questions': updated_data.get('feedback_questions', [])
                })
            }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'No feedback entries were successfully processed',
                    'results': results
                })
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error processing feedback: {str(e)}'})
        }

def store_referral_feedback(user_id, referral_id, feedback):
    """
    Stores user feedback for a specific referral or service.

    Args:
        user_id: The ID of the user
        referral_id: The ID of the referral or service
        feedback: The feedback value ('yes' or 'no')

    Returns:
        Response indicating success or failure
    """
    # Validation
    if not referral_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'referral_id is required'})
        }

    if not feedback or feedback.lower() not in ['yes', 'no']:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': "feedback must be 'yes' or 'no'"})
        }

    try:
        # Check if user exists
        response = dynamodb_client.get_item(
            TableName=USER_DATA_TABLE,
            Key={
                'user_id': {'S': user_id}
            }
        )

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'User not found'})
            }

        user_data = response['Item']
        current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        feedback_stored = False

        # First, check in traditional referrals
        if 'referrals' in user_data and referral_id in user_data['referrals']['M']:
            dynamodb_client.update_item(
                TableName=USER_DATA_TABLE,
                Key={
                    'user_id': {'S': user_id}
                },
                UpdateExpression="SET referrals.#referral_id.feedback = :feedback, referrals.#referral_id.feedback_timestamp = :timestamp",
                ExpressionAttributeNames={
                    '#referral_id': referral_id
                },
                ExpressionAttributeValues={
                    ':feedback': {'S': feedback.lower()},
                    ':timestamp': {'S': current_time}
                }
            )
            feedback_stored = True

        # If not found in referrals, check in query services
        if not feedback_stored and 'queries' in user_data:
            service_found = False
            # Look through all queries to find the service
            for query_id, query_data in user_data['queries']['M'].items():
                if 'response' in query_data['M']:
                    try:
                        response_json = json.loads(query_data['M']['response']['S'])
                        if 'services' in response_json:
                            for service in response_json['services']:
                                service_id = service.get('details', {}).get('id') or service.get('id')
                                if service_id == referral_id:
                                    # Store feedback in a special feedback structure for query services
                                    dynamodb_client.update_item(
                                        TableName=USER_DATA_TABLE,
                                        Key={
                                            'user_id': {'S': user_id}
                                        },
                                        UpdateExpression="SET service_feedback.#service_id = :feedback_data",
                                        ExpressionAttributeNames={
                                            '#service_id': referral_id
                                        },
                                        ExpressionAttributeValues={
                                            ':feedback_data': {
                                                'M': {
                                                    'feedback': {'S': feedback.lower()},
                                                    'feedback_timestamp': {'S': current_time},
                                                    'query_id': {'S': query_id},
                                                    'agency': {'S': service.get('agency', '')},
                                                    'service_category': {'S': service.get('details', {}).get('service_category', '')}
                                                }
                                            }
                                        }
                                    )
                                    feedback_stored = True
                                    service_found = True
                                    break
                        if service_found:
                            break
                    except (json.JSONDecodeError, KeyError):
                        continue

        if not feedback_stored:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Referral/Service not found for this user'})
            }

        # Get the language from the response item if it exists
        language = 'english'
        if 'language' in user_data:
            language = user_data['language']['S']

        # After storing feedback, get a new set of feedback questions
        result = get_user_with_feedback_questions(user_id, language)
        response_body = json.loads(result.get('body', '{}'))

        # Add the success message
        response_body['feedback_stored'] = {
            'message': 'Feedback recorded successfully.',
            'user_id': user_id,
            'referral_id': referral_id,
            'feedback': feedback.lower(),
            'timestamp': current_time
        }

        return {
            'statusCode': 200,
            'body': json.dumps(response_body)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error storing feedback: {str(e)}'})
        }

def get_user_with_feedback_questions(user_id, language='english'):
    """
    ✅ SIMPLIFIED: Fetches user details and only returns referrals that need feedback.
    Also generates top 5 feedback questions for referrals without feedback.
    NOTE: Only processes referrals, skips queries entirely.

    Args:
        user_id: The ID of the user to fetch
        language: The language for translation (english, spanish, polish)

    Returns:
        Response with user details, only referrals needing feedback, and top 5 feedback questions
    """
    try:
        # Get the user from DynamoDB with native format
        response = dynamodb_client.get_item(
            TableName=USER_DATA_TABLE,
            Key={
                'user_id': {'S': user_id}
            }
        )

        # Check if user exists
        if 'Item' not in response:
            # Validate and normalize language for error message
            language = validate_language(language)
            lang_code = get_language_code(language)
            needs_translation = language.lower() in ['spanish', 'polish']

            message = 'User not found'
            if needs_translation:
                message = translate_text(message, lang_code)

            return {
                'statusCode': 404,
                'body': json.dumps({'message': message})
            }

        # Extract user data
        user_data = response['Item']

        # ✅ FIX: Check user's stored language preference if language wasn't explicitly provided
        # or if default 'english' was passed
        stored_language = 'english'
        if 'language' in user_data:
            stored_language = user_data['language']['S']

        # Use stored language if the provided language is the default
        if language == 'english' and stored_language != 'english':
            language = stored_language
            print(f"Using stored language preference: {language}")

        # Validate and normalize the final language choice
        language = validate_language(language)

        # Get the language code for translations
        lang_code = get_language_code(language)
        needs_translation = language.lower() in ['spanish', 'polish']

        # Extract and format user data
        formatted_user = {
            'user_id': user_id,
            'language': language  # Store the language preference
        }

        # Add basic user info if available
        if 'Zipcode' in user_data:
            formatted_user['Zipcode'] = user_data['Zipcode']['S']
        if 'Phone' in user_data:
            formatted_user['Phone'] = user_data['Phone']['S']
        if 'Email' in user_data:
            formatted_user['Email'] = user_data['Email']['S']

        # ✅ SIMPLIFIED: Only collect referrals that need feedback
        referrals_needing_feedback = []
        items_with_feedback = []  # For reference/history

        # ✅ Process traditional referrals only
        if 'referrals' in user_data and 'M' in user_data['referrals']:
            referrals_map = user_data['referrals']['M']

            for referral_id, referral_data in referrals_map.items():
                referral_content = referral_data['M']

                # Extract referral details
                agency = referral_content.get('organization', {}).get('S', '') or referral_content.get('agency', {}).get('S', '')
                address = referral_content.get('address', {}).get('S', '')
                zipcode = referral_content.get('zipcode', {}).get('S', '')
                service_category = referral_content.get('serviceCategory', {}).get('S', '')
                state = referral_content.get('state', {}).get('S', '')
                timestamp = referral_content.get('timestamp', {}).get('S', '')

                # Translate agency and service_category if needed
                if needs_translation:
                    agency = translate_text(agency, lang_code)
                    service_category = translate_text(service_category, lang_code)

                # Check if feedback exists
                has_feedback = 'feedback' in referral_content
                feedback_value = referral_content.get('feedback', {}).get('S', '') if has_feedback else None

                formatted_referral = {
                    'referral_id': referral_id,
                    'agency': agency,
                    'address': address,
                    'zipcode': zipcode,
                    'serviceCategory': service_category,
                    'state': state,
                    'timestamp': timestamp,
                    'source': 'referral'
                }

                # ✅ Only add to appropriate list based on feedback status
                if has_feedback:
                    formatted_referral['feedback'] = feedback_value
                    items_with_feedback.append(formatted_referral)
                else:
                    # Add to list of referrals needing feedback
                    try:
                        ts = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f').timestamp() if timestamp else 0
                    except ValueError:
                        try:
                            ts = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() if timestamp else 0
                        except ValueError:
                            ts = 0

                    formatted_referral['ts'] = ts
                    referrals_needing_feedback.append(formatted_referral)

        # ✅ Sort referrals needing feedback by timestamp (newest first) and generate questions
        referrals_needing_feedback.sort(key=lambda x: x['ts'], reverse=True)

        feedback_questions = []
        # Generate feedback questions for the top 5 referrals/services
        for item in referrals_needing_feedback[:5]:
            # Create the base question in English
            english_question = f"Hi {user_id}, Did the referral {item['agency']}, {item['address']}, {item['zipcode']} help you in {item['serviceCategory']}? Please reply with yes or no."

            # Translate the question if needed
            question = english_question
            if needs_translation:
                question = translate_text(english_question, lang_code)

            feedback_questions.append({
                'referral_id': item['referral_id'],
                'question': question,
                'agency': item['agency'],
                'service_category': item['serviceCategory'],
                'source': item['source']
            })

        # ✅ Only return referrals that need feedback (remove 'ts' field for clean response)
        referrals_needing_feedback_clean = []
        for item in referrals_needing_feedback:
            clean_item = {k: v for k, v in item.items() if k != 'ts'}
            referrals_needing_feedback_clean.append(clean_item)

        # Add only referrals needing feedback to user data
        formatted_user['referrals'] = referrals_needing_feedback_clean  # ✅ Only referrals needing feedback
        formatted_user['items_with_feedback_count'] = len(items_with_feedback)  # ✅ Count for reference

        # Prepare the success message
        success_message = 'User data retrieved successfully.'
        if needs_translation:
            success_message = translate_text(success_message, lang_code)

        print(f"✅ Found {len(referrals_needing_feedback_clean)} referrals needing feedback")
        print(f"✅ Found {len(items_with_feedback)} referrals with existing feedback")
        print(f"✅ Generated {len(feedback_questions)} feedback questions")
        print(f"✅ Using language: {language}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'user': formatted_user,
                'feedback_questions': feedback_questions,
                'message': success_message,
                'language': language,
                'summary': {
                    'referrals_needing_feedback': len(referrals_needing_feedback_clean),
                    'referrals_with_feedback': len(items_with_feedback),
                    'feedback_questions_generated': len(feedback_questions)
                }
            })
        }

    except Exception as e:
        error_message = f'Error retrieving user data: {str(e)}'
        if language.lower() in ['spanish', 'polish']:
            error_message = translate_text(f'Error retrieving user data', get_language_code(language))

        return {
            'statusCode': 500,
            'body': json.dumps({'error': error_message})
        }

def create_or_update_user(user_id, zipcode, phone=None, email=None, language='english'):
    """
    Creates or updates a user in DynamoDB with language support.

    Args:
        user_id: The ID of the user
        zipcode: User's zipcode
        phone: User's phone number (optional)
        email: User's email (optional)
        language: User's preferred language (english, spanish, polish) - defaults to english

    Returns:
        Response indicating success or failure
    """
    # Validation
    if not zipcode:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Zipcode is required for creating/updating a user'})
        }

    # Validate and normalize language
    language = validate_language(language)

    try:
        # Check if user exists
        response = dynamodb_client.get_item(
            TableName=USER_DATA_TABLE,
            Key={
                'user_id': {'S': user_id}
            }
        )

        user_exists = 'Item' in response

        if user_exists:
            # Update existing user without overwriting referrals
            update_expressions = []
            expression_attribute_values = {}

            if zipcode:
                update_expressions.append("Zipcode = :zipcode")
                expression_attribute_values[':zipcode'] = {'S': zipcode}

            if phone:
                update_expressions.append("Phone = :phone")
                expression_attribute_values[':phone'] = {'S': phone}

            if email:
                update_expressions.append("Email = :email")
                expression_attribute_values[':email'] = {'S': email}

            # Always update language preference
            update_expressions.append("#lang = :language")
            expression_attribute_values[':language'] = {'S': language}

            if update_expressions:
                update_expression = "SET " + ", ".join(update_expressions)

                # Handle language as a reserved keyword
                expression_attribute_names = {'#lang': 'language'}

                dynamodb_client.update_item(
                    TableName=USER_DATA_TABLE,
                    Key={
                        'user_id': {'S': user_id}
                    },
                    UpdateExpression=update_expression,
                    ExpressionAttributeNames=expression_attribute_names,
                    ExpressionAttributeValues=expression_attribute_values
                )

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'User data updated successfully.',
                    'user_id': user_id,
                    'language': language
                })
            }
        else:
            # Create new user
            item = {
                'user_id': {'S': user_id},
                'Zipcode': {'S': zipcode},
                'language': {'S': language}  # Always include language for new users
            }

            if phone:
                item['Phone'] = {'S': phone}
            if email:
                item['Email'] = {'S': email}

            dynamodb_client.put_item(
                TableName=USER_DATA_TABLE,
                Item=item
            )

            return {
                'statusCode': 201,
                'body': json.dumps({
                    'message': 'User data created successfully.',
                    'user_id': user_id,
                    'language': language
                })
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error storing user data: {str(e)}'})
        }