# Architecture: Anticipatory Latency Engine (ALE)

## Problem
Most assistants wait for the user message, then start retrieval, planning, and tool prep. This adds avoidable latency.

## ALE approach
Predict likely next-turn intents and precompute safe context packs before user input arrives.

## Core components

1. Intent Forecaster
- Input: recent conversation turns + temporal signals
- Output: top-K intent hypotheses with confidence

2. Speculative Context Builder
- Creates context packs per hypothesis:
  - retrieval candidates
  - tool plans
  - partial response skeletons
- Strictly read-only precompute (no destructive side effects)

3. Online Matcher
- On real user input, matches to nearest hypothesis
- Reuses prebuilt pack if confidence and freshness pass thresholds

4. Finalizer
- Produces final response from matched pack
- Falls back to normal path if mismatch is high

5. Learning Loop
- Tracks hypothesis hit-rate
- Updates intent priors and confidence calibration

## Out-of-the-box ideas included

- Turn-level speculative execution (similar spirit to token speculation, but at intent level)
- TTL-governed context caching
- Confidence gating to prevent stale/wrong assumptions
- Adaptive budget: precompute only while idle windows exist

## Safety model

Allowed during precompute:
- retrieval
- embedding similarity
- read-only metadata lookups
- tool schema loading

Blocked during precompute:
- writes/deletes
- external side-effecting tool calls
- irreversible actions

## Latency model
Total latency = STT + retrieval + planning + tool prep + generation + TTS

ALE reduces: retrieval + planning + tool prep overlap by moving part of them before user turn.

## Metrics

- p50/p95 end-to-end latency
- perceived first-token latency
- hypothesis hit-rate
- wasted precompute ratio
- cost per successful response
