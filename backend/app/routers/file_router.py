from fastapi import APIRouter, HTTPException, Depends
import uuid
import os
from ..core.backblaze.b2_client import initiate_s3_client
from ..core.middleware import get_current_trainer, get_current_user
from ..schemas.file_schema import UploadRequest

router = APIRouter(prefix="/videos", tags=["videos"])

BUCKET_NAME = os.getenv("B2_BUCKET_NAME")


@router.post("/presign-upload", dependencies=[Depends(get_current_trainer)])
def get_presigned_upload_url(payload: UploadRequest):
    try:
        file_key = f"videos/{uuid.uuid4()}-{payload.filename}"

        client = initiate_s3_client(role="uploader")
        presigned_url = client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": file_key,
                "ContentType": payload.content_type,
            },
            ExpiresIn=3600,
        )

        return {
            "upload_url": presigned_url,
            "file_key": file_key,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presign-download/{file_key:path}", dependencies=[Depends(get_current_user)])
def get_presigned_download_url(file_key: str):
    try:
        client = initiate_s3_client(role="viewer")
        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": file_key},
            ExpiresIn=3600,
        )
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))