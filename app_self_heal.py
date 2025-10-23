# =============================================
# Self-Healing Web Scraper - Main Application
# =============================================
# FastAPI app with AI-assisted self-healing capabilities for web scraping

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, constr
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from penske_adapter import PenskeAdapter, Quote
from simple_scraper import SimplePenskeScraper, SimpleQuote

# =============================================
# FastAPI App Setup
# =============================================

app = FastAPI(
    title="Self-Healing Web Scraper API",
    description="AI-assisted web scraper with automatic selector repair",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================
# Data Models
# =============================================

ZipStr = constr(strip_whitespace=True, min_length=3, max_length=12)

class SearchRequest(BaseModel):
    pickup_zip: ZipStr
    dropoff_zip: ZipStr
    pickup_date: datetime
    dropoff_date: datetime
    truck: Optional[str] = Field(None, description="Truck size hint, e.g. '16 ft Truck'")
    headless: bool = Field(False, description="Headful helps you map selectors for the first run")

class QuoteResponse(BaseModel):
    provider: str
    truck_class: str
    pickup_zip: str
    dropoff_zip: str
    pickup_datetime: str
    dropoff_datetime: str
    price_total: float
    currency: str = "USD"
    taxes_and_fees: Optional[float] = None
    included_miles: Optional[int] = None
    per_mile_rate: Optional[float] = None
    add_ons: List[dict] = []
    cancellation_policy: Optional[str] = None
    demo_fallback: bool = False

# =============================================
# Initialize Adapter
# =============================================

penske_adapter = PenskeAdapter()
simple_scraper = SimplePenskeScraper()

# =============================================
# API Endpoints
# =============================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Self-Healing Web Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "quotes": "/quotes/penske",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "adapter": "penske_adapter_initialized"
    }

@app.post("/quotes/penske", response_model=List[QuoteResponse])
async def get_penske_quotes(request: SearchRequest):
    """
    Get truck rental quotes from Penske with self-healing selectors
    
    This endpoint demonstrates the self-healing capabilities:
    - Uses multiple fallback strategies for each form field
    - Automatically repairs broken selectors using AI heuristics
    - Learns from successful selector usage
    - Adapts to website changes over time
    """
    try:
        # Try the self-healing adapter first
        try:
            quotes = await penske_adapter.scrape_quotes(
                pickup_zip=request.pickup_zip,
                dropoff_zip=request.dropoff_zip,
                pickup_date=request.pickup_date,
                dropoff_date=request.dropoff_date,
                truck=request.truck,
                headless=request.headless
            )
        except Exception:
            # Fall back to simple scraper if self-healing fails
            simple_quotes = await simple_scraper.scrape_quotes(
                pickup_zip=request.pickup_zip,
                dropoff_zip=request.dropoff_zip,
                pickup_date=request.pickup_date,
                dropoff_date=request.dropoff_date,
                truck=request.truck,
                headless=request.headless
            )
            # Convert simple quotes to regular quotes
            quotes = []
            for sq in simple_quotes:
                quote = Quote(
                    provider=sq.provider,
                    truck_class=sq.truck_class,
                    pickup_zip=sq.pickup_zip,
                    dropoff_zip=sq.dropoff_zip,
                    pickup_datetime=sq.pickup_datetime,
                    dropoff_datetime=sq.dropoff_datetime,
                    price_total=sq.price_total,
                    currency=sq.currency,
                    included_miles=sq.included_miles,
                    demo_fallback=sq.demo_fallback
                )
                quotes.append(quote)
        
        # Convert to response format
        response_quotes = []
        for quote in quotes:
            response_quotes.append(QuoteResponse(
                provider=quote.provider,
                truck_class=quote.truck_class,
                pickup_zip=quote.pickup_zip,
                dropoff_zip=quote.dropoff_zip,
                pickup_datetime=quote.pickup_datetime,
                dropoff_datetime=quote.dropoff_datetime,
                price_total=quote.price_total,
                currency=quote.currency,
                taxes_and_fees=quote.taxes_and_fees,
                included_miles=quote.included_miles,
                per_mile_rate=quote.per_mile_rate,
                add_ons=quote.add_ons,
                cancellation_policy=quote.cancellation_policy,
                demo_fallback=quote.demo_fallback
            ))
        
        return response_quotes
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}"
        )

@app.get("/kb/status")
async def kb_status():
    """Get knowledge base status and statistics"""
    kb = penske_adapter.kb
    return {
        "kb_file": kb.kb_file,
        "version": kb.kb.get("version", "unknown"),
        "last_updated": kb.kb.get("last_updated", "unknown"),
        "providers": list(kb.kb.get("providers", {}).keys()),
        "penske_fields": list(kb.kb.get("providers", {}).get("penske", {}).keys())
    }

@app.get("/kb/strategies/{provider}/{field}")
async def get_strategies(provider: str, field: str):
    """Get strategies for a specific provider and field"""
    strategies = penske_adapter.kb.get_strategies(provider, field)
    return {
        "provider": provider,
        "field": field,
        "strategies": strategies
    }

# =============================================
# Development/Demo Endpoints
# =============================================

@app.post("/demo/fallback")
async def demo_fallback():
    """Demo endpoint showing fallback behavior"""
    return [
        {
            "provider": "penske",
            "truck_class": "16 ft Truck",
            "pickup_zip": "19103",
            "dropoff_zip": "10001",
            "pickup_datetime": "2025-11-10T00:00:00",
            "dropoff_datetime": "2025-11-12T00:00:00",
            "price_total": 129.99,
            "currency": "USD",
            "included_miles": 100,
            "demo_fallback": True
        }
    ]

# =============================================
# Run Instructions
# =============================================

if __name__ == "__main__":
    import uvicorn
    print("""
    🧠 Self-Healing Web Scraper - Starting...
    
    Quickstart:
    1. Install dependencies:
       pip install fastapi uvicorn pydantic playwright
       playwright install chromium
    
    2. Run the server:
       uvicorn app_self_heal:app --reload --port 8080
    
    3. Test the endpoint:
       curl -X POST http://localhost:8080/quotes/penske \\
         -H 'Content-Type: application/json' \\
         -d '{
               "pickup_zip": "19103",
               "dropoff_zip": "10001", 
               "pickup_date": "2025-11-10",
               "dropoff_date": "2025-11-12",
               "truck": "16 ft Truck",
               "headless": false
             }'
    
    4. Check KB status:
       curl http://localhost:8080/kb/status
    
    Features:
    ✅ Multi-strategy selector fallbacks
    ✅ AI-assisted selector repair
    ✅ Learning from successful strategies
    ✅ Knowledge base persistence
    ✅ Comprehensive error handling
    """)
    uvicorn.run(app, host="0.0.0.0", port=8080)
