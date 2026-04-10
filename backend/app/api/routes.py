"""LUXOR9 - API Routes"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
from datetime import datetime

from app.config import get_settings
from app.database import get_sync_db
from app.agents.base_agent import AgentStatus
from app.orchestrator import orchestrator, get_orchestrator

try:
    from app.database.models import Agent, Stream, Category
except ImportError:
    from app.models import Agent, Stream, Category

# Pydantic models
class AgentCreate(BaseModel):
    agent_id: str
    name: str
    tier: int
    role: str
    model: str = "gpt-4o-mini"
    parent_agent_id: Optional[str] = None

class AgentUpdate(BaseModel):
    status: Optional[str] = None
    config: Optional[Dict] = None

class StreamCreate(BaseModel):
    title: str
    category_id: int

class StreamUpdate(BaseModel):
    status: Optional[str] = None
    config: Optional[Dict] = None

class CommandRequest(BaseModel):
    command: str
    target: str = "LUXOR-PRIME"

class DirectiveRequest(BaseModel):
    to_agent_id: str
    directive: Dict


# Create routers
agents_router = APIRouter(prefix="/api/agents", tags=["agents"])
streams_router = APIRouter(prefix="/api/streams", tags=["streams"])
categories_router = APIRouter(prefix="/api/categories", tags=["categories"])
system_router = APIRouter(prefix="/api/system", tags=["system"])
metrics_router = APIRouter(prefix="/api/metrics", tags=["metrics"])


# ─── CATEGORIES ROUTES ───────────────────────────────────────

@categories_router.get("")
async def list_categories(db: Session = Depends(get_sync_db)):
    """List all categories"""
    categories = db.query(Category).all()
    return [{"id": c.id, "name": c.name, "color": c.color, "vp_name": c.vp_name} for c in categories]


# ─── AGENT ROUTES ─────────────────────────────────────────────

@agents_router.get("")
async def list_agents(db: Session = Depends(get_sync_db)):
    """List all agents"""
    agents = db.query(Agent).all()
    return [{"id": str(a.id), "name": a.name, "tier": a.tier, "role": a.role, "status": a.status, 
             "tasks_completed": a.tasks_completed, "tasks_failed": a.tasks_failed, 
             "success_rate": float(a.success_rate), "revenue_generated": float(a.revenue_generated)} for a in agents]


@agents_router.get("/{agent_id}")
async def get_agent(agent_id: str, db: Session = Depends(get_sync_db)):
    """Get agent by ID"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@agents_router.patch("/{agent_id}")
async def update_agent(
    agent_id: str,
    update: AgentUpdate,
    db: Session = Depends(get_sync_db)
):
    """Update agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if update.status:
        agent.status = update.status
    if update.config:
        agent.config = update.config

    db.commit()
    return agent


@agents_router.get("/{agent_id}/metrics")
async def get_agent_metrics(agent_id: str):
    """Get real-time agent metrics"""
    agent = orchestrator.agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent.to_dict()


@agents_router.post("/{agent_id}/start")
async def start_agent(agent_id: str):
    """Start an agent"""
    agent = orchestrator.agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent.status = AgentStatus.ACTIVE
    return {"status": "started", "agent_id": agent_id}


@agents_router.post("/{agent_id}/stop")
async def stop_agent(agent_id: str):
    """Stop an agent"""
    agent = orchestrator.agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent.status = AgentStatus.IDLE
    return {"status": "stopped", "agent_id": agent_id}


# ─── STREAM ROUTES ────────────────────────────────────────────

@streams_router.get("")
async def list_streams(db: Session = Depends(get_sync_db)):
    """List all streams"""
    streams = db.query(Stream).all()
    return [{"id": s.id, "title": s.title, "category_id": s.category_id, "status": s.status,
             "revenue_today": float(s.revenue_today), "revenue_total": float(s.revenue_total)} for s in streams]


@streams_router.get("/{stream_id}")
async def get_stream(stream_id: int, db: Session = Depends(get_sync_db)):
    """Get stream by ID"""
    stream = db.query(Stream).filter(Stream.id == stream_id).first()
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")
    return stream


@streams_router.post("")
async def create_stream(stream: StreamCreate, db: Session = Depends(get_sync_db)):
    """Create a new stream"""
    new_stream = Stream(
        title=stream.title,
        category_id=stream.category_id,
        status="idle"
    )
    db.add(new_stream)
    db.commit()
    db.refresh(new_stream)
    return new_stream


@streams_router.post("/{stream_id}/deploy")
async def deploy_stream(stream_id: int, db: Session = Depends(get_sync_db)):
    """Deploy a stream"""
    stream = db.query(Stream).filter(Stream.id == stream_id).first()
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    stream.status = "deploying"
    db.commit()

    # Trigger deployment logic
    await orchestrator.deploy_stream(stream_id)

    stream.status = "active"
    db.commit()

    return {"status": "deployed", "stream_id": stream_id}


@streams_router.post("/{stream_id}/stop")
async def stop_stream(stream_id: int, db: Session = Depends(get_sync_db)):
    """Stop a stream"""
    stream = db.query(Stream).filter(Stream.id == stream_id).first()
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    stream.status = "idle"
    db.commit()

    return {"status": "stopped", "stream_id": stream_id}


# ─── SYSTEM ROUTES ────────────────────────────────────────────

@system_router.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": str(datetime.utcnow()),
        "agents": len(orchestrator.agents),
        "running": orchestrator.is_running
    }


@system_router.get("/stats")
async def get_stats(db: Session = Depends(get_sync_db)):
    """Get system stats for dashboard"""
    from sqlalchemy import func
    
    total_agents = db.query(func.count(Agent.id)).scalar() or 0
    active_agents = db.query(func.count(Agent.id)).filter(Agent.status == "active").scalar() or 0
    total_streams = db.query(func.count(Stream.id)).scalar() or 0
    active_streams = db.query(func.count(Stream.id)).filter(Stream.status == "active").scalar() or 0
    total_revenue = db.query(func.sum(Stream.revenue_total)).scalar() or 0.0
    tasks_completed_today = db.query(func.count(Agent.tasks_completed)).scalar() or 0
    
    return {
        "total_agents": total_agents,
        "active_agents": active_agents,
        "total_streams": total_streams,
        "active_streams": active_streams,
        "total_revenue": float(total_revenue),
        "tasks_completed_today": tasks_completed_today
    }


@system_router.post("/boot")
async def boot_system():
    """Boot the entire system"""
    if orchestrator.is_running:
        return {"status": "already_running"}

    await orchestrator.boot()
    return {"status": "booted"}


@system_router.post("/shutdown")
async def shutdown_system():
    """Shutdown the entire system"""
    await orchestrator.shutdown()
    return {"status": "shutdown"}


@system_router.post("/command")
async def send_command(command: CommandRequest):
    """Send a command to an agent"""
    await orchestrator.send_command(command.command, command.target)
    return {"status": "sent", "target": command.target}


@system_router.get("/state")
async def get_system_state():
    """Get full system state"""
    return await orchestrator.get_full_state()


@system_router.get("/hierarchy")
async def get_hierarchy():
    """Get agent hierarchy tree"""
    return orchestrator.agent_factory.get_hierarchy_tree()


# ─── METRICS ROUTES ──────────────────────────────────────────

@metrics_router.get("/live")
async def get_live_metrics():
    """Get live metrics"""
    return orchestrator._collect_metrics()


@metrics_router.get("/revenue")
async def get_revenue_metrics():
    """Get revenue metrics"""
    metrics = orchestrator._collect_metrics()
    return {
        "total_revenue": metrics.get("total_revenue", 0),
        "active_agents": metrics.get("active_agents", 0),
        "total_tasks": metrics.get("total_tasks_completed", 0)
    }


# ─── WEBSOCKET ───────────────────────────────────────────────

settings = get_settings()


@system_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()

    try:
        while True:
            # Send metrics update every second
            if orchestrator.is_running:
                metrics = orchestrator._collect_metrics()
                await websocket.send_json({
                    "type": "metrics_update",
                    "data": metrics
                })

            # Also send hierarchy updates
            hierarchy = orchestrator.agent_factory.get_hierarchy_tree()
            await websocket.send_json({
                "type": "hierarchy_update",
                "data": hierarchy
            })

            import asyncio
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("Client disconnected")
