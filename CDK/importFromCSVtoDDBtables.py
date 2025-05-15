import boto3
import csv
import uuid
from decimal import Decimal
import os

def import_csv_to_dynamodb(csv_file_path, table_name, region='us-east-1', profile_name='default'):
    """
    Import data from a CSV file to a DynamoDB table.

    Args:
        csv_file_path (str): Path to the CSV file to import
        table_name (str): Name of the DynamoDB table
        region (str): AWS region name (default: 'us-east-1')
        profile_name (str): AWS profile name (default: 'default')
    """
    # Create a boto3 session with the specified profile
    session = boto3.Session(profile_name="Brightpoint")

    # Initialize DynamoDB resource using the session
    dynamodb = session.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)

    # Verify the CSV file exists
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file '{csv_file_path}' not found")
        return

    # Read the CSV file
    with open(csv_file_path, 'r') as file:
        csv_reader = csv.DictReader(file)

        # Track imported items
        item_count = 0
        error_count = 0

        # Process each row
        for row in csv_reader:
            # Create a clean item dictionary
            item = {}

            for key, value in row.items():
                # Remove any non-printable characters and strip spaces
                clean_key = ''.join(char for char in key if char.isprintable()).strip()

                # Fix specifically for "Organization" field
                if "Organization" in clean_key:
                    clean_key = "Organization"  # Force correct key name

                # Skip columns with no header name
                if not clean_key or clean_key == '':
                    continue

                if 'referral_id' not in item:
                    item['referral_id'] = str(uuid.uuid4())

                if clean_key.lower() == 'zipcode' or clean_key.lower() == 'zip_code' or clean_key.lower() == 'zip':
                    if value is None or value.strip() == '':
                        # Use a default value for empty zipcodes
                        item[clean_key] = "00000"
                    else:
                        item[clean_key] = value
                # Handle all other fields
                else:
                    # Skip empty values for other fields
                    if value is None or value.strip() == '':
                        continue

                    # Try to convert to Decimal if it's a number
                    try:
                        float_val = float(value)
                        item[clean_key] = Decimal(str(float_val))
                    except (ValueError, TypeError):
                        # Keep as string if not a number
                        item[clean_key] = value

            # Add a unique ID if not present
            if 'id' not in item:
                item['id'] = str(uuid.uuid4())

            try:
                # Insert into DynamoDB
                table.put_item(Item=item)
                item_count += 1

                # Print progress every 10 items
                if item_count % 10 == 0:
                    print(f"Progress: {item_count} items imported...")
            except Exception as e:
                error_count += 1
                print(f"Error importing item {item.get('id', 'unknown')}: {str(e)}")
                print(f"Problematic item: {item}")

        print(f"Import complete: {item_count} items imported successfully, {error_count} errors")

if __name__ == "__main__":
    # Define your variables here
    csv_file_path = "../ProviderReferralData.csv"
    table_name = "referral_data-dev"
    region = "us-east-1"
    profile_name = "default"

    # Run the import
    import_csv_to_dynamodb(csv_file_path, table_name, region, profile_name)