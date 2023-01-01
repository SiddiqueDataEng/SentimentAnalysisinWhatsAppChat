@echo off
echo 🚀 Setting up Enhanced WhatsApp Sentiment Analysis System...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Create environment file if it doesn't exist
if not exist .env (
    echo 📝 Creating environment file...
    copy .env.example .env
    echo ✅ Environment file created. Please edit .env with your configuration.
)

REM Build and start services
echo 🐳 Building and starting Docker services...
docker-compose up -d --build

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Run database migrations
echo 🗄️ Running database migrations...
docker-compose exec backend python manage.py migrate

REM Create superuser (optional)
echo 👤 Creating superuser (optional)...
echo You can skip this by pressing Ctrl+C
docker-compose exec backend python manage.py createsuperuser

REM Collect static files
echo 📁 Collecting static files...
docker-compose exec backend python manage.py collectstatic --noinput

echo.
echo 🎉 Setup complete!
echo.
echo 📊 Access the application:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000/api/
echo    Admin Panel: http://localhost:8000/admin/
echo    Health Check: http://localhost:8000/health/
echo.
echo 🔧 Useful commands:
echo    View logs: docker-compose logs -f
echo    Stop services: docker-compose down
echo    Restart services: docker-compose restart
echo.
echo 📖 Check DEPLOYMENT.md for detailed documentation.
pause