"""Database setup script - creates tables and initializes the database."""
import sys
import asyncio
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.config import settings


async def setup_database():
    """Create all database tables and initialize the database."""
    print("Setting up database...")
    print(f"Database URL: {settings.database_url}")

    # Create data directory if it doesn't exist
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)

    # Create cache directories
    cache_dir = settings.cache_dir
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / "thumbnails").mkdir(exist_ok=True)

    # Create async engine
    engine = create_async_engine(
        settings.database_url,
        echo=True  # Log SQL queries
    )

    # Create all tables
    async with engine.begin() as conn:
        print("Creating tables...")
        await conn.run_sync(Base.metadata.drop_all)  # Drop existing tables (for clean setup)
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully!")

    # Close engine
    await engine.dispose()

    print("\nDatabase setup complete!")
    print(f"Database file: {data_dir / 'images.db'}")
    print(f"Cache directory: {cache_dir}")


if __name__ == "__main__":
    asyncio.run(setup_database())
