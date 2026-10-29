# Verification registry

<!-- One row per thing that must keep working. Link to the brief's AC; never restate it. A bug fix always adds a row. With no test suite, the method is a manual or browser check and the evidence says what was seen. -->

| ID | Source | State | Level | Tags | Method | Input → expected | Evidence (date) |
| -- | ------ | ----- | ----- | ---- | ------ | ---------------- | --------------- |
| TEST-<AREA>-001 | <TICKET>/AC-001 | covered | browser | smoke | /path at 375 + desktop | <input> → <observable result> | <date>: seen, request body checked |

States: missing · in progress · unverified · covered · not applicable (say why).
Levels: unit · integration · api · browser · device · cli · manual (from the app type in `.bdt/dev/STACK.md`).
Tags: `smoke` (a main flow; run on every new build) · `regression` (run again when its area changes). The area is the `<AREA>` in the ID. An automated row names the test file in Method.
