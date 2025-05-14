import json
import boto3
import re
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import getServiceCategories
import logging
from boto3.dynamodb.conditions import Attr
from boto3.dynamodb.types import TypeDeserializer
import traceback
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients with Lambda environment in mind
def get_boto_clients():
    try:
        # When running in Lambda, always use the default session
        # No need to check for environment variables
        session = boto3.Session()

        return {
            "bedrock": session.client('bedrock-runtime', region_name="us-east-1"),
            "dynamodb": session.resource("dynamodb", region_name="us-east-1"),
            "dynamodb_client": session.client('dynamodb', region_name="us-east-1")
        }
    except Exception as e:
        print(f"Error initializing AWS clients: {str(e)}")
        # Re-raise to make debugging easier
        raise

# Get clients
clients = get_boto_clients()
bedrock = clients["bedrock"]
dynamodb = clients["dynamodb"]
dynamodb_client = clients["dynamodb_client"]
ENV = os.environ.get('ENVIRONMENT', 'dev')
USER_TABLE = f'user_data-{ENV}'
REFERRAL_TABLE_NAME = f'referral_data-{ENV}'
QUERY_ANALYTICS_TABLE_NAME = f'query_analytics-{ENV}'
user_data_table = dynamodb.Table(USER_TABLE)
table = dynamodb.Table(REFERRAL_TABLE_NAME)
inference_profile_arn = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

def extract_categories_and_zipcode(query: str) -> Dict[str, Any]:
    """
    Args:
        query (str): The user's query
    Returns:
        Dict[str, Any]: Parsed response with extracted service categories and zipcode
    """
    try:
        # Use a valid model ID
        model_id = inference_profile_arn

        logger.info(f"Fetched service categories {getServiceCategories.getUniqueCategories()}")

        prompt = f"""
        TASK: Extract TWO key pieces of information from this query:
        1. ALL RELEVANT SERVICE CATEGORIES that match what the user is asking for
        2. The specific ZIPCODE where they need these services
        
        User Query: "{query}"
        
        AVAILABLE SERVICE CATEGORIES IN DATABASE:
        {', '.join(getServiceCategories.getUniqueCategories())}
        
        DETAILED INSTRUCTIONS:
        
        1. SERVICE CATEGORIES:
           - Identify ALL categories from our database that relate to what the user is asking for
           - Look for both EXACT MATCHES and SIMILAR/RELATED terms to what the user is asking about
           - Rank categories by relevance: exact matches first, followed by similar/related matches
           - Consider synonyms and related concepts (e.g., "hungry" → "Food Pantry", "can't pay rent" → "Housing")
           - For questions about food, consider "Food Pantry", "Food Assistance", "WIC", "SNAP", etc.
           - For questions about shelter or housing, consider "Housing", "Homeless Services", "Rental Assistance", etc.
           - For questions about children, consider "Child Care", "Children Services", "Youth Programs", etc.
           - For questions about medical needs, consider "Medical Services", "Healthcare", "Clinics", etc.
           - Return ALL relevant categories without limiting the number
           - Be comprehensive, but don't include categories that are completely unrelated
           - If no categories match or relate, return an empty array
        
        2. ZIPCODE:
           - Extract the exact 5-digit zipcode where the user needs services
           - Look for a 5-digit number in the query (e.g., 60605, 90210, 30312)
           - If no zipcode is mentioned, return null
        
        EXAMPLES:
        "Where are the food pantries in my area?" → ["Food Pantry"], null
        "Where are the food pantries in 60605?" → ["Food Pantry"], "60605"
        "Where are the shelters?" → ["Homeless Services", "Housing"], null
        "Where are the shelters near 90210?" → ["Homeless Services", "Housing"], "90210"
        
        RESPONSE FORMAT:
        Return ONLY a JSON object with this structure:
        {{
            "service_categories": ["category1", "category2", "category3", ...], 
            "zipcode": "5-digit zipcode or null if none found"
        }}
        
        The response must be valid, parseable JSON with no additional text.
        """

        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "system": "You are a specialized assistant that extracts specific structured information from human services queries.",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )

        # Parse response from Bedrock
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']

        logger.info(f"Response from Bedrock model: {response_body}")

        # Clean up the content - remove markdown code blocks if present
        content = content.strip()
        if content.startswith("```json") or content.startswith("```"):
            content = re.sub(r'^```json\s*', '', content)
            content = re.sub(r'^```\s*', '', content)
            content = re.sub(r'\s*```$', '', content)

        # Extract JSON from response
        try:
            # Try to parse the content as JSON
            result = json.loads(content)
            return result

        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {str(e)}")

            # Try to extract JSON from the response if there's extra text
            json_match = re.search(r'({.*})', content, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(1)
                    result = json.loads(json_str)
                    return result
                except Exception as e:
                    print(f"Failed to parse extracted JSON: {str(e)}")
                    return {"service_categories": [], "zipcode": None}

            return {"service_categories": [], "zipcode": None}

    except Exception as e:
        print(f"Error in Bedrock API call: {str(e)}")
        return {"service_categories": [], "zipcode": None}

def query_dynamodb_for_services(service_categories: Optional[List[str]], zipcode: Optional[str]) -> List[Dict[str, Any]]:
    """
    Query DynamoDB for services matching the given categories and zipcode using scan operation
    """
    try:
        print(f"DEBUG - Input parameters: service_categories={service_categories}, zipcode={zipcode}")

        # Return empty results if either service_categories or zipcode is missing
        if not zipcode or not service_categories:
            print("DEBUG - Both service_categories and zipcode are required, returning empty results")
            return []

        clean_zip = int(zipcode.strip())

        # Create FilterExpression - we know both parameters are present at this point
        filter_expr = Attr('Service Category Type').is_in(service_categories) & Attr('Service Area Zip Code').eq(clean_zip)

        # Execute the scan operation
        response = table.scan(
            FilterExpression=filter_expr,
        )

        logger.info(f"DEBUG - Filter expression response: {response}")

        # Get items from response
        all_results = response.get('Items', [])

        # Handle pagination if necessary
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                FilterExpression=filter_expr,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            all_results.extend(response.get('Items', []))

        # The items from DynamoDB are already in the correct format
        # No need for manual deserialization since boto3 handles this for you
        return all_results

    except Exception as e:
        print(f"Error in query_dynamodb_for_services: {str(e)}")
        print(traceback.format_exc())
        return []

def format_response(services: List[Dict[str, Any]], service_categories: Optional[List[str]],
                    zipcode: Optional[str] = None, user_id: str = None) -> Dict[str, Any]:
    """
    Formats the service data into a JSON response and stores referrals in user_data table.

    Args:
        services: List of service items from DynamoDB
        service_categories: Optional list of service categories that were searched for
        zipcode: Optional zipcode that was searched for
        user_id: User ID for storing referrals (required)

    Returns:
        JSON formatted response
    """
    try:
        # Validate user_id is provided
        if user_id is None:
            raise ValueError("user_id is required for format_response")

        response_data = {
            "status": "success",
            "service_categories": service_categories if service_categories else [],
            "zipcode": zipcode,
            "services": [],
            "message": ""
        }

        if not services:
            response_data["status"] = "no_results"
            if service_categories and len(service_categories) > 0 and zipcode:
                categories_str = ", ".join(service_categories)
                response_data["message"] = f"I couldn't find any {categories_str} services in the {zipcode} area."
            elif service_categories and len(service_categories) > 0:
                categories_str = ", ".join(service_categories)
                response_data["message"] = f"I couldn't find any information about {categories_str} services."
            else:
                response_data["message"] = "I need more information to help you find services. Can you tell me what type of service you're looking for?"

            return response_data

        # Format intro based on query params
        if service_categories and len(service_categories) > 0:
            categories_str = ", ".join(service_categories)
            if zipcode:
                response_data["message"] = f"Here are {categories_str} services available in the {zipcode} area."
            else:
                response_data["message"] = f"Here are {categories_str} services available."
        else:
            response_data["message"] = "Here are the services that match your query."

        # Format service details and add referral_id to each service
        for i, service in enumerate(services):
            # Set referral_id to be the same as user_id
            service['referral_id'] = service.get('referral_id')

            # Handle Organization field (was Agency)
            organization_name = service.get('\ufeffOrganization', service.get('Organization', 'Unnamed Service'))

            service_details = {
                "agency": organization_name,  # Keep output field name as "agency" for backward compatibility
                "details": {}
            }

            # Add referral process if available
            referral = service.get('Referral Process', '')
            if referral and referral.lower() != 'not specified':
                service_details["details"]["referral_process"] = referral

            # Add hours if available
            hours = service.get('Hours', '')
            if hours and hours.lower() != 'information not found':
                service_details["details"]["hours"] = hours

            # Add referral_id to details
            service_details["details"]["referral_id"] = user_id

            # Add eligibility if available
            eligibility = service.get('Eligibility Requirements', '')
            if eligibility and eligibility.lower() != 'not specified':
                service_details["details"]["eligibility"] = eligibility

            # Add service availability if available
            availability = service.get('Service Availability', '')
            if availability and availability.lower() != 'not specified':
                service_details["details"]["service_availability"] = availability

            # Add any other fields that might be useful
            for key, value in service.items():
                if key not in ['\ufeffOrganization', 'Organization', 'Referral Process', 'Hours',
                             'Eligibility Requirements', 'Service Availability', 'referral_id'] and value:
                    # Don't duplicate data we've already included
                    service_details["details"][key.lower().replace(" ", "_")] = value

            print("Service details:", service_details)
            response_data["services"].append(service_details)

        # Always attempt to store referrals if services were found
        if services:
            print(f"Services found, adding referrals for user {user_id}")
            add_referrals_to_user_data(user_id, services)

        return response_data
    except Exception as e:
        print(f"Error formatting response: {str(e)}")
        return {
            "status": "error",
            "message": "I encountered an error while formatting the service information. Please try again.",
            "error": str(e)
        }

def add_referrals_to_user_data(user_id: str, services: List[Dict[str, Any]]) -> None:
    """
    Add referral data to the user_data DynamoDB table by appending to existing user records
    or creating new ones if the user doesn't exist. Uses a nested referrals map structure.

    Args:
        user_id: The ID of the user receiving the referrals
        services: List of service items to be stored as referrals
    """
    try:
        if not services or not user_id:
            print("No services or user_id provided. Skipping referral storage.")
            return

        timestamp = datetime.now().isoformat()

        # Check if user exists in the database
        try:
            response = dynamodb_client.get_item(
                TableName=USER_TABLE,
                Key={
                    'user_id': {'S': user_id}
                }
            )
            user_exists = 'Item' in response
            print(f"User exists check: {user_exists}")
        except Exception as e:
            print(f"Error checking if user exists: {str(e)}")
            user_exists = False

        # For a new user, we'll build a complete item with referrals map
        if not user_exists:
            # Build a referrals map with all services for new user
            referrals_map = {'M': {}}

            for service in services:
                # Handle the Unicode BOM in the Organization field name
                organization_name = service.get('\ufeffOrganization', service.get('Organization', 'Unnamed Service'))
                address = service.get('Address', '')
                zipcode = service.get('Service Area Zip Code', '')  # Updated to use Service Area Zip Code
                service_category = service.get('Service Category Type', '')  # Updated to use Service Category Type
                state = service.get('State', '')
                print("service", service)
                # Get the referral_id directly from the service
                referral_id = service.get('referral_id', '')
                print("referral_id:", referral_id)
                if not referral_id:
                    print(f"No referral_id found for service {organization_name}. Skipping.")
                    continue

                # Create the referral data
                referral_data = {
                    'M': {
                        'organization': {'S': organization_name},  # Changed from 'agency' to 'organization'
                        'address': {'S': address},
                        'zipcode': {'S': str(zipcode)},  # Convert to string to handle numeric values
                        'serviceCategory': {'S': service_category},
                        'state': {'S': state},
                        'timestamp': {'S': timestamp}
                    }
                }

                # Add this referral to the referrals map using referral_id as key
                referrals_map['M'][referral_id] = referral_data

            # Create new user with all referrals
            if referrals_map['M']:  # Only if we have valid referrals
                try:
                    user_item = {
                        'user_id': {'S': user_id},
                        'referrals': referrals_map
                    }

                    # Create the new user record with the referrals map
                    dynamodb_client.put_item(
                        TableName=USER_TABLE,
                        Item=user_item
                    )
                    print(f"Successfully created new user {user_id} with {len(referrals_map['M'])} referrals")
                except Exception as e:
                    print(f"Error creating new user with referrals: {str(e)}")
        else:
            # For existing user, process each service as an update to add to the referrals map
            for service in services:
                try:
                    # Handle the Unicode BOM in the Organization field name
                    organization_name = service.get('\ufeffOrganization', service.get('Organization', 'Unnamed Service'))
                    address = service.get('Address', '')
                    zipcode = service.get('Service Area Zip Code', '')  # Updated to use Service Area Zip Code
                    service_category = service.get('Service Category Type', '')  # Updated to use Service Category Type
                    state = service.get('State', '')

                    # Get the referral_id directly from the service
                    referral_id = service.get('referral_id', '')
                    if not referral_id:
                        print(f"No referral_id found for service {organization_name}. Skipping.")
                        continue

                    # Create the referral data
                    referral_data = {
                        'M': {
                            'organization': {'S': organization_name},  # Changed from 'agency' to 'organization'
                            'address': {'S': address},
                            'zipcode': {'S': str(zipcode)},  # Convert to string to handle numeric values
                            'serviceCategory': {'S': service_category},
                            'state': {'S': state},
                            'timestamp': {'S': timestamp}
                        }
                    }

                    # Check if referrals map already exists
                    check_response = dynamodb_client.get_item(
                        TableName=USER_TABLE,
                        Key={
                            'user_id': {'S': user_id}
                        },
                        ProjectionExpression='referrals'
                    )

                    referrals_exists = 'Item' in check_response and 'referrals' in check_response['Item']

                    if referrals_exists:
                        # Add new referral to existing referrals map
                        dynamodb_client.update_item(
                            TableName=USER_TABLE,
                            Key={
                                'user_id': {'S': user_id}
                            },
                            UpdateExpression="SET referrals.#rid = :rdata",
                            ExpressionAttributeNames={
                                '#rid': referral_id  # Use referral_id as the key
                            },
                            ExpressionAttributeValues={
                                ':rdata': referral_data
                            }
                        )
                    else:
                        # Create new referrals map with this referral
                        dynamodb_client.update_item(
                            TableName=USER_TABLE,
                            Key={
                                'user_id': {'S': user_id}
                            },
                            UpdateExpression="SET referrals = :rmap",
                            ExpressionAttributeValues={
                                ':rmap': {
                                    'M': {
                                        referral_id: referral_data  # Use referral_id as the key
                                    }
                                }
                            }
                        )

                    print(f"Successfully added referral with ID {referral_id} to user {user_id}")
                except Exception as e:
                    print(f"Error adding referral for service {organization_name}: {str(e)}")

    except Exception as e:
        print(f"Error in add_referrals_to_user_data: {str(e)}")

# Lambda handler - Keeping this for backward compatibility if this is called directly
def lambda_handler(event, context):
    try:
        # Extract query and user_id from the event
        query = event.get('query', '')
        user_id = event.get('user_id')
        language = event.get('language', 'english') # Extract language preference

        # Validate required parameters
        if not query:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "status": "error",
                    "message": "Query parameter is required"
                })
            }

        if not user_id:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "status": "error",
                    "message": "user_id parameter is required"
                })
            }

        # Extract categories and zipcode from the query
        extracted_data = extract_categories_and_zipcode(query)
        service_categories = extracted_data.get('service_categories', [])
        zipcode = extracted_data.get('zipcode')

        # Query DynamoDB for matching services
        services = query_dynamodb_for_services(service_categories, zipcode)
        print("Inside bedrockAgent lambda handler")

        # Format the response and store referrals if services found
        response_data = format_response(services, service_categories, zipcode, user_id)

        # Wrap the response for API Gateway
        return {
            "statusCode": 200,
            "body": json.dumps(response_data)
        }

    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "message": "An unexpected error occurred",
                "error": str(e)
            })
        }