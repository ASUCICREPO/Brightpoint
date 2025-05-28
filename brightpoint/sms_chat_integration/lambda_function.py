import json
import boto3
import os
import logging
from botocore.exceptions import ClientError
import uuid
from urllib.parse import urlencode
import http.client
import urllib.parse
import socket
import re

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuration - retrieve from environment variables
APPLICATION_ID = os.environ.get('PINPOINT_APPLICATION_ID')
API_GATEWAY_URL = os.environ.get('API_GATEWAY_URL')
ENV = os.environ.get('ENVIRONMENT', 'dev')
USER_TABLE_NAME = f'user_data-{ENV}'
SOURCE_ACCOUNT_ROLE_ARN = os.environ.get('SOURCE_ACCOUNT_ROLE_ARN', 'arn:aws:iam::514811724234:role/crossAccountPinpointAccess')
DEFAULT_ZIPCODE = os.environ.get('DEFAULT_ZIPCODE', '60067')
DEFAULT_LANGUAGE = os.environ.get('DEFAULT_LANGUAGE', 'english')
PINPOINT_REGION = os.environ.get('PINPOINT_REGION', 'us-east-1')
HTTP_TIMEOUT = int(os.environ.get('HTTP_TIMEOUT', '60'))  # 60 seconds timeout
MAX_SMS_LENGTH = int(os.environ.get('MAX_SMS_LENGTH', '1600'))  # Increased for concatenated SMS
SENDER_ID = os.environ.get('SENDER_ID', 'CHATBOT')  # Sender ID for SMS

# Log all environment variables for debugging
logger.info(f"APPLICATION_ID: {APPLICATION_ID}")
logger.info(f"API_GATEWAY_URL: {API_GATEWAY_URL}")
logger.info(f"USER_TABLE_NAME: {USER_TABLE_NAME}")
logger.info(f"SOURCE_ACCOUNT_ROLE_ARN: {SOURCE_ACCOUNT_ROLE_ARN}")
logger.info(f"DEFAULT_ZIPCODE: {DEFAULT_ZIPCODE}")
logger.info(f"DEFAULT_LANGUAGE: {DEFAULT_LANGUAGE}")
logger.info(f"PINPOINT_REGION: {PINPOINT_REGION}")
logger.info(f"HTTP_TIMEOUT: {HTTP_TIMEOUT}")
logger.info(f"MAX_SMS_LENGTH: {MAX_SMS_LENGTH}")
logger.info(f"SENDER_ID: {SENDER_ID}")
logger.info(f"Current region: {os.environ.get('AWS_REGION', 'not set')}")

# Initialize AWS clients for services in the current account
sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

# Get the user_data table
user_table = dynamodb.Table(USER_TABLE_NAME)

def sanitize_sms_message(message, max_length=1000):  # Use a more conservative max length
    """
    Sanitize the SMS message to prevent delivery failures:
    - Trim to maximum length (conservative)
    - Remove problematic characters
    - Ensure valid encoding
    """
    try:
        if not message:
            return "Message received."

        # If message is a dictionary or JSON, convert to string
        if isinstance(message, dict):
            try:
                message = json.dumps(message)
            except:
                message = str(message)

        # Remove potentially problematic characters (extended list)
        problematic_chars = ['\u2028', '\u2029', '\0', '\u001F', '\u007F', '\u2022',
                            '•', '…', '—', '–', '†', '‡', '‹', '›', ''', ''', '"', '"',
                            '™', '®', '©', '§', '¶', '≈', '≠', '≤', '≥', '±', '¼', '½', '¾']
        for char in problematic_chars:
            message = message.replace(char, '')

        # Replace fancy quotes/apostrophes with standard ones
        message = message.replace('"', '"').replace('"', '"')
        message = message.replace(''', "'").replace(''', "'")
        message = message.replace('–', '-').replace('—', '-')

        # Replace other potentially problematic characters
        message = message.replace('•', '*').replace('…', '...')

        # Remove any URLs or links if present (these often cause issues)
        message = re.sub(r'https?://\S+', '[link]', message)
        message = re.sub(r'www\.\S+', '[link]', message)

        # Replace any instances of multiple spaces with a single space
        message = re.sub(r'\s+', ' ', message)

        # Ensure message is valid GSM 7-bit compatible (most restrictive but safest for SMS)
        gsm_compatible = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ @£$¥èéùìòÇØøÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ!\"#¤%&'()*+,-./:;<=>?¡ÄÖÑÜä§ö¿ñüà"
        filtered_message = ""
        for char in message:
            if char in gsm_compatible:
                filtered_message += char
            else:
                filtered_message += " "  # Replace with space instead of dropping

        message = filtered_message

        # Strict maximum length - SMS providers often have hard limits
        if len(message) > max_length:
            message = message[:max_length-5] + "..."

        # Ensure there's actually content
        if not message or message.strip() == '':
            return "Message received."

        logger.info(f"Sanitized message length: {len(message)}")
        return message
    except Exception as e:
        logger.error(f"Error sanitizing message: {str(e)}")
        return "We received your message. Please try again with simpler text."

def clean_api_response(response_data):
    """
    Clean API response to extract Agency, Address, Phone for up to 3 services
    Each service will be returned as a separate message
    """
    try:
        # Parse the response data if it's a string
        if isinstance(response_data, str):
            try:
                data = json.loads(response_data)
            except:
                return [response_data[:600]]  # Limit plain text to 600 chars
        elif isinstance(response_data, dict):
            data = response_data
        else:
            return [str(response_data)[:600]]

        # Extract services if available
        services = None

        # Direct services access
        if 'services' in data and isinstance(data['services'], list):
            services = data['services']
        # Nested services access in response_data
        elif 'response_data' in data and isinstance(data['response_data'], dict):
            if 'services' in data['response_data'] and isinstance(data['response_data']['services'], list):
                services = data['response_data']['services']

        # If no services found or empty list
        if not services or len(services) == 0:
            return ["No services found for your query."]

        logger.info(f"Services are {services}")
        # Limit to max 3 services
        services = services[:3]

        # Format each service with only Agency, Address and Phone information
        formatted_services = []
        for service in services:
            # Initialize parts
            service_parts = []

            # Add agency name
            if 'agency' in service and service['agency']:
                service_parts.append(service['agency'])

            # Get address components and phone from details
            if 'details' in service and isinstance(service['details'], dict):
                details = service['details']

                # Collect address components
                address_parts = []
                if 'address' in details and details['address']:
                    address_parts.append(details['address'])
                if 'city' in details and details['city']:
                    address_parts.append(details['city'])
                if 'state' in details and details['state']:
                    address_parts.append(details['state'])

                # Create address string
                if address_parts:
                    address_str = ", ".join(address_parts)
                    service_parts.append(address_str)

                # Add phone only if it contains digits
                if 'phone' in details and details['phone']:
                    phone = details['phone']
                    # Remove 'Phone:' prefix
                    if 'Phone:' in phone:
                        phone = phone.replace('Phone:', '').strip()
                    # Fix phone formatting if it has Notes in it
                    if "[" in phone:
                        phone = phone.split("[")[0].strip()

                    # Check if phone contains any digits
                    if re.search(r'\d', phone):
                        service_parts.append(phone)
                    else:
                        logger.info(f"Skipping phone that contains no digits: {phone}")

            # Join the service info with spaces
            formatted_service = " ".join(service_parts)

            # Ensure the message isn't too long
            if len(formatted_service) > 600:
                formatted_service = formatted_service[:597] + "..."

            formatted_services.append(formatted_service)

        # Return the formatted services as individual messages
        return formatted_services

    except Exception as e:
        logger.error(f"Error cleaning API response: {str(e)}")
        return ["Request processed successfully."]

def get_pinpoint_client():
    """Get Pinpoint client with cross-account credentials"""
    try:
        logger.info("Starting cross-account role assumption process")
        # Assume role in source account
        sts_client = boto3.client('sts')

        logger.info(f"Attempting to assume role: {SOURCE_ACCOUNT_ROLE_ARN}")
        assumed_role = sts_client.assume_role(
            RoleArn=SOURCE_ACCOUNT_ROLE_ARN,
            RoleSessionName="PinpointCrossAccountAccess"
        )

        logger.info("Successfully assumed role, retrieving temporary credentials")
        credentials = assumed_role['Credentials']

        # Log credentials expiration (but not the secret values)
        if 'Expiration' in credentials:
            logger.info(f"Temporary credentials will expire at: {credentials['Expiration']}")

        # Use the explicit Pinpoint region
        logger.info(f"Creating Pinpoint client in region: {PINPOINT_REGION}")

        # Create Pinpoint client with the assumed role credentials
        pinpoint_client = boto3.client(
            'pinpoint',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
            region_name=PINPOINT_REGION
        )

        logger.info("Successfully created cross-account Pinpoint client")
        return pinpoint_client
    except Exception as e:
        logger.error(f"Error assuming role for Pinpoint access: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        # Fallback to default client if cross-account access fails
        logger.warning("Falling back to default Pinpoint client in current account")
        default_client = boto3.client('pinpoint', region_name=PINPOINT_REGION)
        logger.info(f"Default client created in region: {default_client.meta.region_name}")
        return default_client

def detect_language(message_text):
    """
    Language detection for English, Polish, and Spanish only.
    Returns: "english", "polish", or "spanish"
    """
    # Convert message to lowercase for comparison
    message_lower = message_text.lower()

    # List of common Spanish words/patterns
    spanish_indicators = [
        'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
        'y', 'o', 'pero', 'porque', 'como', 'cuando', 'donde',
        'qué', 'quién', 'cómo', 'cuándo', 'dónde', 'por qué',
        'gracias', 'hola', 'adiós', 'buenos días', 'buenas tardes',
        'buenas noches', 'por favor', 'de', 'en', 'con', 'para', 'por',
        'cerca', 'mí', 'tú', 'él', 'ella', 'nosotros', 'ustedes'
    ]

    # List of common Polish words/patterns
    polish_indicators = [
        'i', 'w', 'z', 'na', 'to', 'się', 'nie', 'jest', 'do', 'że',
        'a', 'jak', 'co', 'po', 'tak', 'czy', 'dla', 'od', 'przez', 'przy',
        'jestem', 'jesteś', 'dziękuję', 'proszę', 'przepraszam',
        'dzień dobry', 'dobry wieczór', 'dobranoc', 'cześć', 'pa'
    ]

    # Count indicators for each language
    spanish_count = 0
    polish_count = 0

    # Check Spanish indicators
    for indicator in spanish_indicators:
        if f" {indicator} " in f" {message_lower} " or message_lower.startswith(f"{indicator} ") or message_lower.endswith(f" {indicator}"):
            spanish_count += 1

    # Check Polish indicators
    for indicator in polish_indicators:
        if f" {indicator} " in f" {message_lower} " or message_lower.startswith(f"{indicator} ") or message_lower.endswith(f" {indicator}"):
            polish_count += 1

    # Determine language based on count
    if spanish_count > 1 and spanish_count > polish_count:
        return "spanish"
    elif polish_count > 1 and polish_count > spanish_count:
        return "polish"

    # Default to English if no clear match
    return "english"

def get_user_data_from_phone(phone_number):
    """
    Get user_id and zipcode based on phone number from DynamoDB
    Returns: (user_id, zipcode, exists)
    """
    try:
        logger.info(f"Retrieving user data for phone number: {phone_number}")
        logger.info(f"Using DynamoDB table: {USER_TABLE_NAME}")

        # Query DynamoDB for the phone number
        response = user_table.scan(
            FilterExpression="Phone = :phone",
            ExpressionAttributeValues={
                ":phone": phone_number
            }
        )

        logger.info(f"Scanned response is: {response}")
        logger.info(f"Scan response count: {response.get('Count', 0)}")

        # If phone exists, extract user_id and zipcode
        if response['Items'] and len(response['Items']) > 0:
            user_data = response['Items'][0]
            user_id = user_data.get('user_id', f"temp_{uuid.uuid4()}")
            zipcode = user_data.get('Zipcode', DEFAULT_ZIPCODE)

            logger.info(f"Found registered user with ID: {user_id}, zipcode: {zipcode}")
            return user_id, zipcode, True

        # Phone doesn't exist - use defaults
        logger.info(f"Phone number {phone_number} not found in database")
        temp_user_id = f"temp_{uuid.uuid4()}"
        return temp_user_id, DEFAULT_ZIPCODE, False

    except Exception as e:
        logger.error(f"Error retrieving user data: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error traceback: ", exc_info=True)

        # Default values in case of error
        temp_user_id = f"temp_{uuid.uuid4()}"
        return temp_user_id, DEFAULT_ZIPCODE, False

def send_sms_response(phone_number, message):
    """Send SMS response via Pinpoint with improved error handling - sending each service as a separate message"""
    try:
        # Clean the message to extract service information
        service_messages = []

        if isinstance(message, dict) or (isinstance(message, str) and message.startswith('{')):
            # Looks like JSON, clean it to get service messages
            service_messages = clean_api_response(message)
            if not isinstance(service_messages, list):
                service_messages = [service_messages]
            logger.info(f"Extracted {len(service_messages)} service messages")
        else:
            # For non-JSON responses, just use the message as-is
            service_messages = [message]

        # Get the appropriate Pinpoint client
        logger.info("Getting Pinpoint client via cross-account access")
        pinpoint = get_pinpoint_client()

        # Send each service message as a separate SMS, maximum 3
        responses = []
        sent_count = 0
        max_messages = min(len(service_messages), 3)  # Send at most 3 messages

        for i in range(max_messages):
            msg = service_messages[i]

            # Sanitize each message
            sanitized_message = sanitize_sms_message(msg, max_length=600)
            logger.info(f"Sending service message {i+1}/{max_messages}, length: {len(sanitized_message)} chars")

            # Prepare the SMS request for this service
            message_request = {
                'Addresses': {
                    phone_number: {
                        'ChannelType': 'SMS'
                    }
                },
                'MessageConfiguration': {
                    'SMSMessage': {
                        'Body': sanitized_message,
                        'MessageType': 'TRANSACTIONAL'
                    }
                }
            }

            # Send the message
            try:
                response = pinpoint.send_messages(
                    ApplicationId=APPLICATION_ID,
                    MessageRequest=message_request
                )

                # Check for success
                if 'MessageResponse' in response and 'Result' in response['MessageResponse']:
                    for phone, result in response['MessageResponse']['Result'].items():
                        delivery_status = result.get('DeliveryStatus')
                        status_message = result.get('StatusMessage', '')

                        if delivery_status == 'SUCCESSFUL':
                            logger.info(f"Successfully sent service message {i+1} to {phone}")
                            sent_count += 1
                        else:
                            logger.error(f"Failed to deliver service message {i+1}: {delivery_status} - {status_message}")

                            # Try again with a shorter message if it fails
                            if (delivery_status == 'PERMANENT_FAILURE' and
                                ('Invalid Message Body' in status_message or 'invalid' in status_message.lower())):
                                # Simplify even further
                                shorter_msg = sanitized_message[:300] + "..."
                                logger.info(f"Retrying with shorter message ({len(shorter_msg)} chars)")

                                fallback_request = {
                                    'Addresses': {
                                        phone_number: {
                                            'ChannelType': 'SMS'
                                        }
                                    },
                                    'MessageConfiguration': {
                                        'SMSMessage': {
                                            'Body': shorter_msg,
                                            'MessageType': 'TRANSACTIONAL'
                                        }
                                    }
                                }

                                fallback_response = pinpoint.send_messages(
                                    ApplicationId=APPLICATION_ID,
                                    MessageRequest=fallback_request
                                )

                                # Check if fallback was successful
                                if ('MessageResponse' in fallback_response and
                                    'Result' in fallback_response['MessageResponse']):
                                    for phone, result in fallback_response['MessageResponse']['Result'].items():
                                        if result.get('DeliveryStatus') == 'SUCCESSFUL':
                                            logger.info(f"Successfully sent shortened fallback for message {i+1}")
                                            sent_count += 1

                responses.append(response)

                # Add a small delay between messages to prevent rate limiting
                if i < max_messages - 1:
                    import time
                    time.sleep(1)

            except Exception as msg_err:
                logger.error(f"Error sending service message {i+1}: {str(msg_err)}")

        # Summary log
        logger.info(f"SMS sending completed. Successfully sent {sent_count}/{max_messages} messages")

        # Return the list of responses
        return responses

    except Exception as e:
        logger.error(f"Failed to send SMS: {e}")
        logger.error(f"Error type: {type(e).__name__}")

        # Try a simple fallback message
        try:
            logger.info("Sending simple fallback message after error")
            pinpoint = get_pinpoint_client()

            fallback_request = {
                'Addresses': {
                    phone_number: {
                        'ChannelType': 'SMS'
                    }
                },
                'MessageConfiguration': {
                    'SMSMessage': {
                        'Body': "Your message was received. We found services in your area. Please try again for details.",
                        'MessageType': 'TRANSACTIONAL'
                    }
                }
            }

            return pinpoint.send_messages(
                ApplicationId=APPLICATION_ID,
                MessageRequest=fallback_request
            )
        except Exception as fallback_err:
            logger.error(f"Failed to send fallback message: {str(fallback_err)}")
            return None

def extract_response_message(response_data):
    """Extract the message from API response data"""
    try:
        # Try to parse response as JSON
        json_response = json.loads(response_data)
        logger.info(f"Response JSON keys: {list(json_response.keys())}")

        # Return the entire response for further processing
        return json_response

    except:
        # If parsing fails, return the original response
        if response_data:
            return response_data
        else:
            return f"Your message has been processed. Reference: {uuid.uuid4()}"

def call_api_using_lambda(payload):
    """Use AWS Lambda invoke to call another service"""
    try:
        # Check if there's an environment variable for a Lambda function name
        chatbot_lambda = os.environ.get('CHATBOT_LAMBDA_NAME')
        if not chatbot_lambda:
            logger.error("CHATBOT_LAMBDA_NAME environment variable not set")
            return None

        logger.info(f"Attempting to invoke Lambda function: {chatbot_lambda}")

        # Convert payload to JSON string
        payload_json = json.dumps(payload)

        # Invoke Lambda
        lambda_client = boto3.client('lambda')
        lambda_response = lambda_client.invoke(
            FunctionName=chatbot_lambda,
            InvocationType='RequestResponse',
            Payload=payload_json
        )

        # Read and parse Lambda response
        if 'Payload' in lambda_response:
            lambda_response_payload = lambda_response['Payload'].read().decode('utf-8')
            logger.info(f"Lambda response received, length: {len(lambda_response_payload)}")
            return lambda_response_payload
        else:
            logger.error("No payload in Lambda response")
            return None
    except Exception as e:
        logger.error(f"Lambda invocation failed: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        return None

def forward_to_chatbot_api(phone_number, message_text):
    """Forward the message to the chatbot API Gateway endpoint and get response"""
    try:
        # Get user data from the phone number
        user_id, zipcode, phone_exists = get_user_data_from_phone(phone_number)

        # If phone number is not registered, return registration message and don't forward to API
        if not phone_exists:
            logger.info(f"Phone number {phone_number} not registered - sending registration reminder")
            return "You are not registered with our service. Please register or add your phone number to your profile to access our services."

        # Continue with API call only if phone exists in database
        logger.info(f"Forwarding message to chatbot API - Phone: {phone_number}, User ID: {user_id}, Zipcode: {zipcode}")
        logger.info(f"Message content: {message_text}")
        logger.info(f"API Gateway URL: {API_GATEWAY_URL}")

        # Detect language
        language = detect_language(message_text)
        logger.info(f"Detected language: {language}")

        # Prepare the payload in the required format
        payload = {
            "user_id": user_id,
            "zipcode": zipcode,
            "user_query": message_text,
            "language": language
        }

        # Log the payload being sent
        logger.info(f"Prepared payload for API Gateway: {json.dumps(payload, default=str)}")

        # If API Gateway URL is not set, return error message
        if not API_GATEWAY_URL:
            logger.error("API_GATEWAY_URL is not set")
            return f"Your message has been received, but we're unable to process it at this time. ID: {uuid.uuid4()}"

        # First attempt: Direct HTTP connection with longer timeout
        try:
            logger.info(f"Attempting to call API using HTTP connection with {HTTP_TIMEOUT}s timeout")

            # Convert payload to JSON string
            payload_json = json.dumps(payload)

            # Parse URL
            url = urllib.parse.urlparse(API_GATEWAY_URL)
            host = url.netloc
            path = url.path

            logger.info(f"Parsed API Gateway URL - Host: {host}, Path: {path}")

            # Set socket timeout
            original_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(HTTP_TIMEOUT)

            try:
                # Create HTTP connection
                is_https = url.scheme == 'https' or not url.scheme
                if is_https:
                    conn = http.client.HTTPSConnection(host)
                else:
                    conn = http.client.HTTPConnection(host)

                # Set headers
                headers = {
                    'Content-Type': 'application/json'
                }

                # Send request
                logger.info(f"Sending HTTP request to {host}{path}")
                conn.request('POST', path, payload_json, headers)

                # Get response - this is where the timeout often occurs
                logger.info("Waiting for response...")
                response = conn.getresponse()
                logger.info(f"Received response with status: {response.status}")

                # Read response data
                response_data = response.read().decode()
                logger.info(f"Response received, length: {len(response_data)}")

                # Extract message from response but keep full data structure
                api_response = extract_response_message(response_data)
                logger.info(f"Extracted API response type: {type(api_response)}")

                # Success, return response
                logger.info("Successfully called API using HTTP connection")
                return api_response
            finally:
                # Reset socket timeout to original value
                socket.setdefaulttimeout(original_timeout)
                try:
                    conn.close()
                except:
                    pass

        except (socket.timeout, TimeoutError) as timeout_err:
            logger.warning(f"API call timed out after {HTTP_TIMEOUT} seconds: {str(timeout_err)}")
            # Continue to next method
        except Exception as http_err:
            logger.warning(f"HTTP connection failed: {str(http_err)}")
            # Continue to next method

        # Second attempt: Try using Lambda to call the chatbot API
        try:
            logger.info("Attempting to call API using Lambda invoke")
            lambda_response = call_api_using_lambda(payload)

            if lambda_response:
                api_response = extract_response_message(lambda_response)

                if api_response:
                    logger.info("Successfully called API using Lambda invoke")
                    return api_response
        except Exception as lambda_err:
            logger.warning(f"Lambda method failed: {str(lambda_err)}")

        # If all methods fail, return a friendly message
        logger.warning("All API call methods failed")
        return "We've received your message. Our system is currently experiencing high volume. Please try again in a few moments."

    except Exception as e:
        logger.error(f"Failed to forward to chatbot API: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error("Error traceback: ", exc_info=True)
        return f"Sorry, we encountered an error processing your request. Please try again later. Reference: {uuid.uuid4()}"

def lambda_handler(event, context):
    """AWS Lambda handler for SMS events from SNS/Pinpoint"""
    logger.info(f"Received event: {json.dumps(event, default=str)}")

    try:
        # Extract the SNS message
        logger.info("Extracting SNS message from event")
        sns_message = json.loads(event['Records'][0]['Sns']['Message'])
        logger.info(f"Extracted SNS message: {json.dumps(sns_message, default=str)}")

        # Extract phone number and message from the SNS notification
        phone_number = sns_message.get('originationNumber')
        message_text = sns_message.get('messageBody')

        logger.info(f"Extracted phone number: {phone_number}")
        logger.info(f"Extracted message text: {message_text}")

        if not phone_number or not message_text:
            logger.error("Missing required fields in SNS message")
            logger.error(f"Phone number present: {bool(phone_number)}")
            logger.error(f"Message text present: {bool(message_text)}")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields in SNS message'})
            }

        # Process the incoming SMS and forward to chatbot API
        logger.info("Processing the incoming SMS message")
        response_message = forward_to_chatbot_api(phone_number, message_text)
        logger.info(f"Response message type: {type(response_message)}")

        # Send response back to user
        logger.info("Sending response back to user")
        send_sms_response(phone_number, response_message)

        logger.info("Message processing completed successfully")
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Message processed successfully'})
        }

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error("Error traceback: ", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }