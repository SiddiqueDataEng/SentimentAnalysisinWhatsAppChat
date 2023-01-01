import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const fetchAnalyses = async () => {
    try {
      const response = await fetch('/api/chat/analyses/');
      if (response.ok) {
        const data = await response.json();
        setAnalyses(data.results || data);
      } else {
        setError('Failed to load analyses');
      }
    } catch (err) {
      setError('Failed to load analyses');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusColors = {
      completed: '#28a745',
      processing: '#ffc107',
      pending: '#17a2b8',
      failed: '#dc3545'
    };

    return (
      <span 
        className="status-badge"
        style={{ 
          backgroundColor: statusColors[status] || '#6c757d',
          color: 'white',
          padding: '0.25rem 0.5rem',
          borderRadius: '0.25rem',
          fontSize: '0.75rem'
        }}
      >
        {status}
      </span>
    );
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
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">Your Analyses</h1>
          <p className="card-subtitle">
            Manage and view your WhatsApp chat sentiment analyses
          </p>
        </div>

        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}

        {analyses.length === 0 ? (
          <div className="empty-state">
            <h3>No analyses yet</h3>
            <p>Upload your first WhatsApp chat to get started!</p>
            <Link to="/upload" className="btn btn-primary">
              Upload Chat
            </Link>
          </div>
        ) : (
          <div className="analyses-list">
            {analyses.map((analysis) => (
              <div key={analysis.id} className="analysis-item">
                <div className="analysis-header">
                  <h3 className="analysis-title">
                    <Link to={`/analysis/${analysis.id}`}>
                      {analysis.title}
                    </Link>
                  </h3>
                  {getStatusBadge(analysis.status)}
                </div>
                
                <div className="analysis-meta">
                  <span>📅 {new Date(analysis.created_at).toLocaleDateString()}</span>
                  <span>💬 {analysis.total_messages} messages</span>
                  <span>👥 {analysis.total_participants} participants</span>
                  {analysis.detected_language && (
                    <span>🌍 {analysis.detected_language}</span>
                  )}
                </div>

                {analysis.status === 'completed' && (
                  <div className="analysis-results">
                    <div className="sentiment-summary">
                      <span className="sentiment-indicator">
                        {getSentimentEmoji(analysis.overall_sentiment_label)}
                        <span className="sentiment-label">
                          {analysis.overall_sentiment_label}
                        </span>
                      </span>
                      {analysis.overall_sentiment_score && (
                        <span className="sentiment-score">
                          Score: {analysis.overall_sentiment_score.toFixed(2)}
                        </span>
                      )}
                    </div>
                    
                    {analysis.dominant_emotion && (
                      <div className="emotion-summary">
                        <span>Dominant emotion: {analysis.dominant_emotion}</span>
                      </div>
                    )}
                  </div>
                )}

                {analysis.status === 'processing' && (
                  <div className="processing-indicator">
                    <div className="spinner"></div>
                    <span>Processing...</span>
                  </div>
                )}

                {analysis.status === 'failed' && analysis.error_message && (
                  <div className="error-summary">
                    <span>❌ {analysis.error_message}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;