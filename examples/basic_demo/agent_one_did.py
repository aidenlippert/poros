# agent_one_did.py - DID-Enabled Bootstrap Agent (Premium)
from agent_web import Agent
import asyncio
import os

def handle_greeting(sender_did: str, message_body: dict):
    print(f"\n[Agent ONE] Received job from: {sender_did[:20]}...")
    name = message_body.get("name", "stranger")
    return {"response": f"Hello, {name}! This is Agent ONE (Premium Service)."}

async def main():
    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="agent_one_did.key"  # This file IS the identity
    )

    agent.on_message(handle_greeting)

    http_host = "127.0.0.1"
    http_port = 8001
    dht_host = "127.0.0.1"
    dht_port = 8468  # Main Bootstrap Port

    listen_task = asyncio.create_task(
        agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node=None)
    )

    await asyncio.sleep(1)

    await agent.register(
        public_endpoint=f"http://{http_host}:{http_port}",
        capabilities=["greeter"],
        price=10.0,
        payment_method="usdc:eth"
    )

    print(f"Agent ONE (Premium) is running and waiting for messages...")
    await listen_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down Agent ONE")