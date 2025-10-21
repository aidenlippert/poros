# test_langchain_simple.py - Simple test without using LangChain agents
import asyncio
from agent_web import Agent

async def main():
    # 1. Setup our Agent Web "Phone" with DID-based identity
    customer_agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="langchain_simple_did.key",
        default_policy={'price': 0.7, 'reputation': 0.3}
    )

    print(f"[LangChain Test] Initialized with DID: {customer_agent.did}")

    # 2. Join the network
    bootstrap_node = ("127.0.0.1", 8480)
    listen_task = asyncio.create_task(
        customer_agent.listen_and_join(
            http_host="127.0.0.1", http_port=8015,
            dht_host="127.0.0.1", dht_port=8485,
            bootstrap_node=bootstrap_node
        )
    )
    await asyncio.sleep(2)

    # 3. Direct test without LLM orchestration
    print("\n--- Testing Direct Agent Web Communication (LangChain would use this) ---")
    my_text = "This is a test from LangChain framework to prove cross-framework DID-based interoperability!"

    try:
        result = await customer_agent.execute_task(
            capability="text_analyzer",
            message_body={"text": my_text}
        )

        print("\n--- LangChain Test Result ---")
        print(f"✅ Successfully analyzed text using DID-based agent communication!")
        print(f"Result: {result}")

        if "word_count" in result:
            print(f"\n📊 Analysis Details:")
            print(f"  - Word count: {result.get('word_count')}")
            print(f"  - Character count: {result.get('char_count')}")
            print(f"  - Long form: {result.get('is_long_form')}")
            print("\n🎯 LangChain could use this service through our DID protocol!")
    except Exception as e:
        print(f"❌ Error: {e}")

    listen_task.cancel()

if __name__ == "__main__":
    print("=== LangChain Simple DID Test ===")
    print("Testing direct agent communication that LangChain would use internally")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down LangChain test")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()