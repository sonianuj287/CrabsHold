import hashlib
from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.models.identity import Agent

API_KEY_NAME = "Authorization"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key_hash(api_key: str) -> str:
    """Hash the API key using SHA-256."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()

async def get_current_agent(
    api_key_header: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db)
) -> Agent:
    """
    FastAPI dependency to extract Bearer token, hash it, 
    and identify the Agent.
    """
    if not api_key_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    # Support "Bearer <token>" or just "<token>"
    api_key = api_key_header.replace("Bearer ", "").strip()
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    key_hash = get_api_key_hash(api_key)

    result = await db.execute(select(Agent).filter(Agent.hashed_api_key == key_hash))
    agent = result.scalars().first()

    if not agent:
        raise HTTPException(status_code=401, detail="Invalid API Key or Agent not found")
    
    if not agent.is_active:
        raise HTTPException(status_code=403, detail="Agent is deactivated")

    return agent
