from fastapi import APIRouter, HTTPException, Depends, UploadFile
import uuid
import os
from ..core.backblaze.b2_client import initiate_s3_client
from ..core.middleware import get_current_trainer, get_current_user
from ..schemas.file_schema import UploadRequest

router = APIRouter(prefix="/videos", tags=["videos"])

BUCKET_NAME = os.getenv("B2_BUCKET_NAME")


@router.post("/workout-video/upload", dependencies=[Depends(get_current_trainer)])
async def upload_workout_video(file: UploadFile):
    try:
        file_key = f"workout-videos/{uuid.uuid4()}-{file.filename}"
        print(f"Uploading video: {file_key}")

        client = initiate_s3_client(role="uploader")

        # Stream upload to avoid loading entire file into memory
        client.upload_fileobj(
            file.file,
            BUCKET_NAME,
            file_key,
            ExtraArgs={'ContentType': file.content_type or 'video/mp4'}
        )

        print(f"Successfully uploaded: {file_key}")

        return {
            "video_key": file_key,
            "message": "Video uploaded successfully"
        }
    except Exception as e:
        print(f"Error uploading video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workout-video/{video_key:path}", dependencies=[Depends(get_current_user)])
def get_workout_video_watch_url(video_key: str):
    try:
        client = initiate_s3_client(role="viewer")
        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": video_key},
            ExpiresIn=3600,
        )
        print("url: ", url)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))