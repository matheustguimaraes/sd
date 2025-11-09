#!/usr/bin/env python3
"""
Simple script to push Terraform state file to S3 using boto3.
Can be run from the backend directory.
"""

import os
import sys
import boto3
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError

# Get project root (assuming this script is in backend/)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TERRAFORM_DIR = PROJECT_ROOT / "terraform"
STATE_FILE = TERRAFORM_DIR / "terraform.tfstate"
STATE_BACKUP = TERRAFORM_DIR / "terraform.tfstate.backup"


def upload_file_to_s3(s3_client, bucket_name, local_file, s3_key, region):
    """Upload a file to S3."""
    try:
        print(f"Uploading {local_file.name} to s3://{bucket_name}/{s3_key}...")
        s3_client.upload_file(
            str(local_file),
            bucket_name,
            s3_key,
            ExtraArgs={
                'ServerSideEncryption': 'AES256',
                'ContentType': 'application/json'
            }
        )
        print(f"✓ Successfully uploaded {local_file.name}")
        return True
    except FileNotFoundError:
        print(f"✗ File not found: {local_file}")
        return False
    except ClientError as e:
        print(f"✗ Error uploading {local_file.name}: {e}")
        return False


def main():
    # Get bucket name from environment or prompt
    bucket_name = os.environ.get('TERRAFORM_STATE_BUCKET')
    if not bucket_name:
        bucket_name = input("Enter S3 bucket name for Terraform state: ").strip()
        if not bucket_name:
            print("Error: Bucket name cannot be empty")
            sys.exit(1)

    # Get AWS region
    region = os.environ.get('AWS_REGION', 'us-east-1')
    
    # Get AWS profile (optional)
    profile = os.environ.get('AWS_PROFILE')

    print(f"Bucket: {bucket_name}")
    print(f"Region: {region}")
    print(f"State file: {STATE_FILE}")

    # Check if state file exists
    if not STATE_FILE.exists():
        print(f"Error: Terraform state file not found: {STATE_FILE}")
        sys.exit(1)

    # Initialize S3 client
    try:
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        s3_client = session.client('s3', region_name=region)
        
        # Test credentials by listing bucket
        try:
            s3_client.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"Error: Bucket '{bucket_name}' does not exist")
                print(f"Create it first with: aws s3 mb s3://{bucket_name} --region {region}")
                sys.exit(1)
            elif error_code == '403':
                print(f"Error: Access denied to bucket '{bucket_name}'")
                sys.exit(1)
            else:
                raise

    except NoCredentialsError:
        print("Error: AWS credentials not found. Configure them using:")
        print("  - AWS CLI: aws configure")
        print("  - Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        print("  - AWS profile: export AWS_PROFILE=your-profile")
        sys.exit(1)
    except Exception as e:
        print(f"Error initializing S3 client: {e}")
        sys.exit(1)

    # Upload main state file
    success = upload_file_to_s3(
        s3_client,
        bucket_name,
        STATE_FILE,
        "terraform.tfstate",
        region
    )

    if not success:
        sys.exit(1)

    # Upload backup state file if it exists
    if STATE_BACKUP.exists():
        upload_file_to_s3(
            s3_client,
            bucket_name,
            STATE_BACKUP,
            "terraform.tfstate.backup",
            region
        )

    print(f"\n✓ State file(s) uploaded successfully to s3://{bucket_name}/")


if __name__ == "__main__":
    main()

