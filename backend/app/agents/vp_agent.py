"""LUXOR9 - VP (Vice President) Agent — Tier 2

Each VP manages one of the 10 categories and coordinates
3 managers (ACQ, DEL, RET) plus their workers.
"""
import logging
from typing import Dict, List, Optional
from app.agents.base_agent import BaseAgent, AgentClass, AgentStatus

logger = logging.getLogger("luxor9.vp")


class VPAgent(BaseAgent):
    """Vice President Agent - Category Commander"""

    def __init__(
        self,
        agent_id: str,
        name: str,
        category_id: int,
        category_name: str,
        stream_ids: List[int],
        parent_agent_id: str = "CORTEX"
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            tier=2,
            role=f"vp_{category_name.lower().replace(' ', '_')}",
            model="gpt-4o-mini",
            think_cycle_seconds=60,
            authority_level=7,
            parent_agent_id=parent_agent_id,
            personality=self._default_personality(category_name),
            agent_class=AgentClass.VP
        )
        self.category_id = category_id
        self.category_name = category_name
        self.stream_ids = stream_ids
        self.children: List[str] = []
        self.csuite_ref: Optional[BaseAgent] = None

    def _default_personality(self, category_name: str) -> str:
        return f"""
You are {self.name}, VP of {category_name} for the Luxor9 Empire.

RESPONSIBILITIES:
- Coordinate all streams in {category_name} category (streams {self.stream_ids[0]}-{self.stream_ids[-1]})
- Deploy/stop streams based on performance
- Assign tasks to manager agents (ACQ, DEL, RET)
- Report category metrics up the chain
- Identify cross-sell opportunities within category

DECISION AUTHORITY:
- CAN: Start/stop workers, adjust pricing ±15%, reassign tasks
- CANNOT: Kill a stream (needs CORTEX approval)
- CANNOT: Exceed budget (needs TREASURY approval)

You can use tools to query stream metrics, deploy/stop streams, and assign tasks.

OUTPUT FORMAT: Respond as JSON with:
- category_status: summary of category health
- stream_actions: list of deploy/stop/adjust actions
- manager_tasks: tasks to assign to ACQ/DEL/RET managers
- escalations: issues needing CORTEX attention
"""

    async def think(self):
        """VP reasoning cycle — manage category streams and managers."""

        # Gather stream metrics for this category
        stream_metrics = await self._get_stream_metrics()
        manager_reports = await self._gather_manager_reports()

        prompt = f"""
CATEGORY: {self.category_name}
STREAMS ({self.stream_ids[0]}-{self.stream_ids[-1]}):
{stream_metrics}

MANAGER REPORTS (ACQ/DEL/RET):
{manager_reports}

MANAGERS: {self.children}

Analyze category performance:
1. Which streams are performing well vs underperforming?
2. Should any streams be deployed or stopped?
3. What tasks should be assigned to ACQ, DEL, RET managers?
4. Any issues to escalate to CORTEX?

Respond as JSON with: category_status, stream_actions (list), manager_tasks (list with worker_id and task), escalations (list).
"""
        result = await self.reason(prompt)

        # Execute stream actions
        for action in result.get("stream_actions", []):
            await self._execute_decision(action)

        # Assign tasks to managers
        for task in result.get("manager_tasks", []):
            target = task.get("manager_id") or task.get("worker_id")
            if target:
                await self.send_directive_down(target, task)

        # Report to CORTEX
        await self.send_report_up({
            "category": self.category_name,
            "status": result.get("category_status", ""),
            "escalations": result.get("escalations", []),
        })
        self.metrics.tasks_completed += 1

    async def _get_stream_metrics(self) -> List[Dict]:
        """Get metrics for all streams in this category."""
        from app.database import SessionLocal, Stream
        db = SessionLocal()
        try:
            streams = db.query(Stream).filter(
                Stream.id.in_(self.stream_ids)
            ).all()
            return [
                {
                    "id": s.id, "title": s.title, "status": s.status,
                    "revenue_today": s.revenue_today, "health_score": s.health_score,
                }
                for s in streams
            ]
        except Exception:
            return []
        finally:
            db.close()

    async def _gather_manager_reports(self) -> List[Dict]:
        """Gather reports from child managers."""
        # Reports come in via inbox — summarize recent ones
        reports = [
            entry["msg"] for entry in self.memory
            if entry.get("type") == "report_received"
        ]
        return reports[-5:]  # Last 5 reports

    async def _execute_decision(self, decision: Dict):
        """Execute a stream-level decision."""
        action = decision.get("action", "")
        stream_id = decision.get("stream_id")
        if action == "deploy" and stream_id:
            from app.agents.tools.system_tools import DeployStreamTool
            DeployStreamTool().invoke({"stream_id": stream_id})
        elif action == "stop" and stream_id:
            from app.agents.tools.system_tools import StopStreamTool
            StopStreamTool().invoke({"stream_id": stream_id})
