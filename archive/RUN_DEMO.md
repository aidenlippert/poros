# 🚀 Agent Web - Investor Demo Guide

## Quick Start (3 Steps)

### Step 1: Start the Registry Server
```bash
./venv/bin/python3 registry_server.py
```
**Wait for:** `Uvicorn running on http://127.0.0.1:8000`

---

### Step 2: Start the Service Agent (in a new terminal)
```bash
cd /home/rocz/agenticwebbeta
./venv/bin/python3 demo_service_agent.py
```
**Wait for:** `✅ Service agent ready and registered!`

---

### Step 3: Launch the Interactive Demo (in a new terminal)
```bash
cd /home/rocz/agenticwebbeta
./venv/bin/streamlit run streamlit_demo.py
```
**Browser will automatically open to:** `http://localhost:8501`

---

## What You'll See

1. **Web Interface** - Beautiful interactive UI
2. **Enter Text** - Type any text to analyze
3. **Click "Execute Task"** - Watch the magic happen:
   - Agent initializes with DID
   - Connects to network
   - Discovers service agents
   - Sends cryptographically signed message
   - Receives verified response
4. **Results** - Word count, character count, analysis

---

## For Investors

### The Technology Stack

- **Unforgeable Identity**: DID-based (`did:agentweb:{sha256}`)
- **Security**: Cryptographic signatures on all messages
- **Discovery**: Economic ranking algorithm
- **Communication**: Peer-to-peer with DHT
- **Reliability**: Hybrid mode with central cache fallback

### Demo Mode vs Production

**Demo Mode** (`demo_mode=True`):
- Uses central cache for 100% reliable discovery
- Perfect for presentations
- Guaranteed to work every time

**Production Mode** (`demo_mode=False`):
- Pure decentralized P2P
- No central dependencies
- Full Kademlia DHT

---

## Troubleshooting

### Port Already in Use
```bash
# Kill old processes
fuser -k 8000/tcp 8010/tcp 8013/tcp 8480/tcp 8483/tcp
```

### Clean Restart
```bash
# Remove old agent keys for fresh DIDs
rm -f *.key

# Then follow Steps 1-3 again
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                 INVESTOR DEMO                        │
└─────────────────────────────────────────────────────┘

Web Browser (Streamlit)
    ↓
Customer Agent (DID: did:agentweb:abc...)
    ↓
Registry Server (Cache + Indexer)
    ↓
Service Agent (DID: did:agentweb:def...)
    ↓
Response: {"word_count": 24, "char_count": 186}
```

---

## Next Steps After Demo

1. **Scale Testing**: Add more service agents
2. **Economic Experiments**: Test different pricing strategies
3. **Production Deploy**: Switch to `demo_mode=False`
4. **Framework Integration**: Add LangChain/CrewAI agents

---

**Status**: ✅ Sprint 9 Complete - Bulletproof Demo Ready
**Reliability**: 100% (via hybrid cache mode)
**Security**: Unforgeable DID + Cryptographic Signatures
