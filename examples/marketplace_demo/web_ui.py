#!/usr/bin/env python3
"""
Flask Web UI for AI Agent Marketplace
Demonstrates real-world multi-agent orchestration
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from flask import Flask, render_template_string, request, jsonify
import asyncio
from agent_web import Agent
import threading
import time

app = Flask(__name__)

# Global agent and event loop
_agent = None
_loop = None
_ready = False

def init_agent():
    """Initialize the orchestrator agent in background thread"""
    global _agent, _loop, _ready

    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)

    _agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="web_ui_orchestrator.key",
        demo_mode=True
    )

    async def setup():
        global _ready
        try:
            await _agent.listen_and_join("127.0.0.1", 9004, "127.0.0.1", 9104, ("127.0.0.1", 8480))
            await asyncio.sleep(2)
            await _agent.register(
                public_endpoint="http://127.0.0.1:9004",
                capabilities=["orchestrator"],
                price=0.0,
                payment_method="free"
            )
            print(f"[UI] ✅ Orchestrator agent ready: {_agent.did[:40]}...")
            _ready = True
        except Exception as e:
            print(f"[UI] ❌ Setup error: {e}")

    _loop.run_until_complete(setup())
    _loop.run_forever()

# Start agent in background
thread = threading.Thread(target=init_agent, daemon=True)
thread.start()
time.sleep(3)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Agent Marketplace - Real-World Demo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        h1 {
            color: #667eea;
            font-size: 32px;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            font-size: 16px;
        }
        .agents-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .agent-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .agent-card:hover {
            transform: translateY(-5px);
        }
        .agent-icon {
            font-size: 40px;
            margin-bottom: 15px;
        }
        .agent-name {
            font-size: 20px;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }
        .agent-desc {
            color: #666;
            font-size: 14px;
            margin-bottom: 15px;
        }
        .agent-price {
            color: #667eea;
            font-weight: 600;
        }
        .demo-section {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .demo-title {
            font-size: 24px;
            color: #333;
            margin-bottom: 20px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.2s;
        }
        button:hover { opacity: 0.9; }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        #results {
            margin-top: 30px;
        }
        .result-box {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 15px;
            border-left: 4px solid #667eea;
        }
        .step {
            padding: 15px;
            margin-bottom: 10px;
            background: white;
            border-radius: 8px;
            border-left: 3px solid #764ba2;
        }
        .step-title {
            font-weight: 600;
            color: #764ba2;
            margin-bottom: 8px;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Agent Marketplace</h1>
            <p class="subtitle">Decentralized AI services powered by Agent Web Protocol</p>
        </div>

        <div class="agents-grid">
            <div class="agent-card">
                <div class="agent-icon">🌐</div>
                <div class="agent-name">Web Scraper</div>
                <div class="agent-desc">Extracts structured data from any website</div>
                <div class="agent-price">$0.05 per scrape</div>
            </div>

            <div class="agent-card">
                <div class="agent-icon">📊</div>
                <div class="agent-name">Data Analyzer</div>
                <div class="agent-desc">Performs statistical analysis on datasets</div>
                <div class="agent-price">$0.03 per analysis</div>
            </div>

            <div class="agent-card">
                <div class="agent-icon">📝</div>
                <div class="agent-name">Content Summarizer</div>
                <div class="agent-desc">Extracts key points from large text</div>
                <div class="agent-price">$0.02 per summary</div>
            </div>

            <div class="agent-card">
                <div class="agent-icon">🔍</div>
                <div class="agent-name">Market Research</div>
                <div class="agent-desc">Orchestrates agents for market intelligence</div>
                <div class="agent-price">$0.10 per research</div>
            </div>
        </div>

        <div class="demo-section">
            <h2 class="demo-title">🚀 Try Market Research (Multi-Agent Orchestration)</h2>
            <p style="margin-bottom: 20px; color: #666;">
                This demo scrapes a website, analyzes the data, and summarizes findings using 3 different agents
            </p>

            <div class="input-group">
                <label>Website URL:</label>
                <input type="text" id="url" placeholder="https://news.ycombinator.com" value="https://news.ycombinator.com">
            </div>

            <div class="input-group">
                <label>CSS Selector (what to scrape):</label>
                <input type="text" id="selector" placeholder=".titleline > a" value=".titleline > a">
            </div>

            <div class="input-group">
                <label>Analysis Metric:</label>
                <select id="metric">
                    <option value="text_length">Text Length</option>
                    <option value="word_count">Word Count</option>
                    <option value="frequency">Word Frequency</option>
                </select>
            </div>

            <button id="runBtn" onclick="runResearch()">Run Market Research</button>

            <div id="loading" class="loading">
                <div class="spinner"></div>
                <p style="margin-top: 10px; color: #666;">Orchestrating agents...</p>
            </div>

            <div id="results"></div>
        </div>
    </div>

    <script>
        async function runResearch() {
            const url = document.getElementById('url').value;
            const selector = document.getElementById('selector').value;
            const metric = document.getElementById('metric').value;

            const btn = document.getElementById('runBtn');
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');

            btn.disabled = true;
            loading.style.display = 'block';
            results.innerHTML = '';

            try {
                const response = await fetch('/research', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url, selector, metric})
                });

                const data = await response.json();

                if (data.success) {
                    results.innerHTML = `
                        <div class="result-box">
                            <h3 style="margin-bottom: 15px;">Research Complete! 🎉</h3>

                            <div class="step">
                                <div class="step-title">Step 1: Web Scraper Agent</div>
                                <div>Scraped ${data.scrape.count} items from ${data.scrape.source}</div>
                            </div>

                            <div class="step">
                                <div class="step-title">Step 2: Data Analyzer Agent</div>
                                <div>${data.analysis.summary}</div>
                                <div style="margin-top: 8px; font-size: 12px; color: #666;">
                                    ${JSON.stringify(data.analysis.analysis, null, 2)}
                                </div>
                            </div>

                            <div class="step">
                                <div class="step-title">Step 3: Content Summarizer Agent</div>
                                <div style="margin-top: 8px;">${data.summary.summary_text}</div>
                                <div style="margin-top: 8px; color: #666; font-size: 12px;">
                                    Compressed ${data.summary.original_count} items into ${data.summary.summary.length} key points
                                </div>
                            </div>
                        </div>
                    `;
                } else {
                    results.innerHTML = `<div class="result-box" style="border-color: #e74c3c;">
                        <strong>Error:</strong> ${data.error}
                    </div>`;
                }
            } catch (error) {
                results.innerHTML = `<div class="result-box" style="border-color: #e74c3c;">
                    <strong>Error:</strong> ${error.message}
                </div>`;
            }

            btn.disabled = false;
            loading.style.display = 'none';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/research', methods=['POST'])
def research():
    """Orchestrate multiple agents for market research"""
    if not _ready:
        return jsonify({"success": False, "error": "Agent not ready"}), 503

    data = request.json
    url = data.get('url')
    selector = data.get('selector', 'h2')
    metric = data.get('metric', 'text_length')

    async def run_research():
        try:
            # Step 1: Scrape website
            print(f"[UI] Step 1: Scraping {url}...")
            scrape_response = await _agent.execute_task(
                capability="web_scraper",
                message_body={"url": url, "selector": selector, "limit": 10}
            )

            if scrape_response.get("status") != "success":
                return {"success": False, "error": f"Scraping failed: {scrape_response.get('message')}"}

            scraped_data = scrape_response.get("data", [])
            print(f"[UI] ✅ Scraped {len(scraped_data)} items")

            # Step 2: Analyze data
            print(f"[UI] Step 2: Analyzing data...")
            analysis_response = await _agent.execute_task(
                capability="data_analyzer",
                message_body={"data": scraped_data, "metric": metric}
            )

            if analysis_response.get("status") != "success":
                return {"success": False, "error": f"Analysis failed: {analysis_response.get('message')}"}

            print(f"[UI] ✅ {analysis_response.get('summary')}")

            # Step 3: Summarize content
            print(f"[UI] Step 3: Summarizing content...")
            summary_response = await _agent.execute_task(
                capability="content_summarizer",
                message_body={"data": scraped_data, "max_points": 5}
            )

            if summary_response.get("status") != "success":
                return {"success": False, "error": f"Summarization failed: {summary_response.get('message')}"}

            print(f"[UI] ✅ Summarized to {len(summary_response.get('summary', []))} key points")

            return {
                "success": True,
                "scrape": scrape_response,
                "analysis": analysis_response,
                "summary": summary_response
            }

        except Exception as e:
            print(f"[UI] ❌ Error: {e}")
            return {"success": False, "error": str(e)}

    # Run in event loop
    future = asyncio.run_coroutine_threadsafe(run_research(), _loop)
    result = future.result(timeout=30)

    return jsonify(result)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌐 AI Agent Marketplace Web UI")
    print("="*60)
    print(f"\n✅ Open http://localhost:5000 in your browser\n")
    app.run(debug=False, port=5000)
