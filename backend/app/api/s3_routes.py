from fastapi import APIRouter, HTTPException

from app.services.s3_service import get_s3_data
from app.core.config import settings

router = APIRouter()

@router.get("/reports")
async def get_all_s3_folders():
    try:
        data = get_s3_data(
            bucket_name=settings.S3_BUCKET_NAME,
            json_file="reports/test_report.json",
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
