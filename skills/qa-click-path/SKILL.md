---
name: qa-click-path
description: Trace what every button and handler actually does to state, in order, to find bugs where a click "does nothing", saves silently fails, a filter resets, or two effects fight. Use for UI bugs with no error message, flaky state, forms that refuse to submit, or after changing shared state, query invalidation or effects.
---

# qa-click-path

**Input:** a page or flow and the symptom.
**Output:** `CLICK-PATH-NNN` findings with call traces and fixes, verified in the browser.

## Step 1: state map
For each store, context, form, query or hook involved: what each action **sets** and what it **resets** (including side effects: query invalidation, URL params, local storage, timers). One table per state owner.

## Step 2: trace each handler
For each interactive element on the page: the full call sequence from the event to the final state, with file:line. For a large page, split by section and trace in parallel subagents, each given the state map.

## Step 3: check against six patterns
1. **Sequential undo:** a later call resets what an earlier one set (for example a reset that runs after the set).
2. **Async race:** a slow response overwrites a newer one; no key or abort.
3. **Stale closure:** a handler or effect reads an old value.
4. **Missing transition:** a state the UI needs is never set (loading never ends, error never cleared).
5. **Dead path:** a branch that can never run, or a guard that always blocks (validation failing on a field with no visible error line).
6. **Effect interference:** an effect reacts to a change made by another effect or by a library (for example a select emitting an empty value while it registers options).

## Output
`CLICK-PATH-NNN`: element · pattern · call trace with file:line · expected vs actual · fix at the right layer · how to verify. Then a short list of handlers checked with no finding.

## Verify
Reproduce each finding in the browser before calling it real; for a form that silently refuses, inspect the form's error state for fields without an error line.
