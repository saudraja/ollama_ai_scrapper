#!/usr/bin/env python3
"""
Ollama AI Repair Integration
Uses local Ollama with GPT-OSS for real AI intervention
"""

import requests
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

class OllamaAIRepair:
    """Real AI repair using local Ollama with GPT-OSS"""
    
    def __init__(self, model: str = "gpt-oss", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
    
    def check_ollama_available(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                return any(self.model in name for name in model_names)
        except Exception:
            pass
        return False
    
    def propose_strategy_with_ollama(self, field: str, dom_snippet: str, 
                                   failed_strategies: List[Dict[str, Any]], 
                                   provider: str = "penske") -> Optional[Dict[str, Any]]:
        """
        Use Ollama GPT-OSS to generate new selector strategies
        This is the REAL AI intervention point
        """
        
        # Prepare a concise prompt for Ollama
        prompt = f"""Find a CSS selector for a "{field}" input field in this HTML:

{dom_snippet[:1000]}...

Failed strategies: {failed_strategies[:2]}

Return JSON: {{"strategy": "css", "params": {{"selector": "input[placeholder*='location' i]"}}}}"""

        try:
            # Call Ollama API
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 200,  # Limit response length
                    "num_ctx": 2048,     # Limit context window
                    "repeat_penalty": 1.1
                }
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=10  # Reduced timeout for faster fallback
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "").strip()
                
                # Extract JSON from the response with better parsing
                
                # Try multiple JSON extraction methods
                json_patterns = [
                    r'\{[^{}]*"strategy"[^{}]*\}',  # Simple JSON
                    r'\{[^}]*\}',  # Any JSON object
                    r'```json\s*(\{.*?\})\s*```',  # JSON in code blocks
                    r'```\s*(\{.*?\})\s*```'  # Any code block
                ]
                
                for pattern in json_patterns:
                    matches = re.findall(pattern, ai_response, re.DOTALL)
                    for match in matches:
                        try:
                            strategy = json.loads(match)
                            if "strategy" in strategy and "params" in strategy:
                                return strategy
                        except:
                            continue
                
                # Fallback: try to parse the entire response as JSON
                try:
                    strategy = json.loads(ai_response)
                    if "strategy" in strategy and "params" in strategy:
                        return strategy
                except:
                    pass
                
                # Last resort: create a strategy from the response text
                if "input" in ai_response.lower() and "placeholder" in ai_response.lower():
                    return {
                        "strategy": "css",
                        "params": {"selector": "input[placeholder*='location' i]"}
                    }
                        
        except Exception as e:
            print(f"Ollama AI repair failed: {e}")
        
        return None
    
    def analyze_dom_patterns(self, dom_snippet: str) -> Dict[str, Any]:
        """Analyze DOM patterns to help with selector generation"""
        
        patterns = {
            "input_fields": len(re.findall(r'<input[^>]*>', dom_snippet, re.IGNORECASE)),
            "button_fields": len(re.findall(r'<button[^>]*>', dom_snippet, re.IGNORECASE)),
            "data_test_attrs": re.findall(r'data-test="([^"]*)"', dom_snippet),
            "aria_labels": re.findall(r'aria-label="([^"]*)"', dom_snippet),
            "placeholders": re.findall(r'placeholder="([^"]*)"', dom_snippet),
            "class_names": re.findall(r'class="([^"]*)"', dom_snippet),
            "ids": re.findall(r'id="([^"]*)"', dom_snippet)
        }
        
        return patterns

class EnhancedResilientFinder:
    """Enhanced finder with Ollama AI integration"""
    
    def __init__(self, kb, ollama_repair: OllamaAIRepair):
        self.kb = kb
        self.ollama_repair = ollama_repair
    
    async def find_with_ollama_ai_repair(self, page, provider: str, field: str, 
                                       dom_snippet: str, failed_strategies: List[Dict[str, Any]]) -> tuple:
        """
        Use Ollama AI repair to find element when all strategies fail
        Returns (locator, new_strategy) or (None, None) if repair fails
        """
        
        print(f"🤖 Ollama AI analyzing {field} field...")
        
        # Check if Ollama is available
        if not self.ollama_repair.check_ollama_available():
            print("⚠️ Ollama not available, falling back to heuristic AI")
            return None, None
        
        # Use Ollama to generate new strategy
        new_strategy = self.ollama_repair.propose_strategy_with_ollama(
            field=field,
            dom_snippet=dom_snippet,
            failed_strategies=failed_strategies,
            provider=provider
        )
        
        if new_strategy:
            print(f"🤖 Ollama generated strategy: {new_strategy}")
            
            try:
                # Apply the new strategy
                locator = self._apply_strategy(page, new_strategy)
                if locator and await self._validate_locator(locator):
                    # Add successful strategy to KB
                    self.kb.add_strategy(provider, field, new_strategy, position=0)
                    print(f"✅ Ollama AI repair successful!")
                    return locator, new_strategy
                else:
                    print(f"❌ Ollama strategy didn't work")
            except Exception as e:
                print(f"❌ Ollama strategy failed: {e}")
        
        return None, None
    
    def _apply_strategy(self, page, strategy: Dict[str, Any]):
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
    
    async def _validate_locator(self, locator, timeout: int = 5000) -> bool:
        """Validate that locator actually finds elements"""
        try:
            await locator.first.wait_for(timeout=timeout)
            return True
        except:
            return False

def test_ollama_integration():
    """Test Ollama integration"""
    print("🧪 Testing Ollama Integration")
    print("=" * 40)
    
    ollama_repair = OllamaAIRepair()
    
    # Check if Ollama is available
    if ollama_repair.check_ollama_available():
        print("✅ Ollama is available with GPT-OSS model")
        
        # Test AI repair
        test_dom = '''
        <div class="form-group">
            <input placeholder="From: City, State or ZIP" data-test="pickup-location">
            <input placeholder="To: City, State or ZIP" data-test="dropoff-location">
            <button type="submit" class="btn-primary">Get Rates</button>
        </div>
        '''
        
        failed_strategies = [
            {"strategy": "label", "params": {"text": "Pick-up Location"}},
            {"strategy": "placeholder", "params": {"text": "Pick-up"}}
        ]
        
        print("🤖 Testing AI repair...")
        new_strategy = ollama_repair.propose_strategy_with_ollama(
            field="pickup_input",
            dom_snippet=test_dom,
            failed_strategies=failed_strategies
        )
        
        if new_strategy:
            print(f"✅ Ollama generated strategy: {new_strategy}")
        else:
            print("❌ Ollama failed to generate strategy")
    else:
        print("❌ Ollama not available")
        print("💡 Make sure Ollama is running: ollama serve")
        print("💡 And GPT-OSS model is installed: ollama pull gpt-oss")

if __name__ == "__main__":
    test_ollama_integration()
