#!/usr/bin/env python3
"""
Railway Deployment - All-in-One Service
Runs chat UI with embedded agents (no DHT/P2P required for MVP)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import os
import asyncio
from flask import Flask, render_template_string, request, jsonify
import re

app = Flask(__name__)

# In-memory agent registry (no DHT for now)
_agents = {}

def register_agent(capability, handler):
    """Register an agent capability with its handler"""
    _agents[capability] = handler
    print(f"✅ Registered agent: {capability}")

# Import agent handlers directly
async def web_scraper_handler(message_body):
    """Web scraper - embedded version"""
    from bs4 import BeautifulSoup
    import requests

    url = message_body.get('url')
    selector = message_body.get('selector', '.titleline > a')
    limit = message_body.get('limit', 20)

    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.select(selector)

        data = []
        for elem in elements[:limit]:
            text = elem.get_text(strip=True)
            if text:
                data.append(text)

        return {
            "status": "success",
            "data": data,
            "count": len(data)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def data_analyzer_handler(message_body):
    """Data analyzer - embedded version"""
    data = message_body.get('data', [])

    if not data:
        return {"status": "error", "message": "No data provided"}

    text_data = [str(item) for item in data]

    analysis = {
        "total_items": len(text_data),
        "total_characters": sum(len(item) for item in text_data),
        "avg_length": sum(len(item) for item in text_data) / len(text_data) if text_data else 0,
        "shortest": min(text_data, key=len) if text_data else "",
        "longest": max(text_data, key=len) if text_data else ""
    }

    return {
        "status": "success",
        "analysis": analysis
    }

async def content_summarizer_handler(message_body):
    """Content summarizer - embedded version"""
    data = message_body.get('data', [])
    max_points = message_body.get('max_points', 5)

    if not data:
        return {"status": "error", "message": "No data provided"}

    # Simple summarization: take first N items
    summary_points = []
    for i, item in enumerate(data[:max_points], 1):
        summary_points.append(f"{i}. {str(item)[:100]}...")

    return {
        "status": "success",
        "summary": summary_points
    }

async def flight_search_handler(message_body):
    """Flight search - embedded version"""
    import random
    from datetime import datetime, timedelta

    origin = message_body.get("origin", "").upper()
    destination = message_body.get("destination", "").upper()
    date_str = message_body.get("date", "tomorrow")
    time_pref = message_body.get("time_preference", "any")
    budget = message_body.get("budget", "any")
    nonstop = message_body.get("nonstop", False)

    # Parse date
    today = datetime.now()
    if "tomorrow" in date_str.lower():
        travel_date = today + timedelta(days=1)
    elif "today" in date_str.lower():
        travel_date = today
    else:
        travel_date = today + timedelta(days=1)

    date_formatted = travel_date.strftime("%Y-%m-%d")

    # Generate sample flights
    flights = []
    if time_pref in ["morning", "any"]:
        flights.append({
            "airline": "Alaska Airlines",
            "flight_number": "AS1234",
            "departure": "06:30 AM",
            "arrival": "09:15 AM",
            "duration": "2h 45m",
            "price": "$127",
            "nonstop": True
        })

    if time_pref in ["afternoon", "any"]:
        flights.append({
            "airline": "United",
            "flight_number": "UA9012",
            "departure": "01:20 PM",
            "arrival": "04:05 PM",
            "duration": "2h 45m",
            "price": "$156",
            "nonstop": True
        })

    # Sort by price if cheapest
    if budget == "cheapest":
        flights.sort(key=lambda f: float(f["price"].replace("$", "")))

    return {
        "status": "success",
        "origin": origin,
        "destination": destination,
        "date": date_formatted,
        "results": [{
            "source": "Google Flights",
            "flights": flights[:3]
        }]
    }

# Register all agents
register_agent("web_scraper", web_scraper_handler)
register_agent("data_analyzer", data_analyzer_handler)
register_agent("content_summarizer", content_summarizer_handler)
register_agent("flight_search", flight_search_handler)

# Simple orchestrator
async def intelligent_route(user_query: str):
    """Route queries to appropriate agents"""
    query_lower = user_query.lower()

    # Detect intent
    needs_flight = any(word in query_lower for word in ['flight', 'fly', 'plane'])
    needs_scraping = any(word in query_lower for word in ['scrape', 'fetch', 'get', 'find'])
    needs_analysis = any(word in query_lower for word in ['analyze', 'statistics'])
    needs_summary = any(word in query_lower for word in ['summarize', 'summary'])

    # Extract URL
    url_match = re.search(r'(https?://[^\s]+|(?:[a-z0-9-]+\.)+[a-z]{2,})', query_lower)
    url = url_match.group(0) if url_match else None
    if url and not url.startswith('http'):
        url = f'https://{url}'

    steps = []
    results = {}

    # Execute agents
    if needs_scraping and url:
        steps.append({"text": f"🌐 Scraping {url}", "completed": False})
        try:
            result = await _agents["web_scraper"]({"url": url, "selector": ".titleline > a, h1, h2", "limit": 20})
            if result.get("status") == "success":
                results['scrape'] = result['data']
                steps[-1]["completed"] = True
        except Exception as e:
            steps[-1]["text"] += f" (error: {str(e)})"

    if needs_analysis and results.get('scrape'):
        steps.append({"text": "📊 Analyzing data", "completed": False})
        try:
            result = await _agents["data_analyzer"]({"data": results['scrape']})
            if result.get("status") == "success":
                results['analysis'] = result['analysis']
                steps[-1]["completed"] = True
        except Exception as e:
            steps[-1]["text"] += f" (error: {str(e)})"

    if needs_summary and results.get('scrape'):
        steps.append({"text": "📝 Summarizing", "completed": False})
        try:
            result = await _agents["content_summarizer"]({"data": results['scrape'], "max_points": 5})
            if result.get("status") == "success":
                results['summary'] = result['summary']
                steps[-1]["completed"] = True
        except Exception as e:
            steps[-1]["text"] += f" (error: {str(e)})"

    # Format response
    if results:
        response = []
        if results.get('scrape'):
            response.append(f"📦 Found {len(results['scrape'])} items from {url}")
            response.append(f"\nFirst few items: {', '.join(results['scrape'][:3])}...")

        if results.get('summary'):
            response.append("\n\n📝 Key Points:")
            response.extend(results['summary'])

        if results.get('analysis'):
            analysis = results['analysis']
            response.append(f"\n\n📊 Analysis:")
            response.append(f"  • Total items: {analysis['total_items']}")
            response.append(f"  • Avg length: {analysis['avg_length']:.0f} characters")

        return {
            "success": True,
            "response": "\n".join(response),
            "orchestration_steps": steps
        }

    return {
        "success": True,
        "response": "I can help you scrape websites, analyze data, or summarize content! Try asking me to scrape a URL.",
        "orchestration_steps": []
    }

# Flask routes
@app.route('/')
def home():
    """Serve the chat UI"""
    # Use the same HTML from chat_ui.py but simplified
    from examples.marketplace_demo.chat_ui import HTML_TEMPLATE
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        message = data.get('message', '')

        if not message:
            return jsonify({"success": False, "error": "No message provided"})

        # Run async route
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(intelligent_route(message))
        loop.close()

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Agent Web Marketplace - Railway Deployment")
    print("=" * 60)
    print("\n✅ All agents loaded (embedded mode)")
    print("  • Web Scraper")
    print("  • Data Analyzer")
    print("  • Content Summarizer")
    print("  • Flight Search")

    port = int(os.getenv('PORT', 5001))
    print(f"\n🚀 Starting server on port {port}...")

    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
