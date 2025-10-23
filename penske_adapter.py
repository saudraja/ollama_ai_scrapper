# =============================================
# Penske Adapter - Core Scraper with Self-Healing
# =============================================
# Handles Penske-specific scraping logic with resilient selectors

from typing import List, Optional, Dict, Any
from datetime import datetime
from playwright.async_api import async_playwright, Page, TimeoutError as PWTimeout
import re
from selector_kb import SelectorKB
from resilient_finder import ResilientFinder

class Quote:
    """Quote data model"""
    def __init__(self, provider: str, truck_class: str, pickup_zip: str, dropoff_zip: str,
                 pickup_datetime: str, dropoff_datetime: str, price_total: float,
                 currency: str = "USD", taxes_and_fees: Optional[float] = None,
                 included_miles: Optional[int] = None, per_mile_rate: Optional[float] = None,
                 add_ons: List[dict] = None, cancellation_policy: Optional[str] = None,
                 demo_fallback: bool = False):
        self.provider = provider
        self.truck_class = truck_class
        self.pickup_zip = pickup_zip
        self.dropoff_zip = dropoff_zip
        self.pickup_datetime = pickup_datetime
        self.dropoff_datetime = dropoff_datetime
        self.price_total = price_total
        self.currency = currency
        self.taxes_and_fees = taxes_and_fees
        self.included_miles = included_miles
        self.per_mile_rate = per_mile_rate
        self.add_ons = add_ons or []
        self.cancellation_policy = cancellation_policy
        self.demo_fallback = demo_fallback
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "truck_class": self.truck_class,
            "pickup_zip": self.pickup_zip,
            "dropoff_zip": self.dropoff_zip,
            "pickup_datetime": self.pickup_datetime,
            "dropoff_datetime": self.dropoff_datetime,
            "price_total": self.price_total,
            "currency": self.currency,
            "taxes_and_fees": self.taxes_and_fees,
            "included_miles": self.included_miles,
            "per_mile_rate": self.per_mile_rate,
            "add_ons": self.add_ons,
            "cancellation_policy": self.cancellation_policy,
            "demo_fallback": self.demo_fallback
        }

class PenskeAdapter:
    """Self-healing Penske scraper adapter"""
    
    def __init__(self, kb_file: str = "selector_kb.json"):
        self.kb = SelectorKB(kb_file)
        self.finder = ResilientFinder(self.kb)
    
    async def scrape_quotes(self, pickup_zip: str, dropoff_zip: str, pickup_date: datetime,
                     dropoff_date: datetime, truck: Optional[str] = None,
                     headless: bool = True) -> List[Quote]:
        """
        Scrape quotes from Penske with self-healing selectors
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=headless,
                    slow_mo=(60 if not headless else 0)
                )
                ctx = await browser.new_context()
                page = await ctx.new_page()
                
                try:
                    # Navigate to Penske
                    await page.goto("https://www.pensketruckrental.com/", timeout=45000)
                    
                    # Fill form with resilient selectors
                    await self._fill_form_resilient(page, pickup_zip, dropoff_zip, pickup_date, dropoff_date, truck)
                    
                    # Submit form
                    await self._submit_form_resilient(page)
                    
                    # Wait for results
                    await page.wait_for_load_state("networkidle", timeout=45000)
                    
                    # Parse results with resilient selectors
                    quotes = await self._parse_results_resilient(page, pickup_zip, dropoff_zip, pickup_date, dropoff_date)
                    
                    return quotes
                
                finally:
                    await ctx.close()
                    await browser.close()
        
        except PWTimeout as e:
            raise RuntimeError(f"Timeout while loading Penske: {e}")
        except Exception as e:
            raise RuntimeError(f"Scrape error: {e}")
    
    async def _fill_form_resilient(self, page: Page, pickup_zip: str, dropoff_zip: str,
                           pickup_date: datetime, dropoff_date: datetime, truck: Optional[str]):
        """Fill form using resilient selectors"""
        
        # Pickup location
        pickup_loc, strategy_index = await self.finder.find_with_strategies(page, "penske", "pickup_input")
        if pickup_loc:
            await pickup_loc.fill(pickup_zip)
            await page.keyboard.press("Enter")
        else:
            # Try AI repair
            dom_snippet = await page.content()
            pickup_loc, new_strategy = await self.finder.find_with_ai_repair(
                page, "penske", "pickup_input", dom_snippet, []
            )
            if pickup_loc:
                await pickup_loc.fill(pickup_zip)
                await page.keyboard.press("Enter")
            else:
                raise RuntimeError("Could not find pickup input field - all strategies failed")
        
        # Dropoff location
        dropoff_loc, _ = await self.finder.find_with_strategies(page, "penske", "dropoff_input")
        if dropoff_loc:
            await dropoff_loc.fill(dropoff_zip)
            await page.keyboard.press("Enter")
        else:
            raise RuntimeError("Could not find dropoff input field")
        
        # Pickup date
        pickup_date_loc, _ = await self.finder.find_with_strategies(page, "penske", "pickup_date")
        if pickup_date_loc:
            await pickup_date_loc.fill(pickup_date.strftime("%m/%d/%Y"))
        else:
            raise RuntimeError("Could not find pickup date field")
        
        # Dropoff date
        dropoff_date_loc, _ = await self.finder.find_with_strategies(page, "penske", "dropoff_date")
        if dropoff_date_loc:
            await dropoff_date_loc.fill(dropoff_date.strftime("%m/%d/%Y"))
        else:
            raise RuntimeError("Could not find dropoff date field")
        
        # Optional truck size
        if truck:
            try:
                truck_loc = page.get_by_label("Truck Size")
                await truck_loc.select_option(label=truck)
            except Exception:
                pass  # Truck size is optional
    
    async def _submit_form_resilient(self, page: Page):
        """Submit form using resilient selectors"""
        submit_loc, _ = await self.finder.find_with_strategies(page, "penske", "submit_button")
        if submit_loc:
            await submit_loc.click(timeout=30000)
        else:
            raise RuntimeError("Could not find submit button")
    
    async def _parse_results_resilient(self, page: Page, pickup_zip: str, dropoff_zip: str,
                               pickup_date: datetime, dropoff_date: datetime) -> List[Quote]:
        """Parse results using resilient selectors"""
        
        # Find result cards
        cards_loc, _ = await self.finder.find_with_strategies(page, "penske", "result_cards")
        if not cards_loc:
            # Try AI repair for result cards
            dom_snippet = await page.content()
            cards_loc, new_strategy = await self.finder.find_with_ai_repair(
                page, "penske", "result_cards", dom_snippet, []
            )
            if not cards_loc:
                raise RuntimeError("Could not find result cards")
        
        cards = await cards_loc.all()
        quotes = []
        
        for card in cards:
            try:
                quote = await self._parse_single_card(card, pickup_zip, dropoff_zip, pickup_date, dropoff_date)
                if quote:
                    quotes.append(quote)
            except Exception:
                continue
        
        if not quotes:
            raise RuntimeError("No result cards parsed — update selectors for results container and fields.")
        
        return quotes
    
    async def _parse_single_card(self, card, pickup_zip: str, dropoff_zip: str,
                         pickup_date: datetime, dropoff_date: datetime) -> Optional[Quote]:
        """Parse a single result card"""
        try:
            # Get truck title
            title_loc, _ = await self.finder.find_with_strategies(card.page, "penske", "truck_title")
            if not title_loc:
                title_loc = card.locator("h3, h2").first
            title = await title_loc.inner_text(timeout=2000) if title_loc else "Truck"
            title = title.strip() if title else "Truck"
            
            # Get price
            price_loc, _ = await self.finder.find_with_strategies(card.page, "penske", "price_element")
            if not price_loc:
                price_loc = card.locator(".price, .total, [data-test=total-price]").first
            price_text = await price_loc.inner_text(timeout=2000) if price_loc else "0"
            price = self._parse_money(price_text)
            
            # Get miles info
            miles_loc, _ = await self.finder.find_with_strategies(card.page, "penske", "miles_element")
            if not miles_loc:
                miles_loc = card.locator(".miles, [data-test=included-miles]").first
            miles_text = await miles_loc.inner_text(timeout=1200) if miles_loc else None
            
            included_miles = self._parse_miles(miles_text)
            
            return Quote(
                provider="penske",
                truck_class=title,
                pickup_zip=pickup_zip,
                dropoff_zip=dropoff_zip,
                pickup_datetime=pickup_date.isoformat(),
                dropoff_datetime=dropoff_date.isoformat(),
                price_total=price,
                included_miles=included_miles
            )
        
        except Exception:
            return None
    
    def _parse_money(self, text: str) -> float:
        """Parse money from text"""
        if not text:
            return 0.0
        m = re.search(r"([0-9]+(?:\.[0-9]{1,2})?)", text.replace(",", ""))
        return float(m.group(1)) if m else 0.0
    
    def _parse_miles(self, text: Optional[str]) -> Optional[int]:
        """Parse miles from text"""
        if not text:
            return None
        if "unlimited" in text.lower():
            return None  # Represent as None for unlimited
        m = re.search(r"(\d{1,6})\s*mile", text.lower())
        return int(m.group(1)) if m else None
