# 🐳 Docker Setup for Self-Healing Web Scraper

## 🚀 Quick Start

### **Option 1: Simple Docker Run**
```bash
# Build and run the scraper
./docker-start.sh
```

### **Option 2: Docker Compose**
```bash
# Basic setup (without AI)
docker-compose up --build

# With Ollama AI (optional)
docker-compose --profile ai up --build
```

### **Option 3: Manual Docker Commands**
```bash
# Build the image
docker build -t self-healing-scraper .

# Run the container
docker run -d \
  --name self-healing-scraper \
  -p 8080:8080 \
  -v $(pwd)/selector_kb.json:/app/selector_kb.json \
  self-healing-scraper
```

## 📋 What's Included

### **Core Application**
- ✅ FastAPI server with self-healing capabilities
- ✅ Playwright browser automation
- ✅ Multi-strategy selector fallbacks
- ✅ Simple scraper fallback
- ✅ Demo data generation

### **AI Features (Optional)**
- ✅ Ollama integration for real AI
- ✅ Heuristic AI (rule-based)
- ✅ Knowledge base learning

### **Production Features**
- ✅ Health checks
- ✅ Non-root user for security
- ✅ Optimized Docker layers
- ✅ Volume persistence for KB

## 🧪 Testing the Docker Setup

### **1. Check if it's running:**
```bash
curl http://localhost:8080/health
```

### **2. Test the API:**
```bash
curl -X POST http://localhost:8080/quotes/penske \
  -H 'Content-Type: application/json' \
  -d '{
        "pickup_zip": "19103",
        "dropoff_zip": "10001",
        "pickup_date": "2025-11-10",
        "dropoff_date": "2025-11-12",
        "truck": "16 ft Truck",
        "headless": true
      }'
```

### **3. View API documentation:**
Open http://localhost:8080/docs in your browser

## 🔧 Docker Commands

### **Container Management**
```bash
# View logs
docker logs self-healing-scraper

# Stop container
docker stop self-healing-scraper

# Remove container
docker rm self-healing-scraper

# Restart container
docker restart self-healing-scraper
```

### **Development**
```bash
# Run with volume mounting for development
docker run -it --rm \
  -p 8080:8080 \
  -v $(pwd):/app \
  self-healing-scraper

# Access container shell
docker exec -it self-healing-scraper /bin/bash
```

## 🚀 Deployment Options

### **1. Local Development**
```bash
./docker-start.sh
```

### **2. Production with Docker Compose**
```bash
docker-compose up -d
```

### **3. Cloud Deployment**
- **AWS ECS**: Use the Dockerfile with ECS task definition
- **Google Cloud Run**: Deploy directly from container registry
- **Azure Container Instances**: Use the Docker image
- **Kubernetes**: Create deployment with the Docker image

## 📊 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTHONUNBUFFERED` | `1` | Python output buffering |
| `OLLAMA_HOST` | `http://ollama:11434` | Ollama service URL (when using compose) |

## 🔍 Troubleshooting

### **Container won't start:**
```bash
# Check logs
docker logs self-healing-scraper

# Check if port is available
netstat -tulpn | grep 8080
```

### **Playwright issues:**
```bash
# Rebuild with fresh Playwright install
docker build --no-cache -t self-healing-scraper .
```

### **Permission issues:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

## 📁 File Structure

```
pen_sake_demo/
├── Dockerfile              # Main Docker configuration
├── docker-compose.yml      # Multi-service setup
├── docker-start.sh         # Quick start script
├── requirements.txt        # Python dependencies
├── .dockerignore          # Docker ignore file
├── app_self_heal.py       # Main FastAPI app
├── penske_adapter.py       # Core scraper
├── resilient_finder.py     # AI selector finder
├── simple_scraper.py       # Fallback scraper
├── ollama_ai_repair.py     # Ollama AI integration
├── selector_kb.py          # Knowledge base
└── selector_kb.json        # Persistent KB data
```

## 🎯 Next Steps

1. **Test locally**: `./docker-start.sh`
2. **Push to registry**: Tag and push to Docker Hub
3. **Deploy**: Use in production environment
4. **Monitor**: Check logs and health endpoints

---

**Your self-healing scraper is now fully dockerized and ready for deployment! 🎉**
