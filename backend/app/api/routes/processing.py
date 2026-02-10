"""API routes for image processing operations (scan, analyze)."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from pathlib import Path
from typing import List, Optional

from app.models import Image
from app.utils.database import get_db
from app.services.image_scanner import scan_folder
from app.services.exif_extractor import extract_exif
from app.services.image_analyzer import analyze_image
from app.config import settings


router = APIRouter()


class ScanRequest(BaseModel):
    """Request model for folder scanning."""
    folder_path: str
    recursive: bool = True


class AnalyzeRequest(BaseModel):
    """Request model for image analysis."""
    image_ids: Optional[List[int]] = None
    force: bool = False


@router.post("/scan")
async def scan_images(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Scan a folder for images and add them to the database."""
    folder_path = Path(request.folder_path)

    if not folder_path.exists():
        raise HTTPException(status_code=400, detail=f"Folder does not exist: {folder_path}")

    try:
        # Scan folder
        results = await scan_folder(db, folder_path, request.recursive)

        return {
            "status": "success",
            "results": results,
            "message": f"Found {results['found']} images, added {results['new']}, skipped {results['skipped']}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scanning folder: {str(e)}")


@router.post("/extract-exif")
async def extract_exif_batch(
    db: AsyncSession = Depends(get_db)
):
    """Extract EXIF data from all images that don't have it yet."""
    # Get images without EXIF data
    query = (
        select(Image)
        .outerjoin(Image.exif_data)
        .where(Image.exif_data == None)
    )

    result = await db.execute(query)
    images = result.scalars().all()

    success_count = 0
    error_count = 0
    errors = []

    for image in images:
        try:
            await extract_exif(db, image.id)
            success_count += 1
        except Exception as e:
            error_count += 1
            errors.append({
                "image_id": image.id,
                "file_name": image.file_name,
                "error": str(e)
            })

    return {
        "status": "success",
        "total_processed": len(images),
        "success": success_count,
        "errors": error_count,
        "error_details": errors[:10]  # Return first 10 errors
    }


@router.post("/analyze")
async def analyze_images(
    request: AnalyzeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Analyze images using LLaVA."""
    # Get images to analyze
    if request.image_ids:
        query = select(Image).where(Image.id.in_(request.image_ids))
    elif not request.force:
        # Only analyze images without analysis
        query = (
            select(Image)
            .outerjoin(Image.ai_analysis)
            .where(Image.ai_analysis == None)
        )
    else:
        # Analyze all images
        query = select(Image)

    result = await db.execute(query)
    images = result.scalars().all()

    if not images:
        return {
            "status": "success",
            "message": "No images to analyze",
            "total_processed": 0,
            "success": 0,
            "errors": 0
        }

    success_count = 0
    error_count = 0
    errors = []

    for image in images:
        try:
            await analyze_image(db, image.id)
            success_count += 1
        except Exception as e:
            error_count += 1
            errors.append({
                "image_id": image.id,
                "file_name": image.file_name,
                "error": str(e)
            })

    return {
        "status": "success",
        "total_processed": len(images),
        "success": success_count,
        "errors": error_count,
        "error_details": errors[:10]  # Return first 10 errors
    }


@router.post("/process-all")
async def process_all(
    folder_path: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Process all images: scan, extract EXIF, and analyze."""
    results = {
        "scan": None,
        "exif": None,
        "analysis": None
    }

    # Step 1: Scan folder if provided
    if folder_path:
        folder = Path(folder_path)
        if folder.exists():
            scan_results = await scan_folder(db, folder, recursive=True)
            results["scan"] = scan_results

    # Step 2: Extract EXIF from images without it
    query = (
        select(Image)
        .outerjoin(Image.exif_data)
        .where(Image.exif_data == None)
    )
    result = await db.execute(query)
    images_for_exif = result.scalars().all()

    exif_success = 0
    for image in images_for_exif:
        try:
            await extract_exif(db, image.id)
            exif_success += 1
        except Exception:
            pass

    results["exif"] = {
        "total": len(images_for_exif),
        "success": exif_success
    }

    # Step 3: Analyze images without analysis
    query = (
        select(Image)
        .outerjoin(Image.ai_analysis)
        .where(Image.ai_analysis == None)
    )
    result = await db.execute(query)
    images_for_analysis = result.scalars().all()

    analysis_success = 0
    for image in images_for_analysis:
        try:
            await analyze_image(db, image.id)
            analysis_success += 1
        except Exception:
            pass

    results["analysis"] = {
        "total": len(images_for_analysis),
        "success": analysis_success
    }

    return {
        "status": "success",
        "results": results
    }
