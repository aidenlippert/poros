# 🤖 Agent Developer Guide - Build Your Own AI Agent

## Quick Start: Deploy Your First Agent in 10 Minutes

### Step 1: Set Up Your Environment

```bash
cd /home/rocz/agenticwebbeta

# Make sure you have the virtual environment
source venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt
```

### Step 2: Create Your Agent File

Let's build a **Weather Agent** as an example:

```python
#!/usr/bin/env python3
"""
Weather Agent - Provides weather information for cities
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
from agent_web import Agent
import random  # For demo data

async def handle_weather_request(sender_did: str, message_body: dict):
    """
    Get weather information for a city

    Input:
        - city: city name (e.g., "Seattle", "New York", "London")
        - units: "celsius" or "fahrenheit" (default: fahrenheit)

    Output:
        - temperature: current temperature
        - conditions: weather conditions
        - humidity: humidity percentage
        - forecast: 3-day forecast
    """

    city = message_body.get("city", "")
    units = message_body.get("units", "fahrenheit")

    print(f"[WEATHER] Looking up weather for {city} ({units})")

    if not city:
        return {
            "status": "error",
            "message": "City name required"
        }

    # In production, you would call a real weather API here
    # For demo, generate sample data

    temp_c = random.randint(-10, 35)
    temp_f = (temp_c * 9/5) + 32

    conditions = random.choice([
        "Sunny", "Partly Cloudy", "Cloudy",
        "Light Rain", "Rainy", "Clear"
    ])

    humidity = random.randint(30, 90)

    return {
        "status": "success",
        "city": city,
        "current": {
            "temperature": temp_f if units == "fahrenheit" else temp_c,
            "units": "°F" if units == "fahrenheit" else "°C",
            "conditions": conditions,
            "humidity": f"{humidity}%"
        },
        "forecast": [
            {"day": "Tomorrow", "high": temp_f + 5, "low": temp_f - 3, "conditions": "Sunny"},
            {"day": "Day 2", "high": temp_f + 2, "low": temp_f - 5, "conditions": "Cloudy"},
            {"day": "Day 3", "high": temp_f + 1, "low": temp_f - 4, "conditions": "Partly Cloudy"}
        ]
    }

async def main():
    # Create agent
    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="weather_agent.key",
        demo_mode=True
    )

    # Set up message handler
    agent.on_message(handle_weather_request)

    # Configure ports (make sure these are unique!)
    http_host = "127.0.0.1"
    http_port = 9007  # Choose an unused port
    dht_host = "127.0.0.1"
    dht_port = 9107   # Choose an unused port
    bootstrap_node = ("127.0.0.1", 8480)

    # Start listening
    listen_task = asyncio.create_task(
        agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node)
    )

    await asyncio.sleep(2)

    # Register capabilities
    await agent.register(
        public_endpoint=f"http://{http_host}:{http_port}",
        capabilities=["weather"],  # This is how users will find you
        price=0.01,  # $0.01 per request
        payment_method="points"
    )

    print(f"\n🌤️  Weather Agent LIVE")
    print(f"   DID: {agent.did[:40]}...")
    print(f"   HTTP: {http_host}:{http_port}")
    print(f"   DHT: {dht_host}:{dht_port}")
    print(f"   Capability: weather")
    print(f"   Price: $0.01 per request\n")

    await listen_task

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 3: Run Your Agent

```bash
# Save the file
nano examples/marketplace_demo/weather_agent.py
# (paste the code above)

# Make it executable
chmod +x examples/marketplace_demo/weather_agent.py

# Run it
./venv/bin/python3 examples/marketplace_demo/weather_agent.py > /tmp/weather_agent.log 2>&1 &

# Check it's running
tail -f /tmp/weather_agent.log
```

### Step 4: Update the Orchestrator to Use Your Agent

Edit `chat_ui.py` to detect weather requests:

```python
# Add to intelligent_route() function

needs_weather = any(word in query_lower for word in ['weather', 'temperature', 'forecast', 'clima'])

# Add weather handling
if needs_weather:
    # Extract city
    city_match = re.search(r'(?:in|for|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', user_query)
    city = city_match.group(1) if city_match else None

    if city:
        steps.append({"text": f"🌤️  Weather: Looking up {city}", "completed": False})
        try:
            weather_result = await _agent.execute_task(
                capability="weather",
                message_body={"city": city, "units": "fahrenheit"}
            )
            if weather_result.get("status") == "success":
                results['weather'] = weather_result
                steps[-1]["completed"] = True
        except Exception as e:
            steps[-1]["text"] += f" (error: {str(e)})"
```

### Step 5: Test It!

Open http://localhost:5001 and type:
```
What's the weather in Seattle?
```

You should see your weather agent respond!

---

## More Agent Ideas

### 1. Currency Converter Agent
```python
async def handle_currency_conversion(sender_did: str, message_body: dict):
    """Convert between currencies"""
    amount = message_body.get("amount")
    from_currency = message_body.get("from", "USD")
    to_currency = message_body.get("to", "EUR")

    # Call real API: exchangerate-api.com
    rate = await fetch_exchange_rate(from_currency, to_currency)
    converted = amount * rate

    return {
        "status": "success",
        "amount": amount,
        "from": from_currency,
        "to": to_currency,
        "result": converted,
        "rate": rate
    }
```

### 2. Code Formatter Agent
```python
async def handle_code_format(sender_did: str, message_body: dict):
    """Format code in various languages"""
    code = message_body.get("code")
    language = message_body.get("language", "python")

    if language == "python":
        import black
        formatted = black.format_str(code, mode=black.Mode())
    elif language == "javascript":
        # Use prettier via subprocess
        formatted = await run_prettier(code)

    return {
        "status": "success",
        "formatted_code": formatted
    }
```

### 3. Image Optimization Agent
```python
async def handle_image_optimize(sender_did: str, message_body: dict):
    """Optimize and resize images"""
    from PIL import Image
    import io

    image_url = message_body.get("url")
    max_width = message_body.get("max_width", 1920)
    quality = message_body.get("quality", 85)

    # Download image
    image_data = await download_image(image_url)
    img = Image.open(io.BytesIO(image_data))

    # Resize if needed
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    # Optimize
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)

    return {
        "status": "success",
        "original_size": len(image_data),
        "optimized_size": len(output.getvalue()),
        "savings": f"{(1 - len(output.getvalue())/len(image_data)) * 100:.1f}%",
        "optimized_image": base64.b64encode(output.getvalue()).decode()
    }
```

### 4. SQL Query Generator Agent
```python
async def handle_sql_generation(sender_did: str, message_body: dict):
    """Generate SQL queries from natural language"""
    import anthropic  # Or OpenAI

    description = message_body.get("description")
    schema = message_body.get("schema")

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""Given this database schema:
    {schema}

    Generate a SQL query that: {description}

    Return only the SQL query, no explanation."""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    sql_query = response.content[0].text

    return {
        "status": "success",
        "query": sql_query
    }
```

### 5. Email Summarizer Agent
```python
async def handle_email_summary(sender_did: str, message_body: dict):
    """Summarize long emails"""
    email_content = message_body.get("content")
    max_length = message_body.get("max_length", 100)

    # Use AI to summarize
    summary = await ai_summarize(email_content, max_words=max_length)

    # Extract key info
    action_items = extract_action_items(email_content)
    important_dates = extract_dates(email_content)

    return {
        "status": "success",
        "summary": summary,
        "action_items": action_items,
        "important_dates": important_dates,
        "word_count": len(email_content.split()),
        "summary_word_count": len(summary.split())
    }
```

---

## Agent Deployment Checklist

### Before Launch
- [ ] Test handler with various inputs
- [ ] Handle error cases gracefully
- [ ] Add logging for debugging
- [ ] Set appropriate pricing
- [ ] Choose unique port numbers
- [ ] Test with orchestrator

### Production Considerations
- [ ] Use environment variables for secrets
- [ ] Add rate limiting
- [ ] Implement caching (Redis)
- [ ] Monitor uptime
- [ ] Set up alerts
- [ ] Document your API
- [ ] Add health check endpoint
- [ ] Use HTTPS for public endpoints

### Monetization
- [ ] Research competitive pricing
- [ ] Offer free tier for testing
- [ ] Volume discounts for high usage
- [ ] Premium features (faster, more accurate)
- [ ] Subscription option

---

## Agent Port Reference

**Reserved Ports (Don't Use):**
- 8480: Bootstrap DHT node
- 9000-9002: Web scraper, analyzer, summarizer
- 9005: Chat orchestrator
- 9006: Flight search

**Available Ports for Your Agents:**
- 9007-9099: HTTP
- 9107-9199: DHT

**Example Allocation:**
```
Weather Agent:     HTTP 9007, DHT 9107
Currency Agent:    HTTP 9008, DHT 9108
Code Format:       HTTP 9009, DHT 9109
Image Optimize:    HTTP 9010, DHT 9110
SQL Generator:     HTTP 9011, DHT 9111
```

---

## Making Money with Agents

### Pricing Strategies

**1. Per-Request Pricing**
```python
await agent.register(
    capabilities=["image_resize"],
    price=0.02,  # $0.02 per image
    payment_method="points"
)
```

**2. Tiered Pricing**
```python
# Basic tier
if request_count < 100:
    price = 0.05
# Pro tier (volume discount)
elif request_count < 1000:
    price = 0.03
# Enterprise tier
else:
    price = 0.01
```

**3. Time-Based Pricing**
```python
# Higher price during peak hours
current_hour = datetime.now().hour
if 9 <= current_hour <= 17:  # Business hours
    price = 0.10
else:  # Off-peak
    price = 0.05
```

**4. Freemium Model**
```python
# Free for first 10 requests per day
if daily_request_count <= 10:
    price = 0.00
else:
    price = 0.05
```

### Revenue Estimates

**Example: Image Optimization Agent**
- Price: $0.02 per image
- Daily requests: 1,000
- Monthly revenue: $600
- Costs (hosting): ~$50/month
- **Net profit: $550/month**

**Example: SQL Query Generator**
- Price: $0.10 per query
- Daily requests: 200
- Monthly revenue: $600
- Costs (API fees + hosting): ~$200/month
- **Net profit: $400/month**

**Example: Web Scraper (High Volume)**
- Price: $0.05 per scrape
- Daily requests: 5,000
- Monthly revenue: $7,500
- Costs (proxies + hosting): ~$500/month
- **Net profit: $7,000/month**

---

## Next Steps

1. **Build your agent** using the template above
2. **Test thoroughly** with edge cases
3. **Deploy to production** server (AWS, DigitalOcean, etc.)
4. **Monitor performance** and uptime
5. **Iterate based on feedback**
6. **Scale as demand grows**

## Questions?

Check out:
- `ROADMAP.md` - Long-term platform vision
- `FINAL_DEMO.md` - Working demo features
- `README.md` - Project overview

Or explore existing agents in `examples/marketplace_demo/` for inspiration!
