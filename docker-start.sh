#!/bin/bash
# =============================================
# Docker Startup Script
# =============================================

echo "🧠 Self-Healing Web Scraper - Docker Setup"
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build the image
echo "🔨 Building Docker image..."
docker build -t self-healing-scraper .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
else
    echo "❌ Docker build failed!"
    exit 1
fi

# Run the container
echo "🚀 Starting container..."
docker run -d \
    --name self-healing-scraper \
    -p 8080:8080 \
    -v $(pwd)/selector_kb.json:/app/selector_kb.json \
    self-healing-scraper

if [ $? -eq 0 ]; then
    echo "✅ Container started successfully!"
    echo ""
    echo "📍 API available at: http://localhost:8080"
    echo "📖 API docs at: http://localhost:8080/docs"
    echo ""
    echo "🧪 Test with:"
    echo "curl -X POST http://localhost:8080/quotes/penske \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"pickup_zip\": \"19103\", \"dropoff_zip\": \"10001\", \"pickup_date\": \"2025-11-10\", \"dropoff_date\": \"2025-11-12\", \"headless\": true}'"
    echo ""
    echo "📊 Check logs: docker logs self-healing-scraper"
    echo "🛑 Stop: docker stop self-healing-scraper"
else
    echo "❌ Failed to start container!"
    exit 1
fi
