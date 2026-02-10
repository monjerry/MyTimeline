"""Image scanner service - scans directories for image files."""
import os
from pathlib import Path
from typing import List, Set
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Image


class ImageScanner:
    """Scans directories for image files and stores metadata in database."""

    # Supported image file extensions
    SUPPORTED_EXTENSIONS: Set[str] = {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp",
        ".tiff", ".tif", ".heic", ".heif", ".webp"
    }

    def __init__(self, db_session: AsyncSession):
        """Initialize scanner with database session."""
        self.db_session = db_session

    async def scan_folder(self, folder_path: Path, recursive: bool = True) -> dict:
        """
        Scan a folder for images and add them to the database.

        Args:
            folder_path: Path to the folder to scan
            recursive: Whether to scan subdirectories recursively

        Returns:
            Dictionary with scan results (found, new, skipped, errors)
        """
        if not folder_path.exists():
            raise ValueError(f"Folder does not exist: {folder_path}")

        if not folder_path.is_dir():
            raise ValueError(f"Path is not a directory: {folder_path}")

        results = {
            "found": 0,
            "new": 0,
            "skipped": 0,
            "errors": 0,
            "error_files": []
        }

        # Get existing file paths from database
        existing_paths = await self._get_existing_paths()

        # Find all image files
        image_files = self._find_images(folder_path, recursive)
        results["found"] = len(image_files)

        # Process each image file
        for image_path in image_files:
            try:
                # Skip if already in database
                if str(image_path) in existing_paths:
                    results["skipped"] += 1
                    continue

                # Add to database
                await self._add_image(image_path)
                results["new"] += 1

            except Exception as e:
                results["errors"] += 1
                results["error_files"].append({
                    "path": str(image_path),
                    "error": str(e)
                })

        # Commit all changes
        await self.db_session.commit()

        return results

    def _find_images(self, folder_path: Path, recursive: bool) -> List[Path]:
        """
        Find all image files in a folder.

        Args:
            folder_path: Path to the folder to scan
            recursive: Whether to scan subdirectories recursively

        Returns:
            List of Path objects for image files
        """
        image_files = []

        if recursive:
            # Recursive search
            for root, _, files in os.walk(folder_path):
                for filename in files:
                    file_path = Path(root) / filename
                    if self._is_image_file(file_path):
                        image_files.append(file_path)
        else:
            # Non-recursive search (only immediate children)
            for item in folder_path.iterdir():
                if item.is_file() and self._is_image_file(item):
                    image_files.append(item)

        return image_files

    def _is_image_file(self, file_path: Path) -> bool:
        """Check if a file is a supported image format."""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    async def _get_existing_paths(self) -> Set[str]:
        """Get set of all existing file paths from database."""
        result = await self.db_session.execute(
            select(Image.file_path)
        )
        return {path for (path,) in result}

    async def _add_image(self, image_path: Path):
        """Add an image to the database."""
        # Get file stats
        stats = image_path.stat()

        # Create Image record
        image = Image(
            file_path=str(image_path.absolute()),
            file_name=image_path.name,
            file_size=stats.st_size,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db_session.add(image)


async def scan_folder(db_session: AsyncSession, folder_path: Path, recursive: bool = True) -> dict:
    """
    Convenience function to scan a folder.

    Args:
        db_session: Database session
        folder_path: Path to the folder to scan
        recursive: Whether to scan subdirectories recursively

    Returns:
        Dictionary with scan results
    """
    scanner = ImageScanner(db_session)
    return await scanner.scan_folder(folder_path, recursive)
