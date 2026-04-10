"""LUXOR9 - CEO Agent Persistent Memory Storage"""
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger("luxor9.ceo_memory")


class CEOMemory:
    """
    Persistent memory storage for CEO Agent context.
    Stores conversation history, preferences, and business context.
    """

    def __init__(self, storage_path: str = "/root/luxor9/data/ceo_memory.json"):
        self.storage_path = storage_path
        self.data: Dict = self._load()

    def _load(self) -> Dict:
        """Load memory from disk"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load CEO memory: {e}")

        return {
            "conversations": [],
            "preferences": {},
            "business_context": {},
            "tasks": [],
            "insights": [],
            "last_updated": None
        }

    def _save(self):
        """Save memory to disk"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self.data["last_updated"] = datetime.utcnow().isoformat()

        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save CEO memory: {e}")

    def add_conversation(self, role: str, content: str, metadata: Dict = None):
        """Add a human-AI conversation message"""
        message = {
            "id": len(self.data["conversations"]) + 1,
            "role": role,  # "human" or "ai"
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self.data["conversations"].append(message)

        # Keep only last 100 conversations
        if len(self.data["conversations"]) > 100:
            self.data["conversations"] = self.data["conversations"][-100:]

        self._save()

    def get_conversations(self, limit: int = 20) -> List[Dict]:
        """Get recent conversation history"""
        return self.data["conversations"][-limit:]

    def get_context_for_llm(self) -> str:
        """Get formatted context for LLM prompts"""
        recent = self.get_conversations(10)

        context_parts = ["=== RECENT CONVERSATIONS ==="]
        for msg in recent:
            role = msg["role"].upper()
            content = msg["content"][:200]  # Truncate long messages
            context_parts.append(f"[{role}]: {content}")

        if self.data.get("business_context"):
            context_parts.append("\n=== BUSINESS CONTEXT ===")
            for key, value in self.data["business_context"].items():
                context_parts.append(f"{key}: {value}")

        return "\n".join(context_parts)

    def set_preference(self, key: str, value: Any):
        """Set a user preference"""
        self.data["preferences"][key] = value
        self._save()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference"""
        return self.data["preferences"].get(key, default)

    def add_task(self, task: Dict):
        """Add a task to memory"""
        task["created_at"] = datetime.utcnow().isoformat()
        self.data["tasks"].append(task)
        self._save()

    def get_tasks(self, status: str = None) -> List[Dict]:
        """Get tasks, optionally filtered by status"""
        if status:
            return [t for t in self.data["tasks"] if t.get("status") == status]
        return self.data["tasks"]

    def update_task(self, task_id: str, updates: Dict):
        """Update a task"""
        for task in self.data["tasks"]:
            if task.get("id") == task_id:
                task.update(updates)
                break
        self._save()

    def add_insight(self, insight: str, category: str = "general"):
        """Add a business insight"""
        self.data["insights"].append({
            "text": insight,
            "category": category,
            "timestamp": datetime.utcnow().isoformat()
        })
        # Keep last 50 insights
        if len(self.data["insights"]) > 50:
            self.data["insights"] = self.data["insights"][-50:]
        self._save()


# Singleton instance
_ceo_memory: Optional[CEOMemory] = None


def get_ceo_memory() -> CEOMemory:
    """Get or create CEO memory singleton"""
    global _ceo_memory
    if _ceo_memory is None:
        _ceo_memory = CEOMemory()
    return _ceo_memory