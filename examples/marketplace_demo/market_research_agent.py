#!/usr/bin/env python3
"""
Market Research Agent - Orchestrates multiple agents for comprehensive research
Real-world use case: competitive analysis, trend research, market intelligence
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
from agent_web import Agent
import json

async def handle_research_request(sender_did: str, message_body: dict):
    """
    Conduct market research by orchestrating multiple specialist agents

    Input:
        - url: website to research
        - topic: what to focus on

    Output:
        - research: comprehensive market research report
    """
    return {"status": "info", "message": "This agent orchestrates via the web UI"}

async def main():
    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="market_research.key",
        demo_mode=True
    )

    agent.on_message(handle_research_request)

    http_host = "127.0.0.1"
    http_port = 9003
    dht_host = "127.0.0.1"
    dht_port = 9103
    bootstrap_node = ("127.0.0.1", 8480)

    listen_task = asyncio.create_task(
        agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node)
    )

    await asyncio.sleep(2)

    await agent.register(
        public_endpoint=f"http://{http_host}:{http_port}",
        capabilities=["market_research"],
        price=0.10,
        payment_method="points"
    )

    print(f"\n🔍 Market Research Agent LIVE")
    print(f"   DID: {agent.did[:40]}...")
    print(f"   HTTP: {http_host}:{http_port}")
    print(f"   DHT: {dht_host}:{dht_port}")
    print(f"   Price: $0.10 per research task\n")
    print(f"   Orchestrates: Web Scraper + Data Analyzer + Content Summarizer\n")

    await listen_task

if __name__ == "__main__":
    asyncio.run(main())
