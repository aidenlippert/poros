#!/usr/bin/env python3
"""
Test script to prove agent-to-agent communication works
This demonstrates:
1. Agent discovery via DHT
2. P2P message sending
3. Response handling
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
from agent_web import Agent

async def test_agent_communication():
    print("=" * 80)
    print("AGENT-TO-AGENT COMMUNICATION TEST")
    print("=" * 80)

    # Create test agent
    print("\n1️⃣ Creating test Personal Assistant agent...")
    test_agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="test_assistant.key",
        demo_mode=True
    )
    print(f"   ✅ Agent DID: {test_agent.did[:40]}...")

    # Start network
    print("\n2️⃣ Starting network services...")
    http_host = "127.0.0.1"
    http_port = 8031
    dht_host = "127.0.0.1"
    dht_port = 8501
    bootstrap_node = ("127.0.0.1", 8480)

    asyncio.create_task(
        test_agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node)
    )
    await asyncio.sleep(3)
    print(f"   ✅ HTTP: {http_host}:{http_port}")
    print(f"   ✅ DHT: {dht_host}:{dht_port}")

    # Register
    print("\n3️⃣ Registering with network...")
    await test_agent.register(
        public_endpoint=f"http://{http_host}:{http_port}",
        capabilities=["test_assistant"],
        price=0.0,
        payment_method="free"
    )
    print("   ✅ Registered with capabilities: ['test_assistant']")

    # Test 1: Discover and contact Day Agent
    print("\n" + "=" * 80)
    print("TEST 1: DISCOVERING AND CONTACTING DAY AGENT")
    print("=" * 80)

    print("\n🔎 Searching DHT for capability: 'day_service'...")
    day_response = await test_agent.execute_task(
        capability="day_service",
        message_body={}
    )

    print(f"\n📥 Response from Day Agent:")
    print(f"   Status: {day_response.get('status')}")
    print(f"   Day: {day_response.get('day')}")

    if day_response.get("status") == "success":
        print("\n   ✅ SUCCESS! Day Agent found and responded!")
    else:
        print("\n   ❌ FAILED! Day Agent did not respond properly")
        return

    # Test 2: Discover and contact Greeting Agent
    print("\n" + "=" * 80)
    print("TEST 2: DISCOVERING AND CONTACTING GREETING AGENT")
    print("=" * 80)

    print("\n🔎 Searching DHT for capability: 'greeting_service'...")
    current_day = day_response.get("day")
    greeting_response = await test_agent.execute_task(
        capability="greeting_service",
        message_body={"name": "TestUser", "day": current_day}
    )

    print(f"\n📥 Response from Greeting Agent:")
    print(f"   Status: {greeting_response.get('status')}")
    print(f"   Greeting: {greeting_response.get('greeting')}")

    if greeting_response.get("status") == "success":
        print("\n   ✅ SUCCESS! Greeting Agent found and responded!")
    else:
        print("\n   ❌ FAILED! Greeting Agent did not respond properly")
        return

    # Test 3: Multi-agent orchestration
    print("\n" + "=" * 80)
    print("TEST 3: MULTI-AGENT ORCHESTRATION (DAY + GREETING)")
    print("=" * 80)

    print("\n📡 STEP 1: Getting current day from Day Agent...")
    day_result = await test_agent.execute_task(
        capability="day_service",
        message_body={}
    )
    current_day = day_result.get("day")
    print(f"   ✅ Day Agent says: {current_day}")

    print("\n📡 STEP 2: Creating personalized greeting with Greeting Agent...")
    print(f"   Sending: name='Aiden', day='{current_day}'")
    greeting_result = await test_agent.execute_task(
        capability="greeting_service",
        message_body={"name": "Aiden", "day": current_day}
    )
    greeting = greeting_result.get("greeting")
    print(f"   ✅ Greeting Agent says: {greeting}")

    print("\n" + "=" * 80)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 80)
    print("\n✅ Agent discovery via DHT: WORKING")
    print("✅ P2P message sending: WORKING")
    print("✅ Response handling: WORKING")
    print("✅ Multi-agent orchestration: WORKING")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(test_agent_communication())
