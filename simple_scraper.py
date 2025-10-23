#!/usr/bin/env python3
"""
Simple, reliable scraper that works without complex AI
"""

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
from typing import List, Optional

class SimpleQuote:
    """Simple quote data model"""
    def __init__(self, provider: str, truck_class: str, pickup_zip: str, dropoff_zip: str,
                 pickup_datetime: str, dropoff_datetime: str, price_total: float,
                 currency: str = "USD", included_miles: Optional[int] = None,
                 demo_fallback: bool = False):
        self.provider = provider
        self.truck_class = truck_class
        self.pickup_zip = pickup_zip
        self.dropoff_zip = dropoff_zip
        self.pickup_datetime = pickup_datetime
        self.dropoff_datetime = dropoff_datetime
        self.price_total = price_total
        self.currency = currency
        self.included_miles = included_miles
        self.demo_fallback = demo_fallback
    
    def to_dict(self):
        return {
            "provider": self.provider,
            "truck_class": self.truck_class,
            "pickup_zip": self.pickup_zip,
            "dropoff_zip": self.dropoff_zip,
            "pickup_datetime": self.pickup_datetime,
            "dropoff_datetime": self.dropoff_datetime,
            "price_total": self.price_total,
            "currency": self.currency,
            "included_miles": self.included_miles,
            "demo_fallback": self.demo_fallback
        }

class SimplePenskeScraper:
    """Simple, reliable Penske scraper"""
    
    async def scrape_quotes(self, pickup_zip: str, dropoff_zip: str, pickup_date: datetime,
                           dropoff_date: datetime, truck: Optional[str] = None,
                           headless: bool = True) -> List[SimpleQuote]:
        """Scrape quotes with simple, reliable approach"""
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=headless,
                    slow_mo=1000 if not headless else 0
                )
                ctx = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )
                page = await ctx.new_page()
                
                try:
                    # Navigate to Penske
                    await page.goto("https://www.pensketruckrental.com/", timeout=30000)
                    await page.wait_for_load_state("networkidle", timeout=10000)
                    
                    # Find and fill pickup location
                    pickup_filled = False
                    inputs = await page.locator("input").all()
                    
                    for input_elem in inputs:
                        try:
                            placeholder = await input_elem.get_attribute("placeholder") or ""
                            if "from" in placeholder.lower() or "pickup" in placeholder.lower():
                                await input_elem.fill(pickup_zip)
                                await page.keyboard.press("Enter")
                                await page.wait_for_timeout(1000)
                                pickup_filled = True
                                break
                        except:
                            continue
                    
                    if not pickup_filled:
                        # Try first text input
                        try:
                            first_input = page.locator("input[type='text']").first
                            await first_input.fill(pickup_zip)
                            await page.keyboard.press("Enter")
                            await page.wait_for_timeout(1000)
                            pickup_filled = True
                        except:
                            pass
                    
                    # Find and fill dropoff location
                    dropoff_filled = False
                    for input_elem in inputs:
                        try:
                            placeholder = await input_elem.get_attribute("placeholder") or ""
                            if "to" in placeholder.lower() or "dropoff" in placeholder.lower():
                                await input_elem.fill(dropoff_zip)
                                await page.keyboard.press("Enter")
                                await page.wait_for_timeout(1000)
                                dropoff_filled = True
                                break
                        except:
                            continue
                    
                    if not dropoff_filled:
                        # Try second text input
                        try:
                            second_input = page.locator("input[type='text']").nth(1)
                            await second_input.fill(dropoff_zip)
                            await page.keyboard.press("Enter")
                            await page.wait_for_timeout(1000)
                            dropoff_filled = True
                        except:
                            pass
                    
                    # Try to submit
                    submit_clicked = False
                    buttons = await page.locator("button").all()
                    for button in buttons:
                        try:
                            text = await button.inner_text()
                            if any(word in text.lower() for word in ["get", "search", "find", "rates", "quote"]):
                                await button.click()
                                submit_clicked = True
                                break
                        except:
                            continue
                    
                    if not submit_clicked:
                        # Try pressing Enter on last input
                        try:
                            last_input = page.locator("input").last
                            await last_input.press("Enter")
                        except:
                            pass
                    
                    # Wait for results
                    await page.wait_for_timeout(5000)
                    
                    # Look for result cards
                    quotes = []
                    result_selectors = ["article", ".card", "[class*='rate']", "[class*='quote']"]
                    
                    for selector in result_selectors:
                        try:
                            cards = await page.locator(selector).all()
                            if cards:
                                for card in cards[:3]:  # Limit to first 3
                                    try:
                                        # Try to extract title
                                        title_elem = card.locator("h1, h2, h3").first
                                        title = await title_elem.inner_text() if await title_elem.count() > 0 else "Truck"
                                        
                                        # Try to extract price
                                        price_elem = card.locator("[class*='price'], [class*='total'], [class*='cost']").first
                                        price_text = await price_elem.inner_text() if await price_elem.count() > 0 else "0"
                                        
                                        # Parse price
                                        import re
                                        price_match = re.search(r'([0-9]+(?:\.[0-9]{1,2})?)', price_text.replace(",", ""))
                                        price = float(price_match.group(1)) if price_match else 0.0
                                        
                                        if price > 0:  # Only add if we found a real price
                                            quote = SimpleQuote(
                                                provider="penske",
                                                truck_class=title.strip(),
                                                pickup_zip=pickup_zip,
                                                dropoff_zip=dropoff_zip,
                                                pickup_datetime=pickup_date.isoformat(),
                                                dropoff_datetime=dropoff_date.isoformat(),
                                                price_total=price,
                                                included_miles=100
                                            )
                                            quotes.append(quote)
                                    except:
                                        continue
                                
                                if quotes:
                                    break
                        except:
                            continue
                    
                    # If no real quotes found, return demo data
                    if not quotes:
                        quotes = self._create_demo_quotes(pickup_zip, dropoff_zip, pickup_date, dropoff_date, truck)
                    
                    return quotes
                    
                finally:
                    await ctx.close()
                    await browser.close()
        
        except Exception as e:
            # Return demo data on any error
            return self._create_demo_quotes(pickup_zip, dropoff_zip, pickup_date, dropoff_date, truck)
    
    def _create_demo_quotes(self, pickup_zip: str, dropoff_zip: str, pickup_date: datetime, 
                          dropoff_date: datetime, truck: Optional[str]) -> List[SimpleQuote]:
        """Create demo quotes when scraping fails"""
        
        base_price = 89.99
        if truck and "16" in truck:
            base_price = 129.99
        elif truck and "24" in truck:
            base_price = 189.99
        
        # Add variation based on zip codes
        distance_factor = abs(hash(pickup_zip + dropoff_zip)) % 50
        price_variation = base_price + distance_factor
        
        quotes = [
            SimpleQuote(
                provider="penske",
                truck_class=truck or "16 ft Truck",
                pickup_zip=pickup_zip,
                dropoff_zip=dropoff_zip,
                pickup_datetime=pickup_date.isoformat(),
                dropoff_datetime=dropoff_date.isoformat(),
                price_total=round(price_variation, 2),
                included_miles=100,
                demo_fallback=True
            ),
            SimpleQuote(
                provider="penske",
                truck_class="24 ft Truck",
                pickup_zip=pickup_zip,
                dropoff_zip=dropoff_zip,
                pickup_datetime=pickup_date.isoformat(),
                dropoff_datetime=dropoff_date.isoformat(),
                price_total=round(price_variation + 60, 2),
                included_miles=100,
                demo_fallback=True
            )
        ]
        
        return quotes

async def main():
    """Test the simple scraper"""
    scraper = SimplePenskeScraper()
    
    quotes = await scraper.scrape_quotes(
        pickup_zip="19103",
        dropoff_zip="10001",
        pickup_date=datetime(2025, 11, 10),
        dropoff_date=datetime(2025, 11, 12),
        truck="16 ft Truck",
        headless=True
    )
    
    print(f"Results: {len(quotes)} quotes found")
    for quote in quotes:
        status = "Demo" if quote.demo_fallback else "Real"
        print(f"  - {quote.truck_class}: ${quote.price_total} ({status})")

if __name__ == "__main__":
    asyncio.run(main())
