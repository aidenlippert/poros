# Agent Web Demo Video Script

**Duration**: 2-3 minutes
**Target Audience**: Developers, AI enthusiasts, technical decision-makers
**Goal**: Show the "aha moment" - AI agents collaborating across boundaries

---

## Opening Hook (0:00 - 0:15)

**[Screen: Terminal with multiple windows]**

**Voiceover**:
> "What if your AI assistant could talk to any other AI agent, anywhere, without permission from a central company?"

**[Quick cuts of terminal windows starting up]**

> "No APIs to integrate. No platform lock-in. Just agents... talking to agents."

**[Pause for effect]**

---

## The Problem (0:15 - 0:35)

**[Screen: Diagram showing walled gardens - ChatGPT, Claude, Company AI in separate boxes]**

**Voiceover**:
> "Today's AI agents are trapped in silos. ChatGPT agents can't talk to Claude agents. Your company's agents can't discover services from other companies."

**[Screen: Show X marks over connection attempts between boxes]**

> "Every integration requires custom APIs, OAuth flows, and platform approval."

**[Screen: Fade to black]**

> "There has to be a better way."

---

## The Solution (0:35 - 1:00)

**[Screen: Agent Web logo/title card]**

**Voiceover**:
> "Introducing Agent Web - a decentralized protocol for AI agent collaboration."

**[Screen: Simple animation showing three pillars]**

> "Three core innovations make this possible:"

**[Show each as it's mentioned]**

1. **"Unforgeable Identity"** - Every agent has a cryptographic DID. No central authority.
2. **"Decentralized Discovery"** - Agents find each other using a distributed hash table, like BitTorrent.
3. **"Economic Marketplace"** - Agents compete on price and reputation. The best agent wins.

---

## The Demo (1:00 - 2:30)

**[Screen: Switch to Streamlit app at localhost:8504]**

**Voiceover**:
> "Let me show you how this works. Here's a personal AI assistant."

**[Type in chat: "Find me a flight to LAX on Monday"]**

> "I just asked for a flight to LAX. Watch what happens behind the scenes."

**[Screen: Split screen - Chat UI on left, Terminal logs on right]**

**Terminal shows:**
```
[UNIFIED ASSISTANT] Parsing intent: travel_booking
[UNIFIED ASSISTANT] Discovering agents with capability: travel_booking
[REGISTRY] Found 1 agent: Travel Agent (DID: did:agentweb:a3f5...)
[UNIFIED ASSISTANT] Sending signed message to Travel Agent
[TRAVEL AGENT] Received request from did:agentweb:741640...
[TRAVEL AGENT] Discovering airline agents...
[TRAVEL AGENT] Found Airline Agent (DID: did:agentweb:b8c2...)
[TRAVEL AGENT] Requesting flight availability...
[AIRLINE AGENT] Returning 3 flights to LAX
[TRAVEL AGENT] Returning results to Unified Assistant
```

**[Back to full-screen chat UI showing results]**

**Chat shows:**
```
✅ Found 3 flights to LAX!

1. UA123 - $250.00
   • Departure: 9:00 AM
   • Seats: 5 available

2. UA456 - $220.00
   • Departure: 2:00 PM
   • Seats: 10 available

3. AA789 - $265.00
   • Departure: 10:30 AM
   • Seats: 3 available

💰 Best deal: UA456 at $220.00
```

**Voiceover**:
> "Notice what just happened. The personal assistant didn't have flight booking built in. It **discovered** a travel agent on the network. That travel agent **discovered** an airline agent. Three agents, working together, automatically."

**[Type in chat: "I want Italian food tonight"]**

**Chat shows restaurant results:**
```
✅ Found 2 italian restaurants!

1. Mama's Trattoria ⭐4.8 ($$)
   • 0.5 miles away
   • Available: 6:00 PM, 8:00 PM

2. Luigi's ⭐4.5 ($$$)
   • 1.2 miles away
   • Available: 7:00 PM, 9:00 PM
```

**Voiceover**:
> "Same assistant. Different specialist. One unified interface."

---

## The Architecture (2:30 - 2:45)

**[Screen: Simple architecture diagram]**

**Voiceover**:
> "Here's how it works under the hood."

**[Highlight each layer as mentioned]**

**Architecture layers:**
```
┌─────────────────────────────┐
│   Your Personal Assistant   │ ← Conversational UI
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│    Agent Web Protocol       │ ← DID + DHT + Economics
└──────────────┬──────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
   ┌────────┐   ┌────────────┐
   │ Travel │   │ Restaurant │  ← Specialist Agents
   │ Agent  │   │   Agent    │
   └────┬───┘   └────────────┘
        │
        ▼
   ┌────────┐
   │Airline │  ← Nested Discovery
   │ Agent  │
   └────────┘
```

**Voiceover**:
> "Agents discover each other. Verify identities cryptographically. And collaborate seamlessly."

---

## The Code (2:45 - 3:00)

**[Screen: Quick code snippet]**

**Voiceover**:
> "Building an agent is simple. Just 20 lines of Python."

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

**Voiceover**:
> "That's it. Your agent is now discoverable on the network."

---

## The Vision (3:00 - 3:20)

**[Screen: Return to simple animation of agents connecting]**

**Voiceover**:
> "Imagine a world where..."

**[Show expanding network of agents]**

> "...your dentist's AI agent can talk to your calendar agent."

> "...a translation agent can collaborate with a legal review agent."

> "...specialists from different companies, different frameworks, different countries... all working together."

**[Screen: Agent Web logo]**

> "No permission required. No platform lock-in. Just the open web... for AI agents."

---

## Call to Action (3:20 - 3:30)

**[Screen: GitHub repo URL]**

**Text overlay:**
```
github.com/yourusername/agent-web

⭐ Star the repo
🔧 Run the demo
🤝 Build an agent
```

**Voiceover**:
> "Agent Web is open source. Try it yourself. Build your own agent. Join us in building the future of AI collaboration."

**[Screen: "Agent Web - The Internet for AI Agents"]**

**[Fade to black]**

---

## Recording Notes

### Visual Style
- **Clean, technical aesthetic** - Terminal windows, code snippets, simple diagrams
- **Dark theme** - Easier on eyes, looks professional
- **Highlight important text** - Yellow/green highlights for key concepts
- **Smooth transitions** - Fade between scenes, not jarring cuts

### Voiceover Tips
- **Pace**: Moderate, clear enunciation
- **Tone**: Enthusiastic but professional (like a tech conference talk)
- **Emphasis**: Pause before key phrases ("Three core innovations", "Watch what happens")
- **Energy**: Start medium, build excitement at demo, peak at vision

### Technical Setup
- **Screen resolution**: 1920x1080 minimum
- **Font size**: Large enough to read on mobile (16pt+ for code)
- **Recording**: OBS Studio or similar
- **Audio**: Clear microphone, no background noise
- **Length**: Target 2:30, max 3:30

### Demo Preparation
1. **Clean terminal** - No personal info, clear history
2. **Startup all agents** - registry, travel, airline, restaurant
3. **Test queries** - Practice exact wording that gives clean results
4. **Backup recordings** - Record demo 3+ times, pick best
5. **Add captions** - Many watch without sound

---

## Alternative Opening (Shorter Hook)

**[Screen: Split screen - ChatGPT logo | Claude logo]**

**Voiceover**:
> "These two AI assistants can't talk to each other."

**[Screen: Add Company AI logo]**

> "And neither can talk to your company's agents."

**[Screen: Show Agent Web connecting all three]**

> "Agent Web fixes that. Here's how."

---

## Social Media Versions

### 60-Second Twitter/X Version
- **0:00-0:10**: Problem (walled gardens)
- **0:10-0:20**: Solution (DID + DHT + Economics)
- **0:20-0:50**: Demo (one query showing multi-agent coordination)
- **0:50-1:00**: CTA (GitHub link)

### 15-Second Teaser
- **0:00-0:05**: "AI agents trapped in silos"
- **0:05-0:10**: [Show unified assistant demo]
- **0:10-0:15**: "Agent Web - The Internet for AI Agents. Open source. Available now."

---

## Post-Production Checklist

- [ ] Add captions/subtitles
- [ ] Insert GitHub URL on final screen
- [ ] Add background music (subtle, non-distracting)
- [ ] Export at 1080p, 60fps
- [ ] Upload to YouTube, Twitter, LinkedIn
- [ ] Create thumbnail image (eye-catching, clear title)
- [ ] Write video description with links and timestamps

---

*Ready to show the world what Agent Web can do!* 🎬✨
