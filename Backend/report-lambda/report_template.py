from datetime import datetime, timezone

MATURITY_COLORS = {
    "Level 1 - Initial": "#d9534f",
    "Level 2 - Developing": "#f0ad4e",
    "Level 3 - Defined": "#f0d84e",
    "Level 4 - Managed": "#5bc0de",
    "Level 5 - Optimized": "#5cb85c",
}

CATEGORY_LABELS = {
    "infrastructure": "Infrastructure & Technology",
    "process": "Processes & Digital Operations",
    "people": "People & Skills",
    "data": "Data Management",
    "security": "Security & Governance",
}


def _category_rows(category_scores):
    rows = []
    for key, label in CATEGORY_LABELS.items():
        score = category_scores.get(key, 0)
        rows.append(f"""
        <tr>
          <td>{label}</td>
          <td>
            <div class="bar-track">
              <div class="bar-fill" style="width:{score}%;"></div>
            </div>
          </td>
          <td class="score-cell">{score}</td>
        </tr>""")
    return "\n".join(rows)


def _priority_items(priorities):
    return "\n".join(f"<li>{p}</li>" for p in priorities)


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
):
    level_color = MATURITY_COLORS.get(maturity_level, "#777777")
    generated_at = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    gaps_text = ", ".join(CATEGORY_LABELS.get(g, g) for g in gaps) if gaps else "None - strong across all categories"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Cloud Maturity Assessment Report</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #f4f6f8; color: #222; }}
  .container {{ max-width: 760px; margin: 30px auto; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }}
  .header {{ background: #1f2937; color: #fff; padding: 28px 32px; }}
  .header h1 {{ margin: 0 0 4px 0; font-size: 22px; }}
  .header p {{ margin: 0; opacity: 0.8; font-size: 13px; }}
  .section {{ padding: 24px 32px; border-bottom: 1px solid #eee; }}
  .section:last-child {{ border-bottom: none; }}
  .section h2 {{ font-size: 16px; margin: 0 0 14px 0; color: #1f2937; }}
  .score-hero {{ display: flex; align-items: center; gap: 24px; }}
  .score-circle {{ width: 90px; height: 90px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
                   font-size: 22px; font-weight: bold; color: #fff; background: {level_color}; flex-shrink: 0; }}
  .score-meta .level {{ font-size: 18px; font-weight: 600; color: {level_color}; margin-bottom: 2px; }}
  .score-meta .biz {{ font-size: 13px; color: #666; }}
  table {{ width: 100%; border-collapse: collapse; }}
  td {{ padding: 8px 4px; font-size: 13px; vertical-align: middle; }}
  .bar-track {{ background: #e9ecef; border-radius: 6px; height: 10px; width: 100%; }}
  .bar-fill {{ background: #4f8cff; height: 10px; border-radius: 6px; }}
  .score-cell {{ text-align: right; width: 40px; font-weight: 600; }}
  .gaps {{ background: #fff3f3; border-left: 4px solid #d9534f; padding: 12px 16px; font-size: 13px; border-radius: 4px; }}
  .summary-text {{ font-size: 14px; line-height: 1.6; color: #333; }}
  ol {{ margin: 0; padding-left: 20px; font-size: 14px; line-height: 1.8; }}
  .footer {{ padding: 16px 32px; font-size: 11px; color: #999; text-align: center; }}
</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Cloud Maturity Assessment Report</h1>
      <p>{business_name} &middot; {business_type} &middot; Generated {generated_at}</p>
    </div>

    <div class="section">
      <h2>Overall Maturity</h2>
      <div class="score-hero">
        <div class="score-circle">{overall_score}</div>
        <div class="score-meta">
          <div class="level">{maturity_level}</div>
          <div class="biz">Out of 100</div>
        </div>
      </div>
    </div>

    <div class="section">
      <h2>Category Breakdown</h2>
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
      <p class="summary-text">{summary}</p>
    </div>

    <div class="section">
      <h2>Recommended Roadmap</h2>
      <ol>
        {_priority_items(priorities)}
      </ol>
    </div>

    <div class="footer">
      Assessment ID: {assessment_id} &middot; AI Cloud Maturity Assessment for Rural MSMEs
    </div>
  </div>
</body>
</html>"""
