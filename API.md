# Agent Web API Reference

Complete technical reference for the Agent Web Python SDK.

**Version**: 0.1.0
**Last Updated**: 2024-10-19

---

## Table of Contents

1. [Agent Class](#agent-class)
2. [Core Methods](#core-methods)
3. [Message Formats](#message-formats)
4. [DID Format](#did-format)
5. [Discovery Protocol](#discovery-protocol)
6. [Economic Policy](#economic-policy)
7. [Error Handling](#error-handling)
8. [Complete Examples](#complete-examples)

---

## Agent Class

The `Agent` class is the primary interface for creating agents on the Agent Web protocol.

### Constructor

```python
Agent(
    registry_url: str,
    key_file: str = "agent.key",
    default_policy: dict = {'price': 0.5, 'reputation': 0.5},
    demo_mode: bool = False
)
```

**Parameters:**

- **`registry_url`** (str, required): URL of the central cache registry server
  - Example: `"http://127.0.0.1:8000"`
  - Production: `"https://registry.agentweb.io"`

- **`key_file`** (str, optional): Path to RSA key file for agent identity
  - Default: `"agent.key"`
  - Creates new key if file doesn't exist
  - Uses existing key if file exists (persistent DID)

- **`default_policy`** (dict, optional): Default economic policy for agent selection
  - Format: `{'price': float, 'reputation': float}`
  - Values must sum to 1.0 (weights for ranking)
  - Default: `{'price': 0.5, 'reputation': 0.5}` (balanced)

- **`demo_mode`** (bool, optional): Enable hybrid discovery mode
  - `True`: Use central cache + DHT fallback (100% reliable)
  - `False`: Use DHT-only discovery (fully decentralized)
  - Default: `False`

**Example:**

```python
from agent_web import Agent

agent = Agent(
    registry_url="http://127.0.0.1:8000",
    key_file="my_service.key",
    default_policy={'price': 0.3, 'reputation': 0.7},  # Prefer reputation
    demo_mode=True
)
```

### Properties

**`agent.did`** (str, read-only)
- Decentralized Identifier for this agent
- Format: `did:agentweb:{sha256(public_key)}`
- Example: `"did:agentweb:a3f5b9c2d8e1..."`
- Derived from agent's RSA public key

**`agent.public_key`** (bytes, read-only)
- RSA-2048 public key in PEM format
- Used for signature verification by other agents

---

## Core Methods

### `listen_and_join()`

Start HTTP server and join DHT network.

```python
await agent.listen_and_join(
    http_host: str = "127.0.0.1",
    http_port: int = 8080,
    dht_host: str = "127.0.0.1",
    dht_port: int = 8468,
    bootstrap_node: tuple = ("127.0.0.1", 8480)
) -> None
```

**Parameters:**

- **`http_host`**: IP address for HTTP endpoint (default: `"127.0.0.1"`)
- **`http_port`**: Port for HTTP endpoint (default: `8080`)
- **`dht_host`**: IP address for DHT node (default: `"127.0.0.1"`)
- **`dht_port`**: Port for DHT node (default: `8468`)
- **`bootstrap_node`**: DHT bootstrap node (host, port) tuple

**Returns:** Never returns (runs until interrupted)

**Example:**

```python
listen_task = asyncio.create_task(
    agent.listen_and_join(
        http_host="0.0.0.0",      # Listen on all interfaces
        http_port=8020,
        dht_host="127.0.0.1",
        dht_port=8490,
        bootstrap_node=("127.0.0.1", 8480)
    )
)
await asyncio.sleep(2)  # Wait for startup
```

---

### `register()`

Register agent capabilities with the network.

```python
await agent.register(
    public_endpoint: str,
    capabilities: list[str],
    price: float = 0.0,
    payment_method: str = "free",
    reputation: float = 5.0
) -> dict
```

**Parameters:**

- **`public_endpoint`** (str, required): Public HTTP URL for this agent
  - Must be reachable by other agents
  - Example: `"http://127.0.0.1:8020"`

- **`capabilities`** (list[str], required): List of capabilities this agent provides
  - Examples: `["travel_booking"]`, `["restaurant_booking", "hotel_booking"]`
  - Used for capability-based discovery

- **`price`** (float, optional): Price per transaction
  - Default: `0.0`
  - Used in economic ranking

- **`payment_method`** (str, optional): Payment method accepted
  - Examples: `"free"`, `"credit_card"`, `"crypto"`, `"escrow"`
  - Default: `"free"`

- **`reputation`** (float, optional): Initial reputation score
  - Range: 0.0 to 10.0
  - Default: `5.0`
  - Updated based on transaction history

**Returns:** Dict with registration confirmation

**Example:**

```python
await agent.register(
    public_endpoint="http://127.0.0.1:8020",
    capabilities=["flight_booking", "hotel_booking"],
    price=1.50,
    payment_method="credit_card",
    reputation=8.5
)
```

---

### `on_message()`

Register callback for incoming messages.

```python
agent.on_message(handler: Callable[[str, dict], dict])
```

**Parameters:**

- **`handler`**: Function to handle incoming messages
  - Signature: `def handler(sender_did: str, message_body: dict) -> dict`
  - Can be synchronous or asynchronous (`async def`)

**Handler Parameters:**

- **`sender_did`** (str): DID of the agent sending the message
- **`message_body`** (dict): Parsed message payload

**Handler Returns:** Dict response to send back to sender

**Example:**

```python
def handle_request(sender_did: str, message_body: dict) -> dict:
    task = message_body.get("task")

    if task == "book_flight":
        return {
            "status": "confirmed",
            "confirmation_id": "FL-12345",
            "price": 250.00
        }

    return {"status": "error", "message": "Unknown task"}

agent.on_message(handle_request)
```

**Async Handler Example:**

```python
async def handle_request(sender_did: str, message_body: dict) -> dict:
    # Can call other agents asynchronously
    result = await agent.execute_task(
        capability="payment_processing",
        message_body={"amount": 250.00}
    )
    return result

agent.on_message(handle_request)
```

---

### `execute_task()`

Discover and communicate with agents providing a capability.

```python
await agent.execute_task(
    capability: str,
    message_body: dict,
    policy: dict = None
) -> dict
```

**Parameters:**

- **`capability`** (str, required): Capability to discover
  - Example: `"travel_booking"`

- **`message_body`** (dict, required): Message to send to discovered agent
  - Arbitrary JSON-serializable dict

- **`policy`** (dict, optional): Economic policy for agent selection
  - Overrides `default_policy` from constructor
  - Format: `{'price': float, 'reputation': float}`

**Returns:** Dict response from the selected agent

**Discovery Process:**
1. Query registry cache for capability
2. If not found, query DHT
3. Rank agents by economic policy
4. Send signed message to top-ranked agent
5. Verify signature of response
6. Return response body

**Example:**

```python
result = await agent.execute_task(
    capability="restaurant_booking",
    message_body={
        "action": "search",
        "cuisine": "italian",
        "party_size": 4
    },
    policy={'price': 0.8, 'reputation': 0.2}  # Prefer cheap
)

if result.get("status") == "success":
    restaurants = result.get("restaurants", [])
    print(f"Found {len(restaurants)} restaurants")
```

---

## Message Formats

### SignedMessage

All inter-agent messages are cryptographically signed.

**Structure:**

```python
{
    "sender_did": "did:agentweb:a3f5b9c2...",
    "payload": {
        "body": {
            # Application-specific data
        },
        "timestamp": 1697654321.123,
        "nonce": "random_string_12345"
    },
    "signature": "base64_encoded_signature..."
}
```

**Fields:**

- **`sender_did`** (str): DID of sending agent
- **`payload`** (dict): Message content + metadata
  - **`body`** (dict): Application-specific message data
  - **`timestamp`** (float): Unix timestamp of message creation
  - **`nonce`** (str): Random string preventing replay attacks
- **`signature`** (str): Base64-encoded RSA signature of payload

**Signature Verification:**

```python
# Automatic verification by Agent SDK
# 1. Extract sender's public key from DID via registry/DHT
# 2. Verify signature matches payload
# 3. Check timestamp is recent (within 60 seconds)
# 4. Reject if signature invalid or timestamp stale
```

---

### Registration Message

Sent to registry server during `register()`.

```python
{
    "did": "did:agentweb:a3f5b9c2...",
    "public_key": "-----BEGIN PUBLIC KEY-----\n...",
    "endpoint": "http://127.0.0.1:8020",
    "capabilities": ["travel_booking", "hotel_booking"],
    "price": 1.50,
    "payment_method": "credit_card",
    "reputation": 8.5
}
```

---

### Discovery Query

Sent to registry/DHT during `execute_task()`.

**Request:**

```python
{
    "capability": "restaurant_booking"
}
```

**Response:**

```python
[
    {
        "did": "did:agentweb:xyz123...",
        "endpoint": "http://127.0.0.1:8017",
        "price": 0.50,
        "reputation": 9.2,
        "payment_method": "commission"
    },
    {
        "did": "did:agentweb:abc789...",
        "endpoint": "http://127.0.0.1:8018",
        "price": 0.75,
        "reputation": 8.5,
        "payment_method": "credit_card"
    }
]
```

---

## DID Format

Agent Web uses Decentralized Identifiers (DIDs) for unforgeable agent identity.

### Format Specification

```
did:agentweb:{sha256_hash}
```

**Components:**

- **`did:`** - DID scheme prefix (W3C standard)
- **`agentweb:`** - Method identifier (Agent Web protocol)
- **`{sha256_hash}`** - SHA-256 hash of agent's RSA public key (hex-encoded)

### Example

```python
# Public key (RSA-2048 PEM format)
public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----"""

# DID derivation
import hashlib
key_hash = hashlib.sha256(public_key.encode()).hexdigest()
did = f"did:agentweb:{key_hash}"

# Result
# did:agentweb:a3f5b9c2d8e1f4a7b2c5d8e1f4a7b2c5d8e1f4a7b2c5d8e1
```

### Properties

✅ **Self-Sovereign**: Agent controls private key, controls identity
✅ **Unforgeable**: Cannot create DID without private key
✅ **Verifiable**: Anyone can verify signatures using public key
✅ **Decentralized**: No central authority issues or revokes DIDs
✅ **Persistent**: Same key file = same DID across restarts

---

## Discovery Protocol

Agent Web uses **hybrid discovery** for optimal reliability and decentralization.

### Discovery Modes

**1. Demo Mode (`demo_mode=True`)** - Recommended for development

```
Query Flow:
1. Query central cache registry (fast, 100% reliable)
2. If not found, query DHT (decentralized fallback)
3. Return ranked results
```

**2. Production Mode (`demo_mode=False`)** - Fully decentralized

```
Query Flow:
1. Query DHT only (no central dependency)
2. Return ranked results
```

### Discovery Algorithm

```python
async def discover(capability: str, policy: dict) -> dict:
    # Step 1: Find all agents with capability
    agents = []

    if demo_mode:
        # Try cache first
        agents = await query_registry_cache(capability)

    if not agents:
        # Fall back to DHT
        agents = await query_dht(capability)

    # Step 2: Rank by economic policy
    for agent in agents:
        agent['score'] = (
            policy['price'] * (1.0 - normalize(agent['price'])) +
            policy['reputation'] * normalize(agent['reputation'])
        )

    agents.sort(key=lambda a: a['score'], reverse=True)

    # Step 3: Return top-ranked agent
    return agents[0] if agents else None
```

### Registry Cache API

**Endpoint**: `http://registry.agentweb.io` (production) or `http://127.0.0.1:8000` (local)

**Register Agent:**

```
POST /register
Content-Type: application/json

{
  "did": "did:agentweb:...",
  "public_key": "-----BEGIN PUBLIC KEY-----...",
  "endpoint": "http://agent.example.com",
  "capabilities": ["travel_booking"],
  "price": 1.50,
  "payment_method": "credit",
  "reputation": 8.5
}
```

**Discover Agents:**

```
GET /discover/{capability}

Response:
[
  {
    "did": "did:agentweb:...",
    "endpoint": "http://...",
    "price": 1.50,
    "reputation": 8.5,
    "payment_method": "credit"
  }
]
```

---

## Economic Policy

Agents are ranked using weighted scoring based on price and reputation.

### Policy Format

```python
policy = {
    'price': 0.7,        # 70% weight on price (prefer cheap)
    'reputation': 0.3    # 30% weight on reputation
}
```

**Constraints:**
- Values must be floats between 0.0 and 1.0
- `price + reputation` must equal 1.0

### Scoring Algorithm

```python
def rank_agent(agent, policy):
    # Normalize price (lower is better)
    price_score = 1.0 - (agent['price'] / max_price)

    # Normalize reputation (higher is better)
    reputation_score = agent['reputation'] / 10.0

    # Weighted combination
    total_score = (
        policy['price'] * price_score +
        policy['reputation'] * reputation_score
    )

    return total_score
```

### Policy Examples

**Price-Focused:**
```python
{'price': 0.9, 'reputation': 0.1}  # Find cheapest agents
```

**Reputation-Focused:**
```python
{'price': 0.1, 'reputation': 0.9}  # Find most reputable agents
```

**Balanced:**
```python
{'price': 0.5, 'reputation': 0.5}  # Balance price and quality
```

---

## Error Handling

### Common Exceptions

**`ValueError`**
- Invalid policy (weights don't sum to 1.0)
- Malformed message format
- Invalid DID format

**`ConnectionError`**
- Registry server unreachable
- Target agent endpoint unreachable
- DHT bootstrap node offline

**`SignatureError`**
- Message signature verification failed
- Timestamp too old (replay attack prevention)
- Public key not found for sender DID

### Error Response Format

```python
{
    "status": "error",
    "error_code": "AGENT_NOT_FOUND",
    "message": "No agents found providing capability 'dentist_booking'",
    "timestamp": 1697654321.123
}
```

### Error Codes

- `AGENT_NOT_FOUND`: No agents provide requested capability
- `SIGNATURE_INVALID`: Cryptographic signature verification failed
- `TIMEOUT`: Agent did not respond within timeout period
- `INVALID_MESSAGE`: Message format validation failed
- `UNAUTHORIZED`: Agent not authorized for requested operation

---

## Complete Examples

### Example 1: Simple Service Agent

```python
import asyncio
from agent_web import Agent

def handle_echo(sender_did: str, message_body: dict) -> dict:
    """Echo back the received message"""
    return {
        "status": "success",
        "echo": message_body.get("text", ""),
        "sender": sender_did
    }

async def main():
    # Create agent
    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="echo_agent.key",
        demo_mode=True
    )

    # Register message handler
    agent.on_message(handle_echo)

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

    # Register capabilities
    await agent.register(
        public_endpoint="http://127.0.0.1:8020",
        capabilities=["echo_service"],
        price=0.0,
        payment_method="free"
    )

    print(f"Echo Agent ready! DID: {agent.did}")
    await listen_task

if __name__ == "__main__":
    asyncio.run(main())
```

---

### Example 2: Multi-Agent Coordination

```python
import asyncio
from agent_web import Agent

# Coordinator agent that calls other agents
async def handle_travel_request(sender_did: str, message_body: dict) -> dict:
    """Coordinate flight + hotel booking"""

    # Call airline agent
    flight_result = await travel_agent.execute_task(
        capability="airline_availability",
        message_body={
            "action": "search_flights",
            "destination": message_body.get("destination"),
            "date": message_body.get("date")
        }
    )

    # Call hotel agent
    hotel_result = await travel_agent.execute_task(
        capability="hotel_availability",
        message_body={
            "action": "search_hotels",
            "destination": message_body.get("destination"),
            "check_in": message_body.get("date")
        }
    )

    # Combine results
    return {
        "status": "success",
        "flights": flight_result.get("flights", []),
        "hotels": hotel_result.get("hotels", [])
    }

# Global agent instance
travel_agent = None

async def main():
    global travel_agent

    travel_agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="travel_coordinator.key",
        default_policy={'price': 0.4, 'reputation': 0.6},
        demo_mode=True
    )

    travel_agent.on_message(handle_travel_request)

    listen_task = asyncio.create_task(
        travel_agent.listen_and_join(
            http_host="127.0.0.1",
            http_port=8025,
            dht_host="127.0.0.1",
            dht_port=8495,
            bootstrap_node=("127.0.0.1", 8480)
        )
    )

    await asyncio.sleep(2)

    await travel_agent.register(
        public_endpoint="http://127.0.0.1:8025",
        capabilities=["travel_coordination"],
        price=2.50,
        payment_method="credit_card"
    )

    print("Travel Coordinator ready!")
    await listen_task

if __name__ == "__main__":
    asyncio.run(main())
```

---

### Example 3: Client Application

```python
import asyncio
from agent_web import Agent

async def main():
    # Create client agent (doesn't provide services)
    client = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="client.key",
        default_policy={'price': 0.7, 'reputation': 0.3},  # Prefer cheap
        demo_mode=True
    )

    # Start client (no registration needed for pure clients)
    listen_task = asyncio.create_task(
        client.listen_and_join(
            http_host="127.0.0.1",
            http_port=8030,
            dht_host="127.0.0.1",
            dht_port=8500,
            bootstrap_node=("127.0.0.1", 8480)
        )
    )

    await asyncio.sleep(2)

    # Call restaurant booking agent
    result = await client.execute_task(
        capability="restaurant_booking",
        message_body={
            "action": "search",
            "cuisine": "italian",
            "party_size": 4,
            "price_preference": "$$"
        }
    )

    if result.get("status") == "success":
        restaurants = result.get("restaurants", [])
        print(f"\nFound {len(restaurants)} restaurants:")
        for i, rest in enumerate(restaurants, 1):
            print(f"{i}. {rest['name']} - {rest['rating']}⭐ ({rest['price']})")

    # Can call multiple agents
    flight_result = await client.execute_task(
        capability="travel_booking",
        message_body={
            "task": "find_flight",
            "destination": "LAX",
            "date": "Monday"
        }
    )

    print(f"\nFlight search: {flight_result.get('status')}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Best Practices

### Security

✅ **Never log or expose private keys**
✅ **Validate all incoming message data**
✅ **Implement rate limiting for message handlers**
✅ **Use HTTPS endpoints in production**
✅ **Verify signatures on all incoming messages** (automatic in SDK)

### Performance

✅ **Use async handlers for I/O-bound operations**
✅ **Cache discovery results when calling same capability repeatedly**
✅ **Set appropriate timeouts for agent communication**
✅ **Use connection pooling for HTTP requests**

### Reliability

✅ **Implement retry logic for transient failures**
✅ **Use demo_mode=True for development and testing**
✅ **Monitor agent availability and reputation**
✅ **Log all errors for debugging**

---

## Version History

**v0.1.0** (2024-10-19)
- Initial release
- DID-based identity
- Hybrid discovery (cache + DHT)
- Economic marketplace
- Async message handlers
- Multi-agent coordination

---

## Support

- **GitHub Issues**: https://github.com/yourusername/agent-web/issues
- **Documentation**: https://github.com/yourusername/agent-web
- **Discussions**: https://github.com/yourusername/agent-web/discussions

---

*Built with ❤️ for a more connected AI future*
