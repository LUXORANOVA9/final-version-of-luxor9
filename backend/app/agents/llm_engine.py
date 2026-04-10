"""
LUXOR9 - LLM Fusion Engine
Centralized AI routing and fallback system.
Replaces the legacy Node.js router with internal Python orchestration.
"""
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, AsyncIterator
from functools import lru_cache
from pydantic import BaseModel

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq

logger = logging.getLogger("luxor9.fusion")

# ─── Token budgets per tier ────────────────────────────────
TIER_TOKEN_BUDGETS = {
    0: 4096,   # PRIME — large context for strategic decisions
    1: 3072,   # C-Suite — substantial for domain reasoning
    2: 2048,   # VPs — operational decisions
    3: 1024,   # Managers — task routing
    4: 512,    # Workers — simple execution
}

# ─── Model mapping per tier ────────────────────────────────
TIER_MODELS = {
    0: "gpt-4o",
    1: "gpt-4o",
    2: "gpt-4o-mini",
    3: "gpt-4o-mini",
    4: "gpt-4o-mini",
}

class LLMResponse(BaseModel):
    content: str
    provider: str
    model: str
    tokens_used: int = 0

class LLMFusionEngine:
    """
    The Fusion Engine handles multi-provider routing with automatic failover.
    It implements the logic previously handled by the external Node.js router.
    """
    def __init__(self, settings):
        self.settings = settings
        self._models: Dict[str, Any] = {}
        self._initialized = False
        self.fallback_chain = settings.FALLBACK_MODELS.split(",") if hasattr(settings, 'FALLBACK_MODELS') else ["openai", "anthropic", "groq"]

    def _ensure_init(self):
        """Lazy-init models only when first needed."""
        if self._initialized:
            return
        self._initialized = True

        # Initialize providers
        if self.settings.openai_api_key:
            try:
                self._models["openai"] = {
                    "gpt-4o": ChatOpenAI(model="gpt-4o", api_key=self.settings.openai_api_key, temperature=0.7),
                    "gpt-4o-mini": ChatOpenAI(model="gpt-4o-mini", api_key=self.settings.openai_api_key, temperature=0.7),
                }
                logger.info("✓ OpenAI provider initialized")
            except Exception as e:
                logger.warning(f"OpenAI init failed: {e}")

        if self.settings.anthropic_api_key:
            try:
                self._models["anthropic"] = {
                    "gpt-4o": ChatAnthropic(model="claude-3-5-sonnet-20241022", api_key=self.settings.anthropic_api_key, temperature=0.7),
                    "gpt-4o-mini": ChatAnthropic(model="claude-3-haiku-20240307", api_key=self.settings.anthropic_api_key, temperature=0.7),
                }
                logger.info("✓ Anthropic provider initialized")
            except Exception as e:
                logger.warning(f"Anthropic init failed: {e}")

        if self.settings.groq_api_key:
            try:
                self._models["groq"] = {
                    "gpt-4o": ChatGroq(model="llama-3.1-70b-versatile", api_key=self.settings.groq_api_key, temperature=0.7),
                    "gpt-4o-mini": ChatGroq(model="llama-3.1-8b-instant", api_key=self.settings.groq_api_key, temperature=0.7),
                }
                logger.info("✓ Groq provider initialized")
            except Exception as e:
                logger.warning(f"Groq init failed: {e}")

    def get_model_for_tier(self, tier: int, provider: str = None):
        """
        Retrieves the appropriate model for a tier from a specific provider,
        or falls back to the primary provider.
        """
        self._ensure_init()
        model_name = TIER_MODELS.get(tier, "gpt-4o-mini")

        # If no provider specified, use the first one in the fallback chain
        if not provider:
            provider = self.fallback_chain[0] if self.fallback_chain else "openai"

        provider_models = self._models.get(provider)
        if provider_models:
            return provider_models.get(model_name)
        return None

    async def reason(self, agent, prompt: str, tools: Optional[List[BaseTool]] = None) -> Dict[str, Any]:
        """
        The core reasoning loop with automatic provider failover.
        """
        self._ensure_init()

        # Try each provider in the fallback chain
        for provider_name in self.fallback_chain:
            try:
                model = self.get_model_for_tier(agent.tier, provider=provider_name)
                if model is None:
                    continue

                messages = [
                    SystemMessage(content=agent.personality),
                    HumanMessage(content=self._build_context(agent, prompt)),
                ]

                if tools:
                    model_with_tools = model.bind_tools(tools)
                    response = await model_with_tools.ainvoke(messages)
                    if response.tool_calls:
                        return await self._execute_tool_calls(agent, model_with_tools, messages, response, tools)
                else:
                    response = await model.ainvoke(messages)

                # Token tracking
                token_count = 0
                if hasattr(response, "usage_metadata") and response.usage_metadata:
                    token_count = response.usage_metadata.get("total_tokens", 0)
                if token_count and hasattr(agent, "metrics"):
                    agent.metrics.tokens_used += token_count

                return self._parse_response(response.content, agent)

            except Exception as e:
                logger.error(f"[{agent.agent_id}] Provider {provider_name} failed: {e}")
                continue

        return self._stub_response(agent, prompt)

    async def stream_reason(self, agent, prompt: str, tools: Optional[List[BaseTool]] = None) -> AsyncIterator[str]:
        """Streaming version with fallback support."""
        self._ensure_init()

        for provider_name in self.fallback_chain:
            try:
                model = self.get_model_for_tier(agent.tier, provider=provider_name)
                if model is None:
                    continue

                messages = [
                    SystemMessage(content=agent.personality),
                    HumanMessage(content=self._build_context(agent, prompt)),
                ]

                if tools:
                    model_with_tools = model.bind_tools(tools)
                    async for chunk in model_with_tools.astream(messages):
                        if hasattr(chunk, "content") and chunk.content:
                            yield chunk.content
                    return # Exit after first successful provider
                else:
                    async for chunk in model.astream(messages):
                        if hasattr(chunk, "content") and chunk.content:
                            yield chunk.content
                    return # Exit after first successful provider

            except Exception as e:
                logger.error(f"[{agent.agent_id}] Streaming error via {provider_name}: {e}")
                continue

        yield "⚠ No LLM provider available - simulation mode"

    def _build_context(self, agent, prompt: str) -> str:
        memory_window = min(len(agent.memory), 5 + (4 - agent.tier) * 3)
        recent_memory = agent.memory[-memory_window:] if agent.memory else []
        context_parts = [prompt]
        if recent_memory:
            context_parts.append("\n--- RECENT MEMORY ---")
            for entry in recent_memory:
                entry_type = entry.get("type", "unknown")
                if entry_type == "sent":
                    msg = entry.get("msg", {})
                    context_parts.append(f"[SENT to {msg.get('to_agent_id', '?')}] {msg.get('type', '?')}: {json.dumps(msg.get('payload', {}))[:200]}")
                elif "msg" in entry:
                    msg = entry.get("msg", {})
                    context_parts.append(f"[{entry_type.upper()}] {json.dumps(msg)[:200]}")
        context_parts.append(f"\n--- AGENT STATE ---\nTasks completed: {agent.metrics.tasks_completed} | Success rate: {agent.success_rate:.1f}% | Revenue: ${agent.metrics.revenue_generated:.2f}")
        return "\n".join(context_parts)

    def _parse_response(self, content: str, agent) -> Dict:
        try:
            cleaned = content.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                cleaned = "\n".join(lines[1:-1])
            return json.loads(cleaned)
        except (json.JSONDecodeError, ValueError):
            try:
                start = content.index("{")
                end = content.rindex("}") + 1
                return json.loads(content[start:end])
            except (ValueError, json.JSONDecodeError):
                return {"raw_response": content, "decisions": [], "directives": [], "alerts": []}

    async def _execute_tool_calls(self, agent, model, messages, ai_response, tools) -> Dict:
        from langchain_core.messages import ToolMessage
        tool_map = {t.name: t for t in tools}
        results = []
        for tool_call in ai_response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool = tool_map.get(tool_name)
            if tool:
                try:
                    result = tool.invoke(tool_args)
                    results.append({"tool": tool_name, "args": tool_args, "result": result})
                except Exception as e:
                    results.append({"tool": tool_name, "error": str(e)})
        messages.append(ai_response)
        for i, tool_call in enumerate(ai_response.tool_calls):
            result_str = json.dumps(results[i]) if i < len(results) else "{}"
            messages.append(ToolMessage(content=result_str, tool_call_id=tool_call["id"]))
        final_response = await model.ainvoke(messages)
        parsed = self._parse_response(final_response.content, agent)
        parsed["tool_results"] = results
        return parsed

    def _stub_response(self, agent, prompt: str) -> Dict:
        return {"decisions": [], "directives": [], "alerts": [], "status": "stub", "note": f"Simulation mode for {agent.name}."}

_engine: Optional[LLMFusionEngine] = None

def get_engine() -> LLMFusionEngine:
    global _engine
    if _engine is None:
        from app.config import get_settings
        _engine = LLMFusionEngine(get_settings())
    return _engine

@lru_cache()
def get_engine_for_settings(settings) -> LLMFusionEngine:
    return LLMFusionEngine(settings)
