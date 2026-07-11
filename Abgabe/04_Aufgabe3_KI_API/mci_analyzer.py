"""
MCI-based production analyzer (Task 3).

Drop-in alternative to ``ProductionLLMAnalyzer`` that talks to the MCI account's
own REST API instead of OpenAI. It exposes the same async ``analyze()`` method
that ``LLMOptimizer`` expects, so it can be swapped in via a command line flag
without changing the optimizer or the simulation.

The REST interface mirrors the MCI example snippet:
    POST {base_url}/api/v1/llm/chat
    headers: X-Client-ID, X-Client-Secret
    body:    {"model", "messages", "temperature", "maxTokens"}
    reply:   data.content, data.usage.totalTokens

This module intentionally depends only on ``requests`` (not ``openai``), so the
MCI path works independently of the existing OpenAI integration.
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Optional

import requests

from .prompts import (
    PRODUCTION_ANALYSIS_PROMPT,
    PRODUCTION_DATA_TEMPLATE,
    SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = (
    "https://ca-backend-mciai-prod.mangoforest-0c569892."
    "swedencentral.azurecontainerapps.io"
)

# Models the MCI account accepts. Used only for a friendlier warning; the
# request is still sent so the server stays the source of truth.
KNOWN_MCI_MODELS = {"gpt-4o", "gpt-5.2", "gpt-5-nano", "o3", "Mistral-Large-3"}


class MCIRequestError(RuntimeError):
    """Raised when the MCI API returns a non-2xx response. Carries the body so
    the real reason (e.g. an invalid model name) is visible in logs."""

    def __init__(self, status_code: int, body: str):
        self.status_code = status_code
        self.body = body
        super().__init__(f"MCI API {status_code}: {body}")


class APIClient:
    """Thin wrapper around the MCI chat-completion REST endpoint."""

    def __init__(self, api_key: str, api_secret: str, base_url: str = DEFAULT_BASE_URL):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url

    def create_chat_completion(self, model: str, messages: List[Dict], **kwargs) -> Dict:
        url = f"{self.base_url}/api/v1/llm/chat"
        headers = {
            "X-Client-ID": self.api_key,
            "X-Client-Secret": self.api_secret,
            "Content-Type": "application/json",
        }
        payload = {"model": model, "messages": messages, **kwargs}
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if not response.ok:
            # Surface the server-provided error detail instead of a bare status.
            raise MCIRequestError(response.status_code, response.text)
        return response.json()


class MCIProductionAnalyzer:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: Optional[str] = None,
        model: str = "gpt-4o",
    ):
        self.client = APIClient(api_key, api_secret, base_url or DEFAULT_BASE_URL)
        self.model = model
        self.analysis_history: List[Dict] = []
        self.last_analysis_time: Optional[datetime] = None
        self.min_analysis_interval = 60  # seconds between LLM calls
        self.last_tokens_used = 0
        self.last_error: Optional[str] = None

        if model not in KNOWN_MCI_MODELS:
            logger.warning(
                f"LLM_MODEL '{model}' is not a known MCI model {sorted(KNOWN_MCI_MODELS)}. "
                "The MCI API will likely reject it with HTTP 400. "
                "Set MCI_MODEL (e.g. gpt-4o) in your .env."
            )

    def should_analyze(self, simulation_time: float) -> bool:
        """Only analyze if enough wall-clock time has passed since the last call."""
        if self.last_analysis_time is None:
            return True
        elapsed = (datetime.now() - self.last_analysis_time).total_seconds()
        return elapsed >= self.min_analysis_interval

    def format_production_data(self, data: Dict) -> str:
        """Render the raw process data dict into the compact prompt template."""
        machines_str = "\n".join(
            f"- {m['name']}: {m['status']}, Takt={m['cycle_time']}s, "
            f"Fehler={m['error_rate'] * 100:.1f}%, Produziert={m['produced']}, "
            f"OEE={m['oee']:.1f}%"
            for m in data["machines"]
        )
        buffers_str = "\n".join(
            f"- {b['name']}: Füllstand={b['fill_level']:.0f}%, "
            f"Kap={b['capacity']}, Überlauf={b['overflow']}"
            for b in data["buffers"]
        )
        kpis = data["kpis"]
        return PRODUCTION_DATA_TEMPLATE.format(
            machines=machines_str,
            buffers=buffers_str,
            raw_stock=data["raw_stock"],
            finished_stock=data["finished_stock"],
            oee=kpis["oee"],
            throughput=kpis["throughput"],
            scrap=kpis["scrap_rate"],
            utilization=kpis["utilization"],
        )

    def _call(self, messages: List[Dict]) -> Dict:
        return self.client.create_chat_completion(
            model=self.model,
            messages=messages,
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
            maxTokens=int(os.getenv("LLM_MAX_TOKENS", "1000")),
        )

    @staticmethod
    def _extract_json(content: str) -> Optional[Dict]:
        """Parse the model reply into a dict, tolerating markdown code fences
        (```json ... ```) or surrounding prose. The MCI API cannot force a JSON
        response format, so the model may wrap or annotate its answer.
        Returns None if no JSON object can be recovered."""
        text = (content or "").strip()
        if not text:
            return None
        # Strip a surrounding markdown code fence (``` or ```json).
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z0-9]*\s*", "", text)
            text = re.sub(r"\s*```$", "", text).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # Fall back: take the first {...} block found in the text.
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                return None
        return None

    async def analyze(self, simulation_data: Dict) -> Optional[Dict]:
        """Send process data to the MCI model; return the parsed recommendation."""
        if not self.should_analyze(simulation_data.get("simulation_time", 0)):
            logger.debug("Skipping MCI analysis - too soon")
            return None

        prompt = PRODUCTION_ANALYSIS_PROMPT.format(
            production_data=self.format_production_data(simulation_data)
        )
        # The MCI API only accepts the roles 'user' and 'assistant' (no
        # 'system'). Merge the system instructions into a single user message.
        messages = [{"role": "user", "content": f"{SYSTEM_PROMPT}\n\n{prompt}"}]

        try:
            response = self._call(messages)

            data_block = response.get("data", {})
            content = data_block.get("content", "")
            self.last_tokens_used = data_block.get("usage", {}).get("totalTokens", 0)

            analysis = self._extract_json(content)
            if analysis is None:
                snippet = (content or "").strip()[:200]
                self.last_error = (
                    f"Model did not return valid JSON. Raw content (truncated): {snippet!r}"
                )
                logger.error(self.last_error)
                return None

            self.analysis_history.append({
                "timestamp": datetime.now().isoformat(),
                "simulation_time": simulation_data.get("simulation_time", 0),
                "analysis": analysis,
                "tokens_used": self.last_tokens_used,
            })
            self.last_analysis_time = datetime.now()
            self.last_error = None
            logger.info(f"MCI analysis complete. Tokens used: {self.last_tokens_used}")
            return analysis

        except Exception as e:  # noqa: BLE001 - keep the simulation running
            self.last_error = str(e)
            logger.error(f"MCI analysis failed: {e}")
            return None
