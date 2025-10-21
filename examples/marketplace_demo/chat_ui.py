#!/usr/bin/env python3
"""
Conversational AI Agent Marketplace
Talk to an orchestrator that automatically finds and coordinates specialist agents
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from flask import Flask, render_template_string, request, jsonify
from agent_web import Agent
import asyncio
import threading
import re

app = Flask(__name__)

_agent = None
_loop = None
_ready = False
_conversation_context = {}  # Store conversation context by session

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Agent Chat - Conversational Marketplace</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .chat-container {
            width: 100%;
            max-width: 800px;
            height: 90vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }

        .chat-header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }

        .chat-header p {
            font-size: 14px;
            opacity: 0.9;
        }

        .agent-status {
            background: rgba(255,255,255,0.1);
            padding: 10px;
            margin-top: 10px;
            border-radius: 10px;
            font-size: 12px;
        }

        .agent-list {
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 5px;
        }

        .agent-badge {
            background: rgba(255,255,255,0.2);
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 11px;
        }

        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f5f5f5;
        }

        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message.user {
            flex-direction: row-reverse;
        }

        .message-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            flex-shrink: 0;
        }

        .message.user .message-avatar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin-left: 10px;
        }

        .message.agent .message-avatar {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            margin-right: 10px;
        }

        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            line-height: 1.4;
        }

        .message.user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .message.agent .message-content {
            background: white;
            color: #333;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        .agent-thinking {
            font-style: italic;
            color: #666;
            font-size: 14px;
        }

        .orchestration-steps {
            margin-top: 10px;
            padding: 10px;
            background: #f9f9f9;
            border-radius: 10px;
            font-size: 13px;
        }

        .step {
            padding: 5px 0;
            border-left: 3px solid #667eea;
            padding-left: 10px;
            margin: 5px 0;
        }

        .step.completed {
            border-left-color: #4caf50;
        }

        .input-area {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }

        .input-container {
            display: flex;
            gap: 10px;
        }

        #userInput {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 15px;
            outline: none;
            transition: border-color 0.3s;
        }

        #userInput:focus {
            border-color: #667eea;
        }

        #sendBtn {
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        #sendBtn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        #sendBtn:active {
            transform: translateY(0);
        }

        #sendBtn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .examples {
            padding: 10px 20px;
            background: #f9f9f9;
            border-top: 1px solid #e0e0e0;
            font-size: 13px;
            color: #666;
        }

        .example-queries {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 5px;
        }

        .example-query {
            background: white;
            padding: 5px 12px;
            border-radius: 15px;
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid #e0e0e0;
        }

        .example-query:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤖 AI Agent Marketplace</h1>
            <p>Ask me anything - I'll find and coordinate the right agents for you</p>
            <div class="agent-status">
                <div>Available Specialist Agents:</div>
                <div class="agent-list">
                    <span class="agent-badge">🌐 Web Scraper</span>
                    <span class="agent-badge">📊 Data Analyzer</span>
                    <span class="agent-badge">📝 Summarizer</span>
                </div>
            </div>
        </div>

        <div class="messages" id="messages">
            <div class="message agent">
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    Hi! I'm your AI orchestrator. Tell me what you need, and I'll automatically find and coordinate the right specialist agents to help you.
                    <div style="margin-top: 10px; font-size: 12px; opacity: 0.8;">
                        Try asking me to scrape websites, analyze data, or summarize content!
                    </div>
                </div>
            </div>
        </div>

        <div class="examples">
            <div>💡 Try these examples:</div>
            <div class="example-queries">
                <span class="example-query" onclick="useExample('Scrape news.ycombinator.com for the top headlines')">Scrape Hacker News</span>
                <span class="example-query" onclick="useExample('Find articles about AI on techcrunch.com and summarize them')">Tech articles</span>
                <span class="example-query" onclick="useExample('Scrape github.com trending and analyze the most popular languages')">GitHub trending</span>
            </div>
        </div>

        <div class="input-area">
            <div class="input-container">
                <input type="text" id="userInput" placeholder="Ask me to scrape, analyze, or summarize..." onkeypress="handleKeyPress(event)">
                <button id="sendBtn" onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        function addMessage(text, isUser, orchestrationSteps = null) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'agent'}`;

            let content = `
                <div class="message-avatar">${isUser ? '👤' : '🤖'}</div>
                <div class="message-content">
                    ${text}
                    ${orchestrationSteps ? `
                        <div class="orchestration-steps">
                            <strong>🔄 Orchestration:</strong>
                            ${orchestrationSteps.map(step => `
                                <div class="step ${step.completed ? 'completed' : ''}">
                                    ${step.completed ? '✅' : '⏳'} ${step.text}
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            `;

            messageDiv.innerHTML = content;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function addThinkingMessage() {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message agent';
            messageDiv.id = 'thinking-message';
            messageDiv.innerHTML = `
                <div class="message-avatar">🤖</div>
                <div class="message-content agent-thinking">
                    🤔 Analyzing your request and finding the best agents...
                </div>
            `;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function removeThinkingMessage() {
            const thinking = document.getElementById('thinking-message');
            if (thinking) thinking.remove();
        }

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const sendBtn = document.getElementById('sendBtn');
            const message = input.value.trim();

            if (!message) return;

            addMessage(message, true);
            input.value = '';
            sendBtn.disabled = true;

            addThinkingMessage();

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });

                const data = await response.json();
                removeThinkingMessage();

                if (data.success) {
                    addMessage(data.response, false, data.orchestration_steps);
                } else {
                    addMessage(`❌ Error: ${data.error}`, false);
                }
            } catch (error) {
                removeThinkingMessage();
                addMessage(`❌ Error: ${error.message}`, false);
            } finally {
                sendBtn.disabled = false;
                input.focus();
            }
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        function useExample(text) {
            document.getElementById('userInput').value = text;
            document.getElementById('userInput').focus();
        }
    </script>
</body>
</html>
"""

def extract_flight_params(original_query, query_lower):
    """Extract flight search parameters from natural language"""
    params = {}

    # Common airport codes mapping
    city_to_code = {
        'san diego': 'SAN', 'seattle': 'SEA', 'san francisco': 'SFO',
        'los angeles': 'LAX', 'new york': 'JFK', 'miami': 'MIA',
        'chicago': 'ORD', 'boston': 'BOS', 'denver': 'DEN',
        'las vegas': 'LAS', 'portland': 'PDX', 'phoenix': 'PHX'
    }

    # Extract origin and destination
    from_match = re.search(r'from\s+([a-z\s]+?)(?:\s+to|\s+and)', query_lower)
    to_match = re.search(r'to\s+([a-z\s]+?)(?:\s|$|,)', query_lower)

    if from_match:
        origin_city = from_match.group(1).strip()
        params['origin'] = city_to_code.get(origin_city, origin_city.upper()[:3])

    if to_match:
        dest_city = to_match.group(1).strip()
        params['destination'] = city_to_code.get(dest_city, dest_city.upper()[:3])

    # Extract date
    if 'tomorrow' in query_lower:
        params['date'] = 'tomorrow'
    elif 'today' in query_lower:
        params['date'] = 'today'
    elif 'next week' in query_lower:
        params['date'] = 'next week'
    else:
        # Try to find date pattern like 10/25/25 or 2025-10-25
        date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', original_query)
        if date_match:
            month, day, year = date_match.groups()
            # Convert 2-digit year to 4-digit
            if len(year) == 2:
                year = f"20{year}"
            params['date'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        else:
            params['date'] = 'tomorrow'  # default

    # Extract time preference
    if 'morning' in query_lower:
        params['time_preference'] = 'morning'
    elif 'afternoon' in query_lower:
        params['time_preference'] = 'afternoon'
    elif 'evening' in query_lower:
        params['time_preference'] = 'evening'
    else:
        params['time_preference'] = 'any'

    # Extract budget
    if 'cheapest' in query_lower or 'cheap' in query_lower:
        params['budget'] = 'cheapest'
    else:
        budget_match = re.search(r'under\s+\$?(\d+)', query_lower)
        if budget_match:
            params['budget'] = f"under ${budget_match.group(1)}"
        else:
            params['budget'] = 'any'

    # Extract airline preference
    if 'no preference' in query_lower or 'any airline' in query_lower:
        params['airline'] = 'any'
    else:
        params['airline'] = 'any'

    # Extract nonstop preference
    params['nonstop'] = 'nonstop' in query_lower or 'non-stop' in query_lower or 'direct' in query_lower

    return params

def format_flight_response(flight_result, steps):
    """Format flight search results for user"""
    response_parts = []

    origin = flight_result.get('origin')
    dest = flight_result.get('destination')
    date = flight_result.get('date')

    response_parts.append(f"✈️  **Flight Options: {origin} → {dest} on {date}**\n")

    if flight_result.get('results'):
        for result in flight_result['results']:
            source = result.get('source', 'Unknown')
            flights = result.get('flights', [])

            response_parts.append(f"\n**{source}** ({len(flights)} options):\n")

            for i, flight in enumerate(flights[:5], 1):
                response_parts.append(f"\n{i}. **{flight['airline']}** {flight['flight_number']}")
                response_parts.append(f"   • Depart: {flight['departure']} → Arrive: {flight['arrival']}")
                response_parts.append(f"   • Duration: {flight['duration']}")
                response_parts.append(f"   • Price: **{flight['price']}**")
                if not flight.get('nonstop', True):
                    response_parts.append(f"   • {flight.get('stops', '1 stop')}")

    return {
        "success": True,
        "response": "\n".join(response_parts),
        "orchestration_steps": steps
    }

async def intelligent_route(user_query: str, session_id: str = "default"):
    """
    Analyzes user query and automatically routes to appropriate agents
    Returns orchestration plan and results
    """
    global _conversation_context

    query_lower = user_query.lower()

    # Check if we have pending context for this session
    context = _conversation_context.get(session_id, {})

    # Parse intent
    needs_flight_search = any(word in query_lower for word in ['flight', 'fly', 'plane', 'airline', 'airport'])
    needs_scraping = any(word in query_lower for word in ['scrape', 'fetch', 'get', 'find', 'extract', 'pull', 'grab', 'website', 'url', 'articles', 'data from'])
    needs_analysis = any(word in query_lower for word in ['analyze', 'statistics', 'calculate', 'measure', 'count', 'compare'])
    needs_summary = any(word in query_lower for word in ['summarize', 'summary', 'key points', 'insights', 'overview', 'summarize them'])

    # Extract URL if present - improved pattern
    url_match = re.search(r'(https?://[^\s]+|(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s]*)?)', query_lower)
    url = url_match.group(0) if url_match else None
    if url and not url.startswith('http'):
        url = f'https://{url}'

    # Clean up URL - remove trailing punctuation and "and"
    if url:
        url = url.rstrip('.,;:!?')
        # Remove trailing "and" if present
        if url.endswith(' and'):
            url = url[:-4]

    # Extract selector hints
    selector = '.titleline > a'  # default
    if 'headline' in query_lower or 'title' in query_lower:
        selector = '.titleline > a, h1, h2'
    elif 'article' in query_lower:
        selector = 'article, .post, .article'
    elif 'link' in query_lower:
        selector = 'a'

    steps = []
    results = {}

    # Handle flight search first (higher priority than generic scraping)
    if needs_flight_search or context.get('awaiting') == 'flight_preferences':
        # If we're awaiting flight preferences, merge with stored context
        if context.get('awaiting') == 'flight_preferences':
            # User is providing preferences for a pending flight search
            flight_params = context.get('flight_params', {})

            # Extract additional preferences from current message
            new_params = extract_flight_params(user_query, query_lower)

            # Merge: new params override stored params
            for key, value in new_params.items():
                if value:  # Only update if value is not empty/None/False
                    flight_params[key] = value

            # Clear context - we're processing now
            _conversation_context[session_id] = {}
        else:
            # Extract flight parameters from query
            flight_params = extract_flight_params(user_query, query_lower)

        # Check if we have minimum required information
        if flight_params.get('origin') and flight_params.get('destination'):
            # Check if user provided preferences - if not, ask for them
            # Only ask if this is a NEW query (not a response to our clarification)
            missing_info = []
            is_new_query = context.get('awaiting') != 'flight_preferences'

            if is_new_query:
                if flight_params.get('date') == 'tomorrow' and 'tomorrow' not in query_lower and 'today' not in query_lower and 'next week' not in query_lower and not re.search(r'\d{1,2}/\d{1,2}', query_lower):
                    missing_info.append("• **When** would you like to travel? (tomorrow, specific date, next week)")

                if flight_params.get('time_preference') == 'any' and 'morning' not in query_lower and 'afternoon' not in query_lower and 'evening' not in query_lower:
                    missing_info.append("• What **time of day** do you prefer? (morning/afternoon/evening)")

                if flight_params.get('budget') == 'any' and 'cheapest' not in query_lower and 'cheap' not in query_lower and 'under' not in query_lower:
                    missing_info.append("• What's your **budget** or price range? (cheapest, under $X, any)")

                if not flight_params.get('nonstop') and 'nonstop' not in query_lower and 'direct' not in query_lower and 'connection' not in query_lower:
                    missing_info.append("• Do you prefer **nonstop** flights or are connections okay?")

            # If missing key information, ask for it
            if missing_info and is_new_query:
                response_parts = []
                response_parts.append(f"Great! I can help you find flights from **{flight_params['origin']}** to **{flight_params['destination']}**.")
                response_parts.append("\nTo find the best options, could you tell me:")
                response_parts.extend(missing_info)
                response_parts.append("\n💡 Or I can search with default preferences (tomorrow, any time, all options)!")

                # Store context for next message
                _conversation_context[session_id] = {
                    'awaiting': 'flight_preferences',
                    'flight_params': flight_params
                }

                return {
                    "success": True,
                    "response": "\n".join(response_parts),
                    "orchestration_steps": []
                }

            # All required info present - proceed with search
            steps.append({"text": f"✈️  Flight Search: Finding flights {flight_params['origin']} → {flight_params['destination']}", "completed": False})
            try:
                flight_result = await _agent.execute_task(
                    capability="flight_search",
                    message_body=flight_params
                )
                if flight_result.get("status") == "success":
                    results['flights'] = flight_result
                    steps[-1]["completed"] = True
                    return format_flight_response(flight_result, steps)
                else:
                    steps[-1]["text"] += " (no flights found)"
            except Exception as e:
                steps[-1]["text"] += f" (error: {str(e)})"
        else:
            # Missing origin or destination - ask for them
            response_parts = []
            response_parts.append("I'd be happy to help you find flights! To search, I need:")
            if not flight_params.get('origin'):
                response_parts.append("\n• **Where are you flying from?** (city name or airport code)")
            if not flight_params.get('destination'):
                response_parts.append("\n• **Where are you flying to?** (city name or airport code)")
            response_parts.append("\n💡 Then I can ask about your preferences and search for you!")

            return {
                "success": True,
                "response": "\n".join(response_parts),
                "orchestration_steps": []
            }

    # Execute orchestration
    if needs_scraping and url:
        steps.append({"text": f"🌐 Web Scraper: Extracting data from {url}", "completed": False})
        try:
            scrape_result = await _agent.execute_task(
                capability="web_scraper",
                message_body={"url": url, "selector": selector, "limit": 20}
            )
            if scrape_result.get("status") == "success":
                results['scrape'] = scrape_result['data']
                steps[-1]["completed"] = True
            else:
                return {
                    "success": False,
                    "error": f"Scraping failed: {scrape_result.get('message', 'Unknown error')}"
                }
        except Exception as e:
            return {"success": False, "error": f"Scraping failed: {str(e)}"}

    if needs_analysis and results.get('scrape'):
        steps.append({"text": "📊 Data Analyzer: Computing statistics", "completed": False})
        try:
            analysis_result = await _agent.execute_task(
                capability="data_analyzer",
                message_body={"data": results['scrape'], "metric": "text_length"}
            )
            if analysis_result.get("status") == "success":
                results['analysis'] = analysis_result['analysis']
                steps[-1]["completed"] = True
            else:
                steps[-1]["text"] += " (failed)"
        except Exception as e:
            steps[-1]["text"] += f" (error: {str(e)})"

    if needs_summary and results.get('scrape'):
        steps.append({"text": "📝 Summarizer: Extracting key insights", "completed": False})
        try:
            summary_result = await _agent.execute_task(
                capability="content_summarizer",
                message_body={"data": results['scrape'], "max_points": 5}
            )
            if summary_result.get("status") == "success":
                results['summary'] = summary_result['summary']
                steps[-1]["completed"] = True
            else:
                steps[-1]["text"] += " (failed)"
        except Exception as e:
            steps[-1]["text"] += f" (error: {str(e)})"

    # Format response
    response_parts = []

    if results.get('scrape'):
        count = len(results['scrape'])
        response_parts.append(f"📦 Found {count} items from {url}")
        if count > 0:
            response_parts.append(f"\nFirst few items: {', '.join([item['text'][:50] for item in results['scrape'][:3]])}")

    if results.get('analysis'):
        analysis = results['analysis']
        response_parts.append(f"\n\n📊 Analysis:")
        response_parts.append(f"  • Count: {analysis.get('count', 'N/A')}")
        response_parts.append(f"  • Avg length: {analysis.get('mean', 'N/A')} chars")
        response_parts.append(f"  • Range: {analysis.get('min', 'N/A')} - {analysis.get('max', 'N/A')} chars")

    if results.get('summary'):
        response_parts.append(f"\n\n📝 Key Points:")
        # Handle both dict and list formats
        summary = results['summary']
        if isinstance(summary, dict):
            key_points = summary.get('key_points', [])
        elif isinstance(summary, list):
            key_points = summary
        else:
            key_points = []

        for i, point in enumerate(key_points, 1):
            response_parts.append(f"  {i}. {point}")

    if not results:
        if not url:
            # Check if this is a general query that might need a different type of agent
            if any(word in query_lower for word in ['flight', 'hotel', 'book', 'reserve', 'travel']):
                response_parts.append("I'd be happy to help you with that! To find the best flights, I need a bit more information:")
                response_parts.append("\n• What dates are you looking to travel?")
                response_parts.append("• What time of day do you prefer (morning/afternoon/evening)?")
                response_parts.append("• What's your budget or price range?")
                response_parts.append("• Any airline preferences?")
                response_parts.append("• Do you prefer nonstop or are connections okay?")
                response_parts.append("\n💡 Note: Currently I can scrape flight search websites like Google Flights, Kayak, or Skyscanner if you provide the URL!")
            else:
                response_parts.append("I'd like to help! Could you provide more details?")
                response_parts.append("\n• If you need web scraping, please include a website URL")
                response_parts.append("• If you need data analysis, please describe the data source")
                response_parts.append("• Or tell me more about what you're trying to accomplish!")
        else:
            response_parts.append("I understood your request but couldn't execute it. Please try rephrasing.")

    return {
        "success": True,
        "response": "\n".join(response_parts),
        "orchestration_steps": steps
    }

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    if not _ready:
        return jsonify({"success": False, "error": "Agent orchestrator not ready yet. Please wait a few seconds."})

    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({"success": False, "error": "No message provided"})

        # Use simple session ID (in production, use actual session management)
        session_id = request.remote_addr

        async def process_query():
            return await intelligent_route(user_message, session_id)

        future = asyncio.run_coroutine_threadsafe(process_query(), _loop)
        result = future.result(timeout=30)

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def init_agent():
    global _agent, _loop, _ready

    try:
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)

        _agent = Agent(
            registry_url="http://127.0.0.1:8000",
            key_file="chat_orchestrator.key",
            demo_mode=True
        )

        async def setup_and_run():
            try:
                await _agent.listen_and_join(
                    "127.0.0.1", 9005,
                    "127.0.0.1", 9105,
                    ("127.0.0.1", 8480)
                )
                print("📡 Orchestrator listening on 127.0.0.1:9005")

                await _agent.register(
                    public_endpoint="http://127.0.0.1:9005",
                    capabilities=["chat_orchestrator"],
                    price=0.00,
                    payment_method="points"
                )
                print("✅ Chat Orchestrator fully registered!")
            except Exception as e:
                print(f"⚠️  Registration warning: {e}")
                print("   Agent will still work via direct discovery")

            # Keep event loop alive
            while True:
                await asyncio.sleep(1)

        _ready = True  # Agent is ready to accept requests
        print("✅ Chat Orchestrator ready to accept requests!")

        _loop.run_until_complete(_agent.listen_and_join(
            "127.0.0.1", 9005,
            "127.0.0.1", 9105,
            ("127.0.0.1", 8480)
        ))

        # Run registration in background
        async def register_async():
            try:
                await _agent.register(
                    public_endpoint="http://127.0.0.1:9005",
                    capabilities=["chat_orchestrator"],
                    price=0.00,
                    payment_method="points"
                )
                print("✅ Chat Orchestrator registered with indexer!")
            except Exception as e:
                print(f"⚠️  Registration failed: {e}")

        _loop.create_task(register_async())
        _loop.run_forever()

    except Exception as e:
        print(f"[Orchestrator] ❌ Setup error: {e}")

if __name__ == "__main__":
    import os

    print("=" * 60)
    print("🤖 AI Agent Chat - Conversational Marketplace")
    print("=" * 60)
    print("\nStarting chat orchestrator...")

    agent_thread = threading.Thread(target=init_agent, daemon=True)
    agent_thread.start()

    import time
    time.sleep(3)

    # Use Railway's PORT environment variable, fallback to 5001 for local
    port = int(os.getenv('PORT', 5001))

    print("\n" + "=" * 60)
    print("💬 Chat UI Ready!")
    print("=" * 60)
    print(f"\n✅ Server running on port {port}")
    print("\nJust type what you need:")
    print("  • 'Scrape news.ycombinator.com for headlines'")
    print("  • 'Get trending repos from github.com and analyze'")
    print("  • 'Summarize articles from techcrunch.com'")
    print("\nThe orchestrator will automatically find the right agents!\n")

    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
