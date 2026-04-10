"""LUXOR9 - Agent Factory & Registry"""
from typing import Dict, List, Optional
from app.agents.base_agent import BaseAgent, AgentClass, AgentStatus
from app.agents.prime import LuxorPrime
from app.agents.csuite import Cortex, Treasury, Sentinel
from app.agents.vp_agent import VPAgent
from app.agents.manager_agent import ManagerAgent
from app.agents.worker_agent import WorkerAgent


class AgentFactory:
    """Factory for creating and managing Luxor9 agents"""

    CATEGORIES = {
        1: {"name": "AI Agency", "vp_name": "FORGE", "color": "#3b82f6"},
        2: {"name": "SaaS", "vp_name": "NEXUS", "color": "#8b5cf6"},
        3: {"name": "Creative", "vp_name": "MUSE", "color": "#ec4899"},
        4: {"name": "Digital", "vp_name": "ATLAS", "color": "#f59e0b"},
        5: {"name": "Finance", "vp_name": "VAULT", "color": "#10b981"},
        6: {"name": "E-commerce", "vp_name": "MARKET", "color": "#06b6d4"},
        7: {"name": "Real Estate", "vp_name": "TERRA", "color": "#f97316"},
        8: {"name": "Marketing", "vp_name": "SIGNAL", "color": "#ef4444"},
        9: {"name": "Enterprise", "vp_name": "TITAN", "color": "#6366f1"},
        10: {"name": "Consulting", "vp_name": "ORACLE", "color": "#64748b"},
    }

    MANAGER_TYPES = [
        ("ACQ", "acquisition_manager", "Lead generation and customer acquisition"),
        ("DEL", "delivery_manager", "Service delivery and fulfillment"),
        ("RET", "retention_manager", "Customer retention and upselling"),
    ]

    WORKER_TYPES = [
        "scout", "mail", "social", "sales", "build",
        "write", "chat", "data", "test", "growth"
    ]

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}

    def create_prime(self) -> LuxorPrime:
        """Create LUXOR-PRIME (Tier 0)"""
        prime = LuxorPrime()
        self.agents[prime.agent_id] = prime
        return prime

    def create_csuite(self) -> Dict[str, BaseAgent]:
        """Create C-Suite agents (Tier 1)"""
        cortex = Cortex(parent_agent_id="LUXOR-PRIME")
        treasury = Treasury(parent_agent_id="LUXOR-PRIME")
        sentinel = Sentinel(parent_agent_id="LUXOR-PRIME")

        self.agents[cortex.agent_id] = cortex
        self.agents[treasury.agent_id] = treasury
        self.agents[sentinel.agent_id] = sentinel

        return {"CORTEX": cortex, "TREASURY": treasury, "SENTINEL": sentinel}

    def create_vps(self) -> Dict[str, VPAgent]:
        """Create VP agents (Tier 2) - one per category"""
        vps = {}
        for cat_id, cat_info in self.CATEGORIES.items():
            vp = VPAgent(
                agent_id=cat_info["vp_name"],
                name=cat_info["vp_name"],
                category_id=cat_id,
                category_name=cat_info["name"],
                stream_ids=list(range((cat_id - 1) * 10 + 1, cat_id * 10 + 1)),
                parent_agent_id="CORTEX"
            )
            self.agents[vp.agent_id] = vp
            vps[vp.agent_id] = vp

        return vps

    def create_managers(self, vps: Dict[str, VPAgent]) -> Dict[str, ManagerAgent]:
        """Create Manager agents (Tier 3) - three per VP"""
        managers = {}

        for vp in vps.values():
            for suffix, role, description in self.MANAGER_TYPES:
                mgr_id = f"{vp.name}-{suffix}"
                mgr = ManagerAgent(
                    agent_id=mgr_id,
                    name=mgr_id,
                    role=role,
                    description=description,
                    category_id=vp.category_id,
                    parent_agent_id=vp.agent_id
                )
                self.agents[mgr_id] = mgr
                managers[mgr_id] = mgr

        return managers

    def create_workers(
        self,
        managers: Dict[str, ManagerAgent],
        workers_per_manager: int = 3
    ) -> Dict[str, WorkerAgent]:
        """Create Worker agents (Tier 4) - multiple per Manager"""
        workers = {}

        for mgr in managers.values():
            worker_count = min(workers_per_manager, len(self.WORKER_TYPES))
            for i in range(worker_count):
                worker_type = self.WORKER_TYPES[i % len(self.WORKER_TYPES)]
                worker_id = f"{mgr.agent_id}-{worker_type}-{i+1}"
                worker = WorkerAgent(
                    agent_id=worker_id,
                    name=worker_id,
                    worker_type=worker_type,
                    category_id=mgr.category_id,
                    parent_agent_id=mgr.agent_id
                )
                self.agents[worker_id] = workers[worker_id] = worker

        return workers

    def create_all_agents(self) -> Dict[str, BaseAgent]:
        """Create the entire agent hierarchy"""
        # Tier 0: PRIME
        prime = self.create_prime()

        # Tier 1: C-Suite
        csuite = self.create_csuite()
        prime.csuite_agents = list(csuite.keys())

        # Tier 2: VPs
        vps = self.create_vps()

        # Tier 3: Managers
        managers = self.create_managers(vps)

        # Tier 4: Workers
        workers = self.create_workers(managers)

        # Set up parent-child relationships
        for vp in vps.values():
            vp.children = [m for m in managers if m.startswith(vp.name + "-")]
            vp.csuite_ref = csuite["CORTEX"]

        for mgr in managers.values():
            mgr.children = [w for w in workers if w.startswith(mgr.agent_id + "-")]

        csuite["CORTEX"].children = list(vps.keys())
        csuite["TREASURY"].vp_agents = list(vps.keys())
        csuite["SENTINEL"].vp_agents = list(vps.keys())

        return self.agents

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)

    def get_agents_by_tier(self, tier: int) -> List[BaseAgent]:
        """Get all agents at a specific tier"""
        return [a for a in self.agents.values() if a.tier == tier]

    def get_agents_by_status(self, status: AgentStatus) -> List[BaseAgent]:
        """Get all agents with a specific status"""
        return [a for a in self.agents.values() if a.status == status]

    def get_hierarchy_tree(self) -> Dict:
        """Build the full hierarchy tree for visualization"""

        def build_node(agent: BaseAgent) -> Dict:
            return {
                "id": agent.agent_id,
                "name": agent.name,
                "tier": agent.tier,
                "role": agent.role,
                "status": agent.status.value,
                "model": agent.model,
                "metrics": {
                    "tasks": agent.metrics.tasks_completed,
                    "success_rate": agent.success_rate
                },
                "children": [
                    build_node(self.agents[cid])
                    for cid in agent.children
                    if cid in self.agents
                ]
            }

        prime = self.agents.get("LUXOR-PRIME")
        if prime:
            return build_node(prime)
        return {}
