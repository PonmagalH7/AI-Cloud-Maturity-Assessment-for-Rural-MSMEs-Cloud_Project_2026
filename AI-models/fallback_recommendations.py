FALLBACK_TIPS = {
    "infrastructure": [
        "Move critical business files to a cloud storage service with automatic backup",
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


def get_fallback_recommendation(overall_score, maturity_level, gaps):
    priorities = []

    # First pass: one tip per gap category, worst gap first
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

    # Still short (e.g. no gaps at all - business is doing well)? Give
    # distinct maintenance-style tips instead of repeating one generic line.
    generic_fallbacks = [
        "Continue maintaining your current digital practices",
        "Review your setup periodically as your business grows",
        "Consider light staff refreshers to keep digital skills current",
    ]
    i = 0
    while len(priorities) < 3:
        priorities.append(generic_fallbacks[i % len(generic_fallbacks)])
        i += 1

    return {
        "summary": (
            f"Your business scored {overall_score}/100, placing it at {maturity_level}. "
            f"The areas needing the most attention are: "
            f"{', '.join(gaps) if gaps else 'none - strong across the board'}."
        ),
        "priorities": priorities[:3],
    }
