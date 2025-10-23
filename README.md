# 🧠 Self-Healing Web Scraper

A **FastAPI + Playwright** web scraper with **AI-assisted self-healing** capabilities. When selectors break due to website changes, the system automatically generates new selectors using **Ollama AI** and **heuristic rules**.

## 🎯 **Key Features**

- **🧠 AI-Powered Self-Healing** - Automatically adapts to website changes
- **🛡️ Bulletproof Reliability** - Always returns results with fallback strategies
- **🐳 Docker Ready** - One-command deployment
- **📚 Well Documented** - Complete setup and usage guides

## 🚀 **Quick Start**

### **Docker (Recommended)**
```bash
# Clone and run
git clone <your-repo-url>
cd self-healing-scraper
./docker-start.sh

# Test the API
curl -X POST http://localhost:8080/quotes/penske \
  -H 'Content-Type: application/json' \
  -d '{"pickup_zip": "19103", "dropoff_zip": "10001", "pickup_date": "2025-11-10", "dropoff_date": "2025-11-12", "headless": true}'
```

### **Local Development**
```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run the server
uvicorn app_self_heal:app --reload --port 8080
```

## 🏗️ **Architecture**

### **Core Components**
- **`app_self_heal.py`** - FastAPI server with self-healing endpoints
- **`penske_adapter.py`** - Main scraper with AI integration
- **`resilient_finder.py`** - Multi-strategy element finder with AI repair
- **`simple_scraper.py`** - Reliable fallback scraper
- **`ollama_ai_repair.py`** - Ollama AI integration
- **`selector_kb.py`** - Knowledge base for selector strategies

### **AI Integration Flow**
```
1. Try existing selectors from knowledge base
2. If selectors fail → Capture DOM snippet
3. Generate new selectors using:
   - Heuristic AI (rule-based) - FAST
   - Ollama AI (LLM-based) - INTELLIGENT
4. Test new selectors and update knowledge base
5. Fall back to simple scraper if all else fails
```

## 📊 **API Endpoints**

### **POST /quotes/penske**
Scrape Penske truck rental quotes with self-healing capabilities.

**Request:**
```json
{
  "pickup_zip": "19103",
  "dropoff_zip": "10001", 
  "pickup_date": "2025-11-10",
  "dropoff_date": "2025-11-12",
  "truck": "16 ft Truck",
  "headless": true
}
```

### **GET /health**
Health check endpoint for monitoring.

## 🐳 **Docker Deployment**

### **Quick Start**
```bash
./docker-start.sh
```

### **Docker Compose**
```bash
# Basic deployment
docker-compose up -d

# With Ollama AI
docker-compose --profile ai up -d
```

## 📚 **Documentation**

- **`README_DOCKER.md`** - Docker setup and usage
- **`DEPLOYMENT.md`** - Cloud deployment guide
- **`OLLAMA_AI_GUIDE.md`** - AI integration details
- **`DOCKER_SUMMARY.md`** - Quick reference

## 🎯 **Use Cases**

- **Production Web Scraping** - E-commerce, real estate, job postings
- **Data Pipeline Integration** - ETL processes with self-healing
- **Research & Development** - Market research automation

---

**🧠 Your self-healing web scraper is ready to handle any website changes! 🚀**