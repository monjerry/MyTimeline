/**
 * Main App component for Timeline AI
 */
import { useState, useEffect } from 'react';
import Timeline from './components/Timeline/Timeline';
import ImageViewer from './components/ImageViewer/ImageViewer';
import { imagesAPI, processingAPI } from './services/api';
import './App.css';

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [filters, setFilters] = useState({});
  const [stats, setStats] = useState(null);
  const [folderPath, setFolderPath] = useState('');
  const [processing, setProcessing] = useState(false);

  // Fetch stats on mount
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await imagesAPI.getStats();
        setStats(response.data);
      } catch (err) {
        console.error('Error fetching stats:', err);
      }
    };
    fetchStats();
  }, []);

  const handleItemSelect = (item) => {
    setSelectedImage(item);
  };

  const handleCloseViewer = () => {
    setSelectedImage(null);
  };

  const handleBrowseFolder = async () => {
    try {
      // Check if File System Access API is supported
      if (!('showDirectoryPicker' in window)) {
        alert('Folder picker is not supported in your browser. Please use Chrome, Edge, or Opera.');
        return;
      }

      setProcessing(true);
      const dirHandle = await window.showDirectoryPicker();
      setFolderPath(dirHandle.name);

      // Read all image files from the directory
      const imageFiles = [];
      const supportedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.heic', '.heif', '.webp'];

      async function scanDirectory(directoryHandle, path = '') {
        for await (const entry of directoryHandle.values()) {
          if (entry.kind === 'file') {
            const fileName = entry.name.toLowerCase();
            if (supportedExtensions.some(ext => fileName.endsWith(ext))) {
              const file = await entry.getFile();
              imageFiles.push({
                file,
                relativePath: path ? `${path}/${entry.name}` : entry.name
              });
            }
          } else if (entry.kind === 'directory') {
            // Recursively scan subdirectories
            await scanDirectory(entry, path ? `${path}/${entry.name}` : entry.name);
          }
        }
      }

      await scanDirectory(dirHandle);

      if (imageFiles.length === 0) {
        alert('No image files found in the selected folder.');
        setProcessing(false);
        return;
      }

      const confirmed = window.confirm(
        `Found ${imageFiles.length} image(s) in "${dirHandle.name}".\n\nProceed with processing?`
      );

      if (!confirmed) {
        setProcessing(false);
        return;
      }

      // Process the images
      await processImageFiles(imageFiles, dirHandle.name);

    } catch (err) {
      // User cancelled or error occurred
      if (err.name !== 'AbortError') {
        console.error('Error selecting folder:', err);
        alert('Error accessing folder: ' + err.message);
      }
      setProcessing(false);
    }
  };

  const processImageFiles = async (imageFiles, folderName) => {
    try {
      // Upload and process each file
      const formData = new FormData();
      formData.append('folder_name', folderName);

      imageFiles.forEach((item) => {
        formData.append('files', item.file);
        formData.append('relative_paths', item.relativePath);
      });

      const response = await processingAPI.uploadAndProcess(formData);
      console.log('Processing complete:', response.data);

      alert(`Processing complete!\n\nScanned: ${response.data.scanned || imageFiles.length} images\nProcessed: ${response.data.processed || 0}`);
      window.location.reload();
    } catch (err) {
      console.error('Error processing images:', err);
      alert('Error processing images: ' + err.message);
    } finally {
      setProcessing(false);
    }
  };

  const handleClearAll = async () => {
    const confirmed = window.confirm(
      '⚠️ Are you sure you want to delete ALL images from the database?\n\nThis will remove all scanned images, EXIF data, AI analysis, and tags. This action cannot be undone!'
    );

    if (!confirmed) return;

    setProcessing(true);
    try {
      await processingAPI.clearAll();
      alert('All images cleared successfully!');
      window.location.reload();
    } catch (err) {
      console.error('Error clearing images:', err);
      alert('Error clearing images: ' + err.message);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>📷 Timeline AI</h1>
        <p>Interactive image timeline with AI analysis</p>
      </header>

      <div className="app-content">
        {/* Stats Bar */}
        {stats && (
          <div className="stats-bar">
            <div className="stat-item">
              <span className="stat-label">Total Images:</span>
              <span className="stat-value">{stats.total_images}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">With EXIF:</span>
              <span className="stat-value">{stats.with_exif}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Analyzed:</span>
              <span className="stat-value">{stats.with_analysis}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">With GPS:</span>
              <span className="stat-value">{stats.with_gps}</span>
            </div>
          </div>
        )}

        {/* Scan Control */}
        <div className="scan-control">
          {folderPath && (
            <div className="selected-folder">
              📁 Selected: <strong>{folderPath}</strong>
            </div>
          )}
          <button
            onClick={handleBrowseFolder}
            disabled={processing}
            className="browse-button-large"
            title="Browse and process folder"
          >
            {processing ? '⏳ Processing...' : '📁 Browse & Process Folder'}
          </button>
          <button
            onClick={handleClearAll}
            disabled={processing}
            className="clear-button"
            title="Delete all images from database"
          >
            🗑️ Clear All
          </button>
        </div>

        {/* Timeline */}
        <Timeline onItemSelect={handleItemSelect} filters={filters} />

        {/* Image Viewer Modal */}
        {selectedImage && (
          <ImageViewer
            imageId={selectedImage.id}
            onClose={handleCloseViewer}
          />
        )}
      </div>

      <footer className="app-footer">
        <p>
          Built with React + FastAPI + LLaVA | API: <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">Docs</a>
        </p>
      </footer>
    </div>
  );
}

export default App;
