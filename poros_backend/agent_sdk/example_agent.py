"""
Poros Agent SDK - Example Agent

This is a complete, working example of an A2A-compliant agent that:
1. Implements the A2A protocol using Google's SDK
2. Registers itself with Poros Protocol
3. Handles incoming queries via message/send
4. Returns proper A2A-compliant responses

CUSTOMIZE THIS FOR YOUR USE CASE:
- Replace the agent logic in handle_message()
- Update AgentCard with your skills/capabilities
- Add your model inference, API calls, database queries, etc.
"""

import os
import asyncio
from typing import Optional

# A2A SDK
from a2a.server import A2AFastAPIApplication, AgentExecutor
from a2a.server.agent_execution import RequestContext
from a2a.types import Task, Message, Artifact, TextPart

# FastAPI
from fastapi import FastAPI
import uvicorn

# Registration
import httpx


# ============================================
# AGENT CONFIGURATION
# ============================================

AGENT_NAME = os.getenv("AGENT_NAME", "Example Weather Agent")
AGENT_PORT = int(os.getenv("AGENT_PORT", 9100))
AGENT_PUBLIC_URL = os.getenv("AGENT_PUBLIC_URL", f"http://localhost:{AGENT_PORT}")

# Poros Registry
POROS_REGISTRY_URL = os.getenv("POROS_REGISTRY_URL", "http://localhost:8000")
POROS_AUTH_TOKEN = os.getenv("POROS_AUTH_TOKEN")  # JWT token from registration


# ============================================
# AGENT CARD (A2A Protocol)
# ============================================

AGENT_CARD = {
    "protocolVersion": "0.3.0",
    "name": AGENT_NAME,
    "description": "Example agent that provides weather information for cities",
    "url": AGENT_PUBLIC_URL,
    "preferredTransport": "JSONRPC",
    "skills": [
        {
            "id": "weather_lookup",
            "name": "Weather Lookup",
            "description": "Get current weather and forecast for any location",
            "tags": ["weather", "forecast", "temperature"],
            "examples": [
                "What's the weather in San Francisco?",
                "Will it rain in Seattle tomorrow?",
                "Temperature in New York"
            ]
        }
    ],
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
        "stateTransitionHistory": False
    },
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["text/plain", "application/json"],
    "version": "1.0.0",
    "provider": {
        "organization": "Example Org",
        "url": "https://example.com"
    }
}


# ============================================
# AGENT LOGIC (CUSTOMIZE THIS!)
# ============================================

# Mock weather data (replace with real API call to OpenWeather, etc.)
MOCK_WEATHER = {
    "san francisco": {
        "temp_f": 65,
        "conditions": "Partly Cloudy",
        "forecast": "Cool and foggy morning, clearing by afternoon"
    },
    "seattle": {
        "temp_f": 52,
        "conditions": "Rainy",
        "forecast": "Showers throughout the day"
    },
    "new york": {
        "temp_f": 45,
        "conditions": "Clear",
        "forecast": "Cold and sunny"
    }
}


async def handle_message(message: Message, context: RequestContext) -> Task:
    """
    Handle incoming message from client (via Poros Orchestrator).

    THIS IS WHERE YOU PUT YOUR AGENT LOGIC:
    - Parse the message
    - Call your model/API/database
    - Generate response
    - Return as A2A Task with Artifacts
    """
    # Extract query from message
    query = ""
    if message.parts:
        for part in message.parts:
            if hasattr(part, 'text'):
                query += part.text

    print(f"[AGENT] Received query: {query}")

    # YOUR CUSTOM LOGIC HERE
    # Example: Simple weather lookup
    city = extract_city(query)
    weather = get_weather(city)

    # Format response
    if weather:
        response_text = (
            f"Weather in {city.title()}:\\n"
            f"Temperature: {weather['temp_f']}°F\\n"
            f"Conditions: {weather['conditions']}\\n"
            f"Forecast: {weather['forecast']}"
        )
    else:
        response_text = f"Sorry, I don't have weather data for {city}"

    # Create A2A-compliant response
    task = context.task
    task.artifacts = [
        Artifact(
            parts=[TextPart(text=response_text)]
        )
    ]

    print(f"[AGENT] Responding with: {response_text[:100]}...")
    return task


def extract_city(query: str) -> str:
    """Extract city name from query (simple version)"""
    query_lower = query.lower()
    for city in MOCK_WEATHER.keys():
        if city in query_lower:
            return city
    return "unknown"


def get_weather(city: str) -> Optional[dict]:
    """
    Get weather for city.

    REPLACE THIS with real API call:
    - OpenWeather API
    - Weather.gov
    - Your own weather service
    """
    return MOCK_WEATHER.get(city.lower())


# ============================================
# A2A AGENT SERVER
# ============================================

class ExampleAgentExecutor(AgentExecutor):
    """Agent executor that handles message/send requests"""

    async def execute(self, context: RequestContext) -> Task:
        """Execute agent logic for incoming message"""
        return await handle_message(context.message, context)


# Create A2A FastAPI application
agent_executor = ExampleAgentExecutor()
a2a_app = A2AFastAPIApplication(
    agent_card=AGENT_CARD,
    agent_executor=agent_executor
)

# Get the FastAPI app
app = a2a_app.app


# ============================================
# REGISTRATION WITH POROS
# ============================================

async def register_with_poros():
    """
    Register this agent with Poros Protocol Registry.

    You need to:
    1. Create a Poros account first: POST /api/registry/users
    2. Save your JWT token as POROS_AUTH_TOKEN env var
    3. Run this agent - it will auto-register
    """
    if not POROS_AUTH_TOKEN:
        print("[AGENT] POROS_AUTH_TOKEN not set - skipping registration")
        print("[AGENT] To register:")
        print("[AGENT] 1. Create account: POST http://localhost:8000/api/registry/users")
        print("[AGENT] 2. Set POROS_AUTH_TOKEN env var")
        print("[AGENT] 3. Restart agent")
        return

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{POROS_REGISTRY_URL}/api/registry/agents",
                json={"agent_card": AGENT_CARD},
                headers={"Authorization": f"Bearer {POROS_AUTH_TOKEN}"},
                timeout=10.0
            )

            if response.status_code == 201:
                data = response.json()
                print(f"[AGENT] Successfully registered with Poros!")
                print(f"[AGENT] Agent ID: {data['agent_id']}")
            elif response.status_code == 409:
                print(f"[AGENT] Already registered with Poros")
            else:
                print(f"[AGENT] Registration failed: {response.status_code}")
                print(f"[AGENT] Response: {response.text}")

    except Exception as e:
        print(f"[AGENT] Registration error: {e}")


# ============================================
# STARTUP
# ============================================

@app.on_event("startup")
async def startup():
    """Register agent with Poros on startup"""
    print(f"[AGENT] {AGENT_NAME} starting...")
    print(f"[AGENT] URL: {AGENT_PUBLIC_URL}")
    print(f"[AGENT] Skills: {[s['name'] for s in AGENT_CARD['skills']]}")

    # Register with Poros in background
    asyncio.create_task(register_with_poros())


# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print(f"POROS AGENT: {AGENT_NAME}")
    print("=" * 60)
    print(f"Port: {AGENT_PORT}")
    print(f"URL: {AGENT_PUBLIC_URL}")
    print(f"Registry: {POROS_REGISTRY_URL}")
    print("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=AGENT_PORT,
        log_level="info"
    )
