"""LUXOR9 - CEO Agent API Routes"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import json
from datetime import datetime

from app.agents.ceo_agent import get_ceo_agent
from app.ceo_memory import get_ceo_memory
from app.config import get_settings

# Router
ceo_router = APIRouter(prefix="/api/ceo", tags=["ceo"])


# ─── Request Models ─────────────────────────────────────────

class CommandRequest(BaseModel):
    command: str
    include_history: bool = True


class FeedbackRequest(BaseModel):
    task_id: str
    rating: int  # 1-5
    feedback: Optional[str] = None


class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str = "medium"
    due_date: Optional[str] = None


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None


# ─── CEO Command Endpoints ───────────────────────────────────

@ceo_router.post("/command")
async def send_command(request: CommandRequest):
    """Send a command to the CEO Agent"""
    ceo = get_ceo_agent()
    memory = get_ceo_memory()

    # Add to conversation history
    memory.add_conversation("human", request.command)

    # Execute command
    result = await ceo.receive_command(request.command)

    # Store AI response in history
    ai_response = result.get("result", {}).get("raw_response", str(result))
    memory.add_conversation("ai", ai_response)

    return {
        "task_id": result.get("task_id"),
        "status": result.get("status"),
        "response": result.get("result"),
        "timestamp": datetime.utcnow().isoformat()
    }


@ceo_router.get("/status")
async def get_ceo_status():
    """Get CEO Agent status"""
    ceo = get_ceo_agent()
    return ceo.to_dict()


@ceo_router.get("/suggestions")
async def get_suggestions():
    """Get proactive suggestions from CEO Agent"""
    ceo = get_ceo_agent()
    return {
        "suggestions": ceo.suggestions,
        "alerts": ceo.alerts,
        "opportunities": ceo.opportunities,
        "last_update": datetime.utcnow().isoformat()
    }


@ceo_router.get("/history")
async def get_conversation_history(limit: int = 20):
    """Get conversation history with CEO Agent"""
    memory = get_ceo_memory()
    return {
        "conversations": memory.get_conversations(limit),
        "total": len(memory.data["conversations"])
    }


@ceo_router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback on CEO Agent response"""
    memory = get_ceo_memory()

    # Store feedback
    memory.add_insight(
        f"Task {request.task_id} rated {request.rating}/5: {request.feedback}",
        "feedback"
    )

    return {"status": "saved", "task_id": request.task_id}


# ─── CEO Task Endpoints ───────────────────────────────────────

@ceo_router.get("/tasks")
async def get_tasks(status: Optional[str] = None):
    """Get CEO tasks"""
    memory = get_ceo_memory()
    return {"tasks": memory.get_tasks(status)}


@ceo_router.post("/tasks")
async def create_task(task: TaskCreate):
    """Create a new CEO task"""
    import uuid
    memory = get_ceo_memory()

    new_task = {
        "id": str(uuid.uuid4())[:8],
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "due_date": task.due_date,
        "status": "pending"
    }

    memory.add_task(new_task)

    return {"task": new_task, "status": "created"}


@ceo_router.patch("/tasks/{task_id}")
async def update_task(task_id: str, updates: TaskUpdate):
    """Update a task"""
    memory = get_ceo_memory()
    update_dict = updates.model_dump(exclude_unset=True)
    memory.update_task(task_id, update_dict)
    return {"status": "updated", "task_id": task_id}


# ─── WebSocket for Real-time Updates ─────────────────────────

@ceo_router.websocket("/ws")
async def ceo_websocket(websocket: WebSocket):
    """WebSocket for real-time CEO Agent communication"""
    await websocket.accept()

    ceo = get_ceo_agent()
    memory = get_ceo_memory()

    try:
        while True:
            # Wait for commands
            data = await websocket.receive_text()
            message = json.loads(data)

            command = message.get("command")
            if command:
                # Execute command
                result = await ceo.receive_command(command)

                # Store in history
                memory.add_conversation("human", command)
                memory.add_conversation("ai", str(result.get("result", {})))

                # Send response
                await websocket.send_json({
                    "type": "response",
                    "task_id": result.get("task_id"),
                    "result": result.get("result"),
                    "timestamp": datetime.utcnow().isoformat()
                })

            # Send periodic suggestions/alerts
            suggestions = ceo.suggestions
            alerts = ceo.alerts

            if suggestions or alerts:
                await websocket.send_json({
                    "type": "update",
                    "suggestions": suggestions,
                    "alerts": alerts,
                    "timestamp": datetime.utcnow().isoformat()
                })

    except WebSocketDisconnect:
        pass