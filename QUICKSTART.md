# 🚀 Quick Start Guide

## WhatsApp Sentiment Analysis - Enhanced Production System

### ⚡ One-Minute Setup

**Windows Users:**
```cmd
setup.bat
```

**Linux/Mac Users:**
```bash
chmod +x setup.sh
./setup.sh
```

### 📋 Prerequisites

- **Docker Desktop** (required)
- **Docker Compose** (usually included with Docker Desktop)
- **Python 3.9+** (for testing)

### 🔧 Manual Setup (Alternative)

1. **Start Services**
   ```bash
   docker-compose up -d --build
   ```

2. **Initialize Database**
   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py createsuperuser
   ```

3. **Access Application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000/api/
   - **Admin Panel**: http://localhost:8000/admin/

### 🧪 Verify Installation

```bash
python verify_setup.py  # Check project structure
python test_system.py   # Test running system
```

### 📱 How to Use

1. **Export WhatsApp Chat**
   - Open WhatsApp → Chat → Menu → Export Chat → Without Media
   - Save as .txt file

2. **Upload & Analyze**
   - Go to http://localhost:3000
   - Click "Upload Chat"
   - Drag & drop your .txt file
   - Wait for analysis to complete

3. **View Results**
   - See sentiment scores, emotions, and participant insights
   - Export results as needed

### 🛠️ Common Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Update system
docker-compose pull && docker-compose up -d --build
```

### 🆘 Troubleshooting

**Services won't start?**
- Check Docker is running: `docker --version`
- Check ports 3000, 8000, 5432, 6379 are free
- Run: `docker-compose down && docker-compose up -d`

**Upload fails?**
- Ensure file is .txt format from WhatsApp export
- Check file size < 50MB
- Verify backend is running: http://localhost:8000/health/

**Need help?**
- Check logs: `docker-compose logs backend`
- See full documentation: `DEPLOYMENT.md`
- Run diagnostics: `python test_system.py`

### 🎯 What's Included

- ✅ **Multi-Model Sentiment Analysis** (VADER, TextBlob, RoBERTa)
- ✅ **Emotion Detection** (6 basic emotions)
- ✅ **Language Support** (English, Hindi, Hinglish)
- ✅ **Privacy Protection** (Participant anonymization)
- ✅ **Interactive Dashboard** (React frontend)
- ✅ **REST API** (Django backend)
- ✅ **Production Ready** (Docker deployment)

### 📊 System Requirements

- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Internet connection for Docker images
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)

---

**🎉 You're ready to analyze WhatsApp chats with advanced AI!**