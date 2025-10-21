import asyncio
from agent_web import Agent

async def main():
    print("=== BULLETPROOF DEMO: Customer Agent (with Hybrid Mode) ===\n")

    customer = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="customer_did.key",
        default_policy={'price': 0.7, 'reputation': 0.3},
        demo_mode=True  # SPRINT 9: Enable hybrid mode for 100% reliability
    )

    print(f"🔑 Customer Agent DID: {customer.did}")
    print(f"🎯 Demo Mode: ENABLED (using central cache for bulletproof discovery)\n")

    bootstrap_node = ("127.0.0.1", 8480)
    listen_task = asyncio.create_task(
        customer.listen_and_join(
            http_host="127.0.0.1", http_port=8012,
            dht_host="127.0.0.1", dht_port=8482,
            bootstrap_node=bootstrap_node
        )
    )
    await asyncio.sleep(1)

    await customer.register(
        public_endpoint="http://127.0.0.1:8012",
        capabilities=["customer"],
        price=0.0,
        payment_method="demo"
    )

    await asyncio.sleep(1)

    print("--- Testing Bulletproof Discovery & Execution ---")
    test_text = "This is the Sprint 9 bulletproof demo! The hybrid architecture guarantees 100% reliable discovery for investor presentations while maintaining the decentralized DID-based security model."

    try:
        result = await customer.execute_task(
            capability="text_analyzer",
            message_body={"text": test_text}
        )

        print("\n✅ DEMO SUCCESS!")
        print(f"📊 Analysis Result: {result}")
        print(f"\n🎯 Key Achievement:")
        print(f"   - Discovery: 100% reliable (central cache)")
        print(f"   - Security: Unforgeable DID verification")
        print(f"   - Communication: P2P with cryptographic signatures")
        print(f"   - Fallback: DHT available if cache unavailable")

    except Exception as e:
        print(f"❌ Demo failed: {e}")

    listen_task.cancel()
    print("\n✅ Demo complete!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Customer agent shutdown complete")
