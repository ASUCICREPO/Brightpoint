import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

# Initialize the DynamoDB client
dynamodb_client = boto3.client('dynamodb')
# Initialize AWS Translate client
translate_client = boto3.client('translate')

def lambda_handler(event, context):
    """
    Lambda handler to process both WebSocket and REST API events
    """
    try:
        # Determine if this is a WebSocket or REST API event
        if 'requestContext' in event and 'connectionId' in event.get('requestContext', {}):
            # WebSocket event
            return handle_websocket_event(event, context)
        else:
            # REST API event (keep your original functionality)
            return handle_rest_event(event, context)
    except Exception as e:
        print(f"Unhandled error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }

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
            language = body.get('language', 'english').lower()  # Default to English

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

                result = create_or_update_user(user_id, zipcode, phone, email)
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
                    result = store_multiple_feedbacks(user_id, body['feedback_list'], zipcode, phone, email)
                else:
                    # Legacy single feedback
                    referral_id = body.get('referral_id')
                    feedback = body.get('feedback')

                    # First update user info if provided
                    if zipcode or phone or email:
                        create_or_update_user(user_id, zipcode, phone, email)

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
    Handle REST API events
    """
    try:
        # Parse the incoming JSON payload
        body = json.loads(event['body'])

        # Extract user_id (required for all operations)
        user_id = body.get('user_id')
        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'user_id is required'})
            }

        # Extract common profile fields
        zipcode = body.get('Zipcode')
        phone = body.get('Phone')
        email = body.get('Email')
        language = body.get('language', 'english').lower()  # Default to English

        # Determine which operation to perform
        operation = body.get('operation', 'GET').upper()

        # Route to appropriate handler based on operation
        if operation == 'GET':
            return get_user_with_feedback_questions(user_id, language)
        elif operation == 'PUT':
            return create_or_update_user(user_id, zipcode, phone, email)
        elif operation == 'FEEDBACK':
            # Check for multiple feedback format
            if 'feedback_list' in body and isinstance(body['feedback_list'], list):
                return store_multiple_feedbacks(user_id, body['feedback_list'], zipcode, phone, email)
            else:
                # Legacy single feedback
                referral_id = body.get('referral_id')
                feedback = body.get('feedback')

                # First update user info if provided
                if zipcode or phone or email:
                    create_or_update_user(user_id, zipcode, phone, email)

                return store_referral_feedback(user_id, referral_id, feedback)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Unsupported operation: {operation}'})
            }

    except KeyError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Missing required field: {str(e)}'})
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error', 'details': str(e)})
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON format'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }

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

def store_multiple_feedbacks(user_id, feedback_list, zipcode=None, phone=None, email=None):
    """
    Stores feedback for multiple referrals at once (up to 5) and updates user info if provided.

    Args:
        user_id: The ID of the user
        feedback_list: List of objects containing referral_id and feedback values
        zipcode: User's zipcode (optional)
        phone: User's phone number (optional)
        email: User's email (optional)

    Returns:
        Response indicating success or failure
    """
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
            update_result = create_or_update_user(user_id, zipcode, phone, email)
            if update_result.get('statusCode') not in [200, 201]:
                # If user update/creation failed, return the error
                return update_result

        # Get the user to verify existence
        response = dynamodb_client.get_item(
            TableName='user_data',
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

            # Check if referral exists
            if 'referrals' not in user_data or referral_id not in user_data['referrals']['M']:
                results.append({
                    'status': 'error',
                    'message': 'Referral not found for this user',
                    'referral_id': referral_id
                })
                continue

            # Store feedback
            dynamodb_client.update_item(
                TableName='user_data',
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

            results.append({
                'status': 'success',
                'message': 'Feedback recorded successfully',
                'referral_id': referral_id,
                'feedback': feedback.lower()
            })
            success_count += 1

        # Get updated user data with feedback questions
        if success_count > 0:
            # Get the language from the response item if it exists
            language = 'english'
            if 'language' in user_data:
                language = user_data['language']['S']

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
    Stores user feedback for a specific referral.

    Args:
        user_id: The ID of the user
        referral_id: The ID of the referral
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
        # Check if user and referral exist
        response = dynamodb_client.get_item(
            TableName='user_data',
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

        if 'referrals' not in user_data or referral_id not in user_data['referrals']['M']:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Referral not found for this user'})
            }

        # Store feedback with timestamp
        current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        dynamodb_client.update_item(
            TableName='user_data',
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
    Fetches user details with all referrals from DynamoDB.
    Also generates top 5 feedback questions for referrals without feedback.

    Args:
        user_id: The ID of the user to fetch
        language: The language for translation (english, spanish, polish)

    Returns:
        Response with user details, formatted referrals, and top 5 feedback questions
    """
    try:
        # Get the language code for translations
        lang_code = get_language_code(language)
        needs_translation = language.lower() in ['spanish', 'polish']

        # Get the user from DynamoDB with native format
        response = dynamodb_client.get_item(
            TableName='user_data',
            Key={
                'user_id': {'S': user_id}
            }
        )

        # Check if user exists
        if 'Item' not in response:
            message = 'User not found'
            if needs_translation:
                message = translate_text(message, lang_code)

            return {
                'statusCode': 404,
                'body': json.dumps({'message': message})
            }

        # Extract and format user data
        user_data = response['Item']
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

        # Process referrals if available
        formatted_referrals = []
        feedback_questions = []

        if 'referrals' in user_data and 'M' in user_data['referrals']:
            referrals_map = user_data['referrals']['M']

            # Create a list of referrals without feedback to prioritize
            referrals_needing_feedback = []

            for referral_id, referral_data in referrals_map.items():
                referral_content = referral_data['M']

                # Extract referral details
                agency = referral_content.get('agency', {}).get('S', '')
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
                    'timestamp': timestamp
                }

                # Add feedback if it exists
                if has_feedback:
                    formatted_referral['feedback'] = feedback_value

                formatted_referrals.append(formatted_referral)

                # Add to list of referrals needing feedback if no feedback exists
                if not has_feedback:
                    # Sort by timestamp if available (newest first)
                    try:
                        ts = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() if timestamp else 0
                    except ValueError:
                        ts = 0

                    referrals_needing_feedback.append({
                        'referral_id': referral_id,
                        'agency': agency,  # Already translated if needed
                        'address': address,
                        'zipcode': zipcode,
                        'service_category': service_category,  # Already translated if needed
                        'timestamp': timestamp,
                        'ts': ts  # Use for sorting
                    })

            # Sort referrals needing feedback by timestamp (newest first)
            referrals_needing_feedback.sort(key=lambda x: x['ts'], reverse=True)

            # Generate feedback questions for the top 5 referrals
            for referral in referrals_needing_feedback[:5]:
                # Create the base question in English
                english_question = f"Hi {user_id}, Did the referral {referral['agency']}, {referral['address']}, {referral['zipcode']} help you in {referral['service_category']}? Please reply with yes or no."

                # Translate the question if needed
                question = english_question
                if needs_translation:
                    question = translate_text(english_question, lang_code)

                feedback_questions.append({
                    'referral_id': referral['referral_id'],
                    'question': question,
                    'agency': referral['agency'],
                    'service_category': referral['service_category']
                })

        # Add formatted referrals to user data
        formatted_user['referrals'] = formatted_referrals

        # Prepare the success message
        success_message = 'User data retrieved successfully.'
        if needs_translation:
            success_message = translate_text(success_message, lang_code)

        # Store the language preference in DynamoDB for future use
        if language != 'english':
            try:
                dynamodb_client.update_item(
                    TableName='user_data',
                    Key={
                        'user_id': {'S': user_id}
                    },
                    UpdateExpression="SET #lang = :language",
                    ExpressionAttributeNames={
                        '#lang': 'language'
                    },
                    ExpressionAttributeValues={
                        ':language': {'S': language}
                    }
                )
            except Exception as e:
                print(f"Error updating language preference: {str(e)}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'user': formatted_user,
                'feedback_questions': feedback_questions,
                'message': success_message,
                'language': language
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

def create_or_update_user(user_id, zipcode, phone, email):
    """
    Creates or updates a user in DynamoDB.

    Args:
        user_id: The ID of the user
        zipcode: User's zipcode
        phone: User's phone number (optional)
        email: User's email (optional)

    Returns:
        Response indicating success or failure
    """
    # Validation
    if not zipcode:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Zipcode is required for creating/updating a user'})
        }

    try:
        # Check if user exists
        response = dynamodb_client.get_item(
            TableName='user_data',
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

            if update_expressions:
                update_expression = "SET " + ", ".join(update_expressions)

                dynamodb_client.update_item(
                    TableName='user_data',
                    Key={
                        'user_id': {'S': user_id}
                    },
                    UpdateExpression=update_expression,
                    ExpressionAttributeValues=expression_attribute_values
                )

            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'User data updated successfully.'})
            }
        else:
            # Create new user
            item = {
                'user_id': {'S': user_id},
                'Zipcode': {'S': zipcode}
            }

            if phone:
                item['Phone'] = {'S': phone}
            if email:
                item['Email'] = {'S': email}

            dynamodb_client.put_item(
                TableName='user_data',
                Item=item
            )

            return {
                'statusCode': 201,
                'body': json.dumps({'message': 'User data created successfully.'})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error storing user data: {str(e)}'})
        }