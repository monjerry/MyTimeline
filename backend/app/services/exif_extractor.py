"""EXIF extractor service - extracts metadata from images."""
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from PIL import Image as PILImage
import piexif
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Image, ExifData


class ExifExtractor:
    """Extracts EXIF metadata from images."""

    def __init__(self, db_session: AsyncSession):
        """Initialize extractor with database session."""
        self.db_session = db_session

    async def extract_from_image(self, image_id: int) -> Optional[ExifData]:
        """
        Extract EXIF data from an image and store in database.

        Args:
            image_id: ID of the image in the database

        Returns:
            ExifData object if successful, None otherwise
        """
        # Get image from database
        result = await self.db_session.execute(
            select(Image).where(Image.id == image_id)
        )
        image = result.scalar_one_or_none()

        if not image:
            raise ValueError(f"Image with ID {image_id} not found")

        # Extract EXIF data
        exif_dict = self._extract_exif_dict(Path(image.file_path))

        if not exif_dict:
            return None

        # Parse EXIF data
        exif_data = ExifData(
            image_id=image_id,
            date_taken=self._extract_date_taken(exif_dict),
            camera_make=self._extract_camera_make(exif_dict),
            camera_model=self._extract_camera_model(exif_dict),
            lens_model=self._extract_lens_model(exif_dict),
            iso=self._extract_iso(exif_dict),
            aperture=self._extract_aperture(exif_dict),
            shutter_speed=self._extract_shutter_speed(exif_dict),
            focal_length=self._extract_focal_length(exif_dict),
            orientation=self._extract_orientation(exif_dict),
            width=self._extract_width(exif_dict),
            height=self._extract_height(exif_dict)
        )

        # Extract GPS data
        gps_data = self._extract_gps(exif_dict)
        if gps_data:
            exif_data.gps_latitude = gps_data.get("latitude")
            exif_data.gps_longitude = gps_data.get("longitude")
            exif_data.gps_altitude = gps_data.get("altitude")

        # Add to database
        self.db_session.add(exif_data)
        await self.db_session.commit()

        return exif_data

    def _extract_exif_dict(self, image_path: Path) -> Optional[Dict]:
        """Extract EXIF dictionary from image file."""
        try:
            img = PILImage.open(image_path)

            # Try to load EXIF data
            if hasattr(img, '_getexif') and img._getexif():
                return piexif.load(img.info.get('exif', b''))
            elif 'exif' in img.info:
                return piexif.load(img.info['exif'])
            else:
                return None

        except Exception as e:
            print(f"Error extracting EXIF from {image_path}: {e}")
            return None

    def _extract_date_taken(self, exif_dict: Dict) -> Optional[datetime]:
        """Extract date/time the photo was taken."""
        try:
            # Try DateTimeOriginal first
            if "Exif" in exif_dict and piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]:
                date_str = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
                return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")

            # Try DateTime as fallback
            if "0th" in exif_dict and piexif.ImageIFD.DateTime in exif_dict["0th"]:
                date_str = exif_dict["0th"][piexif.ImageIFD.DateTime].decode('utf-8')
                return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")

        except Exception as e:
            print(f"Error extracting date: {e}")

        return None

    def _extract_camera_make(self, exif_dict: Dict) -> Optional[str]:
        """Extract camera manufacturer."""
        try:
            if "0th" in exif_dict and piexif.ImageIFD.Make in exif_dict["0th"]:
                return exif_dict["0th"][piexif.ImageIFD.Make].decode('utf-8').strip()
        except Exception:
            pass
        return None

    def _extract_camera_model(self, exif_dict: Dict) -> Optional[str]:
        """Extract camera model."""
        try:
            if "0th" in exif_dict and piexif.ImageIFD.Model in exif_dict["0th"]:
                return exif_dict["0th"][piexif.ImageIFD.Model].decode('utf-8').strip()
        except Exception:
            pass
        return None

    def _extract_lens_model(self, exif_dict: Dict) -> Optional[str]:
        """Extract lens model."""
        try:
            if "Exif" in exif_dict and piexif.ExifIFD.LensModel in exif_dict["Exif"]:
                return exif_dict["Exif"][piexif.ExifIFD.LensModel].decode('utf-8').strip()
        except Exception:
            pass
        return None

    def _extract_iso(self, exif_dict: Dict) -> Optional[int]:
        """Extract ISO speed."""
        try:
            if "Exif" in exif_dict and piexif.ExifIFD.ISOSpeedRatings in exif_dict["Exif"]:
                return int(exif_dict["Exif"][piexif.ExifIFD.ISOSpeedRatings])
        except Exception:
            pass
        return None

    def _extract_aperture(self, exif_dict: Dict) -> Optional[float]:
        """Extract aperture value (f-number)."""
        try:
            if "Exif" in exif_dict and piexif.ExifIFD.FNumber in exif_dict["Exif"]:
                f_number = exif_dict["Exif"][piexif.ExifIFD.FNumber]
                if isinstance(f_number, tuple):
                    return float(f_number[0]) / float(f_number[1])
                return float(f_number)
        except Exception:
            pass
        return None

    def _extract_shutter_speed(self, exif_dict: Dict) -> Optional[str]:
        """Extract shutter speed."""
        try:
            if "Exif" in exif_dict and piexif.ExifIFD.ExposureTime in exif_dict["Exif"]:
                exposure = exif_dict["Exif"][piexif.ExifIFD.ExposureTime]
                if isinstance(exposure, tuple):
                    numerator, denominator = exposure
                    if denominator != 0:
                        return f"{numerator}/{denominator}"
                return str(exposure)
        except Exception:
            pass
        return None

    def _extract_focal_length(self, exif_dict: Dict) -> Optional[float]:
        """Extract focal length in mm."""
        try:
            if "Exif" in exif_dict and piexif.ExifIFD.FocalLength in exif_dict["Exif"]:
                focal = exif_dict["Exif"][piexif.ExifIFD.FocalLength]
                if isinstance(focal, tuple):
                    return float(focal[0]) / float(focal[1])
                return float(focal)
        except Exception:
            pass
        return None

    def _extract_orientation(self, exif_dict: Dict) -> Optional[int]:
        """Extract image orientation."""
        try:
            if "0th" in exif_dict and piexif.ImageIFD.Orientation in exif_dict["0th"]:
                return int(exif_dict["0th"][piexif.ImageIFD.Orientation])
        except Exception:
            pass
        return None

    def _extract_width(self, exif_dict: Dict) -> Optional[int]:
        """Extract image width."""
        try:
            if "Exif" in exif_dict and piexif.ExifIFD.PixelXDimension in exif_dict["Exif"]:
                return int(exif_dict["Exif"][piexif.ExifIFD.PixelXDimension])
        except Exception:
            pass
        return None

    def _extract_height(self, exif_dict: Dict) -> Optional[int]:
        """Extract image height."""
        try:
            if "Exif" in exif_dict and piexif.ExifIFD.PixelYDimension in exif_dict["Exif"]:
                return int(exif_dict["Exif"][piexif.ExifIFD.PixelYDimension])
        except Exception:
            pass
        return None

    def _extract_gps(self, exif_dict: Dict) -> Optional[Dict[str, float]]:
        """Extract GPS coordinates and convert to decimal format."""
        try:
            if "GPS" not in exif_dict:
                return None

            gps = exif_dict["GPS"]
            result = {}

            # Extract latitude
            if piexif.GPSIFD.GPSLatitude in gps and piexif.GPSIFD.GPSLatitudeRef in gps:
                lat = self._convert_gps_to_decimal(gps[piexif.GPSIFD.GPSLatitude])
                lat_ref = gps[piexif.GPSIFD.GPSLatitudeRef].decode('utf-8')
                if lat_ref == 'S':
                    lat = -lat
                result["latitude"] = lat

            # Extract longitude
            if piexif.GPSIFD.GPSLongitude in gps and piexif.GPSIFD.GPSLongitudeRef in gps:
                lon = self._convert_gps_to_decimal(gps[piexif.GPSIFD.GPSLongitude])
                lon_ref = gps[piexif.GPSIFD.GPSLongitudeRef].decode('utf-8')
                if lon_ref == 'W':
                    lon = -lon
                result["longitude"] = lon

            # Extract altitude
            if piexif.GPSIFD.GPSAltitude in gps:
                altitude = gps[piexif.GPSIFD.GPSAltitude]
                if isinstance(altitude, tuple):
                    result["altitude"] = float(altitude[0]) / float(altitude[1])
                else:
                    result["altitude"] = float(altitude)

            return result if result else None

        except Exception as e:
            print(f"Error extracting GPS: {e}")
            return None

    def _convert_gps_to_decimal(self, coords: tuple) -> float:
        """Convert GPS coordinates from degrees/minutes/seconds to decimal."""
        degrees = float(coords[0][0]) / float(coords[0][1])
        minutes = float(coords[1][0]) / float(coords[1][1])
        seconds = float(coords[2][0]) / float(coords[2][1])

        return degrees + (minutes / 60.0) + (seconds / 3600.0)


async def extract_exif(db_session: AsyncSession, image_id: int) -> Optional[ExifData]:
    """
    Convenience function to extract EXIF data from an image.

    Args:
        db_session: Database session
        image_id: ID of the image

    Returns:
        ExifData object if successful, None otherwise
    """
    extractor = ExifExtractor(db_session)
    return await extractor.extract_from_image(image_id)
