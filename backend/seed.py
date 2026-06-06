import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.models.identity import User, Agent
from app.models.governance import Policy

async def seed():
    async with AsyncSessionLocal() as session:
        # Create user
        user = User(username="admin", email="admin@crabshold.com")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Create agent
        agent = Agent(name="CustomerSupportAgent", description="Handles customer requests", token_cost_limit=5000, owner_id=user.id)
        session.add(agent)
        await session.commit()
        await session.refresh(agent)

        # Create policies
        p1 = Policy(name="Read customer data", action="customer_read", requires_approval=False, max_token_cost=100)
        p2 = Policy(name="Delete customer", action="customer_delete", requires_approval=True)
        p3 = Policy(name="Expensive action", action="expensive_action", requires_approval=False, max_token_cost=500)
        
        session.add_all([p1, p2, p3])
        await session.commit()
        
        print(f"Seed complete. Agent ID: {agent.id}")

if __name__ == "__main__":
    asyncio.run(seed())
