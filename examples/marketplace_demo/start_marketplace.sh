#!/bin/bash

# AI Agent Marketplace - Startup Script
# Starts all specialist agents and the web UI

cd "$(dirname "$0")"
cd ../..

echo "=================================="
echo "🤖 AI Agent Marketplace"
echo "=================================="
echo ""
echo "Starting specialist agents..."
echo ""

# Start Web Scraper Agent
echo "🌐 Starting Web Scraper Agent (port 9000)..."
nohup ./venv/bin/python3 examples/marketplace_demo/web_scraper_agent.py > /tmp/web_scraper.log 2>&1 &
sleep 2

# Start Data Analyzer Agent
echo "📊 Starting Data Analyzer Agent (port 9001)..."
nohup ./venv/bin/python3 examples/marketplace_demo/data_analyzer_agent.py > /tmp/data_analyzer.log 2>&1 &
sleep 2

# Start Content Summarizer Agent
echo "📝 Starting Content Summarizer Agent (port 9002)..."
nohup ./venv/bin/python3 examples/marketplace_demo/content_summarizer_agent.py > /tmp/content_summarizer.log 2>&1 &
sleep 2

echo ""
echo "✅ All agents running!"
echo ""
echo "Starting Web UI..."
echo ""

# Start Flask Web UI
./venv/bin/python3 examples/marketplace_demo/web_ui.py
