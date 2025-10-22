"""
Poros Protocol - Database Models

Stores registered AgentCards and orchestration history using the A2A protocol schema.
"""

from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


# ============================================
# USER / AGENT OWNER MODELS
# ============================================

class User(SQLModel, table=True):
    """Agent owner/developer account"""
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: Optional[str] = None
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)


# ============================================
# AGENT CARD STORAGE (A2A Protocol)
# ============================================

class RegisteredAgent(SQLModel, table=True):
    """
    Stores AgentCards for registered agents.

    This is the A2P (Agent-to-Platform) registration system.
    Agents submit their AgentCard to Poros Registry.
    """
    __tablename__ = "registered_agents"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Agent identity
    agent_id: str = Field(index=True, unique=True)  # Unique agent identifier
    owner_id: int = Field(foreign_key="users.id")

    # AgentCard JSON (full A2A protocol AgentCard)
    agent_card: Dict[str, Any] = Field(sa_column=Column(JSON))

    # Extracted for indexing/search
    name: str = Field(index=True)
    description: str
    url: str  # Primary endpoint
    preferred_transport: str = Field(default="JSONRPC")

    # Skills (for capability-based discovery)
    skills_tags: List[str] = Field(sa_column=Column(JSON), default=[])  # Flattened skill tags

    # Status
    is_active: bool = Field(default=True)
    last_verified: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Metrics (for ranking)
    total_calls: int = Field(default=0)
    success_rate: float = Field(default=1.0)
    avg_latency_ms: float = Field(default=0.0)


# ============================================
# ORCHESTRATION LOGS
# ============================================

class OrchestrationLog(SQLModel, table=True):
    """
    Logs client queries and orchestration results.

    Useful for debugging, analytics, and improving ranking.
    """
    __tablename__ = "orchestration_logs"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Client request
    client_query: Dict[str, Any] = Field(sa_column=Column(JSON))
    skill_filter: Optional[str] = None

    # Selected agents
    selected_agents: List[str] = Field(sa_column=Column(JSON))  # List of agent_ids

    # Results
    results: Dict[str, Any] = Field(sa_column=Column(JSON))
    success: bool = Field(default=True)

    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    latency_ms: float = Field(default=0.0)


# ============================================
# PYDANTIC MODELS (API Request/Response)
# ============================================

class UserCreate(BaseModel):
    """Create new agent owner account"""
    username: str
    email: Optional[str] = None
    password: str


class Token(BaseModel):
    """JWT auth token"""
    access_token: str
    token_type: str = "bearer"


class AgentCardSubmit(BaseModel):
    """
    Agent submits their AgentCard for registration.

    This should be a complete A2A protocol AgentCard.
    """
    agent_card: Dict[str, Any]  # Full AgentCard JSON


class AgentCardResponse(BaseModel):
    """Return registered AgentCard"""
    id: int
    agent_id: str
    owner_id: int
    name: str
    description: str
    url: str
    agent_card: Dict[str, Any]
    is_active: bool
    created_at: datetime


class OrchestrateRequest(BaseModel):
    """
    Client request to orchestrate a query across agents.

    The orchestrator will discover agents by skill tags and route the query.
    """
    # Natural language query or structured request
    query: str

    # Optional skill filter (e.g., "hotel_booking", "weather")
    skill_tags: Optional[List[str]] = None

    # Optional agent preference
    prefer_agent_ids: Optional[List[str]] = None

    # Max agents to call
    max_agents: int = Field(default=3, le=10)


class OrchestrateResponse(BaseModel):
    """Orchestration result"""
    query: str
    selected_agents: List[Dict[str, Any]]  # List of {agent_id, name, url}
    results: List[Dict[str, Any]]  # List of agent responses
    summary: Optional[str] = None  # Optional aggregated summary
    latency_ms: float
