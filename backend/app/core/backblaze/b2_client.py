from functools import lru_cache
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

@lru_cache
def initiate_s3_client(role: str):
    if role == "uploader":
        key_id = os.getenv("B2_UPLOADER_KEY_ID")
        app_key = os.getenv("B2_UPLOADER_APPLICATION_KEY")
    elif role == "viewer":
        key_id = os.getenv("B2_VIEWER_KEY_ID")
        app_key = os.getenv("B2_VIEWER_APPLICATION_KEY")
    else:
        raise ValueError("Invalid role specified. Use 'uploader' or 'viewer'.")

    s3_client = boto3.client(
        "s3",
        endpoint_url=os.getenv("B2_ENDPOINT"),
        aws_access_key_id=key_id,
        aws_secret_access_key=app_key,
        region_name=os.getenv("B2_REGION"),
    )
    
    return s3_client

def upload_video(local_path, target_key):
    """Uses the uploader client to push a video file."""
    client = initiate_s3_client(role="uploader")
    bucket = os.getenv("B2_BUCKET_NAME")
    
    client.upload_file(
        Filename=local_path, 
        Bucket=bucket, 
        Key=target_key,
        ExtraArgs={'ContentType': 'video/mp4'}  # Forces browser streaming instead of raw downloading
    )
    print(f"Uploaded successfully to {target_key}")

def generate_watch_link(video_key, expires_in_seconds=3600):
    """Uses the viewer client to create a temporary streaming link."""
    client = initiate_s3_client(role="viewer")
    bucket = os.getenv("B2_BUCKET_NAME")
    
    url = client.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': bucket, 'Key': video_key},
        ExpiresIn=expires_in_seconds
    )
    return url

if __name__ == "__main__":
    # trainer: Uploading a video file
    upload_video(local_path="./user_video.mp4", target_key="videos/movie.mp4")
    
    # client: Getting a link so a viewer can watch it
    playback_link = generate_watch_link(video_key="videos/movie.mp4", expires_in_seconds=1800)
    print("\nProvide this temporary streaming URL to the client:\n", playback_link)
