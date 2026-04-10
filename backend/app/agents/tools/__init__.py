"""LUXOR9 - Agent Tool Registry"""
from typing import List
from langchain_core.tools import BaseTool
from app.agents.tools.system_tools import (
    QueryStreamMetricsTool,
    QueryAgentStatusTool,
    DeployStreamTool,
    StopStreamTool,
    AssignTaskTool,
    SendAgentMessageTool,
    LogRevenueTool,
    SearchWebTool,
    SendEmailTool,
    GenerateContentTool,
)
from app.agents.tools.ceo_tools import (
    CEOSearchTool,
    CEOEmailTool,
    CEOContentTool,
    CEOAnalysisTool,
    CEOTaskTool,
)


# Tier-based tool access mapping
TIER_TOOLS = {
    0: [  # PRIME — full access
        QueryStreamMetricsTool,
        QueryAgentStatusTool,
        DeployStreamTool,
        StopStreamTool,
        SendAgentMessageTool,
    ],
    1: [  # C-Suite — strategic + domain
        QueryStreamMetricsTool,
        QueryAgentStatusTool,
        DeployStreamTool,
        StopStreamTool,
        SendAgentMessageTool,
    ],
    2: [  # VPs — operational
        QueryStreamMetricsTool,
        DeployStreamTool,
        StopStreamTool,
        AssignTaskTool,
        SendAgentMessageTool,
    ],
    3: [  # Managers — task management
        AssignTaskTool,
        SendAgentMessageTool,
        LogRevenueTool,
    ],
    4: [  # Workers — execution
        SendAgentMessageTool,
        LogRevenueTool,
    ],
}

# Worker-type specific tools
WORKER_TYPE_TOOLS = {
    "scout": [SearchWebTool],
    "mail": [SendEmailTool],
    "write": [GenerateContentTool],
    "social": [GenerateContentTool],
    "sales": [SearchWebTool, SendEmailTool],
    "build": [GenerateContentTool],
    "chat": [GenerateContentTool],
    "data": [QueryStreamMetricsTool],
    "test": [],
    "growth": [QueryStreamMetricsTool],
}


def get_tools_for_tier(tier: int) -> List[BaseTool]:
    """Get tool instances for a given tier."""
    tool_classes = TIER_TOOLS.get(tier, [])
    return [cls() for cls in tool_classes]


def get_tools_for_worker(worker_type: str) -> List[BaseTool]:
    """Get additional tools for a specific worker type."""
    extra_classes = WORKER_TYPE_TOOLS.get(worker_type, [])
    base = get_tools_for_tier(4)
    extras = [cls() for cls in extra_classes if cls not in TIER_TOOLS.get(4, [])]
    return base + extras


def get_tools_for_agent(agent) -> List[BaseTool]:
    """Get all tools for an agent based on tier and type."""
    from app.agents.worker_agent import WorkerAgent
    from app.agents.ceo_agent import CEOAgent

    if isinstance(agent, CEOAgent):
        # CEO agent gets all CEO-specific tools
        return [
            CEOSearchTool(),
            CEOEmailTool(),
            CEOContentTool(),
            CEOAnalysisTool(),
            CEOTaskTool(),
        ]
    if isinstance(agent, WorkerAgent):
        return get_tools_for_worker(agent.worker_type)
    return get_tools_for_tier(agent.tier)
