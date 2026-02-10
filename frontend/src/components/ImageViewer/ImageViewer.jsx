/**
 * Image Viewer Modal Component
 */
import { useState, useEffect } from 'react';
import { imagesAPI } from '../../services/api';
import './ImageViewer.css';

export default function ImageViewer({ imageId, onClose }) {
  const [imageData, setImageData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchImageData = async () => {
      try {
        setLoading(true);
        const response = await imagesAPI.get(imageId);
        setImageData(response.data);
      } catch (err) {
        console.error('Error fetching image:', err);
        setError('Failed to load image details');
      } finally {
        setLoading(false);
      }
    };

    if (imageId) {
      fetchImageData();
    }
  }, [imageId]);

  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  if (loading) {
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <div className="loading">Loading...</div>
        </div>
      </div>
    );
  }

  if (error || !imageData) {
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <div className="error">{error || 'Image not found'}</div>
          <button onClick={onClose} className="close-button">Close</button>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button onClick={onClose} className="close-button">✕</button>

        <div className="viewer-layout">
          {/* Image */}
          <div className="image-section">
            <img
              src={imagesAPI.getOriginal(imageId)}
              alt={imageData.file_name}
              className="full-image"
            />
          </div>

          {/* Metadata */}
          <div className="metadata-section">
            <h2>{imageData.file_name}</h2>

            {/* EXIF Data */}
            {imageData.exif && (
              <div className="metadata-group">
                <h3>📷 Camera Info</h3>
                {imageData.exif.date_taken && (
                  <p><strong>Date:</strong> {new Date(imageData.exif.date_taken).toLocaleString()}</p>
                )}
                {imageData.exif.camera_make && (
                  <p><strong>Camera:</strong> {imageData.exif.camera_make} {imageData.exif.camera_model}</p>
                )}
                {imageData.exif.lens_model && (
                  <p><strong>Lens:</strong> {imageData.exif.lens_model}</p>
                )}
                {imageData.exif.iso && (
                  <p><strong>ISO:</strong> {imageData.exif.iso}</p>
                )}
                {imageData.exif.aperture && (
                  <p><strong>Aperture:</strong> f/{imageData.exif.aperture.toFixed(1)}</p>
                )}
                {imageData.exif.shutter_speed && (
                  <p><strong>Shutter:</strong> {imageData.exif.shutter_speed}s</p>
                )}
                {imageData.exif.focal_length && (
                  <p><strong>Focal Length:</strong> {imageData.exif.focal_length}mm</p>
                )}
                {(imageData.exif.gps_latitude && imageData.exif.gps_longitude) && (
                  <p>
                    <strong>Location:</strong>{' '}
                    <a
                      href={`https://www.google.com/maps?q=${imageData.exif.gps_latitude},${imageData.exif.gps_longitude}`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {imageData.exif.gps_latitude.toFixed(6)}, {imageData.exif.gps_longitude.toFixed(6)}
                    </a>
                  </p>
                )}
              </div>
            )}

            {/* AI Analysis */}
            {imageData.analysis && (
              <div className="metadata-group">
                <h3>🤖 AI Analysis</h3>
                {imageData.analysis.description && (
                  <p><strong>Description:</strong> {imageData.analysis.description}</p>
                )}
                {imageData.analysis.scene_type && (
                  <p><strong>Scene:</strong> {imageData.analysis.scene_type}</p>
                )}
              </div>
            )}

            {/* Tags */}
            {imageData.tags && imageData.tags.length > 0 && (
              <div className="metadata-group">
                <h3>🏷️ Tags</h3>
                <div className="tags">
                  {imageData.tags.map((tag, index) => (
                    <span key={index} className={`tag tag-${tag.type}`}>
                      {tag.name}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
