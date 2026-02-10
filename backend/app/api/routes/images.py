"""API routes for image operations."""
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from pathlib import Path
from PIL import Image as PILImage
from io import BytesIO

from app.models import Image, ExifData, AIAnalysis, Tag
from app.utils.database import get_db
from app.config import settings


router = APIRouter()


@router.get("/images")
async def list_images(
    skip: int = 0,
    limit: int = 50,
    has_exif: Optional[bool] = None,
    has_analysis: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all images with optional filters."""
    query = select(Image)

    # Apply filters
    if has_exif is not None:
        if has_exif:
            query = query.join(ExifData)
        else:
            query = query.outerjoin(ExifData).where(ExifData.id == None)

    if has_analysis is not None:
        if has_analysis:
            query = query.join(AIAnalysis)
        else:
            query = query.outerjoin(AIAnalysis).where(AIAnalysis.id == None)

    if search:
        query = query.where(Image.file_name.contains(search))

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    images = result.scalars().all()

    return {
        "images": [
            {
                "id": img.id,
                "file_name": img.file_name,
                "file_size": img.file_size,
                "created_at": img.created_at.isoformat() if img.created_at else None,
            }
            for img in images
        ],
        "skip": skip,
        "limit": limit,
        "count": len(images)
    }


@router.get("/images/{image_id}")
async def get_image(image_id: int, db: AsyncSession = Depends(get_db)):
    """Get detailed information about a specific image."""
    # Get image
    result = await db.execute(
        select(Image).where(Image.id == image_id)
    )
    image = result.scalar_one_or_none()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Get EXIF data
    exif_result = await db.execute(
        select(ExifData).where(ExifData.image_id == image_id)
    )
    exif = exif_result.scalar_one_or_none()

    # Get AI analysis
    analysis_result = await db.execute(
        select(AIAnalysis).where(AIAnalysis.image_id == image_id)
    )
    analysis = analysis_result.scalar_one_or_none()

    # Get tags
    tags_result = await db.execute(
        select(Tag).where(Tag.image_id == image_id)
    )
    tags = tags_result.scalars().all()

    return {
        "id": image.id,
        "file_name": image.file_name,
        "file_path": image.file_path,
        "file_size": image.file_size,
        "created_at": image.created_at.isoformat() if image.created_at else None,
        "exif": {
            "date_taken": exif.date_taken.isoformat() if exif and exif.date_taken else None,
            "camera_make": exif.camera_make if exif else None,
            "camera_model": exif.camera_model if exif else None,
            "lens_model": exif.lens_model if exif else None,
            "iso": exif.iso if exif else None,
            "aperture": exif.aperture if exif else None,
            "shutter_speed": exif.shutter_speed if exif else None,
            "focal_length": exif.focal_length if exif else None,
            "gps_latitude": exif.gps_latitude if exif else None,
            "gps_longitude": exif.gps_longitude if exif else None,
            "gps_altitude": exif.gps_altitude if exif else None,
            "width": exif.width if exif else None,
            "height": exif.height if exif else None,
        } if exif else None,
        "analysis": {
            "description": analysis.description if analysis else None,
            "detected_objects": analysis.detected_objects if analysis else None,
            "detected_people": analysis.detected_people if analysis else None,
            "scene_type": analysis.scene_type if analysis else None,
            "confidence_score": analysis.confidence_score if analysis else None,
            "analyzed_at": analysis.analyzed_at.isoformat() if analysis and analysis.analyzed_at else None,
        } if analysis else None,
        "tags": [
            {
                "name": tag.tag_name,
                "type": tag.tag_type,
                "confidence": tag.confidence
            }
            for tag in tags
        ]
    }


@router.get("/images/{image_id}/thumbnail")
async def get_thumbnail(
    image_id: int,
    size: int = 300,
    db: AsyncSession = Depends(get_db)
):
    """Get a thumbnail of the image."""
    # Get image
    result = await db.execute(
        select(Image).where(Image.id == image_id)
    )
    image = result.scalar_one_or_none()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    image_path = Path(image.file_path)
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image file not found")

    # Generate thumbnail
    try:
        img = PILImage.open(image_path)

        # Convert to RGB if necessary
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')

        # Create thumbnail
        img.thumbnail((size, size), PILImage.Resampling.LANCZOS)

        # Save to bytes
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)

        return Response(content=buffer.getvalue(), media_type="image/jpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating thumbnail: {str(e)}")


@router.get("/images/{image_id}/original")
async def get_original(image_id: int, db: AsyncSession = Depends(get_db)):
    """Get the original image file."""
    # Get image
    result = await db.execute(
        select(Image).where(Image.id == image_id)
    )
    image = result.scalar_one_or_none()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    image_path = Path(image.file_path)
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image file not found")

    return FileResponse(image_path)


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get overall statistics."""
    # Count images
    images_count_result = await db.execute(select(func.count(Image.id)))
    images_count = images_count_result.scalar()

    # Count with EXIF
    exif_count_result = await db.execute(select(func.count(ExifData.id)))
    exif_count = exif_count_result.scalar()

    # Count with analysis
    analysis_count_result = await db.execute(select(func.count(AIAnalysis.id)))
    analysis_count = analysis_count_result.scalar()

    # Count with GPS
    gps_count_result = await db.execute(
        select(func.count(ExifData.id)).where(
            ExifData.gps_latitude.isnot(None),
            ExifData.gps_longitude.isnot(None)
        )
    )
    gps_count = gps_count_result.scalar()

    return {
        "total_images": images_count,
        "with_exif": exif_count,
        "with_analysis": analysis_count,
        "with_gps": gps_count
    }
