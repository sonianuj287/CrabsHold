from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from app.api.proxy import router as proxy_router  # noqa: E402
from app.api.dashboard import router as dashboard_router  # noqa: E402

app = FastAPI(title="CrabsHold API", description="Governance Layer Between AI Agents and Enterprise Systems")

app.include_router(proxy_router)
app.include_router(dashboard_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to CrabsHold API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
