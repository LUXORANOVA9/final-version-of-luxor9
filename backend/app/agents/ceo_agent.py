"""LUXOR9 - CEO Agent for 1-Person Company"""
import asyncio
import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import deque

from app.agents.base_agent import BaseAgent, AgentStatus, AgentClass, AgentMetrics
from app.config import get_settings

logger = logging.getLogger("luxor9.ceo")


class CEOAgent(BaseAgent):
    """
    Single AI Agent for 1-person company CEO operations.
    Handles all business tasks from a unified interface.
    """

    MAX_MEMORY_SIZE = 500

    def __init__(self):
        super().__init__(
            agent_id="CEO-AGENT",
            name="CEO Agent",
            tier=0,
            role="chief_executive_officer",
            model="gpt-4o",
            think_cycle_seconds=30,
            authority_level=10,
            personality=self._default_personality(),
            agent_class=AgentClass.COMMANDER
        )
        self.pending_tasks: List[Dict] = []
        self.last_human_command: Optional[str] = None
        self.suggestions: List[str] = []
        self.alerts: List[str] = []
        self.opportunities: List[str] = []

    def _default_personality(self) -> str:
        return """You are the CEO Agent for a 1-person company. You are the single AI that handles ALL business operations.

IDENTITY:
- You are the CEO of this company - the only AI agent
- You handle strategy, execution, research, communication, and analysis
- You operate from a single unified dashboard
- You are proactive, suggesting improvements and alerting the human CEO to important matters

CAPABILITIES:
- Web research and lead generation
- Content creation (blogs, social media, emails)
- Data analysis and reporting
- Email communication
- Task execution and tracking
- Market analysis

COMMUNICATION STYLE:
- Be direct, actionable, and concise
- When presenting options, number them clearly
- Proactively suggest improvements
- Alert to urgent matters immediately

When the human CEO gives you a command:
1. Understand the goal
2. Execute using available tools
3. Report results clearly
4. Suggest next steps if relevant"""

    async def think(self):
        """Main reasoning cycle - processes commands and generates proactive suggestions"""

        # 1. Process any pending human commands first
        if self.pending_tasks:
            task = self.pending_tasks.pop(0)
            await self._execute_task(task)

        # 2. Generate proactive suggestions
        prompt = f"""
As the CEO of this 1-person company, analyze the current state and generate:
1. Any urgent alerts or concerns
2. Proactive suggestions for the human CEO
3. Opportunities or threats to highlight

Current agent metrics:
- Tasks completed: {self.metrics.tasks_completed}
- Tasks failed: {self.metrics.tasks_failed}
- Revenue generated: ${self.metrics.revenue_generated}

Recent memory (last 5 items):
{self._get_memory_summary()}

Respond as JSON with keys: alerts (list), suggestions (list), opportunities (list)
"""

        try:
            result = await self.reason(prompt, tools=[])
            if result.get("raw_response"):
                try:
                    parsed = json.loads(result["raw_response"])
                    self.suggestions = parsed.get("suggestions", [])
                    self.alerts = parsed.get("alerts", [])
                    self.opportunities = parsed.get("opportunities", [])
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            logger.warning(f"CEO think cycle error: {e}")

    def _get_memory_summary(self) -> str:
        """Get summary of recent memory items"""
        items = list(self.memory)[-5:]
        return "\n".join([str(m)[:100] for m in items]) if items else "No memory yet"

    async def _execute_task(self, task: Dict):
        """Execute a task from the human CEO"""
        command = task.get("command", "")
        task_type = task.get("type", "general")

        prompt = f"""
HUMAN CEO COMMAND: {command}

Execute this command. Use available tools as needed.
Report results clearly. If there are multiple options, present them numbered.

Task type: {task_type}
"""

        try:
            result = await self.reason(prompt)
            task["result"] = result
            task["completed_at"] = datetime.utcnow().isoformat()
            task["status"] = "completed"
            self.metrics.tasks_completed += 1
        except Exception as e:
            task["result"] = {"error": str(e)}
            task["completed_at"] = datetime.utcnow().isoformat()
            task["status"] = "failed"
            self.metrics.tasks_failed += 1

        return result

    async def receive_command(self, command: str) -> Dict:
        """Receive a command from the human CEO"""
        task = {
            "id": str(uuid.uuid4()),
            "command": command,
            "type": "human_command",
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending"
        }
        self.pending_tasks.append(task)
        self.last_human_command = command

        # Add to memory
        self.memory.append({
            "type": "human_command",
            "command": command,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Execute immediately for responsive feel
        result = await self._execute_task(task)

        return {
            "task_id": task["id"],
            "result": result,
            "status": task["status"]
        }

    def to_dict(self) -> Dict:
        base = super().to_dict()
        base.update({
            "pending_tasks_count": len(self.pending_tasks),
            "last_command": self.last_human_command,
            "suggestions": self.suggestions,
            "alerts": self.alerts,
            "opportunities": self.opportunities
        })
        return base


# Global singleton
_ceo_agent: Optional[CEOAgent] = None


def get_ceo_agent() -> CEOAgent:
    """Get or create CEO agent singleton"""
    global _ceo_agent
    if _ceo_agent is None:
        _ceo_agent = CEOAgent()
    return _ceo_agent