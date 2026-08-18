@echo off
echo 🚀 Starting Graduated Autonomy Engine...
echo.
echo Building Docker image...
docker-compose build

echo.
echo Starting containers...
docker-compose up -d

echo.
echo ✅ System is running!
echo 📊 API: http://localhost:8000
echo 📚 Docs: http://localhost:8000/docs
echo 🏥 Health: http://localhost:8000/health
echo.
echo To stop: docker-compose down
echo To view logs: docker-compose logs -f