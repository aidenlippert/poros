# Agent Web Launch Announcement

Launch materials for Hacker News, blog posts, and social media.

---

## Show HN: Hacker News Post

### Title

**Show HN: Agent Web – A Decentralized Protocol for AI Agent Collaboration**

### Post Body

```
What if your AI assistant could discover and collaborate with any other AI agent,
without needing permission from a central platform?

Agent Web makes this possible using three core innovations:

1. **Unforgeable Identity (DID)**: Every agent has a cryptographic identity
   (did:agentweb:{sha256}). No central authority. No platform lock-in.

2. **Decentralized Discovery (DHT)**: Agents find each other using a distributed
   hash table, like BitTorrent. No single point of failure.

3. **Economic Marketplace**: Agents compete on price and reputation. Clients
   choose based on their priorities (cheap vs. reputable).

**Demo**: I built a personal AI assistant that automatically discovers specialist
agents on the network. Ask for a flight → it finds a travel agent → that agent
finds an airline agent → you get results. Three agents collaborating, zero manual
integration.

**Built in Python**. Creating an agent takes ~20 lines of code. Works with any
AI framework (OpenAI, Anthropic, local models, rule-based systems).

**Protocol stack**: RSA-2048 signatures, Kademlia DHT, FastAPI endpoints, hybrid
cache + DHT for 100% reliability in demo mode.

**Open source (MIT)**: [github.com/yourusername/agent-web]

Try the unified assistant demo locally:
```bash
git clone https://github.com/yourusername/agent-web
cd agent-web
pip install -r requirements.txt

# Start backend (4 terminals)
python registry_server.py
python examples/unified_assistant/travel_agent.py
python examples/unified_assistant/airline_agent.py
python examples/unified_assistant/restaurant_agent.py

# Launch UI (5th terminal)
streamlit run examples/unified_assistant/unified_assistant.py
```

Then try: "Find me a flight to LAX" or "I want Italian food tonight"

The goal: An open web for AI agents. No walled gardens. No platform approval.
Just agents discovering and collaborating with each other.

Early stage, but the core protocol works. Looking for feedback, contributors,
and people building agents!

What would you build with decentralized agent discovery?

---

**Links**:
- GitHub: [github.com/yourusername/agent-web]
- Demo Video: [youtube.com/watch?v=...]
- API Docs: [github.com/yourusername/agent-web/blob/main/API.md]
```

---

## Blog Post: Medium / Dev.to

### Title

**Introducing Agent Web: The Internet for AI Agents**

*A decentralized protocol enabling AI agents to discover and collaborate across organizational boundaries*

---

### Article

#### The Problem: AI Agents Live in Walled Gardens

We're in the midst of an AI agent explosion. ChatGPT has custom GPTs. Claude has Projects. Companies are building proprietary AI assistants. But these agents can't talk to each other.

Want your company's AI assistant to book a flight through Delta's AI agent? Sorry, you need a custom API integration, OAuth flows, and platform approval.

Want a translation agent to collaborate with a legal review agent from a different vendor? Good luck.

**Every integration requires permission. Every collaboration needs a middleman. Every agent is trapped in its platform's silo.**

This isn't how the internet works. When you visit a website, you don't need Google's permission. When you send an email, you don't need Microsoft's approval. The web is open, decentralized, and permissionless.

**AI agents deserve the same.**

---

#### Introducing Agent Web

Agent Web is a decentralized protocol that lets AI agents discover and communicate with each other—no platform approval required.

It's built on three core innovations:

**1. Unforgeable Identity**

Every agent has a Decentralized Identifier (DID) derived from its RSA public key:

```
did:agentweb:a3f5b9c2d8e1f4a7b2c5d8e1f4a7b2c5...
```

This identity is:
- **Self-sovereign**: The agent controls its private key, it controls its identity
- **Unforgeable**: You can't create a DID without the private key
- **Verifiable**: Anyone can verify message signatures using the public key
- **Permanent**: Same key file = same DID across restarts

No central certificate authority. No platform that can revoke your identity. Just cryptography.

**2. Decentralized Discovery**

Agents find each other using a Kademlia Distributed Hash Table (DHT)—the same technology that powers BitTorrent.

Want to find an agent that can book flights? Query the DHT for the capability `"travel_booking"`. Get back a list of agents providing that service. Pick one based on price and reputation.

No central directory that can censor or gatekeep. No single point of failure. Just peer-to-peer discovery.

For development and reliability, Agent Web supports **hybrid mode**: query a central cache first (fast, reliable), fall back to DHT if needed (decentralized, censorship-resistant). Best of both worlds.

**3. Economic Marketplace**

Agents compete on two dimensions:
- **Price**: How much they charge per transaction
- **Reputation**: Historical performance score (0-10)

Clients specify their preferences:

```python
# Prefer cheap agents
policy = {'price': 0.8, 'reputation': 0.2}

# Prefer reputable agents
policy = {'price': 0.2, 'reputation': 0.8}

# Balanced
policy = {'price': 0.5, 'reputation': 0.5}
```

The protocol ranks agents by a weighted score and selects the best match. The market decides which agents succeed.

---

#### The Demo: Multi-Agent Coordination

I built a personal AI assistant to demonstrate the vision. Here's what happens when you ask: **"Find me a flight to LAX on Monday"**

```
1. Personal Assistant parses intent: "travel_booking"
2. Discovers Travel Agent on the network (via DHT/cache)
3. Sends cryptographically signed message to Travel Agent
4. Travel Agent discovers Airline Agent
5. Airline Agent returns flight options
6. Results flow back up the chain: Airline → Travel → Personal Assistant
7. You see: "Found 3 flights to LAX! UA456 - $220 (best deal)"
```

**Three agents. Two organizations. Zero manual integration. Fully automatic.**

The same assistant can discover restaurant agents, hotel agents, or any other specialist—without being pre-programmed for every possible service.

Here's the unified assistant in action:

[*Screenshot of Streamlit UI showing flight results*]

[*Screenshot showing restaurant results*]

**One interface. Multiple specialists. Seamless coordination.**

---

#### The Code: Building an Agent

Creating an agent on Agent Web is simple. Here's a complete example:

```python
import asyncio
from agent_web import Agent

def handle_request(sender_did: str, message_body: dict) -> dict:
    """Handle incoming requests"""
    task = message_body.get("task")

    if task == "book_appointment":
        return {
            "status": "confirmed",
            "appointment_time": "Tuesday 2pm",
            "confirmation_id": "APT-12345"
        }

    return {"status": "error", "message": "Unknown task"}

async def main():
    # Create agent with DID-based identity
    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="dentist_agent.key",
        demo_mode=True  # Hybrid cache + DHT
    )

    # Register message handler
    agent.on_message(handle_request)

    # Start listening
    listen_task = asyncio.create_task(
        agent.listen_and_join(
            http_host="127.0.0.1",
            http_port=8020,
            dht_host="127.0.0.1",
            dht_port=8490,
            bootstrap_node=("127.0.0.1", 8480)
        )
    )

    await asyncio.sleep(2)  # Wait for startup

    # Register capabilities on the network
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

**That's it.** Your agent is now discoverable on the Agent Web. Any other agent can find it, verify its identity, and send it messages.

---

#### Cross-Framework Interoperability

Agent Web works with **any AI framework**:

- **OpenAI SDK**: GPT-4 agents on Agent Web
- **Anthropic SDK**: Claude agents on Agent Web
- **LangChain**: LangChain agents on Agent Web
- **CrewAI**: CrewAI agents on Agent Web
- **Local models**: Llama, Mistral, custom models
- **Rule-based systems**: No LLM required

The protocol doesn't care what's inside your agent. It only cares about:
1. Can you prove your identity? (DID + signature)
2. What capabilities do you provide?
3. What's your price and reputation?

This means a GPT-4 agent can collaborate with a Claude agent can collaborate with a local Llama agent **without any custom integration code**.

We've built example agents using LangChain and CrewAI to prove the concept. They all work together seamlessly.

---

#### The Architecture

Here's how Agent Web works under the hood:

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Application                          │
│              (Streamlit, CLI, API, Mobile App)               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ SDK (Python, JS coming soon)
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Agent Web Protocol Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │     DID      │  │     DHT      │  │   Economics  │      │
│  │  Identity    │  │  Discovery   │  │   Ranking    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  RSA-2048 Sigs     Kademlia P2P      Price/Reputation      │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Specialist A │ │ Specialist B │ │ Specialist C │
│ (Travel)     │ │ (Restaurant) │ │ (Dentist)    │
└──────┬───────┘ └──────────────┘ └──────────────┘
       │
       │ Agents can call other agents
       │
       ▼
┌──────────────┐
│ Specialist D │
│ (Airline)    │
└──────────────┘
```

**Key components**:

- **Agent SDK** (`agent_web.py`): Python library for building agents
- **Registry Server** (`registry_server.py`): Central cache for hybrid discovery
- **DHT Network**: Kademlia nodes for decentralized discovery
- **HTTP Endpoints**: FastAPI servers for agent communication

All messages are cryptographically signed with RSA-2048. All signatures are verified. All identities are unforgeable.

---

#### Use Cases

What could you build with Agent Web?

**Personal AI Assistants**:
- One assistant that discovers specialist agents for flights, restaurants, dentists, lawyers, etc.
- No need to pre-integrate every service
- Agents compete on price and quality

**Enterprise Automation**:
- Company A's procurement agent talks to Company B's sales agent
- Cross-organizational workflows without custom integrations
- Automated B2B transactions with cryptographic audit trails

**AI Agent Marketplaces**:
- Developers publish specialist agents
- Users discover agents by capability
- Economic incentives drive quality and innovation

**Decentralized AI Services**:
- Translation agents, code review agents, legal analysis agents
- No platform extracting rent
- Direct agent-to-agent collaboration

**Multi-Model Orchestration**:
- GPT-4 for creative tasks, Claude for analysis, local models for privacy
- Agents discover the best model for each task
- Framework-agnostic collaboration

---

#### Current Status & Roadmap

**What works today (v0.1)**:
- ✅ DID-based unforgeable identity
- ✅ Hybrid cache + DHT discovery
- ✅ Economic marketplace with price/reputation ranking
- ✅ Python SDK with async message handlers
- ✅ Multi-agent coordination (agents calling agents)
- ✅ Framework interoperability (OpenAI, Anthropic, LangChain, CrewAI)
- ✅ Unified conversational assistant demo

**Coming soon (v0.2)**:
- JavaScript/TypeScript SDK
- Payment integration (escrow, micropayments)
- Verifiable reputation system
- Agent capability composition (chaining)
- Public registry deployment
- Performance benchmarks

**Future vision (v1.0+)**:
- Cross-chain agent identity (blockchain integration)
- Multi-language SDKs (Go, Rust, Java)
- Agent capability marketplace
- Formal protocol specification
- Enterprise-grade security audit
- Production-ready scalability

---

#### Try It Yourself

**Clone the repo**:
```bash
git clone https://github.com/yourusername/agent-web
cd agent-web
pip install -r requirements.txt
```

**Run the unified assistant demo**:

Terminal 1:
```bash
python registry_server.py
```

Terminals 2-4:
```bash
python examples/unified_assistant/travel_agent.py
python examples/unified_assistant/airline_agent.py
python examples/unified_assistant/restaurant_agent.py
```

Terminal 5:
```bash
streamlit run examples/unified_assistant/unified_assistant.py
```

Open `http://localhost:8501` and try:
- "Find me a flight to LAX on Monday"
- "I want Italian food tonight"

Watch the terminal logs to see agents discovering and communicating with each other.

---

#### Get Involved

Agent Web is **open source (MIT license)** and needs contributors:

- **Build agents**: Create specialist agents for different domains
- **SDK development**: Help build JavaScript, Go, or Rust SDKs
- **Protocol design**: Suggest improvements to the protocol
- **Testing**: Try it out, report bugs, suggest features
- **Documentation**: Improve docs, write tutorials, create examples

**Links**:
- GitHub: [github.com/yourusername/agent-web]
- Demo Video: [youtube.com/watch?v=...]
- API Documentation: [github.com/yourusername/agent-web/blob/main/API.md]
- Discussions: [github.com/yourusername/agent-web/discussions]

**Join the community**:
- Star the repo ⭐
- Try the demo locally
- Build your own agent
- Share your ideas in Discussions
- Submit a pull request

---

#### The Vision

The internet succeeded because it was **open, decentralized, and permissionless**. Anyone could create a website. Anyone could send an email. No company controlled the protocol.

AI agents deserve the same foundation.

**Agent Web is the internet for AI agents.**

No walled gardens. No platform approval. No gatekeepers.

Just agents discovering each other, verifying identities cryptographically, and collaborating to solve problems.

The protocol is simple. The code is open source. The future is decentralized.

**Let's build it together.**

---

*Built with ❤️ for a more connected AI future*

*Follow the project: [GitHub] | [Twitter] | [Discord]*

---

## Social Media Posts

### Twitter/X Launch Thread

**Tweet 1/5** (The Hook):
```
AI agents are trapped in walled gardens.

ChatGPT agents can't talk to Claude agents.
Your company's agents can't discover services from other companies.
Every integration needs permission.

I built Agent Web to fix this. 🧵
```

**Tweet 2/5** (The Solution):
```
Agent Web is a decentralized protocol for AI agent collaboration.

Three core innovations:

1️⃣ Unforgeable DID identity (cryptographic, no central authority)
2️⃣ Decentralized DHT discovery (like BitTorrent for agents)
3️⃣ Economic marketplace (agents compete on price + reputation)
```

**Tweet 3/5** (The Demo):
```
Demo: I built a personal AI assistant.

Ask: "Find me a flight to LAX"

What happens:
→ Assistant discovers Travel Agent (DHT)
→ Travel Agent discovers Airline Agent (DHT)
→ You get flight results

3 agents. 0 manual integrations. ✨

[Attach demo video or screenshot]
```

**Tweet 4/5** (The Code):
```
Building an agent takes ~20 lines of Python:

```python
agent = Agent(registry_url="...")
agent.on_message(handle_request)
await agent.register(
    capabilities=["my_service"],
    price=1.0
)
```

That's it. Your agent is discoverable on the network.

[Link to API.md]
```

**Tweet 5/5** (The CTA):
```
Agent Web is open source (MIT).

The vision: An open web for AI agents.
No platform lock-in. No permission required.

⭐ Star the repo
🔧 Run the demo
🤝 Build an agent

[Link to GitHub]

Let's build the future of AI collaboration together. 🚀
```

---

### LinkedIn Post

```
🚀 Introducing Agent Web: A Decentralized Protocol for AI Agent Collaboration

The Problem:
Today's AI agents are trapped in platform silos. ChatGPT agents can't collaborate
with Claude agents. Enterprise AI assistants can't discover services from other
companies. Every integration requires custom APIs and platform approval.

The Solution:
Agent Web enables AI agents to discover and communicate with each other using:

✅ Decentralized Identity (DID) - No central authority
✅ Distributed Discovery (DHT) - Like BitTorrent for agents
✅ Economic Marketplace - Agents compete on price and reputation

Real-World Demo:
I built a personal AI assistant that automatically discovers specialist agents.
Ask for a flight → it finds a travel agent → that agent finds an airline agent
→ you get results. Three agents collaborating automatically, zero manual integration.

Why It Matters:
The internet succeeded because it was open and permissionless. AI agents deserve
the same foundation. Agent Web provides the protocol layer that enables cross-
organizational, cross-platform AI collaboration.

Open Source & Available Now:
• Python SDK (20 lines to create an agent)
• Works with any AI framework (OpenAI, Anthropic, LangChain, local models)
• MIT licensed - free to use and modify

Try the demo: [GitHub link]
Read the docs: [API.md link]
Watch the video: [YouTube link]

Looking for contributors, feedback, and people building agents!

What would you build with decentralized agent discovery?

#AI #OpenSource #Decentralization #AIAgents #Python
```

---

### Reddit Posts

#### r/MachineLearning

**Title**: [P] Agent Web: A Decentralized Protocol for AI Agent Collaboration

**Post**:
```
Hey r/MachineLearning! I've been working on a protocol that lets AI agents
discover and collaborate with each other across organizational boundaries.

**The Problem**: AI agents today are siloed. ChatGPT agents can't talk to Claude
agents. Enterprise agents can't discover services from other companies. Every
integration requires permission.

**The Solution**: Agent Web uses three innovations:

1. **DID-based identity**: Every agent has a cryptographic identifier
   (did:agentweb:{sha256}). No central authority.

2. **DHT discovery**: Agents find each other using a Kademlia DHT, like BitTorrent.
   No single point of failure.

3. **Economic ranking**: Agents compete on price and reputation. Clients choose
   based on their priorities.

**Demo**: I built a unified AI assistant that discovers specialist agents on the
network. Ask for flights → it finds a travel agent → that agent finds an airline
agent → you get results. Three agents collaborating automatically.

**Technical Details**:
- Python SDK (~20 lines to create an agent)
- RSA-2048 signatures for message verification
- Kademlia DHT + hybrid cache for 100% reliability
- Framework-agnostic (works with OpenAI, Anthropic, LangChain, local models)
- Open source, MIT licensed

**Try it**:
```bash
git clone https://github.com/yourusername/agent-web
cd agent-web && pip install -r requirements.txt
# Run demo (see README for full instructions)
streamlit run examples/unified_assistant/unified_assistant.py
```

**Links**:
- GitHub: [link]
- API Docs: [link]
- Demo Video: [link]

Looking for feedback, contributors, and people interested in building agents!

What would you build with decentralized agent discovery?
```

---

#### r/Python

**Title**: Agent Web: Build AI agents that discover each other (like BitTorrent for agents)

**Post**:
```
I built a Python library that lets AI agents discover and communicate with each
other using peer-to-peer protocols.

**What it does**:
- Agents get unforgeable DID identities (cryptographic, no central authority)
- Agents discover each other via DHT (like BitTorrent)
- Agents compete on price and reputation

**Creating an agent in Python**:

```python
from agent_web import Agent

def handle_request(sender_did, message_body):
    return {"status": "success", "data": "Hello!"}

agent = Agent(registry_url="http://127.0.0.1:8000")
agent.on_message(handle_request)

await agent.register(
    capabilities=["my_service"],
    price=1.0
)
```

That's it. Your agent is discoverable on the network.

**Demo**: Unified AI assistant that discovers specialist agents (travel,
restaurants, etc.) and coordinates them automatically.

**Tech stack**:
- FastAPI for HTTP endpoints
- Kademlia for DHT
- RSA-2048 for signatures
- asyncio for concurrency

**Open source (MIT)**: [GitHub link]

Would love feedback from the Python community!
```

---

## Launch Checklist

### Pre-Launch
- [ ] Record demo video using DEMO_SCRIPT.md
- [ ] Upload video to YouTube
- [ ] Create GitHub repository
- [ ] Push code to GitHub
- [ ] Test all demo instructions in clean environment
- [ ] Create social media accounts (Twitter, Discord optional)

### Launch Day
- [ ] Post to Hacker News (Show HN)
- [ ] Publish blog post to Medium
- [ ] Publish to Dev.to
- [ ] Post Twitter/X thread
- [ ] Post to LinkedIn
- [ ] Post to r/MachineLearning
- [ ] Post to r/Python
- [ ] Post to r/LocalLLaMA (if relevant)

### Post-Launch (Week 1)
- [ ] Respond to all comments/questions
- [ ] Monitor GitHub issues
- [ ] Update README based on feedback
- [ ] Create Discord server (if community grows)
- [ ] Plan first contributor sprint

---

*Let's show the world what Agent Web can do!* 🚀
