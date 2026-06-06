import asyncio
from sqlalchemy.future import select
from app.db.database import AsyncSessionLocal
from app.models.identity import Agent

async def lower_trust():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Agent).filter(Agent.id == 1))
        agent = result.scalars().first()
        if agent:
            print(f"Current trust score: {agent.trust_score}")
            agent.trust_score = 40
            await db.commit()
            print(f"Lowered trust score to: {agent.trust_score}")

if __name__ == "__main__":
    asyncio.run(lower_trust())
