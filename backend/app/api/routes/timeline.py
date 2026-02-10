"""API routes for timeline operations."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime

from app.models import Image, ExifData, AIAnalysis, Tag
from app.utils.database import get_db


router = APIRouter()


@router.get("/timeline")
async def get_timeline(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    tags: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get timeline data for visualization."""
    query = (
        select(Image, ExifData, AIAnalysis)
        .outerjoin(ExifData, Image.id == ExifData.image_id)
        .outerjoin(AIAnalysis, Image.id == AIAnalysis.image_id)
    )

    # Apply date filters
    if date_from:
        date_from_dt = datetime.fromisoformat(date_from)
        query = query.where(ExifData.date_taken >= date_from_dt)

    if date_to:
        date_to_dt = datetime.fromisoformat(date_to)
        query = query.where(ExifData.date_taken <= date_to_dt)

    # Apply tag filters
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        query = query.join(Tag, Image.id == Tag.image_id).where(
            Tag.tag_name.in_(tag_list)
        )

    # Order by date taken
    query = query.order_by(ExifData.date_taken.desc())

    result = await db.execute(query)
    rows = result.all()

    timeline_items = []
    for image, exif, analysis in rows:
        # Use date_taken if available, otherwise use created_at
        item_date = exif.date_taken if exif and exif.date_taken else image.created_at

        timeline_items.append({
            "id": image.id,
            "content": f'<img src="/api/images/{image.id}/thumbnail?size=150" alt="{image.file_name}" />',
            "start": item_date.isoformat() if item_date else None,
            "title": analysis.description[:100] if analysis and analysis.description else image.file_name,
            "className": "timeline-item",
            "file_name": image.file_name,
            "description": analysis.description if analysis else None,
            "scene_type": analysis.scene_type if analysis else None,
            "has_gps": bool(exif and exif.gps_latitude and exif.gps_longitude) if exif else False
        })

    return {
        "items": timeline_items,
        "count": len(timeline_items)
    }


@router.get("/tags")
async def get_tags(
    tag_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all available tags with counts."""
    query = select(
        Tag.tag_name,
        Tag.tag_type,
        func.count(Tag.id).label('count')
    ).group_by(Tag.tag_name, Tag.tag_type)

    if tag_type:
        query = query.where(Tag.tag_type == tag_type)

    query = query.order_by(func.count(Tag.id).desc())

    result = await db.execute(query)
    rows = result.all()

    return {
        "tags": [
            {
                "name": row.tag_name,
                "type": row.tag_type,
                "count": row.count
            }
            for row in rows
        ]
    }


@router.get("/locations")
async def get_locations(db: AsyncSession = Depends(get_db)):
    """Get unique GPS locations with image counts."""
    query = (
        select(
            ExifData.gps_latitude,
            ExifData.gps_longitude,
            func.count(ExifData.id).label('count')
        )
        .where(
            ExifData.gps_latitude.isnot(None),
            ExifData.gps_longitude.isnot(None)
        )
        .group_by(ExifData.gps_latitude, ExifData.gps_longitude)
    )

    result = await db.execute(query)
    rows = result.all()

    return {
        "locations": [
            {
                "latitude": row.gps_latitude,
                "longitude": row.gps_longitude,
                "count": row.count
            }
            for row in rows
        ]
    }
