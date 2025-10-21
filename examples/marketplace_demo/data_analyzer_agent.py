#!/usr/bin/env python3
"""
Data Analyzer Agent - Performs statistical analysis on datasets
Real-world capability: analyze trends, compute statistics, generate insights
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
from agent_web import Agent
import statistics
import json

async def handle_analyze_request(sender_did: str, message_body: dict):
    """
    Analyze a dataset and return statistics

    Input:
        - data: list of items to analyze
        - metric: what to analyze ('text_length', 'word_count', 'frequency')

    Output:
        - analysis: statistical insights
        - summary: human-readable summary
    """
    try:
        data = message_body.get("data", [])
        metric = message_body.get("metric", "text_length")

        if not data:
            return {"status": "error", "message": "Data required"}

        print(f"[ANALYZER] Analyzing {len(data)} items...")
        print(f"[ANALYZER] Metric: {metric}")

        values = []
        if metric == "text_length":
            values = [len(item.get("text", "")) for item in data]
        elif metric == "word_count":
            values = [len(item.get("text", "").split()) for item in data]
        elif metric == "frequency":
            word_freq = {}
            for item in data:
                words = item.get("text", "").lower().split()
                for word in words:
                    word_freq[word] = word_freq.get(word, 0) + 1
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            return {
                "status": "success",
                "analysis": {
                    "top_words": top_words,
                    "unique_words": len(word_freq),
                    "total_words": sum(word_freq.values())
                },
                "summary": f"Found {len(word_freq)} unique words. Top word: '{top_words[0][0]}' ({top_words[0][1]} times)"
            }

        if not values:
            return {"status": "error", "message": "No numeric values to analyze"}

        analysis = {
            "count": len(values),
            "mean": round(statistics.mean(values), 2),
            "median": round(statistics.median(values), 2),
            "min": min(values),
            "max": max(values),
            "stdev": round(statistics.stdev(values), 2) if len(values) > 1 else 0
        }

        summary = f"Analyzed {len(values)} items. Average {metric}: {analysis['mean']}, Range: {analysis['min']}-{analysis['max']}"

        print(f"[ANALYZER] ✅ {summary}")

        return {
            "status": "success",
            "analysis": analysis,
            "summary": summary,
            "metric": metric
        }

    except Exception as e:
        print(f"[ANALYZER] ❌ Error: {e}")
        return {"status": "error", "message": str(e)}

async def main():
    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="data_analyzer.key",
        demo_mode=True
    )

    agent.on_message(handle_analyze_request)

    http_host = "127.0.0.1"
    http_port = 9001
    dht_host = "127.0.0.1"
    dht_port = 9101
    bootstrap_node = ("127.0.0.1", 8480)

    listen_task = asyncio.create_task(
        agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node)
    )

    await asyncio.sleep(2)

    await agent.register(
        public_endpoint=f"http://{http_host}:{http_port}",
        capabilities=["data_analyzer"],
        price=0.03,
        payment_method="points"
    )

    print(f"\n📊 Data Analyzer Agent LIVE")
    print(f"   DID: {agent.did[:40]}...")
    print(f"   HTTP: {http_host}:{http_port}")
    print(f"   DHT: {dht_host}:{dht_port}")
    print(f"   Price: $0.03 per analysis\n")

    await listen_task

if __name__ == "__main__":
    asyncio.run(main())
