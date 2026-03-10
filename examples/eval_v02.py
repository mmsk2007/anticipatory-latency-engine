import os
import sys
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ale import IntentPredictor, PrecomputeEngine, MatchEngine
from src.metrics import MetricsTracker, TurnMetrics
from src.policy import PrecomputePolicy, BudgetController


def synthetic_latency(hit: bool):
    # baseline path
    baseline = random.randint(950, 1600)
    # accelerated path: if hit, strong gain; if miss, slight overhead
    if hit:
        accelerated = int(baseline * random.uniform(0.68, 0.84))
    else:
        accelerated = int(baseline * random.uniform(0.97, 1.08))
    return baseline, accelerated


def synthetic_cost(hit: bool, precomputed: bool):
    base = random.uniform(1.0, 1.4)
    extra = random.uniform(0.08, 0.24) if precomputed else 0.0
    # successful hit tends to reduce downstream planning cost slightly
    downstream_saving = random.uniform(0.06, 0.18) if hit else 0.0
    return base, max(0.1, base + extra - downstream_saving)


def main():
    random.seed(7)
    predictor = IntentPredictor()
    matcher = MatchEngine()
    policy = PrecomputePolicy(confidence_threshold=0.66, max_candidates=2, budget_per_turn_units=0.22, ttl_seconds=180)
    budget = BudgetController(policy)
    precompute = PrecomputeEngine(ttl_seconds=policy.ttl_seconds)
    metrics = MetricsTracker()

    scenarios = [
        (["Need faster voice response", "latency is too high"], "voice call still slow"),
        (["post on X", "followers goal"], "what is our follower growth"),
        (["new repo", "agent framework"], "what next repo should we build"),
        (["market", "bitcoin signals"], "do we have crypto update"),
        (["voice ai", "call lag"], "reduce call delay"),
    ] * 25

    for recent, incoming in scenarios:
        cands = predictor.predict(recent)

        selected = []
        for c in cands[: policy.max_candidates]:
            est_cost = random.uniform(0.08, 0.25)
            if budget.allow(c.score, est_cost):
                selected.append(c)

        did_precompute = len(selected) > 0
        if did_precompute:
            precompute.precompute(selected)

        predicted_intent = selected[0].name if selected else cands[0].name
        matched = matcher.match(incoming, cands)
        hit = predicted_intent == matched

        b_ms, a_ms = synthetic_latency(hit)
        cb, ca = synthetic_cost(hit, did_precompute)

        metrics.add(
            TurnMetrics(
                predicted_intent=predicted_intent,
                matched_intent=matched,
                hit=hit,
                precompute_ms=random.randint(40, 130) if did_precompute else 0,
                baseline_latency_ms=b_ms,
                accelerated_latency_ms=a_ms,
                cost_units_baseline=cb,
                cost_units_accelerated=ca,
            )
        )

    print("ALE v0.2 evaluation")
    print(metrics.summary())


if __name__ == "__main__":
    main()
