import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div className="home">
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">Welcome to WhatsApp Sentiment Analysis</h1>
          <p className="card-subtitle">
            Analyze emotions and sentiments in your WhatsApp conversations with advanced AI
          </p>
        </div>
        
        <div className="features">
          <div className="feature-grid">
            <div className="feature-card">
              <h3>🎯 Multi-Model Analysis</h3>
              <p>Uses VADER, TextBlob, and RoBERTa for comprehensive sentiment analysis</p>
            </div>
            
            <div className="feature-card">
              <h3>😊 Emotion Detection</h3>
              <p>Identifies 6 basic emotions: joy, sadness, anger, fear, surprise, disgust</p>
            </div>
            
            <div className="feature-card">
              <h3>🌍 Multi-Language</h3>
              <p>Supports English, Hindi, and Hinglish conversations</p>
            </div>
            
            <div className="feature-card">
              <h3>🔒 Privacy First</h3>
              <p>Participant names are anonymized by default for privacy protection</p>
            </div>
            
            <div className="feature-card">
              <h3>📊 Rich Analytics</h3>
              <p>Interactive charts, trends, and detailed participant analysis</p>
            </div>
            
            <div className="feature-card">
              <h3>⚡ Fast Processing</h3>
              <p>Efficient batch processing with real-time progress updates</p>
            </div>
          </div>
        </div>
        
        <div className="cta-section">
          <h2>Ready to analyze your WhatsApp chats?</h2>
          <p>Upload your exported WhatsApp chat file and get detailed sentiment insights</p>
          <Link to="/upload" className="btn btn-primary">
            Start Analysis
          </Link>
        </div>
      </div>
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">How It Works</h2>
        </div>
        
        <div className="steps">
          <div className="step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Export Your Chat</h3>
              <p>Export your WhatsApp chat as a text file from your phone</p>
            </div>
          </div>
          
          <div className="step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>Upload & Process</h3>
              <p>Upload the file and let our AI analyze the sentiments and emotions</p>
            </div>
          </div>
          
          <div className="step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Explore Results</h3>
              <p>View detailed analytics, trends, and insights about your conversations</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;