# Web research — gap wave 2 (April 2026)

## Source

Follow-up to [../research_report.md](../research_report.md) **§ Gaps and limitations** and **§ Suggested next experiments** (LocalStack, Browserless, OpenHands hardening).

## Questions (non-overlapping)

| # | File | Gap addressed |
|---|------|----------------|
| 1 | `findings_gap_dtu_localstack_browserless.md` | StrongDM DTU stack mentioned **LocalStack** + **Browserless** in prior notes but not researched: self-host, CI/agent integration, limits vs Mockoon/Keploy. |
| 2 | `findings_gap_openhands_production.md` | OpenHands **headless `always-approve`**: official security guidance, secrets, sandbox escape notes, VPS/systemd patterns, rate limits. |
| 3 | `findings_gap_openjudge_canonical.md` | **OpenJudge**: which GitHub org + PyPI package is canonical for `pip install`; ModelScope vs AgentScope relationship. |
| 4 | `findings_gap_opencode_ruflo_gastown.md` | **oh-my-opencode** vs **oh-my-openagent** (rename? archive?); **Ruflo** scheduler issue #1335 status; **Gas Town** #24 cost tracking resolution if any. |

## Synthesis

Merge into `research_report_gaps_wave2.md` in this folder: answers, remaining unknowns, recommended pins (package names, image tags).
