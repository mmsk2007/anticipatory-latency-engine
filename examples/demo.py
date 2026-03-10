import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ale import IntentPredictor, PrecomputeEngine, MatchEngine


def main():
    recent = [
        "We need faster voice replies",
        "Can we reduce latency for calls and messaging?",
        "Also keep X growth active",
    ]

    predictor = IntentPredictor()
    precompute = PrecomputeEngine(ttl_seconds=180)
    matcher = MatchEngine()

    candidates = predictor.predict(recent)
    print("Predicted intents:")
    for c in candidates:
        print(f"- {c.name}: {c.score:.2f}")

    precompute.precompute(candidates)

    # Simulate next user message arriving
    next_input = "Latency is still high in voice calls"
    chosen = matcher.match(next_input, candidates)
    pack = precompute.get(chosen)

    print("\nMatched intent:", chosen)
    print("Prebuilt context:", pack["context_pack"] if pack else None)


if __name__ == "__main__":
    main()
