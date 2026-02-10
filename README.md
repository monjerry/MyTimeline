# 📷 Timeline AI

An interactive image timeline application with AI-powered analysis using LLaVA. Scan your photo library, extract EXIF metadata, analyze images with local AI, and visualize everything on an interactive timeline.

## Features

- 📸 **Image Scanning** - Recursively scan folders for images
- 📊 **EXIF Extraction** - Extract camera settings, GPS coordinates, dates, and more
- 🤖 **AI Analysis** - Analyze images with LLaVA (vision language model) via Ollama
- 📅 **Interactive Timeline** - Beautiful timeline visualization with Vis.js
- 🏷️ **Smart Tagging** - Automatic tag extraction from AI analysis
- 🗺️ **GPS Support** - View image locations on maps
- 🔍 **Filtering** - Filter by date, tags, location, and more
- 🗑️ **Data Management** - Clear all data with one click

## Tech Stack

**Backend:**
- Python 3.14+
- FastAPI - Web framework
- SQLAlchemy - Database ORM
- SQLite - Database
- Ollama - LLaVA integration
- Pillow & piexif - Image processing
- uv - Package management

**Frontend:**
- React 18 - UI framework
- Vite - Build tool
- Vis.js Timeline - Timeline visualization
- Axios - HTTP client

## Prerequisites

1. **Python 3.10+** - [Download](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download](https://nodejs.org/)
3. **uv** - Fast Python package manager
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
4. **Ollama** - For LLaVA model
   - Install: [https://ollama.ai/download](https://ollama.ai/download)
   - Pull model: `ollama pull llama3.2-vision` or `ollama pull llava`

## Installation

### 1. Setup Backend

```bash
# Navigate to project root
cd /Users/monjerry/Documents/timelineai

# Navigate to backend directory
cd backend

# Install Python dependencies
uv sync

# Initialize database
uv run python scripts/setup_db.py
```

### 2. Configure Environment

Edit `backend/.env` file with your settings:
```bash
IMAGE_FOLDER=/Users/yourusername/Pictures
OLLAMA_MODEL=llama3.2-vision
```

### 3. Setup Frontend

```bash
# From project root
cd frontend
npm install
```

## Running the Application

### Start Backend (Terminal 1)

```bash
# From project root
cd backend
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### Start Frontend (Terminal 2)

```bash
# From project root
cd frontend
npm run dev
```

The frontend will be available at: **http://localhost:5173**

## Usage

### 1. Scan Images

1. Enter a folder path in the input field (e.g., `/Users/username/Pictures`)
2. Click **"Scan & Process"**

This will:
- Scan the folder for images (recursive)
- Extract EXIF metadata (date, camera, GPS)
- Analyze images with LLaVA AI
- Generate searchable tags

### 2. View Timeline

Once processing is complete, the timeline will display your images chronologically:

- **Zoom:** Scroll up/down or use trackpad gestures
- **Pan:** Click and drag the timeline
- **Select:** Click any image thumbnail to view details
- **Navigate:** Timeline shows date-based organization

### 3. View Image Details

Click on any timeline item to open the full image viewer:

- **Full-resolution image display**
- **EXIF Data:**
  - Camera make and model
  - Lens information
  - ISO, aperture, shutter speed, focal length
  - Date and time photo was taken
- **GPS Location:**
  - Coordinates with clickable Google Maps link
  - Altitude information
- **AI Analysis:**
  - Detailed image description
  - Detected objects and people
  - Scene type classification
- **Tags:** Auto-generated searchable tags

### 4. Clear Timeline

Click the **"🗑️ Clear All"** button to remove all data:

- Deletes all scanned images from database
- Removes EXIF data, AI analysis, and tags
- Shows confirmation dialog before deletion
- **⚠️ Warning:** Cannot be undone - use with caution!

## API Endpoints

### Images
- `GET /api/images` - List images with filtering options
- `GET /api/images/{id}` - Get specific image details
- `GET /api/images/{id}/thumbnail?size=150` - Get thumbnail
- `GET /api/images/{id}/original` - Get original image file

### Timeline
- `GET /api/timeline` - Get timeline data for visualization
- `GET /api/tags` - Get available tags with counts
- `GET /api/locations` - Get unique GPS locations

### Processing
- `POST /api/scan` - Scan folder for images
  ```json
  {"folder_path": "/path/to/images", "recursive": true}
  ```
- `POST /api/extract-exif` - Extract EXIF from unprocessed images
- `POST /api/analyze` - Analyze images with LLaVA
  ```json
  {"image_ids": [1, 2, 3], "force": false}
  ```
- `POST /api/process-all` - Run complete pipeline
- `DELETE /api/clear-all` - Delete all images and data ⚠️

### Stats
- `GET /api/stats` - Get overview statistics

## Project Structure

```
timelineai/
├── backend/                        # Python backend
│   ├── app/
│   │   ├── config.py              # Configuration management
│   │   ├── models/                # SQLAlchemy models
│   │   │   └── __init__.py        # Image, ExifData, AIAnalysis, Tag
│   │   ├── services/              # Business logic
│   │   │   ├── image_scanner.py   # Folder scanning
│   │   │   ├── exif_extractor.py  # EXIF extraction
│   │   │   └── image_analyzer.py  # LLaVA integration
│   │   ├── api/routes/            # API endpoints
│   │   │   ├── images.py          # Image operations
│   │   │   ├── timeline.py        # Timeline data
│   │   │   └── processing.py      # Scan/analyze/clear
│   │   └── utils/
│   │       └── database.py        # DB session management
│   ├── data/
│   │   ├── images.db              # SQLite database
│   │   └── cache/                 # Thumbnail cache
│   ├── scripts/
│   │   └── setup_db.py            # Database initialization
│   ├── main.py                    # FastAPI entry point
│   ├── pyproject.toml             # uv dependencies
│   └── .env                       # Configuration
├── frontend/                       # React frontend
│   ├── src/
│   │   ├── App.jsx                # Main application
│   │   ├── components/
│   │   │   ├── Timeline/          # Vis.js timeline
│   │   │   └── ImageViewer/       # Image detail modal
│   │   ├── services/
│   │   │   └── api.js             # API client
│   │   └── hooks/                 # Custom React hooks
│   ├── package.json
│   └── .env.local                 # Frontend config
└── README.md
```

## Configuration

### Backend (.env)

Located at `backend/.env`:

```bash
# Image source folder
IMAGE_FOLDER=/path/to/images

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/images.db

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2-vision
OLLAMA_TIMEOUT=120

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173

# Processing
BATCH_SIZE=10
MAX_WORKERS=4

# Caching
CACHE_DIR=./data/cache
THUMBNAIL_SIZES=150,300,600
```

### Frontend (.env.local)

Located at `frontend/.env.local`:

```bash
VITE_API_URL=http://localhost:8000
```

## UI Features

### Timeline Navigation
- **Zoom:** Scroll up/down or pinch on trackpad
- **Pan:** Click and drag the timeline
- **Select:** Click any image to view full details
- **View:** Thumbnails display directly on timeline items

### Action Buttons
- **Scan & Process:** Scan folder, extract EXIF, analyze with AI
- **Clear All:** Remove all data from database (with confirmation)

### Statistics Dashboard
Real-time counts displayed at the top:
- Total images in database
- Images with EXIF data
- Images with AI analysis
- Images with GPS coordinates

## Database Schema

SQLite database with optimized indexes:

- **images** - File metadata (path, name, size, timestamps)
- **exif_data** - Camera settings, GPS, image properties
- **ai_analysis** - LLaVA descriptions, detected objects, scene types
- **tags** - Searchable tags (objects, people, scenes, activities)

To reset the database:
```bash
cd backend
rm data/images.db
uv run python scripts/setup_db.py
```

## Development

### Run Tests

```bash
cd backend
uv run pytest
```

### Format Code

```bash
cd backend
uv run black app/
uv run ruff check app/
```

### Frontend Development

```bash
cd frontend
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build
```

## Performance Notes

- **LLaVA Processing:** 5-10 seconds per image (GPU: 1-3 seconds)
- **Batch Processing:** Images processed in configurable batches
- **Caching:** Thumbnails and analysis results cached automatically
- **GPU Acceleration:** Ollama automatically uses GPU if available
- **Database:** Indexed for fast queries on date, GPS, and tags

## Troubleshooting

### Timeline Images Not Showing
- Ensure backend is running on http://localhost:8000
- Check browser console for errors
- Verify images were scanned successfully
- Try clearing browser cache

### Ollama Connection Issues

```bash
# Check if Ollama is running
ollama list

# Pull the vision model
ollama pull llama3.2-vision

# Test Ollama
ollama run llama3.2-vision "describe this image" --image /path/to/test.jpg
```

### CORS Errors

Ensure `CORS_ORIGINS` in backend `.env` includes frontend URL:
```bash
CORS_ORIGINS=http://localhost:5173
```

### Database Issues

Reset the database:
```bash
cd backend
rm data/images.db
uv run python scripts/setup_db.py
```

### Port Already in Use

Backend (port 8000):
```bash
lsof -ti:8000 | xargs kill -9
```

Frontend (port 5173):
```bash
lsof -ti:5173 | xargs kill -9
```

### Image Loading Issues
- Check file permissions on image folder
- Ensure IMAGE_FOLDER path is correct
- Verify supported formats: JPG, PNG, HEIC, TIFF, WebP

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff, .tif)
- HEIC (.heic, .heif) - Requires pillow-heif on some systems
- WebP (.webp)

## Future Enhancements

- [ ] Face recognition and grouping
- [ ] Duplicate image detection
- [ ] Automatic event clustering by time/location
- [ ] Semantic search with vector embeddings
- [ ] Export timeline as video or PDF
- [ ] Multi-user support with authentication
- [ ] Mobile responsive optimization
- [ ] Batch download selected images
- [ ] Custom tag editing
- [ ] Advanced filtering (date ranges, multiple tags)
- [ ] Map view with photo clusters
- [ ] PostgreSQL support for production
- [ ] Docker containerization
- [ ] Image editing capabilities

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI library
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [Vis.js Timeline](https://visjs.org/) - Interactive timeline component
- [LLaVA](https://llava-vl.github.io/) - Vision language model
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

## Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check existing documentation
- Review API docs at http://localhost:8000/docs

---

**Enjoy exploring your photo timeline with AI! 📸✨**
