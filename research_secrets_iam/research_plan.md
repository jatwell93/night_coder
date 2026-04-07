# Secrets / IAM Pillar — Research Plan

## Question
How should API keys and provider auth be handled for overnight agents, with Doppler as a named candidate?

## Subtopics
1. **Doppler** — CLI injection, rotation, teams, agent/CI patterns.
2. **Alternatives** — 1Password CLI, Vault, SOPS, cloud secret managers, env-only baseline.
3. **Boundaries** — what never enters logs/traces; Ralph/OpenRouter/OpenJudge touchpoints.

## Synthesis
Primary + fallback + minimal pilot posture vs v1 hardening.
