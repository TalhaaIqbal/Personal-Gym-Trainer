from fastapi import APIRouter, HTTPException
from services.b2_client import s3_client, BUCKET_NAME
import uuid
from ..schemas.file_schema import UploadRequest

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/presign-upload")
def get_presigned_upload_url(payload: UploadRequest):
    try:
        file_key = f"videos/{uuid.uuid4()}-{payload.filename}"

        presigned_url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": file_key,
                "ContentType": payload.content_type,
            },
            ExpiresIn=3600,  # 1 hour
        )

        return {
            "upload_url": presigned_url,
            "file_key": file_key,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presign-download/{file_key:path}")
def get_presigned_download_url(file_key: str):
    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": file_key},
            ExpiresIn=3600,
        )
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))