from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    action = Column(String, nullable=False) # e.g., 'customer_delete', '*'
    requires_approval = Column(Boolean, default=False)
    max_token_cost = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    action = Column(String, nullable=False)
    tool_name = Column(String, nullable=False)
    parameters = Column(JSON, nullable=True)
    status = Column(String, nullable=False) # 'allowed', 'blocked', 'suspended'
    reason = Column(String, nullable=True) # Reason for block/suspend
    cost = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    agent = relationship("Agent", back_populates="audit_logs")

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    action = Column(String, nullable=False)
    tool_name = Column(String, nullable=False)
    parameters = Column(JSON, nullable=True)
    status = Column(String, default="pending") # 'pending', 'approved', 'rejected'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    agent = relationship("Agent")

class WorkflowCheckpoint(Base):
    __tablename__ = "workflow_checkpoints"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    workflow_run_id = Column(String, index=True, nullable=False)
    tool_name = Column(String, nullable=False)
    parameters = Column(JSON, nullable=True)
    agent_state = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    agent = relationship("Agent")
