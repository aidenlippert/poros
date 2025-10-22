"""
Poros Protocol - Orchestrator (A2A: Agent-to-Agent Communication)

Routes client queries to registered agents using the A2A protocol.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import asyncio

# Simple HTTP client for calling agents
import httpx

from .models import (
    RegisteredAgent,
    OrchestrationLog,
    OrchestrateRequest,
    OrchestrateResponse
)
from .database import get_session
from .auth import get_current_user_optional

# Import PROPRIETARY ranking system (YOUR competitive advantage!)
from .ranking import rank_agents

router = APIRouter(prefix="/api/orchestrator", tags=["Orchestrator"])


# ============================================
# A2A AGENT CALLING
# ============================================

async def call_agent_http(
    agent: RegisteredAgent,
    query: str,
    timeout: float = 30.0
) -> Dict[str, Any]:
    """
    Call an agent using simple HTTP POST.

    Agents implement a simple /query endpoint that accepts JSON.
    """
    try:
        # Simple HTTP call to agent endpoint
        url = agent.url
        if not url.endswith("/query"):
            url = f"{url}/query"

        payload = {"query": query}

        start_time = time.time()

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        latency = (time.time() - start_time) * 1000  # Convert to ms

        # Return standardized result
        return {
            "agent_id": agent.agent_id,
            "agent_name": agent.name,
            "status": "success",
            "latency_ms": latency,
            "result": data
        }

    except Exception as e:
        # Agent call failed
        return {
            "agent_id": agent.agent_id,
            "agent_name": agent.name,
            "status": "error",
            "error": str(e),
            "latency_ms": 0.0
        }


# ============================================
# ORCHESTRATION ENDPOINT
# ============================================

@router.post("/orchestrate", response_model=OrchestrateResponse)
async def orchestrate(
    request: OrchestrateRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    session: Session = Depends(get_session)
):
    """
    Orchestrate a client query across registered agents.

    Process:
    1. Discover agents matching skill tags
    2. Rank agents using proprietary algorithm
    3. Call top N agents in parallel using A2A protocol
    4. Aggregate results
    5. Return to client
    """
    start_time = time.time()

    # Step 1: Discover agents
    query_db = select(RegisteredAgent).where(RegisteredAgent.is_active == True)
    all_agents = session.exec(query_db).all()

    # Filter by skill tags if provided
    if request.skill_tags:
        matching_agents = [
            a for a in all_agents
            if any(tag in a.skills_tags for tag in request.skill_tags)
        ]
    else:
        matching_agents = all_agents

    if not matching_agents:
        raise HTTPException(
            status_code=404,
            detail="No agents found matching criteria"
        )

    # Step 2: Rank agents
    ranked_agents = rank_agents(
        matching_agents,
        request.query,
        request.skill_tags
    )

    # Step 3: Select top N agents
    selected_agents = ranked_agents[:request.max_agents]

    # Prefer specific agents if requested
    if request.prefer_agent_ids:
        preferred = [
            a for a in matching_agents
            if a.agent_id in request.prefer_agent_ids
        ]
        selected_agents = preferred + [
            a for a in selected_agents if a not in preferred
        ]
        selected_agents = selected_agents[:request.max_agents]

    # Step 4: Call agents in parallel using simple HTTP
    tasks = [
        call_agent_http(agent, request.query)
        for agent in selected_agents
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle exceptions
    formatted_results = []
    for result in results:
        if isinstance(result, Exception):
            formatted_results.append({
                "status": "error",
                "error": str(result)
            })
        else:
            formatted_results.append(result)

    # Step 5: Update agent metrics
    for agent, result in zip(selected_agents, formatted_results):
        if isinstance(result, dict):
            agent.total_calls += 1

            # Update success rate (exponential moving average)
            success = 1.0 if result.get("status") == "success" else 0.0
            agent.success_rate = (agent.success_rate * 0.9) + (success * 0.1)

            # Update avg latency
            if result.get("latency_ms", 0) > 0:
                agent.avg_latency_ms = (agent.avg_latency_ms * 0.9) + (result["latency_ms"] * 0.1)

    session.commit()

    # Calculate total latency
    total_latency = (time.time() - start_time) * 1000

    # Step 6: Log orchestration
    log = OrchestrationLog(
        client_query={"query": request.query, "skill_tags": request.skill_tags},
        skill_filter=",".join(request.skill_tags) if request.skill_tags else None,
        selected_agents=[a.agent_id for a in selected_agents],
        results={"results": formatted_results},
        success=all(r.get("status") == "success" for r in formatted_results),
        latency_ms=total_latency
    )
    session.add(log)
    session.commit()

    # Step 7: Return response
    return OrchestrateResponse(
        query=request.query,
        selected_agents=[
            {
                "agent_id": a.agent_id,
                "name": a.name,
                "url": a.url,
                "skills": [skill["name"] for skill in a.agent_card.get("skills", [])]
            }
            for a in selected_agents
        ],
        results=formatted_results,
        summary=_generate_summary(request.query, formatted_results),
        latency_ms=total_latency
    )


def _generate_summary(query: str, results: List[Dict[str, Any]]) -> str:
    """
    Generate a simple text summary of orchestration results.

    TODO: Use LLM to generate intelligent summary
    """
    successful = [r for r in results if r.get("status") == "success"]

    if not successful:
        return "No agents successfully responded to your query."

    summary_parts = [f"Query: {query}\n"]
    summary_parts.append(f"Agents responded: {len(successful)}/{len(results)}\n")

    for result in successful:
        agent_name = result.get("agent_name", "Unknown")
        summary_parts.append(f"\n{agent_name}:")

        artifacts = result.get("artifacts", [])
        for artifact in artifacts:
            if artifact.get("type") == "text":
                summary_parts.append(f"  {artifact.get('content', '')}")

    return "\n".join(summary_parts)
