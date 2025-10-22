"""
Poros Protocol - Database Configuration
"""

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
import os

# Database URL - defaults to SQLite for development
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./poros_registry.db")

# Create engine
# For SQLite, use check_same_thread=False to allow FastAPI async operations
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,  # Set to True for SQL query logging
)


def init_db():
    """Initialize database tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency for getting database session"""
    with Session(engine) as session:
        yield session
