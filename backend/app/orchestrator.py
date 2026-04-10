"""LUXOR9 - Orchestrator Engine"""
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime

import redis.asyncio as redis

from app.config import get_settings
from app.database import init_db
from app.agents.llm_engine import get_engine
from app.agents.base_agent import BaseAgent, AgentStatus, MessageType, Priority

logger = logging.getLogger("luxor9.orchestrator")

SHUTDOWN_TIMEOUT = 30.0


class Orchestrator:
    """
    The central orchestration engine that manages the entire
    Luxor9 agent hierarchy and all 100 income streams.
    """

    def __init__(self):
        self.settings = get_settings()
        self.agent_factory = AgentFactory()
        self.agents: Dict[str, BaseAgent] = {}
        self.is_running = False
        self._redis: Optional[redis.Redis] = None
        self._tasks: List[asyncio.Task] = []
        self._shutdown_event: Optional[asyncio.Event] = None

    async def boot(self) -> bool:
        """Boot the entire system — spawn all agents in hierarchy order"""
        if self.is_running:
            logger.warning("Orchestrator already running")
            return False

        try:
            logger.info("═══ LUXOR9 ORCHESTRATOR BOOTING ═══")
            
            self._shutdown_event = asyncio.Event()
            self.is_running = True

            try:
                self._redis = redis.from_url(self.settings.redis_url, decode_responses=True)
                await self._redis.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Continuing without Redis.")
                self._redis = None

            init_db()
            logger.info("Database initialized")

            self.agents = self.agent_factory.create_all_agents()

            # Inject the Unified Fusion Engine into every agent
            fusion_engine = get_engine()
            for agent in self.agents.values():
                agent.llm = fusion_engine

            logger.info(f"[BOOT] Created {len(self.agents)} agents and injected Fusion Engine")
            logger.info(f"[BOOT] Tier 0: {len(self.agent_factory.get_agents_by_tier(0))} Commander")
            logger.info(f"[BOOT] Tier 1: {len(self.agent_factory.get_agents_by_tier(1))} C-Suite")
            logger.info(f"[BOOT] Tier 2: {len(self.agent_factory.get_agents_by_tier(2))} VPs")
            logger.info(f"[BOOT] Tier 3: {len(self.agent_factory.get_agents_by_tier(3))} Managers")
            logger.info(f"[BOOT] Tier 4: {len(self.agent_factory.get_agents_by_tier(4))} Workers")

            agent_tasks = []
            for agent in self.agents.values():
                await agent.initialize()
                task = asyncio.create_task(agent.start())
                self._tasks.append(task)
                agent_tasks.append(agent.agent_id)

            metrics_task = asyncio.create_task(self._metrics_loop())
            self._tasks.append(metrics_task)

            logger.info(f"[BOOT] Started {len(agent_tasks)} agent tasks")
            logger.info("═══ LUXOR9 SYSTEM ONLINE ═══")
            return True

        except Exception as e:
            logger.error(f"[BOOT] Failed to boot: {e}")
            await self.shutdown()
            return False

    async def shutdown(self, timeout: float = SHUTDOWN_TIMEOUT):
        """Gracefully shutdown the orchestrator with proper cancellation"""
        if not self.is_running:
            logger.info("Orchestrator not running")
            return

        logger.info("═══ LUXOR9 SHUTTING DOWN ═══")
        self.is_running = False

        if self._shutdown_event:
            self._shutdown_event.set()

        stopped_agents = []
        for agent in self.agents.values():
            try:
                await asyncio.wait_for(agent.stop(), timeout=5.0)
                stopped_agents.append(agent.agent_id)
            except asyncio.TimeoutError:
                logger.warning(f"[{agent.agent_id}] Stop timeout, terminating")
                await agent.terminate()
            except Exception as e:
                logger.error(f"[{agent.agent_id}] Error stopping: {e}")

        logger.info(f"Stopped {len(stopped_agents)} agents")

        cancelled_tasks = []
        for i, task in enumerate(self._tasks):
            if not task.done():
                task.cancel()
                cancelled_tasks.append(i)
        
        if cancelled_tasks:
            logger.info(f"Cancelling {len(cancelled_tasks)} background tasks")

        if self._tasks:
            results = await asyncio.wait_for(
                asyncio.gather(*self._tasks, return_exceptions=True),
                timeout=timeout
            )
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Task {i} error: {result}")

        self._tasks.clear()

        if self._redis:
            try:
                await asyncio.wait_for(self._redis.close(), timeout=5.0)
            except Exception as e:
                logger.error(f"Redis close error: {e}")

        self._redis = None
        logger.info("═══ LUXOR9 OFFLINE ═══")

    async def force_shutdown(self):
        """Force immediate shutdown without graceful cleanup"""
        logger.warning("FORCE SHUTDOWN")
        self.is_running = False
        
        for agent in self.agents.values():
            try:
                agent.terminate()
            except Exception:
                pass

        for task in self._tasks:
            task.cancel()

        self._tasks.clear()
        
        if self._redis:
            try:
                self._redis.close()
            except Exception:
                pass

    # ─── PUBLIC CONTROL METHODS ─────────────────────────────

    async def deploy_stream(self, stream_id: int):
        """Deploy a specific income stream"""
        logger.debug(f"Deploy stream {stream_id}")

    async def stop_stream(self, stream_id: int):
        """Stop a specific income stream"""
        logger.debug(f"Stop stream {stream_id}")

    async def send_command(self, command: str, target: str = "LUXOR-PRIME"):
        """Send a human operator command to an agent"""
        agent = self.agents.get(target)
        if agent:
            await agent.send_message(
                target,
                MessageType.DIRECTIVE,
                {"action": "human_command", "command": command},
                priority=Priority.P0_CRITICAL
            )
            logger.info(f"Sent command to {target}: {command}")
        else:
            logger.warning(f"Agent not found: {target}")

    async def get_full_state(self) -> Dict:
        """Get the complete system state for the dashboard"""
        return {
            "agents": {
                aid: a.to_dict() for aid, a in self.agents.items()
            },
            "hierarchy": self.agent_factory.get_hierarchy_tree(),
            "metrics": self._collect_metrics(),
        }

    async def get_agent_health(self) -> Dict:
        """Get health status of all agents"""
        healthy = []
        unhealthy = []
        
        for agent in self.agents.values():
            if agent.is_healthy():
                healthy.append(agent.agent_id)
            else:
                unhealthy.append(agent.agent_id)
        
        return {
            "total": len(self.agents),
            "healthy": len(healthy),
            "unhealthy": len(unhealthy),
            "healthy_agents": healthy,
            "unhealthy_agents": unhealthy
        }

    # ─── METRICS ─────────────────────────────────────────

    async def _metrics_loop(self):
        """Collect and broadcast metrics every second"""
        while self.is_running:
            try:
                metrics = self._collect_metrics()
                await self._broadcast_metrics(metrics)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics error: {e}")

            try:
                await asyncio.wait_for(
                    asyncio.sleep(1),
                    timeout=self.settings.metrics_interval
                )
            except asyncio.CancelledError:
                break

    def _collect_metrics(self) -> Dict:
        """Collect real-time metrics from all agents"""
        active_agents = sum(
            1 for a in self.agents.values() if a.status == AgentStatus.ACTIVE
        )
        healthy_agents = sum(
            1 for a in self.agents.values() if a.is_healthy()
        )
        total_tasks = sum(
            a.metrics.tasks_completed for a in self.agents.values()
        )
        total_revenue = sum(
            a.metrics.revenue_generated for a in self.agents.values()
        )

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_agents": len(self.agents),
            "active_agents": active_agents,
            "healthy_agents": healthy_agents,
            "total_tasks_completed": total_tasks,
            "total_revenue": total_revenue,
            "agents_by_tier": self._count_by_tier(),
            "agents_by_status": self._count_by_status(),
        }

    async def _broadcast_metrics(self, metrics: Dict):
        """Send metrics to Redis for WebSocket clients"""
        if self._redis:
            try:
                import json
                await self._redis.set(
                    "luxor9:metrics",
                    json.dumps(metrics),
                    ex=10
                )
            except Exception as e:
                logger.error(f"Redis broadcast error: {e}")

    def _count_by_tier(self) -> Dict:
        tiers = {}
        for a in self.agents.values():
            tiers[a.tier] = tiers.get(a.tier, 0) + 1
        return tiers

    def _count_by_status(self) -> Dict:
        statuses = {}
        for a in self.agents.values():
            s = a.status.value
            statuses[s] = statuses.get(s, 0) + 1
        return statuses


orchestrator = Orchestrator()


async def get_orchestrator() -> Orchestrator:
    return orchestrator
