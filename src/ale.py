from dataclasses import dataclass
from typing import List, Dict
import time


@dataclass
class IntentCandidate:
    name: str
    score: float


class IntentPredictor:
    """Simple baseline predictor from recent conversation signals."""

    def predict(self, recent_messages: List[str]) -> List[IntentCandidate]:
        text = " ".join(recent_messages).lower()
        candidates: List[IntentCandidate] = []

        if any(k in text for k in ["x", "twitter", "followers", "post"]):
            candidates.append(IntentCandidate("x_growth_update", 0.78))
        if any(k in text for k in ["repo", "project", "framework", "build"]):
            candidates.append(IntentCandidate("repo_planning", 0.73))
        if any(k in text for k in ["voice", "latency", "call", "reply faster"]):
            candidates.append(IntentCandidate("voice_latency_optimization", 0.81))

        if not candidates:
            candidates = [IntentCandidate("general_followup", 0.5)]

        return sorted(candidates, key=lambda c: c.score, reverse=True)[:3]


class PrecomputeEngine:
    """Build safe context packs for probable intents."""

    def __init__(self, ttl_seconds: int = 180):
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict] = {}

    def precompute(self, intents: List[IntentCandidate]) -> None:
        now = time.time()
        for intent in intents:
            self.cache[intent.name] = {
                "built_at": now,
                "expires_at": now + self.ttl_seconds,
                "intent": intent.name,
                "score": intent.score,
                "context_pack": self._build_context_pack(intent.name),
            }

    def _build_context_pack(self, intent: str) -> Dict:
        # Read-only prep only (no external side effects)
        if intent == "x_growth_update":
            return {"needs": ["latest followers", "recent posts", "growth KPI delta"]}
        if intent == "repo_planning":
            return {"needs": ["current project status", "next milestone", "repo queue"]}
        if intent == "voice_latency_optimization":
            return {"needs": ["pipeline latency budget", "stt/llm/tts timings", "fallback plan"]}
        return {"needs": ["recent context"]}

    def get(self, intent: str) -> Dict | None:
        item = self.cache.get(intent)
        if not item:
            return None
        if time.time() > item["expires_at"]:
            self.cache.pop(intent, None)
            return None
        return item


class MatchEngine:
    def match(self, user_input: str, candidates: List[IntentCandidate]) -> str:
        text = user_input.lower()
        for c in candidates:
            if "x" in text and "x_growth" in c.name:
                return c.name
            if "repo" in text and "repo" in c.name:
                return c.name
            if "latency" in text and "latency" in c.name:
                return c.name
        return candidates[0].name if candidates else "general_followup"
