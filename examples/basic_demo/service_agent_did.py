# service_agent_did.py
from agent_web import Agent
import asyncio

# --- This is the agent's "skill" ---
def handle_text_analysis(sender_did: str, message_body: dict):
    print(f"\n[Text Analyzer] Received job from: {sender_did[:20]}...")
    text = message_body.get("text", "")

    if not text:
        return {"error": "No text provided"}

    word_count = len(text.split())
    char_count = len(text)

    # This is the "product" we are selling
    return {
        "word_count": word_count,
        "char_count": char_count,
        "is_long_form": word_count > 100
    }
# ------------------------------------

async def main():
    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="service_agent_did.key"
    )

    agent.on_message(handle_text_analysis)

    # This is the Bootstrap Node for the entire network
    http_host = "127.0.0.1"
    http_port = 8010
    dht_host = "127.0.0.1"
    dht_port = 8480 # Main Bootstrap Port

    listen_task = asyncio.create_task(
        agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node=None)
    )

    await asyncio.sleep(1)

    # Register our service
    await agent.register(
        public_endpoint=f"http://{http_host}:{http_port}",
        capabilities=["text_analyzer"],
        price=1.50, # We charge $1.50 per analysis
        payment_method="usdc:polygon"
    )

    print("--- Text Analyzer Service is LIVE ---")
    await listen_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down Text Analyzer")
