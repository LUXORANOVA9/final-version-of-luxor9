"""LUXOR9 - System Tools for LangChain Agents

Each tool wraps an internal LUXOR9 operation so that LangChain agents
can invoke them during their think() cycle.
"""
import json
from typing import Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


# ─── Schema Models ──────────────────────────────────────────

class StreamIdInput(BaseModel):
    stream_id: int = Field(description="Stream ID (1-100)")

class AgentIdInput(BaseModel):
    agent_id: str = Field(description="Target agent ID, e.g. 'FORGE' or 'CORTEX'")

class AssignTaskInput(BaseModel):
    worker_id: str = Field(description="Worker agent ID to assign the task to")
    task_type: str = Field(description="Type of task: scout, mail, social, sales, build, write, chat, data, test, growth")
    description: str = Field(description="Brief description of what to do")

class MessageInput(BaseModel):
    to_agent_id: str = Field(description="Recipient agent ID")
    message_type: str = Field(description="One of: report, directive, alert, escalation")
    content: str = Field(description="Message content")

class RevenueInput(BaseModel):
    stream_id: int = Field(description="Stream that generated revenue")
    amount: float = Field(description="Revenue amount in USD")
    source: str = Field(description="Revenue source description")

class SearchInput(BaseModel):
    query: str = Field(description="Search query")

class EmailInput(BaseModel):
    to: str = Field(description="Recipient email address")
    subject: str = Field(description="Email subject line")
    body: str = Field(description="Email body text")

class ContentInput(BaseModel):
    topic: str = Field(description="Content topic or brief")
    content_type: str = Field(description="Type: blog_post, social_post, landing_page, email_copy, ad_copy")
    tone: str = Field(default="professional", description="Tone: professional, casual, persuasive, technical")


# ─── Tools ──────────────────────────────────────────────────

class QueryStreamMetricsTool(BaseTool):
    name: str = "query_stream_metrics"
    description: str = "Get revenue, health score, and status for a specific income stream (1-100). Returns stream metrics as JSON."
    args_schema: type[BaseModel] = StreamIdInput

    def _run(self, stream_id: int) -> str:
        from app.database import SessionLocal, Stream
        db = SessionLocal()
        try:
            stream = db.query(Stream).filter(Stream.id == stream_id).first()
            if not stream:
                return json.dumps({"error": f"Stream {stream_id} not found"})
            return json.dumps({
                "stream_id": stream.id,
                "title": stream.title,
                "status": stream.status,
                "revenue_today": stream.revenue_today,
                "revenue_total": stream.revenue_total,
                "customers": stream.customers,
                "health_score": stream.health_score,
            })
        finally:
            db.close()


class QueryAgentStatusTool(BaseTool):
    name: str = "query_agent_status"
    description: str = "Get the current status, metrics, and tier of a specific agent in the hierarchy."
    args_schema: type[BaseModel] = AgentIdInput

    def _run(self, agent_id: str) -> str:
        from app.orchestrator import orchestrator
        agent = orchestrator.agents.get(agent_id)
        if not agent:
            return json.dumps({"error": f"Agent {agent_id} not found"})
        return json.dumps(agent.to_dict())


class DeployStreamTool(BaseTool):
    name: str = "deploy_stream"
    description: str = "Deploy/activate an income stream so it starts generating revenue. Stream ID must be 1-100."
    args_schema: type[BaseModel] = StreamIdInput

    def _run(self, stream_id: int) -> str:
        from app.database import SessionLocal, Stream
        db = SessionLocal()
        try:
            stream = db.query(Stream).filter(Stream.id == stream_id).first()
            if not stream:
                return json.dumps({"error": f"Stream {stream_id} not found"})
            stream.status = "active"
            db.commit()
            return json.dumps({"status": "deployed", "stream_id": stream_id})
        finally:
            db.close()


class StopStreamTool(BaseTool):
    name: str = "stop_stream"
    description: str = "Stop/deactivate an income stream. Stream ID must be 1-100."
    args_schema: type[BaseModel] = StreamIdInput

    def _run(self, stream_id: int) -> str:
        from app.database import SessionLocal, Stream
        db = SessionLocal()
        try:
            stream = db.query(Stream).filter(Stream.id == stream_id).first()
            if not stream:
                return json.dumps({"error": f"Stream {stream_id} not found"})
            stream.status = "idle"
            db.commit()
            return json.dumps({"status": "stopped", "stream_id": stream_id})
        finally:
            db.close()


class AssignTaskTool(BaseTool):
    name: str = "assign_task"
    description: str = "Assign a task to a worker agent. Specify worker ID, task type, and description."
    args_schema: type[BaseModel] = AssignTaskInput

    def _run(self, worker_id: str, task_type: str, description: str) -> str:
        from app.orchestrator import orchestrator
        worker = orchestrator.agents.get(worker_id)
        if not worker:
            return json.dumps({"error": f"Worker {worker_id} not found"})
        # Put task in worker's inbox
        import uuid
        task = {
            "id": str(uuid.uuid4())[:8],
            "type": task_type,
            "description": description,
            "status": "assigned",
        }
        worker.inbox.append({
            "type": "directive",
            "payload": {"action": "execute_task", "task": task}
        })
        return json.dumps({"status": "assigned", "task_id": task["id"], "worker": worker_id})


class SendAgentMessageTool(BaseTool):
    name: str = "send_agent_message"
    description: str = "Send a message to another agent in the hierarchy. Used for reports, directives, alerts, or escalations."
    args_schema: type[BaseModel] = MessageInput

    def _run(self, to_agent_id: str, message_type: str, content: str) -> str:
        from app.orchestrator import orchestrator
        target = orchestrator.agents.get(to_agent_id)
        if not target:
            return json.dumps({"error": f"Agent {to_agent_id} not found"})
        import uuid
        from datetime import datetime
        msg = {
            "msg_id": str(uuid.uuid4())[:8],
            "type": message_type,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }
        target.inbox.append(msg)
        return json.dumps({"status": "sent", "to": to_agent_id, "msg_id": msg["msg_id"]})


class LogRevenueTool(BaseTool):
    name: str = "log_revenue"
    description: str = "Log revenue generated from a stream. Records the amount and source."
    args_schema: type[BaseModel] = RevenueInput

    def _run(self, stream_id: int, amount: float, source: str) -> str:
        from app.database import SessionLocal, Stream
        db = SessionLocal()
        try:
            stream = db.query(Stream).filter(Stream.id == stream_id).first()
            if stream:
                stream.revenue_today += amount
                stream.revenue_total += amount
                db.commit()
            return json.dumps({
                "status": "logged",
                "stream_id": stream_id,
                "amount": amount,
                "source": source,
            })
        finally:
            db.close()


class SearchWebTool(BaseTool):
    name: str = "search_web"
    description: str = "Search the web for leads, market info, or research. Returns simulated search results."
    args_schema: type[BaseModel] = SearchInput

    def _run(self, query: str) -> str:
        # In production: integrate with SerpAPI, Tavily, etc.
        return json.dumps({
            "query": query,
            "results": [
                {"title": f"Result for: {query}", "snippet": "Simulated search result. Connect a real search API for production use.", "url": "https://example.com"},
            ],
            "note": "Connect SerpAPI or Tavily for real results"
        })


class SendEmailTool(BaseTool):
    name: str = "send_email"
    description: str = "Send an email to a prospect or customer. In development mode, emails are logged but not sent."
    args_schema: type[BaseModel] = EmailInput

    def _run(self, to: str, subject: str, body: str) -> str:
        # In production: integrate with Resend, SendGrid, etc.
        return json.dumps({
            "status": "logged",
            "to": to,
            "subject": subject,
            "note": "Development mode — email logged, not sent. Connect Resend/SendGrid for production."
        })


class GenerateContentTool(BaseTool):
    name: str = "generate_content"
    description: str = "Generate marketing content, blog posts, social posts, or ad copy."
    args_schema: type[BaseModel] = ContentInput

    def _run(self, topic: str, content_type: str, tone: str = "professional") -> str:
        # The LLM itself will generate content; this tool just structures the request
        return json.dumps({
            "status": "generated",
            "topic": topic,
            "content_type": content_type,
            "tone": tone,
            "content": f"[Generated {content_type} about '{topic}' in {tone} tone. In production, the agent LLM generates real content.]",
        })
