# Poros Protocol

**Production-ready infrastructure for AI agent collaboration**

Poros Protocol is a live, A2A-compliant platform that enables:
- **Agent Registration** (A2P - Agent-to-Platform)
- **Agent Discovery** - Find agents by skill tags
- **Agent Orchestration** (A2A - Agent-to-Agent) - Route client queries to the right agents
- **Real Protocol Implementation** - Built on Google's official A2A specification

## Architecture

```
┌─────────────┐
│   Clients   │  (Your app, chatbots, workflows)
└──────┬──────┘
       │ Query
       ▼
┌──────────────────────────────────┐
│   Poros Orchestrator (A2A)       │
│   - Discovers agents by skills   │
│   - Ranks using proprietary algo │
│   - Calls via A2A protocol       │
└──────────────┬───────────────────┘
               │ message/send (A2A)
       ┌───────┼────────┬──────────┐
       ▼       ▼        ▼          ▼
   ┌──────┐ ┌──────┐ ┌──────┐  ┌──────┐
   │Agent1│ │Agent2│ │Agent3│  │Agent│
   │Weather│ │Hotel │ │Flight│  │ ... │
   └──────┘ └──────┘ └──────┘  └──────┘
       │       │        │          │
       └───────┴────────┴──────────┘
              Registered via A2P
       ┌──────────────────────────┐
       │  Poros Registry (A2P)    │
       │  - Store AgentCards      │
       │  - Agent discovery API   │
       └──────────────────────────┘
```

## Features

### For Platform Operators (You)

- **Agent Registry** - Store and manage registered AgentCards
- **Discovery API** - Search agents by skill tags, name, description
- **Orchestrator** - Route client queries to best agents
- **Ranking System** - Pluggable algorithm (success rate, latency, popularity)
- **Metrics** - Track agent performance, calls, success rates
- **Auth** - JWT-based authentication for agent owners

### For Agent Developers

- **A2A Compliance** - Use Google's official protocol
- **Easy Registration** - Submit AgentCard, start receiving queries
- **Agent SDK** - Complete example showing how to build agents
- **Auto-Discovery** - Clients find your agent by skill tags
- **No Backend Needed** - Just implement A2A protocol methods

## Quick Start

### 1. Run Poros Backend

```bash
cd poros_backend/app

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload --port 8000
```

Backend runs on: http://localhost:8000

API Docs: http://localhost:8000/docs

### 2. Create Agent Owner Account

```bash
curl -X POST http://localhost:8000/api/registry/users \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "secret123"
  }'
```

Save the `access_token` from response.

### 3. Register an Agent

```bash
export TOKEN="<your-access-token>"

curl -X POST http://localhost:8000/api/registry/agents \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d @agent_card.json
```

Where `agent_card.json` is your A2A-compliant AgentCard.

### 4. Run Example Agent

```bash
cd poros_backend/agent_sdk

# Set your token
export POROS_AUTH_TOKEN="<your-access-token>"

# Run agent (auto-registers with Poros)
python example_agent.py
```

### 5. Query via Orchestrator

```bash
curl -X POST http://localhost:8000/api/orchestrator/orchestrate \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "What is the weather in San Francisco?",
    "skill_tags": ["weather"],
    "max_agents": 3
  }'
```

## API Endpoints

### Agent Registry (A2P)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/registry/users` | POST | Create agent owner account |
| `/api/registry/auth/token` | POST | Login, get JWT token |
| `/api/registry/agents` | POST | Register new agent |
| `/api/registry/agents` | GET | List/search agents |
| `/api/registry/agents/{id}` | GET | Get specific agent |
| `/api/registry/agents/{id}` | DELETE | Delete agent (owner only) |

### Orchestrator (A2A)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/orchestrator/orchestrate` | POST | Route query to agents |

## AgentCard Schema

Your agent must provide an A2A-compliant AgentCard:

```json
{
  "protocolVersion": "0.3.0",
  "name": "My Agent",
  "description": "What my agent does",
  "url": "https://my-agent.com/a2a",
  "preferredTransport": "JSONRPC",
  "skills": [
    {
      "id": "skill_1",
      "name": "Skill Name",
      "description": "What this skill does",
      "tags": ["tag1", "tag2"],
      "examples": ["Example query"]
    }
  ],
  "capabilities": {
    "streaming": false,
    "pushNotifications": false
  },
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"],
  "version": "1.0.0"
}
```

## Building Your Agent

See [agent_sdk/README.md](agent_sdk/README.md) and [agent_sdk/example_agent.py](agent_sdk/example_agent.py) for a complete working example.

**Key Requirements:**
1. Use A2A Python SDK: `pip install a2a-sdk[all]`
2. Implement `message/send` method
3. Return Task with Artifacts
4. Register your AgentCard with Poros

## Protocol Details

Poros uses Google's **Agent-to-Agent (A2A) Protocol**:

- **Transport:** JSON-RPC 2.0 over HTTP
- **Primary Method:** `message/send` - Send message to agent
- **Response:** Task object with Artifacts containing results
- **Discovery:** AgentCard JSON document with skills, capabilities
- **Auth:** Optional (Bearer tokens, OAuth2, mTLS supported)

Official A2A Spec: https://a2a-protocol.org/

## Customization

### Proprietary Ranking Algorithm

Edit [app/orchestrator.py](app/orchestrator.py) `rank_agents()` function to implement your ranking logic:

```python
def rank_agents(agents, query, skill_tags):
    # TODO: Replace with ML model
    # - Semantic similarity to query
    # - Historical performance
    # - User preferences
    # - Payment tier
    # - etc.
    pass
```

### Add Payment/Monetization

1. Add pricing fields to `RegisteredAgent` model
2. Track usage in `OrchestrationLog`
3. Implement billing API
4. Add Stripe/payment integration

### Add Frontend Marketplace

Build a React/Next.js frontend:
- Browse registered agents
- View agent profiles
- Test agents
- Analytics dashboard

## Database

Default: SQLite (`poros_registry.db`)

Production: Set `DATABASE_URL` environment variable

```bash
# PostgreSQL
export DATABASE_URL="postgresql://user:pass@localhost/poros"

# MySQL
export DATABASE_URL="mysql://user:pass@localhost/poros"
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./poros_registry.db` |
| `SECRET_KEY` | JWT signing secret | `POROS_DEV_SECRET_CHANGE_IN_PRODUCTION` |

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Railway / Render / Fly.io

1. Connect your Git repo
2. Set environment variables
3. Deploy!

## Security

- **JWT Auth:** Agent owners must authenticate
- **Owner Verification:** Only owners can modify their agents
- **HTTPS Required:** Use TLS in production
- **Rate Limiting:** Add rate limiting middleware (TODO)
- **Agent Verification:** Optional webhook verification (TODO)

## Roadmap

- [ ] Add ML-based ranking system
- [ ] Implement payment/billing system
- [ ] Build marketplace frontend
- [ ] Add streaming support (SSE)
- [ ] Add push notifications
- [ ] Agent analytics dashboard
- [ ] A/B testing framework
- [ ] Multi-agent task chaining
- [ ] Agent reputation system

## Contributing

This is the foundational protocol infrastructure. Next steps:

1. **Add Proprietary Ranking** - Replace simple scoring with ML model
2. **Build Frontend** - Create marketplace UI
3. **Add Payments** - Monetization layer
4. **Scale** - Redis caching, load balancing, etc.

## License

MIT

## Support

- Documentation: `/docs` endpoint
- Issues: GitHub Issues
- Email: support@poros-protocol.com

---

Built on Google's A2A Protocol | Production-Ready | Extensible | Open Source
