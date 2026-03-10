import random
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ale import IntentPredictor, PrecomputeEngine, MatchEngine


def simulate_round(precompute_enabled: bool) -> float:
    # synthetic latency model (ms)
    stt = random.randint(120, 220)
    retrieval = random.randint(180, 380)
    planning = random.randint(120, 260)
    generation = random.randint(220, 480)
    tts = random.randint(180, 340)

    if precompute_enabled:
        # Assume retrieval+planning partially precomputed
        retrieval = int(retrieval * random.uniform(0.35, 0.6))
        planning = int(planning * random.uniform(0.4, 0.7))

    return stt + retrieval + planning + generation + tts


def main():
    random.seed(42)
    rounds = 200

    baseline = [simulate_round(False) for _ in range(rounds)]
    ale = [simulate_round(True) for _ in range(rounds)]

    def p95(xs):
        xs = sorted(xs)
        return xs[int(0.95 * (len(xs) - 1))]

    print("Latency benchmark (synthetic)")
    print(f"baseline avg: {sum(baseline)/len(baseline):.1f}ms | p95: {p95(baseline)}ms")
    print(f"ALE avg:      {sum(ale)/len(ale):.1f}ms | p95: {p95(ale)}ms")


if __name__ == "__main__":
    main()
