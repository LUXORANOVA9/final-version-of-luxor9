"""LUXOR9 - Base Agent Implementation"""
import asyncio
import uuid
import json
import logging
import time
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from collections import deque

from app.database import get_db
from app.config import get_settings

logger = logging.getLogger("luxor9.agents")


class AgentClass(str, Enum):
    COMMANDER = "commander"
    CSUITE = "csuite"
    VP = "vp"
    MANAGER = "manager"
    WORKER = "worker"


class AgentStatus(str, Enum):
    ACTIVE = "active"
    IDLE = "idle"
    ERROR = "error"
    TERMINATED = "terminated"


class MessageType(str, Enum):
    REPORT = "report"
    REQUEST = "request"
    DIRECTIVE = "directive"
    ALERT = "alert"
    ESCALATION = "escalation"


class Priority(str, Enum):
    P0_CRITICAL = "P0_CRITICAL"
    P1_HIGH = "P1_HIGH"
    P2_MEDIUM = "P2_MEDIUM"
    P3_LOW = "P3_LOW"


@dataclass
class AgentMetrics:
    tasks_completed: int = 0
    tasks_failed: int = 0
    success_rate: float = 100.0
    revenue_generated: float = 0.0
    tokens_used: int = 0
    messages_sent: int = 0
    messages_received: int = 0


class BaseAgent(ABC):
    """Base class for all Luxor9 AI agents with proper memory management"""

    MAX_MEMORY_SIZE = 100
    MAX_INBOX_SIZE = 50
    HEARTBEAT_INTERVAL = 60

    def __init__(
        self,
        agent_id: str,
        name: str,
        tier: int,
        role: str,
        model: str = "gpt-4o-mini",
        think_cycle_seconds: float = 30,
        authority_level: int = 5,
        parent_agent_id: Optional[str] = None,
        category_id: Optional[int] = None,
        personality: Optional[str] = None,
        agent_class: AgentClass = AgentClass.WORKER
    ):
        self.agent_id = agent_id
        self.name = name
        self.tier = tier
        self.role = role
        self.model = model
        self.think_cycle = think_cycle_seconds
        self.authority = authority_level
        self.parent_agent_id = parent_agent_id
        self.category_id = category_id
        self.personality = personality or self._default_personality()
        self.agent_class = agent_class

        self.status = AgentStatus.IDLE
        self.metrics = AgentMetrics()
        self.memory: deque = deque(maxlen=self.MAX_MEMORY_SIZE)
        self.inbox: deque = deque(maxlen=self.MAX_INBOX_SIZE)
        self.children: List[str] = []
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        self._last_heartbeat: float = 0
        self._consecutive_errors: int = 0
        self._max_consecutive_errors: int = 5

        self.settings = get_settings()

    @abstractmethod
    def _default_personality(self) -> str:
        """Return the system prompt for this agent"""
        pass

    @abstractmethod
    async def think(self):
        """Main reasoning cycle — override in each agent type"""
        pass

    async def initialize(self):
        """Initialize agent and register"""
        await self._register()
        await self._log_event("agent_initialized", {"name": self.name, "tier": self.tier})

    async def start(self):
        """Start the agent's think loop with proper cancellation support"""
        if self._running:
            logger.warning(f"[{self.agent_id}] Already running")
            return

        self.status = AgentStatus.ACTIVE
        self._running = True
        self._shutdown_event.clear()
        await self._register()
        await self._log_event("agent_started", {"name": self.name})
        self._last_heartbeat = time.time()

        self._task = asyncio.create_task(self._run_loop())
        logger.info(f"[{self.agent_id}] Agent started")

    async def _run_loop(self):
        """Main think loop with proper error handling and cancellation"""
        try:
            while self._running and not self._shutdown_event.is_set():
                try:
                    cycle_start = time.time()
                    
                    if not self._running:
                        break

                    if self.inbox:
                        messages_to_process = list(self.inbox)
                        self.inbox.clear()
                        for msg in messages_to_process:
                            await self._process_message(msg)

                    if self._running:
                        await self.think()

                    self._consecutive_errors = 0
                    self._last_heartbeat = time.time()

                    if self.status != AgentStatus.ACTIVE:
                        self.status = AgentStatus.ACTIVE

                    cycle_time = time.time() - cycle_start
                    sleep_time = max(0, self.think_cycle - cycle_time)
                    
                    if sleep_time > 0:
                        await asyncio.wait_for(
                            self._shutdown_event.wait(),
                            timeout=sleep_time
                        )
                        
                except asyncio.CancelledError:
                    logger.info(f"[{self.agent_id}] Cancelled")
                    break
                except Exception as e:
                    self._consecutive_errors += 1
                    logger.error(f"[{self.agent_id}] Think cycle error ({self._consecutive_errors}): {e}")
                    await self._handle_error(e)
                    
                    if self._consecutive_errors >= self._max_consecutive_errors:
                        logger.error(f"[{self.agent_id}] Too many errors, going to error state")
                        self.status = AgentStatus.ERROR
                        break
                        
        finally:
            self._running = False
            logger.info(f"[{self.agent_id}] Loop ended")

    async def stop(self):
        """Stop the agent gracefully with proper cleanup"""
        if not self._running:
            return
            
        logger.info(f"[{self.agent_id}] Stopping...")
        self._running = False
        self._shutdown_event.set()
        
        if self._task and not self._task.done():
            try:
                self._task.cancel()
                await asyncio.wait_for(asyncio.shield(self._task), timeout=5.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
            except Exception as e:
                logger.error(f"[{self.agent_id}] Error during stop: {e}")
        
        self.status = AgentStatus.IDLE
        await self._log_event("agent_stopped", {"name": self.name})
        self._cleanup()

    async def terminate(self):
        """Permanently terminate the agent"""
        logger.info(f"[{self.agent_id}] Terminating...")
        self._running = False
        self._shutdown_event.set()
        
        if self._task and not self._task.done():
            self._task.cancel()
            
        self.status = AgentStatus.TERMINATED
        self._cleanup()

    def _cleanup(self):
        """Clean up agent resources"""
        self.memory.clear()
        self.inbox.clear()
        self._task = None

    def _get_memory_max_size(self) -> int:
        """Get max memory size based on tier"""
        tier_multipliers = {0: 170, 1: 140, 2: 110, 3: 80, 4: 50}
        return tier_multipliers.get(self.tier, 50)

    # ─── LLM REASONING ──────────────────────────────────────

    async def reason(self, prompt: str, tools: list = None) -> Dict:
        """Call the LLM engine with this agent's personality + prompt."""
        from app.agents.llm_engine import get_engine
        from app.agents.tools import get_tools_for_agent

        if tools is None:
            tools = get_tools_for_agent(self)

        try:
            result = await get_engine().reason(self, prompt, tools)
            self._trim_memory()
            return result
        except Exception as e:
            logger.error(f"[{self.agent_id}] Reason error: {e}")
            return self._stub_response()

    def _stub_response(self) -> Dict:
        """Fallback stub response"""
        return {
            "decisions": [],
            "directives": [],
            "alerts": [],
            "status": "stub",
        }

    def _trim_memory(self):
        """Keep memory within bounds - already handled by deque maxlen"""

    # ─── COMMUNICATION ──────────────────────────────────────

    async def send_message(
        self,
        to_agent_id: str,
        msg_type: MessageType,
        payload: Dict,
        priority: Priority = Priority.P2_MEDIUM
    ):
        """Send a message to another agent"""
        message = {
            "msg_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "from": {
                "agent_id": self.agent_id,
                "tier": self.tier,
                "role": self.role
            },
            "to_agent_id": to_agent_id,
            "type": msg_type.value,
            "priority": priority.value,
            "payload": payload
        }

        self.metrics.messages_sent += 1
        self.memory.append({"type": "sent", "msg": message})

    async def send_report_up(self, data: Dict):
        """Send a status report to parent agent"""
        if self.parent_agent_id:
            await self.send_message(
                self.parent_agent_id,
                MessageType.REPORT,
                {"action": "status_report", "data": data}
            )

    async def send_directive_down(self, child_id: str, directive: Dict):
        """Send a directive to a child agent"""
        await self.send_message(
            child_id,
            MessageType.DIRECTIVE,
            directive,
            priority=Priority.P1_HIGH
        )

    async def escalate(self, issue: Dict):
        """Escalate an issue to parent agent"""
        if not self.parent_agent_id:
            logger.warning(f"[{self.agent_id}] No parent to escalate to")
            return
            
        await self.send_message(
            self.parent_agent_id,
            MessageType.ESCALATION,
            {
                "action": "escalation",
                "issue": issue,
                "agent_attempts": self.metrics.tasks_failed,
                "context": list(self.memory)[-5:]
            },
            priority=Priority.P0_CRITICAL
        )

    async def broadcast_to_children(self, message: Dict):
        """Send message to all child agents"""
        for child_id in self.children:
            await self.send_message(child_id, MessageType.DIRECTIVE, message)

    # ─── INTERNAL METHODS ───────────────────────────────────

    async def receive_message(self, msg: Dict):
        """Receive a message from another agent"""
        if len(self.inbox) >= self.MAX_INBOX_SIZE:
            logger.warning(f"[{self.agent_id}] Inbox full, dropping oldest message")
            try:
                self.inbox.popleft()
            except Exception:
                pass
        self.inbox.append(msg)
        self.metrics.messages_received += 1

    async def _process_message(self, msg: Dict):
        """Process an incoming message"""
        msg_type = msg.get("type")

        if msg_type == MessageType.DIRECTIVE.value:
            await self._handle_directive(msg)
        elif msg_type == MessageType.REPORT.value:
            await self._handle_report(msg)
        elif msg_type == MessageType.ALERT.value:
            await self._handle_alert(msg)
        elif msg_type == MessageType.ESCALATION.value:
            await self._handle_escalation(msg)

        self.memory.append({"type": "message_received", "msg": msg})

    async def _handle_directive(self, msg: Dict):
        """Handle directive from higher-tier agent"""
        self.memory.append({"type": "directive_received", "msg": msg})

    async def _handle_report(self, msg: Dict):
        """Handle report from lower-tier agent"""
        self.memory.append({"type": "report_received", "msg": msg})

    async def _handle_alert(self, msg: Dict):
        """Handle alert"""
        self.memory.append({"type": "alert_received", "msg": msg})

    async def _handle_escalation(self, msg: Dict):
        """Handle escalation from lower-tier agent"""
        self.memory.append({"type": "escalation_received", "msg": msg})

    async def _register(self):
        """Register agent in database"""
        db_gen = get_db()
        try:
            db = next(db_gen)
            from app.models import Agent
            existing = db.query(Agent).filter(Agent.id == self.agent_id).first()
            if not existing:
                agent = Agent(
                    id=self.agent_id,
                    name=self.name,
                    agent_class=self.agent_class.value,
                    tier=self.tier,
                    role=self.role,
                    model=self.model,
                    status=self.status.value,
                    personality=self.personality,
                    config={
                        "think_cycle": self.think_cycle,
                        "authority": self.authority
                    },
                    metrics=asdict(self.metrics),
                    parent_agent_id=self.parent_agent_id,
                    category_id=self.category_id
                )
                db.add(agent)
                db.commit()
            else:
                existing.status = self.status.value
                existing.metrics = asdict(self.metrics)
                db.commit()
        except Exception as e:
            logger.error(f"[{self.agent_id}] Register error: {e}")
        finally:
            try:
                next(db_gen, None)
            except Exception:
                pass

    async def _log_event(self, event_type: str, data: Dict):
        """Log an event to the database"""
        db_gen = get_db()
        try:
            db = next(db_gen)
            from app.models import Event
            event = Event(
                event_type=event_type,
                source=self.agent_id,
                agent_id=self.agent_id,
                data=data
            )
            db.add(event)
            db.commit()
        except Exception as e:
            logger.error(f"[{self.agent_id}] Log event error: {e}")
        finally:
            try:
                next(db_gen, None)
            except Exception:
                pass

    async def _handle_error(self, error: Exception):
        """Handle an error in the agent's think loop"""
        try:
            await self._log_event("agent_error", {
                "error": str(error),
                "agent": self.name,
                "consecutive_errors": self._consecutive_errors
            })
        except Exception:
            pass

    def is_healthy(self) -> bool:
        """Check if agent is healthy based on heartbeat"""
        if not self._running:
            return False
        return (time.time() - self._last_heartbeat) < (self.HEARTBEAT_INTERVAL * 3)

    # ─── PROPERTIES ─────────────────────────────────────────

    @property
    def success_rate(self) -> float:
        total = self.metrics.tasks_completed + self.metrics.tasks_failed
        if total == 0:
            return 100.0
        return (self.metrics.tasks_completed / total) * 100

    @property
    def memory_size(self) -> int:
        return len(self.memory)

    def to_dict(self) -> Dict:
        """Serialize agent state"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "tier": self.tier,
            "role": self.role,
            "model": self.model,
            "status": self.status.value,
            "authority": self.authority,
            "agent_class": self.agent_class.value,
            "tasks_completed": self.metrics.tasks_completed,
            "tasks_failed": self.metrics.tasks_failed,
            "success_rate": self.success_rate,
            "revenue_generated": self.metrics.revenue_generated,
            "memory_size": self.memory_size,
            "inbox_size": len(self.inbox),
            "children_count": len(self.children),
            "is_healthy": self.is_healthy(),
            "last_heartbeat": self._last_heartbeat
        }
