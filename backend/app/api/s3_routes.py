from fastapi import APIRouter, HTTPException

from app.services.s3_service import get_latest_player_report
from app.core.config import settings

router = APIRouter()

@router.get("/reports/latest")
async def get_latest_report(player: str, team: str):
    try:
        report = get_latest_player_report(
            bucket_name=settings.S3_BUCKET_NAME,
            team=team,
            player_name=player
        )

        if not report:
            raise HTTPException(status_code=404, detail="No reports found for this player/team")

        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
