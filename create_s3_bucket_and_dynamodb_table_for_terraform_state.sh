#!/bin/bash

# https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-envvars.html
export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}
export BUCKET=${BUCKET:-acme-terraform-state-bucket}
export DYNAMODB_TABLE=${DYNAMODB_TABLE:-acme-terraform-lock-table}

aws s3api create-bucket --bucket ${BUCKET} --region ${AWS_DEFAULT_REGION}
aws s3api put-bucket-versioning --bucket ${BUCKET} --versioning-configuration Status=Enabled

aws dynamodb create-table \
    --table-name ${DYNAMODB_TABLE} \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
