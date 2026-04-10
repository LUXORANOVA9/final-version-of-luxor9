"""LUXOR9 - Manager Agent — Tier 3

Each Manager handles one of three functions per VP:
- ACQ: Customer acquisition (scout, mail, social, sales workers)
- DEL: Service delivery (build, write, test workers)
- RET: Customer retention (chat, data, growth workers)
"""
import logging
from typing import Dict, List, Optional
from app.agents.base_agent import BaseAgent, AgentClass, AgentStatus

logger = logging.getLogger("luxor9.manager")


class ManagerAgent(BaseAgent):
    """Manager Agent — task routing and worker coordination."""

    MANAGER_TYPES = {
        "ACQ": {
            "focus": "Getting new customers/leads",
            "worker_types": ["scout", "mail", "social", "sales"]
        },
        "DEL": {
            "focus": "Fulfilling orders/delivering services",
            "worker_types": ["build", "write", "test"]
        },
        "RET": {
            "focus": "Keeping customers, upselling, support",
            "worker_types": ["chat", "data", "growth"]
        }
    }

    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        description: str,
        category_id: int,
        parent_agent_id: str
    ):
        mgr_type = "ACQ" if "-ACQ" in agent_id else ("DEL" if "-DEL" in agent_id else "RET")

        super().__init__(
            agent_id=agent_id,
            name=name,
            tier=3,
            role=role,
            model="gpt-4o-mini",
            think_cycle_seconds=45,
            authority_level=5,
            parent_agent_id=parent_agent_id,
            personality=self._default_personality(mgr_type, description),
            agent_class=AgentClass.MANAGER
        )
        self.manager_type = mgr_type
        self.category_id = category_id
        self.children: List[str] = []
        self.task_queue: List[Dict] = []

    def _default_personality(self, mgr_type: str, description: str) -> str:
        type_info = self.MANAGER_TYPES.get(mgr_type, {})
        return f"""
You are {self.name}, a {mgr_type} Manager for the Luxor9 Empire.

FOCUS: {type_info.get('focus', description)}

RESPONSIBILITIES:
- Manage team of workers for {type_info.get('focus', description).lower()}
- Assign tasks to worker agents intelligently based on their type
- Monitor worker performance and redistribute if needed
- Escalate issues to VP after 3 failed attempts
- Report metrics to parent VP

WORKERS: {', '.join(type_info.get('worker_types', []))}

KPIs:
- ACQ: New leads/day, conversion rate, CAC
- DEL: Delivery time, quality score, completion rate
- RET: Churn rate, NPS, upsell revenue, ticket resolution

OUTPUT FORMAT: Respond as JSON with:
- assignments: list of task assignments (worker_id, task_type, description)
- status_report: summary for VP
- escalations: issues for VP
"""

    async def think(self):
        """Manager reasoning — route tasks to workers intelligently."""

        # Gather worker status
        worker_status = await self._check_worker_status()
        pending = self.task_queue

        prompt = f"""
MANAGER TYPE: {self.manager_type}
PENDING TASKS: {len(pending)} tasks
TASK QUEUE: {pending[:5]}

WORKERS ({len(self.children)}):
{worker_status}

INBOX DIRECTIVES: {[m for m in self.memory[-5:] if m.get('type') == 'directive_received']}

Decide:
1. How to assign pending tasks to available workers?
2. Any workers underperforming that need attention?
3. Should any tasks be escalated to VP?
4. Status summary for VP report.

Respond as JSON with: assignments (list with worker_id, task_type, description), status_report (dict), escalations (list).
"""
        result = await self.reason(prompt)

        # Execute task assignments
        for assignment in result.get("assignments", []):
            worker_id = assignment.get("worker_id")
            if worker_id and worker_id in self.children:
                await self.send_directive_down(worker_id, {
                    "action": "execute_task",
                    "task": assignment,
                })

        # Report to VP
        await self.send_report_up({
            "manager_type": self.manager_type,
            "pending_tasks": len(pending),
            "worker_count": len(self.children),
            "status": result.get("status_report", {}),
            "escalations": result.get("escalations", []),
        })
        self.metrics.tasks_completed += 1

    async def _check_worker_status(self) -> List[Dict]:
        """Check status of all workers."""
        from app.orchestrator import orchestrator
        status = []
        for child_id in self.children:
            worker = orchestrator.agents.get(child_id)
            if worker:
                status.append({
                    "id": child_id,
                    "status": worker.status.value,
                    "tasks_done": worker.metrics.tasks_completed,
                    "success_rate": worker.success_rate,
                })
            else:
                status.append({"id": child_id, "status": "unknown"})
        return status

    async def _handle_escalations(self):
        """Handle escalations from workers."""
        escalations = [
            e for e in self.memory
            if e.get("type") == "escalation_received"
        ]
        if escalations:
            await self.escalate({
                "issue": "worker_escalations",
                "count": len(escalations),
                "details": escalations[-3:],
            })
