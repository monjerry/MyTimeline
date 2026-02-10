"""Database models for the timeline application."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class Image(Base):
    """Image file metadata."""
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column(String(512), unique=True, nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    exif_data: Mapped[Optional["ExifData"]] = relationship("ExifData", back_populates="image", uselist=False)
    ai_analysis: Mapped[Optional["AIAnalysis"]] = relationship("AIAnalysis", back_populates="image", uselist=False)
    tags: Mapped[list["Tag"]] = relationship("Tag", back_populates="image")

    def __repr__(self):
        return f"<Image(id={self.id}, file_name='{self.file_name}')>"


class ExifData(Base):
    """EXIF metadata extracted from images."""
    __tablename__ = "exif_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey("images.id"), unique=True)

    # Date and time
    date_taken: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True)

    # Camera info
    camera_make: Mapped[Optional[str]] = mapped_column(String(100))
    camera_model: Mapped[Optional[str]] = mapped_column(String(100))
    lens_model: Mapped[Optional[str]] = mapped_column(String(100))

    # Camera settings
    iso: Mapped[Optional[int]] = mapped_column(Integer)
    aperture: Mapped[Optional[float]] = mapped_column(Float)
    shutter_speed: Mapped[Optional[str]] = mapped_column(String(50))
    focal_length: Mapped[Optional[float]] = mapped_column(Float)

    # GPS data
    gps_latitude: Mapped[Optional[float]] = mapped_column(Float, index=True)
    gps_longitude: Mapped[Optional[float]] = mapped_column(Float, index=True)
    gps_altitude: Mapped[Optional[float]] = mapped_column(Float)

    # Image properties
    orientation: Mapped[Optional[int]] = mapped_column(Integer)
    width: Mapped[Optional[int]] = mapped_column(Integer)
    height: Mapped[Optional[int]] = mapped_column(Integer)

    # Relationship
    image: Mapped["Image"] = relationship("Image", back_populates="exif_data")

    # Composite index for GPS queries
    __table_args__ = (
        Index('idx_gps_coordinates', 'gps_latitude', 'gps_longitude'),
    )

    def __repr__(self):
        return f"<ExifData(image_id={self.image_id}, date_taken={self.date_taken})>"


class AIAnalysis(Base):
    """AI-generated analysis of images using LLaVA."""
    __tablename__ = "ai_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey("images.id"), unique=True)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Analysis results
    description: Mapped[Optional[str]] = mapped_column(Text)
    detected_objects: Mapped[Optional[str]] = mapped_column(Text)  # JSON array as string
    detected_people: Mapped[Optional[str]] = mapped_column(Text)   # JSON array as string
    scene_type: Mapped[Optional[str]] = mapped_column(String(100))
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    raw_response: Mapped[Optional[str]] = mapped_column(Text)

    # Relationship
    image: Mapped["Image"] = relationship("Image", back_populates="ai_analysis")

    def __repr__(self):
        return f"<AIAnalysis(image_id={self.image_id}, scene_type='{self.scene_type}')>"


class Tag(Base):
    """Tags extracted from AI analysis for filtering."""
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey("images.id"))
    tag_name: Mapped[str] = mapped_column(String(100), nullable=False)
    tag_type: Mapped[str] = mapped_column(String(50))  # 'object', 'person', 'scene', 'location'
    confidence: Mapped[Optional[float]] = mapped_column(Float)

    # Relationship
    image: Mapped["Image"] = relationship("Image", back_populates="tags")

    # Composite index for tag queries
    __table_args__ = (
        Index('idx_tag_name_type', 'tag_name', 'tag_type'),
        Index('idx_image_tags', 'image_id'),
    )

    def __repr__(self):
        return f"<Tag(tag_name='{self.tag_name}', tag_type='{self.tag_type}')>"
