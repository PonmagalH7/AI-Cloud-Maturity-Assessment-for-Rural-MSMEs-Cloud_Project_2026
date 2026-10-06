"""
Rules-based recommendations used when Bedrock is unavailable or returns
something we can't trust. Two modes:

1. Question-based (preferred): pass `weak_questions` from scoring and each tip
   is chosen from the exact answers that cost the business the most points.
2. Category-based (legacy): only `gaps` is known, so one tip per weak category.

Micro enterprises only ever get free / near-zero-cost tips.
"""
from scoring import CATEGORY_LABELS, MAX_ANSWER_VALUE

# One practical tip per question. "free" suits every business; "upgrade" is
# offered to Small/Medium businesses whose answer is already 2 or higher.
QUESTION_TIPS = {
    "infra_1": {
        "free": "Keep a mobile-hotspot backup plan so billing and orders continue when the main internet connection drops",
        "upgrade": "Add a second internet connection from a different provider, or a router that switches over automatically",
    },
    "infra_2": {
        "free": "Start with one free cloud tool, such as Google Drive or Google Sheets, for files you now keep on only one device",
        "upgrade": "Move one core process, such as billing or inventory, to a paid cloud application",
    },
    "infra_3": {
        "free": "List the three things your devices and tools make slow or difficult, and fix the one that wastes the most time first",
        "upgrade": "Have a local IT technician review your devices and network once and fix the biggest bottleneck",
    },
    "infra_4": {
        "free": "Choose tools with free tiers that can grow with you instead of keeping everything on one computer",
        "upgrade": "Move storage or hosting to a pay-as-you-grow cloud plan so capacity rises with demand",
    },
    "infra_5": {
        "free": "Set a monthly reminder to update your devices and apps and to clear files you no longer need",
        "upgrade": "Make a simple three-year plan for replacing computers and network equipment",
    },
    "process_1": {
        "free": "Pick one daily paper task, such as the sales or stock register, and move it to a spreadsheet or phone app",
        "upgrade": "Adopt one business app that covers daily sales, stock and customer records in one place",
    },
    "process_2": {
        "free": "Use a free billing or accounting app to record sales and expenses digitally",
        "upgrade": "Move to GST-ready accounting and inventory software that connects sales, stock and accounts",
    },
    "process_3": {
        "free": "Write your three most common daily workflows as short step-by-step checklists in a shared document",
        "upgrade": "Turn your key workflows into standard checklists in a shared tool so any staff member can follow them",
    },
    "process_4": {
        "free": "Use free automation such as WhatsApp Business quick replies, reminders and auto-calculating spreadsheet formulas",
        "upgrade": "Automate recurring tasks like invoicing, payment reminders and stock alerts in your business software",
    },
    "process_5": {
        "free": "Once a month, look at a simple chart of your sales or stock before deciding what to buy or promote",
        "upgrade": "Set up a monthly dashboard of sales, stock and cash that you review before big decisions",
    },
    "people_1": {
        "free": "Practise one new digital task each week with the staff member who is least comfortable, using tools you already have",
        "upgrade": "Run a short hands-on session on your core business tools for all staff",
    },
    "people_2": {
        "free": "Use free training videos in your own language for 30 minutes a week on the tools you use",
        "upgrade": "Book a part-time trainer or a short course on the tools your business relies on",
    },
    "people_3": {
        "free": "Choose one staff member as the go-to person for your cloud tools and let them learn first",
        "upgrade": "Train a staff member or hire part-time support to manage your cloud applications",
    },
    "people_4": {
        "free": "Set one small digital goal for this quarter, such as making all bills digitally, and review it every month",
        "upgrade": "Write a short digital plan with a named owner, a timeline and a small budget",
    },
    "people_5": {
        "free": "Introduce one new tool at a time and give staff a week to try it before adding another",
        "upgrade": "Pilot each new tool with one team first, collect feedback, then roll it out to everyone",
    },
    "data_1": {
        "free": "Photograph or scan your most important papers, such as invoices, licences and customer lists, and keep them in one folder",
        "upgrade": "Store business records in an organised digital system instead of loose files",
    },
    "data_2": {
        "free": "Set up automatic weekly backups of your most important files to free cloud storage",
        "upgrade": "Use an automatic daily cloud backup service and test restoring a file every quarter",
    },
    "data_3": {
        "free": "Keep business files in one shared cloud folder instead of spread across phones and computers",
        "upgrade": "Move to managed shared cloud storage or a database with separate access for each staff member",
    },
    "data_4": {
        "free": "Agree on one way to write customer names, product names and dates, and check records weekly for duplicates",
        "upgrade": "Use software that validates entries and flags duplicate or missing records",
    },
    "data_5": {
        "free": "Each month, review your best-selling and slowest-selling items from your records",
        "upgrade": "Use a simple reporting tool that turns your sales and stock data into charts automatically",
    },
    "security_1": {
        "free": "Give each person their own login, use strong unique passwords, and turn on two-step verification for email and payment accounts",
        "upgrade": "Use a business password manager and give staff access only to what their role needs",
    },
    "security_2": {
        "free": "Turn on automatic updates for phones, computers and apps",
        "upgrade": "Use a managed device service or IT technician to keep security updates current on every device",
    },
    "security_3": {
        "free": "Keep customer and payment details only where needed, protect those files with a password, and never share them in open chat groups",
        "upgrade": "Encrypt the devices and cloud storage that hold customer or financial data",
    },
    "security_4": {
        "free": "Write a one-page checklist for when something breaks: who to call, where backups are, and how to restore",
        "upgrade": "Create a recovery plan with a named owner and test it at least once a year",
    },
    "security_5": {
        "free": "Show staff examples of fake payment messages and phishing links, and agree never to share OTPs or passwords",
        "upgrade": "Run a short cybersecurity awareness session for staff twice a year",
    },
}

# Category-level tips, used only when per-question detail is not available.
FALLBACK_TIPS = {
    "infrastructure": [
        "Move critical business files to a free-tier cloud storage service with automatic backup",
        "Set up a basic scheduled maintenance check for business devices",
    ],
    "process": [
        "Document your top 3 daily workflows in a simple shared document",
        "Start using one free digital tool (e.g. spreadsheet-based tracking) for inventory or billing",
    ],
    "people": [
        "Run a short internal session to walk staff through the tools you already use",
        "Assign one staff member as the point of contact for basic tech issues",
    ],
    "data": [
        "Set up automatic weekly backups for your most important business data",
        "Start using a shared spreadsheet or basic database instead of paper records",
    ],
    "security": [
        "Turn on multi-factor authentication (MFA) for all business accounts",
        "Set a policy requiring strong, unique passwords across all business logins",
    ],
}

TIER_UPGRADE_TIPS = {
    "infrastructure": "Consider a paid cloud hosting/storage plan with stronger reliability guarantees",
    "process": "Invest in a lightweight business management tool instead of fully manual tracking",
    "people": "Bring in a part-time trainer for structured digital upskilling",
    "data": "Move to a managed cloud database service instead of spreadsheet-based records",
    "security": "Engage a professional to set up a formal cybersecurity policy",
}

# Used only when the business has nothing left to fix (all answers at maximum)
# or when there is no per-question detail at all.
MAINTAIN_TIPS = [
    "Review your cloud costs and usage every quarter to remove anything you no longer need",
    "Run a yearly test of restoring your backups to confirm they really work",
    "Share your digital practices with nearby businesses; teaching others strengthens your own processes",
]
GENERIC_FREE_TIPS = [
    "Continue maintaining your current digital practices",
    "Review your setup periodically as your business grows",
    "Consider light staff refreshers to keep digital skills current",
]


def _summary(overall_score, maturity_level, gaps):
    areas = ", ".join(CATEGORY_LABELS.get(g, g) for g in gaps) if gaps else "none - strong across the board"
    return (
        f"Your business scored {overall_score}/100, placing it at {maturity_level}. "
        f"The areas needing the most attention are: {areas}."
    )


def _pick_questions(weak_questions, gaps, count=3):
    """Choose `count` questions: best one from each gap category first, then biggest losses."""
    ranked = sorted(
        (q for q in weak_questions if q["answer"] < MAX_ANSWER_VALUE),
        key=lambda q: (-q["pointsLost"], q["id"]),
    )
    chosen = []
    for gap in gaps:
        for q in ranked:
            if q["category"] == gap and q not in chosen:
                chosen.append(q)
                break
        if len(chosen) >= count:
            return chosen
    for q in ranked:
        if q not in chosen:
            chosen.append(q)
        if len(chosen) >= count:
            break
    return chosen


def _tip_for(question, business_type):
    tips = QUESTION_TIPS[question["id"]]
    if business_type in ("Small", "Medium") and question["answer"] >= 2:
        return tips["upgrade"]
    return tips["free"]


def _question_based(overall_score, maturity_level, gaps, business_type, weak_questions):
    priorities = []
    for q in _pick_questions(weak_questions, gaps):
        tip = _tip_for(q, business_type)
        if tip not in priorities:
            priorities.append(tip)
    for tip in MAINTAIN_TIPS:
        if len(priorities) >= 3:
            break
        if tip not in priorities:
            priorities.append(tip)
    return {"summary": _summary(overall_score, maturity_level, gaps), "priorities": priorities[:3]}


def _category_based(overall_score, maturity_level, gaps, business_type):
    priorities = []
    for gap in gaps[:3]:
        tips = FALLBACK_TIPS.get(gap, [])
        if tips:
            priorities.append(tips[0])
    if len(priorities) < 3:
        for gap in gaps[:3]:
            tips = FALLBACK_TIPS.get(gap, [])
            if len(tips) > 1:
                priorities.append(tips[1])
            if len(priorities) >= 3:
                break
    if len(priorities) < 3 and business_type in ("Small", "Medium"):
        for gap in gaps:
            tip = TIER_UPGRADE_TIPS.get(gap)
            if tip and tip not in priorities:
                priorities.append(tip)
            if len(priorities) >= 3:
                break
    i = 0
    while len(priorities) < 3:
        priorities.append(GENERIC_FREE_TIPS[i % len(GENERIC_FREE_TIPS)])
        i += 1
    return {"summary": _summary(overall_score, maturity_level, gaps), "priorities": priorities[:3]}


def get_fallback_recommendation(
    overall_score, maturity_level, gaps, business_type="Micro", weak_questions=None
):
    """
    weak_questions: optional list of dicts from scoring (needs id, category,
    answer, pointsLost), e.g. result["questionBreakdown"]. When given, advice
    is tied to the exact answers that cost the most points.
    """
    if weak_questions:
        return _question_based(overall_score, maturity_level, gaps, business_type, weak_questions)
    return _category_based(overall_score, maturity_level, gaps, business_type)
