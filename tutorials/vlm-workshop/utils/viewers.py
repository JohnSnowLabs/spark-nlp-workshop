"""
Viewer & HTML generation utilities extracted from demo_utils.py.

All interactive HTML viewers, card generators, and chart builders
for notebook display. Dark-mode optimized.
"""

import numpy as np
from IPython.display import display, HTML
from PIL import Image
from pathlib import Path
from io import BytesIO
import json
import base64
import uuid


__all__ = [
    "COLORS",
    "ECG_MEASURE_FIELDS",
    "ECG_PRED_FIELDS",
    "display_ecg_extraction",
    "show_ecg_mae",
    "plot_ecg_scatter",
    "show_ecg_comparison",
    "show_ecg_mae_comparison",
    "show_triage_comparison",
    "display_ecg_triage",
    "show_triage_accuracy",
    "display_ecg_triage_from_merged",
    "show_merged_triage_accuracy",
    "display_ecg_predictions",
    "display_document_analysis",
    "execute_rag_query",
    "display_rag_results",
    "display_extraction_charts",
    "create_hero_section",
    "create_metrics_card",
    "create_schema_card",
    "create_success_banner",
    "create_use_case_card",
    "USE_CASES",
    "show_use_case",
    "display_schema_comparison",
    "create_demo_results_card",
    "create_comparison_table",
    "display_case_similarity",
]


COLORS = {
    'primary': '#7c3aed',      # Purple (dark mode friendly)
    'secondary': '#a78bfa',    # Light purple
    'accent': '#06b6d4',       # Cyan
    'success': '#10b981',      # Green
    'warning': '#f59e0b',      # Amber
    'error': '#ef4444',        # Red
    'bg_dark': '#1e293b',      # Dark background
    'bg_medium': '#334155',    # Medium background
    'bg_light': '#475569',     # Light background
    'text': '#e2e8f0',         # Light text
    'text_muted': '#94a3b8',   # Muted text
    'border': '#475569',       # Border color
}


ECG_MEASURE_FIELDS = [
    ("heart_rate_bpm",   "gt_hr",  "Heart Rate",   "bpm"),
    ("pr_interval_ms",   "gt_pr",  "PR Interval",  "ms"),
    ("qrs_duration_ms",  "gt_qrs", "QRS Duration", "ms"),
    ("qt_interval_ms",   "gt_qt",  "QT Interval",  "ms"),
    ("qrs_axis_degrees", "gt_axis","QRS Axis",     "°"),
]


ECG_PRED_FIELDS = ["heart_rate_bpm", "pr_interval_ms", "qrs_duration_ms",
                   "qt_interval_ms", "qrs_axis_degrees", "rhythm", "findings", "clinical_summary"]


def display_ecg_extraction(images, results, gt_data):
    """Show ECG extraction viewer: image + pred vs GT table."""
    v_imgs, v_preds, v_gt = [], [], []
    for img, r, gt in zip(images, results, gt_data):
        if r.get("data") is None:
            continue
        d = r["data"]
        v_imgs.append(img)
        v_preds.append({k: d.get(k) for k in ECG_PRED_FIELDS})
        gt_display = dict(gt)
        gt_display["class"] = r.get("gt_class", "")
        v_gt.append(gt_display)
    print(f"{len(v_imgs)} ECGs")
    display_ecg_predictions(v_imgs, v_preds, v_gt)


def show_ecg_mae(results, model_name=None):
    """Compute and display MAE table for ECG extraction results."""
    import pandas as pd

    valid = [r for r in results if r.get("data")]
    rows = []
    for field, gt_field, label, unit in ECG_MEASURE_FIELDS:
        preds, gts = [], []
        for r in valid:
            p, g = r["data"].get(field), r.get(gt_field)
            if p is not None and g is not None and not np.isnan(float(g)):
                preds.append(float(p))
                gts.append(float(g))
        if preds:
            errors = np.abs(np.array(preds) - np.array(gts))
            abs_gts = np.maximum(np.abs(np.array(gts)), 1)
            rows.append({
                "Measurement": f"{label} ({unit})",
                "MAE": f"±{np.mean(errors):.1f}",
                "Median AE": f"±{np.median(errors):.1f}",
                "Within 10%": f"{np.mean(errors < 0.10 * abs_gts) * 100:.0f}%",
                "Within 15%": f"{np.mean(errors < 0.15 * abs_gts) * 100:.0f}%",
                "Within 20%": f"{np.mean(errors < 0.20 * abs_gts) * 100:.0f}%",
                "n": len(preds),
            })
    title = f"{model_name} ({len(valid)} ECGs)" if model_name else f"{len(valid)} ECGs"
    print(f"Extraction Accuracy -- {title}")
    display(pd.DataFrame(rows).style.set_caption("MAE vs PTB-XL+ 12SL Ground Truth"))


def plot_ecg_scatter(models_results):
    """Multi-model predicted vs GT scatter plots (2x3 grid) for ECG measurements."""
    import matplotlib.pyplot as plt

    _MODEL_COLORS = ['#22d3ee', '#f97316', '#a78bfa', '#4ade80', '#fb7185']
    model_names = list(models_results.keys())
    color_map = {m: _MODEL_COLORS[i % len(_MODEL_COLORS)] for i, m in enumerate(model_names)}

    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    fig.patch.set_facecolor('#1e293b')

    for idx, (field, gt_field, label, unit) in enumerate(ECG_MEASURE_FIELDS):
        ax = axes.flat[idx]
        ax.set_facecolor('#1e293b')
        all_vals = []
        for model, results in models_results.items():
            valid = [r for r in results if r.get("data")]
            preds, gts = [], []
            for r in valid:
                p, g = r["data"].get(field), r.get(gt_field)
                if p is not None and g is not None and not np.isnan(float(g)):
                    preds.append(float(p))
                    gts.append(float(g))
            if not preds:
                continue
            pa, ga = np.array(preds), np.array(gts)
            all_vals.extend(list(pa) + list(ga))
            mae = np.mean(np.abs(pa - ga))
            short = model.split("/")[-1] if "/" in model else model
            ax.scatter(ga, pa, c=color_map[model], alpha=0.6, edgecolors='#475569',
                       s=40, label=f'{short} (±{mae:.1f})')
        if not all_vals:
            ax.set_visible(False)
            continue
        lo, hi = min(all_vals) * 0.9, max(all_vals) * 1.1
        ax.plot([lo, hi], [lo, hi], 'r--', alpha=0.5)
        ax.set_xlabel(f"GT ({unit})", color='#94a3b8', fontsize=10)
        ax.set_ylabel(f"Predicted ({unit})", color='#94a3b8', fontsize=10)
        ax.set_title(label, color='#e2e8f0', fontsize=12, fontweight='bold')
        ax.tick_params(colors='#94a3b8')
        ax.spines[:].set_color('#475569')
        ax.legend(fontsize=8, facecolor='#334155', edgecolor='#475569', labelcolor='#e2e8f0')

    if len(ECG_MEASURE_FIELDS) < 6:
        axes.flat[-1].set_visible(False)
    fig.suptitle('Predicted vs Ground Truth — Model Comparison', color='#e2e8f0',
                 fontsize=15, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.show()


def show_ecg_comparison(results, n=20):
    """Per-sample comparison table: ECG | Class | measurements with GT + error."""
    import pandas as pd

    valid = [r for r in results if r.get("data")]
    rows = []
    for r in valid[:n]:
        d = r["data"]
        row = {"ECG": r.get("id", ""), "Class": r.get("gt_class", "")}
        for field, gt_field, label, _ in ECG_MEASURE_FIELDS:
            p, g = d.get(field), r.get(gt_field)
            if p is not None and g is not None and not np.isnan(float(g)):
                row[label] = f"{p} (gt={float(g):.0f}, err={abs(float(p)-float(g)):.0f})"
            else:
                row[label] = f"{p}" if p else "—"
        rows.append(row)
    print(f"Per-sample comparison ({len(rows)}/{len(valid)})")
    display(pd.DataFrame(rows).style.set_caption("Predicted vs GT — per ECG"))


def show_ecg_mae_comparison(models_results):
    """Side-by-side MAE table for multiple models."""
    import pandas as pd

    rows = []
    for field, gt_field, label, unit in ECG_MEASURE_FIELDS:
        row = {"Measurement": f"{label} ({unit})"}
        for model, results in models_results.items():
            valid = [r for r in results if r.get("data")]
            preds, gts = [], []
            for r in valid:
                p, g = r["data"].get(field), r.get(gt_field)
                if p is not None and g is not None and not np.isnan(float(g)):
                    preds.append(float(p))
                    gts.append(float(g))
            if preds:
                errors = np.abs(np.array(preds) - np.array(gts))
                abs_gts = np.maximum(np.abs(np.array(gts)), 1)
                short = model.split("/")[-1] if "/" in model else model
                row[short] = f"±{np.mean(errors):.1f}"
            else:
                short = model.split("/")[-1] if "/" in model else model
                row[short] = "—"
        rows.append(row)
    display(pd.DataFrame(rows).style.set_caption("MAE Comparison — Multiple Models"))


def show_triage_comparison(models_results):
    """Side-by-side triage accuracy for multiple models."""
    import pandas as pd

    rows = []
    for model, results in models_results.items():
        valid = [r for r in results if r.get("data")]
        tp = fn = tn = fp = 0
        for r in valid:
            gt_class = r.get("gt_class", "")
            gt_triage = "normal" if gt_class == "NORM" else "abnormal"
            pred = r["data"].get("screening_result", "").lower()
            if gt_triage == "abnormal" and pred == "abnormal": tp += 1
            elif gt_triage == "abnormal" and pred != "abnormal": fn += 1
            elif gt_triage == "normal" and pred == "normal": tn += 1
            else: fp += 1
        n = tp + fn + tn + fp
        short = model.split("/")[-1] if "/" in model else model
        rows.append({
            "Model": short,
            "Accuracy": f"{(tp+tn)/max(n,1)*100:.0f}%",
            "Sensitivity": f"{tp/max(tp+fn,1)*100:.0f}%",
            "Specificity": f"{tn/max(tn+fp,1)*100:.0f}%",
            "n": n,
        })
    display(pd.DataFrame(rows).style.set_caption("Triage Comparison — Multiple Models"))


def display_ecg_triage(genecg_dir, results):
    """Show triage results in the same image+table viewer as extraction."""
    imgs, preds, gts = [], [], []
    for r in results:
        if r.get("data") is None:
            continue
        img_file = r["ecg_id"] + ".png"
        img_path = Path(genecg_dir) / img_file
        if not img_path.exists():
            continue
        imgs.append(Image.open(img_path).convert("RGB"))
        d = r["data"]
        preds.append({
            "screening_result": d.get("screening_result", ""),
            "confidence": d.get("confidence", ""),
            "findings": d.get("findings", []),
            "clinical_summary": d.get("clinical_summary", ""),
        })
        correct = d.get("screening_result") == r.get("gt_triage")
        gts.append({
            "gt_triage": r.get("gt_triage", ""),
            "gt_label": r.get("gt_label", ""),
            "correct": correct,
        })
    print(f"{len(imgs)} ECGs")
    _display_ecg_triage_viewer(imgs, preds, gts)


def _display_ecg_triage_viewer(images, predictions, ground_truths):
    """Image+table viewer for triage: screening result, confidence, findings vs GT."""
    images_b64 = []
    for img in images:
        buf = BytesIO()
        img.save(buf, format="PNG")
        images_b64.append(base64.b64encode(buf.getvalue()).decode())

    table_data = []
    for pred, gt in zip(predictions, ground_truths):
        rows = []
        # Screening result with match indicator
        p = pred.get("screening_result", "")
        g = gt.get("gt_triage", "")
        match = "good" if p == g else "bad"
        rows.append({"field": "Screening Result", "pred": p, "gt": g, "error": "Correct" if p == g else "Wrong", "match": match})
        # GT label
        rows.append({"field": "GT Diagnosis", "pred": "", "gt": gt.get("gt_label", ""), "error": "", "match": "neutral"})
        # Confidence
        rows.append({"field": "Confidence", "pred": pred.get("confidence", ""), "gt": "", "error": "", "match": "neutral"})
        # Findings
        findings = pred.get("findings", [])
        if findings:
            rows.append({"field": "Findings", "pred": "; ".join(str(f) for f in findings), "gt": "", "error": "", "match": "neutral"})
        # Summary
        s = pred.get("clinical_summary", "")
        if s:
            rows.append({"field": "Clinical Summary", "pred": s, "gt": "", "error": "", "match": "neutral"})
        table_data.append(rows)

    vid = f"triage_{uuid.uuid4().hex[:8]}"
    total = len(images)
    table_json = json.dumps(table_data)
    images_json = json.dumps(images_b64)

    # Reuse same HTML/JS template as display_ecg_predictions
    html = f"""
<style>
#{vid} {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: #d4d4d4;
}}
#{vid} .header {{
    background: linear-gradient(135deg, #6d28d9 0%, #2a9d8f 100%);
    padding: 18px 30px; border-radius: 12px; margin-bottom: 14px; text-align: center;
}}
#{vid} .header h1 {{ color: white; margin: 0; font-size: 24px; letter-spacing: 2px; }}
#{vid} .header p {{ color: #e2e8f0; margin: 6px 0 0 0; font-size: 13px; }}
#{vid} .nav {{
    display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 14px;
}}
#{vid} .nav button {{
    background: #334155; color: #d4d4d4; border: 1px solid #475569;
    padding: 8px 18px; border-radius: 6px; cursor: pointer; font-size: 14px;
}}
#{vid} .nav button:hover {{ background: #475569; }}
#{vid} .nav span {{ color: #94a3b8; font-size: 14px; min-width: 100px; text-align: center; }}
#{vid} .content {{ display: flex; gap: 16px; align-items: flex-start; }}
#{vid} .img-panel {{ flex: 0 0 45%; max-width: 45%; }}
#{vid} .img-panel img {{ width: 100%; border-radius: 8px; border: 1px solid #475569; }}
#{vid} .table-panel {{ flex: 1; overflow-x: auto; }}
#{vid} table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
#{vid} th {{
    background: #1e293b; color: #8ecae6; padding: 6px 10px;
    text-align: left; border-bottom: 2px solid #6d28d9;
    font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 1px;
}}
#{vid} td {{
    padding: 6px 10px; border-bottom: 1px solid #334155;
    vertical-align: top; word-break: break-word; text-align: left;
}}
#{vid} tr.good td {{ background: rgba(16, 185, 129, 0.08); }}
#{vid} tr.bad td {{ background: rgba(239, 68, 68, 0.08); }}
#{vid} .match-good {{ color: #10b981; }}
#{vid} .match-bad {{ color: #ef4444; }}
</style>
<div id="{vid}">
  <div class="header">
    <h1>ECG Triage</h1>
    <p>{total} ECGs &mdash; Normal vs Abnormal Screening</p>
  </div>
  <div class="nav">
    <button onclick="{vid}_nav(-1)">&larr; Prev</button>
    <span id="{vid}_counter">1 / {total}</span>
    <button onclick="{vid}_nav(1)">Next &rarr;</button>
  </div>
  <div class="content">
    <div class="img-panel"><img id="{vid}_img" src=""></div>
    <div class="table-panel"><table id="{vid}_tbl"></table></div>
  </div>
</div>
<script>
(function() {{
  var imgs = {images_json};
  var data = {table_json};
  var idx = 0, total = {total};
  function show(i) {{
    idx = (i % total + total) % total;
    document.getElementById("{vid}_img").src = "data:image/png;base64," + imgs[idx];
    document.getElementById("{vid}_counter").textContent = (idx+1) + " / " + total;
    var rows = data[idx];
    var h = "<tr><th>Field</th><th>Prediction</th><th>Ground Truth</th><th>Match</th></tr>";
    rows.forEach(function(r) {{
      var cls = r.match !== "neutral" ? r.match : "";
      var errCls = r.match === "good" ? "match-good" : (r.match === "bad" ? "match-bad" : "");
      h += '<tr class="' + cls + '"><td>' + r.field + '</td><td>' + r.pred +
           '</td><td>' + r.gt + '</td><td class="' + errCls + '">' + r.error + '</td></tr>';
    }});
    document.getElementById("{vid}_tbl").innerHTML = h;
  }}
  window.{vid}_nav = function(d) {{ show(idx + d); }};
  show(0);
}})();
</script>"""
    display(HTML(html))


def show_triage_accuracy(results):
    """Confusion matrix + sensitivity/specificity bars for triage results."""
    import matplotlib.pyplot as plt

    rows = [{"gt": r["gt_triage"], "pred": r["data"]["screening_result"]}
            for r in results if r.get("data")]
    if not rows:
        print("No triage results")
        return

    gt = np.array([r["gt"] for r in rows])
    pred = np.array([r["pred"] for r in rows])
    TP = int(((gt == "abnormal") & (pred == "abnormal")).sum())
    TN = int(((gt == "normal") & (pred == "normal")).sum())
    FP = int(((gt == "normal") & (pred == "abnormal")).sum())
    FN = int(((gt == "abnormal") & (pred == "normal")).sum())
    acc = (TP + TN) / len(rows) * 100
    sens = TP / (TP + FN) * 100 if (TP + FN) else 0
    spec = TN / (TN + FP) * 100 if (TN + FP) else 0

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor('#1e293b')

    # Confusion matrix
    ax = axes[0]; ax.set_facecolor('#1e293b')
    cm = np.array([[TN, FP], [FN, TP]])
    ax.imshow(cm, cmap='RdYlGn', aspect='auto')
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(["normal", "abnormal"], color='#94a3b8')
    ax.set_yticklabels(["normal", "abnormal"], color='#94a3b8')
    ax.set_xlabel('Predicted', color='#94a3b8'); ax.set_ylabel('Ground Truth', color='#94a3b8')
    ax.set_title('Triage Confusion Matrix', color='#e2e8f0', fontsize=13, pad=10)
    for i in range(2):
        for j in range(2):
            lbl = ["TN", "FP", "FN", "TP"][i * 2 + j]
            ax.text(j, i, f"{lbl}\n{cm[i,j]}", ha='center', va='center',
                    color='white' if cm[i,j] > cm.max()/2 else '#1e293b', fontsize=14, fontweight='bold')

    # Metrics bars
    ax = axes[1]; ax.set_facecolor('#1e293b')
    bars = ax.bar(["Accuracy", "Sensitivity", "Specificity"], [acc, sens, spec],
                  color=["#7c3aed", "#ef4444", "#10b981"], width=0.5)
    for bar, val in zip(bars, [acc, sens, spec]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{val:.0f}%", ha='center', va='bottom', color='#e2e8f0', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 115); ax.axhline(y=50, color='#475569', linestyle='--', alpha=0.5)
    ax.set_title('Triage Performance', color='#e2e8f0', fontsize=13, pad=10)
    ax.tick_params(colors='#94a3b8'); ax.spines[:].set_color('#475569')
    plt.tight_layout()
    plt.show()
    print(f"Accuracy: {acc:.0f}% | Sensitivity: {sens:.0f}% | Specificity: {spec:.0f}% | TP={TP} TN={TN} FP={FP} FN={FN}")


def display_ecg_triage_from_merged(images, results):
    """Show triage viewer using merged extraction results (have screening_result)."""
    imgs, preds, gts = [], [], []
    for img, r in zip(images, results):
        d = r.get("data")
        if not d:
            continue
        imgs.append(img)
        preds.append({
            "screening_result": d.get("screening_result", ""),
            "confidence": d.get("confidence", ""),
            "findings": d.get("findings", []),
            "clinical_summary": d.get("clinical_summary", ""),
        })
        gt_class = r.get("gt_class", "")
        gt_triage = "normal" if gt_class == "NORM" else "abnormal"
        correct = d.get("screening_result", "").lower() == gt_triage
        gts.append({"gt_triage": gt_triage, "gt_label": gt_class, "correct": correct})
    print(f"{len(imgs)} ECGs")
    _display_ecg_triage_viewer(imgs, preds, gts)


def show_merged_triage_accuracy(results):
    """Confusion matrix for triage from merged extraction results."""
    import matplotlib.pyplot as plt

    rows = []
    for r in results:
        d = r.get("data")
        if not d:
            continue
        gt_class = r.get("gt_class", "")
        gt_triage = "normal" if gt_class == "NORM" else "abnormal"
        pred = d.get("screening_result", "").lower()
        rows.append({"gt": gt_triage, "pred": pred})
    if not rows:
        print("No triage results")
        return

    gt = np.array([r["gt"] for r in rows])
    pred = np.array([r["pred"] for r in rows])
    TP = int(((gt == "abnormal") & (pred == "abnormal")).sum())
    TN = int(((gt == "normal") & (pred == "normal")).sum())
    FP = int(((gt == "normal") & (pred == "abnormal")).sum())
    FN = int(((gt == "abnormal") & (pred == "normal")).sum())
    acc = (TP + TN) / len(rows) * 100
    sens = TP / (TP + FN) * 100 if (TP + FN) else 0
    spec = TN / (TN + FP) * 100 if (TN + FP) else 0

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor('#1e293b')

    ax = axes[0]; ax.set_facecolor('#1e293b')
    cm = np.array([[TN, FP], [FN, TP]])
    ax.imshow(cm, cmap='RdYlGn', aspect='auto')
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(["normal", "abnormal"], color='#94a3b8')
    ax.set_yticklabels(["normal", "abnormal"], color='#94a3b8')
    ax.set_xlabel('Predicted', color='#94a3b8'); ax.set_ylabel('Ground Truth', color='#94a3b8')
    ax.set_title('Triage Confusion Matrix', color='#e2e8f0', fontsize=13, pad=10)
    for i in range(2):
        for j in range(2):
            lbl = ["TN", "FP", "FN", "TP"][i * 2 + j]
            ax.text(j, i, f"{lbl}\n{cm[i,j]}", ha='center', va='center',
                    color='white' if cm[i,j] > cm.max()/2 else '#1e293b', fontsize=14, fontweight='bold')

    ax = axes[1]; ax.set_facecolor('#1e293b')
    bars = ax.bar(["Accuracy", "Sensitivity", "Specificity"], [acc, sens, spec],
                  color=["#7c3aed", "#ef4444", "#10b981"], width=0.5)
    for bar, val in zip(bars, [acc, sens, spec]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{val:.0f}%", ha='center', va='bottom', color='#e2e8f0', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 115); ax.axhline(y=50, color='#475569', linestyle='--', alpha=0.5)
    ax.set_title('Triage Performance', color='#e2e8f0', fontsize=13, pad=10)
    ax.tick_params(colors='#94a3b8'); ax.spines[:].set_color('#475569')
    plt.tight_layout()
    plt.show()
    print(f"Accuracy: {acc:.0f}% | Sensitivity: {sens:.0f}% | Specificity: {spec:.0f}% | TP={TP} TN={TN} FP={FP} FN={FN}")


def display_ecg_predictions(images, predictions, ground_truths, title="ECG Extraction"):
    """KYC-style table viewer for ECG extraction: Image | Field | Pred | GT | Error.

    Args:
        images: list of PIL Images
        predictions: list of dicts with extracted fields (heart_rate_bpm, pr_interval_ms, etc.)
        ground_truths: list of dicts with GT fields (gt_hr, gt_pr, gt_qrs, gt_qt, gt_axis, class, ...)
    """
    # Map pred fields → GT fields + display names
    MEASURE_FIELDS = [
        ("heart_rate_bpm",   "gt_hr",  "Heart Rate",   "bpm"),
        ("pr_interval_ms",   "gt_pr",  "PR Interval",  "ms"),
        ("qrs_duration_ms",  "gt_qrs", "QRS Duration", "ms"),
        ("qt_interval_ms",   "gt_qt",  "QT Interval",  "ms"),
        ("qrs_axis_degrees", "gt_axis","QRS Axis",     "°"),
    ]
    QUAL_FIELDS = ["rhythm", "findings", "clinical_summary"]

    # Build table data
    images_b64 = []
    for img in images:
        buf = BytesIO()
        img.save(buf, format="PNG")
        images_b64.append(base64.b64encode(buf.getvalue()).decode())

    table_data = []
    for pred, gt in zip(predictions, ground_truths):
        rows = []
        # Measurement rows (have GT)
        for pred_key, gt_key, label, unit in MEASURE_FIELDS:
            p = pred.get(pred_key)
            g = gt.get(gt_key)
            pred_str = str(p) if p is not None else "—"
            has_gt = g is not None and not (isinstance(g, float) and np.isnan(g))
            gt_str = f"{g:.0f}" if has_gt else "—"
            if has_gt and p is not None:
                err = abs(float(p) - float(g))
                err_str = f"±{err:.0f} {unit}"
                pct = err / max(abs(float(g)), 1) * 100
                match = "good" if pct < 15 else ("neutral" if pct < 30 else "bad")
            else:
                err_str = "—"
                match = "neutral"
            rows.append({"field": f"{label} ({unit})", "pred": pred_str, "gt": gt_str,
                         "error": err_str, "match": match})
        # Class row
        cls = gt.get("class", gt.get("gt_class", ""))
        if cls:
            rows.append({"field": "Diagnosis (GT)", "pred": "", "gt": cls, "error": "", "match": "neutral"})
        # Qualitative rows
        for key in QUAL_FIELDS:
            val = pred.get(key)
            if val is not None:
                if isinstance(val, list):
                    val_str = "; ".join(str(v) for v in val)
                else:
                    val_str = str(val)
                rows.append({"field": key.replace("_", " ").title(), "pred": val_str, "gt": "", "error": "", "match": "neutral"})
        table_data.append(rows)

    vid = f"ecg_{uuid.uuid4().hex[:8]}"
    total = len(images)
    table_json = json.dumps(table_data)
    images_json = json.dumps(images_b64)

    html = f"""
<style>
#{vid} {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: #d4d4d4;
}}
#{vid} .header {{
    background: linear-gradient(135deg, #6d28d9 0%, #2a9d8f 100%);
    padding: 18px 30px;
    border-radius: 12px;
    margin-bottom: 14px;
    text-align: center;
}}
#{vid} .header h1 {{
    color: white; margin: 0; font-size: 24px; letter-spacing: 2px;
}}
#{vid} .header p {{
    color: #e2e8f0; margin: 6px 0 0 0; font-size: 13px;
}}
#{vid} .nav {{
    display: flex; align-items: center; justify-content: center; gap: 12px;
    margin-bottom: 14px;
}}
#{vid} .nav button {{
    background: #334155; color: #d4d4d4; border: 1px solid #475569;
    padding: 8px 18px; border-radius: 6px; cursor: pointer; font-size: 14px;
}}
#{vid} .nav button:hover {{ background: #475569; }}
#{vid} .nav span {{ color: #94a3b8; font-size: 14px; min-width: 100px; text-align: center; }}
#{vid} .content {{
    display: flex; gap: 16px; align-items: flex-start;
}}
#{vid} .img-panel {{
    flex: 0 0 45%; max-width: 45%;
}}
#{vid} .img-panel img {{
    width: 100%; border-radius: 8px; border: 1px solid #475569;
}}
#{vid} .table-panel {{
    flex: 1; overflow-x: auto;
}}
#{vid} table {{
    width: 100%; border-collapse: collapse; font-size: 13px;
}}
#{vid} th {{
    background: #1e293b; color: #8ecae6; padding: 6px 10px;
    text-align: left; border-bottom: 2px solid #6d28d9;
    font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 1px;
}}
#{vid} td {{
    padding: 6px 10px; border-bottom: 1px solid #334155;
    vertical-align: top; word-break: break-word; text-align: left;
}}
#{vid} tr.good td {{ background: rgba(16, 185, 129, 0.08); }}
#{vid} tr.bad td {{ background: rgba(239, 68, 68, 0.10); }}
#{vid} tr.neutral td {{ background: transparent; }}
#{vid} td.field-name {{
    color: #81b4d8; font-weight: 600; white-space: nowrap; width: 140px;
}}
#{vid} td.pred {{ color: #d4d4d4; max-width: 200px; }}
#{vid} td.gt {{ color: #a7c4bc; }}
#{vid} td.err {{ color: #94a3b8; font-size: 12px; }}
#{vid} tr.good td.field-name::after {{
    content: ' ✓'; color: #7bc47f; font-size: 11px;
}}
#{vid} tr.bad td.field-name::after {{
    content: ' ✗'; color: #ef4444; font-size: 11px;
}}
</style>

<div id="{vid}">
    <div class="header">
        <h1>{title.upper()}</h1>
        <p>Structured extraction vs PTB-XL+ ground truth &mdash; Field | Prediction | GT | Error</p>
    </div>
    <div class="nav">
        <button onclick="{vid}_go(-1)">&larr; Prev</button>
        <span id="{vid}_counter">1 / {total}</span>
        <button onclick="{vid}_go(1)">Next &rarr;</button>
    </div>
    <div class="content">
        <div class="img-panel">
            <img id="{vid}_img" src="" />
        </div>
        <div class="table-panel">
            <table>
                <thead><tr>
                    <th>Field</th>
                    <th>Prediction</th>
                    <th>Ground Truth</th>
                    <th>Error</th>
                </tr></thead>
                <tbody id="{vid}_tbody"></tbody>
            </table>
        </div>
    </div>
</div>

<script>
(function() {{
    var imgs = {images_json};
    var data = {table_json};
    var cur = 0;
    var total = {total};

    function render(i) {{
        document.getElementById('{vid}_img').src = 'data:image/png;base64,' + imgs[i];
        document.getElementById('{vid}_counter').textContent = (i+1) + ' / ' + total;
        var rows = data[i];
        var html = '';
        for (var r = 0; r < rows.length; r++) {{
            var d = rows[r];
            html += '<tr class="' + d.match + '">';
            html += '<td class="field-name">' + d.field + '</td>';
            html += '<td class="pred">' + (d.pred || '&mdash;') + '</td>';
            html += '<td class="gt">' + (d.gt || '&mdash;') + '</td>';
            html += '<td class="err">' + (d.error || '') + '</td>';
            html += '</tr>';
        }}
        document.getElementById('{vid}_tbody').innerHTML = html;
    }}

    window['{vid}_go'] = function(dir) {{
        cur = (cur + dir + total) % total;
        render(cur);
    }};

    render(0);
}})();
</script>
"""
    display(HTML(html))


def display_document_analysis(image_input, predictions, width='100%', title='Model Predictions', ground_truth=None, filter_dropdowns=None, query=None, query_image=None, query_label=None, display_map=None):
    """
    Display document image(s) alongside model predictions in a 2-or-3-column layout.
    Pure HTML/JS implementation for VSCode compatibility with filtering.

    Args:
        image_input: PIL Image, path to image, or list of either
        predictions: dict/JSON string, or list of dicts/JSON strings
        width: width of the display container (default: '100%')
        title: panel heading shown above predictions (default: 'Model Predictions')
        ground_truth: optional list of dicts with GT metadata (one per image)
        filter_dropdowns: optional dict of {pred_key: [value1, value2, ...]} for quick-filter dropdowns
        query: optional RAG query string to display as viewer title
        query_image: optional PIL Image to show as search query thumbnail in header
        display_map: optional dict {display_name: field_name_or_callable} to remap prediction fields
    """
    # Normalize inputs to lists
    if not isinstance(image_input, list):
        image_input = [image_input]
    if not isinstance(predictions, list):
        predictions = [predictions]

    assert len(image_input) == len(predictions), f"Images and predictions must have same length"

    # Auto-filter error entries
    if any(isinstance(p, dict) and "_error" in p for p in predictions):
        ok_mask = [not (isinstance(p, dict) and "_error" in p) for p in predictions]
        image_input = [img for img, ok in zip(image_input, ok_mask) if ok]
        predictions = [p for p, ok in zip(predictions, ok_mask) if ok]
        if ground_truth is not None:
            if not isinstance(ground_truth, list):
                ground_truth = [ground_truth]
            ground_truth = [gt for gt, ok in zip(ground_truth, ok_mask) if ok]
        if not image_input:
            print("[warn] All predictions are errors -- nothing to display")
            return
    
    # Convert all images to base64
    images_b64 = []
    image_names = []
    
    for idx, img_input in enumerate(image_input):
        if isinstance(img_input, (str, Path)):
            img = Image.open(img_input)
            img_name = Path(img_input).name
        else:
            img = img_input
            img_name = f"Document {idx + 1}"
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        images_b64.append(img_str)
        image_names.append(img_name)
    
    # Convert predictions to proper format
    preds_list = []
    for pred in predictions:
        if isinstance(pred, str):
            preds_list.append(json.loads(pred))
        else:
            preds_list.append(pred)

    # Apply display_map: remap fields for display
    if display_map:
        preds_list = [
            {display_name: (mapper(p) if callable(mapper) else p.get(mapper, ""))
             for display_name, mapper in display_map.items()}
            for p in preds_list
        ]

    # Generate unique ID for this viewer
    viewer_id = f"viewer_{uuid.uuid4().hex[:8]}"

    # Normalize ground truth
    gt_list = None
    if ground_truth is not None:
        if not isinstance(ground_truth, list):
            ground_truth = [ground_truth]
        gt_list = []
        for gt in ground_truth:
            if isinstance(gt, str):
                gt_list.append(json.loads(gt))
            else:
                gt_list.append(gt if gt else {})

    # Build HTML
    # Encode query image thumbnail if provided
    query_image_b64 = None
    if query_image is not None:
        qi = query_image
        if isinstance(qi, str):
            qi = Image.open(qi)
        qi = qi.copy()
        qi.thumbnail((128, 128))
        buf = BytesIO()
        qi.save(buf, format="PNG")
        query_image_b64 = base64.b64encode(buf.getvalue()).decode()

    html = _build_viewer_html(images_b64, image_names, preds_list, viewer_id, width, title=title, ground_truth=gt_list, filter_dropdowns=filter_dropdowns, query=query, query_image_b64=query_image_b64, query_label=query_label)

    display(HTML(html))


def execute_rag_query(search_func, query, top_k=5, filters=None, extra_fields=None, show_top_n=3, show_gt=False, **search_kwargs):
    """
    Execute a RAG query and display results with standard formatting.
    Abstracts away repetitive query execution and display code.

    Args:
        search_func: The search function to call (e.g., search_medical_documents)
        query: Natural language search query string
        top_k: Number of results to return (default: 5)
        filters: Optional dict of filters to apply (default: None)
        extra_fields: Optional function to add extra fields to result docs (default: None)
                     Should take (doc, similarity) and return dict of extra fields
        show_top_n: Number of top results to print summary for (default: 3)

    Returns:
        results: The raw results from search_func for further processing if needed

    Example:
        # Simple query
        execute_rag_query(search_medical_documents, "chest X-ray reports")

        # With custom extra fields
        def add_meds_field(doc, similarity):
            if doc.get('medications'):
                return {'medications_found': ', '.join(doc['medications'][:3])}
            return {}

        execute_rag_query(
            search_medical_documents,
            "blood pressure medications",
            extra_fields=add_meds_field
        )
    """
    print(f"Query: '{query}'\n")

    # Execute search
    results = search_func(query, top_k=top_k, filters=filters, **search_kwargs)

    print(f"[ok] Found {len(results)} relevant documents\n")

    if len(results) == 0:
        print("[warn] No results found")
        return results

    # Prepare data for display
    result_images = [img for _, _, img in results]
    result_docs = []

    for doc, similarity, _ in results:
        result_doc = dict(doc)
        result_doc['similarity_score'] = f"{similarity:.3f}"

        # Add any extra fields if provided
        if extra_fields:
            extra = extra_fields(doc, similarity)
            if extra:
                result_doc.update(extra)

        result_docs.append(result_doc)

    # Collect GT from results (attached during extraction as _gt)
    gt_arg = None
    if show_gt:
        result_gt = [doc.get('_gt') for doc, _, _ in results]
        if any(g for g in result_gt):
            gt_arg = result_gt

    # Display interactive gallery
    display_document_analysis(result_images, result_docs, ground_truth=gt_arg, query=query)

    return results


def display_rag_results(results, query=None, query_image=None, query_label=None):
    """Display search results from search_by_image or similar (doc, score, img) tuples."""
    imgs = [img for _, _, img in results]
    preds = [dict(d, similarity_score=f"{s:.3f}") for d, s, _ in results]
    display_document_analysis(imgs, preds, query=query, query_image=query_image, query_label=query_label)


def _build_viewer_html(images_b64, image_names, predictions, viewer_id, width, title='Model Predictions', ground_truth=None, filter_dropdowns=None, query=None, query_image_b64=None, query_label=None):
    """Build the complete HTML viewer with dark mode friendly styling and filtering."""

    has_gt = ground_truth is not None and len(ground_truth) > 0

    # Create JSON data for all documents
    docs_data = []
    for i, (img_b64, img_name, pred) in enumerate(zip(images_b64, image_names, predictions)):
        doc = {
            'id': i,
            'image': img_b64,
            'name': img_name,
            'predictions': pred,
        }
        if has_gt and i < len(ground_truth):
            doc['ground_truth'] = ground_truth[i]
        docs_data.append(doc)

    docs_json  = json.dumps(docs_data)
    title_json = json.dumps(title)
    has_gt_json = json.dumps(has_gt)
    query_json = json.dumps(query) if query else 'null'

    # Build filter dropdown HTML
    dropdowns_html = ''
    if filter_dropdowns:
        for dd_key, dd_values in filter_dropdowns.items():
            opts = f'<option value="">All {dd_key}</option>'
            for v in dd_values:
                opts += f'<option value="{v}">{v}</option>'
            dropdowns_html += f'<select class="filter-dropdown" onchange="window.viewer_{viewer_id}_instance.dropdownFilter(\'{dd_key}\', this.value)">{opts}</select>'

    html = f"""
    <div id="{viewer_id}" style="width: {width}; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <style>
            #{viewer_id} .nav-container {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
                padding: 10px 15px;
                background: #1e293b;
                border-radius: 6px;
                border: 1px solid #334155;
                gap: 20px;
            }}
            #{viewer_id} .filter-display {{
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
                align-items: center;
                flex: 1;
            }}
            #{viewer_id} .filter-label {{
                color: #94a3b8;
                font-size: 13px;
                font-weight: 500;
                margin-right: 4px;
            }}
            #{viewer_id} .filter-placeholder {{
                color: #64748b;
                font-size: 13px;
                font-style: italic;
            }}
            #{viewer_id} .filter-box {{
                background: #d32f2f;
                color: #ffffff;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 12px;
                display: flex;
                align-items: center;
                gap: 6px;
                border: 1px solid #b71c1c;
            }}
            #{viewer_id} .filter-box-text {{
                white-space: nowrap;
            }}
            #{viewer_id} .filter-close {{
                cursor: pointer;
                font-weight: bold;
                padding: 0 3px;
                border-radius: 2px;
                background: rgba(0,0,0,0.2);
                font-size: 14px;
                line-height: 1;
            }}
            #{viewer_id} .filter-close:hover {{
                background: rgba(0,0,0,0.4);
            }}
            #{viewer_id} .nav-controls {{
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 15px;
            }}
            #{viewer_id} .nav-btn {{
                padding: 6px 14px;
                background: #2a9d8f;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 13px;
                font-weight: 500;
            }}
            #{viewer_id} .nav-btn:hover {{
                background: #3db8a9;
            }}
            #{viewer_id} .nav-btn:disabled {{
                background: #334155;
                cursor: not-allowed;
                color: #475569;
            }}
            #{viewer_id} .nav-input {{
                width: 50px;
                padding: 5px;
                text-align: center;
                border: 1px solid #334155;
                border-radius: 4px;
                font-size: 13px;
                background: #0f172a;
                color: #e2e8f0;
            }}
            #{viewer_id} .nav-text {{
                color: #94a3b8;
                font-size: 13px;
            }}
            #{viewer_id} .content-layout {{
                display: flex;
                gap: 10px;
                width: 100%;
            }}
            #{viewer_id} .image-panel {{
                flex: 1;
                height: 600px;
                overflow: auto;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 10px;
                background: #0f172a;
                box-sizing: border-box;
            }}
            #{viewer_id} .preds-panel {{
                flex: 1;
                height: 600px;
                overflow: auto;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 10px;
                background: #1e293b;
                box-sizing: border-box;
            }}
            #{viewer_id} .gt-panel {{
                flex: 1;
                height: 600px;
                overflow: auto;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 10px;
                background: #0f172a;
                box-sizing: border-box;
            }}
            #{viewer_id} .gt-title {{
                margin: 0 0 12px 0;
                padding: 0 0 10px 0;
                color: #10b981;
                border-bottom: 2px solid #10b981;
                font-size: 18px;
            }}
            #{viewer_id} .gt-item {{
                margin-bottom: 6px;
                padding: 8px 10px;
                border-left: 3px solid #334155;
                background: #1e293b;
                border-radius: 4px;
                display: flex;
                align-items: baseline;
                gap: 10px;
            }}
            #{viewer_id} .gt-key {{
                font-weight: 600;
                color: #6ee7b7;
                font-size: 12px;
                min-width: 120px;
                flex-shrink: 0;
                text-transform: uppercase;
                letter-spacing: 0.03em;
            }}
            #{viewer_id} .gt-value {{
                font-size: 13px;
                color: #e2e8f0;
                flex: 1;
            }}
            #{viewer_id} .gt-empty {{
                color: #6b7280;
                font-style: italic;
                font-size: 13px;
                padding: 20px;
                text-align: center;
            }}
            #{viewer_id} .img-name {{
                text-align: center;
                color: #94a3b8;
                font-size: 12px;
                margin-bottom: 8px;
                font-weight: 500;
            }}
            #{viewer_id} .doc-img {{
                max-width: 100%;
                height: auto;
                display: block;
                margin: auto;
            }}
            #{viewer_id} .pred-title {{
                margin: 0 0 12px 0;
                padding: 0 0 10px 0;
                color: #8ecae6;
                border-bottom: 2px solid #2a9d8f;
                font-size: 18px;
            }}
            #{viewer_id} .special-sections {{
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
                border: 2px solid #2a9d8f;
                box-shadow: 0 4px 12px rgba(42, 157, 143, 0.2);
            }}
            #{viewer_id} .special-section {{
                margin-bottom: 12px;
                padding-bottom: 12px;
                border-bottom: 1px solid #334155;
            }}
            #{viewer_id} .special-section:last-child {{
                border-bottom: none;
                margin-bottom: 0;
                padding-bottom: 0;
            }}
            #{viewer_id} .section-header {{
                font-weight: 700;
                color: #8ecae6;
                font-size: 13px;
                margin-bottom: 6px;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            #{viewer_id} .section-content {{
                color: #e2e8f0;
                font-size: 14px;
                line-height: 1.6;
            }}
            #{viewer_id} .similarity-badge {{
                display: inline-block;
                background: #2a9d8f;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-weight: 600;
                font-size: 14px;
            }}
            #{viewer_id} .medication-item {{
                background: #1e293b;
                padding: 6px 10px;
                margin: 4px 0;
                border-radius: 4px;
                border-left: 3px solid #10b981;
                font-size: 13px;
            }}
            #{viewer_id} .keyword-tag-special {{
                background: #2a9d8f;
                color: white;
                padding: 4px 10px;
                border-radius: 4px;
                margin: 3px;
                display: inline-block;
                font-size: 12px;
                cursor: pointer;
                transition: background 0.2s;
            }}
            #{viewer_id} .keyword-tag-special:hover {{
                background: #3db8a9;
            }}
            #{viewer_id} .pred-content {{
                padding: 0;
            }}
            #{viewer_id} .pred-item {{
                margin-bottom: 8px;
                padding: 10px 12px;
                border-left: 3px solid #334155;
                background: #0f172a;
                border-radius: 4px;
                display: flex;
                align-items: baseline;
                gap: 12px;
            }}
            #{viewer_id} .pred-key {{
                font-weight: 600;
                color: #8ecae6;
                font-size: 13px;
                min-width: 160px;
                flex-shrink: 0;
                text-align: left;
            }}
            #{viewer_id} .pred-value {{
                font-size: 13px;
                color: #cbd5e1;
                flex: 1;
                text-align: left;
                max-height: 4.5em;
                overflow: hidden;
                position: relative;
            }}
            #{viewer_id} .pred-value.truncated::after {{
                content: '...';
                position: absolute;
                bottom: 0;
                right: 0;
                background: #0f172a;
                padding-left: 4px;
                color: #64748b;
            }}
            #{viewer_id} .pred-tooltip {{
                position: fixed;
                display: none;
                background: #0f172a;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 12px;
                max-width: 500px;
                max-height: 300px;
                overflow-y: auto;
                word-break: break-word;
                z-index: 9999;
                line-height: 1.5;
                box-shadow: 0 4px 12px rgba(0,0,0,0.5);
                pointer-events: none;
            }}
            #{viewer_id} .tag {{
                background: #2a9d8f;
                color: #ffffff;
                padding: 3px 8px;
                border-radius: 3px;
                margin: 2px;
                display: inline-block;
                font-size: 12px;
                cursor: pointer;
                transition: background 0.2s;
            }}
            #{viewer_id} .tag:hover {{
                background: #3db8a9;
            }}
            #{viewer_id} .bool-true {{
                color: #7bc47f;
                font-weight: bold;
                cursor: pointer;
            }}
            #{viewer_id} .bool-false {{
                color: #64748b;
                font-weight: bold;
                cursor: pointer;
            }}
            #{viewer_id} .number {{
                color: #e8b96a;
                font-weight: 500;
                cursor: pointer;
            }}
            #{viewer_id} .null {{
                color: #64748b;
                font-style: italic;
            }}
            #{viewer_id} .clickable {{
                cursor: pointer;
                text-decoration: underline;
                text-decoration-style: dotted;
                text-underline-offset: 2px;
            }}
            #{viewer_id} .clickable:hover {{
                color: #8ecae6;
            }}
            /* ── Search bar ─────────────────────────────────── */
            #{viewer_id} .search-box {{
                flex: 0 0 180px;
            }}
            #{viewer_id} .search-input {{
                width: 100%;
                padding: 6px 10px;
                border: 1px solid #334155;
                border-radius: 4px;
                font-size: 12px;
                background: #0f172a;
                color: #e2e8f0;
                outline: none;
                box-sizing: border-box;
            }}
            #{viewer_id} .search-input:focus {{
                border-color: #2a9d8f;
            }}
            #{viewer_id} .search-input::placeholder {{
                color: #475569;
            }}
            /* ── Filter dropdowns ──────────────────────────── */
            #{viewer_id} .filter-dropdown {{
                padding: 6px 10px;
                border: 1px solid #334155;
                border-radius: 4px;
                font-size: 12px;
                background: #0f172a;
                color: #e2e8f0;
                outline: none;
                cursor: pointer;
                min-width: 120px;
            }}
            #{viewer_id} .filter-dropdown:focus {{
                border-color: #2a9d8f;
            }}
            /* ── Progress bar ───────────────────────────────── */
            #{viewer_id} .progress-track {{
                height: 3px;
                background: #0f172a;
                border-radius: 2px;
                margin-bottom: 6px;
                overflow: hidden;
            }}
            #{viewer_id} .progress-fill {{
                height: 100%;
                background: linear-gradient(90deg, #2a9d8f, #8ecae6);
                border-radius: 2px;
                transition: width 0.3s ease;
            }}
            /* ── Thumbnail strip ────────────────────────────── */
            #{viewer_id} .thumb-strip {{
                display: flex;
                gap: 4px;
                overflow-x: auto;
                padding: 4px 0 8px 0;
                margin-bottom: 8px;
                scrollbar-width: thin;
                scrollbar-color: #334155 transparent;
            }}
            #{viewer_id} .thumb-strip::-webkit-scrollbar {{
                height: 4px;
            }}
            #{viewer_id} .thumb-strip::-webkit-scrollbar-thumb {{
                background: #334155;
                border-radius: 2px;
            }}
            #{viewer_id} .thumb {{
                flex: 0 0 48px;
                height: 36px;
                border-radius: 3px;
                overflow: hidden;
                cursor: pointer;
                border: 2px solid transparent;
                opacity: 0.5;
                transition: all 0.2s ease;
            }}
            #{viewer_id} .thumb:hover {{
                opacity: 0.8;
                border-color: #8ecae6;
            }}
            #{viewer_id} .thumb.active {{
                opacity: 1;
                border-color: #2a9d8f;
                box-shadow: 0 0 6px rgba(42, 157, 143, 0.5);
            }}
            #{viewer_id} .thumb img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            /* ── Fade transition ────────────────────────────── */
            #{viewer_id} .fade-target {{
                transition: opacity 0.15s ease;
            }}
            #{viewer_id} .fade-target.fading {{
                opacity: 0.3;
            }}
            /* ── Status bar ──────────────────────────────── */
            #{viewer_id} .status-bar {{
                display: flex;
                align-items: center;
                gap: 14px;
                padding: 6px 10px;
                background: #0f172a;
                border: 1px solid #334155;
                border-radius: 5px;
                margin-bottom: 12px;
                font-size: 11px;
                color: #94a3b8;
            }}
            #{viewer_id} .status-bar .stat {{
                display: flex;
                align-items: center;
                gap: 4px;
                white-space: nowrap;
            }}
            #{viewer_id} .status-bar .stat-val {{
                color: #e2e8f0;
                font-weight: 600;
            }}
            /* ── Confidence pills ───────────────────────────── */
            #{viewer_id} .conf-pill {{
                display: inline-block;
                padding: 1px 6px;
                border-radius: 8px;
                font-size: 10px;
                font-weight: 700;
                margin-left: 6px;
                vertical-align: middle;
            }}
            /* ── Viewer title (inside nav-container) ────────── */
            #{viewer_id} .viewer-title {{
                display: flex;
                align-items: center;
                gap: 10px;
                white-space: nowrap;
            }}
            #{viewer_id} .viewer-title-main {{
                color: #8ecae6;
                font-size: 13px;
                font-weight: 600;
                margin: 0;
                opacity: 0.7;
            }}
            #{viewer_id} .query-thumb {{
                width: 36px;
                height: 36px;
                object-fit: cover;
                border-radius: 4px;
                border: 2px solid #6366f1;
                cursor: pointer;
                transition: all 0.2s;
            }}
            #{viewer_id} .query-thumb:hover {{
                transform: scale(2.5);
                z-index: 100;
                border-color: #a78bfa;
                box-shadow: 0 4px 20px rgba(99,102,241,0.5);
            }}
            #{viewer_id} .viewer-title-sub {{
                color: #f1f5f9;
                font-size: 16px;
                font-weight: 700;
                font-style: italic;
                background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(14,165,233,0.15));
                padding: 3px 12px;
                border-radius: 6px;
                border-left: 3px solid #6366f1;
            }}
            /* ── Image zoom lightbox ────────────────────────── */
            #{viewer_id} .doc-img {{
                cursor: zoom-in;
            }}
            #{viewer_id} .lightbox {{
                display: none;
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0,0,0,0.85);
                z-index: 10000;
                cursor: zoom-out;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            #{viewer_id} .lightbox.open {{
                display: flex;
            }}
            #{viewer_id} .lightbox img {{
                max-width: 95vw;
                max-height: 95vh;
                object-fit: contain;
                border-radius: 6px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.6);
            }}
            #{viewer_id} .lightbox-hint {{
                position: absolute;
                bottom: 16px;
                left: 50%;
                transform: translateX(-50%);
                color: #64748b;
                font-size: 11px;
                pointer-events: none;
            }}
            /* ── Export button ───────────────────────────────── */
            #{viewer_id} .export-btn {{
                padding: 4px 10px;
                background: #334155;
                color: #94a3b8;
                border: 1px solid #475569;
                border-radius: 4px;
                cursor: pointer;
                font-size: 11px;
                white-space: nowrap;
            }}
            #{viewer_id} .export-btn:hover {{
                background: #475569;
                color: #e2e8f0;
            }}
            /* ── Dataset source badge (nav) ─────────────────── */
            #{viewer_id} .src-badge {{
                display: inline-block;
                padding: 2px 8px;
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 10px;
                font-size: 10px;
                color: #64748b;
                font-family: monospace;
                margin-left: 6px;
            }}
        </style>

        <div class="lightbox" id="lightbox_{viewer_id}" onclick="this.classList.remove('open')">
            <img id="lightbox_img_{viewer_id}" src="">
            <div class="lightbox-hint">Click anywhere or press Esc to close</div>
        </div>

        <div class="nav-container">
            {"" if not query and not query_image_b64 else f'''<div class="viewer-title">
                <span class="viewer-title-main">{"Search Image:" if query_image_b64 else "RAG Search Results"}</span>
                {"" if not query_image_b64 else f'<img class="query-thumb" src="data:image/png;base64,{query_image_b64}" title="{query_label or "Query image"}">' + (f'<span style="background:#334155;color:#e2e8f0;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;margin-left:4px">{query_label}</span>' if query_label else '')}
                {"" if not query else f'<span class="viewer-title-sub">&ldquo;{query}&rdquo;</span>'}
            </div>'''}
            <div class="filter-display" id="filter_display_{viewer_id}">
                <span class="filter-placeholder">No Filters Applied</span>
            </div>

            {dropdowns_html}

            <div class="search-box">
                <input type="text" class="search-input" id="search_{viewer_id}" placeholder="Search docs..." oninput="window.viewer_{viewer_id}_instance.searchDocs(this.value)">
            </div>

            <div class="nav-controls">
                <button class="nav-btn" onclick="window.viewer_{viewer_id}_instance.prevDoc()">←</button>
                <span>
                    <input type="number" class="nav-input" id="jump_{viewer_id}" value="1" min="1" max="{len(images_b64)}" onchange="window.viewer_{viewer_id}_instance.jumpDoc(this.value)">
                    <span class="nav-text"> / <span id="total_count_{viewer_id}">{len(images_b64)}</span></span>
                </span>
                <button class="nav-btn" onclick="window.viewer_{viewer_id}_instance.nextDoc()">→</button>
                <button class="export-btn" onclick="window.viewer_{viewer_id}_instance.exportJson()" title="Copy current doc JSON to clipboard">📋 Export</button>
            </div>
        </div>

        <div class="progress-track"><div class="progress-fill" id="progress_{viewer_id}" style="width:0%"></div></div>
        <div style="text-align:right;padding:0 4px 2px 0;color:#475569;font-size:10px;letter-spacing:0.04em;">← → navigate &nbsp;·&nbsp; Esc close zoom</div>

        <div class="thumb-strip" id="thumbs_{viewer_id}"></div>
        
        <div class="content-layout" tabindex="0" id="content_{viewer_id}" style="outline:none;"
             onkeydown="window.viewer_{viewer_id}_instance.onKey(event)">
            <div class="image-panel fade-target" id="imgpanel_{viewer_id}">
                <div class="img-name" id="img_name_{viewer_id}"></div>
                <img class="doc-img" id="img_{viewer_id}" src="">
            </div>
            <div class="preds-panel fade-target" id="preds_{viewer_id}"></div>
            {"" if not has_gt else f'<div class="gt-panel fade-target" id="gt_{viewer_id}"></div>'}
        </div>
        
        <script>
            (function() {{
                const allDocs = {docs_json};
                let filteredDocs = [...allDocs];
                let currentIdx = 0;
                let activeFilters = {{}};

                // HTML escape helper
                function _escHtml(s) {{
                    const d = document.createElement('div');
                    d.textContent = s;
                    return d.innerHTML;
                }}

                // Global Esc key to close lightbox (works regardless of focus)
                document.addEventListener('keydown', function(e) {{
                    if (e.key === 'Escape') {{
                        document.getElementById('lightbox_{viewer_id}').classList.remove('open');
                    }}
                }});

                // Shared tooltip for truncated pred-value cells
                const _pvTooltip = document.createElement('div');
                _pvTooltip.className = 'pred-tooltip';
                document.getElementById('{viewer_id}').appendChild(_pvTooltip);

                // ── Build thumbnail strip ────────────────────────────────
                const thumbStrip = document.getElementById('thumbs_{viewer_id}');
                allDocs.forEach((doc, idx) => {{
                    const t = document.createElement('div');
                    t.className = 'thumb' + (idx === 0 ? ' active' : '');
                    t.dataset.idx = idx;
                    if (doc.image) {{
                        const tImg = document.createElement('img');
                        tImg.src = 'data:image/png;base64,' + doc.image;
                        tImg.loading = 'lazy';
                        t.appendChild(tImg);
                    }}
                    t.onclick = () => {{
                        const fi = filteredDocs.findIndex(d => d.id === idx);
                        if (fi >= 0) {{
                            currentIdx = fi;
                            showDoc(currentIdx);
                        }}
                    }};
                    thumbStrip.appendChild(t);
                }});

                let searchTerm = '';

                function updateThumbs() {{
                    const thumbs = thumbStrip.querySelectorAll('.thumb');
                    thumbs.forEach(t => {{
                        const docIdx = parseInt(t.dataset.idx);
                        const inFiltered = filteredDocs.some(d => d.id === docIdx);
                        t.style.display = inFiltered ? '' : 'none';
                        t.classList.toggle('active', filteredDocs[currentIdx] && filteredDocs[currentIdx].id === docIdx);
                    }});
                    // Auto-scroll active thumb into view
                    const active = thumbStrip.querySelector('.thumb.active');
                    if (active) active.scrollIntoView({{ block: 'nearest', inline: 'center', behavior: 'smooth' }});
                }}

                function updateProgress() {{
                    const pct = filteredDocs.length > 1
                        ? (currentIdx / (filteredDocs.length - 1)) * 100 : 100;
                    document.getElementById('progress_{viewer_id}').style.width = pct + '%';
                }}

                function fadeTransition(fn) {{
                    const panels = document.querySelectorAll('#{viewer_id} .fade-target');
                    panels.forEach(p => p.classList.add('fading'));
                    setTimeout(() => {{
                        fn();
                        panels.forEach(p => p.classList.remove('fading'));
                    }}, 100);
                }}

                function applyFilter(key, value) {{
                    const filterKey = `${{key}}:${{JSON.stringify(value)}}`;
                    if (!activeFilters[filterKey]) {{
                        activeFilters[filterKey] = {{ key, value }};
                        updateFilters();
                    }}
                }}
                
                function removeFilter(filterKey) {{
                    delete activeFilters[filterKey];
                    updateFilters();
                }}
                
                function updateFilters() {{
                    // Apply all filters + search term
                    filteredDocs = allDocs.filter(doc => {{
                        // Tag filters
                        for (const [filterKey, filter] of Object.entries(activeFilters)) {{
                            const docValue = doc.predictions[filter.key];
                            if (Array.isArray(docValue)) {{
                                if (!docValue.includes(filter.value)) return false;
                            }} else {{
                                if (docValue !== filter.value) return false;
                            }}
                        }}
                        // Text search
                        if (searchTerm) {{
                            const haystack = JSON.stringify(doc.predictions).toLowerCase();
                            if (!haystack.includes(searchTerm)) return false;
                        }}
                        return true;
                    }});
                    
                    // Update filter display
                    const filterDisplay = document.getElementById('filter_display_{viewer_id}');
                    filterDisplay.innerHTML = '';
                    
                    if (Object.keys(activeFilters).length === 0) {{
                        const placeholder = document.createElement('span');
                        placeholder.className = 'filter-placeholder';
                        placeholder.textContent = 'No Filters Applied';
                        filterDisplay.appendChild(placeholder);
                    }} else {{
                        // Add "Filters Applied:" label
                        const label = document.createElement('span');
                        label.className = 'filter-label';
                        label.textContent = 'Filters Applied:';
                        filterDisplay.appendChild(label);
                        
                        // Add each filter box
                        for (const [filterKey, filter] of Object.entries(activeFilters)) {{
                            const displayKey = filter.key.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                            const displayValue = typeof filter.value === 'boolean' ? 
                                (filter.value ? '✓' : '✗') : filter.value;
                            
                            const box = document.createElement('div');
                            box.className = 'filter-box';
                            
                            const textSpan = document.createElement('span');
                            textSpan.className = 'filter-box-text';
                            textSpan.textContent = `${{displayKey}}: ${{displayValue}}`;
                            
                            const closeSpan = document.createElement('span');
                            closeSpan.className = 'filter-close';
                            closeSpan.textContent = '✕';
                            closeSpan.onclick = () => removeFilter(filterKey);
                            
                            box.appendChild(textSpan);
                            box.appendChild(closeSpan);
                            filterDisplay.appendChild(box);
                        }}
                    }}
                    
                    document.getElementById('total_count_{viewer_id}').textContent = filteredDocs.length;
                    document.getElementById('jump_{viewer_id}').max = filteredDocs.length;
                    
                    // Reset to first document
                    currentIdx = 0;
                    if (filteredDocs.length > 0) {{
                        showDoc(currentIdx);
                    }} else {{
                        document.getElementById('img_{viewer_id}').src = '';
                        document.getElementById('img_name_{viewer_id}').textContent = 'No documents match filters';
                        document.getElementById('preds_{viewer_id}').innerHTML = '<p style="color: #888;">No documents found</p>';
                    }}
                    updateThumbs();
                    updateProgress();
                }}
                
                function showDoc(idx) {{
                    if (filteredDocs.length === 0) return;

                    const doc = filteredDocs[idx];

                    // Fade transition
                    const panels = document.querySelectorAll('#{viewer_id} .fade-target');
                    panels.forEach(p => p.classList.add('fading'));
                    setTimeout(() => {{ panels.forEach(p => p.classList.remove('fading')); }}, 150);

                    const docImg = document.getElementById('img_{viewer_id}');
                    docImg.src = 'data:image/png;base64,' + doc.image;
                    docImg.style.cursor = 'zoom-in';
                    docImg.onclick = function() {{
                        const lb = document.getElementById('lightbox_{viewer_id}');
                        document.getElementById('lightbox_img_{viewer_id}').src = this.src;
                        lb.classList.add('open');
                    }};
                    document.getElementById('img_name_{viewer_id}').textContent = doc.name;
                    updateThumbs();
                    updateProgress();
                    
                    const predsPanel = document.getElementById('preds_{viewer_id}');
                    predsPanel.innerHTML = '';
                    
                    // Add title
                    const title = document.createElement('h3');
                    title.className = 'pred-title';
                    title.textContent = {title_json};
                    predsPanel.appendChild(title);

                    // ── Status bar (real metrics) ────────────────────────────
                    if (doc.predictions._status !== 'error') {{
                        const totalFields = Object.keys(doc.predictions).filter(k => !k.startsWith('_') && k !== 'confidence').length;
                        const filledFields = Object.entries(doc.predictions).filter(([k,v]) => {{
                            if (k.startsWith('_') || k === 'confidence') return false;
                            if (v === null || v === undefined || v === '') return false;
                            if (Array.isArray(v) && v.length === 0) return false;
                            return true;
                        }}).length;
                        const timing = doc.predictions._timing;
                        const tokens = doc.predictions._tokens;
                        const bar = document.createElement('div');
                        bar.className = 'status-bar';
                        let stats = `<span class="stat">✅ <span class="stat-val">${{filledFields}}/${{totalFields}}</span> fields</span>`;
                        if (timing !== undefined) stats += `<span class="stat">⏱ <span class="stat-val">${{Number(timing).toFixed(1)}}s</span></span>`;
                        if (tokens !== undefined) stats += `<span class="stat">📊 <span class="stat-val">${{tokens}}</span> tok</span>`;
                        // Overall model confidence (from confidence object)
                        const conf = doc.predictions.confidence;
                        if (conf && conf.overall !== undefined) {{
                            const ov = Math.round(conf.overall * 100);
                            const cc = ov >= 75 ? '#10b981' : ov >= 50 ? '#f59e0b' : '#ef4444';
                            stats += `<span class="stat">🎯 <span class="stat-val" style="color:${{cc}}">${{ov}}%</span> confidence</span>`;
                        }}
                        bar.innerHTML = stats;
                        predsPanel.appendChild(bar);
                    }}

                    // ── Failure banner ────────────────────────────────────────
                    if (doc.predictions._status === 'error') {{
                        const errBanner = document.createElement('div');
                        errBanner.style.cssText = [
                            'background:#3d1515','border-left:4px solid #e76f51',
                            'border-radius:6px','padding:12px 14px','margin:8px 0',
                            'color:#f4a261','font-size:13px'
                        ].join(';');
                        const errMsg = doc.predictions._error || 'Inference failed';
                        errBanner.innerHTML = `<strong style="color:#e76f51">❌ Extraction failed</strong><br><span style="color:#cccccc;font-size:12px;word-break:break-all;">${{errMsg}}</span>`;
                        predsPanel.appendChild(errBanner);
                        return;
                    }}

                    // ── Confidence pill helper ────────────────────────────────
                    const _conf = doc.predictions.confidence || {{}};
                    function _confPill(field) {{
                        const v = _conf[field];
                        if (v === undefined || v === null) return '';
                        const pct = Math.round(v * 100);
                        const c = pct >= 75 ? '#10b981' : pct >= 50 ? '#f59e0b' : '#ef4444';
                        const bg = pct >= 75 ? '#10b98122' : pct >= 50 ? '#f59e0b22' : '#ef444422';
                        return `<span class="conf-pill" style="color:${{c}};background:${{bg}}">${{pct}}%</span>`;
                    }}

                    // Create special sections for medical/important data
                    const specialSectionsDiv = document.createElement('div');
                    specialSectionsDiv.className = 'special-sections';
                    let hasSpecialContent = false;

                    // Document Type badge (always first if present)
                    if (doc.predictions.document_type) {{
                        hasSpecialContent = true;
                        const typeDiv = document.createElement('div');
                        typeDiv.style.cssText = 'margin-bottom: 10px;';
                        const typeBadge = document.createElement('span');
                        typeBadge.textContent = doc.predictions.document_type.replace(/_/g, ' ').toUpperCase();
                        typeBadge.style.cssText = [
                            'background:#2a9d8f','color:#ffffff','font-size:11px',
                            'font-weight:700','letter-spacing:0.08em',
                            'padding:4px 10px','border-radius:4px','display:inline-block'
                        ].join(';');
                        typeDiv.appendChild(typeBadge);
                        const dtPill = _confPill('document_type');
                        if (dtPill) typeDiv.insertAdjacentHTML('beforeend', dtPill);
                        specialSectionsDiv.appendChild(typeDiv);
                    }}

                    // Summary Section
                    if (doc.predictions.patient_summary || doc.predictions.case_summary || doc.predictions.summary) {{
                        hasSpecialContent = true;
                        const summarySection = document.createElement('div');
                        summarySection.className = 'special-section';

                        const summaryHeader = document.createElement('div');
                        summaryHeader.className = 'section-header';
                        summaryHeader.innerHTML = '📋 Summary' + _confPill('summary');
                        summarySection.appendChild(summaryHeader);

                        const summaryText = document.createElement('div');
                        summaryText.style.cssText = 'color: #e0e0e0; font-size: 13px; margin-top: 6px; line-height: 1.5;';
                        summaryText.textContent = doc.predictions.patient_summary || doc.predictions.case_summary || doc.predictions.summary;
                        summarySection.appendChild(summaryText);

                        specialSectionsDiv.appendChild(summarySection);
                    }}

                    // Medications Section
                    if (doc.predictions.medications && Array.isArray(doc.predictions.medications) && doc.predictions.medications.length > 0) {{
                        hasSpecialContent = true;
                        const medsSection = document.createElement('div');
                        medsSection.className = 'special-section';

                        const medsHeader = document.createElement('div');
                        medsHeader.className = 'section-header';
                        medsHeader.innerHTML = '💊 Medications' + _confPill('medications');
                        medsSection.appendChild(medsHeader);

                        const medsList = document.createElement('div');
                        medsList.style.cssText = 'margin-top: 6px;';

                        doc.predictions.medications.forEach(med => {{
                            const medItem = document.createElement('div');
                            medItem.className = 'medication-item';
                            medItem.style.cssText = 'margin: 4px 0;';

                            if (typeof med === 'object' && med !== null) {{
                                // Object format: {{name: "...", dosage: "...", frequency: "..."}}
                                const medName = med.name || med.medication || med.drug_name || 'Unknown';
                                const medDosage = med.dosage || med.dose || '';
                                const medFreq = med.frequency || '';
                                medItem.textContent = `• ${{medName}}${{medDosage ? ' - ' + medDosage : ''}}${{medFreq ? ' (' + medFreq + ')' : ''}}`;
                            }} else {{
                                // String format
                                medItem.textContent = `• ${{med}}`;
                            }}

                            medsList.appendChild(medItem);
                        }});

                        medsSection.appendChild(medsList);
                        specialSectionsDiv.appendChild(medsSection);
                    }}

                    // Keywords Section
                    if (doc.predictions.keywords && Array.isArray(doc.predictions.keywords) && doc.predictions.keywords.length > 0) {{
                        hasSpecialContent = true;
                        const keywordsSection = document.createElement('div');
                        keywordsSection.className = 'special-section';

                        const keywordsHeader = document.createElement('div');
                        keywordsHeader.className = 'section-header';
                        keywordsHeader.innerHTML = '🏷️ Keywords' + _confPill('keywords');
                        keywordsSection.appendChild(keywordsHeader);

                        const keywordsList = document.createElement('div');
                        keywordsList.style.cssText = 'margin-top: 6px; display: flex; flex-wrap: wrap; gap: 6px;';

                        doc.predictions.keywords.forEach(keyword => {{
                            const tag = document.createElement('span');
                            tag.className = 'keyword-tag-special';
                            tag.textContent = keyword;
                            tag.onclick = () => applyFilter('keywords', keyword);
                            keywordsList.appendChild(tag);
                        }});

                        keywordsSection.appendChild(keywordsList);
                        specialSectionsDiv.appendChild(keywordsSection);
                    }}

                    // Lab Values Section
                    if (doc.predictions.lab_values && Array.isArray(doc.predictions.lab_values) && doc.predictions.lab_values.length > 0) {{
                        hasSpecialContent = true;
                        const labSection = document.createElement('div');
                        labSection.className = 'special-section';

                        const labHeader = document.createElement('div');
                        labHeader.className = 'section-header';
                        labHeader.innerHTML = '🧪 Lab Values' + _confPill('lab_values');
                        labSection.appendChild(labHeader);

                        const table = document.createElement('table');
                        table.style.cssText = 'width:100%;border-collapse:collapse;margin-top:8px;font-size:12px;';

                        // Header row
                        const thead = document.createElement('thead');
                        thead.innerHTML = `<tr style="color:#94a3b8;text-align:left;border-bottom:1px solid #444455;">
                            <th style="padding:4px 6px;">Test</th>
                            <th style="padding:4px 6px;">Value</th>
                            <th style="padding:4px 6px;">Unit</th>
                            <th style="padding:4px 6px;">Range</th>
                            <th style="padding:4px 6px;">Flag</th>
                        </tr>`;
                        table.appendChild(thead);

                        const tbody = document.createElement('tbody');
                        doc.predictions.lab_values.forEach((row, idx) => {{
                            const tr = document.createElement('tr');
                            tr.style.cssText = `border-bottom:1px solid #2d2d3e;background:${{idx%2===0?'transparent':'rgba(255,255,255,0.02)'}};`;
                            const flag = (row.flag || '').toUpperCase();
                            const flagColor = flag === 'H' ? '#e76f51' : flag === 'L' ? '#8ecae6' : '#3db8a9';
                            const flagLabel = flag === 'H' ? '⬆ H' : flag === 'L' ? '⬇ L' : flag ? flag : '—';
                            tr.innerHTML = `
                                <td style="padding:4px 6px;color:#e0e0e0;font-weight:500;">${{row.test || '—'}}</td>
                                <td style="padding:4px 6px;color:#ffffff;font-weight:700;">${{row.value || '—'}}</td>
                                <td style="padding:4px 6px;color:#94a3b8;">${{row.unit || '—'}}</td>
                                <td style="padding:4px 6px;color:#94a3b8;">${{row.reference_range || '—'}}</td>
                                <td style="padding:4px 6px;color:${{flagColor}};font-weight:600;">${{flagLabel}}</td>`;
                            tbody.appendChild(tr);
                        }});
                        table.appendChild(tbody);
                        labSection.appendChild(table);
                        specialSectionsDiv.appendChild(labSection);
                    }}

                    // Similarity Score Section (for RAG search results)
                    if (doc.predictions.similarity_score !== undefined || doc.similarity_score !== undefined) {{
                        hasSpecialContent = true;
                        const simScore = doc.predictions.similarity_score || doc.similarity_score;

                        const simSection = document.createElement('div');
                        simSection.className = 'special-section';
                        simSection.style.borderBottom = 'none';

                        const simHeader = document.createElement('div');
                        simHeader.className = 'section-header';
                        simHeader.innerHTML = '🎯 Similarity Score';
                        simSection.appendChild(simHeader);

                        const simBadge = document.createElement('span');
                        simBadge.className = 'similarity-badge';
                        simBadge.style.cssText = 'margin-top: 6px; display: inline-block; font-size: 14px; font-weight: 600;';
                        simBadge.textContent = typeof simScore === 'number' ? simScore.toFixed(2) : simScore;
                        simSection.appendChild(simBadge);

                        specialSectionsDiv.appendChild(simSection);
                    }}

                    // Finance card — standalone, injected right after title
                    if (doc.predictions.total_amount !== undefined || doc.predictions.currency) {{
                        const amt = doc.predictions.total_amount;
                        const cur = doc.predictions.currency || '';
                        const ven = doc.predictions.vendor_name || '';

                        const finCard = document.createElement('div');
                        finCard.style.cssText = [
                            'background:#1c2c1c',
                            'border-left:4px solid #2a9d8f',
                            'border-radius:6px',
                            'padding:12px 16px',
                            'margin-bottom:14px'
                        ].join(';');

                        const amtRow = document.createElement('div');
                        amtRow.style.cssText = 'display:flex;align-items:baseline;gap:8px;white-space:nowrap;';

                        const amtSpan = document.createElement('span');
                        amtSpan.style.cssText = 'font-size:28px;font-weight:700;color:#e8b96a;line-height:1;';
                        amtSpan.textContent = amt !== undefined
                            ? (typeof amt === 'number'
                                ? amt.toLocaleString(undefined, {{minimumFractionDigits:2, maximumFractionDigits:2}})
                                : amt)
                            : '—';
                        amtRow.appendChild(amtSpan);

                        if (cur) {{
                            const curSpan = document.createElement('span');
                            curSpan.style.cssText = 'font-size:15px;color:#8ecae6;font-weight:600;';
                            curSpan.textContent = cur;
                            amtRow.appendChild(curSpan);
                        }}

                        finCard.appendChild(amtRow);

                        if (ven) {{
                            const venDiv = document.createElement('div');
                            venDiv.style.cssText = 'margin-top:5px;color:#9a9a9a;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;';
                            venDiv.textContent = ven;
                            finCard.appendChild(venDiv);
                        }}

                        // USD equivalent (injected by Python for non-USD currencies)
                        if (doc.predictions._usd_equivalent !== undefined) {{
                            const usdDiv = document.createElement('div');
                            usdDiv.style.cssText = 'margin-top:6px;color:#6b9e6b;font-size:12px;';
                            usdDiv.textContent = '≈ $' + doc.predictions._usd_equivalent.toLocaleString(undefined, {{minimumFractionDigits:2, maximumFractionDigits:2}}) + ' USD';
                            finCard.appendChild(usdDiv);
                        }}

                        // Insert after title (second child = right after <h3>)
                        const titleEl = predsPanel.querySelector('.pred-title');
                        if (titleEl && titleEl.nextSibling) {{
                            predsPanel.insertBefore(finCard, titleEl.nextSibling);
                        }} else {{
                            predsPanel.appendChild(finCard);
                        }}
                    }}

                    // Only add special sections if we have content
                    if (hasSpecialContent) {{
                        predsPanel.appendChild(specialSectionsDiv);
                    }}

                    // GT + Status badge pills (rendered at top if present)
                    const _gt = doc.predictions.GT;
                    const _status = doc.predictions.Status;
                    const _match = doc.predictions.match;
                    if (_gt || _status) {{
                        const badgeRow = document.createElement('div');
                        badgeRow.style.cssText = 'display:flex;gap:6px;align-items:center;margin-bottom:10px;flex-wrap:wrap;';
                        const gtColors = {{'benign':'#10b981','malignant':'#ef4444','pre-cancerous':'#f59e0b',
                            'Normal':'#10b981','Abnormal':'#ef4444','Cancer':'#ef4444','Benign':'#10b981',
                            'Tissue':'#6366f1','WBC':'#0ea5e9','fractured':'#ef4444','non_fractured':'#10b981',
                            'normal':'#10b981','pneumonia':'#f59e0b','covid':'#ef4444'}};
                        if (_gt) {{
                            const pill = document.createElement('span');
                            pill.style.cssText = `background:#1e293b;color:#e2e8f0;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;border:1px solid #334155;`;
                            pill.textContent = `GT: ${{_gt}}`;
                            badgeRow.appendChild(pill);
                        }}
                        if (_status) {{
                            const color = gtColors[_status] || gtColors[_gt] || '#6366f1';
                            const pill = document.createElement('span');
                            pill.style.cssText = `background:${{color}}22;color:${{color}};padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700;border:1px solid ${{color}}44;`;
                            pill.textContent = _status;
                            badgeRow.appendChild(pill);
                        }}
                        if (_match) {{
                            const mColor = _match === 'yes' ? '#10b981' : '#ef4444';
                            const pill = document.createElement('span');
                            pill.style.cssText = `background:${{mColor}}22;color:${{mColor}};padding:3px 8px;border-radius:12px;font-size:10px;font-weight:700;border:1px solid ${{mColor}}44;`;
                            pill.textContent = _match === 'yes' ? 'Match' : 'Mismatch';
                            badgeRow.appendChild(pill);
                        }}
                        predsPanel.appendChild(badgeRow);
                    }}

                    // k-NN prediction pill (separate row, highlighted)
                    const _knnLabel = doc.predictions.kNN_Label;
                    const _knnConf = doc.predictions.kNN_Confidence;
                    if (_knnLabel) {{
                        const knnRow = document.createElement('div');
                        knnRow.style.cssText = 'display:flex;gap:8px;align-items:center;margin-bottom:10px;flex-wrap:wrap;';
                        const knnPill = document.createElement('span');
                        knnPill.style.cssText = 'background:linear-gradient(135deg,#6366f122,#a78bfa22);color:#a78bfa;padding:5px 14px;border-radius:14px;font-size:13px;font-weight:700;border:1px solid #6366f144;';
                        knnPill.textContent = `k-NN: ${{_knnLabel}}` + (_knnConf ? ` (${{Math.round(_knnConf * 100)}}%)` : '');
                        knnRow.appendChild(knnPill);
                        // k-NN match check against GT
                        if (_gt) {{
                            const knnMatch = _knnLabel.toLowerCase().replace(/_/g,' ') === _gt.toLowerCase().replace(/_/g,' ');
                            const kmPill = document.createElement('span');
                            const kmColor = knnMatch ? '#10b981' : '#ef4444';
                            kmPill.style.cssText = `background:${{kmColor}}22;color:${{kmColor}};padding:4px 10px;border-radius:12px;font-size:12px;font-weight:700;border:1px solid ${{kmColor}}44;`;
                            kmPill.textContent = knnMatch ? 'k-NN Correct' : 'k-NN Wrong';
                            knnRow.appendChild(kmPill);
                        }}
                        const knnTag = document.createElement('span');
                        knnTag.style.cssText = 'color:#64748b;font-size:10px;';
                        knnTag.textContent = 'image embedding classification';
                        predsPanel.appendChild(knnRow);
                    }}

                    // ── NLP Enrichment (spark-nlp-display style) ────────────
                    const nlpEnts = doc.predictions._nlp_entities;
                    const nlpCodes = doc.predictions._nlp_codes;
                    const nlpRels = doc.predictions._nlp_relations;
                    if ((nlpEnts && nlpEnts.length > 0) || (nlpCodes && Object.keys(nlpCodes).length > 0)) {{
                        // Color palette for NER labels (spark-nlp-display inspired)
                        const _nerColors = {{
                            'Drug_Ingredient':'#6366f1','Drug_BrandName':'#818cf8','Strength':'#a78bfa','Dosage':'#a78bfa',
                            'Frequency':'#c084fc','Route':'#d946ef','Form':'#e879f9','Duration':'#f0abfc',
                            'DRUG':'#6366f1','DOSAGE':'#a78bfa','ROUTE':'#d946ef','FREQUENCY':'#c084fc','FORM':'#e879f9','STRENGTH':'#a78bfa','DURATION':'#f0abfc',
                            'Heart_Disease':'#ef4444','Disease_Syndrome_Disorder':'#f87171','Symptom':'#fb923c','Communicable_Disease':'#f97316',
                            'PROBLEM':'#ef4444','Oncological':'#dc2626','Diabetes':'#f87171','Obesity':'#fb923c',
                            'Procedure':'#14b8a6','Test':'#2dd4bf','Test_Result':'#5eead4','Imaging_Technique':'#99f6e4',
                            'TREATMENT':'#14b8a6','TEST':'#2dd4bf',
                            'Blood_Pressure':'#f59e0b','Pulse':'#fbbf24','Respiratory_Rate':'#fcd34d','Temperature':'#fde68a','O2_Saturation':'#fef3c7',
                            'Vital_Signs_Header':'#f59e0b',
                            'Internal_organ_or_component':'#0ea5e9','External_body_part_or_region':'#38bdf8','Direction':'#7dd3fc',
                            'Age':'#94a3b8','Gender':'#94a3b8','Race_Ethnicity':'#94a3b8','Employment':'#94a3b8',
                            'Clinical_Dept':'#22d3ee','Admission_Discharge':'#67e8f9','Date':'#a5b4fc','RelativeDate':'#a5b4fc',
                            'ImagingFindings':'#f472b6','BodyPart':'#0ea5e9','Measurements':'#fbbf24','ImagingTest':'#2dd4bf',
                        }};
                        let _nerColorIdx = 0;
                        const _nerFallback = ['#f472b6','#fb7185','#fda4af','#c084fc','#a78bfa','#93c5fd','#7dd3fc','#67e8f9','#5eead4','#6ee7b7'];
                        function _nerColor(label) {{
                            if (_nerColors[label]) return _nerColors[label];
                            const c = _nerFallback[_nerColorIdx % _nerFallback.length];
                            _nerColorIdx++;
                            _nerColors[label] = c;
                            return c;
                        }}

                        const nlpSection = document.createElement('div');
                        nlpSection.style.cssText = 'background:linear-gradient(135deg,#0f172a 0%,#1e1b4b 100%);border:1px solid #334155;border-radius:8px;padding:14px;margin-bottom:14px;';

                        const nlpTitle = document.createElement('div');
                        nlpTitle.style.cssText = 'color:#a78bfa;font-size:13px;font-weight:700;margin-bottom:10px;display:flex;align-items:center;gap:8px;';
                        nlpTitle.innerHTML = '🧬 NLP Enrichment <span style="font-size:10px;color:#64748b;font-weight:400;">Spark NLP for Healthcare</span>';
                        nlpSection.appendChild(nlpTitle);

                        // ── Build entity→codes lookup for tooltips & merged table ──
                        const _entCodes = {{}};  // "chunk|label" → [{{sys, code, conf}}, ...]
                        const sysColors = {{'icd10':'#ef4444','rxnorm':'#6366f1','snomed':'#14b8a6','loinc':'#f59e0b','icdo':'#ec4899','umls':'#8b5cf6'}};
                        if (nlpCodes) {{
                            Object.keys(nlpCodes).forEach(sys => {{
                                (nlpCodes[sys] || []).forEach(r => {{
                                    const ent = r.ner_entity || '';
                                    if (ent) {{
                                        const key = ent.toLowerCase();
                                        if (!_entCodes[key]) _entCodes[key] = [];
                                        _entCodes[key].push({{sys: sys, code: r.code || '—', conf: r.confidence}});
                                    }}
                                }});
                            }});
                        }}

                        // ── Inline NER highlights with hover tooltips ──
                        if (nlpEnts && nlpEnts.length > 0) {{
                            const srcParts = [];
                            ['summary','case_summary','patient_summary','chief_complaint'].forEach(f => {{
                                if (doc.predictions[f]) srcParts.push(doc.predictions[f]);
                            }});
                            ['diagnoses','findings','imaging_findings'].forEach(f => {{
                                const v = doc.predictions[f];
                                if (v && Array.isArray(v) && v.length) srcParts.push(v.join(', '));
                            }});
                            const srcText = srcParts.join(' . ');

                            if (srcText) {{
                                const nerDisplay = document.createElement('div');
                                nerDisplay.style.cssText = 'background:#020617;border:1px solid #1e293b;border-radius:6px;padding:12px;margin-bottom:12px;font-size:13px;line-height:2.2;color:#cbd5e1;position:relative;';

                                const sorted = [...nlpEnts].filter(e => e.begin !== undefined).sort((a,b) => a.begin - b.begin);
                                const deduped = [];
                                let lastEnd = -1;
                                sorted.forEach(e => {{
                                    if (e.begin >= lastEnd) {{
                                        deduped.push(e);
                                        lastEnd = e.end + 1;
                                    }}
                                }});

                                let html = '';
                                let pos = 0;
                                deduped.forEach(e => {{
                                    if (e.begin > pos) html += _escHtml(srcText.substring(pos, e.begin));
                                    const c = _nerColor(e.label);
                                    const assertBorder = '';
                                    // Build tooltip lines
                                    const tipLines = [`Label: ${{e.label.replace(/_/g,' ')}}`, `Assertion: ${{e.assertion || 'present'}}`, `Model: ${{e._ner_model || '—'}}`];
                                    const codes = _entCodes[e.chunk.toLowerCase()] || [];
                                    codes.forEach(cd => tipLines.push(`${{cd.sys.toUpperCase()}}: ${{cd.code}} (${{cd.conf !== undefined ? (cd.conf*100).toFixed(0)+'%' : '—'}})`));
                                    const tip = _escHtml(tipLines.join('&#10;'));
                                    html += `<span class="ner-hl" style="background:${{c}}25;border:1px solid ${{c}}55;border-radius:3px;padding:1px 4px;${{assertBorder}}cursor:default;position:relative;" title="${{tip}}" data-ner-tip="${{tip}}">`;
                                    html += `<span style="color:${{c}};font-weight:500;">${{_escHtml(e.chunk)}}</span>`;
                                    html += '</span>';
                                    pos = e.end + 1;
                                }});
                                if (pos < srcText.length) html += _escHtml(srcText.substring(pos));
                                nerDisplay.innerHTML = html;
                                nlpSection.appendChild(nerDisplay);

                                // Rich hover tooltip (replaces native title)
                                const tipEl = document.createElement('div');
                                tipEl.style.cssText = 'display:none;position:fixed;background:#1e293b;border:1px solid #475569;border-radius:6px;padding:8px 12px;font-size:11px;line-height:1.6;color:#e2e8f0;z-index:99999;pointer-events:none;max-width:320px;box-shadow:0 4px 12px rgba(0,0,0,0.5);';
                                document.body.appendChild(tipEl);
                                nerDisplay.addEventListener('mouseover', ev => {{
                                    const hl = ev.target.closest('.ner-hl');
                                    if (!hl) {{ tipEl.style.display='none'; return; }}
                                    hl.removeAttribute('title');  // suppress native tooltip
                                    const raw = hl.getAttribute('data-ner-tip') || '';
                                    const lines = raw.split('&#10;');
                                    tipEl.innerHTML = lines.map(l => {{
                                        const [k,...v] = l.split(': ');
                                        const val = v.join(': ');
                                        if (['ICD10','RXNORM','SNOMED','LOINC','UMLS','ICDO'].includes(k)) {{
                                            const sc = sysColors[k.toLowerCase()] || '#64748b';
                                            return `<div><span style="background:${{sc}}30;color:${{sc}};padding:0 4px;border-radius:2px;font-weight:700;font-size:10px;">${{k}}</span> <span style="color:#e8b96a;font-family:monospace;">${{val}}</span></div>`;
                                        }}
                                        return `<div><span style="color:#94a3b8;">${{k}}:</span> <span style="color:#f1f5f9;font-weight:500;">${{val}}</span></div>`;
                                    }}).join('');
                                    tipEl.style.display = 'block';
                                    tipEl.style.left = Math.min(ev.clientX + 12, window.innerWidth - 340) + 'px';
                                    tipEl.style.top = (ev.clientY + 16) + 'px';
                                }});
                                nerDisplay.addEventListener('mouseout', ev => {{
                                    if (!ev.target.closest('.ner-hl')) tipEl.style.display = 'none';
                                }});
                                nerDisplay.addEventListener('mouseleave', () => {{ tipEl.style.display = 'none'; }});
                                nerDisplay.addEventListener('mousemove', ev => {{
                                    if (tipEl.style.display === 'block') {{
                                        tipEl.style.left = Math.min(ev.clientX + 12, window.innerWidth - 340) + 'px';
                                        tipEl.style.top = (ev.clientY + 16) + 'px';
                                    }}
                                }});
                                // Kill ghost tooltips on scroll or leaving the viewport
                                document.addEventListener('scroll', () => {{ tipEl.style.display = 'none'; }}, true);
                                document.addEventListener('visibilitychange', () => {{ tipEl.style.display = 'none'; }});
                            }}

                            // ── Merged entity + codes table ──
                            const uniqueEnts = [];
                            const seen = new Set();
                            nlpEnts.forEach(e => {{
                                const key = e.chunk + '|' + e.label;
                                if (!seen.has(key)) {{
                                    seen.add(key);
                                    uniqueEnts.push(e);
                                }}
                            }});

                            if (uniqueEnts.length > 0) {{
                                const tbl = document.createElement('table');
                                tbl.style.cssText = 'width:100%;border-collapse:collapse;font-size:11px;margin-bottom:10px;';
                                tbl.innerHTML = `<thead><tr style="border-bottom:1px solid #334155;">
                                    <th style="padding:4px 6px;text-align:left;color:#64748b;font-weight:600;">Entity</th>
                                    <th style="padding:4px 6px;text-align:left;color:#64748b;font-weight:600;">Label</th>
                                    <th style="padding:4px 6px;text-align:left;color:#64748b;font-weight:600;">Assertion</th>
                                    <th style="padding:4px 6px;text-align:left;color:#64748b;font-weight:600;">Model</th>
                                    <th style="padding:4px 6px;text-align:left;color:#64748b;font-weight:600;">Codes</th>
                                </tr></thead>`;
                                const tbody = document.createElement('tbody');
                                uniqueEnts.forEach((e, idx) => {{
                                    const c = _nerColor(e.label);
                                    const assertColor = e.assertion === 'absent' ? '#ef4444' : e.assertion === 'possible' ? '#f59e0b' : e.assertion === 'past' ? '#64748b' : '#10b981';
                                    // Resolved codes for this entity
                                    const codes = _entCodes[e.chunk.toLowerCase()] || [];
                                    let codeCells = '—';
                                    if (codes.length > 0) {{
                                        codeCells = codes.map(cd => {{
                                            const sc = sysColors[cd.sys] || '#64748b';
                                            const conf = cd.conf !== undefined ? ` ${{(cd.conf*100).toFixed(0)}}%` : '';
                                            return `<span style="white-space:nowrap;"><span style="background:${{sc}}25;color:${{sc}};padding:0 4px;border-radius:2px;font-size:9px;font-weight:700;text-transform:uppercase;">${{cd.sys}}</span> <span style="color:#e8b96a;font-family:monospace;">${{cd.code}}</span><span style="color:#64748b;font-size:9px;">${{conf}}</span></span>`;
                                        }}).join(' ');
                                    }}
                                    const tr = document.createElement('tr');
                                    tr.style.cssText = `border-bottom:1px solid #1e293b;background:${{idx%2===0?'transparent':'rgba(255,255,255,0.02)'}};`;
                                    tr.innerHTML = `
                                        <td style="padding:4px 6px;text-align:left;color:#e2e8f0;font-weight:500;">${{_escHtml(e.chunk)}}</td>
                                        <td style="padding:4px 6px;text-align:left;"><span style="background:${{c}}30;color:${{c}};padding:1px 6px;border-radius:3px;font-size:10px;font-weight:600;">${{e.label.replace(/_/g,' ')}}</span></td>
                                        <td style="padding:4px 6px;text-align:left;color:${{assertColor}};font-weight:500;">${{e.assertion || '—'}}</td>
                                        <td style="padding:4px 6px;text-align:left;color:#64748b;font-family:monospace;font-size:10px;">${{e._ner_model || '—'}}</td>
                                        <td style="padding:4px 6px;text-align:left;">${{codeCells}}</td>`;
                                    tbody.appendChild(tr);
                                }});
                                tbl.appendChild(tbody);
                                nlpSection.appendChild(tbl);
                            }}
                        }}

                        // ── Relations ──
                        if (nlpRels && nlpRels.length > 0) {{
                            const relHdr = document.createElement('div');
                            relHdr.style.cssText = 'color:#f472b6;font-size:11px;font-weight:700;margin:8px 0 6px 0;border-top:1px solid #334155;padding-top:8px;letter-spacing:0.04em;';
                            relHdr.textContent = '🔗 CLINICAL RELATIONS';
                            nlpSection.appendChild(relHdr);
                            nlpRels.forEach(rel => {{
                                const conf = rel.confidence !== undefined ? (rel.confidence * 100).toFixed(0) : null;
                                const confColor = conf >= 80 ? '#10b981' : conf >= 50 ? '#f59e0b' : '#ef4444';
                                const e1Label = rel.entity1_label ? rel.entity1_label.replace(/_/g,' ') : '';
                                const e2Label = rel.entity2_label ? rel.entity2_label.replace(/_/g,' ') : '';
                                const e1c = e1Label ? _nerColor(rel.entity1_label) : '#94a3b8';
                                const e2c = e2Label ? _nerColor(rel.entity2_label) : '#94a3b8';
                                const row = document.createElement('div');
                                row.style.cssText = 'display:flex;align-items:center;gap:6px;margin:3px 0;font-size:11px;cursor:default;';
                                row.title = (e1Label ? `${{_escHtml(rel.entity1 || '')}} [${{e1Label}}]` : _escHtml(rel.entity1 || ''))
                                    + ` → ${{rel.relation || ''}} → `
                                    + (e2Label ? `${{_escHtml(rel.entity2 || '')}} [${{e2Label}}]` : _escHtml(rel.entity2 || ''))
                                    + (conf !== null ? `  (confidence: ${{conf}}%)` : '');
                                row.innerHTML = `<span style="color:${{e1c}};">${{_escHtml(rel.entity1 || '')}}</span>`
                                    + `<span style="color:#f472b6;font-size:10px;">→ ${{rel.relation || ''}} →</span>`
                                    + `<span style="color:${{e2c}};">${{_escHtml(rel.entity2 || '')}}</span>`
                                    + (conf !== null ? `<span style="color:${{confColor}};font-size:9px;margin-left:4px;">${{conf}}%</span>` : '');
                                nlpSection.appendChild(row);
                            }});
                        }}

                        predsPanel.appendChild(nlpSection);
                    }}

                    // Add content container
                    const content = document.createElement('div');
                    content.className = 'pred-content';

                    const _specialFields = new Set([
                        'document_type', 'GT', 'Status', 'match', 'kNN_Label', 'kNN_Confidence',
                        'summary', 'patient_summary', 'case_summary',
                        'medications', 'keywords', 'similarity_score',
                        'lab_values', 'confidence',
                        'total_amount', 'currency', 'vendor_name',
                        '_nlp_entities', '_nlp_codes', '_nlp_relations', '_nlp_error',
                    ]);
                    for (const [key, value] of Object.entries(doc.predictions)) {{
                        if (key.startsWith('_') || _specialFields.has(key)) continue;
                        const displayKey = key.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                        
                        const predItem = document.createElement('div');
                        predItem.className = 'pred-item';
                        
                        const predKey = document.createElement('div');
                        predKey.className = 'pred-key';
                        predKey.textContent = displayKey;
                        
                        const predValue = document.createElement('div');
                        predValue.className = 'pred-value';
                        
                        // Format value and attach click handlers
                        if (typeof value === 'boolean') {{
                            const span = document.createElement('span');
                            span.className = value ? 'bool-true' : 'bool-false';
                            span.textContent = value ? '✓' : '✗';
                            span.onclick = () => applyFilter(key, value);
                            predValue.appendChild(span);
                        }} else if (Array.isArray(value)) {{
                            if (value.length === 0) {{
                                predValue.innerHTML = '<span class="null">None</span>';
                            }} else {{
                                const container = document.createElement('div');
                                container.style.marginTop = '4px';

                                // Check if array contains objects or primitives
                                const firstItem = value[0];
                                if (typeof firstItem === 'object' && firstItem !== null) {{
                                    // Array of objects - mini table
                                    // Stack key above table (full-width, left-aligned)
                                    predItem.style.flexDirection = 'column';
                                    predItem.style.alignItems = 'flex-start';
                                    predKey.style.minWidth = 'unset';
                                    predKey.style.marginBottom = '6px';
                                    predValue.style.width = '100%';

                                    const tableWrap = document.createElement('div');
                                    tableWrap.style.cssText = [
                                        'width:100%', 'border-radius:4px',
                                        'border:1px solid #334155',
                                        'overflow-x:auto', 'max-height:220px', 'overflow-y:auto',
                                        'position:relative'
                                    ].join(';');

                                    // Floating tooltip div (shared across all cells)
                                    const tooltip = document.createElement('div');
                                    tooltip.style.cssText = [
                                        'position:fixed', 'display:none',
                                        'background:#0f172a', 'color:#e2e8f0',
                                        'border:1px solid #334155', 'border-radius:4px',
                                        'padding:6px 10px', 'font-size:12px',
                                        'max-width:340px', 'word-break:break-word',
                                        'z-index:9999', 'pointer-events:none',
                                        'line-height:1.5', 'box-shadow:0 4px 12px rgba(0,0,0,0.5)'
                                    ].join(';');
                                    document.body.appendChild(tooltip);

                                    const tbl = document.createElement('table');
                                    tbl.style.cssText = 'width:100%;border-collapse:collapse;font-size:11px;';

                                    const colKeys = Object.keys(value[0]);

                                    const thead = document.createElement('thead');
                                    const hRow = document.createElement('tr');
                                    hRow.style.cssText = 'background:#242424;position:sticky;top:0;z-index:1;';
                                    colKeys.forEach(k => {{
                                        const th = document.createElement('th');
                                        th.style.cssText = 'padding:5px 8px;text-align:left;color:#8ecae6;font-weight:600;white-space:nowrap;border-bottom:1px solid #334155;';
                                        const _colLabels = {{ 'description_translated': 'translation' }};
                                        th.textContent = _colLabels[k] || k.replace(/_/g, ' ');
                                        hRow.appendChild(th);
                                    }});
                                    thead.appendChild(hRow);
                                    tbl.appendChild(thead);

                                    const tbody = document.createElement('tbody');
                                    value.forEach((item, rowIdx) => {{
                                        const tr = document.createElement('tr');
                                        tr.style.cssText = `background:${{rowIdx % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.03)'}};`;
                                        const _priceCols = new Set(['unit_price','total','subtotal','price','amount']);
                                        const _docCur = doc.predictions.currency || '';
                                        colKeys.forEach(k => {{
                                            const td = document.createElement('td');
                                            const v = item[k];
                                            const _fv = (v !== null && v !== undefined)
                                                ? (typeof v === 'object' ? JSON.stringify(v) : String(v))
                                                : '—';
                                            // Append currency to price columns
                                            const _display = (_priceCols.has(k) && _docCur && _fv !== '—')
                                                ? _fv + ' ' + _docCur
                                                : _fv;
                                            td.style.cssText = 'padding:4px 8px;color:#cbd5e1;border-bottom:1px solid #1e293b;max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;cursor:default;';
                                            td.textContent = _display;
                                            // Hover tooltip for any truncated cell
                                            td.addEventListener('mouseenter', function(e) {{
                                                if (this.scrollWidth > this.clientWidth) {{
                                                    tooltip.textContent = _display;
                                                    tooltip.style.display = 'block';
                                                    tooltip.style.left = (e.clientX + 12) + 'px';
                                                    tooltip.style.top  = (e.clientY + 12) + 'px';
                                                }}
                                            }});
                                            td.addEventListener('mousemove', function(e) {{
                                                tooltip.style.left = (e.clientX + 12) + 'px';
                                                tooltip.style.top  = (e.clientY + 12) + 'px';
                                            }});
                                            td.addEventListener('mouseleave', function() {{
                                                tooltip.style.display = 'none';
                                            }});
                                            tr.appendChild(td);
                                        }});
                                        tbody.appendChild(tr);
                                    }});
                                    tbl.appendChild(tbody);
                                    tableWrap.appendChild(tbl);
                                    container.appendChild(tableWrap);
                                }} else {{
                                    // Array of primitives - show as tags
                                    value.forEach(item => {{
                                        const tag = document.createElement('span');
                                        tag.className = 'tag';
                                        tag.textContent = item;
                                        tag.onclick = () => applyFilter(key, item);
                                        container.appendChild(tag);
                                    }});
                                }}
                                predValue.appendChild(container);
                            }}
                        }} else if (typeof value === 'object' && value !== null) {{
                            // Plain nested object — render as key-value rows
                            const objDiv = document.createElement('div');
                            objDiv.style.cssText = 'background: #0f172a; padding: 8px 10px; margin-top: 4px; border-radius: 4px; border-left: 3px solid #2a9d8f; font-size: 13px;';
                            for (const [k, v] of Object.entries(value)) {{
                                const rowDiv = document.createElement('div');
                                rowDiv.style.cssText = 'margin: 2px 0; display: flex; gap: 8px;';
                                const displayVal = (v !== null && v !== undefined)
                                    ? (typeof v === 'object' ? JSON.stringify(v) : String(v))
                                    : 'N/A';
                                rowDiv.innerHTML = `<span style="color:#94a3b8;min-width:120px;">${{k.replace(/_/g,' ')}}:</span><span style="color:#e0e0e0;font-weight:500;">${{displayVal}}</span>`;
                                objDiv.appendChild(rowDiv);
                            }}
                            predValue.appendChild(objDiv);
                        }} else if (typeof value === 'number') {{
                            const span = document.createElement('span');
                            span.className = 'number';
                            span.textContent = value;
                            span.onclick = () => applyFilter(key, value);
                            predValue.appendChild(span);
                        }} else if (value === null) {{
                            predValue.innerHTML = '<span class="null">N/A</span>';
                        }} else {{
                            const span = document.createElement('span');
                            span.className = 'clickable';
                            span.textContent = value;
                            span.onclick = () => applyFilter(key, value);
                            predValue.appendChild(span);
                        }}

                        // Mark truncated values and add hover tooltip
                        requestAnimationFrame(() => {{
                            if (predValue.scrollHeight > predValue.clientHeight + 2) {{
                                predValue.classList.add('truncated');
                                const fullText = (typeof value === 'object' && value !== null)
                                    ? JSON.stringify(value, null, 2)
                                    : String(value);
                                predValue.addEventListener('mouseenter', function(e) {{
                                    _pvTooltip.textContent = fullText;
                                    _pvTooltip.style.display = 'block';
                                    _pvTooltip.style.left = (e.clientX + 14) + 'px';
                                    _pvTooltip.style.top  = (e.clientY + 14) + 'px';
                                }});
                                predValue.addEventListener('mousemove', function(e) {{
                                    _pvTooltip.style.left = (e.clientX + 14) + 'px';
                                    _pvTooltip.style.top  = (e.clientY + 14) + 'px';
                                }});
                                predValue.addEventListener('mouseleave', function() {{
                                    _pvTooltip.style.display = 'none';
                                }});
                                predValue.style.cursor = 'help';
                            }}
                        }});

                        predItem.appendChild(predKey);
                        predItem.appendChild(predValue);
                        content.appendChild(predItem);
                    }}

                    predsPanel.appendChild(content);

                    // Dataset source badge at bottom
                    if (doc.predictions._dataset_source) {{
                        const srcBadge = document.createElement('div');
                        srcBadge.style.cssText = [
                            'margin-top:16px', 'padding:8px 12px',
                            'background:#1a1a2e', 'border:1px solid #3a3a5c',
                            'border-radius:6px', 'display:flex',
                            'align-items:center', 'gap:8px'
                        ].join(';');
                        const srcLabel = document.createElement('span');
                        srcLabel.style.cssText = 'color:#6b7280;font-size:11px;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;flex-shrink:0;';
                        srcLabel.textContent = 'Dataset';
                        const srcVal = document.createElement('span');
                        srcVal.style.cssText = 'color:#8ecae6;font-size:12px;font-family:monospace;word-break:break-all;';
                        srcVal.textContent = doc.predictions._dataset_source;
                        srcBadge.appendChild(srcLabel);
                        srcBadge.appendChild(srcVal);
                        predsPanel.appendChild(srcBadge);
                    }}

                    // ── Ground Truth panel ───────────────────────────────────
                    const gtPanel = document.getElementById('gt_{viewer_id}');
                    if (gtPanel) {{
                        gtPanel.innerHTML = '';
                        const gtTitle = document.createElement('h3');
                        gtTitle.className = 'gt-title';
                        gtTitle.textContent = 'Ground Truth';
                        gtPanel.appendChild(gtTitle);

                        const gt = doc.ground_truth;
                        if (gt && Object.keys(gt).length > 0) {{
                            for (const [key, value] of Object.entries(gt)) {{
                                if (key.startsWith('_')) continue;
                                const item = document.createElement('div');
                                item.className = 'gt-item';

                                const k = document.createElement('div');
                                k.className = 'gt-key';
                                k.textContent = key.replace(/_/g, ' ');
                                item.appendChild(k);

                                const v = document.createElement('div');
                                v.className = 'gt-value';
                                if (Array.isArray(value)) {{
                                    v.textContent = value.length > 0 ? value.join(', ') : '—';
                                }} else if (typeof value === 'object' && value !== null) {{
                                    v.textContent = JSON.stringify(value);
                                }} else {{
                                    v.textContent = (value !== null && value !== undefined) ? String(value) : '—';
                                }}
                                item.appendChild(v);
                                gtPanel.appendChild(item);
                            }}
                        }} else {{
                            const empty = document.createElement('div');
                            empty.className = 'gt-empty';
                            empty.textContent = 'No ground truth available for this document';
                            gtPanel.appendChild(empty);
                        }}
                    }}

                    document.getElementById('jump_{viewer_id}').value = idx + 1;
                }}
                
                // Export functions to global scope with instance pattern
                window.viewer_{viewer_id}_instance = {{
                    nextDoc: function() {{
                        if (filteredDocs.length === 0) return;
                        currentIdx = (currentIdx + 1) % filteredDocs.length;
                        showDoc(currentIdx);
                    }},
                    prevDoc: function() {{
                        if (filteredDocs.length === 0) return;
                        currentIdx = (currentIdx - 1 + filteredDocs.length) % filteredDocs.length;
                        showDoc(currentIdx);
                    }},
                    jumpDoc: function(value) {{
                        const idx = parseInt(value) - 1;
                        if (idx >= 0 && idx < filteredDocs.length) {{
                            currentIdx = idx;
                            showDoc(currentIdx);
                        }}
                    }},
                    onKey: function(e) {{
                        if (e.key === 'Escape') {{
                            document.getElementById('lightbox_{viewer_id}').classList.remove('open');
                        }}
                        else if (e.key === 'ArrowRight') {{ e.preventDefault(); this.nextDoc(); }}
                        else if (e.key === 'ArrowLeft') {{ e.preventDefault(); this.prevDoc(); }}
                    }},
                    searchDocs: function(term) {{
                        searchTerm = term.toLowerCase().trim();
                        updateFilters();
                    }},
                    exportJson: function() {{
                        if (filteredDocs.length === 0) return;
                        const doc = filteredDocs[currentIdx];
                        const exportData = {{predictions: doc.predictions}};
                        if (doc.ground_truth && Object.keys(doc.ground_truth).length > 0) {{
                            exportData.ground_truth = doc.ground_truth;
                        }}
                        const json = JSON.stringify(exportData, (k,v) => k === 'image' ? undefined : v, 2);
                        navigator.clipboard.writeText(json).then(() => {{
                            const btn = document.querySelector('#{viewer_id} .export-btn');
                            const orig = btn.textContent;
                            btn.textContent = '✅ Copied!';
                            setTimeout(() => {{ btn.textContent = orig; }}, 1500);
                        }}).catch(() => {{
                            // Fallback for non-secure contexts
                            const ta = document.createElement('textarea');
                            ta.value = json;
                            document.body.appendChild(ta);
                            ta.select();
                            document.execCommand('copy');
                            document.body.removeChild(ta);
                            const btn = document.querySelector('#{viewer_id} .export-btn');
                            const orig = btn.textContent;
                            btn.textContent = '✅ Copied!';
                            setTimeout(() => {{ btn.textContent = orig; }}, 1500);
                        }});
                    }},
                    dropdownFilter: function(key, value) {{
                        // Remove any existing filter for this dropdown key
                        for (const fk of Object.keys(activeFilters)) {{
                            if (activeFilters[fk].key === key) {{
                                delete activeFilters[fk];
                            }}
                        }}
                        // Apply new filter if not "All"
                        if (value) {{
                            applyFilter(key, value);
                        }} else {{
                            updateFilters();
                        }}
                    }}
                }};
                
                // Show first document
                showDoc(0);
                document.getElementById('content_{viewer_id}').focus();
            }})();
        </script>
    </div>
    """
    
    return html


def display_extraction_charts(extracted_docs, ground_truth=None, width='100%'):
    """
    Display 3 horizontal bar charts in a row: by dataset source, by document type, and GT accuracy.

    Args:
        extracted_docs: list of prediction dicts (with _dataset_source, _status, confidence, etc.)
        ground_truth: optional list of GT dicts (one per doc, same length as extracted_docs)
        width: CSS width of the container
    """
    from collections import defaultdict

    gt_list = ground_truth or [None] * len(extracted_docs)

    # ── Aggregate metrics ──────────────────────────────────────────────
    by_source = defaultdict(lambda: {'total': 0, 'success': 0, 'conf_sum': 0.0, 'conf_n': 0,
                                      'filled_sum': 0, 'field_sum': 0, 'gt_match': 0, 'gt_total': 0})
    by_doctype = defaultdict(lambda: {'count': 0, 'conf_sum': 0.0, 'conf_n': 0})

    for i, doc in enumerate(extracted_docs):
        src = doc.get('_dataset_source', 'unknown')
        b = by_source[src]
        b['total'] += 1
        if doc.get('_status') == 'success':
            b['success'] += 1

        # confidence
        conf = doc.get('confidence', {})
        if isinstance(conf, dict) and conf.get('overall') is not None:
            b['conf_sum'] += conf['overall']
            b['conf_n'] += 1

        # field coverage
        non_meta = {k: v for k, v in doc.items() if not k.startswith('_') and k != 'confidence'}
        total_f = len(non_meta)
        filled_f = sum(1 for v in non_meta.values()
                       if v is not None and v != '' and not (isinstance(v, list) and len(v) == 0))
        b['field_sum'] += total_f
        b['filled_sum'] += filled_f

        # GT accuracy: compare predicted document_type vs GT answer/category
        gt = gt_list[i] if i < len(gt_list) else None
        if gt and isinstance(gt, dict):
            gt_label = gt.get('answer') or gt.get('category') or gt.get('document_type') or gt.get('label')
            pred_label = doc.get('document_type')
            if gt_label and pred_label:
                b['gt_total'] += 1
                if str(pred_label).strip().lower() == str(gt_label).strip().lower():
                    b['gt_match'] += 1

        # by document type
        dt = doc.get('document_type', 'unknown') or 'unknown'
        bd = by_doctype[dt]
        bd['count'] += 1
        if isinstance(conf, dict) and conf.get('overall') is not None:
            bd['conf_sum'] += conf['overall']
            bd['conf_n'] += 1

    # ── Build bars HTML ────────────────────────────────────────────────
    def _bar(label, value, max_val, color, suffix='%', decimals=0):
        pct = (value / max_val * 100) if max_val > 0 else 0
        disp = f"{value:.{decimals}f}{suffix}"
        return (f'<div style="margin:6px 0;">'
                f'<div style="display:flex;justify-content:space-between;font-size:12px;color:#cbd5e1;margin-bottom:2px;">'
                f'<span>{label}</span><span style="font-weight:600;color:#e2e8f0;">{disp}</span></div>'
                f'<div style="height:14px;background:#1e293b;border-radius:3px;overflow:hidden;">'
                f'<div style="height:100%;width:{pct:.1f}%;background:{color};border-radius:3px;'
                f'transition:width 0.4s ease;"></div></div></div>')

    # Chart 1: By Dataset Source — success rate
    chart1_bars = ''
    for src in sorted(by_source.keys()):
        b = by_source[src]
        rate = (b['success'] / b['total'] * 100) if b['total'] > 0 else 0
        chart1_bars += _bar(f"{src} ({b['total']})", rate, 100, '#2a9d8f')
    # add avg confidence per source
    chart1_bars += '<div style="margin-top:10px;border-top:1px solid #334155;padding-top:8px;font-size:11px;color:#64748b;font-weight:600;">Avg Confidence</div>'
    for src in sorted(by_source.keys()):
        b = by_source[src]
        avg_conf = (b['conf_sum'] / b['conf_n'] * 100) if b['conf_n'] > 0 else 0
        c = '#10b981' if avg_conf >= 75 else '#f59e0b' if avg_conf >= 50 else '#ef4444'
        chart1_bars += _bar(src, avg_conf, 100, c)

    # Chart 2: By Document Type — count
    max_count = max((d['count'] for d in by_doctype.values()), default=1)
    chart2_bars = ''
    for dt in sorted(by_doctype.keys(), key=lambda k: -by_doctype[k]['count']):
        bd = by_doctype[dt]
        label = dt.replace('_', ' ')
        if len(label) > 25:
            label = label[:23] + '…'
        chart2_bars += _bar(label, bd['count'], max_count, '#8ecae6', suffix='', decimals=0)

    # Chart 3: GT Accuracy by source
    has_any_gt = any(by_source[s]['gt_total'] > 0 for s in by_source)
    chart3_bars = ''
    if has_any_gt:
        for src in sorted(by_source.keys()):
            b = by_source[src]
            if b['gt_total'] > 0:
                acc = b['gt_match'] / b['gt_total'] * 100
                c = '#10b981' if acc >= 75 else '#f59e0b' if acc >= 50 else '#ef4444'
                chart3_bars += _bar(f"{src} ({b['gt_match']}/{b['gt_total']})", acc, 100, c)
            else:
                chart3_bars += _bar(f"{src} (no GT)", 0, 100, '#334155')
        # field coverage by source
        chart3_bars += '<div style="margin-top:10px;border-top:1px solid #334155;padding-top:8px;font-size:11px;color:#64748b;font-weight:600;">Field Coverage</div>'
        for src in sorted(by_source.keys()):
            b = by_source[src]
            cov = (b['filled_sum'] / b['field_sum'] * 100) if b['field_sum'] > 0 else 0
            chart3_bars += _bar(src, cov, 100, '#a78bfa')
    else:
        chart3_bars = '<div style="color:#64748b;font-size:12px;font-style:italic;padding:20px 0;text-align:center;">No ground truth available</div>'
        # show field coverage instead
        chart3_bars += '<div style="margin-top:6px;font-size:11px;color:#64748b;font-weight:600;">Field Coverage</div>'
        for src in sorted(by_source.keys()):
            b = by_source[src]
            cov = (b['filled_sum'] / b['field_sum'] * 100) if b['field_sum'] > 0 else 0
            chart3_bars += _bar(src, cov, 100, '#a78bfa')

    # ── Totals header ──────────────────────────────────────────────────
    total = len(extracted_docs)
    ok = sum(1 for d in extracted_docs if d.get('_status') == 'success')

    html = f"""
    <div style="width:{width};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;margin:16px 0;">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
            <span style="color:#8ecae6;font-size:16px;font-weight:700;">📊 Extraction Analytics</span>
            <span style="color:#64748b;font-size:12px;">{ok}/{total} successful extractions</span>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;">
            <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:14px;">
                <div style="color:#2a9d8f;font-size:13px;font-weight:700;margin-bottom:10px;border-bottom:1px solid #1e293b;padding-bottom:6px;">By Dataset Source</div>
                {chart1_bars}
            </div>
            <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:14px;">
                <div style="color:#8ecae6;font-size:13px;font-weight:700;margin-bottom:10px;border-bottom:1px solid #1e293b;padding-bottom:6px;">By Document Type</div>
                {chart2_bars}
            </div>
            <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:14px;">
                <div style="color:#10b981;font-size:13px;font-weight:700;margin-bottom:10px;border-bottom:1px solid #1e293b;padding-bottom:6px;">GT Accuracy & Coverage</div>
                {chart3_bars}
            </div>
        </div>
    </div>
    """
    display(HTML(html))


def create_hero_section(title, subtitle, description):
    """Create a beautiful hero section with dark mode support."""
    return f"""
    <div style="background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
                padding: 40px; border-radius: 12px; color: white; margin: 20px 0;
                box-shadow: 0 10px 40px rgba(124, 58, 237, 0.3);">
      <h1 style="margin: 0 0 15px 0; font-weight: 700; font-size: 36px;">{title}</h1>
      <h2 style="margin: 0 0 15px 0; font-weight: 600; font-size: 24px; opacity: 0.95;">{subtitle}</h2>
      <p style="font-size: 16px; line-height: 1.6; margin: 0; opacity: 0.9;">{description}</p>
    </div>
    """


def create_metrics_card(metrics_dict):
    """Create a metrics dashboard card."""
    items = []
    for label, value in metrics_dict.items():
        items.append(f"""
        <div style="background: {COLORS['bg_medium']}; padding: 20px; border-radius: 8px;
                    text-align: center; border: 1px solid {COLORS['border']};">
          <div style="font-size: 42px; font-weight: 700; color: {COLORS['accent']};
                      margin-bottom: 8px;">{value}</div>
          <div style="font-size: 14px; color: {COLORS['text_muted']};">{label}</div>
        </div>
        """)

    return f"""
    <div style="background: {COLORS['bg_dark']}; padding: 25px; border-radius: 12px;
                margin: 20px 0; border: 1px solid {COLORS['border']};">
      <h2 style="margin: 0 0 20px 0; font-weight: 700; color: {COLORS['text']};">
        ⚡ Mining Complete!
      </h2>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                  gap: 20px;">
        {''.join(items)}
      </div>
    </div>
    """


def create_schema_card(total, required, optional):
    """Create schema overview card."""
    return f"""
    <div style="background: {COLORS['bg_dark']}; border-left: 4px solid {COLORS['primary']};
                padding: 20px; margin: 15px 0; border-radius: 6px; border: 1px solid {COLORS['border']};">
      <h4 style="margin: 0 0 15px 0; color: {COLORS['primary']};">📋 Schema Overview</h4>
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;
                  color: {COLORS['text']};">
        <div><strong style="color: {COLORS['accent']};">Total Fields:</strong> {total}</div>
        <div><strong style="color: {COLORS['success']};">Required:</strong> {required}</div>
        <div><strong style="color: {COLORS['text_muted']};">Optional:</strong> {optional}</div>
      </div>
    </div>
    """


def create_success_banner():
    """Create success message banner."""
    return f"""
    <div style="background: linear-gradient(135deg, {COLORS['success']} 0%, #059669 100%);
                border-left: 4px solid #047857; padding: 20px; margin: 20px 0;
                border-radius: 8px; color: white; box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3);">
      <h3 style="margin: 0 0 10px 0; font-weight: 700;">🎉 Perfect Score!</h3>
      <p style="margin: 0; font-size: 16px;">All documents processed successfully with no errors. Your pipeline is production-ready!</p>
    </div>
    """


def create_use_case_card(icon, title, description, roi_items, tech_stack=""):
    """Create a compelling use case showcase card."""
    roi_html = ''.join([
        f'<div style="display: flex; align-items: flex-start; gap: 10px; margin: 8px 0;">'
        f'<span style="color: {COLORS["success"]}; font-size: 18px; margin-top: 2px;">✓</span>'
        f'<span style="flex: 1;">{item}</span></div>'
        for item in roi_items
    ])

    tech_html = ""
    if tech_stack:
        tech_html = f"""
        <div style="margin-top: 15px; padding: 12px; background: {COLORS['bg_medium']};
                    border-radius: 6px; border-left: 3px solid {COLORS['accent']};">
          <div style="font-size: 12px; color: {COLORS['text_muted']}; margin-bottom: 5px;">
            🔧 TECH STACK
          </div>
          <div style="color: {COLORS['text']}; font-size: 13px;">{tech_stack}</div>
        </div>
        """

    return f"""
    <div style="background: {COLORS['bg_dark']}; padding: 30px; border-radius: 12px;
                margin: 25px 0; border: 1px solid {COLORS['border']};
                box-shadow: 0 6px 30px rgba(0,0,0,0.4);">
      <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 25px;">
        <div style="font-size: 56px; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));">{icon}</div>
        <div style="flex: 1;">
          <h2 style="margin: 0 0 8px 0; color: {COLORS['primary']}; font-size: 28px;">{title}</h2>
          <p style="margin: 0; color: {COLORS['text_muted']}; font-size: 15px; line-height: 1.5;">
            {description}
          </p>
        </div>
      </div>
      <div style="background: {COLORS['bg_medium']}; padding: 20px; border-radius: 8px;
                  border-left: 4px solid {COLORS['success']};">
        <h4 style="margin: 0 0 12px 0; color: {COLORS['success']}; font-size: 16px;">
          💰 Business Impact & ROI
        </h4>
        <div style="color: {COLORS['text']}; font-size: 14px; line-height: 1.8;">
          {roi_html}
        </div>
        {tech_html}
      </div>
    </div>
    """


USE_CASES = {
    'invoice_processing': {
        'icon': '💰',
        'title': 'Automated AP Workflow',
        'description': 'End-to-end invoice processing from image to insights in seconds',
        'roi_items': [
            '<strong>95% reduction</strong> in manual data entry time',
            '<strong>2-5% cost savings</strong> from duplicate payment detection',
            '<strong>Real-time visibility</strong> into vendor spend patterns',
            '<strong>Audit-ready</strong> with full extraction lineage'
        ],
        'tech_stack': 'JSON-OCR → Pandas → Any ERP (SAP, Oracle, QuickBooks)'
    },
    'medical_triage': {
        'icon': '🏥',
        'title': 'Smart Medical Triage System',
        'description': 'Automatic form routing with missing field detection and HIPAA compliance',
        'roi_items': [
            '<strong>80% faster</strong> form processing vs manual review',
            '<strong>Zero misfiled documents</strong> with AI classification',
            '<strong>Automatic alerts</strong> for missing required fields',
            '<strong>HIPAA compliant</strong> with full audit trail'
        ],
        'tech_stack': 'JSON-OCR → Rule Engine → EMR Integration (Epic, Cerner)'
    },
    'kyc_compliance': {
        'icon': '🔐',
        'title': 'Automated KYC Compliance',
        'description': 'Instant ID verification with fraud detection and regulatory compliance',
        'roi_items': [
            '<strong>10x faster</strong> KYC processing (minutes vs days)',
            '<strong>60-80% reduction</strong> in fraud through quality checks',
            '<strong>100% compliant</strong> with AML/KYC regulations',
            '<strong>Real-time alerts</strong> for suspicious documents'
        ],
        'tech_stack': 'JSON-OCR → Validation Rules → CRM/Compliance System'
    },
    'expense_automation': {
        'icon': '💳',
        'title': 'Global Expense Automation',
        'description': 'Process receipts in any language with automatic categorization and policy checks',
        'roi_items': [
            '<strong>50+ languages</strong> supported automatically',
            '<strong>90% reduction</strong> in expense report processing time',
            '<strong>Real-time policy</strong> violation detection',
            '<strong>Tax-ready exports</strong> for any jurisdiction'
        ],
        'tech_stack': 'JSON-OCR → Policy Engine → Concur/SAP Concur/Expensify'
    },
    'visual_deid': {
        'icon': '🔍',
        'title': 'OCR + Bounding Boxes + De-ID',
        'description': (
            'Enterprise document pipelines need both text extraction and spatial localization. '
            'JSL Vision OCR detects every text region with pixel-level bounding boxes — enabling '
            'layout-aware extraction, surgical PHI/PII redaction, and visual audit trails.'
        ),
        'roi_items': [
            '<strong>Layout-aware OCR</strong>: every text region has pixel coordinates, not just raw text',
            '<strong>Handwriting support</strong>: reads doctors prescriptions, forms, and notes',
            '<strong>Precision redaction</strong>: mask only sensitive fields, not entire pages',
            '<strong>Audit-ready</strong>: bounding box metadata for compliance documentation',
        ],
        'tech_stack': 'JSL Vision OCR + vLLM + Spark NLP DEID',
    },
    'bank_statements': {
        'icon': '🏦',
        'title': 'Bank Statement Intelligence',
        'description': (
            'Finance teams spend hours manually entering bank statement data for reconciliation '
            'and audit. JSON-OCR extracts every transaction row automatically — across any bank '
            'format, any layout.'
        ),
        'roi_items': [
            '<strong>100% of transactions</strong> extracted — no row missed',
            '<strong>Multi-bank support</strong>: HDFC, ICICI, SBI, Axis — no template per bank',
            '<strong>Instant reconciliation</strong>: opening + credits - debits vs closing balance',
            '<strong>Audit-ready CSV export</strong> in seconds vs hours of manual entry',
        ],
        'tech_stack': 'JSON-OCR → Pandas → Any accounting system (Tally, QuickBooks, SAP)',
    },
}


def show_use_case(config_or_key):
    """
    Display use case card - super simple 1-liner in notebooks!

    Args:
        config_or_key: Either a string key (e.g., 'invoice_processing') or custom dict

    Examples:
        # Predefined use case (1 line in notebook)
        show_use_case('invoice_processing')

        # Custom use case
        show_use_case({'icon': '📋', 'title': 'My Use Case', ...})
    """
    # If string key, fetch from predefined use cases
    if isinstance(config_or_key, str):
        if config_or_key not in USE_CASES:
            raise ValueError(f"Unknown use case: {config_or_key}. Available: {list(USE_CASES.keys())}")
        config = USE_CASES[config_or_key]
    else:
        config = config_or_key

    display(HTML(create_use_case_card(
        icon=config.get('icon', '📋'),
        title=config['title'],
        description=config['description'],
        roi_items=config.get('roi_items', []),
        tech_stack=config.get('tech_stack', '')
    )))


def display_schema_comparison(images, schemas, predictions, labels):
    """Interactive 3-column viewer: Image | Schema | Model Predictions.

    Parameters
    ----------
    images      : list[PIL.Image]
    schemas     : list[dict]   The JSON schema definitions used per doc.
    predictions : list[dict]   Model extraction results per doc.
    labels      : list[str]    Label per doc (e.g. "Driver License (13 fields)").
    """
    import base64, json, uuid
    from io import BytesIO
    from IPython.display import HTML, display

    vid = f"sc_{uuid.uuid4().hex[:8]}"

    # Encode images
    imgs_b64 = []
    thumbs_b64 = []
    for img in images:
        # Full image
        full = img.copy()
        if full.mode in ("RGBA", "P", "LA"):
            full = full.convert("RGB")
        buf = BytesIO()
        full.save(buf, format="JPEG", quality=90)
        imgs_b64.append(base64.b64encode(buf.getvalue()).decode())
        # Thumbnail
        thumb = img.copy()
        thumb.thumbnail((64, 48))
        if thumb.mode in ("RGBA", "P", "LA"):
            thumb = thumb.convert("RGB")
        buf2 = BytesIO()
        thumb.save(buf2, format="JPEG", quality=70)
        thumbs_b64.append(base64.b64encode(buf2.getvalue()).decode())

    # Prepare docs JSON
    docs = []
    skip = {"_timing", "_tokens", "_status", "id", "doc_id", "_error", "_source", "$schema"}
    for i in range(len(images)):
        schema = schemas[i] if i < len(schemas) else {}
        pred = predictions[i] if i < len(predictions) else {}
        clean_pred = {k: v for k, v in pred.items() if k not in skip and not k.startswith("_")}
        # Extract schema field info (with nested children for objects/arrays)
        def _extract_fields(props, required_set, depth=0):
            fields = []
            for fname, fdef in props.items():
                ftype = fdef.get("type", "object")
                children = []
                if "enum" in fdef:
                    ftype = f"enum[{len(fdef['enum'])}]"
                elif ftype == "array":
                    items = fdef.get("items", {})
                    item_type = items.get("type", "object")
                    ftype = f"array<{item_type}>"
                    if item_type == "object" and "properties" in items:
                        children = _extract_fields(
                            items["properties"],
                            set(items.get("required", [])),
                            depth + 1)
                elif ftype == "object" and "properties" in fdef:
                    children = _extract_fields(
                        fdef["properties"],
                        set(fdef.get("required", [])),
                        depth + 1)
                fields.append({
                    "name": fname,
                    "type": ftype,
                    "required": fname in required_set,
                    "description": fdef.get("description", ""),
                    "depth": depth,
                    "children": children,
                })
            return fields

        props = schema.get("properties", {})
        required = set(schema.get("required", []))
        schema_fields = _extract_fields(props, required)
        docs.append({
            "image": imgs_b64[i],
            "thumb": thumbs_b64[i],
            "label": labels[i] if i < len(labels) else f"Doc {i}",
            "schema_fields": schema_fields,
            "schema_n": len(props),
            "predictions": clean_pred,
        })

    docs_json = json.dumps(docs)

    html = f"""
    <div id="{vid}" style="width:100%;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
        <style>
            #{vid} .sc-nav {{
                display:flex;justify-content:space-between;align-items:center;
                padding:10px 15px;background:#1e293b;border-radius:6px;
                border:1px solid #334155;margin-bottom:8px;gap:16px;
            }}
            #{vid} .sc-title {{color:#8ecae6;font-size:14px;font-weight:700;white-space:nowrap;}}
            #{vid} .sc-label {{color:#93c5fd;font-size:12px;font-weight:600;
                background:#1e3a5f;padding:3px 10px;border-radius:12px;white-space:nowrap;}}
            #{vid} .sc-controls {{display:flex;align-items:center;gap:12px;}}
            #{vid} .sc-btn {{
                padding:6px 14px;background:#2a9d8f;color:#fff;border:none;
                border-radius:4px;cursor:pointer;font-size:13px;font-weight:500;
            }}
            #{vid} .sc-btn:hover {{background:#3db8a9;}}
            #{vid} .sc-btn:disabled {{background:#334155;cursor:not-allowed;color:#475569;}}
            #{vid} .sc-input {{
                width:40px;padding:5px;text-align:center;border:1px solid #334155;
                border-radius:4px;font-size:13px;background:#0f172a;color:#e2e8f0;
            }}
            #{vid} .sc-counter {{color:#94a3b8;font-size:13px;}}
            #{vid} .sc-progress {{height:3px;background:#0f172a;border-radius:2px;
                margin-bottom:6px;overflow:hidden;}}
            #{vid} .sc-progress-fill {{height:100%;background:linear-gradient(90deg,#2a9d8f,#8ecae6);
                border-radius:2px;transition:width 0.3s ease;}}
            #{vid} .sc-hint {{text-align:right;padding:0 4px 2px 0;color:#475569;
                font-size:10px;letter-spacing:0.04em;}}
            #{vid} .sc-thumbs {{
                display:flex;gap:4px;overflow-x:auto;padding:4px 0 8px 0;
                scrollbar-width:thin;scrollbar-color:#334155 transparent;
            }}
            #{vid} .sc-thumbs::-webkit-scrollbar {{height:4px;}}
            #{vid} .sc-thumbs::-webkit-scrollbar-thumb {{background:#334155;border-radius:2px;}}
            #{vid} .sc-th {{
                flex:0 0 52px;height:38px;border-radius:3px;overflow:hidden;
                cursor:pointer;border:2px solid transparent;opacity:0.45;
                transition:all 0.2s ease;
            }}
            #{vid} .sc-th:hover {{opacity:0.8;border-color:#8ecae6;}}
            #{vid} .sc-th.active {{opacity:1;border-color:#2a9d8f;
                box-shadow:0 0 6px rgba(42,157,143,0.5);}}
            #{vid} .sc-th img {{width:100%;height:100%;object-fit:cover;}}
            #{vid} .sc-layout {{
                display:flex;gap:10px;width:100%;
            }}
            #{vid} .sc-img-panel {{
                flex:0 0 30%;height:600px;overflow:auto;border:1px solid #334155;
                border-radius:4px;padding:10px;background:#0f172a;box-sizing:border-box;
            }}
            #{vid} .sc-img-panel img {{
                max-width:100%;height:auto;display:block;margin:auto;cursor:zoom-in;
                border-radius:4px;
            }}
            #{vid} .sc-schema-panel {{
                flex:1;height:600px;overflow:auto;border:1px solid #334155;
                border-radius:4px;padding:10px;background:#1e293b;box-sizing:border-box;
            }}
            #{vid} .sc-preds-panel {{
                flex:1;height:600px;overflow:auto;border:1px solid #334155;
                border-radius:4px;padding:10px;background:#0f172a;box-sizing:border-box;
            }}
            #{vid} .sc-panel-title {{
                margin:0 0 12px 0;padding:0 0 10px 0;font-size:16px;font-weight:700;
            }}
            #{vid} .sc-schema-title {{color:#93c5fd;border-bottom:2px solid #3b82f6;}}
            #{vid} .sc-preds-title {{color:#2a9d8f;border-bottom:2px solid #2a9d8f;}}
            #{vid} .sc-field {{
                margin-bottom:6px;padding:8px 10px;border-radius:4px;
                display:flex;align-items:baseline;gap:10px;
            }}
            #{vid} .sc-field-schema {{background:#172554;border-left:3px solid #3b82f6;}}
            #{vid} .sc-field-pred {{background:#1e293b;border-left:3px solid #2a9d8f;}}
            #{vid} .sc-fname {{
                font-weight:600;font-size:12px;min-width:140px;flex-shrink:0;
                font-family:'SF Mono',Monaco,Consolas,monospace;
            }}
            #{vid} .sc-fname-schema {{color:#93c5fd;}}
            #{vid} .sc-fname-pred {{color:#6ee7b7;}}
            #{vid} .sc-ftype {{
                font-size:10px;color:#64748b;font-family:monospace;
                background:#1e293b;padding:1px 6px;border-radius:3px;
                flex-shrink:0;
            }}
            #{vid} .sc-freq {{
                font-size:9px;color:#f59e0b;font-weight:700;margin-left:4px;
            }}
            #{vid} .sc-fdesc {{font-size:11px;color:#64748b;font-style:italic;}}
            #{vid} .sc-fval {{font-size:13px;color:#e2e8f0;flex:1;line-height:1.5;}}
            #{vid} .sc-tag {{
                display:inline-block;background:#2a9d8f;color:#fff;
                padding:2px 8px;border-radius:3px;margin:2px;font-size:11px;
            }}
            #{vid} .sc-bool-true {{color:#7bc47f;font-weight:700;}}
            #{vid} .sc-bool-false {{color:#64748b;font-weight:700;}}
            #{vid} .sc-null {{color:#64748b;font-style:italic;}}
            #{vid} .sc-num {{color:#e8b96a;font-weight:500;}}
            #{vid} .sc-obj-row {{
                background:#0f172a;padding:4px 8px;margin:2px 0;border-radius:3px;
                font-size:12px;border-left:2px solid #334155;
            }}
            #{vid} .sc-lightbox {{
                display:none;position:fixed;top:0;left:0;right:0;bottom:0;
                background:rgba(0,0,0,0.85);z-index:10000;cursor:zoom-out;
                align-items:center;justify-content:center;padding:20px;
            }}
            #{vid} .sc-lightbox.open {{display:flex;}}
            #{vid} .sc-lightbox img {{
                max-width:95vw;max-height:95vh;object-fit:contain;
                border-radius:6px;box-shadow:0 8px 32px rgba(0,0,0,0.6);
            }}
            #{vid} .fade {{transition:opacity 0.15s ease;}}
            #{vid} .fade.fading {{opacity:0.3;}}
        </style>

        <div class="sc-lightbox" id="lb_{vid}" onclick="this.classList.remove('open')">
            <img id="lb_img_{vid}" src="">
        </div>

        <div class="sc-nav">
            <span class="sc-title">Schema Comparison</span>
            <span class="sc-label" id="lbl_{vid}"></span>
            <div class="sc-controls">
                <button class="sc-btn" id="prev_{vid}">&#8592;</button>
                <span>
                    <input type="number" class="sc-input" id="jump_{vid}" value="1" min="1">
                    <span class="sc-counter"> / <span id="tot_{vid}">{len(docs)}</span></span>
                </span>
                <button class="sc-btn" id="next_{vid}">&#8594;</button>
            </div>
        </div>
        <div class="sc-progress"><div class="sc-progress-fill" id="prog_{vid}" style="width:0%"></div></div>
        <div class="sc-hint">&#8592; &#8594; navigate &nbsp;&middot;&nbsp; click image to zoom &nbsp;&middot;&nbsp; Esc close</div>
        <div class="sc-thumbs" id="thumbs_{vid}"></div>

        <div class="sc-layout" tabindex="0" id="layout_{vid}" style="outline:none;">
            <div class="sc-img-panel fade" id="imgp_{vid}">
                <img id="img_{vid}" src="">
            </div>
            <div class="sc-schema-panel fade" id="schp_{vid}">
                <h3 class="sc-panel-title sc-schema-title">Schema Definition</h3>
                <div id="sch_body_{vid}"></div>
            </div>
            <div class="sc-preds-panel fade" id="predp_{vid}">
                <h3 class="sc-panel-title sc-preds-title">Model Predictions</h3>
                <div id="pred_body_{vid}"></div>
            </div>
        </div>

        <script>
        (function() {{
            const D = {docs_json};
            let idx = 0;
            const $ = id => document.getElementById(id);
            const vid = '{vid}';

            // Build thumbnails
            const strip = $('thumbs_'+vid);
            D.forEach((d, i) => {{
                const t = document.createElement('div');
                t.className = 'sc-th' + (i===0?' active':'');
                t.dataset.i = i;
                const im = document.createElement('img');
                im.src = 'data:image/jpeg;base64,' + d.thumb;
                im.loading = 'lazy';
                t.appendChild(im);
                t.onclick = () => {{ idx = i; show(); }};
                strip.appendChild(t);
            }});

            function escHtml(s) {{
                const d = document.createElement('div');
                d.textContent = String(s);
                return d.innerHTML;
            }}

            function fmtVal(v, depth) {{
                depth = depth || 0;
                if (v === null || v === undefined || v === '')
                    return '<span class="sc-null">null</span>';
                if (typeof v === 'boolean')
                    return v ? '<span class="sc-bool-true">\\u2714 true</span>'
                             : '<span class="sc-bool-false">\\u2718 false</span>';
                if (typeof v === 'number')
                    return '<span class="sc-num">' + v + '</span>';
                if (Array.isArray(v)) {{
                    if (v.length === 0) return '<span class="sc-null">[]</span>';
                    if (typeof v[0] === 'object' && v[0] !== null) {{
                        return v.slice(0, 8).map((item, ri) => {{
                            const pairs = Object.entries(item)
                                .map(([k,val]) => '<b>' + escHtml(k) + ':</b> ' + fmtVal(val, depth+1))
                                .join(' &nbsp; ');
                            return '<div class="sc-obj-row">' + pairs + '</div>';
                        }}).join('') + (v.length > 8 ? '<div class="sc-null">... +' + (v.length-8) + ' more</div>' : '');
                    }}
                    return v.slice(0, 10).map(x =>
                        '<span class="sc-tag">' + escHtml(String(x)) + '</span>'
                    ).join('') + (v.length > 10 ? '<span class="sc-null"> +' + (v.length-10) + '</span>' : '');
                }}
                if (typeof v === 'object') {{
                    if (depth > 2) return '<span class="sc-null">' + escHtml(JSON.stringify(v)) + '</span>';
                    const pairs = Object.entries(v)
                        .map(([k,val]) => '<b>' + escHtml(k) + ':</b> ' + fmtVal(val, depth+1))
                        .join(' &nbsp; ');
                    return '<div class="sc-obj-row">' + pairs + '</div>';
                }}
                const s = String(v);
                return escHtml(s.length > 200 ? s.slice(0,200) + '\\u2026' : s);
            }}

            function show() {{
                const d = D[idx];
                // Fade
                document.querySelectorAll('#{vid} .fade').forEach(p => p.classList.add('fading'));
                setTimeout(() => {{
                    document.querySelectorAll('#{vid} .fade').forEach(p => p.classList.remove('fading'));
                }}, 120);

                // Image
                $('img_'+vid).src = 'data:image/jpeg;base64,' + d.image;
                $('img_'+vid).onclick = function() {{
                    $('lb_img_'+vid).src = this.src;
                    $('lb_'+vid).classList.add('open');
                }};

                // Label
                $('lbl_'+vid).textContent = d.label;

                // Nav
                $('jump_'+vid).value = idx + 1;
                $('jump_'+vid).max = D.length;
                $('prev_'+vid).disabled = idx === 0;
                $('next_'+vid).disabled = idx === D.length - 1;

                // Progress
                const pct = D.length > 1 ? (idx / (D.length - 1)) * 100 : 100;
                $('prog_'+vid).style.width = pct + '%';

                // Thumbs
                strip.querySelectorAll('.sc-th').forEach(t => {{
                    t.classList.toggle('active', parseInt(t.dataset.i) === idx);
                }});
                const active = strip.querySelector('.sc-th.active');
                if (active) active.scrollIntoView({{block:'nearest',inline:'center',behavior:'smooth'}});

                // Schema panel (recursive for nested fields)
                const schBody = $('sch_body_'+vid);
                schBody.innerHTML = '';
                function renderSchemaFields(fields, container) {{
                    fields.forEach(f => {{
                        const row = document.createElement('div');
                        row.className = 'sc-field sc-field-schema';
                        row.style.marginLeft = (f.depth * 16) + 'px';
                        if (f.depth > 0) row.style.borderLeftColor = '#2563eb';
                        let inner = '<span class="sc-fname sc-fname-schema">'
                            + (f.depth > 0 ? '\\u2514 ' : '') + escHtml(f.name) + '</span>';
                        inner += '<span class="sc-ftype">' + escHtml(f.type) + '</span>';
                        if (f.required) inner += '<span class="sc-freq">REQ</span>';
                        if (f.description) inner += '<br><span class="sc-fdesc">' + escHtml(f.description) + '</span>';
                        row.innerHTML = inner;
                        container.appendChild(row);
                        if (f.children && f.children.length > 0) {{
                            renderSchemaFields(f.children, container);
                        }}
                    }});
                }}
                renderSchemaFields(d.schema_fields, schBody);

                // Predictions panel
                const predBody = $('pred_body_'+vid);
                predBody.innerHTML = '';
                const preds = d.predictions;
                for (const [k, v] of Object.entries(preds)) {{
                    const row = document.createElement('div');
                    row.className = 'sc-field sc-field-pred';
                    row.innerHTML = '<span class="sc-fname sc-fname-pred">' + escHtml(k) + '</span>'
                        + '<span class="sc-fval">' + fmtVal(v) + '</span>';
                    predBody.appendChild(row);
                }}
                if (Object.keys(preds).length === 0) {{
                    predBody.innerHTML = '<div class="sc-null" style="padding:20px;text-align:center">No predictions</div>';
                }}
            }}

            // Nav handlers
            $('prev_'+vid).onclick = () => {{ if (idx > 0) {{ idx--; show(); }} }};
            $('next_'+vid).onclick = () => {{ if (idx < D.length-1) {{ idx++; show(); }} }};
            $('jump_'+vid).onchange = function() {{
                const v = parseInt(this.value) - 1;
                if (v >= 0 && v < D.length) {{ idx = v; show(); }}
            }};

            // Keyboard
            $('layout_'+vid).addEventListener('keydown', function(e) {{
                if (e.key === 'ArrowLeft')  {{ if (idx > 0) {{ idx--; show(); }} e.preventDefault(); }}
                if (e.key === 'ArrowRight') {{ if (idx < D.length-1) {{ idx++; show(); }} e.preventDefault(); }}
            }});
            document.addEventListener('keydown', function(e) {{
                if (e.key === 'Escape') $('lb_'+vid).classList.remove('open');
            }});

            // Init
            show();
            $('layout_'+vid).focus();
        }})();
        </script>
    </div>
    """
    display(HTML(html))


def create_demo_results_card(demo_name, dataset_name, total, success, errors, avg_time):
    """Create demo results summary card."""
    success_rate = (success / total * 100) if total > 0 else 0
    
    return f"""
    <div style="background: {COLORS['bg_dark']}; padding: 20px; border-radius: 8px;
                margin: 15px 0; border: 1px solid {COLORS['border']};">
      <h4 style="margin: 0 0 15px 0; color: {COLORS['primary']}; font-size: 18px;">{demo_name}</h4>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;
                  color: {COLORS['text']}; font-size: 14px;">
        <div>
          <div style="color: {COLORS['text_muted']}; font-size: 12px; margin-bottom: 5px;">DATASET</div>
          <div style="font-weight: 600;">{dataset_name}</div>
        </div>
        <div>
          <div style="color: {COLORS['text_muted']}; font-size: 12px; margin-bottom: 5px;">SUCCESS RATE</div>
          <div style="font-weight: 600; color: {COLORS['success']};">
            {success_rate:.0f}% ({success}/{total})
          </div>
        </div>
        <div>
          <div style="color: {COLORS['text_muted']}; font-size: 12px; margin-bottom: 5px;">ERRORS</div>
          <div style="font-weight: 600; color: {COLORS['error'] if errors > 0 else COLORS['success']};">
            {errors}
          </div>
        </div>
        <div>
          <div style="color: {COLORS['text_muted']}; font-size: 12px; margin-bottom: 5px;">AVG TIME</div>
          <div style="font-weight: 600;">{avg_time:.2f}s</div>
        </div>
      </div>
    </div>
    """


def create_comparison_table(comp_fields, comp_time, min_fields, min_time):
    """Create schema comparison table."""
    value_diff = ((comp_fields/comp_time) / (min_fields/min_time) - 1) * 100
    return f"""
    <div style="background: {COLORS['bg_dark']}; padding: 25px; border-radius: 8px;
                margin: 20px 0; border: 1px solid {COLORS['border']};">
      <h3 style="color: {COLORS['primary']}; margin-bottom: 20px;">🔬 Schema Comparison</h3>
      <table style="width: 100%; border-collapse: collapse; color: {COLORS['text']};">
        <tr style="background: {COLORS['primary']}; color: white;">
          <th style="padding: 12px; text-align: left;">Metric</th>
          <th style="padding: 12px; text-align: center;">Comprehensive</th>
          <th style="padding: 12px; text-align: center;">Minimal</th>
          <th style="padding: 12px; text-align: center;">Difference</th>
        </tr>
        <tr style="background: {COLORS['bg_medium']};">
          <td style="padding: 12px;"><strong>Fields Extracted</strong></td>
          <td style="padding: 12px; text-align: center;">{comp_fields}</td>
          <td style="padding: 12px; text-align: center;">{min_fields}</td>
          <td style="padding: 12px; text-align: center; color: {COLORS['success']};">
            <strong>+{comp_fields - min_fields}</strong>
          </td>
        </tr>
        <tr style="background: {COLORS['bg_dark']};">
          <td style="padding: 12px;"><strong>Inference Time</strong></td>
          <td style="padding: 12px; text-align: center;">{comp_time:.2f}s</td>
          <td style="padding: 12px; text-align: center;">{min_time:.2f}s</td>
          <td style="padding: 12px; text-align: center; color: {COLORS['warning']};">
            <strong>+{comp_time - min_time:.2f}s</strong>
          </td>
        </tr>
        <tr style="background: {COLORS['bg_medium']};">
          <td style="padding: 12px;"><strong>Value per Second</strong></td>
          <td style="padding: 12px; text-align: center;">{comp_fields/comp_time:.1f} fields/s</td>
          <td style="padding: 12px; text-align: center;">{min_fields/min_time:.1f} fields/s</td>
          <td style="padding: 12px; text-align: center; color: {COLORS['success']};">
            <strong>{value_diff:.0f}% more efficient</strong>
          </td>
        </tr>
      </table>
      <div style="margin-top: 20px; padding: 15px; background: {COLORS['bg_medium']};
                  border-radius: 6px; border-left: 4px solid {COLORS['accent']};">
        <strong style="color: {COLORS['accent']};">💡 Key Insight:</strong>
        <span style="color: {COLORS['text']};">
          Comprehensive schemas extract {comp_fields}× more information with minimal time overhead.
          Rich metadata enables semantic search, routing, and analytics—all from a single inference pass.
        </span>
      </div>
    </div>
    """


def display_case_similarity(query_image, query_case, results, title="Case Similarity Search"):
    """
    Two-panel case similarity viewer.
    Left  : mystery image + extracted case data stacked below.
    Right : scrollable vertical gallery of top-k matches.

    Args:
        query_image : PIL Image of the mystery case
        query_case  : dict returned by infer_image_structured (the extracted case)
        results     : list of (case_dict, similarity_score, image) from find_similar_cases
        title       : panel heading
    """
    def _img_b64(img):
        if img is None:
            return ""
        buf = BytesIO()
        img.convert("RGB").save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

    def _safe(v):
        if isinstance(v, list):
            return ", ".join(str(x) for x in v[:5]) if v else "—"
        if isinstance(v, dict):
            return "; ".join(f"{k}: {v2}" for k, v2 in list(v.items())[:3])
        return str(v) if v else "—"

    q_b64   = _img_b64(query_image)
    uid     = uuid.uuid4().hex[:8]

    # ── Key fields to show for query ──────────────────────────────────────────
    q_fields = [
        ("Document Type",   query_case.get("document_type", "—")),
        ("Chief Complaint",  query_case.get("chief_complaint", "—")),
        ("Patient",          f"{query_case.get('patient_age','?')}yo {query_case.get('patient_gender','?')}"),
        ("Symptoms",         _safe(query_case.get("symptoms", []))),
        ("Vitals",           _safe(query_case.get("vital_signs", {}))),
        ("Findings",         _safe(query_case.get("findings", []) or query_case.get("imaging_findings", []))),
        ("Diagnoses",        _safe(query_case.get("diagnoses", []) or [query_case.get("final_diagnosis", "")])),
        ("Summary",          query_case.get("summary", "") or query_case.get("case_summary", "—")),
        ("Keywords",         _safe(query_case.get("keywords", []))),
    ]

    def _q_rows():
        rows = ""
        for label, val in q_fields:
            if val and val != "—":
                rows += f"""
                <tr>
                  <td style="color:#94a3b8;padding:4px 8px 4px 0;white-space:nowrap;vertical-align:top;font-size:12px">{label}</td>
                  <td style="color:#e2e8f0;padding:4px 0;font-size:12px">{val}</td>
                </tr>"""
        return rows

    # ── Match cards ───────────────────────────────────────────────────────────
    def _match_card(case, sim, img, rank):
        img_b64   = _img_b64(img)
        img_tag   = f'<img src="data:image/png;base64,{img_b64}" style="width:100%;max-height:180px;object-fit:cover;border-radius:6px;margin-bottom:8px">' if img_b64 else '<div style="height:80px;background:#334155;border-radius:6px;display:flex;align-items:center;justify-content:center;color:#64748b;font-size:12px;margin-bottom:8px">No image</div>'
        pct       = int(sim * 100)
        bar_color = "#10b981" if pct >= 70 else "#f59e0b" if pct >= 50 else "#ef4444"
        medal     = ["🥇","🥈","🥉"][rank] if rank < 3 else f"#{rank+1}"

        diag    = case.get("final_diagnosis") or "—"
        complaint = case.get("chief_complaint") or "—"
        summary = case.get("case_summary") or "—"
        summary_short = summary[:140] + "…" if len(summary) > 140 else summary
        dtype   = case.get("document_type") or ""
        spec    = case.get("specialty") or ""
        tag_html = ""
        for tag in [dtype, spec]:
            if tag:
                tag_html += f'<span style="background:#334155;color:#94a3b8;font-size:10px;padding:2px 6px;border-radius:10px;margin-right:4px">{tag}</span>'

        return f"""
        <div style="background:#1e293b;border:1px solid #334155;border-radius:10px;padding:12px;margin-bottom:12px">
          {img_tag}
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">
            <span style="font-size:14px;font-weight:600;color:#e2e8f0">{medal} Match</span>
            <span style="font-size:13px;font-weight:700;color:{bar_color}">{pct}%</span>
          </div>
          <div style="background:#0f172a;border-radius:4px;height:4px;margin-bottom:8px">
            <div style="background:{bar_color};height:4px;border-radius:4px;width:{pct}%"></div>
          </div>
          <div style="margin-bottom:4px">{tag_html}</div>
          <table style="width:100%;border-collapse:collapse">
            <tr><td style="color:#94a3b8;font-size:11px;padding:2px 6px 2px 0;white-space:nowrap">Complaint</td><td style="color:#e2e8f0;font-size:11px">{complaint}</td></tr>
            <tr><td style="color:#94a3b8;font-size:11px;padding:2px 6px 2px 0;white-space:nowrap">Diagnosis</td><td style="color:#10b981;font-size:11px;font-weight:600">{diag}</td></tr>
            <tr><td style="color:#94a3b8;font-size:11px;padding:2px 6px 2px 0;white-space:nowrap;vertical-align:top">Summary</td><td style="color:#cbd5e1;font-size:11px">{summary_short}</td></tr>
          </table>
        </div>"""

    match_cards_html = "".join(_match_card(c, s, img, i) for i, (c, s, img) in enumerate(results))

    status = query_case.get("_status", "success")
    err_banner = ""
    if status == "error":
        err_banner = f'<div style="background:#450a0a;border:1px solid #ef4444;border-radius:6px;padding:8px;margin-bottom:10px;color:#fca5a5;font-size:12px">⚠️ Extraction error: {query_case.get("_error","unknown")}</div>'

    html = f"""
    <div id="cs_{uid}" style="font-family:'Inter',system-ui,sans-serif;background:#0f172a;border:1px solid #334155;border-radius:12px;padding:16px;color:#e2e8f0;margin:8px 0">
      <h3 style="margin:0 0 14px 0;color:#7c3aed;font-size:16px">{title}</h3>
      {err_banner}
      <div style="display:flex;gap:16px;align-items:flex-start">

        <!-- LEFT: mystery image + data -->
        <div style="flex:0 0 38%;min-width:0">
          <div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px">Mystery Case</div>
          {'<img src="data:image/png;base64,' + q_b64 + '" style="width:100%;border-radius:8px;border:1px solid #334155;margin-bottom:10px">' if q_b64 else ''}
          <table style="width:100%;border-collapse:collapse">
            {_q_rows()}
          </table>
        </div>

        <!-- RIGHT: scrollable match gallery -->
        <div style="flex:1;min-width:0">
          <div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px">Top {len(results)} Similar Cases</div>
          <div style="max-height:600px;overflow-y:auto;padding-right:4px">
            {match_cards_html}
          </div>
        </div>

      </div>
    </div>"""

    display(HTML(html))


