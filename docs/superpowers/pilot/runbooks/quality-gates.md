# Quality gates — command matrix (pilot) — T006

Single source of truth for the lint, test, and type-check commands required by the project
constitution. All commands must pass before a task is marked complete (see `NFR-001 Code Quality`
in [`../../../../specs/001-overnight-vps-system/spec.md`](../../../../specs/001-overnight-vps-system/spec.md)).

**Baseline:** Python 3.12+, Bash. Checks run from the repository root unless stated otherwise.

---

## 1. Goals

| Concern | Goal |
|---------|------|
| **Consistency** | Every contributor (human or agent) runs the same checks the same way. |
| **Fail fast** | Lint/type errors are caught before tests; tests are caught before review. |
| **Explainable warnings** | No unexplained warnings — every `# noqa` or `# type: ignore` must have a reason. |
| **Story-scoped evidence** | Each user story maps to a test selector so verification is independently demonstrable. |

---

## 2. Command matrix

| Gate | Command | Scope | Fails on |
|------|---------|-------|----------|
| **Lint** | `ruff check .` | Repo root | Any unresolved lint rule. |
| **Format** | `ruff format --check .` | Repo root | Any unformatted file. |
| **Type-check** | `mypy src` | `src/` | Any type error (strict mode enabled in Phase 6). |
| **Unit tests** | `pytest tests/unit -q` | `tests/unit/` | Any failing or errored unit test. |
| **Integration tests** | `pytest tests/integration -q` | `tests/integration/` | Any failing integration scenario. |
| **Contract tests** | `pytest tests/contract -q` | `tests/contract/` | Any schema contract violation. |
| **Full suite** | `pytest -q` | All tests | Any failing test in any tier. |
| **Runbook validation** | Manual checklist per runbook | `docs/superpowers/pilot/runbooks/*.md` | Any unchecked validation item. |

> **Tooling setup:** dev dependencies are declared in `pyproject.toml` under
> `[project.optional-dependencies].dev`. Install once with:
>
> ```bash
> python3 -m venv .venv
> .venv/bin/pip install -e '.[dev]'
> ```
>
> Then either activate the venv (`source .venv/bin/activate`) or prefix commands with
> `.venv/bin/` (e.g. `.venv/bin/pytest -q`).

---

## 3. Story-scoped test selectors

Use these when validating a single user story's acceptance criteria.

| Story | Selector | Purpose |
|-------|----------|---------|
| **US1** | `pytest -q -k "us1 or guardrail or overnight"` | Safe overnight execution. |
| **US2** | `pytest -q -k "us2 or judge or verdict"` | External outcome-based judging. |
| **US3** | `pytest -q -k "us3 or dtu or memory or telemetry"` | DTU + memory continuous validation. |

Test files include the story tag in their name (`test_guarded_overnight_run.py`,
`test_judge_verdict_contract.py`, etc.) so the `-k` selector is stable.

---

## 4. Pre-commit and pre-PR checklist

Before committing:

```bash
ruff check .
ruff format --check .
pytest -q
```

Before opening a pull request, additionally:

```bash
mypy src tests
pytest tests/contract -q
```

Contract tests run last because they assert schema compatibility across components and are the
slowest to diagnose when failing.

---

## 5. Warning policy

- **No unexplained warnings.** Every suppression must carry a reason comment:

  ```python
  # noqa: E501  # Long URL in docstring — breaking would hurt readability.
  ```

  ```python
  # type: ignore[attr-defined]  # Third-party lib missing stubs (mcp-memory-service v0.4).
  ```

- **No blanket `# noqa`**. Always list the specific rule code(s).
- **No `# type: ignore` without a bracketed error code** once `mypy --strict` is active.

---

## 6. CI integration (planned)

CI is deferred until Phase 6 (T046–T048). Local enforcement via the commands above is the pilot
baseline. When CI lands, it will:

1. Run the full command matrix on every push.
2. Publish test coverage and lint summaries to the run artifact registry.
3. Block merge on any gate failure.

---

## 7. Validation checklist

Run through these before marking T006 complete.

- [x] `ruff check .` exits 0 on a clean checkout.
- [x] `ruff format --check .` exits 0 on a clean checkout.
- [x] `pytest -q` runs and passes the `src/` layout smoke test (`tests/unit/test_src_layout_smoke.py`).
- [x] `mypy src` exits 0 on a clean checkout.
- [x] `tests/unit/`, `tests/integration/`, `tests/contract/` exist (per T003–T005).
- [x] This document is linked from [`README.md`](./README.md).

---

## 8. References

- Feature constitution: [`../../../../specs/001-overnight-vps-system/plan.md`](../../../../specs/001-overnight-vps-system/plan.md) §Constitution Check.
- NFR-001 Code Quality: [`../../../../specs/001-overnight-vps-system/spec.md`](../../../../specs/001-overnight-vps-system/spec.md).
- Future: `verification-matrix.md` (T014) — feature-level quality/test matrix per component.
- Future: `verification-results.md` (T048) — recorded outcomes for the full matrix.
