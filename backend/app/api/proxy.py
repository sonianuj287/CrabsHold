from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_db
from app.schemas.agent import ToolCallRequest, ExecutionResponse, ApprovalStatusUpdate
from app.services.policy_engine import evaluate_policy
from app.services.audit import record_audit_log
from app.models.governance import ApprovalRequest, WorkflowCheckpoint
from app.models.identity import Agent

from app.api.auth import get_current_agent

router = APIRouter(prefix="/v1/proxy", tags=["Proxy"])

@router.post("/execute", response_model=ExecutionResponse)
async def proxy_execute(
    request: ToolCallRequest,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db)
):
    """
    The Identity-Aware Agent Gateway.
    Receives a tool call request from an agent, evaluates policies, and decides whether to allow it.
    """
    
    # Save a WorkflowCheckpoint
    checkpoint = WorkflowCheckpoint(
        agent_id=agent.id,
        workflow_run_id=request.workflow_run_id,
        tool_name=request.tool_name,
        parameters=request.parameters,
        agent_state=request.agent_state
    )
    db.add(checkpoint)
    await db.commit()
    
    status, reason = await evaluate_policy(
        db=db,
        agent_id=agent.id,
        action=request.action,
        tool_name=request.tool_name,
        parameters=request.parameters,
        estimated_cost=request.estimated_cost or 0
    )

    # Record the audit log for immutable traceability
    await record_audit_log(
        db=db,
        agent_id=agent.id,
        action=request.action,
        tool_name=request.tool_name,
        status=status,
        parameters=request.parameters,
        reason=reason,
        cost=request.estimated_cost or 0
    )

    if status == "blocked":
        raise HTTPException(status_code=403, detail={"status": status, "reason": reason})
    
    if status == "suspended":
        # Create an approval request
        approval_req = ApprovalRequest(
            agent_id=agent.id,
            action=request.action,
            tool_name=request.tool_name,
            parameters=request.parameters
        )
        db.add(approval_req)
        await db.commit()
        await db.refresh(approval_req)

        return ExecutionResponse(
            status=status, 
            reason=reason or "Waiting for human approval",
            data={"workflow_id": approval_req.id}
        )

    # If allowed, this is where we would forward the request to the actual tool/API
    mock_data = {"result": f"Successfully executed tool {request.tool_name}", "mock": True}
    return ExecutionResponse(status=status, reason=reason, data=mock_data)

@router.post("/approval/{request_id}", response_model=dict)
async def proxy_approval(
    request_id: int,
    update: ApprovalStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint for a human to approve or reject a suspended tool call.
    """
    result = await db.execute(select(ApprovalRequest).filter(ApprovalRequest.id == request_id))
    approval_req = result.scalars().first()

    if not approval_req:
        raise HTTPException(status_code=404, detail="Approval request not found")
    
    if approval_req.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request already processed: {approval_req.status}")

    approval_req.status = update.status
    
    # If approved, boost trust score slightly
    if update.status == "approved":
        agent_res = await db.execute(select(Agent).filter(Agent.id == approval_req.agent_id))
        agent = agent_res.scalars().first()
        if agent:
            # Cap at 100
            agent.trust_score = min(100, agent.trust_score + 1)
            db.add(agent)

    await db.commit()

    return {"message": f"Request {request_id} has been {update.status}"}

@router.get("/workflows", response_model=list[str])
async def list_workflows(db: AsyncSession = Depends(get_db)):
    """List unique workflow runs."""
    result = await db.execute(select(WorkflowCheckpoint.workflow_run_id).distinct())
    return [row[0] for row in result.all()]

@router.get("/workflows/{workflow_run_id}/checkpoints", response_model=list[dict])
async def get_checkpoints(workflow_run_id: str, db: AsyncSession = Depends(get_db)):
    """Get chronological timeline of checkpoints for a specific run."""
    result = await db.execute(
        select(WorkflowCheckpoint)
        .filter(WorkflowCheckpoint.workflow_run_id == workflow_run_id)
        .order_by(WorkflowCheckpoint.created_at.asc())
    )
    checkpoints = result.scalars().all()
    return [
        {
            "id": cp.id,
            "agent_id": cp.agent_id,
            "tool_name": cp.tool_name,
            "parameters": cp.parameters,
            "agent_state": cp.agent_state,
            "created_at": cp.created_at.isoformat()
        } for cp in checkpoints
    ]

