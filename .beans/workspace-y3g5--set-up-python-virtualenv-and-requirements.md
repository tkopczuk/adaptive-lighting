---
# workspace-y3g5
title: Set up Python virtualenv and requirements
status: completed
type: task
priority: normal
created_at: 2026-05-02T10:48:06Z
updated_at: 2026-05-02T13:03:48Z
---

Create a local Python virtual environment and install the project requirements requested by the user.\n\n- [x] Create virtual environment\n- [x] Install requirements\n- [x] Run validation command

## Summary of Changes\n\nCreated and repaired .venv with pip, installed webapp requirements, installed uv and the Home Assistant test dependency set through scripts/setup-dependencies, cloned core at 2025.1.4 for Python 3.12 compatibility, and set up the test symlinks. Validation included pytest availability, focused Home Assistant tests, requirements reinstall, simulator import, and lint checks. The initial sandboxed pytest attempt hit an asyncio self-pipe permission issue, so the final pytest validation was rerun outside the sandbox.
