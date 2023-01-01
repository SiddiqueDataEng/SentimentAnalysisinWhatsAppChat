#!/usr/bin/env python3
"""
Standalone Demo Version of WhatsApp Sentiment Analysis
Works without complex dependencies - just basic Python libraries
"""

import os
import sys
import re
import json
from datetime import datetime
from collections import Counter, defaultdict
import hashlib
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
import threading
import time

# Simple sentiment analysis without external dependencies
class SimpleSentimentAnalyzer:
    def __init__(self):
        # Basic positive and negative words
        self.positive_words = {
            'love', 'like', 'good', 'great', 'awesome', 'amazing', 'wonderful', 
            'excellent', 'fantastic', 'perfect', 'happy', 'joy', 'smile', 'laugh',
            'best', 'nice', 'cool', 'fun', 'enjoy', 'pleased', 'glad', 'excited',
            'beautiful', 'brilliant', 'superb', 'outstanding', 'marvelous'
        }
        
        self.negative_words = {
            'hate', 'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'worst',
            'sad', 'angry', 'mad', 'upset', 'disappointed', 'frustrated', 'annoyed',
            'stupid', 'dumb', 'ugly', 'boring', 'sucks', 'pathetic', 'useless',
            'wrong', 'problem', 'issue', 'trouble', 'difficult', 'hard'
        }
        
        # Emoji sentiment mapping
        self.positive_emojis = {'😊', '😀', '😃', '😄', '😁', '😆', '😂', '🤣', '😍', '🥰', '😘', '💕', '❤️', '💖', '👍', '👌', '🎉', '🎊', '✨', '🌟'}
        self.negative_emojis = {'😢', '😭', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣', '😖', '😫', '😩', '😤', '😠', '😡', '🤬', '💔', '👎', '😰', '😨'}
    
    def analyze_text(self, text):
        if not text:
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        # Check emojis
        for emoji in self.positive_emojis:
            positive_count += text.count(emoji)
        for emoji in self.negative_emojis:
            negative_count += text.count(emoji)
        
        # Calculate score
        total_words = len(words) + positive_count + negative_count
        if total_words == 0:
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}
        
        score = (positive_count - negative_count) / max(total_words, 1)
        
        # Determine label
        if score > 0.1:
            label = 'positive'
        elif score < -0.1:
            label = 'negative'
        else:
            label = 'neutral'
        
        confidence = min(abs(score) * 2, 1.0)
        
        return {
            'score': score,
            'label': label,
            'confidence': confidence
        }

class WhatsAppChatProcessor:
    def __init__(self):
        self.analyzer = SimpleSentimentAnalyzer()
    
    def parse_whatsapp_chat(self, content):
        """Parse WhatsApp chat export"""
        lines = content.strip().split('\n')
        messages = []
        
        # Pattern for WhatsApp messages
        pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}),?\s(\d{1,2}:\d{2})\s?-\s([^:]+):\s(.+)'
        
        for line in lines:
            match = re.match(pattern, line)
            if match:
                date_str, time_str, username, message = match.groups()
                
                try:
                    # Parse datetime
                    datetime_str = f"{date_str} {time_str}"
                    timestamp = datetime.strptime(datetime_str, '%m/%d/%Y %H:%M')
                except:
                    try:
                        timestamp = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M')
                    except:
                        timestamp = datetime.now()
                
                # Clean username and message
                username = username.strip()
                message = message.strip()
                
                # Skip system messages
                if 'Messages and calls are end-to-end encrypted' in message:
                    continue
                if '<Media omitted>' in message:
                    continue
                
                messages.append({
                    'timestamp': timestamp,
                    'username': username,
                    'message': message,
                    'hour': timestamp.hour,
                    'day_of_week': timestamp.weekday()
                })
        
        return messages
    
    def analyze_chat(self, content, anonymize=True):
        """Analyze WhatsApp chat"""
        messages = self.parse_whatsapp_chat(content)
        
        if not messages:
            return {'error': 'No valid messages found in the chat file'}
        
        # Anonymize participants
        participants = list(set(msg['username'] for msg in messages))
        if anonymize:
            participant_map = {name: f"User_{i+1:02d}" for i, name in enumerate(sorted(participants))}
        else:
            participant_map = {name: name for name in participants}
        
        # Analyze sentiment for each message
        analyzed_messages = []
        sentiment_scores = []
        
        for msg in messages:
            sentiment = self.analyzer.analyze_text(msg['message'])
            
            analyzed_msg = {
                **msg,
                'participant': participant_map[msg['username']],
                'sentiment_score': sentiment['score'],
                'sentiment_label': sentiment['label'],
                'sentiment_confidence': sentiment['confidence'],
                'word_count': len(msg['message'].split())
            }
            
            analyzed_messages.append(analyzed_msg)
            if sentiment['score'] is not None:
                sentiment_scores.append(sentiment['score'])
        
        # Calculate overall statistics
        overall_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        if overall_sentiment > 0.1:
            overall_label = 'positive'
        elif overall_sentiment < -0.1:
            overall_label = 'negative'
        else:
            overall_label = 'neutral'
        
        # Participant statistics
        participant_stats = defaultdict(lambda: {
            'message_count': 0,
            'word_count': 0,
            'sentiment_scores': []
        })
        
        for msg in analyzed_messages:
            participant = msg['participant']
            participant_stats[participant]['message_count'] += 1
            participant_stats[participant]['word_count'] += msg['word_count']
            if msg['sentiment_score'] is not None:
                participant_stats[participant]['sentiment_scores'].append(msg['sentiment_score'])
        
        # Calculate participant averages
        for participant, stats in participant_stats.items():
            if stats['sentiment_scores']:
                stats['avg_sentiment'] = sum(stats['sentiment_scores']) / len(stats['sentiment_scores'])
            else:
                stats['avg_sentiment'] = 0.0
        
        return {
            'success': True,
            'total_messages': len(analyzed_messages),
            'total_participants': len(participants),
            'date_range': {
                'start': min(msg['timestamp'] for msg in analyzed_messages),
                'end': max(msg['timestamp'] for msg in analyzed_messages)
            },
            'overall_sentiment': {
                'score': overall_sentiment,
                'label': overall_label
            },
            'messages': analyzed_messages,
            'participants': dict(participant_stats),
            'sentiment_distribution': Counter(msg['sentiment_label'] for msg in analyzed_messages)
        }

class DemoWebServer:
    def __init__(self, processor):
        self.processor = processor
        self.results = {}
    
    def create_html_interface(self):
        """Create HTML interface"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp Sentiment Analysis - Demo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #25d366, #128c7e); 
            color: white; 
            padding: 2rem; 
            text-align: center; 
        }
        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .header p { font-size: 1.1rem; opacity: 0.9; }
        .content { padding: 2rem; }
        .upload-area { 
            border: 3px dashed #ddd; 
            border-radius: 15px; 
            padding: 3rem; 
            text-align: center; 
            margin: 2rem 0;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .upload-area:hover { 
            border-color: #25d366; 
            background: #f0fff4; 
        }
        .upload-area.dragover { 
            border-color: #25d366; 
            background: #f0fff4; 
            transform: scale(1.02);
        }
        .btn { 
            background: #25d366; 
            color: white; 
            border: none; 
            padding: 1rem 2rem; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        .btn:hover { 
            background: #128c7e; 
            transform: translateY(-2px);
        }
        .results { 
            margin-top: 2rem; 
            padding: 2rem; 
            background: #f8f9fa; 
            border-radius: 10px; 
        }
        .stat-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 1rem; 
            margin: 1rem 0; 
        }
        .stat-card { 
            background: white; 
            padding: 1.5rem; 
            border-radius: 10px; 
            text-align: center; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .stat-value { 
            font-size: 2rem; 
            font-weight: bold; 
            color: #25d366; 
        }
        .stat-label { 
            color: #666; 
            margin-top: 0.5rem; 
        }
        .sentiment-positive { color: #28a745; }
        .sentiment-negative { color: #dc3545; }
        .sentiment-neutral { color: #6c757d; }
        .participants { 
            margin-top: 2rem; 
        }
        .participant-card { 
            background: white; 
            padding: 1rem; 
            margin: 0.5rem 0; 
            border-radius: 8px; 
            border-left: 4px solid #25d366;
        }
        .loading { 
            text-align: center; 
            padding: 2rem; 
        }
        .spinner { 
            border: 4px solid #f3f3f3; 
            border-top: 4px solid #25d366; 
            border-radius: 50%; 
            width: 40px; 
            height: 40px; 
            animation: spin 1s linear infinite; 
            margin: 0 auto;
        }
        @keyframes spin { 
            0% { transform: rotate(0deg); } 
            100% { transform: rotate(360deg); } 
        }
        .instructions {
            background: #e3f2fd;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        .instructions h3 {
            color: #1976d2;
            margin-bottom: 1rem;
        }
        .instructions ol {
            padding-left: 1.5rem;
        }
        .instructions li {
            margin-bottom: 0.5rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📱 WhatsApp Sentiment Analysis</h1>
            <p>Analyze emotions and sentiments in your WhatsApp conversations</p>
        </div>
        
        <div class="content">
            <div class="instructions">
                <h3>How to export your WhatsApp chat:</h3>
                <ol>
                    <li>Open WhatsApp and go to the chat you want to analyze</li>
                    <li>Tap on the chat name at the top</li>
                    <li>Scroll down and tap "Export Chat"</li>
                    <li>Choose "Without Media" for faster processing</li>
                    <li>Save the file and upload it below</li>
                </ol>
            </div>
            
            <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
                <div id="uploadContent">
                    <h3>📁 Drop your WhatsApp chat file here</h3>
                    <p>Or click to browse for a .txt file</p>
                    <input type="file" id="fileInput" accept=".txt" style="display: none;">
                </div>
            </div>
            
            <div style="text-align: center; margin: 1rem 0;">
                <label>
                    <input type="checkbox" id="anonymize" checked> 
                    Anonymize participant names (recommended)
                </label>
            </div>
            
            <div style="text-align: center;">
                <button class="btn" onclick="analyzeChat()" id="analyzeBtn">
                    🚀 Analyze Chat
                </button>
            </div>
            
            <div id="results" style="display: none;"></div>
        </div>
    </div>

    <script>
        let selectedFile = null;
        
        // File upload handling
        document.getElementById('fileInput').addEventListener('change', function(e) {
            selectedFile = e.target.files[0];
            if (selectedFile) {
                document.getElementById('uploadContent').innerHTML = 
                    `<h3>📄 ${selectedFile.name}</h3><p>Size: ${(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>`;
            }
        });
        
        // Drag and drop
        const uploadArea = document.getElementById('uploadArea');
        
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                selectedFile = files[0];
                document.getElementById('uploadContent').innerHTML = 
                    `<h3>📄 ${selectedFile.name}</h3><p>Size: ${(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>`;
            }
        });
        
        function analyzeChat() {
            if (!selectedFile) {
                alert('Please select a WhatsApp chat file first!');
                return;
            }
            
            const analyzeBtn = document.getElementById('analyzeBtn');
            const resultsDiv = document.getElementById('results');
            
            analyzeBtn.innerHTML = '<div class="spinner"></div> Analyzing...';
            analyzeBtn.disabled = true;
            
            const reader = new FileReader();
            reader.onload = function(e) {
                const content = e.target.result;
                const anonymize = document.getElementById('anonymize').checked;
                
                // Simulate processing (in real app, this would be sent to backend)
                setTimeout(() => {
                    const results = processChat(content, anonymize);
                    displayResults(results);
                    
                    analyzeBtn.innerHTML = '🚀 Analyze Chat';
                    analyzeBtn.disabled = false;
                }, 2000);
            };
            
            reader.readAsText(selectedFile);
        }
        
        function processChat(content, anonymize) {
            // This is a simplified client-side processing
            // In the real app, this would be done on the backend
            const lines = content.split('\\n');
            const messages = [];
            const participants = new Set();
            
            const pattern = /(\d{1,2}\/\d{1,2}\/\d{2,4}),?\s(\d{1,2}:\d{2})\s?-\s([^:]+):\s(.+)/;
            
            for (const line of lines) {
                const match = line.match(pattern);
                if (match) {
                    const [, date, time, username, message] = match;
                    
                    if (message.includes('Messages and calls are end-to-end encrypted') ||
                        message.includes('<Media omitted>')) {
                        continue;
                    }
                    
                    participants.add(username.trim());
                    messages.push({
                        username: username.trim(),
                        message: message.trim(),
                        timestamp: new Date(`${date} ${time}`)
                    });
                }
            }
            
            // Simple sentiment analysis
            const positiveWords = ['love', 'like', 'good', 'great', 'awesome', 'happy', 'joy', 'smile', 'laugh', 'best', 'nice', 'cool', 'fun'];
            const negativeWords = ['hate', 'bad', 'terrible', 'awful', 'sad', 'angry', 'mad', 'upset', 'stupid', 'boring', 'worst'];
            
            let totalSentiment = 0;
            let sentimentCount = 0;
            const sentimentDistribution = { positive: 0, negative: 0, neutral: 0 };
            
            messages.forEach(msg => {
                const words = msg.message.toLowerCase().split(/\s+/);
                const positiveCount = words.filter(word => positiveWords.includes(word)).length;
                const negativeCount = words.filter(word => negativeWords.includes(word)).length;
                
                let sentiment = 0;
                if (positiveCount > negativeCount) {
                    sentiment = 0.5;
                    sentimentDistribution.positive++;
                } else if (negativeCount > positiveCount) {
                    sentiment = -0.5;
                    sentimentDistribution.negative++;
                } else {
                    sentimentDistribution.neutral++;
                }
                
                totalSentiment += sentiment;
                sentimentCount++;
                msg.sentiment = sentiment;
            });
            
            const overallSentiment = sentimentCount > 0 ? totalSentiment / sentimentCount : 0;
            let overallLabel = 'neutral';
            if (overallSentiment > 0.1) overallLabel = 'positive';
            else if (overallSentiment < -0.1) overallLabel = 'negative';
            
            // Participant stats
            const participantStats = {};
            Array.from(participants).forEach((participant, index) => {
                const participantMessages = messages.filter(msg => msg.username === participant);
                const participantSentiments = participantMessages.map(msg => msg.sentiment || 0);
                const avgSentiment = participantSentiments.length > 0 ? 
                    participantSentiments.reduce((a, b) => a + b, 0) / participantSentiments.length : 0;
                
                participantStats[anonymize ? `User_${String(index + 1).padStart(2, '0')}` : participant] = {
                    message_count: participantMessages.length,
                    avg_sentiment: avgSentiment,
                    word_count: participantMessages.reduce((total, msg) => total + msg.message.split(' ').length, 0)
                };
            });
            
            return {
                success: true,
                total_messages: messages.length,
                total_participants: participants.size,
                overall_sentiment: {
                    score: overallSentiment,
                    label: overallLabel
                },
                sentiment_distribution: sentimentDistribution,
                participants: participantStats,
                date_range: {
                    start: messages.length > 0 ? Math.min(...messages.map(m => m.timestamp)) : null,
                    end: messages.length > 0 ? Math.max(...messages.map(m => m.timestamp)) : null
                }
            };
        }
        
        function displayResults(results) {
            if (!results.success) {
                document.getElementById('results').innerHTML = 
                    `<div class="results"><h2>❌ Error</h2><p>${results.error || 'Failed to analyze chat'}</p></div>`;
                document.getElementById('results').style.display = 'block';
                return;
            }
            
            const getSentimentEmoji = (label) => {
                switch(label) {
                    case 'positive': return '😊';
                    case 'negative': return '😔';
                    default: return '😐';
                }
            };
            
            const getSentimentClass = (score) => {
                if (score > 0.1) return 'sentiment-positive';
                if (score < -0.1) return 'sentiment-negative';
                return 'sentiment-neutral';
            };
            
            let participantsHtml = '';
            Object.entries(results.participants).forEach(([name, stats]) => {
                participantsHtml += `
                    <div class="participant-card">
                        <strong>${name}</strong><br>
                        Messages: ${stats.message_count} | Words: ${stats.word_count}<br>
                        <span class="${getSentimentClass(stats.avg_sentiment)}">
                            Avg Sentiment: ${stats.avg_sentiment.toFixed(2)}
                        </span>
                    </div>
                `;
            });
            
            const resultsHtml = `
                <div class="results">
                    <h2>📊 Analysis Results</h2>
                    
                    <div class="stat-grid">
                        <div class="stat-card">
                            <div class="stat-value">${results.total_messages}</div>
                            <div class="stat-label">Total Messages</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${results.total_participants}</div>
                            <div class="stat-label">Participants</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${getSentimentEmoji(results.overall_sentiment.label)}</div>
                            <div class="stat-label">Overall Sentiment</div>
                            <div class="${getSentimentClass(results.overall_sentiment.score)}">
                                ${results.overall_sentiment.label}
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${results.overall_sentiment.score.toFixed(2)}</div>
                            <div class="stat-label">Sentiment Score</div>
                        </div>
                    </div>
                    
                    <h3>📈 Sentiment Distribution</h3>
                    <div class="stat-grid">
                        <div class="stat-card">
                            <div class="stat-value sentiment-positive">${results.sentiment_distribution.positive}</div>
                            <div class="stat-label">Positive Messages</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value sentiment-neutral">${results.sentiment_distribution.neutral}</div>
                            <div class="stat-label">Neutral Messages</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value sentiment-negative">${results.sentiment_distribution.negative}</div>
                            <div class="stat-label">Negative Messages</div>
                        </div>
                    </div>
                    
                    <div class="participants">
                        <h3>👥 Participants</h3>
                        ${participantsHtml}
                    </div>
                </div>
            `;
            
            document.getElementById('results').innerHTML = resultsHtml;
            document.getElementById('results').style.display = 'block';
            
            // Scroll to results
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>
        """
        return html
    
    def save_html_file(self):
        """Save HTML interface to file"""
        html_content = self.create_html_interface()
        with open('whatsapp_sentiment_demo.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        return 'whatsapp_sentiment_demo.html'

def main():
    """Main function to run the demo"""
    print("🚀 Starting WhatsApp Sentiment Analysis Demo...")
    print("=" * 60)
    
    # Create processor and web server
    processor = WhatsAppChatProcessor()
    web_server = DemoWebServer(processor)
    
    # Create HTML file
    html_file = web_server.save_html_file()
    html_path = os.path.abspath(html_file)
    
    print(f"✅ Demo interface created: {html_file}")
    print(f"📁 Full path: {html_path}")
    print()
    print("🌐 Opening demo in your web browser...")
    print()
    print("📋 How to use:")
    print("1. Export your WhatsApp chat as a .txt file")
    print("2. Upload the file in the web interface")
    print("3. Click 'Analyze Chat' to see results")
    print()
    print("✨ Features included:")
    print("• Sentiment analysis (positive/negative/neutral)")
    print("• Participant statistics")
    print("• Message count and word analysis")
    print("• Privacy protection (anonymization)")
    print("• Interactive web interface")
    print()
    
    # Open in browser
    try:
        webbrowser.open(f'file://{html_path}')
        print("🎉 Demo is now running in your browser!")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print(f"📖 Please open this file manually: {html_path}")
    
    print()
    print("🔧 This is a simplified demo version.")
    print("📚 For the full production system with Django + React:")
    print("   1. Install Docker Desktop")
    print("   2. Run: docker-compose up -d")
    print("   3. Access: http://localhost:3000")
    print()
    print("Press Ctrl+C to exit...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Demo stopped. Thank you for trying WhatsApp Sentiment Analysis!")

if __name__ == "__main__":
    main()