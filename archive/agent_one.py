# agent_one.py
from agent_web import Agent
import asyncio

# --- Handler (unchanged) ---
def handle_greeting(sender_id: str, message_body: dict):
    print(f"\n[Agent ONE] Received message from: {sender_id}")
    print(f"[Agent ONE] Message body: {message_body}")
    name = message_body.get("name", "stranger")
    return {"response": f"Hello, {name}! This is Agent ONE (Premium Service)."}

# --- Main (now async) ---
async def main():
    agent = Agent(
        agent_id="agent_one",
        registry_url="http://127.0.0.1:8000",
        key_file="agent_one.key"
    )

    agent.on_message(handle_greeting)

    # Define agent's network addresses
    http_host = "127.0.0.1"
    http_port = 8001
    dht_host = "127.0.0.1"
    dht_port = 8468  # This is the main DHT bootstrap port

    # Start all services
    # THIS IS THE FIRST NODE, so bootstrap_node=None
    listen_task = asyncio.create_task(
        agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node=None)
    )

    # Give the services a moment to start
    await asyncio.sleep(1)

    # Register with Indexer and publish to DHT
    await agent.register(
        public_endpoint=f"http://{http_host}:{http_port}",
        capabilities=["greeter"],
        price=10.0,  # Premium price
        payment_method="usdc:eth"
    )

    print(f"Agent ONE (Premium) is running and waiting for messages...")
    await listen_task  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down Agent ONE")