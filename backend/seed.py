"""Rich, handcrafted seed for Version One — built for Little Miss.

Idempotent: `seed(force=True)` wipes and rebuilds Kukdi's world so the very
first launch feels handcrafted rather than empty. Called on startup only when
the memory collection is empty.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone, date

from database import db
from models import COMPANY_STAGES, new_id, now_iso

COLLECTIONS = [
    "memories", "candidates", "conversations", "messages",
    "companies", "prep_items", "people", "events", "knowledge", "settings",
    "countdowns", "stories",
]


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _at(days: int, hour: int, minute: int = 0) -> str:
    base = datetime.now(timezone.utc) + timedelta(days=days)
    return _iso(base.replace(hour=hour, minute=minute, second=0, microsecond=0))


def _mem(type_, title, description, confidence=0.9, tags=None, usable_for=None):
    return {
        "id": new_id(),
        "type": type_,
        "title": title,
        "description": description,
        "confidence": confidence,
        "status": "active",
        "source": "seed",
        "relationships": [],
        "tags": tags or [],
        "usable_for": usable_for or [],
        "created": now_iso(),
        "updated": now_iso(),
        "last_confirmed": now_iso(),
    }


async def seed(force: bool = False) -> dict:
    # Demo seeding is permanently disabled for the real-user deployment. This
    # function is intentionally a no-op so neither startup nor POST /api/seed can
    # reintroduce demo content. Kept for history / potential future dev use only.
    return {"seeded": False, "reason": "demo seeding disabled"}


async def _seed_demo_DISABLED(force: bool = False) -> dict:
    if not force:
        existing = await db.memories.count_documents({})
        if existing:
            return {"seeded": False, "reason": "already populated"}

    for c in COLLECTIONS:
        await db[c].delete_many({})

    memories = [
        _mem("Profile", "Little Miss", "Little Miss is an MBA (PGP) student at ISB Mohali.", 1.0, ["identity"], ["home"]),
        _mem("Career", "Aiming for Product Management", "She wants to build a career in Product Management.", 1.0, ["career", "pm"], ["dream-offer"]),
        _mem("Goal", "Dream companies", "Her dream companies are Google, Microsoft, Adobe and MakeMyTrip.", 0.95, ["career"], ["dream-offer"]),
        _mem("Routine", "Morning person", "She does her best focused work in the mornings, though she tends to sleep late.", 0.85, ["energy"], ["home", "planning"]),
        _mem("Preference", "Running clears her head", "Going for a run helps her reset and lowers her stress.", 0.9, ["wellbeing", "running"], ["home"]),
        _mem("Habit", "Loves planning", "She feels calmer and more in control when she plans ahead.", 0.85, ["planning"], ["home"]),
        _mem("Insight", "Anxious under stress", "She gets anxious when under pressure, and can procrastinate before big tasks.", 0.8, ["wellbeing"], ["home"]),
        _mem("Insight", "Consistent once committed", "Once she commits to something she follows through reliably.", 0.85, ["strength"], ["home"]),
        _mem("Context", "Placements begin in November", "ISB placement season begins around November; preparation ramps up before then.", 0.9, ["placements"], ["dream-offer", "home"]),
        _mem("Preference", "Takes notes on iPad", "She prefers writing and reviewing notes on her iPad.", 0.8, ["study"], ["knowledge"]),
        _mem("Person", "Ananya", "Ananya is a close friend she wants to stay in touch with.", 0.8, ["people"], ["people"]),
    ]
    await db.memories.insert_many(memories)

    companies = [
        {"id": new_id(), "name": "Google", "tier": "dream", "role": "Associate Product Manager",
         "stage": "interviewing", "location": "Bangalore", "notes": "APM programme. Strong fit for her user-centric thinking.",
         "next_action": "Finish 2 product design cases this week", "created": now_iso(), "updated": now_iso()},
        {"id": new_id(), "name": "Microsoft", "tier": "dream", "role": "Product Manager",
         "stage": "applied", "location": "Hyderabad", "notes": "Applied via campus. Referral in progress.",
         "next_action": "Follow up with alum referral", "created": now_iso(), "updated": now_iso()},
        {"id": new_id(), "name": "Adobe", "tier": "dream", "role": "Product Manager",
         "stage": "researching", "location": "Noida", "notes": "Loves their design-led culture.",
         "next_action": "Read up on Adobe Express roadmap", "created": now_iso(), "updated": now_iso()},
        {"id": new_id(), "name": "MakeMyTrip", "tier": "target", "role": "Product Manager",
         "stage": "networking", "location": "Gurugram", "notes": "Travel product she uses and admires.",
         "next_action": "Connect with 2 ISB alumni there", "created": now_iso(), "updated": now_iso()},
    ]
    await db.companies.insert_many(companies)

    prep_items = [
        {"id": new_id(), "category": "roadmap", "title": "Product sense fundamentals", "content": "User empathy, problem framing, metrics.", "status": "done", "company_id": None, "created": now_iso(), "updated": now_iso()},
        {"id": new_id(), "category": "roadmap", "title": "Estimation & guesstimates", "content": "Market sizing structure and practice.", "status": "doing", "company_id": None, "created": now_iso(), "updated": now_iso()},
        {"id": new_id(), "category": "roadmap", "title": "Product design cases", "content": "CIRCLES-driven design rounds.", "status": "doing", "company_id": None, "created": now_iso(), "updated": now_iso()},
        {"id": new_id(), "category": "roadmap", "title": "Root cause & analytical cases", "content": "Metric drops, funnels, tradeoffs.", "status": "todo", "company_id": None, "created": now_iso(), "updated": now_iso()},
        {"id": new_id(), "category": "framework", "title": "CIRCLES", "content": "Comprehend, Identify customer, Report needs, Cut, List solutions, Evaluate, Summarise.", "status": "done", "company_id": None, "created": now_iso(), "updated": now_iso()},
        {"id": new_id(), "category": "framework", "title": "AARRR (Pirate metrics)", "content": "Acquisition, Activation, Retention, Referral, Revenue.", "status": "done", "company_id": None, "created": now_iso(), "updated": now_iso()},
        {"id": new_id(), "category": "framework", "title": "RICE prioritisation", "content": "Reach, Impact, Confidence, Effort.", "status": "done", "company_id": None, "created": now_iso(), "updated": now_iso()},
        {"id": new_id(), "category": "story", "title": "Led the ISB marketing club revamp", "content": "STAR: Situation, Task, Action, Result — a leadership story.", "status": "doing", "company_id": None, "created": now_iso(), "updated": now_iso()},
        {"id": new_id(), "category": "story", "title": "A decision I'd make differently", "content": "Reflective story showing growth and judgement.", "status": "todo", "company_id": None, "created": now_iso(), "updated": now_iso()},
        {"id": new_id(), "category": "case", "title": "Design a product for long-distance friendships", "content": "Practice design case.", "status": "todo", "company_id": None, "created": now_iso(), "updated": now_iso()},
        {"id": new_id(), "category": "resume", "title": "Tighten PM resume bullets", "content": "Quantify impact, lead with outcomes.", "status": "doing", "company_id": None, "created": now_iso(), "updated": now_iso()},
        {"id": new_id(), "category": "networking", "title": "Reach out to 3 ISB alumni in PM", "content": "Google, Microsoft, MakeMyTrip.", "status": "todo", "company_id": None, "created": now_iso(), "updated": now_iso()},
    ]
    await db.prep_items.insert_many(prep_items)

    people = [
        {"id": new_id(), "name": "Ananya", "relation": "Close friend", "company": "", "birthday": "March 14",
         "notes": "Her go-to person to decompress with. Was going through a stressful week recently.",
         "important": ["Call her back this week", "Her birthday is coming up"], "tags": ["friend"],
         "created": now_iso(), "updated": now_iso()},
        {"id": new_id(), "name": "Rohan Mehta", "relation": "ISB alum · Mentor", "company": "Google",
         "birthday": "", "notes": "APM at Google, generous with prep guidance.",
         "important": ["Owes him a thank-you note", "Can refer for Google"], "tags": ["mentor", "alum"],
         "created": now_iso(), "updated": now_iso()},
        {"id": new_id(), "name": "Prof. Nair", "relation": "Marketing professor", "company": "ISB",
         "birthday": "", "notes": "Teaches the marketing course with the upcoming case.",
         "important": ["Marketing case due soon"], "tags": ["faculty"], "created": now_iso(), "updated": now_iso()},
        {"id": new_id(), "name": "Mom", "relation": "Family", "company": "", "birthday": "August 2",
         "notes": "Calls on Sunday evenings. Worries when she doesn't hear from her.",
         "important": ["Sunday call"], "tags": ["family"], "created": now_iso(), "updated": now_iso()},
    ]
    await db.people.insert_many(people)

    events = [
        {"id": new_id(), "type": "class", "title": "Marketing Management", "start": _at(0, 9), "end": _at(0, 10, 30), "location": "AC-3", "course": "Marketing", "notes": "", "done": False, "created": now_iso()},
        {"id": new_id(), "type": "class", "title": "Competitive Strategy", "start": _at(0, 11), "end": _at(0, 12, 30), "location": "AC-1", "course": "Strategy", "notes": "", "done": False, "created": now_iso()},
        {"id": new_id(), "type": "deadline", "title": "Marketing case submission", "start": _at(1, 8), "end": None, "location": "", "course": "Marketing", "notes": "Prep the case tonight.", "done": False, "created": now_iso()},
        {"id": new_id(), "type": "class", "title": "Financial Accounting", "start": _at(1, 9), "end": _at(1, 10, 30), "location": "AC-2", "course": "Finance", "notes": "", "done": False, "created": now_iso()},
        {"id": new_id(), "type": "event", "title": "Morning run", "start": _at(1, 6), "end": _at(1, 7), "location": "Campus loop", "course": "", "notes": "Clears her head.", "done": False, "created": now_iso()},
        {"id": new_id(), "type": "placement", "title": "Google APM case round", "start": _at(3, 15), "end": _at(3, 16), "location": "Online", "course": "", "notes": "Product design case.", "done": False, "created": now_iso()},
        {"id": new_id(), "type": "exam", "title": "Statistics mid-term", "start": _at(6, 10), "end": _at(6, 12), "location": "Exam hall", "course": "Statistics", "notes": "", "done": False, "created": now_iso()},
    ]
    await db.events.insert_many(events)

    knowledge = [
        {"id": new_id(), "kind": "framework", "title": "CIRCLES method", "summary": "A structure for product design interview questions.", "body": "Comprehend the situation, Identify the customer, Report customer needs, Cut through prioritisation, List solutions, Evaluate tradeoffs, Summarise your recommendation.", "tags": ["pm", "framework"], "created": now_iso()},
        {"id": new_id(), "kind": "book", "title": "Inspired — Marty Cagan", "summary": "How great product teams work.", "body": "Notes on discovery, empowered teams and outcome over output.", "tags": ["pm", "book"], "created": now_iso()},
        {"id": new_id(), "kind": "note", "title": "Marketing case — key angles", "summary": "Segmentation, positioning, and the 4Ps for tomorrow's case.", "body": "Lead with the customer problem, then positioning, then the marketing mix.", "tags": ["marketing", "class"], "created": now_iso()},
    ]
    await db.knowledge.insert_many(knowledge)

    await db.settings.insert_one({"id": "singleton", "home_state_override": None, "updated": now_iso()})

    stories = [
        {"id": new_id(), "title": "Turning around the ISB Marketing Club",
         "situation": "The marketing club's flagship event had low turnout two years running and the team had lost momentum.",
         "task": "As the incoming lead I needed to rebuild engagement and deliver a signature event within one term.",
         "action": "I ran quick interviews with members to find what they actually wanted, repositioned the event around a live brand challenge, and split the team into small owned pods with clear deadlines.",
         "result": "Attendance grew roughly 3x versus the prior year and two sponsors signed on for the next edition.",
         "themes": ["leadership", "influence"], "tags": ["pm", "star"],
         "companies_used": ["Google"], "status": "polished", "feedback": "",
         "created": now_iso(), "updated": now_iso()},
        {"id": new_id(), "title": "A decision I'd make differently",
         "situation": "In a group project I pushed hard for a feature-rich prototype under time pressure.",
         "task": "We had to ship a working demo in ten days for a graded review.",
         "action": "I overloaded the scope and we spent too long polishing; I later cut features late and re-scoped around the core user need.",
         "result": "We delivered on time but I learned to define the smallest valuable slice first — I now start every plan with the one job to be done.",
         "themes": ["failure", "growth"], "tags": ["pm", "star"],
         "companies_used": [], "status": "draft", "feedback": "",
         "created": now_iso(), "updated": now_iso()},
    ]
    await db.stories.insert_many(stories)

    return {"seeded": True, "memories": len(memories), "companies": len(companies), "people": len(people)}



# ---------------------------------------------------------------------------
# Real-user provisioning: fill the baseline for a fresh/empty DB WITHOUT ever
# deleting or overwriting anything. Strictly additive and idempotent — each
# baseline item is inserted only if a document with the same name/title does
# not already exist. Safe to run on every startup; existing user data (stories,
# confirmations, prep-circle choices, settings) always survives a restart.
# ---------------------------------------------------------------------------

REAL_COMPANIES = [
    ("Google", "dream"), ("Microsoft", "dream"), ("Amazon", "dream"),
    ("Flipkart", "target"), ("Myntra", "target"), ("Uber", "target"),
    ("Razorpay", "target"), ("Cisco", "target"), ("Qualcomm", "target"),
    ("Booking.com", "target"),
    ("Jio", "safe"), ("Ola", "safe"), ("Deloitte USI", "safe"), ("Honeywell", "safe"),
]

REAL_PREP_CANDIDATES = [
    "Shubhi", "Devina", "Sargam", "Payas", "Himagra", "Rohan",
    "Rasukh", "Prem", "Samparan", "Shruthi", "Pratham", "Amol",
]

# Her 4 STAR story drafts — part of the baseline so a fresh DB has them too.
# Warm, in-voice action text; no square brackets. Shape matches /api/stories.
REAL_STORIES = [
    {
        "title": "Doubling the Toastmasters budget",
        "situation": "As a leader in Thapar Toastmasters, the club needed significantly more budget than the previous year to run a bigger slate of public-speaking events.",
        "task": "Convince the university authorities to approve a budget increase of over 100%.",
        "action": "Presented a clear vision of what public speaking at Thapar could look like that year and walked the authorities through the impact, winning their buy-in. — this part is yours to shape.",
        "result": "Secured a budget increase of more than 100% over the prior year.",
        "themes": ["Influence", "Execution"],
        "tags": ["Toastmasters", "leadership"],
    },
    {
        "title": "Winning HACKOWASP with a contactless-shopping prototype",
        "situation": "During the COVID-19 pandemic, HACKOWASP 2.1 brought together 15+ teams to solve real problems.",
        "task": "Design and build a user-centric solution that stood out.",
        "action": "Built a contactless-shopping interface prototype focused on the user experience of shopping safely during the pandemic. — this part is yours to shape.",
        "result": "Earned first position among 15+ teams.",
        "themes": ["Customer Focus", "Execution"],
        "tags": ["hackathon", "product"],
    },
    {
        "title": "Handling conflict in the OWASP chapter",
        "situation": "A miscommunication and conflict arose within the OWASP student chapter at Thapar.",
        "task": "Step in and resolve the situation while keeping the team functioning.",
        "action": "This is yours to shape — add what you did here, in your own words.",
        "result": "Resolved the conflict and kept the chapter on track.",
        "themes": ["Conflict", "Leadership"],
        "tags": ["OWASP", "teamwork"],
    },
    {
        "title": "Teaching on mobile-only during COVID",
        "situation": "While volunteering as a math tutor for underprivileged Class 9-10 students during COVID-19, students had access to phones only, under severe resource constraints.",
        "task": "Keep learning interactive and effective despite the constraints.",
        "action": "Innovated a low-cost DIY stylus and adapted problem-solving sessions to work on phones, improving engagement. — this part is yours to shape.",
        "result": "Sustained interactive learning over ~8 months for students who otherwise couldn't access it.",
        "themes": ["Ambiguity", "Customer Focus"],
        "tags": ["tutoring", "impact"],
    },
]


def _future_iso(month: int, day: int) -> str:
    """Next occurrence of month/day at 09:00 UTC (this year or next)."""
    today = datetime.now(timezone.utc).date()
    year = today.year
    if date(year, month, day) < today:
        year += 1
    return datetime(year, month, day, 9, 0, tzinfo=timezone.utc).isoformat()


# Calendar events are intentionally NOT provisioned — she adds her own real
# dates. (Previously held two tentative placeholder events; removed by design.)
REAL_EVENTS = []


async def provision_real_data(force: bool = False) -> dict:
    """Idempotent, strictly additive baseline fill. Never wipes or overwrites."""
    added = {"companies": 0, "people": 0, "stories": 0, "events": 0}
    default_stage = COMPANY_STAGES[0]  # earliest stage

    # Companies — insert only those whose name is not already present.
    existing_companies = set(await db.companies.distinct("name"))
    new_companies = [
        {
            "id": new_id(), "name": name, "tier": tier, "role": "",
            "stage": default_stage, "location": "", "notes": "", "next_action": "",
            "created": now_iso(), "updated": now_iso(),
        }
        for name, tier in REAL_COMPANIES
        if name not in existing_companies
    ]
    if new_companies:
        await db.companies.insert_many(new_companies)
        added["companies"] = len(new_companies)

    # Prep-circle candidates — unconfirmed by design (prep_group False).
    existing_people = set(await db.people.distinct("name"))
    new_people = [
        {
            "id": new_id(), "name": name, "relation": "Peer / prep group",
            "company": "", "birthday": "", "notes": "", "important": [], "tags": [],
            "prep_group": False, "prep_candidate": True,
            "strengths": [], "strength_note": "",
            "created": now_iso(), "updated": now_iso(),
        }
        for name in REAL_PREP_CANDIDATES
        if name not in existing_people
    ]
    if new_people:
        await db.people.insert_many(new_people)
        added["people"] = len(new_people)

    # Story drafts — insert only those whose title is not already present.
    existing_stories = set(await db.stories.distinct("title"))
    new_stories = [
        {
            "id": new_id(), "title": s["title"],
            "situation": s["situation"], "task": s["task"],
            "action": s["action"], "result": s["result"],
            "themes": s["themes"], "tags": s["tags"],
            "companies_used": [], "status": "draft", "feedback": "",
            "created": now_iso(), "updated": now_iso(),
        }
        for s in REAL_STORIES
        if s["title"] not in existing_stories
    ]
    if new_stories:
        await db.stories.insert_many(new_stories)
        added["stories"] = len(new_stories)

    # Tentative events — insert only those whose title is not already present.
    existing_events = set(await db.events.distinct("title"))
    new_events = [
        {
            "id": new_id(), "type": e["type"], "title": e["title"],
            "start": _future_iso(e["month"], e["day"]), "end": None,
            "location": "", "course": "", "notes": e["notes"],
            "done": False, "created": now_iso(),
        }
        for e in REAL_EVENTS
        if e["title"] not in existing_events
    ]
    if new_events:
        await db.events.insert_many(new_events)
        added["events"] = len(new_events)

    # Mark provisioned WITHOUT wiping the settings singleton (preserve any
    # home_state_override or other fields the user has set).
    await db.settings.update_one(
        {"id": "singleton"},
        {
            "$set": {"provisioned": True, "updated": now_iso()},
            "$setOnInsert": {"home_state_override": None},
        },
        upsert=True,
    )

    totals = {
        "companies": await db.companies.count_documents({}),
        "people": await db.people.count_documents({}),
        "stories": await db.stories.count_documents({}),
        "events": await db.events.count_documents({}),
    }
    return {"provisioned": True, "added": added, "totals": totals}
