from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from app.models.governance import AuditLog

async def record_audit_log(
    db: AsyncSession,
    agent_id: int,
    action: str,
    tool_name: str,
    status: str,
    parameters: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
    cost: int = 0
) -> AuditLog:
    """
    Creates an immutable audit log entry for an agent's action.
    """
    log_entry = AuditLog(
        agent_id=agent_id,
        action=action,
        tool_name=tool_name,
        parameters=parameters,
        status=status,
        reason=reason,
        cost=cost
    )
    db.add(log_entry)
    await db.commit()
    await db.refresh(log_entry)
    return log_entry
