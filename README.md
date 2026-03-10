# Anticipatory Latency Engine (ALE)

A framework for **predicting likely next user intents before the user sends the next message**, so voice and messaging agents can pre-build context/tools and respond faster.

## Why this exists

LLMs predict next tokens inside a message.
ALE predicts the **next user move across turns**.

This enables:

- prefetching relevant memory/docs
- pre-warming tool calls
- drafting likely responses in advance
- reducing perceived latency in voice/messaging

## Core idea

Given conversation history, generate top-K probable next intents with confidence scores, then run safe precomputation for the top candidates.

## MVP scope

- Intent predictor (heuristic + optional LLM scoring)
- Context prebuilder (memory/docs/tool plan)
- Latency-aware cache (TTL-based)
- Runtime selector (on actual user message, pick best prebuilt context)

## Fast architecture

1. `ConversationState` captures recent turns + metadata.
2. `IntentPredictor` outputs top intents.
3. `PrecomputeEngine` prepares context packs for each intent.
4. `MatchEngine` maps real user input to nearest predicted intent.
5. `ResponseEngine` reuses prebuilt pack and finalizes response.

## Safety constraints

- Never execute destructive actions during precompute.
- Only allow read-only or reversible tool warmups.
- Expire predictions quickly (TTL) to avoid stale assumptions.

## Run demo

```bash
python3 examples/demo.py
```

## Research directions

- online learning from accepted/rejected predictions
- personalization by user style/time/location
- multi-modal anticipatory prediction (voice + chat + calendar context)

## Positioning

This is a core building block for agentic systems that feel instant.
