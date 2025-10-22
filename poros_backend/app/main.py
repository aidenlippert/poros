"""
Poros Protocol - Main Application

Production-ready infrastructure for agent registration, discovery, and orchestration.

Architecture:
- Agent Registry (A2P): Agents register their AgentCards
- Orchestrator (A2A): Routes client queries to agents using A2A protocol
- A2A Compliant: Uses Google's official A2A Python SDK

Built on Google's Agent-to-Agent (A2A) protocol specification.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from .database import init_db
from .registry import router as registry_router
from .orchestrator import router as orchestrator_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Poros Protocol",
    description="""
    Production infrastructure for AI agent collaboration.

    ## Components

    ### Agent Registry (A2P - Agent-to-Platform)
    - Register agents with AgentCards (A2A protocol compliant)
    - Discover agents by skill tags
    - Manage agent lifecycle

    ### Orchestrator (A2A - Agent-to-Agent)
    - Route client queries to registered agents
    - Call agents using official A2A protocol (message/send)
    - Aggregate and return results
    - Proprietary ranking system (placeholder for ML model)

    ## Protocol

    Built on Google's **Agent-to-Agent (A2A) Protocol**:
    - AgentCard: Self-describing agent manifest
    - Skills: Capabilities agents can perform
    - message/send: Primary interaction method
    - JSON-RPC 2.0 transport

    ## For Agent Developers

    1. Register an account: `POST /api/registry/users`
    2. Get your AgentCard compliant with A2A spec
    3. Register your agent: `POST /api/registry/agents`
    4. Your agent will receive queries via A2A protocol `message/send` method

    See example agent SDK in `/agent_sdk` directory.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - Allow Vercel frontend and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://poros.vercel.app",
        "https://*.vercel.app",
        "http://localhost:*",
        "http://127.0.0.1:*",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# STARTUP / SHUTDOWN
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Poros Protocol starting up...")
    init_db()
    logger.info("Database initialized")
    logger.info("Poros Protocol ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Poros Protocol shutting down...")


# ============================================
# ROUTES
# ============================================

@app.get("/")
async def root():
    """Health check and service info"""
    return {
        "service": "Poros Protocol",
        "version": "1.0.0",
        "status": "operational",
        "description": "Agent registration, discovery, and orchestration infrastructure",
        "protocol": "A2A (Agent-to-Agent) compliant",
        "docs": "/docs",
        "components": {
            "registry": "/api/registry",
            "orchestrator": "/api/orchestrator"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-01-21T00:00:00Z"
    }


# Include routers
app.include_router(registry_router)
app.include_router(orchestrator_router)


# ============================================
# ERROR HANDLERS
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
