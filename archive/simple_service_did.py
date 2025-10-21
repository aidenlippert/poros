# simple_service_did.py - A DID-enabled simplified service that joins the existing DHT network
from agent_web import Agent
import asyncio

def handle_text_analysis(sender_did: str, message_body: dict):
    print(f"\n[Text Analyzer] Received job from: {sender_did[:20]}...")
    text = message_body.get("text", "")

    if not text:
        return {"error": "No text provided"}

    word_count = len(text.split())
    char_count = len(text)

    return {
        "word_count": word_count,
        "char_count": char_count,
        "is_long_form": word_count > 100
    }

async def main():
    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="simple_service_did.key"  # This file IS the identity
    )

    agent.on_message(handle_text_analysis)

    # Join the existing DHT network from our earlier test
    bootstrap_node = ("127.0.0.1", 8468)  # Use existing DHT bootstrap
    listen_task = asyncio.create_task(
        agent.listen_and_join(
            http_host="127.0.0.1", http_port=8020,
            dht_host="127.0.0.1", dht_port=8485,
            bootstrap_node=bootstrap_node
        )
    )

    await asyncio.sleep(2)

    # Register our service
    await agent.register(
        public_endpoint="http://127.0.0.1:8020",
        capabilities=["text_analyzer"],
        price=1.50,
        payment_method="usdc:polygon"
    )

    print("--- Simple Text Analyzer Service is LIVE ---")
    await listen_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down Simple Text Analyzer")