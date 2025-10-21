import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
from agent_web import Agent
from datetime import datetime

async def handle_day_request(sender_did: str, message_body: dict):
    print(f"\n[DAY AGENT] Received request for current day from: {sender_did[:20]}...")

    current_day = datetime.now().strftime("%A")

    print(f"[DAY AGENT] Responding with: {current_day}")

    return {
        "status": "success",
        "day": current_day
    }

async def main():
    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="day_agent.key",
        demo_mode=True
    )

    agent.on_message(handle_day_request)

    http_host = "127.0.0.1"
    http_port = 8020
    dht_host = "127.0.0.1"
    dht_port = 8490
    bootstrap_node = ("127.0.0.1", 8480)

    listen_task = asyncio.create_task(
        agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node)
    )
    await asyncio.sleep(2)

    await agent.register(
        public_endpoint=f"http://{http_host}:{http_port}",
        capabilities=["day_service"],
        price=0.01,
        payment_method="points"
    )

    print(f"\n✅ Day Agent is running")
    print(f"   DID: {agent.did}")
    print(f"   HTTP: {http_host}:{http_port}")
    print(f"   Capability: day_service")
    print(f"   Ready to provide current day of the week!\n")

    try:
        await listen_task
    except KeyboardInterrupt:
        print("\n[DAY AGENT] Shutting down...")

if __name__ == "__main__":
    asyncio.run(main())
