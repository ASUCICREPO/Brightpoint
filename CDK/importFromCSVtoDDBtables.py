#!/usr/bin/env python3

import boto3
import csv
import uuid
import subprocess
import sys
import os
import json
from pathlib import Path
from decimal import Decimal
from botocore.exceptions import ProfileNotFound, ClientError
from boto3.session import Session

def read_cdk_config():
    """Read CDK configuration file to get profile and region"""
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent
    config_file = project_root / "config" / "cdk-config.json"

    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            profile = config.get('profile', '')
            region = config.get('region', 'us-east-1')

            # Handle null values similar to bash script
            if profile in [None, 'null', '']:
                profile = None

            print(f"📖 Reading CDK configuration...")
            print(f"✅ Found profile: {profile or '(default)'}")
            print(f"✅ Found region: {region}")

            return profile, region

        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️  Error reading CDK config file: {e}")
            print("💡 Using default profile and region")
            return None, 'us-east-1'
    else:
        print(f"⚠️  CDK config file not found: {config_file}")
        print("💡 Using default profile and region")
        return None, 'us-east-1'

def check_specific_profile(profile_name=None):
    """Check if a specific profile exists and is valid"""
    try:
        # Create session with or without profile
        if profile_name:
            # Explicitly create session with ONLY the profile - no instance metadata
            session = Session(profile_name=profile_name)
            profile_text = f"profile '{profile_name}'"
        else:
            # Use default profile/credentials
            session = Session()
            profile_text = "default profile"

        sts = session.client('sts')
        identity = sts.get_caller_identity()
        print(f"Successfully connected using {profile_text}")
        print(f"AWS Account: {identity['Account']}")
        return True, session
    except (ProfileNotFound, ClientError) as e:
        print(f"Error with {profile_text}: {str(e)}")
        return False, None

def configure_aws_profile(profile_name=None):
    """Configure AWS profile with aws configure"""
    if profile_name:
        print(f"Setting up AWS profile '{profile_name}'...")
        try:
            subprocess.run(['aws', 'configure', '--profile', profile_name], check=True)
            print(f"Profile '{profile_name}' configured successfully.")

            # Verify the newly configured profile
            valid, session = check_specific_profile(profile_name)
            if valid:
                return session
            else:
                print("Profile was created but validation failed. Please check your credentials.")
                sys.exit(1)
        except subprocess.CalledProcessError:
            print(f"Error configuring AWS profile '{profile_name}'.")
            sys.exit(1)
    else:
        print("Setting up default AWS profile...")
        try:
            subprocess.run(['aws', 'configure'], check=True)
            print("Default profile configured successfully.")

            # Verify the newly configured profile
            valid, session = check_specific_profile(None)
            if valid:
                return session
            else:
                print("Profile was created but validation failed. Please check your credentials.")
                sys.exit(1)
        except subprocess.CalledProcessError:
            print("Error configuring default AWS profile.")
            sys.exit(1)

def list_available_tables(session, region):
    """List available DynamoDB tables to help with troubleshooting"""
    try:
        dynamodb_client = session.client('dynamodb', region_name=region)
        tables = dynamodb_client.list_tables()
        if 'TableNames' in tables and tables['TableNames']:
            print("Available DynamoDB tables:")
            for table in tables['TableNames']:
                print(f"  - {table}")
        else:
            print("No DynamoDB tables found in this account/region")
    except Exception as e:
        print(f"Error listing tables: {str(e)}")

def import_csv_to_dynamodb(csv_file_path, table_name, region='us-east-1', profile_name=None):
    """Import data from a CSV file to a DynamoDB table."""

    # First check if the specific profile exists and is valid
    valid, session = check_specific_profile(profile_name)

    # If not valid, configure it
    if not valid:
        session = configure_aws_profile(profile_name)

    # List available tables for troubleshooting
    list_available_tables(session, region)

    # Check if the specific table exists
    dynamodb_client = session.client('dynamodb', region_name=region)
    try:
        table_response = dynamodb_client.describe_table(TableName=table_name)
        print(f"Found table '{table_name}' in region {region}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"ERROR: Table '{table_name}' does not exist in account/region")
            print("Please create the table first or check the table name and region")
            return
        else:
            raise e

    # Now use the resource API for importing
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
                # Skip None keys
                if key is None:
                    continue

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
    # Read configuration from CDK config file
    profile_name, region = read_cdk_config()

    # Define your variables here
    csv_file_path = "../ProviderReferralData.csv"
    table_name = "referral_data-dev"

    print("")
    print("📋 Configuration Summary:")
    print("========================")
    print(f"Profile: {profile_name or '(default)'}")
    print(f"Region: {region}")
    print(f"Table: {table_name}")
    print(f"CSV File: {csv_file_path}")
    print("")

    # Run the import
    import_csv_to_dynamodb(csv_file_path, table_name, region, profile_name)