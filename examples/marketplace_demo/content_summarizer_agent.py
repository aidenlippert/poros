#!/usr/bin/env python3
"""
Content Summarizer Agent - Extracts key points from text
Real-world capability: summarize articles, documents, meeting notes
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
from agent_web import Agent
import re

async def handle_summarize_request(sender_did: str, message_body: dict):
    """
    Summarize text content into key points

    Input:
        - data: list of items with 'text' field
        - max_points: maximum key points to extract (default 5)

    Output:
        - summary: key points extracted
        - original_count: number of items processed
    """
    try:
        data = message_body.get("data", [])
        max_points = message_body.get("max_points", 5)

        if not data:
            return {"status": "error", "message": "Data required"}

        print(f"[SUMMARIZER] Processing {len(data)} items...")
        print(f"[SUMMARIZER] Extracting top {max_points} key points")

        all_text = " ".join([item.get("text", "") for item in data])

        sentences = re.split(r'[.!?]+', all_text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        scored_sentences = []
        for sentence in sentences[:50]:
            score = len(sentence.split())
            if any(word in sentence.lower() for word in ['first', 'new', 'announces', 'launches', 'breaking']):
                score += 10
            scored_sentences.append((score, sentence))

        scored_sentences.sort(reverse=True, key=lambda x: x[0])

        key_points = [sent for score, sent in scored_sentences[:max_points]]

        summary_text = "\n• ".join(key_points)

        print(f"[SUMMARIZER] ✅ Extracted {len(key_points)} key points")

        return {
            "status": "success",
            "summary": key_points,
            "summary_text": "• " + summary_text,
            "original_count": len(data),
            "compression_ratio": f"{len(key_points)}/{len(data)}"
        }

    except Exception as e:
        print(f"[SUMMARIZER] ❌ Error: {e}")
        return {"status": "error", "message": str(e)}

async def main():
    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="content_summarizer.key",
        demo_mode=True
    )

    agent.on_message(handle_summarize_request)

    http_host = "127.0.0.1"
    http_port = 9002
    dht_host = "127.0.0.1"
    dht_port = 9102
    bootstrap_node = ("127.0.0.1", 8480)

    listen_task = asyncio.create_task(
        agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node)
    )

    await asyncio.sleep(2)

    await agent.register(
        public_endpoint=f"http://{http_host}:{http_port}",
        capabilities=["content_summarizer"],
        price=0.02,
        payment_method="points"
    )

    print(f"\n📝 Content Summarizer Agent LIVE")
    print(f"   DID: {agent.did[:40]}...")
    print(f"   HTTP: {http_host}:{http_port}")
    print(f"   DHT: {dht_host}:{dht_port}")
    print(f"   Price: $0.02 per summary\n")

    await listen_task

if __name__ == "__main__":
    asyncio.run(main())
