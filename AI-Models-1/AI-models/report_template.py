import math
from datetime import datetime, timezone
from html import escape

from scoring import CATEGORY_LABELS, get_level_number

# Keyed by level NUMBER so renaming a level label can never silently break colours.
LEVEL_COLORS = {
    1: "#d9534f",
    2: "#f0ad4e",
    3: "#c9b52a",
    4: "#3a9fc4",
    5: "#4cae4c",
}

SHORT_LABELS = {
    "infrastructure": "Infrastructure",
    "process": "Process",
    "people": "People",
    "data": "Data",
    "security": "Security",
}


def _pct(value):
    """Clamp to 0-100 and return a float, so nothing odd can reach the markup."""
    try:
        return max(0.0, min(100.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def _num(value):
    """Format a score without trailing noise (60.5 -> 60.5, 60.0 -> 60)."""
    v = _pct(value)
    return str(int(v)) if v == int(v) else f"{v:.2f}".rstrip("0").rstrip(".")


def _category_rows(category_scores):
    rows = []
    for key, label in CATEGORY_LABELS.items():
        score = _pct(category_scores.get(key, 0))
        rows.append(f"""
        <tr>
          <td>{escape(label)}</td>
          <td class="bar-cell">
            <div class="bar-track">
              <div class="bar-fill" style="width:{score}%;"></div>
            </div>
          </td>
          <td class="score-cell">{_num(score)}</td>
        </tr>""")
    return "\n".join(rows)


def _radar_svg(category_scores):
    """Self-contained 5-axis radar chart (no external libraries, works offline/printed)."""
    keys = list(CATEGORY_LABELS)
    cx, cy, radius = 150, 135, 90
    n = len(keys)

    def point(i, fraction):
        angle = -math.pi / 2 + i * 2 * math.pi / n
        return cx + radius * fraction * math.cos(angle), cy + radius * fraction * math.sin(angle)

    grid = []
    for ring in (0.25, 0.5, 0.75, 1.0):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (point(i, ring) for i in range(n)))
        grid.append(f'<polygon points="{pts}" fill="none" stroke="#d5d9de" stroke-width="1"/>')
    spokes = [
        f'<line x1="{cx}" y1="{cy}" x2="{point(i, 1)[0]:.1f}" y2="{point(i, 1)[1]:.1f}" stroke="#d5d9de"/>'
        for i in range(n)
    ]
    data_pts = " ".join(
        f"{x:.1f},{y:.1f}"
        for x, y in (point(i, _pct(category_scores.get(k, 0)) / 100) for i, k in enumerate(keys))
    )
    labels = []
    for i, k in enumerate(keys):
        x, y = point(i, 1.22)
        labels.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-size="11" fill="#444" text-anchor="middle" '
            f'dominant-baseline="middle">{escape(SHORT_LABELS[k])}</text>'
        )
    return (
        '<svg viewBox="0 0 300 270" width="300" height="270" role="img" '
        'aria-label="Radar chart of the five category scores">'
        + "".join(grid + spokes)
        + f'<polygon points="{data_pts}" fill="rgba(79,140,255,0.28)" stroke="#4f8cff" stroke-width="2"/>'
        + "".join(labels)
        + "</svg>"
    )


def _priority_items(priorities):
    return "\n".join(f"<li>{escape(str(p))}</li>" for p in priorities)


def _next_level_block(next_level):
    if not next_level:
        return '<div class="biz">Top maturity level reached.</div>'
    return (
        f'<div class="biz">Next: {escape(str(next_level["level"]))} &middot; '
        f'score above {escape(str(next_level["scoreToExceed"]))} '
        f'({escape(_num(next_level["pointsToExceed"]))} more points needed)</div>'
    )


def _quick_wins_block(quick_wins):
    if not quick_wins:
        return ""
    rows = "\n".join(
        f"<tr><td>{escape(str(q['text']))}</td>"
        f"<td class='score-cell'>{escape(str(q['answer']))}/{escape(str(q['maxAnswer']))}</td>"
        f"<td class='score-cell'>+{float(q['gainPerStep']):.2f}</td></tr>"
        for q in quick_wins
    )
    return f"""
    <div class="section">
      <h2>Where the next points are</h2>
      <p class="note">Your current answer, and the points gained by improving it one step.</p>
      <table class="wins">
        <tr><th>Question</th><th>Now</th><th>Gain</th></tr>
        {rows}
      </table>
    </div>"""


def render_report_html(
    business_name,
    business_type,
    category_scores,
    overall_score,
    maturity_level,
    gaps,
    summary,
    priorities,
    assessment_id,
    next_level=None,
    quick_wins=None,
    source=None,
):
    level_color = LEVEL_COLORS.get(get_level_number(maturity_level), "#777777")
    generated_at = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    gaps_text = (
        ", ".join(escape(CATEGORY_LABELS.get(g, str(g))) for g in gaps)
        if gaps
        else "None - strong across all categories"
    )
    if source == "bedrock":
        source_note = "Explanation written by AI from your scores; every number comes from the scoring engine."
    elif source == "fallback":
        source_note = "Standard recommendations matched to your answers."
    else:
        source_note = ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cloud Maturity Assessment Report</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #f4f6f8; color: #222; }}
  .container {{ max-width: 760px; margin: 30px auto; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }}
  .header {{ background: #1f2937; color: #fff; padding: 28px 32px; }}
  .header h1 {{ margin: 0 0 4px 0; font-size: 22px; }}
  .header p {{ margin: 0; opacity: 0.8; font-size: 13px; }}
  .section {{ padding: 24px 32px; border-bottom: 1px solid #eee; }}
  .section h2 {{ font-size: 16px; margin: 0 0 14px 0; color: #1f2937; }}
  .score-hero {{ display: flex; align-items: center; gap: 24px; }}
  .score-circle {{ width: 90px; height: 90px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
                   font-size: 22px; font-weight: bold; color: #fff; background: {level_color}; flex-shrink: 0; }}
  .score-meta .level {{ font-size: 18px; font-weight: 600; color: {level_color}; margin-bottom: 2px; }}
  .biz {{ font-size: 13px; color: #666; margin-top: 2px; }}
  .chart {{ text-align: center; margin-bottom: 10px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  td, th {{ padding: 8px 4px; font-size: 13px; vertical-align: middle; text-align: left; }}
  .bar-cell {{ width: 55%; }}
  .bar-track {{ background: #e9ecef; border-radius: 6px; height: 10px; width: 100%; }}
  .bar-fill {{ background: #4f8cff; height: 10px; border-radius: 6px; }}
  .score-cell {{ text-align: right; width: 50px; font-weight: 600; }}
  .wins th {{ color: #666; font-weight: 600; border-bottom: 1px solid #eee; }}
  .wins th:not(:first-child) {{ text-align: right; }}
  .note {{ font-size: 12px; color: #777; margin: 10px 0 8px 0; }}
  .gaps {{ background: #fff3f3; border-left: 4px solid #d9534f; padding: 12px 16px; font-size: 13px; border-radius: 4px; }}
  .summary-text {{ font-size: 14px; line-height: 1.6; color: #333; }}
  ol {{ margin: 0; padding-left: 20px; font-size: 14px; line-height: 1.8; }}
  .footer {{ padding: 16px 32px; font-size: 11px; color: #999; text-align: center; }}
  @media print {{
    body {{ background: #fff; }}
    .container {{ box-shadow: none; margin: 0; max-width: none; }}
    .section {{ break-inside: avoid; }}
  }}
</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Cloud Maturity Assessment Report</h1>
      <p>{escape(str(business_name))} &middot; {escape(str(business_type))} &middot; Generated {generated_at}</p>
    </div>

    <div class="section">
      <h2>Overall Maturity</h2>
      <div class="score-hero">
        <div class="score-circle">{escape(_num(overall_score))}</div>
        <div class="score-meta">
          <div class="level">{escape(str(maturity_level))}</div>
          <div class="biz">Out of 100</div>
          {_next_level_block(next_level)}
        </div>
      </div>
    </div>

    <div class="section">
      <h2>Category Breakdown</h2>
      <div class="chart">{_radar_svg(category_scores)}</div>
      <table>
        {_category_rows(category_scores)}
      </table>
    </div>

    <div class="section">
      <h2>Critical Gaps</h2>
      <div class="gaps">{gaps_text}</div>
    </div>

    <div class="section">
      <h2>Summary</h2>
      <p class="summary-text">{escape(str(summary))}</p>
    </div>

    <div class="section">
      <h2>Recommended Roadmap</h2>
      <ol>
        {_priority_items(priorities)}
      </ol>
      <p class="note">{escape(source_note)}</p>
    </div>
{_quick_wins_block(quick_wins)}
    <div class="footer">
      Assessment ID: {escape(str(assessment_id))} &middot; AI Cloud Maturity Assessment for Rural MSMEs
    </div>
  </div>
</body>
</html>"""
