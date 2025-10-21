#!/usr/bin/env python3
"""
Web Scraper Agent - Extracts structured data from web pages
Real-world capability: scrape product prices, news headlines, job listings, etc.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
from agent_web import Agent
import requests
from bs4 import BeautifulSoup
import json

async def handle_scrape_request(sender_did: str, message_body: dict):
    """
    Scrape structured data from a URL

    Input:
        - url: target URL
        - selector: CSS selector for data extraction
        - limit: max items to extract (default 10)

    Output:
        - data: list of extracted items
        - count: number of items found
    """
    try:
        url = message_body.get("url")
        selector = message_body.get("selector", "h2")
        limit = message_body.get("limit", 10)

        if not url:
            return {"status": "error", "message": "URL required"}

        print(f"[SCRAPER] Fetching {url}...")
        print(f"[SCRAPER] Selector: {selector}, Limit: {limit}")

        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        elements = soup.select(selector)[:limit]

        data = []
        for elem in elements:
            data.append({
                "text": elem.get_text(strip=True),
                "tag": elem.name,
                "href": elem.get('href', '')
            })

        print(f"[SCRAPER] ✅ Extracted {len(data)} items")

        return {
            "status": "success",
            "data": data,
            "count": len(data),
            "source": url
        }

    except Exception as e:
        print(f"[SCRAPER] ❌ Error: {e}")
        return {"status": "error", "message": str(e)}

async def main():
    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="web_scraper.key",
        demo_mode=True
    )

    agent.on_message(handle_scrape_request)

    http_host = "127.0.0.1"
    http_port = 9000
    dht_host = "127.0.0.1"
    dht_port = 9100
    bootstrap_node = ("127.0.0.1", 8480)

    listen_task = asyncio.create_task(
        agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node)
    )

    await asyncio.sleep(2)

    await agent.register(
        public_endpoint=f"http://{http_host}:{http_port}",
        capabilities=["web_scraper"],
        price=0.05,
        payment_method="points"
    )

    print(f"\n🌐 Web Scraper Agent LIVE")
    print(f"   DID: {agent.did[:40]}...")
    print(f"   HTTP: {http_host}:{http_port}")
    print(f"   DHT: {dht_host}:{dht_port}")
    print(f"   Price: $0.05 per scrape\n")

    await listen_task

if __name__ == "__main__":
    asyncio.run(main())
