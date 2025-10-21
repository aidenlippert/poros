# Agent Web Examples

This directory contains working examples demonstrating different aspects of the Agent Web protocol.

## 📁 Directory Structure

### `unified_assistant/` - **The Flagship Demo** ⭐
Complete conversational AI assistant that coordinates multiple specialist agents.

**What it demonstrates:**
- Natural language intent parsing
- Multi-agent coordination (Personal → Travel → Airline)
- Automatic specialist discovery
- Profile-based personalization
- Conversational UI with Streamlit

**Files:**
- `unified_assistant.py` - Main conversational interface (Sprint 11)
- `travel_agent.py` - Travel booking coordinator
- `airline_agent.py` - Flight availability service
- `restaurant_agent.py` - Restaurant booking service
- `streamlit_travel_demo.py` - Travel-focused demo (Sprint 10)
- `streamlit_conversation_demo.py` - Restaurant-focused demo (Sprint 10)

**Quick Start:**
```bash
# Terminal 1: Start registry
cd ../..
python3 registry_server.py

# Terminal 2-4: Start specialist agents
python3 examples/unified_assistant/travel_agent.py
python3 examples/unified_assistant/airline_agent.py
python3 examples/unified_assistant/restaurant_agent.py

# Terminal 5: Launch UI
streamlit run examples/unified_assistant/unified_assistant.py
```

Then try:
- "Find me a flight to LAX on Monday"
- "I want Italian food tonight"

---

### `basic_demo/` - **Getting Started**
Simple agent-to-agent communication examples.

**What it demonstrates:**
- Basic agent registration
- DID-based identity
- Cryptographic message signing
- Simple request/response patterns

**Files:**
- `agent_one_did.py` - Service provider agent
- `agent_two_did.py` - Service consumer agent
- `agent_three_did.py` - Additional agent example
- `service_agent_did.py` - Generic service agent template
- `demo_service_agent.py` - Service demo
- `demo_customer_agent.py` - Customer demo

**Quick Start:**
```bash
# Terminal 1: Start registry
cd ../..
python3 registry_server.py

# Terminal 2: Start service agent
python3 examples/basic_demo/agent_one_did.py

# Terminal 3: Start customer agent
python3 examples/basic_demo/agent_two_did.py
```

---

### `framework_integration/` - **Interoperability Demos**
Examples showing Agent Web works with different AI frameworks.

**What it demonstrates:**
- Framework-agnostic protocol
- CrewAI integration
- LangChain integration
- Cross-framework agent communication

**Files:**
- `crew_ai_client_did.py` - CrewAI agent using Agent Web
- `langchain_client_did.py` - LangChain agent using Agent Web

**Quick Start:**
```bash
# Terminal 1: Start registry
cd ../..
python3 registry_server.py

# Terminal 2: Start CrewAI agent
python3 examples/framework_integration/crew_ai_client_did.py

# Terminal 3: Start LangChain agent
python3 examples/framework_integration/langchain_client_did.py
```

---

## 🎯 Learning Path

**For Beginners:**
1. Start with `basic_demo/` to understand core concepts
2. Review the simple request/response pattern
3. Understand DID-based identity

**For Developers:**
1. Study `unified_assistant/` for production patterns
2. Learn multi-agent coordination
3. Explore intent parsing and routing

**For Framework Users:**
1. Check `framework_integration/` examples
2. See how your favorite framework integrates
3. Build your own integration

---

## 📚 Documentation

- [Main README](../README.md) - Project overview
- [API Reference](../API.md) - SDK documentation
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute

---

## 💡 Building Your Own Agent

All examples follow this pattern:

```python
from agent_web import Agent

# 1. Define message handler
def handle_request(sender_did, message_body):
    # Your business logic here
    return {"status": "success", "data": "result"}

# 2. Create agent
agent = Agent(
    registry_url="http://127.0.0.1:8000",
    key_file="my_agent.key",
    demo_mode=True
)

# 3. Register handler
agent.on_message(handle_request)

# 4. Start listening
await agent.listen_and_join(...)

# 5. Register capabilities
await agent.register(
    public_endpoint="http://127.0.0.1:8020",
    capabilities=["my_capability"],
    price=1.0,
    payment_method="credit"
)
```

---

## 🚀 Next Steps

After exploring these examples:

1. **Modify an existing agent** - Change capabilities, pricing, or logic
2. **Create a new agent** - Build your own specialist agent
3. **Combine agents** - Create complex multi-agent workflows
4. **Share your work** - Contribute back to the project!

---

*Happy building! 🌐✨*
