#!/bin/bash
# Launch an EC2 GPU instance for JSL VLM model serving.
#
# Usage: bash 0_deploy_ec2.sh <key-pair-name> [instance-type]
#
# Instance types:
#   g5.xlarge    — 1x A10G 24GB  (~$1.01/hr) — single model up to 8B
#   g6e.2xlarge  — 1x L40S 48GB  (~$1.86/hr) — multiple models or 32B FP8 (default)
#   g5.12xlarge  — 4x A10G 96GB  (~$5.67/hr) — all models, tensor parallel
set -e

KEY_NAME="${1:?Usage: bash 0_deploy_ec2.sh <key-pair-name> [instance-type]}"
INSTANCE_TYPE="${2:-g6e.2xlarge}"
REGION="us-east-1"
AMI="ami-0669ac5db8b1292fe"  # Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 22.04)
SG_NAME="jsl-vlm-server-sg"

echo "Instance type: ${INSTANCE_TYPE}"
echo "Key pair: ${KEY_NAME}"
echo "Region: ${REGION}"
echo ""

# Security group (reuse if exists)
SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=${SG_NAME}" \
    --query 'SecurityGroups[0].GroupId' --output text --region "$REGION" 2>/dev/null)

if [ "$SG_ID" = "None" ] || [ -z "$SG_ID" ]; then
    SG_ID=$(aws ec2 create-security-group --group-name "$SG_NAME" \
        --description "JSL VLM Server — SSH only" --query 'GroupId' --output text --region "$REGION")
    aws ec2 authorize-security-group-ingress --group-id "$SG_ID" \
        --protocol tcp --port 22 --cidr 0.0.0.0/0 --region "$REGION" > /dev/null
    echo "Created security group: ${SG_ID} (port 22 open)"
else
    echo "Using existing security group: ${SG_ID}"
fi

# Launch instance
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id "$AMI" --instance-type "$INSTANCE_TYPE" --key-name "$KEY_NAME" \
    --security-group-ids "$SG_ID" \
    --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":200,"VolumeType":"gp3"}}]' \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=jsl-vlm-server}]" \
    --query 'Instances[0].InstanceId' --output text --region "$REGION")
echo "Launched: ${INSTANCE_ID} — waiting for running state..."

aws ec2 wait instance-running --instance-ids "$INSTANCE_ID" --region "$REGION"
IP=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text --region "$REGION")

echo ""
echo "=========================================="
echo "Instance: ${INSTANCE_ID}"
echo "IP:       ${IP}"
echo "Type:     ${INSTANCE_TYPE}"
echo "=========================================="
echo ""
echo "SSH:    ssh -i ~/.ssh/${KEY_NAME}.pem ubuntu@${IP}"
echo "Tunnel: ssh -N -L 9460:localhost:9460 -L 9461:localhost:9461 -i ~/.ssh/${KEY_NAME}.pem ubuntu@${IP}"
echo ""
echo "Next steps on the instance:"
echo "  1. Copy .env, docker-compose.yaml, serve.py to ~/jsl-vlm/"
echo "  2. docker compose up -d"
echo "  3. curl http://localhost:9461/v1/models"
echo ""
echo "Stop when done: aws ec2 stop-instances --instance-ids ${INSTANCE_ID} --region ${REGION}"
