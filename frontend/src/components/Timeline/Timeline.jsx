/**
 * Timeline component using Vis.js
 */
import { useEffect, useRef, useState } from 'react';
import { Timeline as VisTimeline } from 'vis-timeline/standalone';
import 'vis-timeline/styles/vis-timeline-graph2d.css';
import { timelineAPI, imagesAPI } from '../../services/api';
import './Timeline.css';

export default function Timeline({ onItemSelect, filters }) {
  const timelineRef = useRef(null);
  const visTimelineRef = useRef(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch timeline data
  useEffect(() => {
    const fetchTimelineData = async () => {
      try {
        setLoading(true);
        setError(null);

        const params = {};
        if (filters?.dateFrom) params.date_from = filters.dateFrom;
        if (filters?.dateTo) params.date_to = filters.dateTo;
        if (filters?.tags && filters.tags.length > 0) {
          params.tags = filters.tags.join(',');
        }

        const response = await timelineAPI.getTimeline(params);
        setItems(response.data.items);
      } catch (err) {
        console.error('Error fetching timeline data:', err);
        setError('Failed to load timeline data');
      } finally {
        setLoading(false);
      }
    };

    fetchTimelineData();
  }, [filters]);

  // Initialize Vis Timeline
  useEffect(() => {
    if (!timelineRef.current || items.length === 0) return;

    // Timeline options
    const options = {
      width: '100%',
      height: '600px',
      margin: {
        item: 20,
      },
      zoomMin: 1000 * 60 * 60 * 24, // 1 day
      zoomMax: 1000 * 60 * 60 * 24 * 365 * 10, // 10 years
      orientation: 'top',
      showCurrentTime: false,
      stack: true,
      cluster: {
        maxItems: 5,
        showStipes: true,
      },
    };

    // Create timeline instance
    if (!visTimelineRef.current) {
      visTimelineRef.current = new VisTimeline(
        timelineRef.current,
        items,
        options
      );

      // Add click event listener
      visTimelineRef.current.on('select', (properties) => {
        if (properties.items.length > 0) {
          const itemId = properties.items[0];
          const item = items.find((i) => i.id === itemId);
          if (item && onItemSelect) {
            onItemSelect(item);
          }
        }
      });
    } else {
      // Update existing timeline
      visTimelineRef.current.setItems(items);
    }

    return () => {
      if (visTimelineRef.current) {
        visTimelineRef.current.destroy();
        visTimelineRef.current = null;
      }
    };
  }, [items, onItemSelect]);

  if (loading) {
    return (
      <div className="timeline-loading">
        <div className="spinner"></div>
        <p>Loading timeline...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="timeline-error">
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="timeline-empty">
        <p>No images found. Try adjusting your filters or scan a folder.</p>
      </div>
    );
  }

  return (
    <div className="timeline-container">
      <div className="timeline-stats">
        <span>{items.length} images</span>
      </div>
      <div ref={timelineRef} className="timeline"></div>
    </div>
  );
}
