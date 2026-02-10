"""Image analyzer service - analyzes images using LLaVA via Ollama."""
import json
import re
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ollama import Client as OllamaClient
from app.models import Image, AIAnalysis, Tag
from app.config import settings


class ImageAnalyzer:
    """Analyzes images using LLaVA vision model via Ollama."""

    def __init__(self, db_session: AsyncSession):
        """Initialize analyzer with database session."""
        self.db_session = db_session
        self.ollama_client = OllamaClient(host=settings.ollama_host)
        self.model = settings.ollama_model

    async def analyze_image(self, image_id: int) -> Optional[AIAnalysis]:
        """
        Analyze an image using LLaVA and store results in database.

        Args:
            image_id: ID of the image in the database

        Returns:
            AIAnalysis object if successful, None otherwise
        """
        # Get image from database
        result = await self.db_session.execute(
            select(Image).where(Image.id == image_id)
        )
        image = result.scalar_one_or_none()

        if not image:
            raise ValueError(f"Image with ID {image_id} not found")

        image_path = Path(image.file_path)
        if not image_path.exists():
            raise ValueError(f"Image file not found: {image_path}")

        # Get analysis from LLaVA
        try:
            analysis_data = await self._analyze_with_llava(image_path)

            if not analysis_data:
                return None

            # Create AIAnalysis record
            ai_analysis = AIAnalysis(
                image_id=image_id,
                analyzed_at=datetime.utcnow(),
                description=analysis_data.get("description"),
                detected_objects=json.dumps(analysis_data.get("objects", [])),
                detected_people=json.dumps(analysis_data.get("people", [])),
                scene_type=analysis_data.get("scene_type"),
                confidence_score=analysis_data.get("confidence", 0.0),
                raw_response=analysis_data.get("raw_response", "")
            )

            self.db_session.add(ai_analysis)

            # Create tags
            tags = self._create_tags_from_analysis(image_id, analysis_data)
            for tag in tags:
                self.db_session.add(tag)

            await self.db_session.commit()

            return ai_analysis

        except Exception as e:
            print(f"Error analyzing image {image_id}: {e}")
            return None

    async def _analyze_with_llava(self, image_path: Path) -> Optional[Dict]:
        """
        Send image to LLaVA for analysis.

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary with analysis results
        """
        prompt = """Analyze this image and provide information in JSON format:

{
    "description": "A brief, detailed description of what's in the image (2-3 sentences)",
    "objects": ["list", "of", "detected", "objects"],
    "people": ["descriptions of people if any, or empty list"],
    "scene_type": "indoor/outdoor/landscape/portrait/etc",
    "activities": ["activities", "or", "events", "happening"],
    "confidence": 0.0-1.0 (your confidence in this analysis)
}

Be specific and descriptive. Only return the JSON, no additional text."""

        try:
            # Call Ollama API
            response = self.ollama_client.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': [str(image_path)]
                }]
            )

            raw_response = response['message']['content']

            # Parse JSON response
            analysis_data = self._parse_response(raw_response)
            analysis_data["raw_response"] = raw_response

            return analysis_data

        except Exception as e:
            print(f"Error calling Ollama API: {e}")
            return None

    def _parse_response(self, response_text: str) -> Dict:
        """
        Parse LLaVA response and extract structured data.

        Args:
            response_text: Raw response from LLaVA

        Returns:
            Dictionary with parsed data
        """
        try:
            # Try to extract JSON from response
            # Sometimes the model includes extra text before/after JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)

            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)

                # Ensure required fields exist
                return {
                    "description": data.get("description", ""),
                    "objects": data.get("objects", []),
                    "people": data.get("people", []),
                    "scene_type": data.get("scene_type", "unknown"),
                    "activities": data.get("activities", []),
                    "confidence": float(data.get("confidence", 0.5))
                }

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")

        # Fallback: return raw text as description
        return {
            "description": response_text,
            "objects": [],
            "people": [],
            "scene_type": "unknown",
            "activities": [],
            "confidence": 0.3
        }

    def _create_tags_from_analysis(self, image_id: int, analysis_data: Dict) -> List[Tag]:
        """
        Create Tag objects from analysis data.

        Args:
            image_id: ID of the image
            analysis_data: Dictionary with analysis results

        Returns:
            List of Tag objects
        """
        tags = []

        # Tags from objects
        for obj in analysis_data.get("objects", []):
            if obj and isinstance(obj, str):
                tags.append(Tag(
                    image_id=image_id,
                    tag_name=obj.lower().strip(),
                    tag_type="object",
                    confidence=analysis_data.get("confidence", 0.5)
                ))

        # Tags from people
        for person in analysis_data.get("people", []):
            if person and isinstance(person, str):
                tags.append(Tag(
                    image_id=image_id,
                    tag_name=person.lower().strip(),
                    tag_type="person",
                    confidence=analysis_data.get("confidence", 0.5)
                ))

        # Tag from scene type
        scene_type = analysis_data.get("scene_type")
        if scene_type:
            tags.append(Tag(
                image_id=image_id,
                tag_name=scene_type.lower().strip(),
                tag_type="scene",
                confidence=analysis_data.get("confidence", 0.5)
            ))

        # Tags from activities
        for activity in analysis_data.get("activities", []):
            if activity and isinstance(activity, str):
                tags.append(Tag(
                    image_id=image_id,
                    tag_name=activity.lower().strip(),
                    tag_type="activity",
                    confidence=analysis_data.get("confidence", 0.5)
                ))

        return tags


async def analyze_image(db_session: AsyncSession, image_id: int) -> Optional[AIAnalysis]:
    """
    Convenience function to analyze an image.

    Args:
        db_session: Database session
        image_id: ID of the image

    Returns:
        AIAnalysis object if successful, None otherwise
    """
    analyzer = ImageAnalyzer(db_session)
    return await analyzer.analyze_image(image_id)
