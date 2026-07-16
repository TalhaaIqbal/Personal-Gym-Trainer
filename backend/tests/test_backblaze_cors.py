"""
Test Backblaze B2 CORS Policy
This script tests uploading a video to Backblaze B2 and verifies CORS configuration
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.backblaze.b2_client import generate_watch_link, initiate_s3_client, upload_video

load_dotenv()

def test_video_upload():
    """Test uploading a video file to Backblaze B2"""
    print("=" * 50)
    print("Testing Video Upload to Backblaze B2")
    print("=" * 50)
    
    # Create a test video file (small MP4 for testing)
    test_video_path = "test_video.mp4"
    test_video_key = "test_videos/cors_test_video.mp4"
    
    # Create a minimal valid MP4 file for testing
    # This is a minimal MP4 header (not a real video, but valid for upload testing)
    minimal_mp4 = b'\x00\x00\x00\x20ftypmp42\x00\x00\x00\x00mp42isom'
    with open(test_video_path, 'wb') as f:
        f.write(minimal_mp4)
    
    try:
        print(f"Uploading test video to B2 bucket...")
        upload_video(local_path=test_video_path, target_key=test_video_key)
        print(f"✓ Upload successful: {test_video_key}")
        
        # Generate watch link
        print(f"\nGenerating presigned URL...")
        watch_url = generate_watch_link(video_key=test_video_key, expires_in_seconds=3600)
        print(f"✓ Watch URL generated: {watch_url}")
        
        return test_video_key, watch_url
        
    except Exception as e:
        print(f"✗ Upload failed: {e}")
        return None, None
    finally:
        # Clean up test file
        if os.path.exists(test_video_path):
            os.remove(test_video_path)

def test_cors_policy(watch_url):
    """Test CORS policy by making requests from different origins"""
    print("\n" + "=" * 50)
    print("Testing CORS Policy")
    print("=" * 50)
    
    if not watch_url:
        print("✗ No watch URL available for CORS testing")
        return
    
    # Test 1: Simple GET request
    print("\n1. Testing simple GET request...")
    try:
        response = requests.get(watch_url)
        print(f"   Status: {response.status_code}")
        print(f"   CORS Headers: {dict(response.headers)}")
        print(f"✓ GET request successful")
    except Exception as e:
        print(f"✗ GET request failed: {e}")
    
    # Test 2: OPTIONS request (preflight)
    print("\n2. Testing OPTIONS request (CORS preflight)...")
    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options(watch_url, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   CORS Headers: {dict(response.headers)}")
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Max-Age': response.headers.get('Access-Control-Max-Age')
        }
        print(f"   CORS Configuration: {cors_headers}")
        
        if response.headers.get('Access-Control-Allow-Origin'):
            print(f"✓ CORS is configured")
        else:
            print(f"✗ CORS not properly configured")
            
    except Exception as e:
        print(f"✗ OPTIONS request failed: {e}")
    
    # Test 3: Request with different origin
    print("\n3. Testing with different origin (http://example.com)...")
    try:
        headers = {'Origin': 'http://example.com'}
        response = requests.get(watch_url, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin')}")
        
        allowed_origin = response.headers.get('Access-Control-Allow-Origin')
        if allowed_origin == '*' or allowed_origin == 'http://example.com':
            print(f"✓ Origin allowed")
        else:
            print(f"✗ Origin not allowed or restricted")
    except Exception as e:
        print(f"✗ Request with custom origin failed: {e}")

def test_bucket_cors_config():
    """Test and display current B2 bucket CORS configuration"""
    print("\n" + "=" * 50)
    print("Testing B2 Bucket CORS Configuration")
    print("=" * 50)
    
    try:
        client = initiate_s3_client(role="uploader")
        bucket = os.getenv("B2_BUCKET_NAME")
        
        # Get bucket CORS configuration
        try:
            cors_config = client.get_bucket_cors(Bucket=bucket)
            print(f"Current CORS Configuration:")
            print(f"CORS Rules: {cors_config.get('CORSRules', [])}")
            
            for i, rule in enumerate(cors_config.get('CORSRules', []), 1):
                print(f"\nRule {i}:")
                print(f"  Allowed Origins: {rule.get('AllowedOrigins')}")
                print(f"  Allowed Methods: {rule.get('AllowedMethods')}")
                print(f"  Allowed Headers: {rule.get('AllowedHeaders')}")
                print(f"  Expose Headers: {rule.get('ExposeHeaders')}")
                print(f"  Max Age: {rule.get('MaxAgeSeconds')}")
                
        except client.exceptions.ClientError as e:
            if 'NoSuchCORSConfiguration' in str(e):
                print("✗ No CORS configuration found on bucket")
                print("   You need to configure CORS in your B2 bucket settings")
            else:
                raise
                
    except Exception as e:
        print(f"✗ Error fetching CORS configuration: {e}")

def cleanup_test_file(video_key):
    """Clean up test file from B2 bucket"""
    print("\n" + "=" * 50)
    print("Cleaning Up Test File")
    print("=" * 50)
    
    try:
        client = initiate_s3_client(role="uploader")
        bucket = os.getenv("B2_BUCKET_NAME")
        
        client.delete_object(Bucket=bucket, Key=video_key)
        print(f"✓ Test file deleted: {video_key}")
        
    except Exception as e:
        print(f"✗ Failed to delete test file: {e}")

if __name__ == "__main__":
    print("Backblaze B2 CORS Policy Test")
    print("=" * 50)
    
    # Test 1: Upload video
    video_key, watch_url = test_video_upload()
    
    if video_key and watch_url:
        # Test 2: Check CORS configuration
        test_bucket_cors_config()
        
        # Test 3: Test CORS policy
        test_cors_policy(watch_url)
        
        # Test 4: Cleanup
        cleanup_test_file(video_key)
    else:
        print("\n✗ Upload failed, skipping CORS tests")
    
    print("\n" + "=" * 50)
    print("Test Complete")
    print("=" * 50)
