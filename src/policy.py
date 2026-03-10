from dataclasses import dataclass


@dataclass
class PrecomputePolicy:
    confidence_threshold: float = 0.65
    max_candidates: int = 2
    budget_per_turn_units: float = 1.0
    ttl_seconds: int = 180


class BudgetController:
    def __init__(self, policy: PrecomputePolicy):
        self.policy = policy

    def allow(self, confidence: float, estimated_cost_units: float) -> bool:
        if confidence < self.policy.confidence_threshold:
            return False
        if estimated_cost_units > self.policy.budget_per_turn_units:
            return False
        return True
