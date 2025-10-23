# 🤖 Ollama AI Integration Guide

## **How AI Intervenes in the Self-Healing Scraper**

Your self-healing scraper now uses **Ollama with GPT-OSS** for real AI intervention! Here's exactly how it works:

### **🎯 AI Intervention Flow**

```
1. Selector Fails → 2. Check Ollama → 3. AI Analysis → 4. Generate Strategy → 5. Test & Learn
```

### **🔧 Where AI Intervenes**

#### **1. When All Selector Strategies Fail**
```python
# In penske_adapter.py - Line 114-125
if pickup_loc:
    # Normal flow - strategies worked
    await pickup_loc.fill(pickup_zip)
else:
    # 🤖 AI INTERVENTION POINT #1
    print("🤖 Trying AI repair for pickup input...")
    pickup_loc, new_strategy = await self.finder.find_with_ai_repair(...)
```

#### **2. Ollama AI Analysis**
```python
# In resilient_finder.py - Line 74-79
if self.ollama_repair.check_ollama_available():
    print(f"🤖 Using Ollama AI for {field} repair...")
    new_strategy = self.ollama_repair.propose_strategy_with_ollama(...)
else:
    print(f"🤖 Ollama not available, using heuristic AI...")
    new_strategy = self._ai_propose_strategy(...)
```

#### **3. AI Learning & Knowledge Base**
```python
# In resilient_finder.py - Line 85-87
if locator and await self._validate_locator(locator):
    # 🤖 AI learns - adds successful strategy to KB
    self.kb.add_strategy(provider, field, new_strategy, position=0)
    print(f"✅ AI repair successful for {field}: {new_strategy}")
```

### **🧠 How Ollama AI Works**

#### **Step 1: AI Receives Context**
- **Field**: What element we're looking for (e.g., "pickup_input")
- **DOM Snippet**: Current page structure (first 2000 chars)
- **Failed Strategies**: What didn't work
- **Provider**: Website being scraped ("penske")

#### **Step 2: AI Analyzes DOM**
Ollama GPT-OSS analyzes the DOM and looks for:
- `data-test` attributes
- `aria-label` attributes  
- `placeholder` text patterns
- `class` and `id` patterns
- Semantic HTML structure

#### **Step 3: AI Generates Strategy**
Ollama returns a JSON strategy like:
```json
{
  "strategy": "css",
  "params": {
    "selector": "input[data-test='pickup-location']"
  }
}
```

#### **Step 4: AI Tests & Learns**
- Tests the new strategy
- If successful → Adds to knowledge base
- If failed → Tries next approach

### **🎯 Real AI Intervention Examples**

#### **Example 1: Pickup Field Not Found**
```
Trigger: All 9 pickup_input strategies fail
AI Input: DOM with "From: City, State or ZIP" input
AI Output: {"strategy": "css", "params": {"selector": "input[placeholder*='from' i]"}}
Result: ✅ Successfully finds pickup field
```

#### **Example 2: Submit Button Missing**
```
Trigger: No submit button found with standard selectors
AI Input: DOM with custom button classes
AI Output: {"strategy": "css", "params": {"selector": "button[class*='primary-btn']"}}
Result: ✅ Successfully clicks submit
```

#### **Example 3: Result Cards Changed**
```
Trigger: Result cards not found after form submission
AI Input: DOM with new card layout
AI Output: {"strategy": "css", "params": {"selector": "[data-testid='quote-card']"}}
Result: ✅ Successfully extracts pricing data
```

### **🚀 Running with Ollama AI**

#### **Start Ollama (if not running)**
```bash
ollama serve
```

#### **Test the AI Integration**
```bash
# Test Ollama AI directly
python ollama_ai_repair.py

# Test full scraper with AI
python demo_ai_intervention.py

# Test API endpoint with AI
curl -X POST http://localhost:8080/quotes/penske \
  -H 'Content-Type: application/json' \
  -d '{
        "pickup_zip": "19103",
        "dropoff_zip": "10001",
        "pickup_date": "2025-11-10",
        "dropoff_date": "2025-11-12",
        "headless": false
      }'
```

### **📊 AI Performance Monitoring**

Watch for these messages to see AI in action:

```
🤖 Using Ollama AI for pickup_input repair...
🤖 Ollama response: {"strategy":"css","params":{"selector":"input[data-test='pickup-location']"}}...
✅ AI repair successful for pickup_input: {'strategy': 'css', 'params': {'selector': "input[data-test='pickup-location']"}}
```

### **🔧 AI Configuration**

#### **Ollama Settings**
- **Model**: `gpt-oss` (your local model)
- **Temperature**: `0.1` (focused responses)
- **Max Tokens**: `500` (sufficient for JSON responses)
- **Base URL**: `http://localhost:11434`

#### **AI Prompt Engineering**
The AI receives a carefully crafted prompt that:
- Explains the scraping context
- Shows failed strategies
- Provides DOM structure
- Requests specific JSON format
- Includes examples

### **🎉 Benefits of Ollama AI Integration**

1. **Real Intelligence**: Uses GPT-OSS for actual AI analysis
2. **Local Processing**: No external API calls, completely private
3. **Learning**: AI strategies are saved to knowledge base
4. **Fallback**: Heuristic AI if Ollama unavailable
5. **Adaptive**: Gets smarter with each successful repair

### **🔮 Future Enhancements**

1. **Multi-Model Support**: Add other Ollama models
2. **Learning Database**: Store successful patterns
3. **Pattern Recognition**: Learn from repeated successes
4. **Cross-Site Learning**: Apply learnings across different websites
5. **Performance Metrics**: Track AI success rates

---

**Your self-healing scraper now has real AI intelligence! 🎉**
