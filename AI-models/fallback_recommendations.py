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

# Slightly bigger-budget alternatives, only used to pad out priorities for
# Small/Medium enterprises (never for Micro, which should stay free/near-zero-cost).
TIER_UPGRADE_TIPS = {
    "infrastructure": "Consider a paid cloud hosting/storage plan with stronger reliability guarantees",
    "process": "Invest in a lightweight business management tool instead of fully manual tracking",
    "people": "Bring in a part-time trainer for structured digital upskilling",
    "data": "Move to a managed cloud database service instead of spreadsheet-based records",
    "security": "Engage a professional to set up a formal cybersecurity policy",
}

# Generic padding tips, split by whether the business can likely absorb a
# small cost (Small/Medium) or should stay free-only (Micro).
GENERIC_FREE_TIPS = [
    "Continue maintaining your current digital practices",
    "Review your setup periodically as your business grows",
    "Consider light staff refreshers to keep digital skills current",
]


def get_fallback_recommendation(overall_score, maturity_level, gaps, business_type="Micro"):
    priorities = []

    # First pass: one free/low-cost tip per gap category, worst gap first.
    # These are appropriate for every tier, so they always come first.
    for gap in gaps[:3]:
        tips = FALLBACK_TIPS.get(gap, [])
        if tips:
            priorities.append(tips[0])

    # Second pass: if still short of 3, use each gap category's SECOND tip
    # (not the first one again) so we never repeat the same advice twice
    if len(priorities) < 3:
        for gap in gaps[:3]:
            tips = FALLBACK_TIPS.get(gap, [])
            if len(tips) > 1:
                priorities.append(tips[1])
            if len(priorities) >= 3:
                break

    # Third pass: for Small/Medium businesses with remaining gap categories,
    # offer the bigger-budget upgrade tip instead of a generic line - this is
    # what keeps the fallback consistent with the Bedrock prompt's tiering.
    if len(priorities) < 3 and business_type in ("Small", "Medium"):
        for gap in gaps:
            tip = TIER_UPGRADE_TIPS.get(gap)
            if tip and tip not in priorities:
                priorities.append(tip)
            if len(priorities) >= 3:
                break

    # Still short (e.g. no gaps at all - business is doing well, or a Micro
    # business with fewer than 3 gap categories)? Pad with generic, free-only tips.
    i = 0
    while len(priorities) < 3:
        priorities.append(GENERIC_FREE_TIPS[i % len(GENERIC_FREE_TIPS)])
        i += 1

    return {
        "summary": (
            f"Your business scored {overall_score}/100, placing it at {maturity_level}. "
            f"The areas needing the most attention are: "
            f"{', '.join(gaps) if gaps else 'none - strong across the board'}."
        ),
        "priorities": priorities[:3],
    }
