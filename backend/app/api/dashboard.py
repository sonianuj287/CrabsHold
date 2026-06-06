from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_db
from app.models.governance import AuditLog, ApprovalRequest

router = APIRouter(prefix="/v1/dashboard", tags=["Dashboard"])

@router.get("/logs")
async def get_audit_logs(db: AsyncSession = Depends(get_db)):
    """Fetch recent audit logs for the dashboard."""
    result = await db.execute(select(AuditLog).order_by(AuditLog.id.desc()).limit(50))
    logs = result.scalars().all()
    return logs

@router.get("/approvals")
async def get_pending_approvals(db: AsyncSession = Depends(get_db)):
    """Fetch pending approval requests."""
    result = await db.execute(select(ApprovalRequest).filter(ApprovalRequest.status == "pending").order_by(ApprovalRequest.id.desc()))
    approvals = result.scalars().all()
    return approvals
