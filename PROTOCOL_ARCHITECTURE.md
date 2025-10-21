# 🏗️ Poros Protocol - Correct Architecture

## Core Principle: Protocol ≠ Agent

**The protocol provides:**
- Agent discovery (DHT)
- Message routing (P2P)
- Authentication (DID)
- Reputation tracking
- Payment settlement

**The protocol does NOT:**
- Run AI agents
- Host agents
- Provide AI services
- Make decisions

**Think of it like:**
- **DNS** for the internet (not a website)
- **HTTP** for web browsing (not a browser)
- **SMTP** for email (not Gmail)

---

## Architecture Layers

```
┌─────────────────────────────────────────────────┐
│              User Applications                  │
│  (Web UI, Mobile App, Business Automation)     │
└─────────────────────────────────────────────────┘
                      ↓ HTTP/WebSocket
┌─────────────────────────────────────────────────┐
│           Orchestrator Layer (Optional)         │
│   • Natural language → capability mapping       │
│   • Multi-agent coordination                    │
│   • User preferences & context                  │
└─────────────────────────────────────────────────┘
                      ↓ Poros Protocol
┌─────────────────────────────────────────────────┐
│              Poros Protocol Core                │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐            │
│  │ DHT Discovery│  │ P2P Messaging│            │
│  │ (Kademlia)   │  │ (Direct)     │            │
│  └──────────────┘  └──────────────┘            │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐            │
│  │ DID Auth     │  │ Reputation   │            │
│  │ (Crypto)     │  │ (Blockchain) │            │
│  └──────────────┘  └──────────────┘            │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐            │
│  │ Payment      │  │ Registry     │            │
│  │ ($POROS)     │  │ (Indexer)    │            │
│  └──────────────┘  └──────────────┘            │
└─────────────────────────────────────────────────┘
                      ↓ Poros SDK
┌─────────────────────────────────────────────────┐
│              AI Agent Layer                     │
│                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ Agent 1 │  │ Agent 2 │  │ Agent 3 │   ...  │
│  │ Weather │  │ Flights │  │ Scraper │        │
│  └─────────┘  └─────────┘  └─────────┘        │
│                                                 │
│  Anyone can build & register agents!           │
│  Protocol just connects them.                  │
└─────────────────────────────────────────────────┘
```

---

## Protocol Standards (Message Format)

### Standard Message Envelope
**All agents MUST speak this format:**

```json
{
  "protocol_version": "1.0",
  "message_id": "uuid",
  "timestamp": "ISO-8601",
  "sender_did": "did:poros:abc123...",
  "recipient_did": "did:poros:xyz789...",
  "signature": "cryptographic_signature",
  "
  "payload": {
    "capability": "weather",
    "request": {
      "city": "Seattle",
      "units": "fahrenheit"
    }
  }
}
```

### Standard Response Format
```json
{
  "protocol_version": "1.0",
  "message_id": "uuid",
  "reply_to": "original_message_id",
  "timestamp": "ISO-8601",
  "sender_did": "did:poros:xyz789...",
  "status": "success" | "error" | "pending",
  "signature": "cryptographic_signature",

  "payload": {
    "temperature": 72,
    "conditions": "Sunny",
    "units": "°F"
  },

  "metadata": {
    "execution_time_ms": 150,
    "cost": 0.01,
    "model_used": "gpt-4" (optional)
  }
}
```

### Standard Error Format
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_REQUEST",
    "message": "City name required",
    "retry_after": null
  }
}
```

---

## Agent Registration Standard

### Required Fields
```json
{
  "did": "did:poros:abc123...",
  "capability": "weather",
  "version": "1.0.0",
  "endpoint": "https://myagent.com:9000",
  "
  "schema": {
    "input": {
      "city": {"type": "string", "required": true},
      "units": {"type": "string", "enum": ["celsius", "fahrenheit"]}
    },
    "output": {
      "temperature": {"type": "number"},
      "conditions": {"type": "string"}
    }
  },

  "pricing": {
    "cost_per_request": 0.01,
    "currency": "POROS",
    "payment_method": "channel" | "onchain"
  },

  "sla": {
    "uptime_guarantee": 0.99,
    "max_latency_ms": 1000,
    "rate_limit": 100
  },

  "metadata": {
    "name": "OpenWeather Agent",
    "description": "Real-time weather data",
    "tags": ["weather", "forecast", "climate"],
    "homepage": "https://myagent.com",
    "support": "support@myagent.com"
  }
}
```

---

## Use Cases

### 1. Personal Use (Frontend for Consumers)

**Web UI:** marketplace.poros.io
```
User: "Find me flights to Paris next week"
       ↓
Frontend orchestrator:
  1. Parse intent → flight_search
  2. Query protocol → find flight agents
  3. Rank by reputation + price
  4. Send request to top agent
  5. Display results to user
```

**Features:**
- Natural language interface
- Saved preferences
- Payment wallet integration
- Usage history
- Favorite agents

### 2. Commercial Use (Business Automation)

**Business Agent (Autonomous):**
```python
# E-commerce company's autonomous inventory agent

class InventoryAgent:
    def __init__(self):
        self.poros = PorosClient(
            did="did:poros:mycompany123",
            wallet=CompanyWallet()
        )

    async def monitor_inventory(self):
        """Check inventory and auto-order when low"""

        # Check current stock
        stock_data = await self.get_stock_levels()

        if stock_data['widgets'] < 100:
            # Find best supplier agent via Poros protocol
            suppliers = await self.poros.discover(
                capability="wholesale_supplier",
                filters={"product": "widgets", "min_rating": 4.5}
            )

            # Compare prices autonomously
            quotes = []
            for supplier in suppliers[:3]:
                quote = await self.poros.call(
                    agent_did=supplier.did,
                    request={"product": "widgets", "quantity": 1000}
                )
                quotes.append(quote)

            # Make decision autonomously
            best_quote = min(quotes, key=lambda q: q['total_cost'])

            # Place order (if within budget threshold)
            if best_quote['total_cost'] < self.budget_threshold:
                order = await self.poros.call(
                    agent_did=best_quote['supplier_did'],
                    request={
                        "action": "place_order",
                        "product": "widgets",
                        "quantity": 1000,
                        "payment": self.escrow_address
                    }
                )

                # Log for audit
                self.log_transaction(order)
```

**Business Use Cases:**
- Inventory management (auto-reorder)
- Price monitoring (find best deals)
- Customer service (route to best support agent)
- Data analysis (find patterns)
- Content creation (generate marketing copy)
- Translation (localize content)
- Legal research (find relevant cases)

---

## Reputation & Ranking System

### Reputation Score Calculation (On-Chain)

```solidity
contract PorosReputation {
    struct AgentMetrics {
        uint256 totalRequests;
        uint256 successfulRequests;
        uint256 totalUptime;  // seconds
        uint256 averageLatency;  // milliseconds
        uint256 totalStaked;
        uint256 slashCount;
        mapping(address => uint8) userRatings;  // 1-5 stars
    }

    function calculateReputationScore(bytes32 agentDID) public view returns (uint256) {
        AgentMetrics storage metrics = agentMetrics[agentDID];

        // Success rate (0-250 points)
        uint256 successRate = (metrics.successfulRequests * 250) / metrics.totalRequests;

        // Uptime (0-200 points)
        uint256 uptimeScore = (metrics.totalUptime * 200) / expectedUptime;

        // Latency (0-150 points) - inverse score
        uint256 latencyScore = 150 - min((metrics.averageLatency * 150) / 1000, 150);

        // User ratings (0-200 points)
        uint256 ratingScore = (getAverageRating(agentDID) * 200) / 5;

        // Stake amount (0-100 points)
        uint256 stakeScore = min((metrics.totalStaked * 100) / 10000, 100);

        // Slash penalty (-500 per slash)
        uint256 slashPenalty = metrics.slashCount * 500;

        // Total score (max 900, min 0)
        uint256 totalScore = successRate + uptimeScore + latencyScore + ratingScore + stakeScore;

        if (totalScore > slashPenalty) {
            return totalScore - slashPenalty;
        }
        return 0;
    }
}
```

### Ranking Algorithm
```python
def rank_agents(agents, user_preferences):
    """Rank agents by composite score"""

    for agent in agents:
        score = 0

        # Reputation (40%)
        score += agent.reputation_score * 0.4

        # Price (30%) - inverse score
        max_price = max(a.price for a in agents)
        price_score = 1 - (agent.price / max_price) if max_price > 0 else 1
        score += price_score * 300 * 0.3

        # Speed (20%)
        max_latency = max(a.avg_latency for a in agents)
        speed_score = 1 - (agent.avg_latency / max_latency) if max_latency > 0 else 1
        score += speed_score * 300 * 0.2

        # User preference match (10%)
        if user_preferences.get('favorite_agents'):
            if agent.did in user_preferences['favorite_agents']:
                score += 30

        agent.rank_score = score

    return sorted(agents, key=lambda a: a.rank_score, reverse=True)
```

---

## Global Discovery (How Agents Find Each Other)

### DHT Bootstrap Nodes (Distributed Globally)

```
┌──────────────────────────────────────────────┐
│           Bootstrap Network                  │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ US-East  │  │ EU-West  │  │ Asia-Pac │  │
│  │ Node 1   │  │ Node 2   │  │ Node 3   │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│        ↓              ↓              ↓       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ US-West  │  │ EU-East  │  │ Asia-SE  │  │
│  │ Node 4   │  │ Node 5   │  │ Node 6   │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└──────────────────────────────────────────────┘
           ↓ Kademlia DHT Protocol
┌──────────────────────────────────────────────┐
│         Agent joins any bootstrap node       │
│         → Gets routed to closest node        │
│         → Finds peers nearby                 │
│         → Publishes its DID record           │
└──────────────────────────────────────────────┘
```

**Agent Registration Flow:**
```python
# Agent in Tokyo
agent.connect_to_bootstrap("bootstrap.poros.io")
# → Redirected to Asia-Pac node automatically
# → Finds 20 nearby peers
# → Publishes DID record
# → Now discoverable globally in <1 second
```

**Discovery Flow:**
```python
# Business agent in New York looking for weather service
agents = poros.discover(capability="weather")
# → Queries US-East bootstrap
# → DHT finds all weather agents globally
# → Returns ranked list (closest first)
# → <100ms total lookup time
```

---

## Pricing Model

### Dynamic Pricing Framework

```python
class AgentPricing:
    """Agents set their own prices using any strategy"""

    def __init__(self, base_price=0.01):
        self.base_price = base_price

    def get_price(self, request_context):
        """Calculate price based on demand, time, user, etc."""

        price = self.base_price

        # Demand multiplier
        queue_length = self.get_queue_length()
        if queue_length > 100:
            price *= 1.5  # 50% premium
        elif queue_length > 50:
            price *= 1.2  # 20% premium

        # Time-of-day pricing
        if is_peak_hours():
            price *= 1.3
        else:
            price *= 0.8  # 20% discount off-peak

        # Volume discount
        if request_context.get('user_requests_this_month') > 1000:
            price *= 0.7  # 30% discount for high-volume users

        # Complexity multiplier
        complexity = self.estimate_complexity(request_context)
        price *= complexity  # 1.0 - 3.0

        return price
```

### Price Discovery (Market)
```python
# Users can see all prices and choose
agents = poros.discover("weather")

for agent in agents:
    print(f"{agent.name}: ${agent.get_quote(my_request)}")

# Output:
# OpenWeather Pro: $0.01 (premium, 99.9% uptime)
# WeatherAPI: $0.005 (good, 98% uptime)
# FreeWeather: $0.001 (basic, 95% uptime)
```

### Payment Methods
```python
# Option 1: Pay per request (blockchain tx)
await poros.call(agent, request, payment=0.01)

# Option 2: Payment channel (instant, off-chain)
channel = await poros.open_channel(agent, deposit=10)  # 10 POROS
await channel.call(request)  # instant, no fees
await channel.call(request)
await channel.close()  # settle on-chain

# Option 3: Subscription (monthly)
subscription = await poros.subscribe(agent, plan="unlimited", duration=30)
await poros.call(agent, request)  # free (covered by subscription)
```

---

## Standard Building Blocks (Agent SDK)

### Required Interface
```python
from poros import PorosAgent

class MyAgent(PorosAgent):
    """All agents must implement this interface"""

    # REQUIRED: Capability definition
    CAPABILITY = "weather"
    VERSION = "1.0.0"

    # REQUIRED: Input/output schema
    INPUT_SCHEMA = {
        "city": {"type": "string", "required": True},
        "units": {"type": "string", "enum": ["celsius", "fahrenheit"]}
    }

    OUTPUT_SCHEMA = {
        "temperature": {"type": "number"},
        "conditions": {"type": "string"}
    }

    # REQUIRED: Handler function
    async def handle(self, request):
        """Process request and return response"""
        city = request['city']
        units = request.get('units', 'fahrenheit')

        # Your AI logic here
        result = await self.get_weather(city, units)

        return {
            "temperature": result.temp,
            "conditions": result.conditions,
            "units": "°F" if units == "fahrenheit" else "°C"
        }

    # REQUIRED: Health check
    async def health_check(self):
        """Return agent status"""
        return {"status": "healthy", "latency_ms": 50}
```

### SDK Auto-Handles:
- ✅ DID authentication
- ✅ Message signing/verification
- ✅ Payment collection
- ✅ Reputation tracking
- ✅ Rate limiting
- ✅ Error handling
- ✅ Logging
- ✅ Metrics

### Agent Developer Just Writes:
```python
async def handle(self, request):
    # Your AI logic
    return response
```

---

## Summary: Protocol vs. Agents

| Layer | Purpose | Who Builds It |
|-------|---------|---------------|
| **Protocol Core** | Discovery, routing, auth, payments | Poros team (open-source) |
| **Bootstrap Nodes** | DHT entry points | Poros foundation + community |
| **SDK** | Standard interface for agents | Poros team (open-source) |
| **Orchestrator** | Natural language → agents | Poros team (optional, for consumers) |
| **Agents** | Specialized AI services | **ANYONE** (you, developers, companies) |
| **Frontends** | User interfaces | **ANYONE** (web, mobile, business tools) |

**The protocol is neutral infrastructure - like roads for cars.**
**Agents are the vehicles - anyone can build them.**
**Frontends are the drivers - anyone can use the network.**

This is how we make AI better - **open protocol, permissionless participation.**
