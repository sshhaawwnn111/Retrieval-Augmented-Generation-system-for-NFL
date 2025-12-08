import boto3
import os
import json
from app.core.config import settings
import re
from datetime import datetime

def player_to_slug(name: str) -> str:
    return name.lower().replace(" ", "_")

def get_latest_player_report(bucket_name: str, team: str, player_name: str):
    s3 = boto3.client(
        "s3",
        region_name=settings.S3_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    prefix = f"reports/{team}/"
    slug = player_to_slug(player_name)

    # 1. List all files under this team
    resp = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    if "Contents" not in resp:
        return None

    # 2. Filter only files that start with the player slug
    player_files = [
        obj["Key"] for obj in resp["Contents"]
        if obj["Key"].lower().startswith(f"{prefix}{slug}")
    ]

    if not player_files:
        return None

    # 3. Extract dates and sort newest → oldest
    def extract_date(key):
        match = re.search(r"\d{4}-\d{2}-\d{2}", key)
        return datetime.strptime(match.group(), "%Y-%m-%d") if match else datetime.min

    player_files.sort(key=extract_date, reverse=True)
    latest_key = player_files[0]

    # 4. Fetch the latest JSON file
    obj = s3.get_object(Bucket=bucket_name, Key=latest_key)
    content = obj["Body"].read().decode("utf-8")

    report = json.loads(content)
    return map_report_to_ui(report, latest_key)

def map_report_to_ui(raw):
    # If it's not an injury report, return raw untouched
    if "analysis_sections" not in raw:
        return raw

    sections = {s["title"].lower(): s["text"] for s in raw.get("analysis_sections", [])}

    return {
        "player": raw["player"],
        "team": raw["team"],
        "date": raw.get("date", ""),
        "status": raw.get("status", "success"),
        "currentStatus": sections.get("current status", ""),
        "medicalAnalysis": sections.get("medical analysis", ""),
        "impactAssessment": sections.get("impact assessment", ""),
        "returnProjection": sections.get("return projection", ""),
    }