ROLE_NAME="query-analytics-stream-processor-role-ipnlblc1"
AWS_PROFILE="account-1087"

# Initialize arrays
attached_json='[]'
inline_json='{}'

# 1. Fetch Attached Policies
attached_policy_arns=$(aws iam list-attached-role-policies \
  --role-name "$ROLE_NAME" \
  --profile "$AWS_PROFILE" \
  --query 'AttachedPolicies[*].PolicyArn' \
  --output text)

for policy_arn in $attached_policy_arns; do
  version_id=$(aws iam get-policy \
    --policy-arn "$policy_arn" \
    --profile "$AWS_PROFILE" \
    --query 'Policy.DefaultVersionId' --output text)

  policy_doc=$(aws iam get-policy-version \
    --policy-arn "$policy_arn" \
    --version-id "$version_id" \
    --profile "$AWS_PROFILE" \
    --query 'PolicyVersion.Document' \
    --output json)

  attached_json=$(echo "$attached_json" | jq --argjson doc "$policy_doc" '. + [$doc]')
done

# 2. Fetch Inline Policies
inline_names=$(aws iam list-role-policies \
  --role-name "$ROLE_NAME" \
  --profile "$AWS_PROFILE" \
  --query 'PolicyNames' \
  --output text)

for policy_name in $inline_names; do
  policy_doc=$(aws iam get-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-name "$policy_name" \
    --profile "$AWS_PROFILE" \
    --query 'PolicyDocument' \
    --output json)

  inline_json=$(echo "$inline_json" | jq --arg name "$policy_name" --argjson doc "$policy_doc" '. + {($name): $doc}')
done

# 3. Combine into one JSON object
final_json=$(jq -n \
  --argjson attached "$attached_json" \
  --argjson inline "$inline_json" \
  '{AttachedPolicies: $attached, InlinePolicies: $inline}')

# 4. Output the final JSON
echo "$final_json" > combined_iam_role_policies.json
cat combined_iam_role_policies.json
