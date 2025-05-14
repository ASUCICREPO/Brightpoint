import json
import boto3
import uuid
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, Any, List, Optional
import os
import re
import copy

_cached_secret = None

# Initialize AWS clients with Lambda environment in mind
def get_boto_clients():
    try:
        # When running in Lambda, always use the default session
        session = boto3.Session()

        return {
            "dynamodb": session.resource("dynamodb", region_name="us-east-1"),
            "dynamodb_client": session.client('dynamodb', region_name="us-east-1"),
            "translate": session.client('translate', region_name="us-east-1")  # Add AWS Translate client
        }
    except Exception as e:
        print(f"Error initializing AWS clients: {str(e)}")
        raise

# Get clients
clients = get_boto_clients()
dynamodb = clients["dynamodb"]
dynamodb_client = clients["dynamodb_client"]
translate_client = clients["translate"]  # AWS Translate client
query_cache_table = dynamodb.Table("perplexity_query_cache")  # Table to store Perplexity query results
user_data_table = dynamodb.Table("user_data")  # For user history

def get_perplexity_api_key():
    """Retrieve the Perplexity API key from AWS Secrets Manager with caching"""
    global _cached_secret

    if _cached_secret is not None:
        return _cached_secret

    secret_arn = os.environ['PERPLEXITY_API_KEY_SECRET_ARN']
    secrets_client = boto3.client('secretsmanager')

    try:
        response = secrets_client.get_secret_value(SecretId=secret_arn)
        _cached_secret = response['SecretString']
        return _cached_secret
    except Exception as e:
        print(f"Error retrieving secret: {str(e)}")
        raise

# Perplexity API configuration
PERPLEXITY_API_KEY = get_perplexity_api_key()
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

def get_language_code(provided_language: str) -> str:
    """
    Get language code from the provided language string

    Args:
        provided_language (str): Language string from input JSON

    Returns:
        str: Language code (e.g., 'en', 'es', 'pl')
    """
    try:
        # Mapping of common language names to ISO codes
        language_mapping = {
            'english': 'en',
            'spanish': 'es',
            'polish': 'pl',
            'español': 'es',
            'inglés': 'en',
            'polski': 'pl',
            'en': 'en',
            'es': 'es',
            'pl': 'pl'
        }

        # Normalize the provided language (lowercase, no spaces)
        normalized_language = provided_language.lower().strip()

        # Get language code from mapping or default to English
        return language_mapping.get(normalized_language, 'en')
    except Exception as e:
        print(f"Error processing language: {str(e)}")
        return 'en'  # Default to English on error

def translate_text(text: str, source_language: str, target_language: str) -> str:
    """
    Translate text from source language to target language

    Args:
        text (str): The text to translate
        source_language (str): Source language code
        target_language (str): Target language code

    Returns:
        str: Translated text
    """
    try:
        # If languages are the same, return the original text
        if source_language == target_language:
            return text

        response = translate_client.translate_text(
            Text=text,
            SourceLanguageCode=source_language,
            TargetLanguageCode=target_language
        )

        return response.get('TranslatedText', text)
    except Exception as e:
        print(f"Error translating text: {str(e)}")
        return text  # Return original text if translation fails

def get_language_name(language_code: str) -> str:
    """
    Convert language code to full name for use in prompts

    Args:
        language_code (str): ISO language code

    Returns:
        str: Full language name
    """
    language_map = {
        'en': 'english',
        'es': 'spanish',
        'pl': 'polish'
    }

    return language_map.get(language_code, 'english')

def translate_response_content(response_data: Dict[str, Any], target_language_code: str) -> Dict[str, Any]:
    """
    Translate the content of a response to the target language

    Args:
        response_data (Dict[str, Any]): The response data
        target_language_code (str): Target language code

    Returns:
        Dict[str, Any]: Translated response data
    """
    try:
        # Make a deep copy to avoid modifying the original
        translated_response = copy.deepcopy(response_data)
        source_language = 'en'  # Assume source is English

        # Update the language field
        target_language_name = get_language_name(target_language_code)
        translated_response['language'] = target_language_name

        # Translate the message field
        if 'message' in translated_response:
            translated_response['message'] = translate_text(
                translated_response['message'],
                source_language,
                target_language_code
            )
            print(f"Translated message: {translated_response['message']}")

        # Translate service categories
        if 'service_categories' in translated_response and isinstance(translated_response['service_categories'], list):
            translated_categories = []
            for category in translated_response['service_categories']:
                translated_category = translate_text(category, source_language, target_language_code)
                translated_categories.append(translated_category)
                print(f"Translated category: {category} -> {translated_category}")
            translated_response['service_categories'] = translated_categories

        # Translate service details
        if 'services' in translated_response and isinstance(translated_response['services'], list):
            for service in translated_response['services']:
                # Translate agency name
                if 'agency' in service:
                    original_agency = service['agency']
                    service['agency'] = translate_text(
                        original_agency,
                        source_language,
                        target_language_code
                    )
                    print(f"Translated agency: {original_agency} -> {service['agency']}")

                # Translate service details
                if 'details' in service:
                    details = service['details']

                    # Translate service category
                    if 'service_category' in details:
                        original_category = details['service_category']
                        details['service_category'] = translate_text(
                            original_category,
                            source_language,
                            target_language_code
                        )
                        print(f"Translated service category: {original_category} -> {details['service_category']}")

                    # Translate additional information
                    if 'additional_information' in details:
                        original_info = details['additional_information']
                        details['additional_information'] = translate_text(
                            original_info,
                            source_language,
                            target_language_code
                        )
                        print(f"Translated additional info: {original_info[:30]}... -> {details['additional_information'][:30]}...")

                    # Translate referral process
                    if 'referral_process' in details:
                        original_referral = details['referral_process']
                        details['referral_process'] = translate_text(
                            original_referral,
                            source_language,
                            target_language_code
                        )
                        print(f"Translated referral process: {original_referral} -> {details['referral_process']}")

                    # Translate hours
                    if 'hours' in details:
                        original_hours = details['hours']
                        details['hours'] = translate_text(
                            original_hours,
                            source_language,
                            target_language_code
                        )
                        print(f"Translated hours: {original_hours} -> {details['hours']}")

                    # Translate eligibility
                    if 'eligibility' in details:
                        original_eligibility = details['eligibility']
                        details['eligibility'] = translate_text(
                            original_eligibility,
                            source_language,
                            target_language_code
                        )
                        print(f"Translated eligibility: {original_eligibility} -> {details['eligibility']}")

        return translated_response
    except Exception as e:
        print(f"Error translating response content: {str(e)}")
        return response_data  # Return original response if translation fails

def query_perplexity(user_query: str, zipcode: Optional[str] = None, language: str = 'english') -> Dict[str, Any]:
    """
    Query the Perplexity API with the user's query using structured instructions

    Args:
        user_query (str): The user's query
        zipcode (Optional[str]): User's zipcode for location context
        language (str): Language to respond in

    Returns:
        Dict[str, Any]: Response from Perplexity
    """
    try:
        # Define the system prompt for specialized assistance with stronger language enforcement
        system_prompt = f"""You are a specialized assistant that provides detailed information about human services and support resources.
IMPORTANT: You must respond ONLY in {language} language. Do not use any other language.
Your responses should be helpful, accurate, and culturally sensitive.
When you don't know the answer to something, acknowledge it rather than making up information."""

        # Build a structured prompt similar to the Bedrock implementation
        structured_prompt = f"""
        TASK: Respond to a user query about human services and support resources.
        
        USER QUERY: "{user_query}"
        
        LOCATION CONTEXT: {f"Zipcode {zipcode}" if zipcode else "Location not specified"}
        
        DETAILED INSTRUCTIONS:
        
        1. SERVICE UNDERSTANDING:
           - Correctly identify what services the user is looking for
           - Consider both explicit and implicit needs in the query
           - Look for keywords related to food, housing, healthcare, childcare, etc.
           - Consider synonyms and related concepts across languages
           - For questions about food, address food pantries, meal programs, SNAP benefits, etc.
           - For questions about shelter, address emergency shelters, housing assistance, etc.
           - For questions about children, address childcare, youth programs, family services, etc.
           - For questions about medical needs, address clinics, healthcare programs, etc.
        
        2. LOCATION AWARENESS:
           - If a zipcode is provided, incorporate this into your response
           - If no location is specified, provide general information applicable to most locations
           - When appropriate, mention that services vary by location
        
        3. RESPONSE STRUCTURE:
           - Begin with a direct answer to the user's question
           - For each service, put the organization name in bold using markdown (** **)
           - After the organization name, list its full address on the next line
           - Use bullet points for hours, phone, and additional information
           - Keep your response concise but informative
           - CRITICAL: Your entire response must be in {language} language only
        
        RESPONSE FORMAT EXAMPLE:
        **Organization Name**
        123 Main Street, City, State 12345
        - Hours: Monday-Friday 9am-5pm
        - Phone: 555-123-4567
        - Additional information: Provides food, clothing, and emergency assistance.

        **Second Organization**
        456 Oak Avenue, City, State 12345
        - Hours: Tuesday & Thursday 10am-2pm
        - Phone: 555-987-6543
        - Requirements: Must bring ID and proof of residence
        
        REMEMBER: Your entire response must be in {language} language. This is absolutely required.
        """

        # Use only the confirmed working model
        model = "sonar-reasoning-pro"

        try:
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": structured_prompt
                    }
                ],
                "max_tokens": 1500
            }

            # Using urllib instead of requests
            data = json.dumps(payload).encode('utf-8')
            headers = {
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json",
                "Accept": "application/json"  # Explicitly request JSON response
            }

            print(f"Trying model: {model}")
            print(f"API Key (first 4 chars): {PERPLEXITY_API_KEY[:4]}...")
            print(f"Requesting response in: {language}")

            req = urllib.request.Request(PERPLEXITY_API_URL, data=data, headers=headers, method="POST")

            with urllib.request.urlopen(req) as response:
                response_data = response.read().decode('utf-8')
                print(f"Successfully queried Perplexity using model: {model}")
                return json.loads(response_data)

        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"Error with model {model}: {error_body}")
            return {"error": f"API Error: {e.code} - {e.reason}. Details: {error_body}"}
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")
            return {"error": f"URL Error: {e.reason}"}
        except Exception as e:
            print(f"Error querying Perplexity API: {str(e)}")
            return {"error": str(e)}

    except Exception as e:
        print(f"Error in query_perplexity: {str(e)}")
        return {"error": str(e)}

def store_query_in_dynamodb(user_query: str, original_query: str, response_data: Dict[str, Any], zipcode: Optional[str] = None, language: str = 'english', original_language_code: str = 'en') -> None:
    """
    Store the query and its response in DynamoDB for future use

    Args:
        user_query (str): The translated user query (in English)
        original_query (str): The original user query in its original language
        response_data (Dict[str, Any]): The response data to be stored
        zipcode (Optional[str]): User's zipcode
        language (str): Language name of the response
        original_language_code (str): Original language code
    """
    try:
        # Generate a query_id for this entry
        query_id = str(uuid.uuid4())

        # Create a normalized version of the query for easier matching
        normalized_query = user_query.lower().strip()
        zipcode_value = zipcode if zipcode else "none"

        # Store English versions of response data in DynamoDB
        english_response = response_data
        if original_language_code != 'en':
            # If the current response isn't in English, we need to create an English version for storage
            print("Creating English version of response for database storage")
            english_response = translate_response_content(response_data, 'en')
            print("Created English version of response for storage")

        # Store in DynamoDB
        query_cache_table.put_item(
            Item={
                "query_id": query_id,
                "original_query": original_query,
                "english_query": user_query,
                "normalized_query": normalized_query,
                "zipcode": zipcode_value,
                "language": "english",  # Always stored in English
                "language_code": "en",  # Always stored in English
                "original_language": language,  # Remember the original language
                "original_language_code": original_language_code,  # Remember the original language code
                "response_data": english_response,
                "timestamp": datetime.now().isoformat()
            }
        )
        print(f"Successfully stored query and response with ID {query_id}")

    except Exception as e:
        print(f"Error storing query in DynamoDB: {str(e)}")

def query_dynamodb_for_cached_response(user_query: str, zipcode: Optional[str] = None, language_code: str = 'en') -> Optional[Dict[str, Any]]:
    """
    Check if a similar query exists in DynamoDB cache, and filter by BOTH query AND zipcode.
    Only returns a cached response when BOTH query and zipcode match exactly.

    Args:
        user_query (str): The user's query (in English)
        zipcode (Optional[str]): User's zipcode for location context
        language_code (str): Language code for the response

    Returns:
        Optional[Dict[str, Any]]: Cached response if found, None otherwise
    """
    try:
        # Normalize the query
        normalized_query = user_query.lower().strip()
        zipcode_value = zipcode if zipcode else "none"

        print(f"Looking for cached response with query: '{normalized_query}', zipcode: '{zipcode_value}'")

        # Scan the table for a matching query + zipcode (looking only for English responses which we'll translate later)
        # IMPORTANT: Only return a match when BOTH query and zipcode match
        filter_expression = "normalized_query = :query AND zipcode = :zip"
        expression_values = {
            ":query": normalized_query,
            ":zip": zipcode_value
        }

        response = query_cache_table.scan(
            FilterExpression=filter_expression,
            ExpressionAttributeValues=expression_values
        )

        items = response.get('Items', [])
        if items:
            print(f"Found match with BOTH query and zipcode. Will translate response if needed.")
            # Return the most recent match
            items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            cached_response = items[0].get('response_data')

            # The cached response is in English - we'll translate it in the lambda handler
            return cached_response

        # If no match found with both query and zipcode, return None - no fallback to query-only matching
        print("No exact match with both query and zipcode. No cached response will be returned.")
        return None

    except Exception as e:
        print(f"Error querying DynamoDB for cached response: {str(e)}")
        return None

def extract_meaningful_response(perplexity_response: Dict[str, Any], language: str = 'english', zipcode: Optional[str] = None, user_query: str = '', user_id: str = '') -> Dict[str, Any]:
    """
    Extract the meaningful content from Perplexity's response and format it into structured service objects

    Args:
        perplexity_response (Dict[str, Any]): Raw response from Perplexity API
        language (str): Language of the response
        zipcode (Optional[str]): User's zipcode
        user_query (str): Original user query
        user_id (str): User's ID for referral tracking

    Returns:
        Dict[str, Any]: Structured response data with service objects
    """
    try:
        # Extract the actual content from Perplexity's response format
        if "choices" in perplexity_response and perplexity_response["choices"]:
            message = perplexity_response["choices"][0].get("message", {})
            content = message.get("content", "")

            # Determine service categories based on query
            service_categories = []
            service_category_main = ""

            # Keywords for all supported languages
            food_keywords = ["food", "pantry", "pantries", "comida", "despensa", "żywność", "spiżarnia"]
            housing_keywords = ["housing", "shelter", "homeless", "vivienda", "refugio", "sin hogar", "mieszkanie", "schronisko", "bezdomny"]
            child_keywords = ["child", "children", "kid", "niño", "niños", "hijo", "dziecko", "dzieci"]
            health_keywords = ["health", "medical", "doctor", "salud", "médico", "zdrowie", "lekarz"]
            education_keywords = ["university", "college", "school", "universidad", "escuela", "uniwersytet", "szkoła"]

            query_lower = user_query.lower()

            if any(keyword in query_lower for keyword in food_keywords):
                service_categories = ["Food Pantry", "Food Assistance", "Emergency Food"]
                service_category_main = "Food Pantry"
            elif any(keyword in query_lower for keyword in housing_keywords):
                service_categories = ["Housing", "Homeless Services", "Emergency Shelter"]
                service_category_main = "Housing"
            elif any(keyword in query_lower for keyword in child_keywords):
                service_categories = ["Child Care", "Children Services", "Youth Programs"]
                service_category_main = "Children Services"
            elif any(keyword in query_lower for keyword in health_keywords):
                service_categories = ["Medical Services", "Healthcare", "Clinics"]
                service_category_main = "Healthcare"
            elif any(keyword in query_lower for keyword in education_keywords):
                service_categories = ["Education", "Universities", "Academic Resources"]
                service_category_main = "Education"
            else:
                service_categories = ["General Assistance", "Social Services", "Community Resources"]
                service_category_main = "Social Services"

            # Extract and structure service information from the content
            services = []

            # Parse the content to find organizations and their details
            lines = content.split('\n')
            current_org = None
            current_details = {}

            for i, line in enumerate(lines):
                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                # Look for organization names (bolded with **)
                if line.startswith('**') and line.endswith('**'):
                    # Save previous organization if exists
                    if current_org and current_details:
                        # Add an ID to each service
                        if "id" not in current_details:
                            current_details["id"] = str(uuid.uuid4())

                        # Ensure referral_id is set
                        current_details["referral_id"] = user_id

                        # Add to services list
                        services.append({
                            "agency": current_org,
                            "details": current_details
                        })

                    # Start new organization
                    current_org = line.strip('*').strip()
                    current_details = {
                        "service_category": service_category_main,
                        "referral_id": user_id,
                        "source": "Perplexity AI",
                        "zipcode": zipcode if zipcode else ""
                    }

                # Look for address (typically the line after org name)
                elif current_org and i > 0 and lines[i-1].strip().startswith('**') and not line.startswith('-'):
                    # This is likely the address line
                    address_parts = line.split(',')

                    if len(address_parts) >= 1:
                        current_details["address"] = address_parts[0].strip()

                    if len(address_parts) >= 2:
                        # Try to extract city and state
                        if len(address_parts) >= 3:
                            current_details["city"] = address_parts[1].strip()
                            state_zip = address_parts[2].strip()

                            # Try to extract state
                            state_match = re.search(r'\b([A-Z]{2})\b', state_zip)
                            if state_match:
                                current_details["state"] = state_match.group(1)

                            # Try to extract zipcode
                            zip_match = re.search(r'\b(\d{5}(?:-\d{4})?)\b', state_zip)
                            if zip_match and "zipcode" not in current_details:
                                current_details["zipcode"] = zip_match.group(1)

                # Look for bullet points with details - handle multilingual cases
                elif current_org and line.startswith('-'):
                    line = line[1:].strip()  # Remove the bullet and trim

                    # Check for hours in any language
                    hour_prefixes = ['hours:', 'horario:', 'godziny:', 'hora:', 'horas:']
                    if any(line.lower().startswith(prefix) for prefix in hour_prefixes):
                        current_details["hours"] = line

                    # Check for phone in any language
                    phone_prefixes = ['phone:', 'teléfono:', 'telefon:', 'tel:']
                    if any(line.lower().startswith(prefix) for prefix in phone_prefixes):
                        current_details["phone"] = line

                        # Extract phone number and create referral process in appropriate language
                        phone_parts = line.split(':')
                        if len(phone_parts) > 1:
                            phone_number = phone_parts[1].strip()
                            if language.lower() == 'spanish':
                                current_details["referral_process"] = f"Llamar {phone_number}"
                            elif language.lower() == 'polish':
                                current_details["referral_process"] = f"Zadzwoń {phone_number}"
                            else:
                                current_details["referral_process"] = f"Call {phone_number}"

                    # Check for eligibility/requirements (multilingual terms)
                    eligibility_terms = [
                        'eligibility:', 'requirements:', 'qualify:', 'who can:',
                        'elegibilidad:', 'requisitos:', 'calificar:', 'quién puede:',
                        'kwalifikowalność:', 'wymagania:', 'kwalifikować:', 'kto może:'
                    ]

                    if any(line.lower().startswith(term) for term in eligibility_terms):
                        current_details["eligibility"] = line

                    # Additional information for anything else
                    else:
                        if "additional_information" not in current_details:
                            current_details["additional_information"] = line
                        else:
                            current_details["additional_information"] += ". " + line

            # Don't forget to add the last organization
            if current_org and current_details:
                # Add an ID to each service
                if "id" not in current_details:
                    current_details["id"] = str(uuid.uuid4())

                # Ensure referral_id is set
                current_details["referral_id"] = user_id

                # Add to services list
                services.append({
                    "agency": current_org,
                    "details": current_details
                })

            # If we couldn't extract any services but have content, create a general service
            if not services and content:
                services.append({
                    "agency": f"{service_category_main} Resources",
                    "details": {
                        "referral_id": user_id,
                        "id": str(uuid.uuid4()),
                        "service_category": service_category_main,
                        "source": "Perplexity AI",
                        "zipcode": zipcode if zipcode else "",
                        "additional_information": content
                    }
                })

            # Create message for response
            message = ""
            if language.lower() == 'spanish':
                message = f"Aquí están los servicios de {service_category_main}" + (f" en {zipcode}" if zipcode else "") + "."
            elif language.lower() == 'polish':
                message = f"Oto usługi {service_category_main}" + (f" w {zipcode}" if zipcode else "") + "."
            else:
                message = f"Here are {service_category_main} services" + (f" in {zipcode}" if zipcode else "") + "."

            # Format the response in a structure similar to the requested format
            formatted_response = {
                "status": "success",
                "source": "perplexity",
                "language": language,
                "service_categories": service_categories,
                "zipcode": zipcode,
                "services": services,
                "message": message
            }

            return formatted_response

        return {
            "status": "error",
            "message": "Failed to extract meaningful content from Perplexity response",
            "source": "perplexity"
        }

    except Exception as e:
        print(f"Error extracting meaningful response: {str(e)}")
        return {
            "status": "error",
            "message": f"Error processing Perplexity response: {str(e)}",
            "source": "perplexity"
        }

def update_user_query_history(user_id: str, user_query: str, original_query: str, response_data: Dict[str, Any], zipcode: Optional[str] = None, language: str = 'english') -> None:
    """
    Update the user's query history in the user_data table

    Args:
        user_id (str): The ID of the user
        user_query (str): The query in English
        original_query (str): The original query in its original language
        response_data (Dict[str, Any]): The response data
        zipcode (Optional[str]): User's zipcode
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
                                'source': {'S': 'perplexity'},
                                'zipcode': {'S': zipcode if zipcode else "none"},
                                'language': {'S': language},
                                'response': {'S': json.dumps(response_data)}
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
                                        'source': {'S': 'perplexity'},
                                        'zipcode': {'S': zipcode if zipcode else "none"},
                                        'language': {'S': language},
                                        'response': {'S': json.dumps(response_data)}
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
                                    'source': {'S': 'perplexity'},
                                    'zipcode': {'S': zipcode if zipcode else "none"},
                                    'language': {'S': language},
                                    'response': {'S': json.dumps(response_data)}
                                }
                            }
                        }
                    }
                }
            )

        print(f"Successfully updated query history for user {user_id}")

    except Exception as e:
        print(f"Error updating user query history: {str(e)}")

# Lambda handler
def lambda_handler(event, context):
    try:
        # Extract parameters from the event
        user_query_original = event.get('user_query', '')
        user_id = event.get('user_id')
        zipcode = event.get('zipcode')
        provided_language = event.get('language', '')

        # Validate required parameters
        if not user_query_original:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "status": "error",
                    "message": "user_query parameter is required"
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

        # Get language code from the provided language parameter
        # If not provided or unrecognized, default to English
        language_code = get_language_code(provided_language) if provided_language else 'en'

        language_name = get_language_name(language_code)
        print(f"Using language: {language_code} ({language_name})")

        # Store the original query
        original_query = user_query_original

        # Translate query to English if not already in English
        user_query = user_query_original
        if language_code != 'en':
            user_query = translate_text(user_query_original, language_code, 'en')
            print(f"Translated query to English: {user_query}")

        # First check if we have this query cached in DynamoDB (using the English version)
        cached_response = query_dynamodb_for_cached_response(user_query, zipcode, language_code)

        if cached_response:
            print("Found cached response in DynamoDB")

            # Always translate cached response to requested language
            # Since we always store in English, we need to translate to requested language
            if language_code != 'en':
                print(f"Translating cached response from English to {language_name}")
                translated_response = translate_response_content(cached_response, language_code)
            else:
                translated_response = cached_response

            # Update user history with both original and translated queries
            update_user_query_history(user_id, user_query, original_query, translated_response, zipcode, language_name)

            # Add response_data wrapper to match example format
            response_wrapper = {
                "user_id": user_id,
                "zipcode": zipcode,
                "language": language_name,
                "response_data": translated_response
            }

            return {
                "statusCode": 200,
                "body": json.dumps(response_wrapper)
            }

        # If not in cache, query Perplexity with the English query but request response in original language
        print(f"Querying Perplexity for: {user_query} (response in {language_name})")
        perplexity_response = query_perplexity(user_query, zipcode, language_name)

        if "error" in perplexity_response:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "status": "error",
                    "message": f"Error from Perplexity API: {perplexity_response['error']}",
                    "source": "perplexity"
                })
            }

        # Extract and format the response - pass the user_id for referral tracking
        formatted_response = extract_meaningful_response(perplexity_response, language_name, zipcode, user_query, user_id)

        # Store the query and response in DynamoDB for future use (store both original and English version)
        store_query_in_dynamodb(user_query, original_query, formatted_response, zipcode, language_name, language_code)

        # Update user history with both original and translated queries
        update_user_query_history(user_id, user_query, original_query, formatted_response, zipcode, language_name)

        # Add response_data wrapper to match example format
        response_wrapper = {
            "user_id": user_id,
            "zipcode": zipcode,
            "language": language_name,
            "response_data": formatted_response
        }

        return {
            "statusCode": 200,
            "body": json.dumps(response_wrapper)
        }

    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "message": "An unexpected error occurred",
                "error": str(e),
                "source": "perplexity_handler"
            })
        }