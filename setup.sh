#!/bin/bash

# Enhanced WhatsApp Sentiment Analysis Setup Script
echo "🚀 Setting up Enhanced WhatsApp Sentiment Analysis System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating environment file..."
    cp .env.example .env
    echo "✅ Environment file created. Please edit .env with your configuration."
fi

# Build and start services
echo "🐳 Building and starting Docker services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose exec backend python manage.py migrate

# Create superuser (optional)
echo "👤 Creating superuser (optional)..."
echo "You can skip this by pressing Ctrl+C"
docker-compose exec backend python manage.py createsuperuser || true

# Collect static files
echo "📁 Collecting static files..."
docker-compose exec backend python manage.py collectstatic --noinput

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📊 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000/api/"
echo "   Admin Panel: http://localhost:8000/admin/"
echo "   Health Check: http://localhost:8000/health/"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo ""
echo "📖 Check DEPLOYMENT.md for detailed documentation."