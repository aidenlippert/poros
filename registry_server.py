# registry_server.py
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, computed_field
from typing import List, Dict

# --- Pydantic Models ---

class AgentCapabilityRegistration(BaseModel):
    # NEW: Agents only register their capabilities and ID
    agent_id: str
    capabilities: List[str]

class TransactionReport(BaseModel):
    # Unchanged from v2
    agent_id: str
    success: bool
    response_time_ms: float

class ReputationStats(BaseModel):
    # Unchanged from v2
    successes: int = 0
    failures: int = 0
    total_response_time_ms: float = 0.0
    count: int = 0

    @computed_field
    @property
    def success_rate(self) -> float:
        if self.count == 0:
            return 0.0
        return (self.successes / self.count) * 100.0

    @computed_field
    @property
    def avg_response_time_ms(self) -> float:
        if self.count == 0:
            return 0.0
        return self.total_response_time_ms / self.count

    @computed_field
    @property
    def reputation_score(self) -> float:
        if self.count == 0:
            return 5.0  # Default score for new agents
        rate = self.success_rate / 100.0  # 0.0 to 1.0
        time_penalty = max(0, (self.avg_response_time_ms - 500) / 1000.0)
        return max(0.1, (rate * 5.0) - time_penalty)

class ReputationRequest(BaseModel):
    # NEW: Model for batch reputation requests
    agent_ids: List[str]

class ReputationResponse(BaseModel):
    # NEW: Model for batch reputation responses
    reputations: Dict[str, ReputationStats]

# --- In-Memory "Databases" ---
# AGENT_DB IS GONE! All agent data now lives on the DHT
INDEX_DB: Dict[str, List[str]] = {}  # NEW: "capability" -> ["agent_id", ...]
REPUTATION_DB: Dict[str, ReputationStats] = {}  # Unchanged

# --- SPRINT 9: DEMO MODE CACHE ---
class AgentRecord(BaseModel):
    did: str
    endpoint: str
    public_key_pem: str
    capabilities: List[str]
    price: float

AGENT_DATA_CACHE: Dict[str, AgentRecord] = {}

# --- FastAPI App ---
app = FastAPI(title="Agent Web - Indexer & Reputation Bureau (v3)")

# --- SPRINT 9: DEMO MODE CACHE ENDPOINTS ---
@app.post("/publish_record", status_code=201)
async def publish_record(record: AgentRecord):
    """
    DEMO MODE: Service agents publish their full record to the central cache.
    This ensures 100% reliability for investor demos.
    """
    AGENT_DATA_CACHE[record.did] = record
    print(f"[DEMO CACHE] Published record for DID: {record.did} with capabilities: {record.capabilities}")
    return {"status": "cached", "did": record.did}

@app.get("/discover/{did}", response_model=AgentRecord)
async def discover(did: str):
    """
    DEMO MODE: Customers can discover service agents via DID lookup in the central cache.
    This bypasses DHT for guaranteed discovery.
    """
    if did not in AGENT_DATA_CACHE:
        raise HTTPException(status_code=404, detail=f"DID {did} not found in cache")
    print(f"[DEMO CACHE] Discovered DID: {did}")
    return AGENT_DATA_CACHE[did]

@app.post("/register_capabilities", status_code=201)
async def register_capabilities(reg: AgentCapabilityRegistration):
    """
    Register an agent's capabilities in the index.
    Note: Agent data (endpoint, pubkey, price) is now stored on the DHT.
    """
    for capability in reg.capabilities:
        if capability not in INDEX_DB:
            INDEX_DB[capability] = []
        if reg.agent_id not in INDEX_DB[capability]:
            INDEX_DB[capability].append(reg.agent_id)
    print(f"[INDEXER] Registered capabilities for: {reg.agent_id} - {reg.capabilities}")
    return {"status": "success", "agent_id": reg.agent_id}

@app.post("/report", status_code=200)
async def report_transaction(report: TransactionReport):
    """
    Reports transaction outcomes to the reputation system.
    """
    agent_id = report.agent_id
    if agent_id not in REPUTATION_DB:
        # First time this agent is being reported on
        REPUTATION_DB[agent_id] = ReputationStats()

    stats = REPUTATION_DB[agent_id]
    stats.count += 1
    stats.total_response_time_ms += report.response_time_ms
    if report.success:
        stats.successes += 1
    else:
        stats.failures += 1

    print(f"[REPUTATION] Updated stats for {agent_id}: Success={stats.successes}/{stats.count}, AvgTime={stats.avg_response_time_ms:.1f}ms, Score={stats.reputation_score:.2f}")
    return {"status": "reputation_updated"}

@app.get("/search", response_model=List[str])
async def search_by_capability(capability: str):
    """
    Searches the index for agents with a specific capability.
    Returns a list of agent IDs (agent data must be fetched from DHT).
    """
    matching_agents = INDEX_DB.get(capability, [])
    if matching_agents:
        print(f"[INDEXER] Found {len(matching_agents)} agents with capability '{capability}': {matching_agents}")
    return matching_agents

@app.post("/get_reputations", response_model=ReputationResponse)
async def get_reputations(req: ReputationRequest):
    """
    Gets the latest reputation stats for a list of agents.
    """
    results = {}
    for agent_id in req.agent_ids:
        # Return default stats for any agent not yet in the DB
        results[agent_id] = REPUTATION_DB.get(agent_id, ReputationStats())
    print(f"[REPUTATION] Returning reputation data for {len(results)} agents")
    return ReputationResponse(reputations=results)

# Note: The /discover endpoint is DELETED - discovery now happens via DHT

if __name__ == "__main__":
    print("Starting Agent Web Indexer/Reputation Server (v3) on http://127.0.0.1:8000")
    print("Note: This server no longer stores agent data - that's on the DHT!")
    uvicorn.run(app, host="127.0.0.1", port=8000)