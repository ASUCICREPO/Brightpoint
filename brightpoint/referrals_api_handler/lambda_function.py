import json
import boto3
import uuid
import os
from boto3.dynamodb.types import TypeSerializer
from typing import Dict, Any, Optional, List
import decimal
import json
import time
import logging
import decimal

# Initialize DynamoDB clients
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('REFERRALS_TABLE_NAME', 'Referrals'))
connections_table = dynamodb.Table(os.environ.get('CONNECTIONS_TABLE_NAME', 'WebSocketConnections'))
serializer = TypeSerializer()

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# API Gateway Management API client
api_gateway_management = None

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)  # Convert Decimal to float for JSON serialization
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    """
    Main Lambda handler for API Gateway requests (both REST and WebSocket)
    """
    try:
        # Detect if this is a WebSocket request
        if 'requestContext' in event and 'connectionId' in event['requestContext'] and 'routeKey' in event['requestContext']:
            return handle_websocket_request(event, context)

        # Otherwise, handle as a REST API request
        http_method = event['httpMethod']
        path = event['path']

        # Route requests based on HTTP method and path
        if http_method == 'POST' and path == '/referrals':
            return create_referral(event)
        elif http_method == 'PUT' and path.startswith('/referrals/'):
            referral_id = path.split('/')[-1]
            return update_referral(event, referral_id)
        elif http_method == 'DELETE' and path.startswith('/referrals/'):
            referral_id = path.split('/')[-1]
            return delete_referral(referral_id)
        elif http_method == 'GET' and path == '/referrals':
            return get_all_referrals()
        elif http_method == 'GET' and path.startswith('/referrals/'):
            referral_id = path.split('/')[-1]
            return get_referral(referral_id)
        elif http_method == 'POST' and path == '/referrals/search':
            # New search endpoint
            return search_referrals(event)
        else:
            return build_response(404, {'message': 'Not Found'})

    except Exception as e:
        return build_response(500, {'error': str(e)})

def handle_websocket_request(event, context):
    """
    Handle WebSocket requests
    """
    connection_id = event['requestContext']['connectionId']
    domain_name = event['requestContext']['domainName']
    stage = event['requestContext']['stage']

    # Initialize API Gateway Management API client
    global api_gateway_management
    if api_gateway_management is None:
        api_gateway_management = boto3.client(
            'apigatewaymanagementapi',
            endpoint_url=f'https://{domain_name}/{stage}'
        )

    route_key = event['requestContext']['routeKey']

    try:
        if route_key == '$connect':
            # Handle new connection
            return handle_connect(connection_id, event)
        elif route_key == '$disconnect':
            # Handle disconnection
            return handle_disconnect(connection_id)
        elif route_key == '$default':
            # Handle default route - could be a catch-all handler
            return handle_default_message(connection_id, event)
        elif route_key == 'searchReferrals':
            # New search route for WebSocket
            return handle_search_referrals(connection_id, event)
        else:
            # Handle other custom routes like "getReferrals", "createReferral", etc.
            return handle_custom_route(connection_id, route_key, event)
    except Exception as e:
        print(f"Error handling WebSocket message: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}

def handle_connect(connection_id, event):
    """
    Handle new WebSocket connection
    """
    # Store connection ID in DynamoDB
    try:
        # You can extract query parameters from the event if needed
        query_params = event.get('queryStringParameters', {}) or {}

        connections_table.put_item(
            Item={
                'connectionId': connection_id,
                'timestamp': decimal.Decimal(int(time.time())),
                'ttl': decimal.Decimal(int(time.time()) + 24 * 60 * 60),  # 24-hour TTL
                'metadata': query_params
            }
        )
        return {'statusCode': 200, 'body': 'Connected'}
    except Exception as e:
        print(f"Error storing connection: {str(e)}")
        return {'statusCode': 500, 'body': 'Failed to connect'}

def handle_disconnect(connection_id):
    """
    Handle WebSocket disconnection
    """
    # Remove connection ID from DynamoDB
    try:
        connections_table.delete_item(Key={'connectionId': connection_id})
        return {'statusCode': 200, 'body': 'Disconnected'}
    except Exception as e:
        print(f"Error removing connection: {str(e)}")
        return {'statusCode': 500, 'body': 'Failed to disconnect'}

def handle_default_message(connection_id, event):
    """
    Handle default WebSocket message
    """
    try:
        message = json.loads(event.get('body', '{}'))

        # Echo the message back to the client
        send_to_connection(connection_id, {
            'message': 'Received your message',
            'data': message
        })

        return {'statusCode': 200, 'body': 'Message processed'}
    except Exception as e:
        print(f"Error handling default message: {str(e)}")
        return {'statusCode': 500, 'body': 'Failed to process message'}

def handle_search_referrals(connection_id, event):
    """
    Handle WebSocket search for referrals
    """
    try:
        message = json.loads(event.get('body', '{}'))
        search_params = message.get('searchParams', {})

        logger.info(f"Search params are {search_params}")
        # Perform the search
        results = perform_search(search_params)

        # Send results back to the client
        send_to_connection(connection_id, {
            'action': 'searchReferrals',
            'referrals': results
        })

        return {'statusCode': 200, 'body': 'Search processed'}
    except Exception as e:
        print(f"Error handling search: {str(e)}")
        send_to_connection(connection_id, {
            'action': 'error',
            'message': str(e)
        })
        return {'statusCode': 500, 'body': 'Failed to process search'}

def handle_custom_route(connection_id, route_key, event):
    """
    Handle custom WebSocket routes
    """
    try:
        message = json.loads(event.get('body', '{}'))

        # Route to appropriate handler based on the route_key
        if route_key == 'getReferrals':
            # Get all referrals and send them to the client
            response = table.scan()
            items = response.get('Items', [])

            # Handle pagination for large datasets
            while 'LastEvaluatedKey' in response:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response.get('Items', []))

            send_to_connection(connection_id, {
                'action': 'getReferrals',
                'referrals': items
            })

        elif route_key == 'getReferral':
            # Get a specific referral by ID
            referral_id = message.get('referral_id')
            if not referral_id:
                send_to_connection(connection_id, {
                    'action': 'error',
                    'message': 'Missing referral_id'
                })
                return {'statusCode': 400, 'body': 'Missing referral_id'}

            response = table.get_item(Key={'referral_id': referral_id})
            if 'Item' not in response:
                send_to_connection(connection_id, {
                    'action': 'error',
                    'message': f'Referral with ID {referral_id} not found'
                })
            else:
                send_to_connection(connection_id, {
                    'action': 'getReferral',
                    'referral': response['Item']
                })

        elif route_key == 'createReferral':
            # Create a new referral
            # Add unique IDs
            referral_id = str(uuid.uuid4())
            item_id = str(uuid.uuid4())

            # Prepare item for DynamoDB
            item = {
                'referral_id': referral_id,
                'id': item_id
            }

            # Add all fields from the request
            data = message.get('data', {})
            for key, value in data.items():
                if key not in ['referral_id', 'id']:  # Skip IDs as we've already set them
                    if key == 'Service Area Zip Code':
                        # Ensure zip code is stored as number
                        item[key] = int(value)
                    else:
                        item[key] = str(value)

            # Write to DynamoDB
            table.put_item(Item=item)

            # Broadcast to all connected clients
            broadcast_to_all({
                'action': 'newReferral',
                'referral': item
            })

            # Also send direct confirmation to the requesting client
            send_to_connection(connection_id, {
                'action': 'createReferral',
                'success': True,
                'referral_id': referral_id
            })

        elif route_key == 'updateReferral':
            # Update an existing referral
            referral_id = message.get('referral_id')
            data = message.get('data', {})

            if not referral_id:
                send_to_connection(connection_id, {
                    'action': 'error',
                    'message': 'Missing referral_id'
                })
                return {'statusCode': 400, 'body': 'Missing referral_id'}

            # Get the existing item first to confirm it exists
            response = table.get_item(Key={'referral_id': referral_id})
            if 'Item' not in response:
                send_to_connection(connection_id, {
                    'action': 'error',
                    'message': f'Referral with ID {referral_id} not found'
                })
                return {'statusCode': 404, 'body': 'Referral not found'}

            # Prepare update expressions
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}

            # Process each field in the request
            i = 0
            for key, value in data.items():
                if key not in ['referral_id', 'id']:  # Can't update primary keys
                    i += 1
                    attr_name = f"#attr{i}"
                    attr_val = f":val{i}"

                    update_expression += f"{attr_name} = {attr_val}, "
                    expression_attribute_names[attr_name] = key

                    if key == 'Service Area Zip Code':
                        # Handle numeric values
                        expression_attribute_values[attr_val] = int(value)
                    else:
                        expression_attribute_values[attr_val] = str(value)

            # Remove trailing comma and space
            update_expression = update_expression.rstrip(', ')

            # Update the item
            updated_item = table.update_item(
                Key={'referral_id': referral_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            ).get('Attributes', {})

            # Broadcast to all connected clients
            broadcast_to_all({
                'action': 'updatedReferral',
                'referral': updated_item
            })

            # Also send direct confirmation to the requesting client
            send_to_connection(connection_id, {
                'action': 'updateReferral',
                'success': True,
                'referral_id': referral_id
            })

        elif route_key == 'deleteReferral':
            # Delete a referral
            referral_id = message.get('referral_id')

            if not referral_id:
                send_to_connection(connection_id, {
                    'action': 'error',
                    'message': 'Missing referral_id'
                })
                return {'statusCode': 400, 'body': 'Missing referral_id'}

            # Check if the item exists
            response = table.get_item(Key={'referral_id': referral_id})
            if 'Item' not in response:
                send_to_connection(connection_id, {
                    'action': 'error',
                    'message': f'Referral with ID {referral_id} not found'
                })
                return {'statusCode': 404, 'body': 'Referral not found'}

            # Delete the item
            table.delete_item(Key={'referral_id': referral_id})

            # Broadcast to all connected clients
            broadcast_to_all({
                'action': 'deletedReferral',
                'referral_id': referral_id
            })

            # Also send direct confirmation to the requesting client
            send_to_connection(connection_id, {
                'action': 'deleteReferral',
                'success': True,
                'referral_id': referral_id
            })

        else:
            # Unknown route
            send_to_connection(connection_id, {
                'action': 'error',
                'message': f'Unknown route: {route_key}'
            })
            return {'statusCode': 400, 'body': f'Unknown route: {route_key}'}

        return {'statusCode': 200, 'body': 'Message processed'}
    except Exception as e:
        print(f"Error handling custom route {route_key}: {str(e)}")
        send_to_connection(connection_id, {
            'action': 'error',
            'message': str(e)
        })
        return {'statusCode': 500, 'body': 'Failed to process message'}

def send_to_connection(connection_id, data):
    """
    Send a message to a WebSocket connection.
    """
    try:
        if api_gateway_management is None:
            raise Exception("API Gateway Management client not initialized.")

        response = api_gateway_management.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(data, cls=DecimalEncoder).encode('utf-8')
        )
        logger.info(f"Successfully sent message to {connection_id}")
        return response

    except api_gateway_management.exceptions.GoneException:
        logger.warning(f"Connection {connection_id} no longer available, deleting.")
        connections_table.delete_item(Key={'connectionId': connection_id})
    except Exception as e:
        logger.error(f"Error sending message to connection {connection_id}: {str(e)}", exc_info=True)

def broadcast_to_all(data):
    """
    Broadcast a message to all connected WebSocket clients
    """
    # Get all connections
    scan_response = connections_table.scan(ProjectionExpression='connectionId')
    connections = scan_response.get('Items', [])

    # Handle pagination for large numbers of connections
    while 'LastEvaluatedKey' in scan_response:
        scan_response = connections_table.scan(
            ProjectionExpression='connectionId',
            ExclusiveStartKey=scan_response['LastEvaluatedKey']
        )
        connections.extend(scan_response.get('Items', []))

    # Send message to each connection
    for connection in connections:
        send_to_connection(connection['connectionId'], data)

# Original REST API functions
def create_referral(event):
    """
    Create a new referral entry in DynamoDB
    """
    try:
        body = json.loads(event['body'])

        # Add unique IDs
        referral_id = str(uuid.uuid4())
        item_id = str(uuid.uuid4())

        # Prepare item for DynamoDB
        item = {
            'referral_id': {'S': referral_id},
            'id': {'S': item_id}
        }

        # Add all fields from the request
        for key, value in body.items():
            if key not in ['referral_id', 'id']:  # Skip IDs as we've already set them
                if key == 'Service Area Zip Code':
                    # Ensure zip code is stored as number
                    item[key] = {'N': str(value)}
                else:
                    item[key] = {'S': str(value)}

        # Write to DynamoDB using low-level put_item
        dynamodb_client = boto3.client('dynamodb')
        dynamodb_client.put_item(
            TableName=table.name,
            Item=item
        )

        # Notify all WebSocket connections about the new referral
        broadcast_to_all({
            'action': 'newReferral',
            'referral': {
                'referral_id': referral_id,
                'id': item_id,
                **{k: v for k, v in body.items() if k not in ['referral_id', 'id']}
            }
        })

        # Return the created item
        return build_response(201, {'message': 'Referral created successfully', 'referral_id': referral_id})

    except Exception as e:
        return build_response(400, {'error': f'Failed to create referral: {str(e)}'})

def update_referral(event, referral_id):
    """
    Update an existing referral in DynamoDB
    """
    try:
        body = json.loads(event['body'])

        # Get the existing item first to confirm it exists
        response = table.get_item(Key={'referral_id': referral_id})
        if 'Item' not in response:
            return build_response(404, {'error': f'Referral with ID {referral_id} not found'})

        # Prepare update expressions
        update_expression = "SET "
        expression_attribute_values = {}
        expression_attribute_names = {}

        # Process each field in the request
        i = 0
        for key, value in body.items():
            if key not in ['referral_id', 'id']:  # Can't update primary keys
                i += 1
                attr_name = f"#attr{i}"
                attr_val = f":val{i}"

                update_expression += f"{attr_name} = {attr_val}, "
                expression_attribute_names[attr_name] = key

                if key == 'Service Area Zip Code':
                    # Handle numeric values
                    expression_attribute_values[attr_val] = int(value)
                else:
                    expression_attribute_values[attr_val] = str(value)

        # Remove trailing comma and space
        update_expression = update_expression.rstrip(', ')

        # Update the item
        updated_item = table.update_item(
            Key={'referral_id': referral_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues='ALL_NEW'
        ).get('Attributes', {})

        # Notify all WebSocket connections about the updated referral
        broadcast_to_all({
            'action': 'updatedReferral',
            'referral': updated_item
        })

        return build_response(200, {'message': f'Referral {referral_id} updated successfully'})

    except Exception as e:
        return build_response(400, {'error': f'Failed to update referral: {str(e)}'})

def delete_referral(referral_id):
    """
    Delete a referral from DynamoDB
    """
    try:
        # Check if the item exists
        response = table.get_item(Key={'referral_id': referral_id})
        if 'Item' not in response:
            return build_response(404, {'error': f'Referral with ID {referral_id} not found'})

        # Delete the item
        table.delete_item(Key={'referral_id': referral_id})

        # Notify all WebSocket connections about the deleted referral
        broadcast_to_all({
            'action': 'deletedReferral',
            'referral_id': referral_id
        })

        return build_response(200, {'message': f'Referral {referral_id} deleted successfully'})

    except Exception as e:
        return build_response(400, {'error': f'Failed to delete referral: {str(e)}'})

def get_all_referrals():
    """
    Get all referrals from DynamoDB
    """
    try:
        response = table.scan()
        items = response.get('Items', [])

        # Handle pagination for large datasets
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))

        return build_response(200, {'referrals': items})

    except Exception as e:
        return build_response(500, {'error': f'Failed to retrieve referrals: {str(e)}'})

def get_referral(referral_id):
    """
    Get a specific referral by ID
    """
    try:
        response = table.get_item(Key={'referral_id': referral_id})

        if 'Item' not in response:
            return build_response(404, {'error': f'Referral with ID {referral_id} not found'})

        return build_response(200, {'referral': response['Item']})

    except Exception as e:
        return build_response(500, {'error': f'Failed to retrieve referral: {str(e)}'})

def search_referrals(event):
    """
    Search referrals based on multiple criteria
    """
    try:
        body = json.loads(event['body'])
        search_params = body.get('searchParams', {})
        logger.info("Performing search operation")

        results = perform_search(search_params)

        return build_response(200, {'referrals': results})
    except Exception as e:
        return build_response(400, {'error': f'Failed to search referrals: {str(e)}'})

def perform_search(search_params):
    """
    Perform a search based on the provided parameters
    Supports search by agency names, zip codes, service categories, or cities
    """
    try:
        logger.info(f"Starting search with parameters: {search_params}")

        # Get all items from DynamoDB
        logger.info("Scanning DynamoDB table for items...")
        response = table.scan()
        items = response.get('Items', [])

        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))

        logger.info(f"Retrieved total of {len(items)} items from DynamoDB")

        # Prepare search terms
        agency_names = [name.lower() for name in search_params.get('Agency Names', []) if name]
        zip_codes = [int(zip_code) for zip_code in search_params.get('Service Area Zip Codes', []) if str(zip_code).isdigit()]
        service_categories = [category.lower() for category in search_params.get('Service Category Types', []) if category]
        cities = [city.lower() for city in search_params.get('Cities', []) if city]

        logger.debug(f"Processed search parameters: agencies={agency_names}, zips={zip_codes}, categories={service_categories}, cities={cities}")

        filtered_items = []

        for item in items:
            match = True  # Assume it matches until proven otherwise

            # Agency name check
            if agency_names:
                agency_value = item.get('Agency Name') or item.get('Organization')
                if agency_value:
                    agency_value = agency_value.lower()
                    if not any(name in agency_value for name in agency_names):
                        match = False
                else:
                    match = False

            # Zip code check
            if zip_codes and match:
                item_zip = None
                try:
                    if 'Service Area Zip Code' in item:
                        item_zip = int(item['Service Area Zip Code']) if isinstance(item['Service Area Zip Code'], (int, decimal.Decimal)) else None
                    elif 'Zipcode' in item:
                        item_zip = int(item['Zipcode']) if str(item['Zipcode']).isdigit() else None
                except Exception as e:
                    logger.warning(f"Failed to parse zip code for item: {e}")

                if item_zip not in zip_codes:
                    match = False

            # Service category check
            if service_categories and match:
                category_value = item.get('Service Category Type', "").lower()
                if not any(category in category_value for category in service_categories):
                    match = False

            # City check
            if cities and match:
                city_value = item.get('City', "").lower()
                if not any(city in city_value for city in cities):
                    match = False

            # If still matching, add to results
            if match:
                filtered_items.append(item)

        logger.info(f"Search completed: Found {len(filtered_items)} matching items.")
        return filtered_items

    except Exception as e:
        logger.error(f"Error during search: {e}", exc_info=True)
        raise e

    """
    Perform a search based on the provided parameters
    Supports search by agency names, zip codes, service categories, or cities
    """
    try:
        logger.info(f"Starting search with parameters: {search_params}")

        # Get all items from DynamoDB
        logger.info("Scanning DynamoDB table for items...")
        response = table.scan()
        items = response.get('Items', [])

        # Handle pagination for large datasets
        page_count = 1
        while 'LastEvaluatedKey' in response:
            logger.info(f"Retrieving additional page {page_count} of results")
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
            page_count += 1

        logger.info(f"Retrieved total of {len(items)} items from DynamoDB")

        # Filter items based on search criteria
        filtered_items = []

        # Extract search parameters
        agency_names = search_params.get('Agency Names', [])
        zip_codes = search_params.get('Service Area Zip Codes', [])
        service_categories = search_params.get('Service Category Types', [])
        cities = search_params.get('Cities', [])

        logger.debug(f"Raw search parameters - Agency Names: {agency_names}, Zip Codes: {zip_codes}, "
                   f"Service Categories: {service_categories}, Cities: {cities}")

        # Convert zip codes to integers if they're provided
        try:
            zip_codes = [int(zip_code) for zip_code in zip_codes]
            logger.debug(f"Converted zip codes to integers: {zip_codes}")
        except (ValueError, TypeError) as e:
            logger.warning(f"Error converting zip codes to integers: {e}. Setting to empty list.")
            # Handle case where zip codes might not be valid integers
            zip_codes = []

        # Case-insensitive search for text fields
        agency_names = [name.lower() if name else "" for name in agency_names]
        service_categories = [category.lower() if category else "" for category in service_categories]
        cities = [city.lower() if city else "" for city in cities]

        logger.debug(f"Processed search parameters - Agency Names: {agency_names}, Zip Codes: {zip_codes}, "
                   f"Service Categories: {service_categories}, Cities: {cities}")

        # Filter the items
        items_processed = 0
        matches_found = 0

        logger.info("Starting to filter items based on search criteria")
        for item in items:
            items_processed += 1
            if items_processed % 100 == 0:
                logger.debug(f"Processed {items_processed}/{len(items)} items")

            # If no search parameters are provided, include all items
            if not any([agency_names, zip_codes, service_categories, cities]):
                logger.debug("No search parameters provided, including all items")
                filtered_items.append(item)
                matches_found += 1
                continue

            # Debug item contents for troubleshooting
            item_id = item.get('id', 'unknown')
            referral_id = item.get('referral_id', 'unknown')
            logger.debug(f"Processing item ID: {item_id}, Referral ID: {referral_id}")

            # Check agency name match (if agency_names is provided)
            agency_match = False
            if not agency_names:
                agency_match = True
            elif 'Agency Name' in item:
                for name in agency_names:
                    if name in item['Agency Name'].lower():
                        logger.debug(f"Agency name match found: '{name}' in '{item['Agency Name']}'")
                        agency_match = True
                        break
            elif 'Organization' in item:  # Check alternative field name
                for name in agency_names:
                    if name in item['Organization'].lower():
                        logger.debug(f"Organization name match found: '{name}' in '{item['Organization']}'")
                        agency_match = True
                        break

            # Check zip code match (if zip_codes is provided)
            zip_match = False
            if not zip_codes:
                zip_match = True
            elif 'Service Area Zip Code' in item:
                try:
                    item_zip = int(item['Service Area Zip Code']) if isinstance(item['Service Area Zip Code'], (int, decimal.Decimal)) else None
                    if item_zip in zip_codes:
                        logger.debug(f"Zip code match found: {item_zip} in {zip_codes}")
                        zip_match = True
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error comparing zip code: {e} for item {item_id}")
            elif 'Zipcode' in item:  # Check alternative field name
                try:
                    item_zip = int(item['Zipcode']) if item['Zipcode'].isdigit() else None
                    if item_zip in zip_codes:
                        logger.debug(f"Zipcode match found: {item_zip} in {zip_codes}")
                        zip_match = True
                except (ValueError, TypeError, AttributeError) as e:
                    logger.warning(f"Error comparing zipcode: {e} for item {item_id}")

            # Check service category match (if service_categories is provided)
            category_match = False
            if not service_categories:
                category_match = True
            elif 'Service Category Type' in item:
                for category in service_categories:
                    if category in item['Service Category Type'].lower():
                        logger.debug(f"Service category match found: '{category}' in '{item['Service Category Type']}'")
                        category_match = True
                        break

            # Check city match (if cities is provided)
            city_match = False
            if not cities:
                city_match = True
            elif 'City' in item:
                for city in cities:
                    if city in item['City'].lower():
                        logger.debug(f"City match found: '{city}' in '{item['City']}'")
                        city_match = True
                        break

            # Include item if it matches at least one criterion
            if agency_match or zip_match or category_match or city_match:
                logger.debug(f"Adding item {item_id} to results. Matches: Agency={agency_match}, Zip={zip_match}, Category={category_match}, City={city_match}")
                filtered_items.append(item)
                matches_found += 1
            else:
                logger.debug(f"Item {item_id} did not match any criteria")

        logger.info(f"Search complete. Found {matches_found} matches out of {len(items)} items.")
        return filtered_items

    except Exception as e:
        logger.error(f"Error performing search: {str(e)}", exc_info=True)
        raise e
    """
    Perform a search based on the provided parameters
    Supports search by agency names, zip codes, service categories, or cities
    """
    try:
        # Get all items from DynamoDB
        response = table.scan()
        items = response.get('Items', [])

        # Handle pagination for large datasets
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))

        # Filter items based on search criteria
        filtered_items = []

        # Extract search parameters
        agency_names = search_params.get('Agency Names', [])
        zip_codes = search_params.get('Service Area Zip Codes', [])
        service_categories = search_params.get('Service Category Types', [])
        cities = search_params.get('Cities', [])

        # Convert zip codes to integers if they're provided
        try:
            zip_codes = [int(zip_code) for zip_code in zip_codes]
        except (ValueError, TypeError):
            # Handle case where zip codes might not be valid integers
            zip_codes = []

        # Case-insensitive search for text fields
        agency_names = [name.lower() if name else "" for name in agency_names]
        service_categories = [category.lower() if category else "" for category in service_categories]
        cities = [city.lower() if city else "" for city in cities]

        # Filter the items
        for item in items:
            # If no search parameters are provided, include all items
            if not any([agency_names, zip_codes, service_categories, cities]):
                filtered_items.append(item)
                continue

            # Check agency name match (if agency_names is provided)
            agency_match = not agency_names or (
                'Agency Name' in item and
                any(name in item['Agency Name'].lower() for name in agency_names)
            )

            # Check zip code match (if zip_codes is provided)
            zip_match = not zip_codes or (
                'Service Area Zip Code' in item and
                (isinstance(item['Service Area Zip Code'], (int, decimal.Decimal)) and int(item['Service Area Zip Code']) in zip_codes)
            )

            # Check service category match (if service_categories is provided)
            category_match = not service_categories or (
                'Service Category Type' in item and
                any(category in item['Service Category Type'].lower() for category in service_categories)
            )

            # Check city match (if cities is provided)
            city_match = not cities or (
                'City' in item and
                any(city in item['City'].lower() for city in cities)
            )

            # Include item if it matches at least one criterion
            if agency_match or zip_match or category_match or city_match:
                filtered_items.append(item)

        return filtered_items
    except Exception as e:
        print(f"Error performing search: {str(e)}")
        raise e

def build_response(status_code, body):
    """
    Build a standardized API response with custom JSON encoder
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # For CORS support
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
        },
        'body': json.dumps(body, cls=DecimalEncoder)  # Use the custom encoder here
    }