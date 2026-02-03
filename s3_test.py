"""
S3 Connectivity Test Script
Verifies connection to the 'narrated' S3 bucket using provided credentials.

Usage:
    Set environment variables before running:
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY
    - AWS_REGION (optional, defaults to us-east-1)
    - S3_ENDPOINT_URL (optional, for S3-compatible storage)
    
    python s3_test.py
"""

import os
import sys
from datetime import datetime

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# Configuration from environment variables
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")  # Optional for S3-compatible storage
BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "narrated")


def get_s3_client():
    """Create and return an S3 client with configured credentials."""
    config = {
        "aws_access_key_id": AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
        "region_name": AWS_REGION,
    }
    
    if S3_ENDPOINT_URL:
        config["endpoint_url"] = S3_ENDPOINT_URL
    
    return boto3.client("s3", **config)


def test_connection():
    """Test basic S3 connectivity."""
    print("=" * 60)
    print("S3 Connectivity Test")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Target Bucket: {BUCKET_NAME}")
    print(f"Region: {AWS_REGION}")
    if S3_ENDPOINT_URL:
        print(f"Endpoint URL: {S3_ENDPOINT_URL}")
    print("-" * 60)
    
    # Check credentials
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        print("❌ ERROR: AWS credentials not set!")
        print("   Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        return False
    
    print("✓ Credentials found in environment")
    
    try:
        s3 = get_s3_client()
        
        # Test 1: List buckets (verify credentials work)
        print("\n[Test 1] Verifying credentials...")
        buckets = s3.list_buckets()
        print(f"✓ Credentials valid. Found {len(buckets.get('Buckets', []))} buckets")
        
        # Test 2: Check if target bucket exists
        print(f"\n[Test 2] Checking bucket '{BUCKET_NAME}'...")
        try:
            s3.head_bucket(Bucket=BUCKET_NAME)
            print(f"✓ Bucket '{BUCKET_NAME}' exists and is accessible")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"⚠ Bucket '{BUCKET_NAME}' does not exist")
                print("  Attempting to create bucket...")
                try:
                    if AWS_REGION == "us-east-1":
                        s3.create_bucket(Bucket=BUCKET_NAME)
                    else:
                        s3.create_bucket(
                            Bucket=BUCKET_NAME,
                            CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
                        )
                    print(f"✓ Bucket '{BUCKET_NAME}' created successfully")
                except Exception as create_error:
                    print(f"❌ Failed to create bucket: {create_error}")
                    return False
            elif error_code == '403':
                print(f"❌ Access denied to bucket '{BUCKET_NAME}'")
                return False
            else:
                print(f"❌ Error checking bucket: {e}")
                return False
        
        # Test 3: List objects in bucket
        print(f"\n[Test 3] Listing objects in '{BUCKET_NAME}'...")
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, MaxKeys=10)
        object_count = response.get('KeyCount', 0)
        print(f"✓ Listed objects. Found {object_count} objects (showing max 10)")
        
        if 'Contents' in response:
            for obj in response['Contents'][:5]:
                print(f"   - {obj['Key']} ({obj['Size']} bytes)")
        
        # Test 4: Write test (optional)
        print(f"\n[Test 4] Testing write access...")
        test_key = f"_test/connectivity_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        test_content = f"Connectivity test at {datetime.now().isoformat()}"
        
        try:
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=test_key,
                Body=test_content.encode('utf-8'),
                ContentType='text/plain'
            )
            print(f"✓ Successfully wrote test file: {test_key}")
            
            # Clean up test file
            s3.delete_object(Bucket=BUCKET_NAME, Key=test_key)
            print(f"✓ Cleaned up test file")
        except ClientError as e:
            print(f"⚠ Write test failed: {e}")
            print("  (This may be expected if bucket is read-only)")
        
        print("\n" + "=" * 60)
        print("✅ S3 CONNECTIVITY TEST PASSED")
        print("=" * 60)
        return True
        
    except NoCredentialsError:
        print("❌ ERROR: No valid credentials found")
        return False
    except ClientError as e:
        print(f"❌ ERROR: {e}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    success = test_connection()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
