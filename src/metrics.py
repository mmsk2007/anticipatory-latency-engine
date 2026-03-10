from dataclasses import dataclass, asdict
from typing import List, Dict


@dataclass
class TurnMetrics:
    predicted_intent: str
    matched_intent: str
    hit: bool
    precompute_ms: int
    baseline_latency_ms: int
    accelerated_latency_ms: int
    cost_units_baseline: float
    cost_units_accelerated: float


class MetricsTracker:
    def __init__(self) -> None:
        self.rows: List[TurnMetrics] = []

    def add(self, row: TurnMetrics) -> None:
        self.rows.append(row)

    def summary(self) -> Dict:
        if not self.rows:
            return {
                "turns": 0,
                "hit_rate": 0.0,
                "avg_baseline_ms": 0.0,
                "avg_accelerated_ms": 0.0,
                "latency_gain_ms": 0.0,
                "cost_delta_units": 0.0,
            }

        n = len(self.rows)
        hits = sum(1 for r in self.rows if r.hit)
        avg_b = sum(r.baseline_latency_ms for r in self.rows) / n
        avg_a = sum(r.accelerated_latency_ms for r in self.rows) / n
        avg_cb = sum(r.cost_units_baseline for r in self.rows) / n
        avg_ca = sum(r.cost_units_accelerated for r in self.rows) / n

        return {
            "turns": n,
            "hit_rate": hits / n,
            "avg_baseline_ms": round(avg_b, 2),
            "avg_accelerated_ms": round(avg_a, 2),
            "latency_gain_ms": round(avg_b - avg_a, 2),
            "cost_delta_units": round(avg_ca - avg_cb, 3),
        }

    def dump_rows(self) -> List[Dict]:
        return [asdict(r) for r in self.rows]
