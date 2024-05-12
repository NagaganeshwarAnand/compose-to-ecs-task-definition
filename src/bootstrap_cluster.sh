#!/usr/bin/env bash
set -euo pipefail

# ===== Config (override via env vars if you like) =====
CLUSTER="${CLUSTER:-demo-ecs-cluster}"
SERVICE="${SERVICE:-demo-ecs-service}"
DESIRED_COUNT="${DESIRED_COUNT:-1}"

# Resolve region for logs (CLI-configured or env; default to us-east-1 if empty)
REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-$(aws configure get region || true)}}"
REGION="${REGION:-us-east-1}"

echo "Using region: $REGION"

# ===== Discover default networking =====
VPC_ID="$(aws ec2 describe-vpcs \
  --filters Name=isDefault,Values=true \
  --query 'Vpcs[0].VpcId' --output text)"

if [[ -z "$VPC_ID" || "$VPC_ID" == "None" ]]; then
  echo "ERROR: No default VPC found in region $REGION." >&2
  exit 1
fi
echo "Default VPC: $VPC_ID"

# Default subnets in that VPC (fallback to any subnets in the VPC)
SUBNET_IDS_TXT="$(aws ec2 describe-subnets \
  --filters Name=vpc-id,Values="$VPC_ID" Name=default-for-az,Values=true \
  --query 'Subnets[].SubnetId' --output text || true)"

if [[ -z "$SUBNET_IDS_TXT" ]]; then
  SUBNET_IDS_TXT="$(aws ec2 describe-subnets \
    --filters Name=vpc-id,Values="$VPC_ID" \
    --query 'Subnets[].SubnetId' --output text)"
fi

if [[ -z "$SUBNET_IDS_TXT" ]]; then
  echo "ERROR: Could not find any subnets in VPC $VPC_ID." >&2
  exit 1
fi

SUBNETS_CSV="$(echo "$SUBNET_IDS_TXT" | tr '\t' ' ' | tr ' ' ',')"
echo "Subnets: $(echo "$SUBNET_IDS_TXT" | tr '\t' ' ')"

# Default security group in that VPC
SG_ID="$(aws ec2 describe-security-groups \
  --filters Name=vpc-id,Values="$VPC_ID" Name=group-name,Values=default \
  --query 'SecurityGroups[0].GroupId' --output text)"

if [[ -z "$SG_ID" || "$SG_ID" == "None" ]]; then
  echo "ERROR: Could not find the default security group in VPC $VPC_ID." >&2
  exit 1
fi
echo "Default Security Group: $SG_ID"

# ===== Create CW Logs group if needed (no-op if exists) =====
# aws logs create-log-group --log-group-name "$LOG_GROUP" 2>/dev/null || true
# echo "Log group ready: $LOG_GROUP"

# ===== Create (or reuse) ECS cluster =====
if aws ecs describe-clusters --clusters "$CLUSTER" \
  --query 'clusters[?status==`ACTIVE`].clusterName' --output text | grep -qx "$CLUSTER"; then
  echo "Cluster exists: $CLUSTER"
else
  aws ecs create-cluster --cluster-name "$CLUSTER" >/dev/null
  echo "Cluster created: $CLUSTER"
fi

# ===== Write task definition JSON (EC2 + awsvpc) =====
TASKDEF_FILE="/Users/naanand/sandboxes/git_repos/compose-to-ecs-task-definition/src/tests/output/nginx_task_definition.json"

# ===== Register task definition =====
TASKDEF_ARN="$(aws ecs register-task-definition \
  --cli-input-json file://"$TASKDEF_FILE" \
  --query 'taskDefinition.taskDefinitionArn' --output text)"
echo "Registered task definition: $TASKDEF_ARN"

# ===== Create or update the Service (EC2 launch type) =====
if aws ecs describe-services --cluster "$CLUSTER" --services "$SERVICE" \
  --query 'services[0].status' --output text 2>/dev/null | grep -q 'ACTIVE'; then
  aws ecs update-service \
    --cluster "$CLUSTER" \
    --service "$SERVICE" \
    --task-definition "$TASKDEF_ARN" >/dev/null
  ACTION="Updated"
else
  aws ecs create-service \
    --cluster "$CLUSTER" \
    --service-name "$SERVICE" \
    --task-definition "$TASKDEF_ARN" \
    --launch-type EC2 \
    --desired-count "$DESIRED_COUNT"
  # --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS_CSV],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" >/dev/null
  ACTION="Created"
fi

# ===== Capacity check (EC2 container instances required) =====
CI_COUNT="$(aws ecs list-container-instances --cluster "$CLUSTER" --status ACTIVE \
  --query 'length(containerInstanceArns)' --output text)"
if [[ "$CI_COUNT" == "0" ]]; then
  echo "WARNING: No EC2 container instances are registered in cluster '$CLUSTER'."
  echo "         The service will stay PENDING until an ECS-optimized EC2 instance joins the cluster."
fi

echo
echo "$ACTION service '$SERVICE' in cluster '$CLUSTER'."
echo "VPC: $VPC_ID"
echo "Security Group: $SG_ID"
echo "Subnets: $(echo "$SUBNET_IDS_TXT" | tr '\t' ' ')"
# echo "Log group: $LOG_GROUP"
