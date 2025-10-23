# =============================================
# Resilient Finder - Multi-Strategy Element Locator
# =============================================
# Implements fallback strategies for finding elements when selectors break

from typing import List, Dict, Any, Optional, Tuple
from playwright.async_api import Page, Locator, TimeoutError as PWTimeout
import re
from selector_kb import SelectorKB
from ollama_ai_repair import OllamaAIRepair

class ResilientFinder:
    """Finds elements using multiple fallback strategies"""
    
    def __init__(self, kb: SelectorKB):
        self.kb = kb
        self.ollama_repair = OllamaAIRepair()
    
    async def find_with_strategies(self, page: Page, provider: str, field: str, timeout: int = 5000) -> Tuple[Optional[Locator], int]:
        """
        Find element using ranked strategies from KB
        Returns (locator, strategy_index) or (None, -1) if all fail
        """
        strategies = self.kb.get_strategies(provider, field)
        
        for i, strategy in enumerate(strategies):
            try:
                locator = self._apply_strategy(page, strategy)
                if locator and await self._validate_locator(locator, timeout):
                    # Record success for this strategy
                    self.kb.record_success(provider, field, i)
                    return locator, i
            except Exception:
                continue
        
        return None, -1
    
    def _apply_strategy(self, page: Page, strategy: Dict[str, Any]) -> Optional[Locator]:
        """Apply a single strategy to find element"""
        strategy_type = strategy["strategy"]
        params = strategy["params"]
        
        if strategy_type == "label":
            return page.get_by_label(params["text"])
        elif strategy_type == "placeholder":
            return page.get_by_placeholder(params["text"])
        elif strategy_type == "role":
            return page.get_by_role(params["role"], name=params["name"])
        elif strategy_type == "css":
            return page.locator(params["selector"])
        elif strategy_type == "xpath":
            return page.locator(f"xpath={params['xpath']}")
        elif strategy_type == "testid":
            return page.get_by_test_id(params["testid"])
        elif strategy_type == "text":
            return page.get_by_text(params["text"])
        else:
            return None
    
    async def _validate_locator(self, locator: Locator, timeout: int = 5000) -> bool:
        """Validate that locator actually finds elements"""
        try:
            await locator.first.wait_for(timeout=timeout)
            return True
        except PWTimeout:
            return False
    
    async def find_with_ai_repair(self, page: Page, provider: str, field: str, dom_snippet: str, failed_strategies: List[Dict[str, Any]]) -> Tuple[Optional[Locator], Optional[Dict[str, Any]]]:
        """
        Use AI repair to find element when all strategies fail
        Returns (locator, new_strategy) or (None, None) if repair fails
        """
        # Use heuristic AI first (faster and more reliable)
        new_strategy = self._ai_propose_strategy(field, dom_snippet, failed_strategies)
        
        # If heuristic AI fails and Ollama is available, try it as last resort
        if not new_strategy and self.ollama_repair.check_ollama_available():
            try:
                new_strategy = self.ollama_repair.propose_strategy_with_ollama(field, dom_snippet, failed_strategies, provider)
            except Exception:
                # Ollama failed, stick with heuristic result (None)
                pass
        
        if new_strategy:
            try:
                locator = self._apply_strategy(page, new_strategy)
                if locator and await self._validate_locator(locator):
                    # Add successful strategy to KB
                    self.kb.add_strategy(provider, field, new_strategy, position=0)
                    return locator, new_strategy
            except Exception:
                pass
        
        return None, None
    
    def _ai_propose_strategy(self, field: str, dom_snippet: str, failed_strategies: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        AI repair stub - proposes new selectors based on DOM analysis
        In future: replace with LLM call
        """
        # Heuristic-based selector generation
        proposals = []
        
        # Look for common patterns in DOM
        if "input" in dom_snippet.lower():
            # Try to find input-related selectors
            if "pickup" in field.lower() or "pick-up" in field.lower():
                proposals.extend([
                    {"strategy": "css", "params": {"selector": "input[placeholder*='pickup']"}},
                    {"strategy": "css", "params": {"selector": "input[placeholder*='Pick-up']"}},
                    {"strategy": "css", "params": {"selector": "input[name*='pickup']"}},
                    {"strategy": "css", "params": {"selector": "input[id*='pickup']"}}
                ])
            elif "dropoff" in field.lower() or "drop-off" in field.lower():
                proposals.extend([
                    {"strategy": "css", "params": {"selector": "input[placeholder*='dropoff']"}},
                    {"strategy": "css", "params": {"selector": "input[placeholder*='Drop-off']"}},
                    {"strategy": "css", "params": {"selector": "input[name*='dropoff']"}},
                    {"strategy": "css", "params": {"selector": "input[id*='dropoff']"}}
                ])
            elif "date" in field.lower():
                proposals.extend([
                    {"strategy": "css", "params": {"selector": "input[type='date']"}},
                    {"strategy": "css", "params": {"selector": "input[placeholder*='date']"}},
                    {"strategy": "css", "params": {"selector": "input[name*='date']"}}
                ])
        
        if "button" in dom_snippet.lower():
            proposals.extend([
                {"strategy": "css", "params": {"selector": "button[type='submit']"}},
                {"strategy": "css", "params": {"selector": "button:has-text('Get')"}},
                {"strategy": "css", "params": {"selector": "button:has-text('Search')"}},
                {"strategy": "css", "params": {"selector": "button:has-text('Find')"}}
            ])
        
        # Look for data-test attributes
        testid_matches = re.findall(r'data-test="([^"]*)"', dom_snippet)
        for testid in testid_matches:
            if any(keyword in testid.lower() for keyword in [field.lower().replace('_', ''), 'input', 'button', 'card']):
                proposals.append({"strategy": "css", "params": {"selector": f"[data-test='{testid}']"}})
        
        # Look for aria-label attributes
        aria_matches = re.findall(r'aria-label="([^"]*)"', dom_snippet)
        for label in aria_matches:
            if any(keyword in label.lower() for keyword in [field.lower().replace('_', ''), 'pickup', 'dropoff', 'date']):
                proposals.append({"strategy": "css", "params": {"selector": f"[aria-label='{label}']"}})
        
        # Return first proposal (in future: rank by confidence)
        return proposals[0] if proposals else None
