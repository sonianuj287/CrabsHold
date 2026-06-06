from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ToolCallRequest(BaseModel):
    action: str = Field(description="The action or tool the agent wants to execute")
    tool_name: str = Field(description="The specific underlying tool being called")
    parameters: Optional[Dict[str, Any]] = None
    estimated_cost: Optional[int] = Field(default=0, description="Estimated token cost of this operation")

class ExecutionResponse(BaseModel):
    status: str # 'allowed', 'blocked', 'suspended'
    reason: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class ApprovalStatusUpdate(BaseModel):
    status: str # 'approved', 'rejected'

