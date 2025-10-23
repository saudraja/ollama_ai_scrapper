# 🚀 Deployment Guide for Self-Healing Web Scraper

## 📋 Pre-Deployment Checklist

### **1. Repository Setup**
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit: Self-healing web scraper with Docker"

# Add remote repository
git remote add origin https://github.com/yourusername/self-healing-scraper.git
git push -u origin main
```

### **2. Docker Hub Setup**
```bash
# Login to Docker Hub
docker login

# Tag and push image
docker tag self-healing-scraper yourusername/self-healing-scraper:latest
docker push yourusername/self-healing-scraper:latest
```

## 🐳 Docker Deployment Options

### **Option 1: Local Docker**
```bash
# Quick start
./docker-start.sh

# Or manual
docker build -t self-healing-scraper .
docker run -d -p 8080:8080 --name scraper self-healing-scraper
```

### **Option 2: Docker Compose**
```bash
# Basic deployment
docker-compose up -d

# With AI features
docker-compose --profile ai up -d
```

### **Option 3: Production Docker Compose**
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  scraper:
    image: yourusername/self-healing-scraper:latest
    ports:
      - "8080:8080"
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## ☁️ Cloud Deployment

### **AWS ECS**
```bash
# Create ECS task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Run ECS service
aws ecs create-service \
  --cluster your-cluster \
  --service-name self-healing-scraper \
  --task-definition self-healing-scraper:1 \
  --desired-count 1
```

### **Google Cloud Run**
```bash
# Deploy to Cloud Run
gcloud run deploy self-healing-scraper \
  --image gcr.io/your-project/self-healing-scraper \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### **Azure Container Instances**
```bash
# Deploy to ACI
az container create \
  --resource-group your-rg \
  --name self-healing-scraper \
  --image yourusername/self-healing-scraper:latest \
  --ports 8080 \
  --dns-name-label self-healing-scraper
```

## 🐙 GitHub Actions CI/CD

### **`.github/workflows/docker.yml`**
```yaml
name: Docker Build and Deploy

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t self-healing-scraper .
    
    - name: Test Docker image
      run: |
        docker run -d -p 8080:8080 --name test-scraper self-healing-scraper
        sleep 30
        curl -f http://localhost:8080/health || exit 1
        docker stop test-scraper
    
    - name: Push to Docker Hub
      if: github.ref == 'refs/heads/main'
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker tag self-healing-scraper ${{ secrets.DOCKER_USERNAME }}/self-healing-scraper:latest
        docker push ${{ secrets.DOCKER_USERNAME }}/self-healing-scraper:latest
```

## 🔧 Environment Configuration

### **Production Environment Variables**
```bash
# .env.production
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
MAX_WORKERS=4
TIMEOUT=30
```

### **Docker Environment**
```dockerfile
# Add to Dockerfile
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO
ENV MAX_WORKERS=4
```

## 📊 Monitoring and Health Checks

### **Health Check Endpoint**
```bash
# Check if service is healthy
curl http://localhost:8080/health

# Expected response:
# {"status": "healthy", "timestamp": "2025-01-01T00:00:00"}
```

### **Logging Configuration**
```python
# Add to app_self_heal.py
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## 🚀 Quick Deployment Commands

### **For Repository Sharing:**
```bash
# 1. Initialize repository
git init
git add .
git commit -m "Self-healing web scraper with Docker"

# 2. Push to GitHub
git remote add origin https://github.com/yourusername/self-healing-scraper.git
git push -u origin main

# 3. Share with team
# Send them the repository URL
```

### **For Team Members:**
```bash
# 1. Clone repository
git clone https://github.com/yourusername/self-healing-scraper.git
cd self-healing-scraper

# 2. Run with Docker
./docker-start.sh

# 3. Test the API
curl -X POST http://localhost:8080/quotes/penske \
  -H 'Content-Type: application/json' \
  -d '{"pickup_zip": "19103", "dropoff_zip": "10001", "pickup_date": "2025-11-10", "dropoff_date": "2025-11-12", "headless": true}'
```

## 📋 Repository Structure

```
self-healing-scraper/
├── .github/
│   └── workflows/
│       └── docker.yml          # CI/CD pipeline
├── app_self_heal.py            # Main FastAPI app
├── penske_adapter.py           # Core scraper
├── resilient_finder.py         # AI selector finder
├── simple_scraper.py           # Fallback scraper
├── ollama_ai_repair.py         # Ollama AI integration
├── selector_kb.py              # Knowledge base
├── selector_kb.json            # Persistent KB data
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Multi-service setup
├── docker-start.sh             # Quick start script
├── requirements.txt            # Python dependencies
├── README.md                   # Main documentation
├── README_DOCKER.md            # Docker documentation
├── DEPLOYMENT.md               # This file
├── .gitignore                  # Git ignore rules
└── .dockerignore               # Docker ignore rules
```

## 🎯 Next Steps for Team

1. **Clone the repository**
2. **Run `./docker-start.sh`**
3. **Test the API at http://localhost:8080**
4. **Check the docs at http://localhost:8080/docs**
5. **Start building with the scraper!**

---

**Your self-healing scraper is now ready for team collaboration! 🎉**
