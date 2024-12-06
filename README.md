# count_terraform_resources

[count_terraform_resources.py](count_terraform_resources.py) provides a way to get a count of Terraform resources stored in [S3](https://aws.amazon.com/s3/) buckets in the specified prefix.

## Requirements

[count_terraform_resources.py](count_terraform_resources.py) has been tested on macOS with Python 3.12.6.
You will also need the [boto3](https://pypi.org/project/boto3/) package. Version `1.35.76` was used in our testing.

```
python3 -m venv .venv
source .venv/bin/activate
pip3 install boto3
```

## Running count_terraform_resources.py

```
usage: count_terraform_resources.py [-h] --bucket_name_filter_prefix
                                    BUCKET_NAME_FILTER_PREFIX
                                    [--terraform_state_object_key TERRAFORM_STATE_OBJECT_KEY]
                                    [--log_level {CRITICAL,ERROR,WARNING,INFO,DEBUG}]
                                    [--version]

count_terraform_resources.py provides examines Terraform state stored in specified S3 buckets and provides a count of resources.

options:
  -h, --help
    show this help message and exit
  --bucket_name_filter_prefix BUCKET_NAME_FILTER_PREFIX, -bucket_name_filter_prefix BUCKET_NAME_FILTER_PREFIX
    Naming prefix for buckets where Terraform state is stored.
  --terraform_state_object_key TERRAFORM_STATE_OBJECT_KEY, -terraform_state_object_key TERRAFORM_STATE_OBJECT_KEY
    Terraform S3 State Storage Key.
  --log_level {CRITICAL,ERROR,WARNING,INFO,DEBUG}, -log_level {CRITICAL,ERROR,WARNING,INFO,DEBUG}
    Optional: Log level. Default: INFO.
  --version, -version, -v
    Show version and exit.
```

### Example run:

```
❯ ./count_terraform_resources.py --bucket_name_filter_prefix acme-terraform-state
2024-12-06 14:48:49 EST: Starting count_terraform_resources.py
2024-12-06 14:48:49 EST: BUCKET_NAME_FILTER_PREFIX: acme-terraform-state
2024-12-06 14:48:49 EST: TF_STATE_OBJ_KEY: terraform.tfstate
2024-12-06 14:48:49 EST: Found credentials in environment variables.
2024-12-06 14:48:49 EST: Bucket: acme-terraform-state-bucket
2024-12-06 14:48:49 EST: State file: acme-account-01x/app-a/dev/us-east-1/terraform.tfstate
2024-12-06 14:48:49 EST: Number of resources in this state file: 12
2024-12-06 14:48:49 EST: State file: acme-account-01x/app-b/dev/us-east-1/terraform.tfstate
2024-12-06 14:48:50 EST: Number of resources in this state file: 12
2024-12-06 14:48:50 EST: Total number of resources: 24
```

Run with the `--log-level DEBUG` flag to see detailed output about the resources managed in your state file and other information.

## Testing

Additionally, we provide [create_s3_bucket_and_dynamodb_table_for_terraform_state.sh](create_s3_bucket_and_dynamodb_table_for_terraform_state.sh) to create and S3 bucket and DynamoDB table for managing Terraform state files. You may use this state file to create an S3 bucket and DynamoDB table, and then reference them in your Terraform configuration in order to store state files in S3 for the purposes of testing.

With the defaults in the script, you'll configure your Terraform state storage as follows:
```
terraform {
  backend "s3" {
    bucket         = "acme-terraform-state-bucket"
    key            = "acme-account-01x/app-a/dev/us-east-1/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "acme-terraform-lock-table"
  }
}
```

Please see [https://developer.hashicorp.com/terraform/language/backend/s3](https://developer.hashicorp.com/terraform/language/backend/s3) for additional information.

---
