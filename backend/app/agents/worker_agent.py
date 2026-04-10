"""LUXOR9 - Worker Agent — Tier 4

Workers are task executors. Each has a specific type that determines
its capabilities and available tools:
- scout: Research leads/market (web search)
- mail: Write & send emails
- social: Social media posting
- sales: Close deals
- build: Build automations
- write: Create content
- chat: Customer support
- data: Analyze data/KPIs
- test: QA & testing
- growth: A/B tests & optimization
"""
import logging
from typing import Dict, Optional
from app.agents.base_agent import BaseAgent, AgentClass, AgentStatus

logger = logging.getLogger("luxor9.worker")


class WorkerAgent(BaseAgent):
    """Worker Agent — Task Execution Unit with LangChain tools."""

    WORKER_CAPABILITIES = {
        "scout": {
            "name": "ScoutBot",
            "focus": "Research leads/market",
            "tools": ["search_web"]
        },
        "mail": {
            "name": "MailBot",
            "focus": "Write & send emails",
            "tools": ["send_email"]
        },
        "social": {
            "name": "SocialBot",
            "focus": "Social media posting",
            "tools": ["generate_content"]
        },
        "sales": {
            "name": "SalesBot",
            "focus": "Close deals",
            "tools": ["search_web", "send_email"]
        },
        "build": {
            "name": "BuildBot",
            "focus": "Build automations",
            "tools": ["generate_content"]
        },
        "write": {
            "name": "WriteBot",
            "focus": "Create content",
            "tools": ["generate_content"]
        },
        "chat": {
            "name": "ChatBot",
            "focus": "Customer support",
            "tools": ["generate_content"]
        },
        "data": {
            "name": "DataBot",
            "focus": "Analyze data/KPIs",
            "tools": ["query_stream_metrics"]
        },
        "test": {
            "name": "TestBot",
            "focus": "QA & testing",
            "tools": []
        },
        "growth": {
            "name": "GrowthBot",
            "focus": "A/B tests & optimization",
            "tools": ["query_stream_metrics"]
        }
    }

    def __init__(
        self,
        agent_id: str,
        name: str,
        worker_type: str,
        category_id: int,
        parent_agent_id: str
    ):
        capability = self.WORKER_CAPABILITIES.get(worker_type, {})

        super().__init__(
            agent_id=agent_id,
            name=name,
            tier=4,
            role=f"worker_{worker_type}",
            model="gpt-4o-mini",
            think_cycle_seconds=30,
            authority_level=3,
            parent_agent_id=parent_agent_id,
            personality=self._default_personality(worker_type, capability),
            agent_class=AgentClass.WORKER
        )
        self.worker_type = worker_type
        self.category_id = category_id
        self.capability = capability
        self.current_task: Optional[Dict] = None

    def _default_personality(self, worker_type: str, capability: Dict) -> str:
        return f"""
You are a {capability.get('name', 'Worker')} for the Luxor9 Empire.

FOCUS: {capability.get('focus', 'Task execution')}
TOOLS: {', '.join(capability.get('tools', []))}

RESPONSIBILITIES:
- Execute assigned tasks efficiently using your tools
- Report completion status to your manager
- Escalate issues after 3 failed attempts
- Maintain high success rate (>90%)

AUTHORITY: Limited — can only execute assigned tasks.

OUTPUT FORMAT: Respond as JSON with:
- action: what you did
- result: outcome of the action
- status: success/failed/needs_escalation
- revenue: any revenue generated (number or 0)
"""

    async def think(self):
        """Worker reasoning — check for tasks and execute them."""

        # 1. Check inbox for task assignments
        if not self.current_task:
            await self._check_for_task()

        # 2. If no task, skip this cycle (save LLM costs)
        if not self.current_task:
            return

        # 3. Execute task with LLM reasoning
        result = await self._execute_task(self.current_task)

        # 4. Report completion to manager
        await self.send_report_up({
            "task_id": self.current_task.get("id", "unknown"),
            "worker_type": self.worker_type,
            "status": result.get("status", "completed"),
            "result": result,
        })

        # 5. Clear task
        self.current_task = None

    async def _check_for_task(self):
        """Check inbox for task directives from manager."""
        for entry in self.memory:
            if entry.get("type") == "directive_received":
                msg = entry.get("msg", {})
                payload = msg.get("payload", {})
                if payload.get("action") == "execute_task":
                    self.current_task = payload.get("task", {})
                    break

        # Also check direct inbox
        for msg in self.inbox:
            payload = msg.get("payload", {})
            if payload.get("action") == "execute_task":
                self.current_task = payload.get("task", {})
                break

    async def _execute_task(self, task: Dict) -> Dict:
        """Execute the assigned task using LLM + tools."""
        try:
            prompt = f"""
TASK ASSIGNED: {task}
YOUR TYPE: {self.worker_type} ({self.capability.get('focus', '')})

Execute this task using your available tools. Be efficient and report:
1. What action did you take?
2. What was the result?
3. Did you generate any revenue? (estimate in USD if applicable)

Respond as JSON with: action, result, status (success/failed), revenue (number).
"""
            result = await self.reason(prompt)

            # Track metrics
            status = result.get("status", "success")
            if status == "success":
                self.metrics.tasks_completed += 1
                revenue = float(result.get("revenue", 0))
                if revenue > 0:
                    self.metrics.revenue_generated += revenue
            else:
                self.metrics.tasks_failed += 1
                if self.metrics.tasks_failed >= 3:
                    await self.escalate({
                        "issue": "repeated_task_failure",
                        "task": task,
                        "failures": self.metrics.tasks_failed,
                    })

            return result

        except Exception as e:
            self.metrics.tasks_failed += 1
            logger.error(f"[{self.agent_id}] Task execution error: {e}")
            if self.metrics.tasks_failed >= 3:
                await self.escalate({
                    "issue": "repeated_task_failure",
                    "task": task,
                    "error": str(e),
                })
            return {"status": "failed", "error": str(e)}
