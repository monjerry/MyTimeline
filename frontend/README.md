# 📷 Timeline AI

An interactive image timeline application with AI-powered analysis using LLaVA. Scan your photo library, extract EXIF metadata, analyze images with local AI, and visualize everything on an interactive timeline.

## Features

- 📸 **Image Scanning**: Recursively scan folders for images
- 📊 **EXIF Extraction**: Extract camera settings, GPS coordinates, dates, and more
- 🤖 **AI Analysis**: Analyze images with LLaVA (vision language model) via Ollama
- 📅 **Interactive Timeline**: Beautiful timeline visualization with Vis.js
- 🏷️ **Smart Tagging**: Automatic tag extraction from AI analysis
- 🗺️ **GPS Support**: View image locations on maps
- 🔍 **Filtering**: Filter by date, tags, location, and more

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
- React - UI framework
- Vite - Build tool
- Vis.js - Timeline visualization
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

### 1. Clone and Setup Backend

```bash
# Navigate to project root
cd timelineai

# Install Python dependencies
uv sync

# Initialize database
uv run python scripts/setup_db.py
```

### 2. Configure Environment

Edit `.env` file with your settings:
```bash
IMAGE_FOLDER=/Users/yourusername/Pictures
OLLAMA_MODEL=llama3.2-vision
```

### 3. Setup Frontend

```bash
cd frontend
npm install
```

## Running the Application

### Start Backend (Terminal 1)

```bash
# From project root
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

The frontend will be available at: http://localhost:5173

## Usage

### 1. Scan Images

Enter a folder path in the input field (e.g., `/Users/username/Pictures`) and click **"Scan & Process"**. This will:
- Scan the folder for images
- Extract EXIF metadata
- Analyze images with LLaVA
- Generate tags

### 2. View Timeline

Once processing is complete, the timeline will display your images chronologically. You can:
- Zoom in/out by scrolling
- Pan by dragging
- Click on images to view details

### 3. View Image Details

Click on any timeline item to open the image viewer, which shows:
- Full-resolution image
- EXIF data (camera, settings, GPS)
- AI analysis (description, scene type)
- Extracted tags

## API Endpoints

### Images
- `GET /api/images` - List images with filtering
- `GET /api/images/{id}` - Get image details
- `GET /api/images/{id}/thumbnail` - Get thumbnail
- `GET /api/images/{id}/original` - Get original image

### Timeline
- `GET /api/timeline` - Get timeline data
- `GET /api/tags` - Get available tags
- `GET /api/locations` - Get GPS locations

### Processing
- `POST /api/scan` - Scan folder for images
- `POST /api/extract-exif` - Extract EXIF data
- `POST /api/analyze` - Analyze with AI
- `POST /api/process-all` - Complete processing pipeline

### Stats
- `GET /api/stats` - Get overview statistics

## Project Structure

```
timelineai/
├── app/                        # Backend application
│   ├── models/                 # Database models
│   ├── services/               # Business logic
│   │   ├── image_scanner.py    # Image scanning
│   │   ├── exif_extractor.py   # EXIF extraction
│   │   └── image_analyzer.py   # AI analysis
│   ├── api/routes/             # API endpoints
│   ├── utils/                  # Utilities
│   └── config.py               # Configuration
├── frontend/                   # React frontend
│   └── src/
│       ├── components/         # React components
│       │   ├── Timeline/       # Timeline component
│       │   └── ImageViewer/    # Image viewer modal
│       └── services/           # API client
├── data/                       # Database and cache
├── scripts/                    # Setup scripts
├── main.py                     # FastAPI entry point
├── pyproject.toml              # Python dependencies
└── .env                        # Configuration
```

## Configuration

### Backend (.env)

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
```

### Frontend (.env.local)

```bash
VITE_API_URL=http://localhost:8000
```

## Development

### Run Tests

```bash
uv run pytest
```

### Format Code

```bash
uv run black app/
uv run ruff check app/
```

### Database Schema

The application uses SQLite with these tables:
- `images` - Image file metadata
- `exif_data` - EXIF metadata (camera, GPS, etc.)
- `ai_analysis` - AI analysis results
- `tags` - Searchable tags

To reset the database:
```bash
uv run python scripts/setup_db.py
```

## Performance Notes

- **LLaVA Processing**: AI analysis can take 5-10 seconds per image
- **Batch Processing**: Images are processed in batches to avoid overwhelming the system
- **Caching**: Thumbnails and results are cached for faster loading
- **GPU Acceleration**: If you have a GPU, Ollama will automatically use it for faster inference

## Troubleshooting

### Ollama Connection Issues

Make sure Ollama is running:
```bash
ollama list  # Check if Ollama is running
ollama pull llama3.2-vision  # Pull the model
```

### CORS Errors

Make sure the backend CORS_ORIGINS includes your frontend URL:
```bash
CORS_ORIGINS=http://localhost:5173
```

### Database Issues

Reset the database:
```bash
rm data/images.db
uv run python scripts/setup_db.py
```

### Image Loading Issues

Check file permissions and ensure the IMAGE_FOLDER path is correct and accessible.

## Future Enhancements

- [ ] Face recognition and grouping
- [ ] Duplicate image detection
- [ ] Automatic event clustering
- [ ] Semantic search with embeddings
- [ ] Export timeline as video/PDF
- [ ] Multi-user support
- [ ] Mobile app

## License

MIT

## Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [Ollama](https://ollama.ai/)
- [Vis.js Timeline](https://visjs.org/)
- [LLaVA](https://llava-vl.github.io/)
