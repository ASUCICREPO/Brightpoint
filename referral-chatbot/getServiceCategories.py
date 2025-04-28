import boto3

# Initialize AWS clients for Lambda environment
def get_boto_clients():
    # Use default credentials in Lambda
    session = boto3.Session()
    return {
        "dynamodb": session.resource("dynamodb", region_name="us-east-1")
    }

# Get clients
clients = get_boto_clients()
dynamodb = clients["dynamodb"]
table = dynamodb.Table("referral_data")
unique_categories = set()

def getUniqueCategories():
    try:
        response = table.scan()
        while True:
            for item in response.get('Items', []):
                # Look for Service Category Type including with ZWNBSP character
                service_category = item.get("Service Category Type") or item.get("\ufeffService Category Type")
                if service_category:
                    unique_categories.add(service_category.strip())
            if 'LastEvaluatedKey' in response:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            else:
                break
        # Return as a sorted list for consistent ordering
        return sorted(list(unique_categories))
    except Exception as e:
        print(f"Error getting unique categories: {str(e)}")
        # Return a default list of common categories if we can't scan DynamoDB
        return [
            "Food Pantry",
            "Housing",
            "Homeless Services",
            "Medical Services",
            "Mental Health Services",
            "Child Care",
            "Children Services",
            "Youth Programs",
            "Education Services",
            "Employment Services",
            "Financial Assistance",
            "Legal Assistance",
            "Transportation",
            "Utility Assistance",
            "Crisis Assistance",
            "Domestic Violence Services",
            "Sexual Assault Services",
            "Substance Use & Addiction Support",  # Updated from "Substance Abuse Services"
            "Clothing & Household Items",
            "WIC (Women, Infants, and Children)",
            "Food Assistance",
            "SNAP",
            "Rental Assistance",
            "Healthcare",
            "Dental",
            "Hospitals",
            "Community Services",
            "Family Services",
            "Adult Education",
            "Support Groups",
            "Medical Assistance",
            "Legal Services",
            "Child Care Assistance"
        ]

def get_services_by_category(service_category):
    try:
        # Try with and without ZWNBSP character since we've seen inconsistencies
        response = table.scan(
            FilterExpression="#sc = :category OR #sc2 = :category",
            ExpressionAttributeNames={
                "#sc": "Service Category Type",
                "#sc2": "\ufeffService Category Type"
            },
            ExpressionAttributeValues={":category": service_category}
        )

        if "Items" not in response or not response["Items"]:
            print(f"No results found for category: {service_category}")
            return []

        # Extract relevant service information
        services = [
            {
                "referral_id": item.get("referral_id", ""),
                "service_area_zip_code": item.get("Service Area Zip Code", ""),  # Updated from "zipcode"
                "organization": item.get("\ufeffOrganization", item.get("Organization", "")),  # Updated from "agency"
                "contact": item.get("Phone", ""),
                "eligibility": item.get("Eligibility Requirements", ""),
                "service_availability": item.get("Service Availability", ""),
            }
            for item in response.get("Items", [])
        ]

        print(f"Found {len(services)} services for category: {service_category}")
        return services
    except Exception as e:
        print(f"Error querying DynamoDB: {str(e)}")
        return []