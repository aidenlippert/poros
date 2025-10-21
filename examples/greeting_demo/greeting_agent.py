import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
from agent_web import Agent

async def handle_greeting_request(sender_did: str, message_body: dict):
    print(f"\n[GREETING AGENT] Received request from: {sender_did[:20]}...")

    name = message_body.get("name", "Friend")
    day = message_body.get("day", "today")

    greeting = f"Hello {name}! Hope you're having a great {day}!"

    print(f"[GREETING AGENT] Created greeting: {greeting}")

    return {
        "status": "success",
        "greeting": greeting
    }

async def main():
    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="greeting_agent.key",
        demo_mode=True
    )

    agent.on_message(handle_greeting_request)

    http_host = "127.0.0.1"
    http_port = 8021
    dht_host = "127.0.0.1"
    dht_port = 8491
    bootstrap_node = ("127.0.0.1", 8480)

    listen_task = asyncio.create_task(
        agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node)
    )
    await asyncio.sleep(2)

    await agent.register(
        public_endpoint=f"http://{http_host}:{http_port}",
        capabilities=["greeting_service"],
        price=0.01,
        payment_method="points"
    )

    print(f"\n✅ Greeting Agent is running")
    print(f"   DID: {agent.did}")
    print(f"   HTTP: {http_host}:{http_port}")
    print(f"   Capability: greeting_service")
    print(f"   Ready to create personalized greetings!\n")

    try:
        await listen_task
    except KeyboardInterrupt:
        print("\n[GREETING AGENT] Shutting down...")

if __name__ == "__main__":
    asyncio.run(main())
