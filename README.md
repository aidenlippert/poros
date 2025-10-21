# 🌐 Agent Web

**A decentralized protocol for AI agents to discover, communicate, and collaborate**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## 🎯 The Vision

Imagine asking your personal AI assistant to "book me a dentist appointment next Tuesday." Your assistant doesn't need to be programmed for every possible service—it simply discovers a dental booking agent on the Agent Web, negotiates on your behalf, and gets you an appointment.

**Agent Web makes this future possible.**

Instead of siloed AI assistants that only work within their own ecosystems, Agent Web enables a decentralized marketplace where AI agents can:

- 🔍 **Discover** specialist agents for any capability
- 🤝 **Communicate** securely using cryptographic identities
- 💰 **Transact** based on reputation and pricing
- 🌍 **Collaborate** across organizational boundaries

---

## 🚨 The Problem

Today's AI agent landscape is fragmented:

- **Walled Gardens**: ChatGPT agents can't talk to Claude agents can't talk to custom company agents
- **No Standard Protocol**: Every platform has its own proprietary communication method
- **Trust Issues**: No verifiable identity system for agents
- **Reinventing the Wheel**: Every assistant needs to implement every capability from scratch

**Result**: Isolated agent islands instead of a collaborative agent ecosystem.

---

## ✨ Our Solution

Agent Web provides a complete protocol stack for agent interoperability:

### 🔐 **Unforgeable Identity (DID)**
Every agent has a cryptographic identity: `did:agentweb:{sha256(public_key)}`
- All messages are signed with RSA-2048
- Zero-knowledge proof of identity
- No central authority required

### 🌐 **Decentralized Discovery (DHT)**
Kademlia-based distributed hash table enables:
- Peer-to-peer agent discovery
- No single point of failure
- Global capability search

### 💰 **Economic Marketplace**
Agents compete on:
- **Price**: Cost per transaction
- **Reputation**: Historical performance scores
- **Policy-based selection**: Clients choose based on their priorities

### 🛡️ **Bulletproof Hybrid Mode**
For development and reliability:
- **Central cache** for instant discovery
- **DHT fallback** for decentralization
- **100% uptime** for demos and testing

### 🔗 **True Interoperability**
Works across:
- Different AI frameworks (OpenAI, Anthropic, local models)
- Different programming languages (Python SDK, extensible to others)
- Different organizations and trust domains

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/agent-web.git
cd agent-web

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Unified Assistant Demo

Experience the full power of Agent Web with our conversational AI assistant that coordinates multiple specialist agents:

**Terminal 1: Start the Registry Server**
```bash
python3 registry_server.py
```

**Terminal 2: Start the Travel Agent**
```bash
python3 travel_agent.py
```

**Terminal 3: Start the Airline Agent**
```bash
python3 airline_agent.py
```

**Terminal 4: Start the Restaurant Agent**
```bash
python3 restaurant_agent.py
```

**Terminal 5: Launch the Unified Assistant**
```bash
streamlit run unified_assistant.py
```

Open your browser to `http://localhost:8501` and try:

- ✈️ **"Find me a flight to LAX on Monday"** → Discovers travel agent → Coordinates with airline agent → Returns flight options
- 🍽️ **"I want Italian food tonight"** → Discovers restaurant agent → Returns dining options

**One interface. Multiple specialists. Seamless coordination.**

---

## 📚 How It Works

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Personal Assistant                   │
│                  (unified_assistant.py)                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ execute_task(capability="travel_booking")
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Agent Web Protocol Layer                    │
│  - DID-based identity                                       │
│  - Capability discovery (hybrid cache + DHT)                │
│  - Cryptographic message signing                            │
│  - Economic ranking                                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Travel Agent │ │Restaurant Agt│ │ Dentist Agent│
│              │ │              │ │  (your agent)│
└──────┬───────┘ └──────────────┘ └──────────────┘
       │
       │ execute_task(capability="airline_availability")
       │
       ▼
┌──────────────┐
│Airline Agent │
└──────────────┘
```

### Core Components

1. **Agent SDK** (`agent_web.py`): Python library for building agents
   - Register capabilities with the network
   - Discover other agents by capability
   - Send/receive cryptographically signed messages
   - Handle economic negotiation

2. **Registry Server** (`registry_server.py`): Central cache for hybrid discovery
   - Instant capability lookup
   - Agent metadata storage
   - Fallback to DHT when needed

3. **Service Agents**: Specialized agents providing capabilities
   - `travel_agent.py`: Flight booking coordination
   - `airline_agent.py`: Flight availability simulation
   - `restaurant_agent.py`: Restaurant reservations
   - Build your own!

4. **Client Applications**: End-user interfaces
   - `unified_assistant.py`: Conversational UI with multi-agent coordination
   - `streamlit_travel_demo.py`: Travel-focused interface
   - Your custom client here!

---

## 🎯 Key Features

### ✅ Built-in Features

- **Unforgeable DID Identity**: Every agent has a cryptographic identity derived from its public key
- **Hybrid Discovery**: Central cache + DHT fallback ensures 100% reliability
- **Economic Marketplace**: Agents compete on price and reputation
- **Cryptographic Security**: All messages signed with RSA-2048, verified on receipt
- **Multi-Agent Coordination**: Agents can call other agents (async handler support)
- **Framework Agnostic**: Works with any AI backend (OpenAI, Anthropic, local LLMs, rule-based)
- **Demo Mode**: Reliable hybrid cache mode perfect for development and demos

### 🔮 Extensible Architecture

- **Language SDKs**: Currently Python, extensible to JavaScript, Go, Rust
- **Custom Capabilities**: Register any capability, from `dentist_booking` to `code_review`
- **Pluggable Discovery**: Swap DHT implementation, add blockchain indexing, etc.
- **Economic Policies**: Customize price/reputation trade-offs per client

---

## 🛠️ Build Your Own Agent

Creating a new agent is simple:

```python
from agent_web import Agent

# Define your agent's message handler
def handle_request(sender_did: str, message_body: dict):
    task = message_body.get("task")

    if task == "book_appointment":
        # Your business logic here
        return {
            "status": "confirmed",
            "appointment_time": "Tuesday 2pm",
            "confirmation_code": "APT-12345"
        }

    return {"status": "error", "message": "Unknown task"}

# Create and register your agent
async def main():
    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="my_agent.key",
        demo_mode=True
    )

    agent.on_message(handle_request)

    # Start listening and register capabilities
    listen_task = asyncio.create_task(
        agent.listen_and_join(
            http_host="127.0.0.1",
            http_port=8020,
            dht_host="127.0.0.1",
            dht_port=8490,
            bootstrap_node=("127.0.0.1", 8480)
        )
    )

    await agent.register(
        public_endpoint="http://127.0.0.1:8020",
        capabilities=["dentist_booking"],
        price=1.50,
        payment_method="credit_card"
    )

    print(f"🦷 Dentist Agent ready! DID: {agent.did}")
    await listen_task

if __name__ == "__main__":
    asyncio.run(main())
```

That's it! Your agent is now discoverable on the Agent Web.

---

## 📖 Documentation

### Core Concepts

- **DID (Decentralized Identifier)**: `did:agentweb:{sha256(public_key)}`
  - Self-sovereign identity
  - Public key cryptography (RSA-2048)
  - No central certificate authority

- **Capabilities**: String identifiers for what an agent can do
  - Examples: `travel_booking`, `restaurant_booking`, `code_review`
  - Agents register capabilities, clients discover by capability

- **Economic Policy**: Client-side preference for agent selection
  - `{'price': 0.3, 'reputation': 0.7}` → Prefer reputable agents
  - `{'price': 0.8, 'reputation': 0.2}` → Prefer cheap agents

- **Hybrid Discovery**: Best of both worlds
  - **Cache**: Instant lookup, great for demos
  - **DHT**: Decentralized, censorship-resistant
  - **Automatic Fallback**: Cache → DHT → Return best match

### API Reference

See [API.md](API.md) for complete SDK documentation.

---

## 🤝 Contributing

We welcome contributions! Agent Web is in active development and we'd love your help.

### Ways to Contribute

- 🐛 **Report bugs** via GitHub Issues
- 💡 **Suggest features** and improvements
- 📝 **Improve documentation** and examples
- 🔧 **Submit pull requests** for bug fixes or features
- 🌍 **Build agents** and share your use cases

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Development Setup

```bash
# Clone and setup
git clone https://github.com/yourusername/agent-web.git
cd agent-web
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests (coming soon)
pytest

# Run linter
flake8 agent_web.py
```

---

## 🗺️ Roadmap

### ✅ Completed (v0.1)

- [x] DID-based unforgeable identity
- [x] Hybrid cache + DHT discovery
- [x] Economic marketplace with price/reputation ranking
- [x] Python SDK
- [x] Async message handler support
- [x] Multi-agent coordination demo
- [x] Unified conversational assistant

### 🔮 Coming Soon (v0.2)

- [ ] Full DHT index decentralization
- [ ] JavaScript/TypeScript SDK
- [ ] Payment integration (escrow, micropayments)
- [ ] Reputation system with verifiable reviews
- [ ] Agent capability composition (chaining)
- [ ] Public registry deployment
- [ ] Performance benchmarks

### 🌟 Future Vision (v1.0+)

- [ ] Cross-chain agent identity (blockchain integration)
- [ ] Multi-language SDK support (Go, Rust, Java)
- [ ] Agent capability marketplace
- [ ] Formal protocol specification
- [ ] Enterprise-grade security audit
- [ ] Production-ready scalability

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Agent Web builds on decades of distributed systems research:

- **Kademlia DHT**: Peer-to-peer discovery (Maymounkov & Mazières, 2002)
- **Decentralized Identifiers**: W3C DID specification
- **Public Key Infrastructure**: RSA cryptography and digital signatures

Special thanks to the open-source community for the excellent libraries:

- FastAPI for HTTP endpoints
- Kademlia for DHT implementation
- Streamlit for rapid UI development
- Cryptography for RSA/signature handling

---

## 📞 Contact & Community

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Community Q&A and brainstorming
- **Twitter**: [@agentweb](https://twitter.com/agentweb) (coming soon)
- **Discord**: Join our community (link coming soon)

---

## 🚀 Get Started Now

```bash
git clone https://github.com/yourusername/agent-web.git
cd agent-web
source venv/bin/activate
pip install -r requirements.txt

# Launch the demo (4 terminals)
python3 registry_server.py          # Terminal 1
python3 travel_agent.py              # Terminal 2
python3 airline_agent.py             # Terminal 3
python3 restaurant_agent.py          # Terminal 4
streamlit run unified_assistant.py  # Terminal 5
```

**Welcome to the Agent Web. Let's build the future of AI collaboration together.** 🌐✨

---

*Built with ❤️ for a more connected AI future*
