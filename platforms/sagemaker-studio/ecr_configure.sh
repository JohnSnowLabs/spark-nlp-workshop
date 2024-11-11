# PLease, introduce your ECR configuration here as described in the instructions
REGION=
ACCOUNT_ID=
IMAGE_NAME=
REPO_NAME=
ROLE_ARN=

aws --region ${REGION} ecr create-repository --repository-name $REPO_NAME
aws --region ${REGION} ecr get-login-password | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}
docker build . -t ${IMAGE_NAME} -t ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}:${IMAGE_NAME}
docker push ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}:${IMAGE_NAME}

aws --region ${REGION} sagemaker create-image --image-name ${IMAGE_NAME} --role-arn ${ROLE_ARN}
aws --region ${REGION} sagemaker create-image-version --image-name ${IMAGE_NAME} --base-image "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}:${IMAGE_NAME}"
aws --region ${REGION} sagemaker describe-image-version --image-name ${IMAGE_NAME}

aws --region ${REGION} sagemaker create-app-image-config --cli-input-json file://app-image-config-input.json