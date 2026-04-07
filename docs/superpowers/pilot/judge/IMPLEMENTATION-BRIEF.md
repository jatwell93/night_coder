# Judge Pillar Implementation Brief

Decision reference: `dec-20260406-003`  
Selected approach: **OpenJudge** (`py-openjudge`)  
Context: overnight-pilot

## Goal

Provide an **external**, **headless** evaluator that reads **scenario markdown** plus **execution traces** and returns **structured scores** (`satisfied`, `score`, `reasoning`) so the coding agent cannot self-certify success.

## Scope

**In scope**

- `LLMGrader` with explicit `{scenario}` / `{trace}` (or equivalent) template inputs.
- `FunctionGrader` for deterministic checks (e.g. stdout format, exit semantics) composed with LLM grading.
- OpenAI-compatible model via OpenJudge’s model adapter; aligns with Model/Provider policy (`dec-20260406-006`) for judge role.
- Langfuse write-back via OpenJudge integration when Observability Phase 2 is live (optional in Phase 1).
- Dependencies: `py-openjudge` in `docs/superpowers/pilot/judge/requirements.txt` (or successor path).

**Out of scope**

- Dify-class platforms, AgentScope as the judge implementation (per decision rationale).
- Modifying scenario files or traces (judge is read-only consumer).

## Invariants (from decision)

- Output schema includes **satisfied** (bool), **score** (0–1), **reasoning** (string).
- Single scoring invocation: **under 60 seconds**, **under ~$0.10 AUD** per call at pilot targets (tune model accordingly).
- No Postgres/Redis/Celery required **for judging alone**.

## Checklist

1. `pip install py-openjudge` on Python 3.12+; verify `import openjudge`.
2. Replace or wrap `pilot_judge.py` to use `LLMGrader` + optional `FunctionGrader` (see long-form narrative in `DECISIONS.md`).
3. Keep **SCN-PILOT-001** (and paths) as the first parity scenario.
4. Add or extend tests (e.g. `test_pilot_judge_output.py`) with mocked grader.
5. Wire Langfuse export when tracing pipeline is ready (`dec-20260406-004`).

## Rollback

Revert to **build-yourself** `pilot_judge.py` + raw OpenAI SDK: remove `py-openjudge` from requirements. Triggers: package yanked, breaking API, or more than six months without maintenance (per `dec-20260406-003`).

## Links

- Canonical package: https://pypi.org/project/py-openjudge/  
- Docs: https://agentscope-ai.github.io/OpenJudge/  
- Full decision: `.quint/decisions/dec-20260406-003.md`
