"""
Plotting and visualization utilities for document processing demos.

Extracted from demo_utils.py — contains all matplotlib-based analysis charts,
gallery views, and summary statistics for invoice, expense, routing, and
mining workflows.
"""

import base64
from io import BytesIO

import numpy as np
import pandas as pd
from IPython.display import display, HTML
from PIL import Image

from utils.viewers import display_document_analysis, create_demo_results_card

__all__ = [
    "plot_routing_analysis",
    "plot_routing_with_accuracy",
    "plot_model_comparison",
    "show_invoice_mvp",
    "show_expense_mvp",
    "plot_invoice_analysis",
    "plot_expense_analysis",
    "encode_image_b64",
    "plot_mining_analysis",
    "plot_ham_demographics",
    "plot_precision_summary",
]


def plot_routing_analysis(df, department_emails, urgency_levels=None):
    """3-panel chart: doc type distribution + department routing + urgency donut, plus email table."""
    if len(df) == 0:
        print("[warn] No data for routing analysis")
        return

    import matplotlib.pyplot as plt

    if urgency_levels is None:
        urgency_levels = ["P1_emergency", "P2_urgent", "P3_standard", "P4_routine"]

    doc_counts = df["document_type"].value_counts()
    routing_counts = df["routing_department"].value_counts()

    fig, axes = plt.subplots(1, 3, figsize=(22, max(8, max(len(doc_counts), len(routing_counts)) * 0.4)))

    axes[0].barh(doc_counts.index, doc_counts.values, color='steelblue')
    axes[0].set_xlabel("Count"); axes[0].set_title("Document Type Classification", fontweight='bold')
    axes[0].grid(axis='x', alpha=0.3)

    dept_labels = [f"{dept}  →  {department_emails.get(dept, '?')}" for dept in routing_counts.index]
    axes[1].barh(dept_labels, routing_counts.values, color='coral')
    axes[1].set_xlabel("Documents Routed"); axes[1].set_title("Department Routing & Email", fontweight='bold')
    axes[1].grid(axis='x', alpha=0.3)

    urg_colors = {"P1_emergency": "#ef4444", "P2_urgent": "#f59e0b", "P3_standard": "#eab308", "P4_routine": "#10b981"}
    urg_short = {"P1_emergency": "P1 Emergency", "P2_urgent": "P2 Urgent", "P3_standard": "P3 Standard", "P4_routine": "P4 Routine"}
    if "urgency" in df.columns:
        urg_counts = df["urgency"].value_counts()
        ordered = [(u, urg_counts.get(u, 0)) for u in urgency_levels if urg_counts.get(u, 0) > 0]
        if ordered:
            axes[2].pie([c for _, c in ordered], labels=[urg_short[u] for u, _ in ordered],
                        colors=[urg_colors[u] for u, _ in ordered], autopct="%1.0f%%", startangle=90,
                        wedgeprops=dict(width=0.55, edgecolor="white"))
    axes[2].set_title("Urgency Distribution", fontweight='bold')
    plt.tight_layout(); plt.show()


def plot_routing_with_accuracy(results, gt_map, department_emails, model_name=None):
    """Combined 2-row chart: routing distributions (row 1) + GT accuracy eval (row 2).

    Row 1: Doc type distribution | Department routing + email | Urgency donut
    Row 2: Per-category accuracy | Confusion matrix | Urgency x Doc type heatmap

    Parameters
    ----------
    results          : list[dict]  Routing results (from run_cached_batch).
    gt_map           : dict        {doc_id: {document_type, routing_department}}.
    department_emails: dict        {department: email}.
    model_name       : str         Model name for display (optional).
    """
    import matplotlib.pyplot as plt
    import pandas as pd
    from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

    ok = [r for r in results if "_error" not in r]
    df = pd.DataFrame(ok)
    if len(df) == 0:
        print("No data for routing analysis")
        return

    urgency_levels = ["P1_emergency", "P2_urgent", "P3_standard", "P4_routine"]

    # Build GT comparison
    rows = []
    for r in ok:
        doc_id = r.get("doc_id", "")
        gt = gt_map.get(doc_id)
        if gt is None:
            continue
        rows.append({
            "doc_id": doc_id,
            "gt_type": gt["document_type"], "pred_type": r["document_type"],
            "type_ok": r["document_type"] == gt["document_type"],
            "gt_dept": gt["routing_department"], "pred_dept": r["routing_department"],
            "dept_ok": r["routing_department"] == gt["routing_department"],
            "urgency": r.get("urgency", ""),
        })
    gt_df = pd.DataFrame(rows) if rows else pd.DataFrame()

    has_gt = len(gt_df) > 0

    # Print accuracy summary
    if has_gt:
        type_acc = gt_df["type_ok"].mean() * 100
        dept_acc = gt_df["dept_ok"].mean() * 100
        print(f"Ground-Truth Accuracy ({len(gt_df)} documents, "
              f"{gt_df['gt_type'].nunique()} categories)\n")
        print(f"  Document Type Accuracy:       {type_acc:5.1f}%  "
              f"({gt_df['type_ok'].sum()}/{len(gt_df)})")
        print(f"  Routing Department Accuracy:  {dept_acc:5.1f}%  "
              f"({gt_df['dept_ok'].sum()}/{len(gt_df)})")
        if model_name:
            print(f"\n  Model: {model_name}")

    # ── Theme ─────────────────────────────────────────────────────────────────
    DARK_BG  = "#1e293b"
    PANEL_BG = "#334155"
    TEXT_CLR = "#e2e8f0"
    BORDER   = "#475569"

    def _style(ax, title):
        ax.set_facecolor(PANEL_BG)
        ax.tick_params(colors=TEXT_CLR, labelsize=9)
        ax.set_title(title, color=TEXT_CLR, fontsize=11, fontweight="bold", pad=8)
        for sp in ax.spines.values():
            sp.set_edgecolor(BORDER)
        for lbl in ax.get_xticklabels() + ax.get_yticklabels():
            lbl.set_color(TEXT_CLR)
        if ax.get_xlabel():
            ax.xaxis.label.set_color(TEXT_CLR)
        if ax.get_ylabel():
            ax.yaxis.label.set_color(TEXT_CLR)

    # ── Figure ────────────────────────────────────────────────────────────────
    nrows = 2 if has_gt else 1
    fig, axes = plt.subplots(nrows, 3, figsize=(24, 8 * nrows),
                             gridspec_kw={"width_ratios": [1, 1.2, 1]})
    fig.patch.set_facecolor(DARK_BG)
    if nrows == 1:
        axes = axes[None, :]  # ensure 2d indexing

    # ── Row 1: Distribution charts ────────────────────────────────────────────
    doc_counts = df["document_type"].value_counts()
    axes[0, 0].barh(doc_counts.index, doc_counts.values, color="#7c3aed")
    axes[0, 0].set_xlabel("Count")
    axes[0, 0].grid(axis="x", alpha=0.15, color=BORDER)
    _style(axes[0, 0], "Document Type Classification")

    routing_counts = df["routing_department"].value_counts()
    dept_labels = [f"{d}  \u2192  {department_emails.get(d, '?')}" for d in routing_counts.index]
    axes[0, 1].barh(dept_labels, routing_counts.values, color="#06b6d4")
    axes[0, 1].set_xlabel("Documents Routed")
    axes[0, 1].grid(axis="x", alpha=0.15, color=BORDER)
    _style(axes[0, 1], "Department Routing & Email")

    urg_colors = {"P1_emergency": "#ef4444", "P2_urgent": "#f59e0b",
                  "P3_standard": "#eab308", "P4_routine": "#10b981"}
    urg_short = {"P1_emergency": "P1 Emergency", "P2_urgent": "P2 Urgent",
                 "P3_standard": "P3 Standard", "P4_routine": "P4 Routine"}
    if "urgency" in df.columns:
        urg_counts = df["urgency"].value_counts()
        ordered = [(u, urg_counts.get(u, 0)) for u in urgency_levels if urg_counts.get(u, 0) > 0]
        if ordered:
            axes[0, 2].pie([c for _, c in ordered],
                           labels=[urg_short[u] for u, _ in ordered],
                           colors=[urg_colors[u] for u, _ in ordered],
                           autopct="%1.0f%%", startangle=90,
                           textprops={"color": TEXT_CLR, "fontsize": 9},
                           wedgeprops=dict(width=0.55, edgecolor=PANEL_BG))
    _style(axes[0, 2], "Urgency Distribution")

    # ── Row 2: GT accuracy (only when GT available) ───────────────────────────
    if has_gt:
        # Panel 1: per-category accuracy bar
        cat_acc = gt_df.groupby("gt_type")["type_ok"].agg(["sum", "count"])
        cat_acc["pct"] = cat_acc["sum"] / cat_acc["count"] * 100
        cat_acc = cat_acc.sort_values("pct")
        bar_colors = ["#ef4444" if p < 50 else "#f59e0b" if p < 80 else "#10b981"
                      for p in cat_acc["pct"]]
        axes[1, 0].barh([t.replace("_", " ") for t in cat_acc.index],
                        cat_acc["pct"], color=bar_colors)
        for i, (idx, row) in enumerate(cat_acc.iterrows()):
            axes[1, 0].text(row["pct"] + 1, i,
                            f'{int(row["sum"])}/{int(row["count"])}',
                            va="center", fontsize=9, color=TEXT_CLR)
        axes[1, 0].set_xlim(0, 110)
        axes[1, 0].set_xlabel("Accuracy %")
        axes[1, 0].axvline(x=50, color=BORDER, linestyle="--", alpha=0.4)
        _style(axes[1, 0], "Per-Category Accuracy")

        # Panel 2: confusion matrix
        labels = sorted(gt_df["gt_type"].unique())
        cm = confusion_matrix(gt_df["gt_type"], gt_df["pred_type"], labels=labels)
        disp = ConfusionMatrixDisplay(
            cm, display_labels=[l.replace("_", " ") for l in labels]
        )
        disp.plot(ax=axes[1, 1], cmap="PuBu", values_format="d", xticks_rotation=45)
        _style(axes[1, 1], "Confusion Matrix")

        # Panel 3: urgency x doc type heatmap
        urg_pivot = pd.crosstab(
            gt_df["gt_type"], gt_df["urgency"]
        ).reindex(columns=urgency_levels, fill_value=0)
        if len(urg_pivot) > 0:
            im = axes[1, 2].imshow(urg_pivot.values, cmap="PuBu", aspect="auto")
            axes[1, 2].set_xticks(range(len(urgency_levels)))
            axes[1, 2].set_xticklabels(["P1", "P2", "P3", "P4"])
            axes[1, 2].set_yticks(range(len(urg_pivot)))
            axes[1, 2].set_yticklabels(
                [t.replace("_", " ") for t in urg_pivot.index], fontsize=8)
            for i in range(len(urg_pivot)):
                for j in range(len(urgency_levels)):
                    v = urg_pivot.values[i, j]
                    if v > 0:
                        axes[1, 2].text(j, i, str(v), ha="center",
                                        va="center", fontweight="bold", color=TEXT_CLR)
            cbar = plt.colorbar(im, ax=axes[1, 2], label="Count", shrink=0.8)
            cbar.ax.yaxis.set_tick_params(color=TEXT_CLR)
            cbar.ax.yaxis.label.set_color(TEXT_CLR)
            plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TEXT_CLR)
            cbar.outline.set_edgecolor(BORDER)
        _style(axes[1, 2], "Urgency \u00d7 Doc Type")

    plt.tight_layout()
    plt.show()


def plot_model_comparison(nb_name, cache_key, gt_map, model_labels=None,
                          exclude_models=None):
    """Compare routing accuracy across all cached models.

    Loads cached results for each model, computes GT accuracy, and plots
    a grouped bar chart (doc type accuracy + dept accuracy + success rate).

    Args:
        nb_name:        notebook cache name
        cache_key:      cache key for routing results (e.g. "routing_results")
        gt_map:         {doc_id: {document_type, routing_department}}
        model_labels:   optional dict {cache_model_name: display_label}
        exclude_models: optional set/list of cache model names to skip
    """
    from utils.core import load_nb_cache, has_nb_cache, list_cached_models
    import matplotlib.pyplot as plt
    import pandas as pd

    _exclude = set(exclude_models or [])
    models = list_cached_models(nb_name)
    models = [m for m in models
              if has_nb_cache(nb_name, cache_key, model=m) and m not in _exclude]
    if not models:
        print("No cached models found")
        return

    if model_labels is None:
        model_labels = {}
    _default_labels = {
        "jsl-medical-vl-7b": "JSL MedVL 7B",
        "jsl-medical-vl-30b": "JSL MedVL 30B",
        "anthropic_claude-sonnet-4": "Claude Sonnet 4",
        "anthropic_claude-sonnet-4.6": "Claude Sonnet 4.6",
        "openai_gpt-4.1": "GPT-4.1",
        "openai_gpt-5.4": "GPT-5.4",
        "jsl_vision_ocr_structured_1_0": "JSL Vision OCR Structured 1.0",
    }

    rows = []
    for m in models:
        label = model_labels.get(m, _default_labels.get(m, m))
        cached = load_nb_cache(nb_name, cache_key, model=m)
        results = cached.get("results", [])
        ok = [r for r in results if "_error" not in r]
        # GT accuracy
        type_match, dept_match, gt_total = 0, 0, 0
        for r in ok:
            gt = gt_map.get(r.get("doc_id", ""))
            if gt is None:
                continue
            gt_total += 1
            if r.get("document_type") == gt["document_type"]:
                type_match += 1
            if r.get("routing_department") == gt["routing_department"]:
                dept_match += 1
        rows.append({
            "model": label,
            "success_rate": len(ok) / len(results) * 100 if results else 0,
            "type_acc": type_match / gt_total * 100 if gt_total else 0,
            "dept_acc": dept_match / gt_total * 100 if gt_total else 0,
            "n_ok": len(ok),
            "n_total": len(results),
            "n_gt": gt_total,
        })

    df = pd.DataFrame(rows)

    # Print table
    print(f"Model Comparison -- {len(df)} models, {cache_key}\n")
    for _, r in df.iterrows():
        print(f"  {r['model']:<22s}  Type: {r['type_acc']:5.1f}%  "
              f"Dept: {r['dept_acc']:5.1f}%  "
              f"Success: {r['n_ok']}/{r['n_total']}")

    # Plot
    DARK_BG  = "#1e293b"
    PANEL_BG = "#334155"
    TEXT_CLR = "#e2e8f0"
    BORDER   = "#475569"

    fig, ax = plt.subplots(figsize=(12, max(5, len(df) * 1.2)))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(PANEL_BG)
    y = range(len(df))
    h = 0.25
    bar_colors = {"type_acc": "#7c3aed", "dept_acc": "#10b981", "success_rate": "#94a3b8"}

    bars1 = ax.barh([i - h for i in y], df["type_acc"], h, label="Doc Type Accuracy",
                    color=bar_colors["type_acc"])
    bars2 = ax.barh(list(y), df["dept_acc"], h, label="Dept Routing Accuracy",
                    color=bar_colors["dept_acc"])
    bars3 = ax.barh([i + h for i in y], df["success_rate"], h, label="Success Rate",
                    color=bar_colors["success_rate"])

    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            w = bar.get_width()
            ax.text(w + 0.5, bar.get_y() + bar.get_height() / 2,
                    f"{w:.0f}%", va="center", fontsize=9, color=TEXT_CLR)

    ax.set_yticks(list(y))
    ax.set_yticklabels(df["model"])
    ax.set_xlim(0, 110)
    ax.set_xlabel("Accuracy %")
    ax.set_title("Model Comparison -- Medical Document Routing",
                 color=TEXT_CLR, fontsize=11, fontweight="bold", pad=8)
    ax.tick_params(colors=TEXT_CLR, labelsize=9)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_color(TEXT_CLR)
    ax.xaxis.label.set_color(TEXT_CLR)
    ax.legend(loc="lower right", facecolor=PANEL_BG, edgecolor=BORDER,
              labelcolor=TEXT_CLR)
    ax.grid(axis="x", alpha=0.15, color=BORDER)
    plt.tight_layout()
    plt.show()


def show_invoice_mvp(invoice_imgs, invoice_results, invoice_df, output_dir):
    """Gallery + vendor spend + duplicate detection + ERP export + results card."""
    import pandas as pd
    from pathlib import Path
    output_dir = Path(output_dir)

    # Visual gallery
    print("\nINVOICE GALLERY\n")
    ok_idx   = [i for i, r in enumerate(invoice_results) if "_error" not in r]
    ok_imgs  = [invoice_imgs[i] for i in ok_idx]
    ok_preds = [dict(r) for r in [invoice_results[i] for i in ok_idx]]
    _inv_src_map = {
        "SR": "rth/sroie-2019-v2",
        "MC": "mychen76/invoices-and-receipts_ocr_v1",
        "RV": "rikeshVertex/invoice-receipt-cheque-bankstatement-dataset",
        "HQ": "Voxel51/high-quality-invoice-images-for-ocr",
        "VX": "Voxel51/scanned_receipts",
    }
    for pred in ok_preds:
        _inv_id = pred.get("invoice_id", "")
        _prefix = _inv_id.split("-")[0] if "-" in _inv_id else _inv_id
        pred["_dataset_source"] = _inv_src_map.get(_prefix, _prefix)
    if ok_imgs:
        display_document_analysis(ok_imgs, ok_preds)
        print(f"\n[ok] {len(ok_imgs)} invoices -- click any value to filter\n")

    if len(invoice_df) == 0:
        return

    # Vendor spend
    if "vendor_name" in invoice_df.columns and "total_amount" in invoice_df.columns:
        df = invoice_df.copy()
        df["vendor_name"]  = df["vendor_name"].fillna("Uncategorized").replace("", "Uncategorized")
        df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce").fillna(0)
        spend = (df.groupby("vendor_name")["total_amount"]
                   .agg(["sum", "count", "mean"])
                   .rename(columns={"sum": "Total Spend", "count": "Invoices", "mean": "Avg"})
                   .sort_values("Total Spend", ascending=False))
        print("VENDOR SPEND")
        print(spend.head(6).to_string())

    # Duplicate detection
    if "vendor_name" in invoice_df.columns and "total_amount" in invoice_df.columns:
        dups = invoice_df[invoice_df.duplicated(subset=["vendor_name", "total_amount"], keep=False)]
        print(f"\n[warn]  DUPLICATES: {len(dups)} potential duplicate entries")
        if len(dups) > 0:
            print(dups[["vendor_name", "total_amount"]].head(5).to_string(index=False))

    # ERP export
    export_file = output_dir / "invoice_extract_for_erp.json"
    invoice_df.to_json(export_file, orient="records", indent=2)
    print(f"\n[ok] ERP export: {export_file}")

    errors = len([r for r in invoice_results if "_error" in r])
    avg_t  = invoice_df["_timing"].mean() if "_timing" in invoice_df.columns else 0
    display(HTML(create_demo_results_card(
        "Invoice Processing", "SROIE-2019 + Voxel51",
        len(invoice_results), len(invoice_df), errors, avg_t,
    )))


def show_expense_mvp(expense_imgs, expense_results, expense_df, output_dir):
    """Gallery + language + categories + line items + policy + tax export + results card."""
    import pandas as pd
    from pathlib import Path
    output_dir = Path(output_dir)

    # Visual gallery
    print("\nMULTILINGUAL RECEIPT GALLERY\n")
    ok_idx   = [i for i, r in enumerate(expense_results) if "_error" not in r]
    ok_imgs  = [expense_imgs[i] for i in ok_idx]
    ok_preds = [dict(r) for r in [expense_results[i] for i in ok_idx]]
    _exp_src_map = {
        "KR": "Kratos-AI/Korean_Receipts_Dataset",
        "CD": "naver-clova-ix/cord-v2",
        "TZ": "gurudal/tezba-invoice-images",
        "ML": "CC1984/mall_receipt_extraction_dataset",
        "BK": "tusharshah2006/bank_statements_transactions",
    }
    # Exchange rates as of 2026-02-16 (units per 1 USD)
    _FX = {
        "KRW": 1462.75, "WON": 1462.75,
        "IDR": 16800.0,  "RUPIAH": 16800.0,
        "MYR": 3.945,    "RM": 3.945,
        "CZK": 20.45,
        "THB": 31.53,    "BAHT": 31.53,
        "JPY": 157.10,   "YEN": 157.10,
        "CNY": 6.939,    "YUAN": 6.939, "RMB": 6.939,
        "SGD": 1.271,
        "EUR": 0.8475,
        "GBP": 0.7356,   "BRITISH POUND": 0.7356,
        "CAD": 1.418,
        "AUD": 1.622,
        "HKD": 7.785,
        "INR": 86.8,
        "MXN": 20.35,
        "BRL": 5.87,
    }
    for pred in ok_preds:
        _exp_id = pred.get("expense_id", "")
        _prefix = _exp_id.split("-")[0] if "-" in _exp_id else _exp_id
        pred["_dataset_source"] = _exp_src_map.get(_prefix, _prefix)
        # USD equivalent
        _cur = str(pred.get("currency") or "").strip().upper()
        _amt = pred.get("total_amount")
        if _cur and _cur not in ("USD", "") and _amt is not None:
            _rate = _FX.get(_cur)
            if _rate:
                pred["_usd_equivalent"] = round(float(_amt) / _rate, 2)
    if ok_imgs:
        display_document_analysis(ok_imgs, ok_preds)
        print(f"\n[ok] {len(ok_imgs)} receipts -- filter by language, category, currency\n")

    if len(expense_df) == 0:
        return

    # Language detection
    if "language" in expense_df.columns:
        print("LANGUAGES DETECTED")
        print(expense_df["language"].fillna("Unknown").value_counts().to_string())
        if "translations" in expense_df.columns:
            print(f"\n  {expense_df['translations'].dropna().__len__()} receipts have English translations")

    # Categorization
    if "expense_category" in expense_df.columns:
        print("\nEXPENSE CATEGORIES")
        print(expense_df["expense_category"].fillna("Uncategorized").value_counts().to_string())

    # Line items
    if "line_items" in expense_df.columns:
        counts     = expense_df["line_items"].apply(lambda x: len(x) if isinstance(x, list) else 0)
        total_items = counts.sum()
        translated  = sum(
            1 for items in expense_df["line_items"] if isinstance(items, list)
            for item in items if isinstance(item, dict) and item.get("description_translated")
        )
        print(f"\nLINE ITEMS: {total_items} total - {total_items/len(expense_df):.1f} avg/receipt - {translated} translated")

    # Policy violations — Python-side rule engine
    # Model flags semantics (has_alcohol, has_personal_items);
    # Python enforces numeric thresholds.
    MEALS_LIMIT_USD = 100  # flag meals receipts whose USD equivalent exceeds this

    violations = []
    for _, row in expense_df.iterrows():
        reasons = []
        if row.get("has_alcohol") is True:
            reasons.append("alcohol detected")
        if row.get("has_personal_items") is True:
            reasons.append("personal items detected")
        cat = str(row.get("expense_category", "")).strip().lower()
        cur = str(row.get("currency", "")).strip().upper()
        amt = pd.to_numeric(row.get("total_amount", 0), errors="coerce") or 0
        # Convert to USD for universal threshold check
        _rate    = _FX.get(cur) or (_FX.get(cur.upper()) if cur else None)
        _usd_amt = (float(amt) / _rate) if _rate else (float(amt) if cur == "USD" else None)
        if cat == "meals" and _usd_amt is not None and _usd_amt > MEALS_LIMIT_USD:
            reasons.append(f"meals > ${MEALS_LIMIT_USD} (≈${_usd_amt:.0f} USD)")
        tip      = pd.to_numeric(row.get("tip", None), errors="coerce")
        subtotal = pd.to_numeric(row.get("subtotal", None), errors="coerce")
        base     = subtotal if (subtotal and subtotal > 0) else amt
        if tip and base and base > 0 and tip / base > 0.20:
            reasons.append(f"excessive tip ({tip/base*100:.0f}% of subtotal)")
        if reasons:
            violations.append({
                "id":      row.get("expense_id", "?"),
                "vendor":  row.get("vendor_name", "?"),
                "reasons": reasons,
            })

    print(f"\n[warn]  POLICY VIOLATIONS: {len(violations)} receipts flagged")
    for v in violations[:5]:
        print(f"  {v['id']} ({v['vendor']}): {', '.join(v['reasons'])}")

    # Tax-ready CSV
    desired = ["expense_id", "date", "vendor_name", "expense_category", "total_amount", "tax_amount"]
    cols    = [c for c in desired if c in expense_df.columns]
    tax_path = output_dir / "expense_report_tax_ready.csv"
    expense_df[cols].to_csv(tax_path, index=False)
    print(f"\n[ok] Tax export ({', '.join(cols)}): {tax_path}")

    errors = len([r for r in expense_results if "_error" in r])
    display(HTML(create_demo_results_card(
        "Multilingual Expense Intelligence", "Korean Receipts + CORD-v2",
        len(expense_results), len(expense_df), errors, 0,
    )))


def plot_invoice_analysis(invoice_results, invoice_df):
    """2×3 dark-mode analysis chart for invoice processing results (NB2 Section 1)."""
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    if len(invoice_df) == 0:
        print("[warn] No invoice data to analyse")
        return

    DARK_BG  = "#1e1e2e"
    PANEL_BG = "#2d2d3e"
    TEXT_CLR = "#cccccc"
    PALETTE  = ["#81b4d8", "#8ecae6", "#e8b96a", "#2a9d8f",
                "#3db8a9", "#f4a261", "#e76f51", "#a8dadc", "#c77dff", "#90e0ef"]

    def _style(ax, title):
        ax.set_facecolor(PANEL_BG)
        ax.tick_params(colors=TEXT_CLR, labelsize=9)
        ax.set_title(title, color="#e0e0e0", fontsize=11, fontweight="bold", pad=8)
        for sp in ax.spines.values():
            sp.set_edgecolor("#444455")
        for lbl in ax.get_xticklabels() + ax.get_yticklabels():
            lbl.set_color(TEXT_CLR)
        if ax.get_xlabel():
            ax.xaxis.label.set_color(TEXT_CLR)
        if ax.get_ylabel():
            ax.yaxis.label.set_color(TEXT_CLR)

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.patch.set_facecolor(DARK_BG)
    fig.suptitle("Invoice Processing · Analysis Overview", color="#e0e0e0",
                 fontsize=14, fontweight="bold", y=1.01)

    # 1 · Top vendors by invoice count (pie)
    ax = axes[0, 0]
    if "vendor_name" in invoice_df.columns:
        vc = invoice_df["vendor_name"].fillna("Uncategorized").replace("", "Uncategorized") \
               .value_counts().head(8)
        if len(vc) > 0:
            _, texts, autos = ax.pie(
                vc.values, labels=vc.index,
                autopct="%1.0f%%", colors=PALETTE[:len(vc)], startangle=90,
                textprops={"color": TEXT_CLR, "fontsize": 8},
            )
            for at in autos:
                at.set_color("white"); at.set_fontsize(8)
            ax.set_facecolor(PANEL_BG)
    _style(ax, "Top Vendors by Invoice Count")

    # 2 · Amount distribution by currency (one KDE line per currency, log scale)
    ax = axes[0, 1]
    if "currency" in invoice_df.columns and "total_amount" in invoice_df.columns:
        df_c = invoice_df.copy()
        df_c["currency"] = df_c["currency"].fillna("Uncategorized").replace("", "Uncategorized")
        df_c["total_amount"] = pd.to_numeric(df_c["total_amount"], errors="coerce")
        df_c = df_c[df_c["total_amount"] > 0]
        currencies = df_c["currency"].value_counts().index[:len(PALETTE)]
        plotted = False
        for i, curr in enumerate(currencies):
            vals = df_c[df_c["currency"] == curr]["total_amount"].dropna()
            if len(vals) > 1:
                kde_ok = False
                if vals.nunique() > 1:
                    try:
                        from scipy.stats import gaussian_kde
                        kde = gaussian_kde(vals, bw_method="scott")
                        x_range = np.linspace(vals.min(), vals.max(), 300)
                        ax.plot(x_range, kde(x_range), color=PALETTE[i], linewidth=2.5, label=curr)
                        kde_ok = True
                        plotted = True
                    except Exception:
                        pass
                if not kde_ok:
                    ax.hist(vals, bins=min(8, vals.nunique()), alpha=0.5,
                            color=PALETTE[i], label=curr, density=True, edgecolor="#444455")
                    plotted = True
            elif len(vals) == 1:
                ax.axvline(vals.iloc[0], color=PALETTE[i], linewidth=2, linestyle="--", label=curr)
                plotted = True
        if plotted:
            ax.legend(facecolor=PANEL_BG, edgecolor="#444455", labelcolor=TEXT_CLR, fontsize=9)
            ax.set_xlabel("Amount")
            ax.set_ylabel("Density")
    _style(ax, "Invoice Amount Distribution by Currency")

    # 3 · Currency breakdown (pie)
    ax = axes[0, 2]
    if "currency" in invoice_df.columns:
        cc = invoice_df["currency"].fillna("Uncategorized").replace("", "Uncategorized") \
               .value_counts().head(8)
        if len(cc) > 0:
            _, texts, autos = ax.pie(
                cc.values, labels=cc.index,
                autopct="%1.0f%%", colors=PALETTE, startangle=90,
                textprops={"color": TEXT_CLR, "fontsize": 9},
            )
            for at in autos:
                at.set_color("white"); at.set_fontsize(8)
            ax.set_facecolor(PANEL_BG)
    _style(ax, "Currency Breakdown")

    # 4 · Line items per invoice (value-count bar — clean for discrete integers)
    ax = axes[1, 0]
    if "line_items" in invoice_df.columns:
        item_counts = invoice_df["line_items"].apply(
            lambda x: len(x) if isinstance(x, list) else 0
        )
        vc = item_counts.value_counts().sort_index()
        if len(vc) > 0:
            ax.bar(vc.index.astype(str), vc.values, color="#3db8a9", edgecolor="#444455")
            ax.set_xlabel("Line Items per Invoice")
            ax.set_ylabel("# Invoices")
    _style(ax, "Line Items per Invoice")

    # 5 · Top vendors by total spend
    ax = axes[1, 1]
    if "vendor_name" in invoice_df.columns and "total_amount" in invoice_df.columns:
        df_s = invoice_df.copy()
        df_s["vendor_name"] = df_s["vendor_name"].fillna("Uncategorized").replace("", "Uncategorized")
        df_s["total_amount"] = pd.to_numeric(df_s["total_amount"], errors="coerce").fillna(0)
        vs = df_s.groupby("vendor_name")["total_amount"].sum().sort_values(ascending=False).head(6)
        vs = vs[vs > 0]
        if len(vs) > 0:
            ax.barh(vs.index[::-1], vs.values[::-1], color="#f4a261")
            ax.set_xlabel("Total Spend")
    _style(ax, "Top Vendors by Spend")

    # 6 · Processing time histogram
    ax = axes[1, 2]
    timings = [r.get("_timing", 0) for r in invoice_results if "_error" not in r and r.get("_timing")]
    if timings:
        ax.hist(timings, bins=min(12, len(timings)), color="#81b4d8", edgecolor="#444455")
        ax.set_xlabel("Seconds")
        ax.set_ylabel("Documents")
    _style(ax, "Processing Time per Invoice")

    plt.tight_layout(pad=2.5)
    plt.show()

    # Summary stats
    total    = len(invoice_results)
    success  = len(invoice_df)
    amt_col  = pd.to_numeric(invoice_df["total_amount"], errors="coerce") if "total_amount" in invoice_df.columns else pd.Series()
    total_val = amt_col.sum()
    avg_items = invoice_df["line_items"].apply(lambda x: len(x) if isinstance(x, list) else 0).mean() \
        if "line_items" in invoice_df.columns else 0
    top_vendor = invoice_df["vendor_name"].dropna().value_counts().index[0] \
        if "vendor_name" in invoice_df.columns and invoice_df["vendor_name"].dropna().any() else "N/A"
    avg_time = float(np.mean(timings)) if timings else 0.0

    print("\nInvoice Processing Summary")
    print(f"  - Documents processed   : {success}/{total}")
    print(f"  - Total value extracted : {total_val:,.0f}")
    print(f"  - Avg line items/invoice: {avg_items:.1f}")
    print(f"  - Top vendor            : {top_vendor}")
    print(f"  - Avg time / invoice    : {avg_time:.1f}s")
    if "currency" in invoice_df.columns:
        print(f"  - Currencies found      : {invoice_df['currency'].dropna().value_counts().to_dict()}")


def plot_expense_analysis(expense_results, expense_df):
    """2×3 dark-mode analysis chart for expense/receipt processing results (NB2 Section 2)."""
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    if len(expense_df) == 0:
        print("[warn] No expense data to analyse")
        return

    DARK_BG  = "#1e1e2e"
    PANEL_BG = "#2d2d3e"
    TEXT_CLR = "#cccccc"
    PALETTE  = ["#81b4d8", "#8ecae6", "#e8b96a", "#2a9d8f",
                "#3db8a9", "#f4a261", "#e76f51", "#a8dadc", "#c77dff", "#90e0ef"]

    def _style(ax, title):
        ax.set_facecolor(PANEL_BG)
        ax.tick_params(colors=TEXT_CLR, labelsize=9)
        ax.set_title(title, color="#e0e0e0", fontsize=11, fontweight="bold", pad=8)
        for sp in ax.spines.values():
            sp.set_edgecolor("#444455")
        for lbl in ax.get_xticklabels() + ax.get_yticklabels():
            lbl.set_color(TEXT_CLR)
        if ax.get_xlabel():
            ax.xaxis.label.set_color(TEXT_CLR)
        if ax.get_ylabel():
            ax.yaxis.label.set_color(TEXT_CLR)

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.patch.set_facecolor(DARK_BG)
    fig.suptitle("Expense Intelligence · Analysis Overview", color="#e0e0e0",
                 fontsize=14, fontweight="bold", y=1.01)

    # 1 · Language distribution
    ax = axes[0, 0]
    if "language" in expense_df.columns:
        lc = expense_df["language"].fillna("Uncategorized").replace("", "Uncategorized") \
               .value_counts().head(8)
        if len(lc) > 0:
            ax.bar(lc.index, lc.values, color=PALETTE[:len(lc)])
            ax.set_ylabel("Count")
            ax.tick_params(axis="x", rotation=30)
    _style(ax, "Language Distribution")

    # 2 · Expense category breakdown (pie)
    ax = axes[0, 1]
    if "expense_category" in expense_df.columns:
        ec = expense_df["expense_category"].fillna("Uncategorized").replace("", "Uncategorized") \
               .value_counts().head(8)
        if len(ec) > 0:
            _, texts, autos = ax.pie(
                ec.values, labels=ec.index,
                autopct="%1.0f%%", colors=PALETTE, startangle=90,
                textprops={"color": TEXT_CLR, "fontsize": 9},
            )
            for at in autos:
                at.set_color("white"); at.set_fontsize(8)
            ax.set_facecolor(PANEL_BG)
    _style(ax, "Expense Categories")

    # 3 · Total amount distribution
    ax = axes[0, 2]
    if "total_amount" in expense_df.columns:
        amounts = pd.to_numeric(expense_df["total_amount"], errors="coerce").dropna()
        amounts = amounts[amounts > 0]
        if len(amounts) > 0:
            ax.hist(amounts, bins=min(15, len(amounts)), color="#e8b96a", edgecolor="#444455")
            ax.set_xlabel("Total Amount")
            ax.set_ylabel("Count")
    _style(ax, "Spend Distribution")

    # 4 · Line items per receipt
    ax = axes[1, 0]
    if "line_items" in expense_df.columns:
        item_counts = expense_df["line_items"].apply(
            lambda x: len(x) if isinstance(x, list) else 0
        )
        pos = item_counts[item_counts > 0]
        if len(pos) > 0:
            ax.hist(pos, bins=min(10, int(pos.max())), color="#3db8a9", edgecolor="#444455")
            ax.set_xlabel("Line Items per Receipt")
            ax.set_ylabel("Count")
    _style(ax, "Line Items per Receipt")

    # 5 · Policy compliance
    ax = axes[1, 1]
    if "policy_violation" in expense_df.columns:
        violations = int(expense_df["policy_violation"].astype(bool).sum())
        clean = len(expense_df) - violations
        pairs = [(f"Clean ({clean})", clean, "#3db8a9"),
                 (f"Violation ({violations})", violations, "#e76f51")]
        labels_, values_, colors_ = zip(*[(l, v, c) for l, v, c in pairs if v > 0])
        ax.pie(values_, labels=labels_, autopct="%1.0f%%", colors=colors_, startangle=90,
               textprops={"color": TEXT_CLR, "fontsize": 9})
        for t in ax.texts:
            t.set_color("white")
        ax.set_facecolor(PANEL_BG)
    _style(ax, "Policy Compliance")

    # 6 · Payment method or receipt quality
    ax = axes[1, 2]
    if "payment_method" in expense_df.columns and expense_df["payment_method"].dropna().any():
        pm = expense_df["payment_method"].fillna("Uncategorized").replace("", "Uncategorized") \
               .value_counts().head(8)
        ax.barh(pm.index[::-1], pm.values[::-1], color="#c77dff")
        ax.set_xlabel("Count")
        _style(ax, "Payment Methods")
    elif "receipt_quality" in expense_df.columns:
        qc = expense_df["receipt_quality"].value_counts().reindex(["clear", "blurry", "partial"]).dropna()
        q_col = {"clear": "#3db8a9", "blurry": "#e8b96a", "partial": "#e76f51"}
        ax.bar(qc.index, qc.values, color=[q_col.get(q, "#81b4d8") for q in qc.index])
        ax.set_ylabel("Count")
        _style(ax, "Receipt Quality")
    else:
        _style(ax, "Payment Methods")

    plt.tight_layout(pad=2.5)
    plt.show()

    # Summary stats
    total     = len(expense_results)
    success   = len(expense_df)
    total_items = expense_df["line_items"].apply(lambda x: len(x) if isinstance(x, list) else 0).sum() \
        if "line_items" in expense_df.columns else 0
    avg_items = total_items / success if success > 0 else 0
    violations = int(expense_df["policy_violation"].astype(bool).sum()) \
        if "policy_violation" in expense_df.columns else 0
    avg_amount = pd.to_numeric(expense_df["total_amount"], errors="coerce").mean() \
        if "total_amount" in expense_df.columns else 0
    languages = expense_df["language"].dropna().value_counts().to_dict() \
        if "language" in expense_df.columns else {}

    print("\nExpense Processing Summary")
    print(f"  - Receipts processed  : {success}/{total}")
    print(f"  - Total line items    : {total_items}")
    print(f"  - Avg items/receipt   : {avg_items:.1f}")
    print(f"  - Avg receipt amount  : {avg_amount:,.0f}")
    print(f"  - Policy violations   : {violations}")
    print(f"  - Languages detected  : {languages}")


def encode_image_b64(image, max_side=None):
    """Convert PIL Image to base64 string, optionally resizing.

    Args:
        image:    PIL Image
        max_side: if set, resize so longest side <= max_side (preserves aspect ratio)
    """
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")
    if max_side and max(image.size) > max_side:
        ratio = max_side / max(image.size)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        image = image.resize(new_size, Image.LANCZOS)
    buf = BytesIO()
    image.save(buf, format="JPEG", quality=95)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def plot_mining_analysis(results, timings=None):
    """2×3 dark-mode analysis chart for core document mining results.

    Parameters
    ----------
    results : list[dict]   Raw results list (includes _status / _tokens fields).
    timings : list[float]  Optional per-doc timing list (falls back to _timing in results).
    """
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from collections import Counter

    preds_df = pd.DataFrame([r for r in results
                              if r.get("_status") == "success" or
                              ("_error" not in r and "_status" not in r)])
    if len(preds_df) == 0:
        print("[warn] No successful extractions to analyse")
        return

    if timings is None:
        timings = [r["_timing"] for r in results
                   if "_timing" in r and "_error" not in r]

    DARK_BG  = "#1e293b"
    PANEL_BG = "#334155"
    TEXT_CLR = "#e2e8f0"
    BORDER   = "#475569"
    PALETTE  = ["#7c3aed", "#06b6d4", "#10b981", "#f59e0b",
                "#a78bfa", "#8ecae6", "#2a9d8f", "#f4a261", "#c77dff", "#90e0ef"]

    def _style(ax, title):
        ax.set_facecolor(PANEL_BG)
        ax.tick_params(colors=TEXT_CLR, labelsize=9)
        ax.set_title(title, color=TEXT_CLR, fontsize=11, fontweight="bold", pad=8)
        for sp in ax.spines.values():
            sp.set_edgecolor(BORDER)
        for lbl in ax.get_xticklabels() + ax.get_yticklabels():
            lbl.set_color(TEXT_CLR)
        if ax.get_xlabel():
            ax.xaxis.label.set_color(TEXT_CLR)
        if ax.get_ylabel():
            ax.yaxis.label.set_color(TEXT_CLR)

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.patch.set_facecolor(DARK_BG)
    fig.suptitle("Document Mining · Analysis Overview", color=TEXT_CLR,
                 fontsize=14, fontweight="bold", y=1.01)

    # 1 · Document types
    ax = axes[0, 0]
    if "document_type" in preds_df.columns:
        tc = preds_df["document_type"].value_counts().head(8)
        ax.barh(tc.index[::-1], tc.values[::-1], color=PALETTE[:len(tc)])
        ax.set_xlabel("Count")
    _style(ax, "Document Types")

    # 2 · Domain distribution (pie)
    ax = axes[0, 1]
    if "document_domain" in preds_df.columns:
        dc = preds_df["document_domain"].value_counts()
        _, texts, autos = ax.pie(
            dc.values[:8], labels=dc.index[:8],
            autopct="%1.0f%%", colors=PALETTE, startangle=90,
            textprops={"color": TEXT_CLR, "fontsize": 8},
        )
        for at in autos:
            at.set_color("white"); at.set_fontsize(8)
        ax.set_facecolor(PANEL_BG)
    _style(ax, "Domain Distribution")

    # 3 · Language distribution
    ax = axes[0, 2]
    if "language" in preds_df.columns:
        lc = preds_df["language"].value_counts().head(8)
        ax.bar(lc.index, lc.values, color=PALETTE[:len(lc)])
        ax.set_ylabel("Count")
        ax.tick_params(axis="x", rotation=35)
    _style(ax, "Languages")

    # 4 · Quality distribution
    ax = axes[1, 0]
    if "document_quality" in preds_df.columns:
        qc = preds_df["document_quality"].value_counts().reindex(["high", "medium", "low"]).dropna()
        q_colors = {"high": "#10b981", "medium": "#f59e0b", "low": "#ef4444"}
        bars = ax.bar(qc.index, qc.values, color=[q_colors.get(q, "#81b4d8") for q in qc.index])
        ax.set_ylabel("Count")
        for bar, val in zip(bars, qc.values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15,
                    str(int(val)), ha="center", color=TEXT_CLR, fontsize=10)
    _style(ax, "Quality Distribution")

    # 5 · Top keywords (from document_keywords array)
    ax = axes[1, 1]
    kw_text = ""
    if "document_keywords" in preds_df.columns:
        kw_lists = preds_df["document_keywords"].dropna()
        kw_text = " ".join(
            w for kws in kw_lists if isinstance(kws, list) for w in kws
        ).lower()
    if kw_text:
        stopwords = {"the", "a", "an", "and", "or", "of", "in", "for",
                     "to", "with", "is", "on", "at", "by", "as", "from"}
        word_freq = Counter(
            w for w in kw_text.split() if w not in stopwords and len(w) > 3
        ).most_common(10)
        if word_freq:
            ww, wc = zip(*word_freq)
            ax.barh(list(ww)[::-1], list(wc)[::-1], color="#06b6d4")
            ax.set_xlabel("Frequency")
    _style(ax, "Top Keywords")

    # 6 · Processing time histogram
    ax = axes[1, 2]
    if timings:
        ax.hist(timings, bins=min(15, len(timings)), color="#06b6d4", edgecolor=BORDER)
        ax.set_xlabel("Seconds")
        ax.set_ylabel("Documents")
        _style(ax, "Processing Time")

    plt.tight_layout(pad=2.5)
    plt.show()

    # ── Summary stats ─────────────────────────────────────────────────────────
    total_tokens = sum(r.get("_tokens", 0) for r in results if r.get("_status") == "success")
    avg_time     = float(np.mean(timings)) if timings else 0.0
    most_type    = preds_df["document_type"].value_counts().index[0] if "document_type" in preds_df.columns else "N/A"
    most_domain  = preds_df["document_domain"].value_counts().index[0] if "document_domain" in preds_df.columns else "N/A"
    most_lang    = preds_df["language"].value_counts().index[0] if "language" in preds_df.columns else "N/A"

    print("\nSummary Statistics")
    print(f"  - Total tokens used  : {total_tokens:,}")
    print(f"  - Avg time / doc     : {avg_time:.1f}s")
    print(f"  - Most common type   : {most_type}")
    print(f"  - Most common domain : {most_domain}")
    print(f"  - Primary language   : {most_lang}")
    if "document_quality" in preds_df.columns:
        qd = preds_df["document_quality"].value_counts().to_dict()
        print(f"  - Quality breakdown  : {qd}")




def plot_ham_demographics(ds):
    """HAM10000 demographics: age histogram, sex pie, top body sites."""
    import matplotlib.pyplot as plt
    import matplotlib
    from collections import Counter
    matplotlib.rcParams.update({
        'figure.facecolor': '#0f172a', 'axes.facecolor': '#0f172a',
        'text.color': '#e2e8f0', 'axes.labelcolor': '#e2e8f0',
        'xtick.color': '#94a3b8', 'ytick.color': '#94a3b8',
    })
    ham_ages = [r["age"] for r in ds if r["age"] and r["age"] > 0]
    ham_sexes = Counter(r["sex"] for r in ds if r["sex"])
    ham_locs = Counter(r["localization"] for r in ds if r["localization"])
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    axes[0].hist(ham_ages, bins=20, color='#6366f1', edgecolor='#1e293b')
    axes[0].set_xlabel("Age"); axes[0].set_title("Age Distribution", color='#f1f5f9')
    axes[1].pie([ham_sexes[s] for s in ham_sexes], labels=list(ham_sexes),
                autopct='%1.0f%%', colors=['#6366f1','#ec4899','#94a3b8'][:len(ham_sexes)],
                wedgeprops=dict(edgecolor='#1e293b'))
    axes[1].set_title("Sex Distribution", color='#f1f5f9')
    loc_top = ham_locs.most_common(10)
    axes[2].barh([l for l,_ in loc_top][::-1], [c for _,c in loc_top][::-1],
                 color='#14b8a6', edgecolor='#1e293b')
    axes[2].set_xlabel("Count"); axes[2].set_title("Top 10 Body Sites", color='#f1f5f9')
    fig.suptitle(f"HAM10000 Demographics ({len(ds)} images)", fontsize=15, color='#f1f5f9', y=1.02)
    plt.tight_layout(); plt.show()


def plot_precision_summary(precision_results, class_colors=None, malignancy_map=None):
    """Plot P@5 bar chart by class. Returns average P@5."""
    import matplotlib.pyplot as plt
    import matplotlib
    import pandas as pd
    matplotlib.rcParams.update({
        'figure.facecolor': '#0f172a', 'axes.facecolor': '#0f172a',
        'text.color': '#e2e8f0', 'axes.labelcolor': '#e2e8f0',
        'xtick.color': '#94a3b8', 'ytick.color': '#94a3b8',
    })
    if not precision_results:
        print("No precision results"); return 0.0
    pr_df = pd.DataFrame(precision_results)
    avg_p5 = pr_df["precision_at_5"].mean()
    class_p5 = pr_df.groupby("query_gt")["precision_at_5"].mean().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(9, max(3, len(class_p5) * 0.5 + 1)))
    if class_colors and malignancy_map:
        colors = [class_colors.get(malignancy_map.get(c, ""), "#6366f1") for c in class_p5.index]
    else:
        colors = ["#6366f1"] * len(class_p5)
    bars = ax.barh(class_p5.index, class_p5.values, color=colors, edgecolor='#1e293b', linewidth=1.5)
    ax.set_xlabel("Precision@5"); ax.set_xlim(0, 1.05); ax.grid(axis='x', alpha=0.3)
    ax.set_title(f"Image Retrieval Precision@5 (avg: {avg_p5:.1%})", fontsize=13, color='#f1f5f9', pad=12)
    ax.axvline(x=avg_p5, color='#f1f5f9', linestyle='--', alpha=0.5, label=f'avg={avg_p5:.1%}')
    ax.legend(facecolor='#1e293b', edgecolor='#334155', labelcolor='#e2e8f0')
    for bar, val in zip(bars, class_p5.values):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2, f"{val:.0%}",
                va='center', fontsize=11, color='#94a3b8')
    plt.tight_layout(); plt.show()
    print(f"Average Precision@5: {avg_p5:.1%}")
    return avg_p5
