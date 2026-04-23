"""Application services — orchestrator, guardrails, judge, DTU, memory, telemetry.

Each service owns one responsibility and communicates through explicit interfaces.
Services may depend on ``src/lib`` utilities but must not import from ``src/cli``.
"""
