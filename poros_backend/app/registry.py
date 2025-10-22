"""
Poros Protocol - Agent Registry (A2P: Agent-to-Platform)

Handles agent registration, AgentCard storage, and discovery.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select, Session
from typing import List, Optional
from datetime import datetime

from .models import (
    User, UserCreate, Token,
    RegisteredAgent, AgentCardSubmit, AgentCardResponse
)
from .database import get_session
from .auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/registry", tags=["Agent Registry"])


# ============================================
# USER / OWNER MANAGEMENT
# ============================================

@router.post("/users", response_model=Token, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """
    Create a new agent owner account.

    Returns JWT token for authentication.
    """
    # Check if username exists
    existing = session.exec(
        select(User).where(User.username == user_data.username)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Create user
    hashed = hash_password(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Generate token
    token = create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )

    return Token(access_token=token)


@router.post("/auth/token", response_model=Token)
async def login(
    username: str,
    password: str,
    session: Session = Depends(get_session)
):
    """
    Login and get JWT token.
    """
    user = session.exec(
        select(User).where(User.username == username)
    ).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Generate token
    token = create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )

    return Token(access_token=token)


# ============================================
# AGENT REGISTRATION (A2P)
# ============================================

@router.post("/agents", response_model=AgentCardResponse, status_code=status.HTTP_201_CREATED)
async def register_agent(
    submission: AgentCardSubmit,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Register a new agent by submitting its AgentCard.

    This is the A2P (Agent-to-Platform) registration endpoint.

    The AgentCard must conform to the A2A protocol specification:
    - protocolVersion
    - name, description
    - url, preferredTransport
    - skills (array of skill objects with id, name, description, tags)
    - capabilities, security schemes, etc.
    """
    agent_card = submission.agent_card

    # Validate required fields
    required_fields = ["name", "description", "url", "skills"]
    for field in required_fields:
        if field not in agent_card:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"AgentCard missing required field: {field}"
            )

    # Extract key fields
    name = agent_card["name"]
    description = agent_card["description"]
    url = agent_card["url"]
    preferred_transport = agent_card.get("preferredTransport", "JSONRPC")

    # Generate unique agent_id if not provided
    # Format: owner-username/agent-name
    agent_id = agent_card.get("id")
    if not agent_id:
        agent_id = f"{current_user['sub']}/{name.lower().replace(' ', '-')}"

    # Check if agent_id already exists
    existing = session.exec(
        select(RegisteredAgent).where(RegisteredAgent.agent_id == agent_id)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Agent ID '{agent_id}' already registered"
        )

    # Extract skill tags for indexing
    skills = agent_card.get("skills", [])
    skills_tags = []
    for skill in skills:
        skills_tags.extend(skill.get("tags", []))

    # Create registered agent
    agent = RegisteredAgent(
        agent_id=agent_id,
        owner_id=current_user["user_id"],
        agent_card=agent_card,
        name=name,
        description=description,
        url=url,
        preferred_transport=preferred_transport,
        skills_tags=skills_tags,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(agent)
    session.commit()
    session.refresh(agent)

    return AgentCardResponse(
        id=agent.id,
        agent_id=agent.agent_id,
        owner_id=agent.owner_id,
        name=agent.name,
        description=agent.description,
        url=agent.url,
        agent_card=agent.agent_card,
        is_active=agent.is_active,
        created_at=agent.created_at
    )


# ============================================
# AGENT DISCOVERY
# ============================================

@router.get("/agents", response_model=List[AgentCardResponse])
async def list_agents(
    skill_tag: Optional[str] = Query(None, description="Filter by skill tag"),
    name_search: Optional[str] = Query(None, description="Search by name or description"),
    active_only: bool = Query(True, description="Only show active agents"),
    limit: int = Query(50, le=100),
    session: Session = Depends(get_session)
):
    """
    Discover registered agents.

    Supports filtering by:
    - skill_tag: Find agents with specific skill tags (e.g., "hotel_booking")
    - name_search: Text search in agent name/description
    - active_only: Only return active agents
    """
    query = select(RegisteredAgent)

    # Filter by active status
    if active_only:
        query = query.where(RegisteredAgent.is_active == True)

    # Execute and get all results
    agents = session.exec(query).all()

    # Filter by skill tag (in Python since we store as JSON array)
    if skill_tag:
        agents = [a for a in agents if skill_tag in a.skills_tags]

    # Filter by name search
    if name_search:
        search_lower = name_search.lower()
        agents = [
            a for a in agents
            if search_lower in a.name.lower() or search_lower in a.description.lower()
        ]

    # Limit results
    agents = agents[:limit]

    return [
        AgentCardResponse(
            id=a.id,
            agent_id=a.agent_id,
            owner_id=a.owner_id,
            name=a.name,
            description=a.description,
            url=a.url,
            agent_card=a.agent_card,
            is_active=a.is_active,
            created_at=a.created_at
        )
        for a in agents
    ]


@router.get("/agents/{agent_id}", response_model=AgentCardResponse)
async def get_agent(
    agent_id: str,
    session: Session = Depends(get_session)
):
    """
    Get a specific agent's AgentCard by ID.
    """
    agent = session.exec(
        select(RegisteredAgent).where(RegisteredAgent.agent_id == agent_id)
    ).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found"
        )

    return AgentCardResponse(
        id=agent.id,
        agent_id=agent.agent_id,
        owner_id=agent.owner_id,
        name=agent.name,
        description=agent.description,
        url=agent.url,
        agent_card=agent.agent_card,
        is_active=agent.is_active,
        created_at=agent.created_at
    )


@router.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete an agent (only owner can delete).
    """
    agent = session.exec(
        select(RegisteredAgent).where(RegisteredAgent.agent_id == agent_id)
    ).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found"
        )

    # Check ownership
    if agent.owner_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this agent"
        )

    session.delete(agent)
    session.commit()

    return None
