# agent_three.py
from agent_web import Agent
import asyncio

# --- Handler (unchanged) ---
def handle_greeting(sender_id: str, message_body: dict):
    print(f"\n[Agent THREE] Received message from: {sender_id}")
    print(f"[Agent THREE] Message body: {message_body}")
    name = message_body.get("name", "stranger")
    return {"response": f"Hi {name}! Agent THREE (Budget) at your service!"}

# --- Main (now async) ---
async def main():
    agent = Agent(
        agent_id="agent_three",
        registry_url="http://127.0.0.1:8000",
        key_file="agent_three.key"
    )

    agent.on_message(handle_greeting)

    http_host = "127.0.0.1"
    http_port = 8003  # New HTTP port
    dht_host = "127.0.0.1"
    dht_port = 8469  # New DHT port

    # We bootstrap to Agent ONE's DHT node
    bootstrap_node = ("127.0.0.1", 8468)

    listen_task = asyncio.create_task(
        agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node)
    )

    await asyncio.sleep(1)

    await agent.register(
        public_endpoint=f"http://{http_host}:{http_port}",
        capabilities=["greeter"],
        price=2.0,  # Budget price
        payment_method="usdc:polygon"
    )

    print(f"Agent THREE (Budget) is running and waiting for messages...")
    await listen_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down Agent THREE")