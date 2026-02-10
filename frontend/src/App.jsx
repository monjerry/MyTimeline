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

  const handleScanFolder = async () => {
    if (!folderPath.trim()) {
      alert('Please enter a folder path');
      return;
    }

    setProcessing(true);
    try {
      const scanResponse = await processingAPI.scan(folderPath, true);
      console.log('Scan results:', scanResponse.data);

      // Extract EXIF
      const exifResponse = await processingAPI.extractExif();
      console.log('EXIF extraction:', exifResponse.data);

      // Analyze images
      const analyzeResponse = await processingAPI.analyze();
      console.log('Analysis results:', analyzeResponse.data);

      alert('Processing complete! Refresh to see results.');
      window.location.reload();
    } catch (err) {
      console.error('Error processing:', err);
      alert('Error processing images: ' + err.message);
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
          <input
            type="text"
            placeholder="Enter folder path (e.g., /Users/username/Pictures)"
            value={folderPath}
            onChange={(e) => setFolderPath(e.target.value)}
            className="folder-input"
            disabled={processing}
          />
          <button
            onClick={handleScanFolder}
            disabled={processing || !folderPath.trim()}
            className="scan-button"
          >
            {processing ? 'Processing...' : 'Scan & Process'}
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
