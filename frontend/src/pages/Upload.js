import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Upload = () => {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [anonymize, setAnonymize] = useState(true);
  const [loading, setLoading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const navigate = useNavigate();

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.type === 'text/plain') {
      setFile(selectedFile);
      if (!title) {
        setTitle(selectedFile.name.replace('.txt', ''));
      }
    } else {
      alert('Please select a valid .txt file');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    handleFileSelect(droppedFile);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      alert('Please select a file');
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('anonymize_participants', anonymize);

    try {
      const response = await fetch('/api/chat/analyses/', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        navigate(`/analysis/${result.id}`);
      } else {
        const error = await response.json();
        alert(`Upload failed: ${error.error || 'Unknown error'}`);
      }
    } catch (error) {
      alert(`Upload failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload">
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">Upload WhatsApp Chat</h1>
          <p className="card-subtitle">
            Upload your exported WhatsApp chat file for sentiment analysis
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="title">Analysis Title</label>
            <input
              type="text"
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter a title for this analysis"
              required
            />
          </div>

          <div className="form-group">
            <label>Chat File</label>
            <div
              className={`upload-area ${dragOver ? 'dragover' : ''}`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => document.getElementById('file-input').click()}
            >
              {file ? (
                <div>
                  <p>📄 {file.name}</p>
                  <p>Size: {(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              ) : (
                <div>
                  <p>📁 Drop your WhatsApp chat file here or click to browse</p>
                  <p>Supported format: .txt files only</p>
                </div>
              )}
            </div>
            <input
              type="file"
              id="file-input"
              accept=".txt"
              onChange={(e) => handleFileSelect(e.target.files[0])}
              style={{ display: 'none' }}
            />
          </div>

          <div className="form-group">
            <label>
              <input
                type="checkbox"
                checked={anonymize}
                onChange={(e) => setAnonymize(e.target.checked)}
              />
              Anonymize participant names (recommended for privacy)
            </label>
          </div>

          <div className="form-actions">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={!file || loading}
            >
              {loading ? (
                <span>
                  <div className="spinner"></div>
                  Processing...
                </span>
              ) : (
                'Start Analysis'
              )}
            </button>
          </div>
        </form>

        <div className="help-section">
          <h3>How to export WhatsApp chat:</h3>
          <ol>
            <li>Open WhatsApp and go to the chat you want to analyze</li>
            <li>Tap on the chat name at the top</li>
            <li>Scroll down and tap "Export Chat"</li>
            <li>Choose "Without Media" for faster processing</li>
            <li>Save the file and upload it here</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default Upload;