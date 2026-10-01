# Kukdi — Continuation & Handoff Map

> Orientation for a fresh Emergent session (connected via GitHub). This is a
> **map, not a manual** — it points you at the two ground-truth docs and records
> what's been built on top of the base so you can continue safely.

## Ground truth (read these first)
- **`HANDOFF.md`** — the architecture: stack, repo layout, data model, API
  reference, layer boundaries, platform rules, and **§13 "How to request changes"**.
- **`KUKDI_CONTEXT.md`** — the voice & feeling: who she is, Kukdi's personality,
  the calm/editorial design intent, the emotional job of each surface.
- **When the two conflict, the _feeling_ wins** (per KUKDI_CONTEXT.md §12): find a
  technical path that keeps Kukdi calm, warm, and quiet.

## What this app is
Kukdi is a calm, single-user "personal operating system" for one person ("Little
Miss", an ISB Mohali MBA targeting a Product Management offer). It absorbs mental
fragmentation — memories, companies, stories, people, calendar — and surfaces the
right thing at the right moment through an editorial, almost-invisible UI, with all
reasoning done by Claude Sonnet 4.6 via the Emergent universal LLM key. The
intelligence is the product; the interface should nearly disappear.

---

## Current state — what's been built on top of the base
All additive; existing flows/design/persona unchanged.

- **Day One Intake** (`/intake`) — a gentle first-run setup screen.
- **Prep-circle layer on People** — `prep_group` flag + `strengths` on people;
  `mock_sessions` collection and `/api/mocks` for logging mock interviews.
- **Reasoning nudge layer** — `prep_nudges` in `ai_engine.py`, `build_prep_context`
  in `context.py`, exposed via `/api/dream/nudges` (gentle, Kukdi-voiced).
- **Strength Matchmaking** — `suggested_peer` / `alternate_peers` added to
  `/api/stories/coverage` (pairs a story gap with a helpful prep-circle peer).
- **"Groundwork" placement hub** (`/groundwork`) — a HUB page that *surfaces and
  links* Dream Offer + Stories + a prep-circle **lens** (people where
  `prep_group == true`). It is NOT a merge of those pages — `/dream-offer`,
  `/stories`, `/people` remain intact standalone routes/components; the lens reads
  the single `people` collection (one source of truth) and refetches on navigation.
- **Nav/rename state** — see below.

## Rename mechanism (reversible, one line)
App identity is centralized in `frontend/src/components/Layout.jsx` as
`APP_NAME` / `APP_TAGLINE`. **Currently `"Kukdi"` / `"A Personal OS"`.** It was
temporarily flipped to `"North"` / `"Your Placement Companion"` for a scoped,
placement-only gift and flipped back — treat it as a **one-line flip** for
reversibility. (The browser tab `<title>` in `frontend/public/index.html` mirrors
the name.) Kukdi still refers to itself as "Kukdi" internally — do not touch
`ai_engine.py` / persona for a rename.

## Nav structure
- **Rail (desktop + mobile):** Home · Groundwork · Reflection · Calendar · People ·
  More, plus the standing **Talk to Kukdi** action.
- **More** (`/more`) indexes the secondary surfaces: **Day One Intake, Memory,
  Knowledge**.
- **Hidden-but-reachable** (routes/pages/helpers all intact, just not on the rail):
  **Dream Offer** (`/dream-offer`) and **Stories** (`/stories`) are reached via the
  Groundwork hub (and direct URL); Memory/Knowledge/Intake via More; Talk via its
  standing action. Nothing was deleted — only re-homed in the nav.

## Data-provisioning fix (critical — read before touching data)
`provision_real_data` in `backend/seed.py` runs on startup. It has been made
**idempotent and non-destructive**: it **never wipes or overwrites** — it inserts a
baseline item only if a doc with the same name (companies/people) or title
(stories/events) doesn't already exist, and it upserts the `settings` singleton
(preserving `home_state_override`). Existing user data always survives restarts
(verified across repeated restarts).

**Why this matters:** **MongoDB data does NOT travel through GitHub** — only the
provisioning *baseline* recreates core data on a fresh/empty DB. If you connect a
fresh environment, these are what get recreated:

- **14 companies (with tiers):**
  - _dream:_ Google, Microsoft, Amazon
  - _target:_ Flipkart, Myntra, Uber, Razorpay, Cisco, Qualcomm, Booking.com
  - _safe:_ Jio, Ola, Deloitte USI, Honeywell
- **12 prep candidates (all unconfirmed — `prep_group: false`, no strengths):**
  Shubhi, Devina, Sargam, Payas, Himagra, Rohan, Rasukh, Prem, Samparan, Shruthi,
  Pratham, Amol
- **4 draft stories:**
  1. "Doubling the Toastmasters budget"
  2. "Winning HACKOWASP with a contactless-shopping prototype"
  3. "Handling conflict in the OWASP chapter"
  4. "Teaching on mobile-only during COVID"
- _(Also currently in the baseline: 2 **tentative** calendar events — "Company
  registrations…" and "Interviews…". See Open Items: these are slated for removal.)_

> Do NOT re-introduce any wipe. Keep provisioning additive-only. The prep circle is
> intentionally empty/unconfirmed by design.

## Conventions reminder (full detail in HANDOFF.md §13)
- **Additive-only** unless a change explicitly says otherwise; minimal diffs.
- **Layer boundaries:** DB access in `routes/*`; **LLM logic only in `ai_engine.py`**
  (via a verb); cross-cutting query assembly in `context.py`; request models + fixed
  vocab in `models.py`; **frontend network only in `lib/api.js`**; shared UI via
  `components/Modal.jsx` primitives (`Field`, `inputClass`, `PrimaryButton`).
- **Platform rules:** every route under **`/api`**; frontend uses
  `REACT_APP_BACKEND_URL`; backend uses `MONGO_URL` / `DB_NAME`; **no hardcoded
  URLs/secrets**; **yarn, never npm**; **uuid string ids + ISO-8601 UTC datetimes +
  project out `_id`**; prefer **computed-on-read** over stored where it mirrors
  existing patterns.
- **`data-testid`** (kebab-case) on every new interactive/important element.
- **Scoped testing:** verify the touched flow + smoke-check the rest; don't full-regress.

## Design guardrails (from KUKDI_CONTEXT.md)
- Calm, editorial, magazine-quiet — **not** a SaaS dashboard.
- **No** dashboards, KPI grids, counters, badges, streaks, gamification.
- **No** red alerts / urgent banners / "you're behind" energy. Nudges are gentle grey
  lines, dismissable on hover.
- AI voice: **warm, brief prose** (2–3 sentences), **no emoji, no bullet lists**,
  feeling-first when it matters, never peppy or corporate.
- Enormous whitespace; serif (Cormorant) headings; uppercase muted micro-labels;
  slow deliberate motion. **Restraint is the feature — silence is allowed.**

---

## Known open items / next work (list — do NOT build here)

### Bugs
- **Tentative calendar events:** remove "Company registrations" and "Interviews" —
  they render far-future ("in 349 days") and are placeholders. Also **remove them
  from the provisioning baseline**. She'll add real dates.
- **"Polish with Kukdi" on a story hangs on "Polishing…":** needs a timeout + error
  handling + retry, with a calm failure state (no spinner-forever).
- **Home state dropdown (Quiet/Placement/Exam/etc.):** currently only updates the
  heading/subtext; the brief doesn't follow until a manual refresh. Make the brief
  follow the state (gently) — or reconsider whether a manual state-picker should
  exist at all (it's somewhat un-Kukdi; Kukdi should *detect* state).

### Reflection
- Remove the **"Sunday Reflection"** label — she can reflect any time; reword so it
  isn't day-bound.
- Add a way for **her to pen her own thoughts** about the week (her input, not just
  Kukdi's generated reflection).

### People
- **Edit details on each existing person** (same fields as "Add a person": name,
  relationship, company, birthday, notes) — today you can only set these at creation.
- **Add her non-ISB people:** Mom, Shrish (brother), Diya / Shruti (college friends),
  Vidip / Sarthak / Dhruv (office gang), Vanshiii (junior + co-founder), Gonu
  (maternal cousin), Dady (father).
- **Group people into areas** — Friends / Family / ISB — able to move people between
  areas and allow the same person in multiple areas. **Keep ONE `people` collection
  as source of truth** — areas are tags/views, not separate stores.
- **Reconnect nudge:** a gentle, Kukdi-voiced reminder to reconnect periodically
  ("it's been a while since you talked to Diya") — not an alert.

### Calendar
- Add a small **month calendar** on the page she can click to open a full month view
  with events.
- Let her **edit and add events** on that calendar.
