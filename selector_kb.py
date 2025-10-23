# =============================================
# Selector Knowledge Base (KB) System
# =============================================
# Manages ranked selector strategies for each field across different providers
# Supports learning and adaptation when selectors break

from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime

class SelectorStrategy:
    """Represents a single selector strategy with metadata"""
    def __init__(self, strategy: str, params: Dict[str, Any], success_count: int = 0, last_success: Optional[str] = None):
        self.strategy = strategy
        self.params = params
        self.success_count = success_count
        self.last_success = last_success or datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy": self.strategy,
            "params": self.params,
            "success_count": self.success_count,
            "last_success": self.last_success
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SelectorStrategy':
        return cls(
            strategy=data["strategy"],
            params=data["params"],
            success_count=data.get("success_count", 0),
            last_success=data.get("last_success")
        )

class SelectorKB:
    """Knowledge base for managing selector strategies across providers"""
    
    def __init__(self, kb_file: str = "selector_kb.json"):
        self.kb_file = kb_file
        self.kb = self._load_kb()
    
    def _load_kb(self) -> Dict[str, Any]:
        """Load knowledge base from file or create default"""
        if os.path.exists(self.kb_file):
            try:
                with open(self.kb_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default KB structure
        return {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "providers": {
                "penske": {
                    "pickup_input": [
                        {"strategy": "label", "params": {"text": "Pick-up Location"}},
                        {"strategy": "placeholder", "params": {"text": "Pick-up"}},
                        {"strategy": "css", "params": {"selector": "input[placeholder*='pickup' i]"}},
                        {"strategy": "css", "params": {"selector": "input[placeholder*='Pick-up' i]"}},
                        {"strategy": "css", "params": {"selector": "input[name*='pickup' i]"}},
                        {"strategy": "css", "params": {"selector": "input[id*='pickup' i]"}},
                        {"strategy": "css", "params": {"selector": "input[placeholder*='location' i]:first-of-type"}},
                        {"strategy": "css", "params": {"selector": "input[type='text']:first-of-type"}},
                        {"strategy": "css", "params": {"selector": "[data-test=pickup] input"}}
                    ],
                    "dropoff_input": [
                        {"strategy": "label", "params": {"text": "Drop-off Location"}},
                        {"strategy": "placeholder", "params": {"text": "Drop-off"}},
                        {"strategy": "css", "params": {"selector": "input[placeholder*='dropoff' i]"}},
                        {"strategy": "css", "params": {"selector": "input[placeholder*='Drop-off' i]"}},
                        {"strategy": "css", "params": {"selector": "input[name*='dropoff' i]"}},
                        {"strategy": "css", "params": {"selector": "input[id*='dropoff' i]"}},
                        {"strategy": "css", "params": {"selector": "input[placeholder*='location' i]:nth-of-type(2)"}},
                        {"strategy": "css", "params": {"selector": "input[type='text']:nth-of-type(2)"}},
                        {"strategy": "css", "params": {"selector": "[data-test=dropoff] input"}}
                    ],
                    "pickup_date": [
                        {"strategy": "label", "params": {"text": "Pick-up Date"}},
                        {"strategy": "css", "params": {"selector": "input[type='date']"}},
                        {"strategy": "css", "params": {"selector": "[data-test=pickup-date] input"}},
                        {"strategy": "css", "params": {"selector": "input[placeholder*='date']"}}
                    ],
                    "dropoff_date": [
                        {"strategy": "label", "params": {"text": "Drop-off Date"}},
                        {"strategy": "css", "params": {"selector": "input[type='date']"}},
                        {"strategy": "css", "params": {"selector": "[data-test=dropoff-date] input"}},
                        {"strategy": "css", "params": {"selector": "input[placeholder*='date']"}}
                    ],
                    "submit_button": [
                        {"strategy": "role", "params": {"name": "Get Rates"}},
                        {"strategy": "role", "params": {"name": "Search"}},
                        {"strategy": "role", "params": {"name": "Find"}},
                        {"strategy": "css", "params": {"selector": "button[type='submit']"}},
                        {"strategy": "css", "params": {"selector": "[data-test=submit]"}}
                    ],
                    "result_cards": [
                        {"strategy": "css", "params": {"selector": "[data-test=rate-card]"}},
                        {"strategy": "css", "params": {"selector": ".rate-card"}},
                        {"strategy": "css", "params": {"selector": "article"}},
                        {"strategy": "css", "params": {"selector": ".quote-card"}},
                        {"strategy": "css", "params": {"selector": "[class*='rate']"}}
                    ],
                    "price_element": [
                        {"strategy": "css", "params": {"selector": ".price"}},
                        {"strategy": "css", "params": {"selector": ".total"}},
                        {"strategy": "css", "params": {"selector": "[data-test=total-price]"}},
                        {"strategy": "css", "params": {"selector": "[class*='price']"}},
                        {"strategy": "css", "params": {"selector": "[class*='total']"}}
                    ],
                    "truck_title": [
                        {"strategy": "css", "params": {"selector": "h3"}},
                        {"strategy": "css", "params": {"selector": "h2"}},
                        {"strategy": "css", "params": {"selector": "[data-test=truck-title]"}},
                        {"strategy": "css", "params": {"selector": "[class*='title']"}}
                    ],
                    "miles_element": [
                        {"strategy": "css", "params": {"selector": ".miles"}},
                        {"strategy": "css", "params": {"selector": "[data-test=included-miles]"}},
                        {"strategy": "css", "params": {"selector": "[class*='mile']"}}
                    ]
                }
            }
        }
    
    def save_kb(self):
        """Save knowledge base to file"""
        self.kb["last_updated"] = datetime.now().isoformat()
        with open(self.kb_file, 'w') as f:
            json.dump(self.kb, f, indent=2)
    
    def get_strategies(self, provider: str, field: str) -> List[Dict[str, Any]]:
        """Get ranked strategies for a specific field"""
        return self.kb.get("providers", {}).get(provider, {}).get(field, [])
    
    def add_strategy(self, provider: str, field: str, strategy: Dict[str, Any], position: int = 0):
        """Add a new strategy to the KB (inserted at position)"""
        if "providers" not in self.kb:
            self.kb["providers"] = {}
        if provider not in self.kb["providers"]:
            self.kb["providers"][provider] = {}
        if field not in self.kb["providers"][provider]:
            self.kb["providers"][provider][field] = []
        
        # Insert at position (0 = highest priority)
        self.kb["providers"][provider][field].insert(position, strategy)
        self.save_kb()
    
    def promote_strategy(self, provider: str, field: str, strategy_index: int):
        """Promote a successful strategy to higher priority"""
        strategies = self.kb.get("providers", {}).get(provider, {}).get(field, [])
        if 0 <= strategy_index < len(strategies):
            # Move to front
            strategy = strategies.pop(strategy_index)
            strategies.insert(0, strategy)
            self.save_kb()
    
    def record_success(self, provider: str, field: str, strategy_index: int):
        """Record successful use of a strategy"""
        strategies = self.kb.get("providers", {}).get(provider, {}).get(field, [])
        if 0 <= strategy_index < len(strategies):
            if "success_count" not in strategies[strategy_index]:
                strategies[strategy_index]["success_count"] = 0
            strategies[strategy_index]["success_count"] += 1
            strategies[strategy_index]["last_success"] = datetime.now().isoformat()
            self.save_kb()

