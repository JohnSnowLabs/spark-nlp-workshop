"""
Tax form utilities — W-2 accuracy, PII visualization, router analysis,
and form field detection.

Extracted from demo_utils.py — contains all tax-form-specific functions
including W-2 field comparison, PII bounding-box drawing and redaction,
multi-form router distribution charts, and field detection galleries.
"""

import base64
import json
import uuid
from io import BytesIO

from IPython.display import display, HTML

__all__ = [
    "_normalize_w2_value",
    "_W2_NUMERIC_FIELDS",
    "_W2_GT_ALIASES",
    "compare_w2_field",
    "find_gt_value",
    "display_w2_predictions",
    "_pii_fallback_bbox",
    "draw_pii_on_image",
    "plot_pii_redaction_gallery",
    "plot_pii_stats",
    "plot_router_distribution",
    "plot_w2_accuracy_chart",
    "draw_fields_on_image",
    "plot_field_detection_gallery",
    "plot_field_detection_stats",
]


def _normalize_w2_value(v):
    """Strip whitespace, lowercase, remove currency symbols."""
    if v is None:
        return ""
    s = str(v).strip().lower()
    import re as _re
    s = _re.sub(r"[\$,]", "", s)
    return s.strip()


_W2_NUMERIC_FIELDS = {
    "wages_tips_other", "federal_income_tax_withheld",
    "social_security_wages", "social_security_tax_withheld",
    "medicare_wages", "medicare_tax_withheld",
    "state_wages", "state_income_tax", "box_12_amount",
}


_W2_GT_ALIASES = {
    "employer_name":                ["box_c_employer_name"],
    "employer_ein":                 ["box_b_employer_identification_number"],
    "employee_name":                ["box_e_employee_name"],
    "employee_ssn_masked":          ["box_a_employee_ssn"],
    "wages_tips_other":             ["box_1_wages"],
    "federal_income_tax_withheld":  ["box_2_federal_tax_withheld"],
    "social_security_wages":        ["box_3_social_security_wages"],
    "social_security_tax_withheld": ["box_4_social_security_tax_withheld"],
    "medicare_wages":               ["box_5_medicare_wages"],
    "medicare_tax_withheld":        ["box_6_medicare_wages_tax_withheld",
                                     "box_6_medicare_tax_withheld"],
    "state":                        ["box_15_1_state"],
    "state_wages":                  ["box_16_1_state_wages"],
    "state_income_tax":             ["box_17_1_state_income_tax"],
}


def compare_w2_field(extracted_val, gt_val, field_name):
    """Compare extracted vs GT for a W-2 field. Returns (is_correct, similarity) or (None, None)."""
    from difflib import SequenceMatcher
    ext_str = _normalize_w2_value(extracted_val)
    gt_str  = _normalize_w2_value(gt_val)
    if not gt_str or gt_str in ("none", "null", ""):
        return None, None
    if not ext_str:
        return False, 0.0
    if field_name in _W2_NUMERIC_FIELDS:
        try:
            ext_f = float(ext_str)
            gt_f  = float(gt_str)
            is_ok = (abs(ext_f - gt_f) / abs(gt_f) < 0.01) if gt_f != 0 else ext_f == 0
            sim   = 1.0 if is_ok else max(0.0, 1.0 - abs(ext_f - gt_f) / max(abs(gt_f), 1))
            return is_ok, sim
        except (ValueError, TypeError):
            pass
    sim = SequenceMatcher(None, ext_str, gt_str).ratio()
    return sim >= 0.85, sim


def find_gt_value(gt_dict, w2_field):
    """Find the GT value for a W-2 schema field from singhsays dataset gt_parse dict."""
    if not gt_dict:
        return None
    if w2_field in gt_dict:
        return gt_dict[w2_field]
    for alias in _W2_GT_ALIASES.get(w2_field, []):
        if alias in gt_dict and gt_dict[alias] is not None:
            return gt_dict[alias]
    lower_field = w2_field.lower().replace("_", "")
    for k, v in gt_dict.items():
        if k.lower().replace("_", "") == lower_field:
            return v
    return None


def display_w2_predictions(images, results, gt_data, gt_fields):
    """
    Interactive 2-panel W-2 predictions viewer.
    Left 42%: document image | Right: Field | Extracted | Ground Truth table.
    Rows color-coded: green = match, red = mismatch, neutral = no GT.
    """
    docs = []
    for img, result, gt in zip(images, results, gt_data):
        if not result.get("data"):
            continue
        extracted = result["data"]
        buf = BytesIO()
        img.save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode()

        rows = []
        match_count = miss_count = 0
        for field in gt_fields:
            ext_val = extracted.get(field)
            gt_val  = find_gt_value(gt, field)
            is_ok, sim = compare_w2_field(ext_val, gt_val, field)
            if is_ok is True:
                match_count += 1
                row_cls = "good"
            elif is_ok is False:
                miss_count += 1
                row_cls = "bad"
            else:
                row_cls = "neutral"
            rows.append({
                "field":     field.replace("_", " ").title(),
                "extracted": str(ext_val) if ext_val is not None else "—",
                "gt":        str(gt_val)  if gt_val  is not None else "—",
                "cls":       row_cls,
            })
        docs.append({
            "id":    result.get("_id", f"doc_{len(docs)}"),
            "image": img_b64,
            "rows":  rows,
            "match": match_count,
            "miss":  miss_count,
        })

    if not docs:
        display(HTML("<p style='color:#ef4444'>No successful extractions to display.</p>"))
        return

    vid       = f"w2pred_{uuid.uuid4().hex[:8]}"
    docs_json = json.dumps(docs)
    total     = len(docs)

    html = f"""
<div id="{vid}" style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
<style>
  #{vid} {{ color:#e2e8f0; background:#0f172a; border:1px solid #334155; border-radius:12px; padding:16px; margin:8px 0 }}
  #{vid} .nav {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; padding:8px 14px; background:#1e293b; border-radius:8px; border:1px solid #334155 }}
  #{vid} .nav button {{ background:#334155; border:none; color:#e2e8f0; padding:6px 16px; border-radius:6px; cursor:pointer; font-size:13px }}
  #{vid} .nav button:hover {{ background:#475569 }}
  #{vid} .doc-id {{ color:#7c3aed; font-size:13px; font-weight:600 }}
  #{vid} .score {{ font-size:12px; padding:3px 10px; border-radius:10px; margin-left:8px }}
  #{vid} .score-good {{ background:#064e3b; color:#6ee7b7 }}
  #{vid} .score-bad  {{ background:#450a0a; color:#fca5a5 }}
  #{vid} .body {{ display:flex; gap:16px; align-items:flex-start }}
  #{vid} .img-panel {{ flex:0 0 42%; max-width:42% }}
  #{vid} .img-panel img {{ width:100%; border-radius:8px; border:1px solid #334155 }}
  #{vid} .tbl-panel {{ flex:1; max-height:600px; overflow-y:auto }}
  #{vid} .lbl {{ font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:.05em; margin-bottom:8px }}
  #{vid} table {{ width:100%; border-collapse:collapse; font-size:12.5px }}
  #{vid} th {{ background:#1e293b; color:#94a3b8; padding:7px 10px; text-align:left; font-size:11px; text-transform:uppercase; letter-spacing:.05em; border-bottom:2px solid #334155; position:sticky; top:0 }}
  #{vid} td {{ padding:6px 10px; border-bottom:1px solid #1e293b; vertical-align:top }}
  #{vid} .good td {{ background:rgba(16,185,129,.07) }}
  #{vid} .bad  td {{ background:rgba(239,68,68,.08) }}
  #{vid} .field-name {{ color:#94a3b8; font-weight:500 }}
  #{vid} .ext-val {{ color:#e2e8f0 }}
  #{vid} .gt-val  {{ color:#7c3aed }}
</style>
<div class="nav">
  <button id="prev_{vid}">← Prev</button>
  <div style="display:flex;align-items:center">
    <span class="doc-id" id="doc_id_{vid}"></span>
    <span id="score_{vid}" class="score"></span>
  </div>
  <div style="display:flex;align-items:center;gap:10px">
    <span style="color:#94a3b8;font-size:13px" id="counter_{vid}">1 / {total}</span>
    <button id="next_{vid}">Next →</button>
  </div>
</div>
<div class="body">
  <div class="img-panel"><img id="img_{vid}" src="" alt="W-2"/></div>
  <div class="tbl-panel">
    <div class="lbl">Extracted vs Ground Truth</div>
    <table>
      <thead><tr><th>Field</th><th>Extracted</th><th>Ground Truth</th></tr></thead>
      <tbody id="tbody_{vid}"></tbody>
    </table>
  </div>
</div>
<script>
(function() {{
  const docs = {docs_json};
  let idx = 0;
  function show(i) {{
    const d = docs[i];
    document.getElementById('img_{vid}').src = 'data:image/png;base64,' + d.image;
    document.getElementById('doc_id_{vid}').textContent = d.id;
    document.getElementById('counter_{vid}').textContent = (i+1) + ' / {total}';
    const sc = document.getElementById('score_{vid}');
    const tot = d.match + d.miss;
    if (tot > 0) {{
      const pct = Math.round(100*d.match/tot);
      sc.textContent = pct + '% (' + d.match + '/' + tot + ' fields)';
      sc.className = 'score ' + (pct >= 80 ? 'score-good' : 'score-bad');
    }} else {{
      sc.textContent = 'No GT'; sc.className = 'score';
    }}
    const tbody = document.getElementById('tbody_{vid}');
    tbody.innerHTML = '';
    d.rows.forEach(function(r) {{
      const tr = document.createElement('tr');
      tr.className = r.cls;
      const icon = r.cls === 'good' ? '✓' : r.cls === 'bad' ? '✗' : '·';
      tr.innerHTML = '<td class="field-name">' + icon + ' ' + r.field + '</td>' +
                     '<td class="ext-val">' + r.extracted + '</td>' +
                     '<td class="gt-val">'  + r.gt        + '</td>';
      tbody.appendChild(tr);
    }});
  }}
  document.getElementById('prev_{vid}').onclick = function() {{ if(idx>0) show(--idx); }};
  document.getElementById('next_{vid}').onclick = function() {{ if(idx<docs.length-1) show(++idx); }};
  show(0);
}})();
</script>
</div>"""
    display(HTML(html))


def _pii_fallback_bbox(entity_type, text="", idx=0):
    """Generate a plausible placeholder bbox when the model returns no coordinates."""
    import random as _rnd
    rng = _rnd.Random(hash(text or entity_type) + idx)
    w = rng.uniform(0.15, 0.30)
    h = rng.uniform(0.030, 0.055)
    x = rng.uniform(0.05, max(0.06, 0.95 - w))
    y_hints = {
        "NAME":         (0.05, 0.25), "SSN":          (0.05, 0.20),
        "EIN":          (0.10, 0.30), "ADDRESS":       (0.20, 0.50),
        "DOB":          (0.15, 0.35), "PHONE":         (0.20, 0.45),
        "EMAIL":        (0.20, 0.45), "BANK_ACCOUNT":  (0.40, 0.70),
        "SIGNATURE":    (0.75, 0.92),
    }
    y_min, y_max = y_hints.get(entity_type, (0.10, 0.80))
    y = rng.uniform(y_min, min(y_max, 0.93 - h))
    return x, y, w, h


def draw_pii_on_image(image, pii_entities, doc_id=""):
    """
    Draw PII bounding boxes on image.
    Returns a matplotlib figure with annotated (left) and auto-redacted (right) views.
    Entities missing bbox coordinates get plausible placeholder boxes.
    CRITICAL + HIGH risk entities are blacked out on the redacted side.
    """
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    RISK_COLORS = {
        "CRITICAL": "#ef4444", "HIGH": "#f59e0b",
        "MEDIUM":   "#3b82f6", "LOW":  "#10b981",
    }

    img_arr = np.array(image)
    img_h, img_w = img_arr.shape[:2]

    fig, axes = plt.subplots(1, 2, figsize=(16, 9), facecolor="#1e293b")
    for ax in axes:
        ax.set_facecolor("#1e293b")
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        for sp in ax.spines.values():
            sp.set_visible(False)

    img_redacted = img_arr.copy()

    for i, e in enumerate(pii_entities):
        etype = e.get("entity_type", "OTHER")
        text  = e.get("text", "")
        risk  = e.get("risk_level", "LOW")
        color = RISK_COLORS.get(risk, "#94a3b8")

        bx = e.get("bbox_x_norm")
        if bx is not None:
            by = e.get("bbox_y_norm", 0)
            bw = e.get("bbox_w_norm", 0.20)
            bh = e.get("bbox_h_norm", 0.05)
            synthetic = False
        else:
            bx, by, bw, bh = _pii_fallback_bbox(etype, text, i)
            synthetic = True

        px, py = bx * img_w, by * img_h
        pw, ph = bw * img_w, bh * img_h

        rect = patches.FancyBboxPatch(
            (px, py), pw, ph,
            boxstyle="round,pad=2", linewidth=1.5,
            edgecolor=color, facecolor=color + "22",
        )
        axes[0].add_patch(rect)
        label = f"{etype}: {str(text)[:16]}" + (" *" if synthetic else "")
        axes[0].text(px, py - 3, label, fontsize=7, color=color,
                     va="bottom", clip_on=True,
                     bbox=dict(boxstyle="round,pad=1", facecolor="#1e293b",
                               alpha=0.75, edgecolor="none"))

        if risk in ("CRITICAL", "HIGH"):
            x1 = max(0, int(px) - 2)
            y1 = max(0, int(py) - 2)
            x2 = min(img_w, int(px + pw) + 2)
            y2 = min(img_h, int(py + ph) + 2)
            img_redacted[y1:y2, x1:x2] = 20

    axes[0].imshow(img_arr)
    axes[0].set_title(f"PII Detected{' — ' + doc_id if doc_id else ''}", color="#e2e8f0", pad=8)
    axes[1].imshow(img_redacted)
    axes[1].set_title("Auto-Redacted (CRITICAL + HIGH)", color="#e2e8f0", pad=8)

    n_syn = sum(1 for e in pii_entities if e.get("bbox_x_norm") is None)
    note  = f" (* {n_syn} synthetic bbox)" if n_syn else ""
    plt.suptitle(f"PII Detection + Auto-Redaction — {len(pii_entities)} entities{note}",
                 color="#e2e8f0", fontsize=12, y=1.01)
    plt.tight_layout()
    return fig


def plot_pii_redaction_gallery(images, pii_results, max_docs=5):
    """Show PII bounding boxes + auto-redaction for the first N successful documents."""
    import matplotlib.pyplot as plt
    shown = 0
    for img, result in zip(images, pii_results):
        if not result.get("data"):
            continue
        data     = result["data"]
        entities = data.get("pii_entities", [])
        print(f"\n{result.get('_id','?')} -- form={data.get('form_type','?')} | "
              f"risk={data.get('deid_risk_level','?')} | {len(entities)} entities")
        for e in entities:
            icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(
                e.get("risk_level", "LOW"), "⚪")
            has_bb   = e.get("bbox_x_norm") is not None
            bbox_tag = (f" @ ({e['bbox_x_norm']:.2f},{e['bbox_y_norm']:.2f})"
                        if has_bb else " [synthetic bbox]")
            print(f"  {icon} {e.get('entity_type','?'):15s}: {str(e.get('text',''))[:40]}{bbox_tag}")
        fig = draw_pii_on_image(img, entities, doc_id=result.get("_id", ""))
        plt.show()
        shown += 1
        if shown >= max_docs:
            break
    if shown == 0:
        print("[warn]  No successful PII extractions to visualize")


def plot_pii_stats(pii_results):
    """Entity type bar chart + document risk level donut for PII extraction results."""
    import matplotlib.pyplot as plt
    from collections import Counter

    all_entities = []
    risk_by_doc  = []
    for r in pii_results:
        if r.get("data"):
            all_entities.extend(r["data"].get("pii_entities", []))
            risk_by_doc.append(r["data"].get("deid_risk_level", "UNKNOWN"))

    entity_type_counts = Counter(e.get("entity_type", "?") for e in all_entities)
    risk_level_counts  = Counter(risk_by_doc)
    RISK_COLORS = {"CRITICAL": "#ef4444", "HIGH": "#f59e0b",
                   "MEDIUM": "#3b82f6",   "LOW":  "#10b981"}

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor="#1e293b")

    # Left: entity type bar
    ax = axes[0]
    ax.set_facecolor("#1e293b")
    for sp in ["top", "right"]: ax.spines[sp].set_visible(False)
    for sp in ["bottom", "left"]: ax.spines[sp].set_color("#475569")
    ax.tick_params(colors="#e2e8f0")
    sorted_types = sorted(entity_type_counts.items(), key=lambda x: -x[1])
    labels = [t for t, _ in sorted_types]
    values = [c for _, c in sorted_types]
    bars = ax.barh(labels, values, color="#7c3aed", alpha=0.85)
    for bar, v in zip(bars, values):
        ax.text(v + 0.1, bar.get_y() + bar.get_height() / 2, str(v),
                va="center", color="#e2e8f0", fontsize=10)
    ax.set_xlabel("Entity Count", color="#94a3b8")
    ax.set_title("PII Entity Types Detected", color="#e2e8f0", fontsize=12, pad=10)
    ax.tick_params(axis="y", labelcolor="#e2e8f0")

    # Right: risk donut
    ax2 = axes[1]
    ax2.set_facecolor("#1e293b")
    risk_labels = list(risk_level_counts.keys())
    risk_vals   = list(risk_level_counts.values())
    colors_used = [RISK_COLORS.get(l, "#94a3b8") for l in risk_labels]
    wedges, texts, autotexts = ax2.pie(
        risk_vals, labels=risk_labels, colors=colors_used,
        autopct="%1.0f%%", startangle=90,
        wedgeprops=dict(width=0.55, edgecolor="#1e293b"),
        textprops=dict(color="#e2e8f0"),
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(11)
    ax2.set_title("Document De-ID Risk Level", color="#e2e8f0", fontsize=12, pad=10)

    plt.suptitle(f"PII Summary — {len(all_entities)} entities across {len(pii_results)} documents",
                 color="#e2e8f0", fontsize=13, y=1.02, fontweight="bold")
    plt.tight_layout()
    plt.show()

    print(f"\n{'Entity Type':20s}  {'Count':>5s}")
    print("-" * 28)
    for t, c in sorted_types:
        print(f"  {t:18s}  {c:>5d}")


def plot_router_distribution(router_results):
    """Form type distribution bar + routing confidence donut for multi-form router results."""
    import matplotlib.pyplot as plt
    from collections import Counter

    detected_types = []
    conf_counts    = Counter()
    for r in router_results:
        if r.get("data"):
            detected_types.append(r["data"].get("form_type", "unknown"))
            conf_counts[r["data"].get("confidence", "unknown")] += 1

    type_counts  = Counter(detected_types)
    sorted_types = sorted(type_counts.items(), key=lambda x: -x[1])

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor="#1e293b")

    # Left: form type bar
    ax = axes[0]
    ax.set_facecolor("#1e293b")
    for sp in ["top", "right"]: ax.spines[sp].set_visible(False)
    for sp in ["bottom", "left"]: ax.spines[sp].set_color("#475569")
    ax.tick_params(colors="#e2e8f0")
    labels     = [t for t, _ in sorted_types]
    values     = [c for _, c in sorted_types]
    bar_colors = ["#7c3aed" if l == "W-2" else "#06b6d4" for l in labels]
    bars = ax.barh(labels, values, color=bar_colors, alpha=0.85)
    for bar, v in zip(bars, values):
        ax.text(v + 0.1, bar.get_y() + bar.get_height() / 2, str(v),
                va="center", color="#e2e8f0", fontsize=10)
    ax.set_xlabel("Documents", color="#94a3b8")
    ax.set_title("Detected Form Types", color="#e2e8f0", fontsize=12, pad=10)
    ax.tick_params(axis="y", labelcolor="#e2e8f0")

    # Right: confidence donut
    ax2 = axes[1]
    ax2.set_facecolor("#1e293b")
    conf_labels = list(conf_counts.keys())
    conf_vals   = list(conf_counts.values())
    conf_colors = {"high": "#10b981", "medium": "#f59e0b", "low": "#ef4444"}
    colors_used = [conf_colors.get(l, "#94a3b8") for l in conf_labels]
    wedges, texts, autotexts = ax2.pie(
        conf_vals, labels=conf_labels, colors=colors_used,
        autopct="%1.0f%%", startangle=90,
        wedgeprops=dict(width=0.55, edgecolor="#1e293b"),
        textprops=dict(color="#e2e8f0"),
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(11)
    ax2.set_title("Routing Confidence", color="#e2e8f0", fontsize=12, pad=10)

    plt.suptitle("Multi-Form Router — Zero Templates, Any IRS Form",
                 color="#e2e8f0", fontsize=13, y=1.02, fontweight="bold")
    plt.tight_layout()
    plt.show()
    print(f"\nRouted {len(detected_types)} docs -> {len(type_counts)} distinct form types")


def plot_w2_accuracy_chart(field_stats, gt_fields):
    """Horizontal bar chart of W-2 field-level extraction accuracy vs ground truth."""
    import matplotlib.pyplot as plt

    fields_with_data = [(f, field_stats[f]) for f in gt_fields if field_stats[f]["total"] > 0]
    if not fields_with_data:
        print("[warn]  No accuracy data to plot -- run W-2 accuracy cell first.")
        return

    field_names = [f.replace("_", " ").title() for f, _ in fields_with_data]
    accuracies  = [s["correct"] / s["total"] * 100 for _, s in fields_with_data]
    avg_sims    = [(sum(s["sims"]) / len(s["sims"]) * 100) if s["sims"] else 0
                   for _, s in fields_with_data]

    fig, axes = plt.subplots(1, 2, figsize=(16, max(5, len(fields_with_data) * 0.55)),
                             facecolor="#1e293b")
    for ax in axes:
        ax.set_facecolor("#1e293b")
        ax.tick_params(colors="#e2e8f0")
        for sp in ["top", "right"]: ax.spines[sp].set_visible(False)
        for sp in ["bottom", "left"]: ax.spines[sp].set_color("#475569")

    y_pos = list(range(len(field_names)))

    # Left: exact accuracy
    bar_colors = ["#10b981" if a >= 80 else "#f59e0b" if a >= 50 else "#ef4444"
                  for a in accuracies]
    axes[0].barh(y_pos, accuracies, color=bar_colors, alpha=0.85)
    axes[0].set_yticks(y_pos)
    axes[0].set_yticklabels(field_names, color="#e2e8f0", fontsize=10)
    axes[0].set_xlim(0, 110)
    axes[0].set_xlabel("Accuracy (%)", color="#94a3b8")
    axes[0].set_title("Field Accuracy (match ≥ 85% / 1% $ tolerance)",
                      color="#e2e8f0", fontsize=11, pad=10)
    axes[0].axvline(85, color="#475569", linestyle="--", alpha=0.6)
    for i, v in enumerate(accuracies):
        axes[0].text(v + 0.5, i, f"{v:.0f}%", va="center", color="#e2e8f0", fontsize=9)

    # Right: avg similarity
    axes[1].barh(y_pos, avg_sims, color="#7c3aed", alpha=0.80)
    axes[1].set_yticks(y_pos)
    axes[1].set_yticklabels(field_names, color="#e2e8f0", fontsize=10)
    axes[1].set_xlim(0, 110)
    axes[1].set_xlabel("Average String Similarity (%)", color="#94a3b8")
    axes[1].set_title("Average String Similarity", color="#e2e8f0", fontsize=11, pad=10)
    for i, v in enumerate(avg_sims):
        axes[1].text(v + 0.5, i, f"{v:.0f}%", va="center", color="#e2e8f0", fontsize=9)

    plt.suptitle("W-2 Extraction Accuracy — Field-Level Analysis",
                 color="#e2e8f0", fontsize=13, y=1.01, fontweight="bold")
    plt.tight_layout()
    plt.show()


def draw_fields_on_image(image, model_fields, gt_data, doc_id="", form_type="unknown"):
    """
    2-column viz: model-predicted field bboxes (left) vs GT bboxes (right).

    model_fields : list of dicts — {field_type, bbox_x_norm, bbox_y_norm, bbox_w_norm, bbox_h_norm}
    gt_data      : dict — {bboxes: [(x_norm, y_norm, w_norm, h_norm),...], categories: [0,1,2,...]}
                   Categories: 0 = text_input, 1 = checkbox, 2 = signature
    """
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.lines import Line2D

    TYPE_COLORS = {
        "text_input": "#3b82f6",
        "checkbox":   "#10b981",
        "signature":  "#a855f7",
        "other":      "#f59e0b",
    }
    CAT_COLORS = {0: "#3b82f6", 1: "#10b981", 2: "#a855f7"}

    img_arr = np.array(image.convert("RGB") if hasattr(image, "convert") else image)
    img_h, img_w = img_arr.shape[:2]

    gt_bboxes = gt_data.get("bboxes", [])
    gt_cats   = gt_data.get("categories", [0] * len(gt_bboxes))

    fig, axes = plt.subplots(1, 2, figsize=(16, 10), facecolor="#1e293b")
    for ax in axes:
        ax.set_facecolor("#1e293b")
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        for sp in ax.spines.values():
            sp.set_visible(False)

    # ── Left: model predictions ───────────────────────────────────────────────
    axes[0].imshow(img_arr)
    axes[0].set_title(
        f"Model Predictions  ({len(model_fields)} fields detected)",
        color="#e2e8f0", fontsize=11, pad=8, fontweight="bold",
    )
    if model_fields:
        for f in model_fields:
            bx = float(f.get("bbox_x_norm") or 0)
            by = float(f.get("bbox_y_norm") or 0)
            bw = float(f.get("bbox_w_norm") or 0.10)
            bh = float(f.get("bbox_h_norm") or 0.03)
            ftype = f.get("field_type", "other")
            color = TYPE_COLORS.get(ftype, "#94a3b8")
            rect = patches.FancyBboxPatch(
                (bx * img_w, by * img_h), bw * img_w, bh * img_h,
                boxstyle="round,pad=1", linewidth=1.5,
                edgecolor=color, facecolor=color + "22",
            )
            axes[0].add_patch(rect)
    else:
        axes[0].text(
            0.5, 0.5, "No fields detected\nby model",
            transform=axes[0].transAxes, color="#64748b",
            fontsize=13, ha="center", va="center",
        )

    # ── Right: ground truth ───────────────────────────────────────────────────
    axes[1].imshow(img_arr)
    axes[1].set_title(
        f"Ground Truth  ({len(gt_bboxes)} fields annotated)",
        color="#e2e8f0", fontsize=11, pad=8, fontweight="bold",
    )
    for (bx, by, bw, bh), cat in zip(gt_bboxes, gt_cats):
        color = CAT_COLORS.get(int(cat), "#94a3b8")
        rect = patches.FancyBboxPatch(
            (bx * img_w, by * img_h), bw * img_w, bh * img_h,
            boxstyle="round,pad=1", linewidth=1.5,
            edgecolor=color, facecolor=color + "22",
        )
        axes[1].add_patch(rect)

    # Shared legend
    legend_elements = [
        Line2D([0], [0], color="#3b82f6", linewidth=2, label="Text input"),
        Line2D([0], [0], color="#10b981", linewidth=2, label="Checkbox"),
        Line2D([0], [0], color="#a855f7", linewidth=2, label="Signature"),
    ]
    for ax in axes:
        ax.legend(
            handles=legend_elements, loc="lower right",
            facecolor="#0f172a", labelcolor="#e2e8f0", fontsize=8, framealpha=0.9,
        )

    fig.suptitle(f"{doc_id}  ·  {form_type}", color="#94a3b8", fontsize=10, y=1.01)
    plt.tight_layout()
    return fig


def plot_field_detection_gallery(images, results, gt_data_list):
    """
    Interactive prev/next gallery: model-predicted field bboxes (left) vs GT bboxes (right).
    Pre-renders all figures to PNG, embeds them in a single HTML/JS viewer with navigation.
    """
    import matplotlib
    matplotlib.use("Agg")          # off-screen — avoids duplicate inline display
    import matplotlib.pyplot as plt
    from io import BytesIO

    figs_b64  = []
    captions  = []

    for img, result, gt in zip(images, results, gt_data_list):
        data         = result.get("data") or {}
        model_fields = data.get("detected_fields", [])
        gt_bboxes    = gt.get("bboxes", [])
        form_type    = data.get("form_type", "unknown")
        doc_id       = result.get("_id", "?")

        fig = draw_fields_on_image(img, model_fields, gt, doc_id=doc_id, form_type=form_type)

        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=96,
                    facecolor="#1e293b")
        plt.close(fig)
        figs_b64.append(base64.b64encode(buf.getvalue()).decode())
        captions.append(
            f"{doc_id}  ·  form={form_type}  |  "
            f"model: {len(model_fields)} fields  ·  GT: {len(gt_bboxes)} fields"
        )

    if not figs_b64:
        print("[warn]  No results to visualize")
        return

    # Switch back to inline for any subsequent plt calls in the notebook
    matplotlib.use("module://matplotlib_inline.backend_inline")

    vid       = f"fdg_{uuid.uuid4().hex[:8]}"
    figs_json = json.dumps(figs_b64)
    caps_json = json.dumps(captions)
    n         = len(figs_b64)

    html = f"""
<div id="{vid}" style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
     background:#1e293b;border-radius:8px;padding:14px;box-sizing:border-box;">

  <!-- nav bar -->
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
    <button id="{vid}-prev"
      onclick="(function(){{var s={vid}_state;if(s.i>0){{s.i--;{vid}_show(s.i)}}}})();"
      style="padding:6px 16px;background:#2a9d8f;color:#fff;border:none;
             border-radius:4px;cursor:pointer;font-size:13px;font-weight:500;">
      ← Prev
    </button>
    <span id="{vid}-ctr" style="color:#94a3b8;font-size:13px;min-width:70px;text-align:center;">
      1 / {n}
    </span>
    <button id="{vid}-next"
      onclick="(function(){{var s={vid}_state;if(s.i<{n}-1){{s.i++;{vid}_show(s.i)}}}})();"
      style="padding:6px 16px;background:#2a9d8f;color:#fff;border:none;
             border-radius:4px;cursor:pointer;font-size:13px;font-weight:500;">
      Next →
    </button>
    <span id="{vid}-cap"
      style="color:#cbd5e1;font-size:12px;flex:1;text-align:right;white-space:nowrap;
             overflow:hidden;text-overflow:ellipsis;">
    </span>
  </div>

  <!-- figure -->
  <img id="{vid}-img" style="width:100%;border-radius:6px;display:block;" />

</div>

<script>
var {vid}_state = {{i: 0}};
var {vid}_figs  = {figs_json};
var {vid}_caps  = {caps_json};

function {vid}_show(i) {{
  document.getElementById('{vid}-img').src  = 'data:image/png;base64,' + {vid}_figs[i];
  document.getElementById('{vid}-cap').textContent  = {vid}_caps[i];
  document.getElementById('{vid}-ctr').textContent  = (i+1) + ' / ' + {vid}_figs.length;
  document.getElementById('{vid}-prev').disabled = (i === 0);
  document.getElementById('{vid}-next').disabled = (i === {vid}_figs.length - 1);
}}
{vid}_show(0);
</script>
"""
    display(HTML(html))


def plot_field_detection_stats(results, gt_data_list):
    """Bar chart of model vs GT field counts per doc + detected form type distribution."""
    import matplotlib.pyplot as plt
    from collections import Counter

    model_counts = [len((r.get("data") or {}).get("detected_fields", [])) for r in results]
    gt_counts    = [len(g.get("bboxes", [])) for g in gt_data_list]
    form_types   = [(r.get("data") or {}).get("form_type", "unknown") for r in results]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor="#1e293b")

    # Left: model vs GT field counts per document
    ax = axes[0]
    ax.set_facecolor("#1e293b")
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color("#334155")
    ax.spines["bottom"].set_color("#334155")
    ax.tick_params(colors="#94a3b8")

    n = len(results)
    x = list(range(n))
    w = 0.38
    ax.bar([i - w / 2 for i in x], model_counts, width=w, label="Model",  color="#7c3aed", alpha=0.85)
    ax.bar([i + w / 2 for i in x], gt_counts,    width=w, label="GT",     color="#06b6d4", alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Doc {i + 1}" for i in x], rotation=30, ha="right", fontsize=8, color="#94a3b8")
    ax.set_ylabel("Fields detected", color="#94a3b8", fontsize=9)
    ax.set_title("Field Count: Model vs Ground Truth", color="#e2e8f0", fontsize=11, pad=10)
    ax.legend(facecolor="#1e293b", labelcolor="#e2e8f0", fontsize=9)
    ax.grid(axis="y", color="#334155", linewidth=0.5, linestyle="--")

    # Right: form type distribution
    ax2 = axes[1]
    ax2.set_facecolor("#1e293b")
    for sp in ["top", "right"]:
        ax2.spines[sp].set_visible(False)
    ax2.spines["left"].set_color("#334155")
    ax2.spines["bottom"].set_color("#334155")

    ft_counts = Counter(form_types)
    labels = list(ft_counts.keys())
    vals   = [ft_counts[l] for l in labels]
    colors = ["#7c3aed", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#a855f7", "#6366f1", "#ec4899"]
    bars   = ax2.barh(labels, vals, color=colors[: len(labels)], alpha=0.85)
    ax2.set_xlabel("Count", color="#94a3b8", fontsize=9)
    ax2.set_title("Detected Form Types", color="#e2e8f0", fontsize=11, pad=10)
    ax2.tick_params(axis="y", labelcolor="#e2e8f0", labelsize=9)
    ax2.tick_params(axis="x", labelcolor="#94a3b8", labelsize=8)
    ax2.grid(axis="x", color="#334155", linewidth=0.5, linestyle="--")
    for bar, val in zip(bars, vals):
        ax2.text(
            bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
            str(val), color="#e2e8f0", va="center", fontsize=9,
        )

    plt.tight_layout()
    plt.show()


