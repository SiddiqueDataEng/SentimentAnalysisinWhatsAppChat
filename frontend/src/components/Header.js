import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          📱 WhatsApp Sentiment Analysis
        </div>
        <nav className="nav">
          <Link to="/">Home</Link>
          <Link to="/upload">Upload Chat</Link>
          <Link to="/dashboard">Dashboard</Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;