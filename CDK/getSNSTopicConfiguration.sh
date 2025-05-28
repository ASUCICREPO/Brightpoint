#!/bin/bash

AWS_PROFILE="account-1087"
REGION="us-east-1"

echo "Fetching SNS topics for account $AWS_PROFILE in region $REGION"
echo "==========================================="

# Get all topics
topics=$(AWS_PROFILE=$AWS_PROFILE aws sns list-topics --region $REGION --query 'Topics[].TopicArn' --output text)

for topic_arn in $topics; do
    echo ""
    echo "Topic: $topic_arn"
    echo "---"
    
    # Get topic name from ARN
    topic_name=$(echo $topic_arn | awk -F: '{print $NF}')
    
    # Get topic attributes
    echo "Attributes:"
    AWS_PROFILE=$AWS_PROFILE aws sns get-topic-attributes \
        --topic-arn $topic_arn \
        --region $REGION \
        --output json
    
    # Get subscriptions
    echo ""
    echo "Subscriptions:"
    AWS_PROFILE=$AWS_PROFILE aws sns list-subscriptions-by-topic \
        --topic-arn $topic_arn \
        --region $REGION \
        --output json
    
    echo "==========================================="
done