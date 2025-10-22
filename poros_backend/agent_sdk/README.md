# Poros Agent SDK

Build A2A-compliant agents that register with Poros Protocol.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn a2a-sdk[all] httpx
   ```

2. **Build your agent** (see `example_agent.py`)

3. **Register your agent:**
   - Create account: `POST https://poros-protocol.com/api/registry/users`
   - Get your agent's AgentCard ready
   - Register: `POST https://poros-protocol.com/api/registry/agents`

4. **Start receiving queries!**
   - Clients query Poros Orchestrator
   - Orchestrator discovers your agent by skill tags
   - Your agent receives `message/send` calls via A2A protocol

## AgentCard Structure

Your AgentCard must include:

```json
{
  "protocolVersion": "0.3.0",
  "name": "My Amazing Agent",
  "description": "Does amazing things",
  "url": "https://my-agent.com/a2a",
  "preferredTransport": "JSONRPC",
  "skills": [
    {
      "id": "skill_1",
      "name": "Amazing Skill",
      "description": "What this skill does",
      "tags": ["tag1", "tag2"],
      "examples": ["Example query 1", "Example query 2"]
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

## Key Points

- **Use A2A SDK:** Your agent must implement A2A protocol methods
- **Implement `message/send`:** This is how you receive queries
- **Return Task with Artifacts:** Results must be A2A-compliant
- **Skill Tags:** These are used for discovery - choose wisely!

See `example_agent.py` for a complete working example.
