# 🚀 WhatsApp Sentiment Analysis - Deployment Guide

## 📋 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 16+ (for frontend development)
- PostgreSQL 15+ (for production)
- Redis 7+ (for caching and task queue)

### 🐳 Docker Deployment (Recommended)

1. **Clone and Setup Environment**
   ```bash
   cd SentimentAnalysisinWhatsAppChat
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start All Services**
   ```bash
   docker-compose up -d
   ```

3. **Initialize Database**
   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py createsuperuser
   ```

4. **Access Services**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000/api/
   - **Admin Panel**: http://localhost:8000/admin/
   - **Health Check**: http://localhost:8000/health/

### 🔧 Manual Development Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup database
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic

# Start development server
python manage.py runserver
```

#### Start Celery Workers
```bash
# In separate terminals
celery -A core worker -l info
celery -A core beat -l info
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 🏗️ Architecture Overview

### Backend Services
- **Django REST API**: Main application server
- **PostgreSQL**: Primary database
- **Redis**: Caching and message broker
- **Celery**: Asynchronous task processing
- **Nginx**: Reverse proxy (production)

### Key Features Implemented

#### 🔬 Advanced ML Pipeline
- **Multiple Sentiment Models**: VADER, TextBlob, RoBERTa
- **Emotion Detection**: 6 basic emotions (joy, sadness, anger, fear, surprise, disgust)
- **Toxicity Detection**: Harmful content identification
- **Language Detection**: English, Hindi, Hinglish support
- **Ensemble Analysis**: Combines multiple models for better accuracy

#### 📊 Production Features
- **Async Processing**: Large chat files processed in background
- **Batch Analysis**: Efficient processing of thousands of messages
- **Real-time Progress**: WebSocket updates during processing
- **Caching**: Redis-based caching for performance
- **Rate Limiting**: API abuse prevention
- **User Authentication**: JWT-based secure authentication

#### 🎨 Enhanced Analytics
- **Interactive Dashboards**: Real-time sentiment trends
- **Participant Analysis**: Individual user behavior patterns
- **Time-based Analysis**: Hourly, daily, monthly patterns
- **Export Capabilities**: PDF, CSV, JSON reports
- **Comparison Tools**: Multi-chat analysis

## 📊 API Endpoints

### Authentication
```
POST /api/auth/register/          # User registration
POST /api/auth/login/             # User login
POST /api/auth/logout/            # User logout
GET  /api/auth/profile/           # User profile
PUT  /api/auth/profile/           # Update profile
POST /api/auth/change-password/   # Change password
```

### Chat Analysis
```
POST /api/chat/upload/            # Upload WhatsApp chat
GET  /api/chat/analyses/          # List user's analyses
GET  /api/chat/analyses/{id}/     # Get analysis details
DELETE /api/chat/analyses/{id}/   # Delete analysis
GET  /api/chat/analyses/{id}/messages/  # Get messages
GET  /api/chat/analyses/{id}/participants/  # Get participants
```

### Analytics
```
GET  /api/analytics/sentiment-trends/{id}/  # Sentiment over time
GET  /api/analytics/emotion-breakdown/{id}/ # Emotion distribution
GET  /api/analytics/activity-patterns/{id}/ # Activity patterns
GET  /api/analytics/word-cloud/{id}/        # Word cloud data
GET  /api/analytics/export/{id}/{format}/   # Export data
```

## 🔐 Security Features

### Data Protection
- **End-to-end Encryption**: Chat data encrypted at rest
- **Anonymization**: Participant names anonymized by default
- **Secure File Upload**: Validated file types and sizes
- **Data Retention**: Automatic cleanup of old analyses

### API Security
- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: Prevents API abuse
- **CORS Configuration**: Secure cross-origin requests
- **Input Validation**: SQL injection prevention
- **HTTPS Enforcement**: SSL/TLS in production

## 📈 Performance Optimizations

### Backend Optimizations
- **Database Indexing**: Optimized query performance
- **Connection Pooling**: Efficient database connections
- **Async Processing**: Non-blocking chat analysis
- **Batch Operations**: Bulk database operations
- **Caching Strategy**: Redis-based caching

### ML Optimizations
- **Model Caching**: Pre-loaded ML models
- **Batch Inference**: Process multiple texts together
- **GPU Support**: CUDA acceleration (if available)
- **Memory Management**: Efficient memory usage

## 🧪 Testing

### Run Tests
```bash
# Backend tests
cd backend
python manage.py test
pytest --cov=apps/

# Frontend tests
cd frontend
npm test
npm run test:coverage
```

### Load Testing
```bash
# Install locust
pip install locust

# Run load tests
locust -f tests/load_test.py --host=http://localhost:8000
```

## 📊 Monitoring & Logging

### Health Monitoring
- **Health Checks**: `/health/` endpoint
- **System Info**: `/health/info/` endpoint
- **Celery Monitoring**: Task queue status
- **Database Monitoring**: Connection status

### Logging
- **Structured Logging**: JSON format logs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Log Rotation**: Automatic log file rotation
- **Error Tracking**: Sentry integration (production)

## 🚀 Production Deployment

### Environment Variables
```bash
# Production settings
DEBUG=False
SECRET_KEY=your-super-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis
REDIS_URL=redis://host:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# AWS (for file storage)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

### Docker Production
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# SSL Setup with Let's Encrypt
docker-compose exec nginx certbot --nginx -d yourdomain.com
```

### Scaling
```bash
# Scale workers
docker-compose up -d --scale celery=4

# Scale backend
docker-compose up -d --scale backend=3
```

## 📋 Maintenance

### Database Maintenance
```bash
# Backup database
docker-compose exec db pg_dump -U postgres whatsapp_sentiment > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres whatsapp_sentiment < backup.sql

# Clean old data
docker-compose exec backend python manage.py cleanup_old_analyses
```

### Log Management
```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f celery

# Clean logs
docker system prune -f
```

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check database status
   docker-compose ps db
   docker-compose logs db
   ```

2. **Celery Tasks Not Processing**
   ```bash
   # Check celery worker status
   docker-compose logs celery
   celery -A core inspect active
   ```

3. **High Memory Usage**
   ```bash
   # Monitor resource usage
   docker stats
   
   # Restart services
   docker-compose restart backend celery
   ```

4. **ML Model Loading Issues**
   ```bash
   # Check model availability
   docker-compose exec backend python -c "from apps.sentiment.analyzers import MultiModelSentimentAnalyzer; analyzer = MultiModelSentimentAnalyzer(); analyzer.load_models()"
   ```

### Performance Tuning

1. **Database Optimization**
   ```sql
   -- Check slow queries
   SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
   
   -- Analyze table statistics
   ANALYZE;
   ```

2. **Redis Optimization**
   ```bash
   # Check Redis memory usage
   docker-compose exec redis redis-cli info memory
   
   # Clear cache if needed
   docker-compose exec redis redis-cli flushall
   ```

## 📞 Support

### Getting Help
- **Documentation**: Check README.md and code comments
- **Logs**: Check application logs for error details
- **Health Checks**: Use `/health/` endpoints
- **Database**: Check database connectivity and migrations

### Development
- **Code Style**: Follow PEP 8 for Python, ESLint for JavaScript
- **Testing**: Write tests for new features
- **Documentation**: Update docs for API changes
- **Security**: Follow security best practices

---

**🎉 Your WhatsApp Sentiment Analysis system is now ready for production!**