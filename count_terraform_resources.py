#!/usr/bin/env python3

# provide a count of resources managed in Terraform state file(s) in specified S3 bucket prefix.

# based on https://gist.github.com/ericjsilva/583cdfcb6ebfac5c1d7b21c0e3fde966
# removed dependency on pyjq

import boto3
import json
import argparse
import logging
from os import path
from EnvDefault import env_default

version = '0.0.1'

help_indent_formatter = lambda prog: argparse.RawTextHelpFormatter(
  prog,
  max_help_position=4, 
  indent_increment=2,
  width=80
)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    formatter_class=help_indent_formatter,
    description = 'count_terraform_resources.py provides examines Terraform state stored in specified S3 buckets and provides a count of resources.',
  )

  parser.add_argument(
    '--bucket_name_filter_prefix', '-bucket_name_filter_prefix',
    action = env_default('BUCKET_NAME_FILTER_PREFIX'),
    help = 'Naming prefix for buckets where Terraform state is stored.',
    required = True,
  )

  parser.add_argument(
    '--terraform_state_object_key', '-terraform_state_object_key',
    action = env_default('TF_STATE_OBJ_KEY'),
    help = 'Terraform S3 State Storage Key.',
    required = True,
    default = "terraform.tfstate"
  )

  # parser.add_argument(
  #   '--output', '-output',
  #   action = env_default('OUTPUT'),
  #   help = 'Optional: Output format. Default: text.',
  #   choices = ['json', 'text', 'csv'],
  #   required = False,
  #   default = None
  # )

  parser.add_argument(
    '--log_level', '-log_level',
    action = env_default('LOG_LEVEL'),
    help = 'Optional: Log level. Default: INFO.',
    choices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
    required = False
  )

  parser.add_argument(
    '--version', '-version', '-v',
    help='Show version and exit.',
    action='version',
    version=f"{version}"
  )

  args = parser.parse_args()

  # logging
  format = "%(asctime)s: %(message)s"
  date_format = "%Y-%m-%d %H:%M:%S %Z"
  logging.basicConfig(format=format, level=logging.INFO, datefmt=date_format)

  if args.log_level == 'CRITICAL':
    logging.getLogger().setLevel(logging.CRITICAL)
  elif args.log_level == 'ERROR':
    logging.getLogger().setLevel(logging.ERROR)
  elif args.log_level == 'WARNING':
    logging.getLogger().setLevel(logging.WARNING)
  elif args.log_level == 'INFO':
    logging.getLogger().setLevel(logging.INFO)
  elif args.log_level == 'DEBUG':
    logging.getLogger().setLevel(logging.DEBUG)

  logging.debug("Log level set to %s", args.log_level)
  logging.info("Starting %s", path.basename(__file__))

  # config
  try:
    BUCKET_NAME_FILTER_PREFIX = args.bucket_name_filter_prefix
    logging.info("BUCKET_NAME_FILTER_PREFIX: %s", BUCKET_NAME_FILTER_PREFIX)
  except Exception as e:
    logging.error(e)
    logging.error('[error]: Naming prefix for buckets where Terraform state is stored not specified.')
    sys.exit(1)

  try:
    TF_STATE_OBJ_KEY = args.terraform_state_object_key
    logging.info("TF_STATE_OBJ_KEY: %s", TF_STATE_OBJ_KEY)
  except Exception as e:
    logging.error(e)
    logging.error('[error]: Terraform S3 State Storage Key not specified.')
    sys.exit(1)

  s3 = boto3.resource("s3")
  s3_client = boto3.client("s3")

  # Get a list of all buckets
  all_buckets = s3.buckets.all()

  # Define a variable to hold the total resource count
  count = 0
  # Iterate through each bucket
  for bucket in all_buckets:
    if bucket.name.startswith(BUCKET_NAME_FILTER_PREFIX):
      logging.info("Bucket: " + bucket.name)
      state_files = s3_client.list_objects_v2(Bucket=bucket.name)
      # Verify that there are files in the bucket
      if "Contents" in state_files:
        for obj in state_files["Contents"]:
          # Only match on objects that match the Terraform state file name
          if TF_STATE_OBJ_KEY in obj["Key"]:
            logging.info("State file: " + obj["Key"])
            # Get the file contents
            tf_state_file = s3_client.get_object(Bucket=bucket.name, Key=obj["Key"])
            tf_state_file_contents = tf_state_file["Body"].read().decode("utf-8")
            # Parse the file as JSON
            state = json.loads(tf_state_file_contents)["resources"]
            state_resource_count = 0
            for resource in state:
              if resource["mode"] == "managed" and resource["type"] != "null_resource":
                # print (resource)
                logging.debug ("Resource: " + resource["type"] + ":" + resource["name"])
                count += 1
                state_resource_count += 1
            logging.info("Number of resources in this state file: " + str(state_resource_count))

  logging.info("Total number of resources: " + str(count))
