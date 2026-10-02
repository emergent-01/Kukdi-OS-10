# Plan: Mark two shipped fixes as done in CONTINUATION.md

A documentation-only edit to the existing CONTINUATION.md handoff file. It marks
the two bugs that were just fixed as resolved, in place, so the next session sees
they're done — nothing else in the doc changes.

## Who it's for
A fresh session (or person) picking up the project via the CONTINUATION.md handoff
map, who needs to know which open items have already been handled.

## Scope of the change
In the "Known open items / next work" list, under **Bugs**, the following two
items are marked as done (left in place, not removed):

1. **Tentative calendar events** — the item describing the "Company registrations"
   and "Interviews" placeholder events that rendered far-future and were to be
   removed from both the data and the provisioning baseline.
2. **"Polish with Kukdi" hangs** — the item describing the story polish action that
   could hang indefinitely on "Polishing…" and needed a timeout, error handling,
   and a calm retry state.

Each will keep its original wording, with a clear "done" marker added (for example
a `~~strikethrough~~` of the text plus a short `✅ Done` tag) so the history of what
was asked stays readable while the status is obvious.

## What is intentionally NOT changed
Per the decision to touch only the two fixed items:

- The provisioning-baseline note that still reads "2 tentative events currently in
  baseline, slated for removal" is **left as-is** (not corrected to "events = none").
- The remaining **Calendar** open items ("add a month calendar", "edit/add events")
  stay as open work.
- All other sections — the ground-truth pointers, current-state summary, rename
  mechanism, nav structure, conventions, design guardrails, and every other open
  item (Home state, Reflection, People) — are untouched.

## How it reads after the edit
The two Bugs entries visibly show as completed, while the rest of the open-items
list and the whole remainder of the document remain exactly as they are today.

## Implementation phases
- **Phase 1 (now, MVP):** Mark the two fixed bug items as done in place in
  CONTINUATION.md. No other edits.
- **Phase 2 (later, not now):** A broader accuracy pass to refresh any other
  now-stale lines (e.g. the provisioning-baseline events note), if desired.
- **Phase 3 (later, not now):** Move completed items into a dedicated
  "Recently resolved" / changelog section if the open-items list grows long.

## Assumptions
- "This" refers to the two fixes completed in the previous turn (tentative
  calendar events removed from DB + baseline; Polish with Kukdi made robust with
  a timeout, graceful failure, and retry).
- Done items are kept in the "Open items" list with a done marker, not deleted and
  not moved to a changelog (per the choice made).
- Only these two items are edited; every other line, including the known-stale
  baseline note, is left unchanged (per the choice made).
- The done marker will be a strikethrough of the existing text plus a short `✅ Done`
  tag; original wording is preserved for traceability.
- No code, data, or behavior changes — this is a single edit to one Markdown file.
