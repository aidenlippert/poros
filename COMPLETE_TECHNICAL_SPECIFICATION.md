# 🏗️ Poros Protocol - Complete Technical Specification

## Executive Summary

**What We're Building:**
A decentralized protocol that enables AI agents to discover, authenticate, communicate with, and pay each other - creating an ecosystem where specialized AI agents can collaborate to accomplish complex tasks that no single AI could do alone.

**What We're NOT Building:**
We are NOT building the AI agents themselves (except for one customer-facing orchestrator). The community builds the specialist agents.

**Think of it as:**
- **Internet** (we're building this) vs. **Websites** (community builds these)
- **HTTP/DNS** (we're building this) vs. **Apps** (community builds these)
- **Email Protocol** (we're building this) vs. **Gmail** (community builds these)

---

## 1. Core Architecture

### 1.1 System Layers

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 5: User Interface (What Users See)                  │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │  Web Dashboard  │  │  Mobile App     │                 │
│  │  - Preferences  │  │  - Chat UI      │                 │
│  │  - History      │  │  - Payments     │                 │
│  └─────────────────┘  └─────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
                         ↓ HTTPS/WebSocket
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: Orchestrator (THE ONLY AI AGENT WE BUILD)        │
│                                                             │
│  Customer-Facing AI Agent:                                 │
│  1. Natural Language Understanding                         │
│     - Parse user intent from conversation                  │
│     - Extract parameters (dates, locations, budget)        │
│     - Ask clarifying questions                             │
│                                                             │
│  2. Agent Discovery & Ranking                              │
│     - Query Poros Protocol for capable agents              │
│     - Apply user's preference weights                      │
│     - Rank agents by composite score                       │
│                                                             │
│  3. Multi-Agent Coordination                               │
│     - Break complex tasks into subtasks                    │
│     - Call multiple agents in sequence/parallel            │
│     - Handle failures and retries                          │
│                                                             │
│  4. Payment Management                                     │
│     - Create escrows for each agent call                   │
│     - Monitor task completion                              │
│     - Release payments or handle disputes                  │
│                                                             │
│  5. Human Translation                                      │
│     - Convert technical results to plain English           │
│     - Provide status updates                               │
│     - Explain what each agent did                          │
└─────────────────────────────────────────────────────────────┘
                         ↓ Poros Protocol API
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Poros Protocol Core (WE BUILD THIS)              │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  3A. Discovery Layer (DHT - Distributed Hash Table) │  │
│  │                                                      │  │
│  │  - Bootstrap Nodes (6 global regions)               │  │
│  │  - Kademlia DHT for distributed registry            │  │
│  │  - Agent registration & lookup                      │  │
│  │  - Capability-based search                          │  │
│  │  - Geographic routing (find closest agents)         │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  3B. Identity Layer (DID - Decentralized Identity)  │  │
│  │                                                      │  │
│  │  - Cryptographic key pairs (Ed25519)                │  │
│  │  - DID generation (did:poros:xxx)                   │  │
│  │  - Message signing & verification                   │  │
│  │  - Revocation mechanism                             │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  3C. Messaging Layer (P2P Communication)            │  │
│  │                                                      │  │
│  │  - Direct agent-to-agent messaging                  │  │
│  │  - Standard message format (JSON)                   │  │
│  │  - Request/response pattern                         │  │
│  │  - Async callbacks for long tasks                   │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  3D. Reputation Layer (Blockchain-Based Trust)      │  │
│  │                                                      │  │
│  │  - On-chain reputation scores                       │  │
│  │  - Immutable transaction history                    │  │
│  │  - Staking mechanism (quality bond)                 │  │
│  │  - Slashing for bad behavior                        │  │
│  │  - User ratings & reviews                           │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  3E. Payment Layer (Token Economics)                │  │
│  │                                                      │  │
│  │  - $POROS ERC-20 token (Polygon/Arbitrum)           │  │
│  │  - Escrow smart contracts                           │  │
│  │  - Payment channels (Lightning-style)               │  │
│  │  - Automatic settlements                            │  │
│  │  - Dispute resolution                               │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         ↓ Poros SDK
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Agent SDK (WE BUILD THIS - For Developers)       │
│                                                             │
│  Standard interface that ALL agents must implement:        │
│                                                             │
│  class PorosAgent:                                         │
│      capability: str        # "flight_booking"            │
│      version: str           # "1.0.0"                      │
│      input_schema: dict     # Define expected inputs       │
│      output_schema: dict    # Define response format       │
│                                                             │
│      async def handle(request):                            │
│          # Agent's custom logic here                       │
│          return response                                    │
│                                                             │
│  SDK auto-handles:                                          │
│  - DID authentication                                       │
│  - Message signing/verification                             │
│  - Payment collection                                       │
│  - Reputation tracking                                      │
│  - Error handling                                           │
│  - Logging & metrics                                        │
└─────────────────────────────────────────────────────────────┘
                         ↓ Developers implement
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Specialist Agents (COMMUNITY BUILDS THESE)       │
│                                                             │
│  Examples:                                                  │
│  - FlightBookingAgent    (books flights on airlines)       │
│  - HotelSearchAgent      (finds hotels via APIs)           │
│  - RestaurantAgent       (makes reservations)              │
│  - WeatherAgent          (provides forecasts)              │
│  - TranslationAgent      (translates languages)            │
│  - LegalResearchAgent    (searches case law)               │
│  - TaxAdvisorAgent       (calculates taxes)                │
│  - ... 1000s more                                           │
│                                                             │
│  These agents:                                              │
│  - Register themselves on Poros Protocol                   │
│  - Implement standard interface (via SDK)                  │
│  - Set their own pricing                                    │
│  - Can call OTHER agents via protocol                      │
│  - Earn $POROS tokens for their work                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Component-by-Component Specification

### 2.1 Discovery Layer (DHT)

**Purpose:** Allow agents to find each other globally without a central registry.

**Technology:** Kademlia Distributed Hash Table

**Components:**

**A. Bootstrap Nodes (6 Globally Distributed)**
```yaml
locations:
  - us-east (Virginia, USA)
  - us-west (California, USA)
  - eu-west (Ireland)
  - eu-central (Frankfurt, Germany)
  - asia-pacific (Tokyo, Japan)
  - asia-southeast (Singapore)

specs_per_node:
  - 4 vCPU
  - 8 GB RAM
  - 100 GB SSD
  - 1 Gbps network
  - 99.9% uptime SLA
```

**B. Agent Registration Flow**
```python
# When an agent starts up:
async def register_agent():
    # 1. Connect to nearest bootstrap node
    bootstrap = find_nearest_bootstrap()  # DNS geo-routing

    # 2. Join DHT network
    await dht.join(bootstrap_addr)

    # 3. Publish agent record
    record = {
        "did": agent.did,
        "capability": "flight_booking",
        "endpoint": "https://myagent.com:9000",
        "version": "1.0.0",
        "schema": {...},
        "pricing": {"per_request": 5.0},
        "reputation": 0  # Initial score
    }

    await dht.put(
        key=hash(agent.did),
        value=record,
        ttl=3600  # Re-publish every hour
    )

    # 4. Advertise capabilities (for searchability)
    await dht.put(
        key=hash("capability:flight_booking"),
        value=[agent.did],  # Add to list
        ttl=3600
    )
```

**C. Agent Discovery Flow**
```python
# When orchestrator needs to find agents:
async def find_agents(capability: str):
    # 1. Query DHT for capability
    agent_dids = await dht.get(
        key=hash(f"capability:{capability}")
    )

    # 2. Fetch full records for each agent
    agents = []
    for did in agent_dids:
        record = await dht.get(key=hash(did))
        if record:
            agents.append(record)

    # 3. Filter by availability
    live_agents = await check_agent_health(agents)

    return live_agents
```

**D. DHT Storage Structure**
```
Key Format: SHA-256(content)

Record Types:

1. Agent Record
   Key: hash(did:poros:abc123)
   Value: {
       "did": "did:poros:abc123",
       "capability": "flight_booking",
       "endpoint": "https://...",
       "schema": {...},
       "pricing": {...}
   }

2. Capability Index
   Key: hash("capability:flight_booking")
   Value: [
       "did:poros:abc123",
       "did:poros:def456",
       "did:poros:ghi789"
   ]

3. Reputation Record
   Key: hash("reputation:did:poros:abc123")
   Value: {
       "score": 875,  # Out of 1000
       "total_requests": 1250,
       "successful": 1200,
       "avg_latency_ms": 180,
       "stake_amount": 1000
   }
```

---

### 2.2 Identity Layer (DID)

**Purpose:** Give each agent a unique, cryptographically verifiable identity.

**Technology:** Decentralized Identifiers (DIDs) + Ed25519 Cryptography

**A. DID Format**
```
did:poros:<base58-encoded-public-key>

Example:
did:poros:5F3sa2TJAWMqDhXG6jhV4N8ko9SxnvyZdp

Components:
- "did" = DID scheme identifier
- "poros" = Our protocol name
- Base58 encoded public key (32 bytes)
```

**B. Key Generation**
```python
import nacl.signing
import base58

def generate_did():
    # 1. Generate Ed25519 key pair
    signing_key = nacl.signing.SigningKey.generate()
    verify_key = signing_key.verify_key

    # 2. Create DID from public key
    public_key_bytes = bytes(verify_key)
    encoded = base58.b58encode(public_key_bytes).decode('utf-8')
    did = f"did:poros:{encoded}"

    # 3. Store private key securely
    save_private_key(signing_key, f"{did}.key")

    return did, signing_key
```

**C. Message Signing**
```python
def sign_message(message: dict, signing_key):
    # 1. Canonicalize message (deterministic JSON)
    canonical = json.dumps(message, sort_keys=True)

    # 2. Create signature
    signature = signing_key.sign(canonical.encode())

    # 3. Attach signature to message
    signed_message = {
        **message,
        "signature": base64.b64encode(signature.signature).decode()
    }

    return signed_message
```

**D. Message Verification**
```python
def verify_message(signed_message: dict, sender_did: str):
    # 1. Extract signature
    signature_b64 = signed_message.pop("signature")
    signature = base64.b64decode(signature_b64)

    # 2. Get public key from DID
    encoded_key = sender_did.split(":")[-1]
    public_key_bytes = base58.b58decode(encoded_key)
    verify_key = nacl.signing.VerifyKey(public_key_bytes)

    # 3. Verify signature
    canonical = json.dumps(signed_message, sort_keys=True)
    try:
        verify_key.verify(canonical.encode(), signature)
        return True
    except:
        return False
```

---

### 2.3 Messaging Layer (P2P Communication)

**Purpose:** Enable direct, authenticated communication between agents.

**Technology:** HTTP/2 with JSON payloads, WebSocket for long-running tasks

**A. Standard Message Format**
```json
{
  "protocol_version": "1.0",
  "message_id": "uuid-v4",
  "timestamp": "2025-10-20T22:00:00Z",
  "sender_did": "did:poros:abc123",
  "recipient_did": "did:poros:def456",
  "message_type": "request" | "response" | "error" | "callback",

  "payload": {
    "capability": "flight_booking",
    "operation": "search" | "book" | "cancel",
    "parameters": {
      "origin": "SFO",
      "destination": "CDG",
      "date": "2025-10-27",
      "passengers": 2,
      "class": "economy"
    }
  },

  "context": {
    "user_id": "user123",
    "session_id": "session456",
    "parent_request_id": "uuid-parent"  // For multi-agent chains
  },

  "payment": {
    "escrow_id": "escrow789",
    "amount": 5.0,
    "currency": "POROS"
  },

  "signature": "base64-encoded-signature"
}
```

**B. Request/Response Flow**
```python
# Agent A calls Agent B
async def call_agent(recipient_did, request_payload):
    # 1. Create message
    message = {
        "protocol_version": "1.0",
        "message_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "sender_did": my_did,
        "recipient_did": recipient_did,
        "message_type": "request",
        "payload": request_payload
    }

    # 2. Sign message
    signed_message = sign_message(message, my_signing_key)

    # 3. Lookup recipient's endpoint
    recipient_record = await dht.get(hash(recipient_did))
    endpoint = recipient_record["endpoint"]

    # 4. Send HTTP POST
    response = await http_client.post(
        f"{endpoint}/invoke",
        json=signed_message,
        timeout=30
    )

    # 5. Verify response signature
    if not verify_message(response.json(), recipient_did):
        raise SecurityError("Invalid signature")

    return response.json()
```

**C. Agent HTTP Server (Receiving Side)**
```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/invoke")
async def handle_invocation(message: dict):
    # 1. Verify signature
    if not verify_message(message, message["sender_did"]):
        return {"error": "Invalid signature"}, 403

    # 2. Verify payment escrow
    escrow_id = message["payment"]["escrow_id"]
    if not await verify_escrow(escrow_id):
        return {"error": "Invalid escrow"}, 402

    # 3. Route to handler
    capability = message["payload"]["capability"]
    handler = get_handler(capability)

    # 4. Execute
    try:
        result = await handler(message["payload"])

        # 5. Create response
        response = {
            "protocol_version": "1.0",
            "message_id": str(uuid.uuid4()),
            "reply_to": message["message_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "sender_did": my_did,
            "recipient_did": message["sender_did"],
            "message_type": "response",
            "status": "success",
            "payload": result
        }

        # 6. Sign and return
        return sign_message(response, my_signing_key)

    except Exception as e:
        # Error response
        return {
            "status": "error",
            "error": {
                "code": "EXECUTION_ERROR",
                "message": str(e)
            }
        }
```

---

### 2.4 Reputation Layer (Blockchain-Based)

**Purpose:** Create immutable trust scores that users can rely on.

**Technology:** Ethereum smart contracts (deployed on Polygon for low fees)

**A. Reputation Smart Contract**
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PorosReputation {
    // Agent metrics
    struct AgentMetrics {
        uint256 totalRequests;
        uint256 successfulRequests;
        uint256 totalLatencyMs;      // Sum of all latencies
        uint256 stakedAmount;
        uint256 slashCount;
        uint256 registrationTime;
    }

    // User ratings (1-5 stars)
    struct Rating {
        uint8 stars;                 // 1-5
        string comment;
        uint256 timestamp;
        address rater;
    }

    mapping(bytes32 => AgentMetrics) public metrics;
    mapping(bytes32 => Rating[]) public ratings;
    mapping(bytes32 => uint256) public stakes;

    event RequestCompleted(
        bytes32 indexed agentDID,
        bool success,
        uint256 latencyMs,
        uint256 timestamp
    );

    event AgentRated(
        bytes32 indexed agentDID,
        address indexed rater,
        uint8 stars,
        uint256 timestamp
    );

    event AgentStaked(
        bytes32 indexed agentDID,
        uint256 amount,
        uint256 timestamp
    );

    event AgentSlashed(
        bytes32 indexed agentDID,
        uint256 amount,
        string reason,
        uint256 timestamp
    );

    // Record a completed request
    function recordRequest(
        bytes32 agentDID,
        bool success,
        uint256 latencyMs
    ) external {
        AgentMetrics storage m = metrics[agentDID];
        m.totalRequests++;
        if (success) {
            m.successfulRequests++;
        }
        m.totalLatencyMs += latencyMs;

        emit RequestCompleted(agentDID, success, latencyMs, block.timestamp);
    }

    // Submit user rating
    function rateAgent(
        bytes32 agentDID,
        uint8 stars,
        string calldata comment
    ) external {
        require(stars >= 1 && stars <= 5, "Invalid rating");

        ratings[agentDID].push(Rating({
            stars: stars,
            comment: comment,
            timestamp: block.timestamp,
            rater: msg.sender
        }));

        emit AgentRated(agentDID, msg.sender, stars, block.timestamp);
    }

    // Stake tokens (quality bond)
    function stake(bytes32 agentDID) external payable {
        require(msg.value >= 0.1 ether, "Minimum stake 0.1 ETH");
        stakes[agentDID] += msg.value;
        metrics[agentDID].stakedAmount += msg.value;

        emit AgentStaked(agentDID, msg.value, block.timestamp);
    }

    // Slash agent for bad behavior
    function slash(
        bytes32 agentDID,
        uint256 amount,
        string calldata reason
    ) external onlyGovernance {
        require(stakes[agentDID] >= amount, "Insufficient stake");

        stakes[agentDID] -= amount;
        metrics[agentDID].stakedAmount -= amount;
        metrics[agentDID].slashCount++;

        // Send slashed amount to treasury
        payable(treasury).transfer(amount);

        emit AgentSlashed(agentDID, amount, reason, block.timestamp);
    }

    // Calculate reputation score (0-1000)
    function getReputationScore(bytes32 agentDID) external view returns (uint256) {
        AgentMetrics memory m = metrics[agentDID];

        if (m.totalRequests == 0) return 0;

        // Success rate (0-300 points)
        uint256 successRate = (m.successfulRequests * 300) / m.totalRequests;

        // Average latency (0-200 points, inverse)
        uint256 avgLatency = m.totalLatencyMs / m.totalRequests;
        uint256 latencyScore = avgLatency < 1000 ? 200 - (avgLatency * 200 / 1000) : 0;

        // User ratings (0-250 points)
        uint256 ratingScore = getAverageRating(agentDID) * 50;  // 5 stars * 50 = 250

        // Stake amount (0-150 points)
        uint256 stakeScore = m.stakedAmount > 10 ether ? 150 : (m.stakedAmount * 15);

        // Volume bonus (0-100 points)
        uint256 volumeScore = m.totalRequests > 1000 ? 100 : (m.totalRequests / 10);

        // Slash penalty (-200 per slash)
        uint256 slashPenalty = m.slashCount * 200;

        // Total score
        uint256 totalScore = successRate + latencyScore + ratingScore + stakeScore + volumeScore;

        if (totalScore > slashPenalty) {
            return totalScore - slashPenalty;
        }
        return 0;
    }

    // Get average user rating (1-5 stars)
    function getAverageRating(bytes32 agentDID) public view returns (uint256) {
        Rating[] memory agentRatings = ratings[agentDID];
        if (agentRatings.length == 0) return 0;

        uint256 sum = 0;
        for (uint256 i = 0; i < agentRatings.length; i++) {
            sum += agentRatings[i].stars;
        }

        return sum / agentRatings.length;
    }
}
```

**B. Reputation Calculation (Off-Chain)**
```python
async def calculate_agent_reputation(agent_did):
    # 1. Fetch on-chain metrics
    metrics = await reputation_contract.methods.metrics(agent_did).call()

    # 2. Calculate components
    success_rate = metrics['successfulRequests'] / metrics['totalRequests']
    avg_latency = metrics['totalLatencyMs'] / metrics['totalRequests']
    avg_rating = await reputation_contract.methods.getAverageRating(agent_did).call()
    stake_amount = metrics['stakedAmount']

    # 3. Calculate score (0-1000)
    score = (
        (success_rate * 300) +
        (max(0, 200 - (avg_latency * 200 / 1000))) +
        (avg_rating * 50) +
        (min(stake_amount * 15, 150))
    )

    # 4. Apply penalties
    score -= (metrics['slashCount'] * 200)

    return max(0, min(1000, score))
```

---

### 2.5 Payment Layer (Token Economics)

**Purpose:** Enable trustless payments between users and agents.

**Technology:** ERC-20 token on Polygon, smart contract escrows

**A. $POROS Token Contract**
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract PorosToken is ERC20 {
    constructor() ERC20("Poros", "POROS") {
        _mint(msg.sender, 1_000_000_000 * 10**18);  // 1 billion tokens
    }
}
```

**B. Escrow Smart Contract**
```solidity
contract PorosEscrow {
    struct Escrow {
        address payer;
        bytes32 recipient;      // Agent DID
        uint256 amount;
        uint256 createdAt;
        uint256 expiresAt;
        bool released;
        bool refunded;
        bytes32 taskId;
    }

    mapping(bytes32 => Escrow) public escrows;
    PorosToken public porosToken;

    event EscrowCreated(
        bytes32 indexed escrowId,
        address payer,
        bytes32 recipient,
        uint256 amount
    );

    event EscrowReleased(
        bytes32 indexed escrowId,
        bytes32 recipient,
        uint256 amount
    );

    event EscrowRefunded(
        bytes32 indexed escrowId,
        address payer,
        uint256 amount
    );

    // Create escrow for agent payment
    function createEscrow(
        bytes32 recipient,
        uint256 amount,
        uint256 timeout,
        bytes32 taskId
    ) external returns (bytes32) {
        // Transfer tokens to escrow
        require(
            porosToken.transferFrom(msg.sender, address(this), amount),
            "Transfer failed"
        );

        // Create escrow record
        bytes32 escrowId = keccak256(abi.encodePacked(
            msg.sender,
            recipient,
            amount,
            block.timestamp
        ));

        escrows[escrowId] = Escrow({
            payer: msg.sender,
            recipient: recipient,
            amount: amount,
            createdAt: block.timestamp,
            expiresAt: block.timestamp + timeout,
            released: false,
            refunded: false,
            taskId: taskId
        });

        emit EscrowCreated(escrowId, msg.sender, recipient, amount);

        return escrowId;
    }

    // Release payment to agent
    function releaseEscrow(bytes32 escrowId) external {
        Escrow storage e = escrows[escrowId];

        require(!e.released && !e.refunded, "Already settled");
        require(msg.sender == e.payer, "Not payer");

        // Mark as released
        e.released = true;

        // Transfer to agent wallet
        address agentWallet = getAgentWallet(e.recipient);
        require(
            porosToken.transfer(agentWallet, e.amount),
            "Transfer failed"
        );

        emit EscrowReleased(escrowId, e.recipient, e.amount);
    }

    // Refund if task fails or times out
    function refundEscrow(bytes32 escrowId) external {
        Escrow storage e = escrows[escrowId];

        require(!e.released && !e.refunded, "Already settled");
        require(
            msg.sender == e.payer || block.timestamp > e.expiresAt,
            "Not authorized"
        );

        // Mark as refunded
        e.refunded = true;

        // Return to payer
        require(
            porosToken.transfer(e.payer, e.amount),
            "Transfer failed"
        );

        emit EscrowRefunded(escrowId, e.payer, e.amount);
    }
}
```

**C. Payment Channels (For High Frequency)**
```solidity
// Lightning-style payment channels for repeated interactions
contract PaymentChannel {
    struct Channel {
        address user;
        bytes32 agent;
        uint256 deposit;
        uint256 withdrawn;
        uint256 nonce;
        bool closed;
    }

    mapping(bytes32 => Channel) public channels;

    // Open channel with deposit
    function openChannel(bytes32 agent, uint256 deposit) external returns (bytes32) {
        bytes32 channelId = keccak256(abi.encodePacked(msg.sender, agent, block.timestamp));

        // Transfer deposit
        require(porosToken.transferFrom(msg.sender, address(this), deposit), "Transfer failed");

        channels[channelId] = Channel({
            user: msg.sender,
            agent: agent,
            deposit: deposit,
            withdrawn: 0,
            nonce: 0,
            closed: false
        });

        return channelId;
    }

    // Close channel and settle
    function closeChannel(
        bytes32 channelId,
        uint256 finalAmount,
        uint256 nonce,
        bytes memory signature
    ) external {
        Channel storage c = channels[channelId];

        require(!c.closed, "Already closed");
        require(nonce > c.nonce, "Outdated nonce");

        // Verify signature from user
        bytes32 message = keccak256(abi.encodePacked(channelId, finalAmount, nonce));
        require(verify(message, signature, c.user), "Invalid signature");

        // Transfer to agent
        address agentWallet = getAgentWallet(c.agent);
        require(porosToken.transfer(agentWallet, finalAmount), "Transfer failed");

        // Refund remainder to user
        uint256 remainder = c.deposit - finalAmount;
        if (remainder > 0) {
            require(porosToken.transfer(c.user, remainder), "Refund failed");
        }

        c.closed = true;
        c.withdrawn = finalAmount;
    }
}
```

---

### 2.6 Orchestrator Agent (THE ONLY AI WE BUILD)

**Purpose:** Customer-facing AI that understands requests, coordinates agents, and manages the experience.

**Technology:** LLM (Claude/GPT-4) + custom orchestration logic

**A. Core Components**

**1. Natural Language Understanding**
```python
async def parse_user_request(user_message: str):
    """Convert natural language to structured request"""

    # Use LLM to extract intent and parameters
    prompt = f"""
    Parse this user request and extract structured information:
    "{user_message}"

    Return JSON with:
    - intent: (plan_trip | book_flight | find_hotel | general_question)
    - parameters: {{key: value pairs}}
    - missing_info: [list of needed information]
    """

    response = await llm.complete(prompt)
    parsed = json.loads(response)

    return parsed
```

**2. Agent Discovery & Ranking**
```python
async def find_and_rank_agents(capability: str, user_preferences: dict):
    """Find capable agents and rank by user preferences"""

    # 1. Discover agents via protocol
    agents = await poros.discover(capability)

    # 2. Fetch reputation scores
    for agent in agents:
        agent.reputation = await get_reputation(agent.did)
        agent.price = agent.pricing['per_request']
        agent.avg_latency = await get_avg_latency(agent.did)

    # 3. Calculate weighted scores
    for agent in agents:
        score = 0

        # Price (inverse - lower is better)
        max_price = max(a.price for a in agents)
        price_score = (1 - agent.price / max_price) * 100
        score += price_score * user_preferences['price_weight']

        # Reputation (0-1000 scale)
        score += (agent.reputation / 1000) * 100 * user_preferences['reputation_weight']

        # Speed (inverse latency)
        max_latency = max(a.avg_latency for a in agents)
        speed_score = (1 - agent.avg_latency / max_latency) * 100
        score += speed_score * user_preferences['speed_weight']

        agent.user_score = score

    # 4. Sort by score
    return sorted(agents, key=lambda a: a.user_score, reverse=True)
```

**3. Multi-Agent Coordination**
```python
async def execute_complex_task(user_request):
    """Break down complex task and coordinate multiple agents"""

    # Parse request
    parsed = await parse_user_request(user_request)

    if parsed['intent'] == 'plan_trip':
        # Multi-agent workflow

        # Step 1: Find travel planner
        planners = await find_and_rank_agents('trip_planning', user.preferences)
        planner = planners[0]

        # Step 2: Call planner (it will coordinate sub-agents)
        plan = await call_agent(planner, {
            'destination': parsed['destination'],
            'duration': parsed['duration'],
            'budget': parsed['budget'],
            'interests': parsed['interests']
        })

        # Step 3: Present to user
        response = await format_trip_plan(plan)

        return response
```

**4. Payment Management**
```python
async def execute_with_payment(agent, request, amount):
    """Execute agent call with escrow payment"""

    # 1. Create escrow
    escrow_id = await create_escrow(
        recipient=agent.did,
        amount=amount,
        timeout=3600,  # 1 hour
        task_id=request['task_id']
    )

    # 2. Call agent with escrow reference
    try:
        result = await call_agent(agent, {
            **request,
            'escrow_id': escrow_id
        })

        # 3. Verify result
        if result['status'] == 'success':
            # Release payment
            await release_escrow(escrow_id)
            return result

        else:
            # Refund on failure
            await refund_escrow(escrow_id)
            raise Exception(f"Agent failed: {result['error']}")

    except Exception as e:
        # Refund on error
        await refund_escrow(escrow_id)
        raise e
```

**5. Human Translation**
```python
async def translate_to_human(technical_result):
    """Convert technical agent responses to plain English"""

    prompt = f"""
    Translate this technical result into friendly, conversational English:
    {json.dumps(technical_result, indent=2)}

    Make it:
    - Easy to understand
    - Highlight key information
    - Use emojis where appropriate
    - Be concise but complete
    """

    response = await llm.complete(prompt)
    return response
```

**B. Orchestrator Architecture**
```python
class PorosOrchestrator:
    """Customer-facing AI orchestrator"""

    def __init__(self):
        self.poros_client = PorosClient()
        self.llm = LLMClient()  # Claude or GPT-4
        self.conversation_history = {}

    async def handle_user_message(self, user_id: str, message: str):
        """Main entry point for user interactions"""

        # 1. Load conversation context
        context = self.conversation_history.get(user_id, [])
        context.append({"role": "user", "content": message})

        # 2. Parse intent with context
        parsed = await self.parse_with_context(message, context)

        # 3. Check if we have all needed info
        if parsed['missing_info']:
            # Ask clarifying questions
            response = await self.ask_clarifying_questions(parsed['missing_info'])

            context.append({"role": "assistant", "content": response})
            self.conversation_history[user_id] = context

            return response

        # 4. Find agents
        capability = self.intent_to_capability(parsed['intent'])
        agents = await self.find_and_rank_agents(
            capability,
            user_preferences=await self.get_user_preferences(user_id)
        )

        # 5. Present options to user (if multiple good options)
        if len(agents) > 1:
            response = await self.present_agent_options(agents[:3])
            context.append({"role": "assistant", "content": response})
            self.conversation_history[user_id] = context
            return response

        # 6. Execute with selected agent
        agent = agents[0]
        result = await self.execute_with_payment(
            agent,
            parsed['parameters'],
            agent.price
        )

        # 7. Translate to human-friendly format
        response = await self.translate_to_human(result)

        context.append({"role": "assistant", "content": response})
        self.conversation_history[user_id] = context

        return response
```

---

### 2.7 User Dashboard (Web Interface)

**Purpose:** Let users configure preferences, view history, manage payments.

**Technology:** React frontend + FastAPI backend

**A. Preference Settings UI**
```typescript
interface UserPreferences {
  priceWeight: number;        // 0-100
  reputationWeight: number;   // 0-100
  speedWeight: number;        // 0-100
  completionWeight: number;   // 0-100
  historyWeight: number;      // 0-100
}

const PreferenceSettings = () => {
  const [prefs, setPrefs] = useState<UserPreferences>({
    priceWeight: 50,
    reputationWeight: 80,
    speedWeight: 50,
    completionWeight: 100,
    historyWeight: 30
  });

  return (
    <div className="preferences">
      <h2>Agent Selection Preferences</h2>

      <Slider
        label="Price Sensitivity"
        value={prefs.priceWeight}
        onChange={(v) => setPrefs({...prefs, priceWeight: v})}
        min={0}
        max={100}
        help="Lower cost preferred"
      />

      <Slider
        label="Reputation"
        value={prefs.reputationWeight}
        onChange={(v) => setPrefs({...prefs, reputationWeight: v})}
        min={0}
        max={100}
        help="Higher ratings preferred"
      />

      <Slider
        label="Speed"
        value={prefs.speedWeight}
        onChange={(v) => setPrefs({...prefs, speedWeight: v})}
        min={0}
        max={100}
        help="Faster completion"
      />

      <Slider
        label="Completion Rate"
        value={prefs.completionWeight}
        onChange={(v) => setPrefs({...prefs, completionWeight: v})}
        min={0}
        max={100}
        help="Must finish successfully"
      />

      <Slider
        label="History with Me"
        value={prefs.historyWeight}
        onChange={(v) => setPrefs({...prefs, historyWeight: v})}
        min={0}
        max={100}
        help="Prefer agents I've used before"
      />

      <div className="presets">
        <button onClick={() => applyPreset('budget')}>
          Budget Conscious
        </button>
        <button onClick={() => applyPreset('quality')}>
          Quality First
        </button>
        <button onClick={() => applyPreset('speed')}>
          Speed Demon
        </button>
        <button onClick={() => applyPreset('balanced')}>
          Balanced
        </button>
      </div>

      <button onClick={() => savePreferences(prefs)}>
        Save Preferences
      </button>
    </div>
  );
};
```

**B. Transaction History**
```typescript
interface Transaction {
  id: string;
  timestamp: Date;
  agentName: string;
  agentDID: string;
  capability: string;
  amount: number;
  status: 'pending' | 'completed' | 'refunded';
  result: any;
}

const TransactionHistory = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  useEffect(() => {
    loadTransactions();
  }, []);

  return (
    <div className="history">
      <h2>Transaction History</h2>

      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Agent</th>
            <th>Service</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map(tx => (
            <tr key={tx.id}>
              <td>{formatDate(tx.timestamp)}</td>
              <td>{tx.agentName}</td>
              <td>{tx.capability}</td>
              <td>{tx.amount} POROS</td>
              <td>
                <StatusBadge status={tx.status} />
              </td>
              <td>
                <button onClick={() => viewDetails(tx)}>
                  Details
                </button>
                {tx.status === 'completed' && (
                  <button onClick={() => rateAgent(tx.agentDID)}>
                    Rate
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

**C. Chat Interface**
```typescript
const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    // Add user message
    setMessages([...messages, {
      role: 'user',
      content: input,
      timestamp: new Date()
    }]);

    // Call orchestrator
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: input})
    });

    const data = await response.json();

    // Add bot response
    setMessages([...messages, {
      role: 'user',
      content: input,
      timestamp: new Date()
    }, {
      role: 'assistant',
      content: data.response,
      timestamp: new Date(),
      orchestrationSteps: data.orchestration_steps
    }]);

    setInput('');
  };

  return (
    <div className="chat">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="content">{msg.content}</div>
            {msg.orchestrationSteps && (
              <OrchestrationSteps steps={msg.orchestrationSteps} />
            )}
          </div>
        ))}
      </div>

      <div className="input">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me anything..."
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
};
```

---

### 2.8 Agent SDK (For Developers)

**Purpose:** Make it trivial for developers to build and register agents.

**Technology:** Python package (pip install poros-sdk)

**A. Standard Agent Interface**
```python
from poros import Agent, capability, input_schema, output_schema

class FlightBookingAgent(Agent):
    """Example: Flight booking agent"""

    # REQUIRED: Define capability
    capability = "flight_booking"
    version = "1.0.0"

    # REQUIRED: Define schemas
    input_schema = {
        "origin": {"type": "string", "required": True},
        "destination": {"type": "string", "required": True},
        "date": {"type": "string", "format": "date", "required": True},
        "passengers": {"type": "integer", "minimum": 1},
        "class": {"type": "string", "enum": ["economy", "business", "first"]}
    }

    output_schema = {
        "confirmation_code": {"type": "string"},
        "total_cost": {"type": "number"},
        "itinerary": {"type": "object"}
    }

    # REQUIRED: Implement handler
    async def handle(self, request):
        """Process flight booking request"""

        # Validate input
        self.validate_input(request)

        # Your custom logic here
        # (call airline APIs, search flights, book tickets, etc.)

        origin = request['origin']
        destination = request['destination']
        date = request['date']

        # Example: Call airline API
        flights = await self.search_flights(origin, destination, date)

        # Book the flight
        booking = await self.book_flight(flights[0], request['passengers'])

        # Return result
        return {
            "confirmation_code": booking.confirmation,
            "total_cost": booking.price,
            "itinerary": booking.details
        }

    # Custom methods
    async def search_flights(self, origin, dest, date):
        # Call airline APIs
        pass

    async def book_flight(self, flight, passengers):
        # Book the flight
        pass
```

**B. SDK Auto-Handles**
```python
# SDK provides these automatically:

class Agent:
    def __init__(self, key_file: str = None):
        # 1. Load or generate DID
        self.did, self.signing_key = self.load_or_generate_identity(key_file)

        # 2. Connect to Poros Protocol
        self.poros = PorosClient()

        # 3. Set up HTTP server
        self.app = FastAPI()
        self.setup_routes()

    async def start(self, host='0.0.0.0', port=9000):
        """Start agent server"""

        # 1. Start HTTP server
        await self.start_server(host, port)

        # 2. Register with DHT
        await self.poros.register(
            did=self.did,
            capability=self.capability,
            endpoint=f"http://{host}:{port}",
            schema={
                "input": self.input_schema,
                "output": self.output_schema
            },
            pricing=self.pricing
        )

        print(f"✅ Agent {self.capability} registered")
        print(f"   DID: {self.did}")
        print(f"   Endpoint: http://{host}:{port}")

    def validate_input(self, request):
        """Auto-validate against input_schema"""
        # JSON Schema validation
        jsonschema.validate(request, self.input_schema)

    async def collect_payment(self, escrow_id):
        """Auto-collect payment from escrow"""
        await self.poros.release_escrow(escrow_id)

    def track_metrics(self, success, latency_ms):
        """Auto-track reputation metrics"""
        await self.poros.record_request(
            agent_did=self.did,
            success=success,
            latency=latency_ms
        )
```

**C. Developer Experience**
```bash
# Install SDK
pip install poros-sdk

# Create agent from template
poros create-agent my-flight-agent --template flight-booking

# Generates:
# my-flight-agent/
#   agent.py          # Your agent code
#   config.yaml       # Configuration
#   requirements.txt  # Dependencies
#   README.md         # Documentation

# Implement your logic
cd my-flight-agent
# Edit agent.py

# Test locally
poros test

# Deploy to production
poros deploy

# Agent is now live and earning $POROS!
```

---

## 3. Implementation Phases

### Phase 1: Core Protocol (Months 1-3)

**Deliverables:**
- ✅ DHT implementation (Kademlia)
- ✅ DID system (Ed25519 keys)
- ✅ P2P messaging (HTTP/JSON)
- ✅ Bootstrap nodes (6 regions)
- ✅ Basic agent SDK
- ✅ Smart contracts (reputation + escrow)
- ✅ $POROS token

**Team Needed:**
- 2 Backend engineers (Python)
- 1 Smart contract engineer (Solidity)
- 1 DevOps engineer
- 1 Protocol designer

**Budget:** $200K-300K

---

### Phase 2: Orchestrator & UI (Months 2-4)

**Deliverables:**
- ✅ Orchestrator agent (LLM-powered)
- ✅ User dashboard (React)
- ✅ Preference settings
- ✅ Transaction history
- ✅ Payment integration
- ✅ Chat interface

**Team Needed:**
- 2 Frontend engineers (React/TypeScript)
- 1 Backend engineer (Python/FastAPI)
- 1 AI engineer (LLM integration)
- 1 UX designer

**Budget:** $150K-250K

---

### Phase 3: Marketplace Launch (Months 4-6)

**Deliverables:**
- ✅ Agent SDK (pip package)
- ✅ Developer documentation
- ✅ Agent templates (10+ examples)
- ✅ Developer onboarding
- ✅ Agent discovery UI
- ✅ Rating system

**Team Needed:**
- 2 Developer advocates
- 1 Technical writer
- 1 Backend engineer
- 1 Marketing lead

**Budget:** $100K-150K

---

### Phase 4: Token Launch (Months 6-9)

**Deliverables:**
- ✅ $POROS token deployment
- ✅ DEX listing (Uniswap)
- ✅ Liquidity mining
- ✅ Staking mechanism
- ✅ Governance DAO

**Team Needed:**
- 1 Smart contract engineer
- 1 Tokenomics specialist
- 1 Community manager
- 1 Legal counsel

**Budget:** $300K-500K (incl. liquidity)

---

### Phase 5: Scale & Optimize (Months 9-12)

**Deliverables:**
- ✅ Performance optimization
- ✅ Additional regions
- ✅ Advanced features
- ✅ Enterprise tier
- ✅ Mobile apps

**Team Needed:**
- 2 Backend engineers
- 1 Mobile engineer (iOS/Android)
- 1 Performance engineer
- 1 Product manager

**Budget:** $200K-300K

---

## 4. Success Metrics

### Month 3 (Protocol Launch)
- 10+ specialist agents registered
- 100+ test users
- 1000+ protocol calls
- 99% uptime

### Month 6 (Marketplace Launch)
- 100+ specialist agents
- 10,000+ users
- 100,000+ protocol calls
- $50K+ agent earnings

### Month 12 (Token Launch)
- 1000+ specialist agents
- 100,000+ users
- 10M+ protocol calls
- $1M+ monthly volume
- $100M+ token market cap

---

## 5. Why This Will Work

### Problem We're Solving
- **Single AI models can't do everything well** (jack of all trades, master of none)
- **No collaboration between AI agents** (each works in isolation)
- **No economic incentives for specialization** (why build better if you can't earn?)
- **No trust system** (how do you know which agent is reliable?)

### Our Solution
- **Specialization** → Each agent does ONE thing extremely well
- **Collaboration** → Agents can call other agents
- **Economic incentives** → Agents earn $POROS for quality work
- **Trust system** → Immutable reputation on blockchain

### Competitive Advantages
1. **First mover** in decentralized AI agent protocol
2. **Network effects** (more agents → more value)
3. **Economic moat** ($POROS token required for payments)
4. **Permissionless innovation** (anyone can build agents)
5. **Neutral infrastructure** (we don't compete with agent builders)

---

## 6. What Makes This Different

### vs. ChatGPT/Claude
- They: One model, many tasks (mediocre at all)
- Us: Many specialists, one task each (excellent at one)

### vs. Agent Frameworks (LangChain, AutoGPT)
- They: Agent orchestration tools (developers use locally)
- Us: Global protocol (agents discover each other, permissionless)

### vs. Centralized AI Platforms
- They: Company controls everything (closed ecosystem)
- Us: Decentralized protocol (open ecosystem)

---

## Summary for AI Agent Helper

**We are building 3 things:**

1. **Poros Protocol** - Infrastructure layer (DHT, DID, messaging, reputation, payments)

2. **Orchestrator Agent** - Customer-facing AI (understands requests, finds agents, coordinates work)

3. **Developer Tools** - SDK, dashboard, docs (make it easy to build agents)

**We are NOT building:**
- Specialist agents (community builds these)

**Key insight:**
Specialized AI agents that collaborate > One generalist AI

**Business model:**
- Protocol takes 2.5% of every transaction
- Agents earn 97.5%
- $POROS token required for payments
- Network effects create economic moat

**Ask me ANY questions - technical, business, architecture, anything!**
