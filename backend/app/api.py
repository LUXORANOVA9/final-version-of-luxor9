"""LUXOR9 - API Routes"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import json
import asyncio

from app.config import get_settings
from app.database import get_db, init_db
from app.orchestrator import orchestrator, get_orchestrator
from app.models import Agent, Stream, Category
from app.agents import AgentFactory

router = APIRouter()
settings = get_settings()


# ─── HEALTH & SYSTEM ─────────────────────────────────────────

@router.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": "2025-01-15T10:30:00.000Z",
        "version": "3.0.0"
    }


@router.post("/boot")
async def boot_system():
    """Boot the entire Luxor9 system"""
    if orchestrator.is_running:
        return {"status": "already_running", "message": "System is already running"}

    await orchestrator.boot()
    return {"status": "booted", "message": "All agents initialized"}


@router.post("/shutdown")
async def shutdown_system():
    """Shutdown the Luxor9 system"""
    if not orchestrator.is_running:
        return {"status": "not_running", "message": "System is not running"}

    await orchestrator.shutdown()
    return {"status": "shutdown", "message": "System shutdown complete"}


# ─── AGENTS ─────────────────────────────────────────────────

@router.get("/api/agents")
async def list_agents():
    """List all agents"""
    if not orchestrator.is_running:
        return {"agents": [], "count": 0}

    agents = []
    for agent in orchestrator.agents.values():
        agents.append(agent.to_dict())

    return {"agents": agents, "count": len(agents)}


@router.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent details"""
    agent = orchestrator.agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent.to_dict()


@router.get("/api/agents/{agent_id}/metrics")
async def get_agent_metrics(agent_id: str):
    """Get agent real-time metrics"""
    agent = orchestrator.agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return {
        "agent_id": agent_id,
        "metrics": agent.metrics.__dict__,
        "success_rate": agent.success_rate,
        "memory_size": len(agent.memory)
    }


@router.post("/api/agents/{agent_id}/start")
async def start_agent(agent_id: str):
    """Start an agent"""
    agent = orchestrator.agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Would start the agent
    return {"status": "started", "agent_id": agent_id}


@router.post("/api/agents/{agent_id}/stop")
async def stop_agent(agent_id: str):
    """Stop an agent"""
    agent = orchestrator.agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Would stop the agent
    return {"status": "stopped", "agent_id": agent_id}


# ─── STREAMS ─────────────────────────────────────────────────

@router.get("/api/streams")
async def list_streams(category_id: Optional[int] = None):
    """List all streams"""
    return {
        "streams": [],
        "count": 0,
        "category_id": category_id
    }


@router.get("/api/streams/{stream_id}")
async def get_stream(stream_id: int):
    """Get stream details"""
    return {
        "id": stream_id,
        "status": "idle",
        "revenue_today": 0.0,
        "health_score": 100.0
    }


@router.post("/api/streams/{stream_id}/deploy")
async def deploy_stream(stream_id: int):
    """Deploy a stream"""
    if stream_id < 1 or stream_id > 100:
        raise HTTPException(status_code=400, detail="Stream ID must be 1-100")

    await orchestrator.deploy_stream(stream_id)
    return {"status": "deployed", "stream_id": stream_id}


@router.post("/api/streams/{stream_id}/stop")
async def stop_stream(stream_id: int):
    """Stop a stream"""
    if stream_id < 1 or stream_id > 100:
        raise HTTPException(status_code=400, detail="Stream ID must be 1-100")

    await orchestrator.stop_stream(stream_id)
    return {"status": "stopped", "stream_id": stream_id}


# ─── HIERARCHY ─────────────────────────────────────────────

@router.get("/api/hierarchy")
async def get_hierarchy():
    """Get full hierarchy tree"""
    if not orchestrator.is_running:
        return {"hierarchy": {}}

    return {"hierarchy": orchestrator.agent_factory.get_hierarchy_tree()}


# ─── METRICS & ANALYTICS ─────────────────────────────────

@router.get("/api/metrics")
async def get_metrics():
    """Get real-time system metrics"""
    if not orchestrator.is_running:
        return {
            "total_agents": 0,
            "active_agents": 0,
            "total_revenue": 0.0,
            "total_tasks": 0
        }

    return orchestrator._collect_metrics()


@router.get("/api/metrics/revenue")
async def get_revenue_metrics():
    """Get revenue metrics"""
    return {
        "daily_total": 0.0,
        "monthly_total": 0.0,
        "yearly_projection": 0.0,
        "by_category": {}
    }


@router.get("/api/metrics/agents")
async def get_agent_metrics_summary():
    """Get agent metrics summary"""
    if not orchestrator.is_running:
        return {"by_tier": {}, "by_status": {}}

    return {
        "by_tier": orchestrator._count_by_tier(),
        "by_status": orchestrator._count_by_status()
    }


# ─── CATEGORIES ───────────────────────────────────────────

@router.get("/api/categories")
async def list_categories():
    """List all categories"""
    return {
        "categories": list(AgentFactory.CATEGORIES.values()),
        "count": len(AgentFactory.CATEGORIES)
    }


# ─── WEBSOCKET ───────────────────────────────────────────

@router.websocket("/ws")
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
                    "timestamp": metrics["timestamp"],
                    "data": metrics
                })

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass
