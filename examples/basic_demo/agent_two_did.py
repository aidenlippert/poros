# agent_two_did.py - DID-Enabled Client Agent
from agent_web import Agent
import asyncio

# --- Main (now async) ---
async def main():
    price_is_everything_policy = {'price': 0.9, 'reputation': 0.1}

    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="agent_two_did.key",  # This file IS the identity
        default_policy=price_is_everything_policy
    )

    # This agent is a client, but it STILL must join the network
    # to find peers via DHT.
    http_host = "127.0.0.1"
    http_port = 8002  # New HTTP port
    dht_host = "127.0.0.1"
    dht_port = 8470  # New DHT port

    bootstrap_node = ("127.0.0.1", 8468)  # Bootstrap to main agent

    # We don't need to await the listen_task forever,
    # as this agent will just send one message and exit.
    # But it must be running to participate in the DHT.
    listen_task = asyncio.create_task(
        agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node)
    )

    await asyncio.sleep(2)  # Give time to join the network

    # Register (not strictly needed for this test, but good practice)
    await agent.register(
        public_endpoint=f"http://{http_host}:{http_port}",
        capabilities=["client"],
        price=0.0
    )

    print("\n[Agent TWO] Running execute_task in 3 seconds...")
    await asyncio.sleep(3)

    message = {"name": "Aiden (the customer)", "question": "What's your price?"}
    response = await agent.execute_task(
        capability="greeter",
        message_body=message
    )

    print("\n[Agent TWO] Got final response:")
    print(response)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down Agent TWO")