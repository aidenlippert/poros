import asyncio
from agent_web import Agent

def handle_text_analysis(sender_did: str, message_body: dict):
    print(f"\n[DEMO SERVICE] Analyzing text from: {sender_did[:20]}...")
    text = message_body.get("text", "")

    if not text:
        return {"error": "No text provided"}

    word_count = len(text.split())
    char_count = len(text)
    is_long = word_count > 50

    return {
        "word_count": word_count,
        "char_count": char_count,
        "is_long_form": is_long
    }

async def main():
    print("=== BULLETPROOF DEMO: Service Agent (with Hybrid Mode) ===\n")

    service = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="service_did.key",
        demo_mode=True  # SPRINT 9: Enable hybrid mode for 100% reliability
    )

    print(f"🔑 Service Agent DID: {service.did}")
    print(f"🎯 Demo Mode: ENABLED (using central cache for bulletproof reliability)\n")

    service.on_message(handle_text_analysis)

    print("Starting service with hybrid discovery...")
    listen_task = asyncio.create_task(
        service.listen_and_join(
            http_host="127.0.0.1", http_port=8010,
            dht_host="127.0.0.1", dht_port=8480,
            bootstrap_node=None
        )
    )

    await asyncio.sleep(1)

    await service.register(
        public_endpoint="http://127.0.0.1:8010",
        capabilities=["text_analyzer"],
        price=0.01,
        payment_method="demo"
    )

    print("\n✅ Service agent ready and registered!")
    print("   - Published to DHT")
    print("   - Published to DEMO CACHE for 100% reliability")
    print("\nWaiting for requests...\n")

    await listen_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Service agent shutdown complete")
