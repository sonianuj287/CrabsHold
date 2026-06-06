from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_db
from app.schemas.agent import ToolCallRequest, ExecutionResponse, ApprovalStatusUpdate
from app.services.policy_engine import evaluate_policy
from app.services.audit import record_audit_log
from app.models.governance import ApprovalRequest

router = APIRouter(prefix="/v1/proxy", tags=["Proxy"])

@router.post("/execute", response_model=ExecutionResponse)
async def proxy_execute(
    request: ToolCallRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    The Identity-Aware Agent Gateway.
    Receives a tool call request from an agent, evaluates policies, and decides whether to allow it.
    """
    
    status, reason = await evaluate_policy(
        db=db,
        agent_id=request.agent_id,
        action=request.action,
        tool_name=request.tool_name,
        parameters=request.parameters,
        estimated_cost=request.estimated_cost or 0
    )

    # Record the audit log for immutable traceability
    await record_audit_log(
        db=db,
        agent_id=request.agent_id,
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
            agent_id=request.agent_id,
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
    await db.commit()

    return {"message": f"Request {request_id} has been {update.status}"}

