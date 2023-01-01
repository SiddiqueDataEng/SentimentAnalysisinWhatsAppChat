import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

const Analysis = () => {
  const { id } = useParams();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalysis();
  }, [id]);

  const fetchAnalysis = async () => {
    try {
      const response = await fetch(`/api/chat/analyses/${id}/`);
      if (response.ok) {
        const data = await response.json();
        setAnalysis(data);
      } else {
        setError('Analysis not found');
      }
    } catch (err) {
      setError('Failed to load analysis');
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (label) => {
    switch (label) {
      case 'positive': return '#28a745';
      case 'negative': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const getSentimentEmoji = (label) => {
    switch (label) {
      case 'positive': return '😊';
      case 'negative': return '😔';
      default: return '😐';
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading analysis...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="error">
          <h2>Error</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return null;
  }

  return (
    <div className="analysis">
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">{analysis.title}</h1>
          <p className="card-subtitle">
            Analysis completed on {new Date(analysis.created_at).toLocaleDateString()}
          </p>
        </div>

        <div className="analysis-overview">
          <div className="stat-grid">
            <div className="stat-card">
              <div className="stat-value">{analysis.total_messages}</div>
              <div className="stat-label">Total Messages</div>
            </div>
            
            <div className="stat-card">
              <div className="stat-value">{analysis.total_participants}</div>
              <div className="stat-label">Participants</div>
            </div>
            
            <div className="stat-card">
              <div className="stat-value">
                {getSentimentEmoji(analysis.overall_sentiment_label)}
              </div>
              <div className="stat-label">Overall Sentiment</div>
              <div 
                className="stat-sublabel"
                style={{ color: getSentimentColor(analysis.overall_sentiment_label) }}
              >
                {analysis.overall_sentiment_label}
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-value">
                {analysis.processing_duration_seconds 
                  ? `${analysis.processing_duration_seconds.toFixed(1)}s`
                  : 'N/A'
                }
              </div>
              <div className="stat-label">Processing Time</div>
            </div>
          </div>
        </div>

        {analysis.overall_sentiment_score !== null && (
          <div className="sentiment-details">
            <h3>Sentiment Score</h3>
            <div className="sentiment-bar">
              <div className="sentiment-scale">
                <div className="scale-negative">Negative</div>
                <div className="scale-neutral">Neutral</div>
                <div className="scale-positive">Positive</div>
              </div>
              <div className="sentiment-indicator">
                <div 
                  className="sentiment-marker"
                  style={{ 
                    left: `${((analysis.overall_sentiment_score + 1) / 2) * 100}%`,
                    backgroundColor: getSentimentColor(analysis.overall_sentiment_label)
                  }}
                ></div>
              </div>
              <div className="sentiment-value">
                Score: {analysis.overall_sentiment_score.toFixed(3)}
              </div>
            </div>
          </div>
        )}

        {analysis.participants && analysis.participants.length > 0 && (
          <div className="participants-section">
            <h3>Participants</h3>
            <div className="participants-grid">
              {analysis.participants.map((participant, index) => (
                <div key={index} className="participant-card">
                  <div className="participant-name">{participant.anonymized_name}</div>
                  <div className="participant-stats">
                    <div>Messages: {participant.message_count}</div>
                    <div>Words: {participant.word_count}</div>
                    {participant.avg_sentiment_score && (
                      <div 
                        style={{ color: getSentimentColor(
                          participant.avg_sentiment_score > 0.1 ? 'positive' :
                          participant.avg_sentiment_score < -0.1 ? 'negative' : 'neutral'
                        )}}
                      >
                        Avg Sentiment: {participant.avg_sentiment_score.toFixed(2)}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="analysis-metadata">
          <h3>Analysis Details</h3>
          <div className="metadata-grid">
            <div>
              <strong>Language:</strong> {analysis.detected_language || 'Unknown'}
            </div>
            <div>
              <strong>Date Range:</strong> 
              {analysis.date_range_start && analysis.date_range_end ? (
                ` ${new Date(analysis.date_range_start).toLocaleDateString()} - ${new Date(analysis.date_range_end).toLocaleDateString()}`
              ) : (
                ' Not available'
              )}
            </div>
            <div>
              <strong>Status:</strong> {analysis.status}
            </div>
            {analysis.dominant_emotion && (
              <div>
                <strong>Dominant Emotion:</strong> {analysis.dominant_emotion}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analysis;