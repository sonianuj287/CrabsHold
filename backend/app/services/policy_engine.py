from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Tuple, Optional, Dict, Any
from app.models.identity import Agent
from app.models.governance import Policy
from app.services.security_scanner import scan_payload_for_injection

async def evaluate_policy(
    db: AsyncSession,
    agent_id: int,
    action: str,
    tool_name: str,
    parameters: Optional[Dict[str, Any]],
    estimated_cost: int
) -> Tuple[str, Optional[str]]:
    """
    Evaluates whether an agent is allowed to perform an action.
    Returns a tuple of (status, reason).
    Status can be: 'allowed', 'blocked', 'suspended'
    """
    # 1. Fetch Agent
    result = await db.execute(select(Agent).filter(Agent.id == agent_id))
    agent = result.scalars().first()

    if not agent:
        return "blocked", "Agent not found"
    
    if not agent.is_active:
        return "blocked", "Agent is deactivated"

    # 2. Check Cost limits
    if agent.token_cost_limit is not None and estimated_cost > agent.token_cost_limit:
         agent.trust_score -= 5
         db.add(agent)
         await db.commit()
         return "blocked", f"Action cost {estimated_cost} exceeds limit {agent.token_cost_limit}"

    # 3. Fetch Policy
    result = await db.execute(select(Policy).filter(Policy.action == action))
    policy = result.scalars().first()

    if not policy:
        result = await db.execute(select(Policy).filter(Policy.action == "*"))
        policy = result.scalars().first()

    if not policy:
        return "blocked", f"No policy defined for action '{action}'"
    
    if not policy.is_active:
         return "blocked", f"Policy for action '{action}' is inactive"

    if policy.max_token_cost is not None and estimated_cost > policy.max_token_cost:
         agent.trust_score -= 5
         db.add(agent)
         await db.commit()
         return "blocked", f"Exceeds max token cost {policy.max_token_cost} for action '{action}'"

    # 4. Semantic Governance / Prompt Injection Scan
    is_malicious, malicious_reason = await scan_payload_for_injection(tool_name, parameters or {})
    if is_malicious:
        agent.trust_score -= 20
        db.add(agent)
        await db.commit()
        return "blocked", f"Prompt Injection Detected: {malicious_reason}"

    # 5. Adaptive Autonomy: Check Trust Score (Strict Mode)
    requires_approval = policy.requires_approval
    if agent.trust_score < 50:
         requires_approval = True # Override to force human approval for untrusted agents

    # 6. Check Human Approval
    if requires_approval:
         return "suspended", "Human approval required"

    return "allowed", None

