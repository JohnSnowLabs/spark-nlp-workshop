"""
ECG document loading, extraction, and triage utilities.

Extracted from demo_utils.py — contains all ECG-specific functions for
loading ECGBench data, running cached measurement extraction, and
binary triage on GenECG samples.
"""

from pathlib import Path
import json

import numpy as np
from PIL import Image

from utils.viewers import display_document_analysis

__all__ = [
    "load_ecg_docs",
    "preview_ecg_docs",
    "run_ecg_extraction_cached",
    "load_ecg_model_results",
    "run_ecg_triage_cached",
]


def load_ecg_docs(n=60, ecgbench_dir=None, gt_csv=None):
    """Load ECGBench images + PTB-XL+ 12SL ground truth measurements.

    Returns (images, ids, ecg_ids, classes, gt_data).
    """
    import pandas as pd
    from collections import Counter

    ecgbench_dir = Path(ecgbench_dir) if ecgbench_dir else Path("cache/ecg_samples/ecgbench_extended")
    gt_csv = Path(gt_csv) if gt_csv else Path("cache/ptbxl_plus/12sl_features.csv")

    with open(ecgbench_dir / "meta.json") as f:
        meta = json.load(f)

    images, ids, ecg_ids, classes = [], [], [], []
    for entry in meta[:n]:
        img_path = ecgbench_dir / entry["file"]
        if img_path.exists():
            images.append(Image.open(img_path).convert("RGB"))
            ids.append(entry["id"])
            ecg_ids.append(entry["ecg_id"])
            classes.append(entry["answer"])

    gt_cols = ["ecg_id", "HR__Global", "PR_Int_Global", "QRS_Dur_Global",
               "QT_Int_Global", "QT_IntBazett_Global", "R_AxisFrontal_Global"]
    gt_df = pd.read_csv(gt_csv, usecols=gt_cols)
    gt_lookup = gt_df.set_index("ecg_id")

    gt_data = []
    matched = 0
    for eid in ecg_ids:
        if eid in gt_lookup.index:
            r = gt_lookup.loc[eid]
            gt_data.append({"gt_hr": r["HR__Global"], "gt_pr": r["PR_Int_Global"],
                            "gt_qrs": r["QRS_Dur_Global"], "gt_qt": r["QT_Int_Global"],
                            "gt_qtc": r["QT_IntBazett_Global"], "gt_axis": r["R_AxisFrontal_Global"]})
            matched += 1
        else:
            gt_data.append({})

    print(f"Loaded {len(images)} ECGBench images ({images[0].width}x{images[0].height}px)")
    print(f"   GT match: {matched}/{len(images)} ({100*matched//len(images)}%)")
    print(f"   Classes: {dict(Counter(classes))}")
    return images, ids, ecg_ids, classes, gt_data


def preview_ecg_docs(images, ids, classes, gt_data):
    """Quick preview gallery for ECG docs with GT measurement summary."""
    import pandas as pd

    preview = []
    for eid, cls, gt in zip(ids, classes, gt_data):
        row = {"ecg_id": eid, "class": cls}
        if gt:
            hr = gt.get("gt_hr")
            qrs = gt.get("gt_qrs")
            qt = gt.get("gt_qt")
            axis = gt.get("gt_axis")
            row["HR"] = f"{hr:.0f} bpm" if hr and not pd.isna(hr) else "—"
            row["QRS"] = f"{qrs:.0f} ms" if qrs and not pd.isna(qrs) else "—"
            row["QT"] = f"{qt:.0f} ms" if qt and not pd.isna(qt) else "—"
            row["Axis"] = f"{axis:.0f}°" if axis and not pd.isna(axis) else "—"
        else:
            row.update({"HR": "—", "QRS": "—", "QT": "—", "Axis": "—"})
        preview.append(row)
    display_document_analysis(images, preview, title="ECGBench — 12-Lead ECG Samples with GT Measurements")


def run_ecg_extraction_cached(nb_name, cache_key, use_cache, images, ids, ecg_ids,
                              classes, gt_data, prompt, schema, base_url, model, api_key=None):
    """Run ECG measurement extraction with caching. Returns list of result dicts."""
    from utils.core import infer_image_structured, save_nb_cache, load_nb_cache, has_nb_cache
    from tqdm.notebook import tqdm

    if use_cache and has_nb_cache(nb_name, cache_key):
        cached = load_nb_cache(nb_name, cache_key)
        results = cached["results"]
        n_ok = sum(1 for r in results if r.get("data") is not None)
        print(f"Cached extraction -- {n_ok}/{len(results)} successful")
        return results

    results = []
    for img, bid, eid, gt, cls in tqdm(
        zip(images, ids, ecg_ids, gt_data, classes), total=len(images), desc="Extracting"
    ):
        try:
            r = infer_image_structured(img, prompt, schema, base_url=base_url, model=model, api_key=api_key)
            r.update({"id": bid, "ecg_id": eid, "gt_class": cls, **gt})
            results.append(r)
        except Exception as e:
            results.append({"id": bid, "ecg_id": eid, "gt_class": cls, "error": str(e), "data": None, **gt})

    n_ok = sum(1 for r in results if r.get("data") is not None)
    avg_t = np.mean([r["_timing"] for r in results if "_timing" in r]) if n_ok else 0
    save_nb_cache(nb_name, cache_key, {"results": results})
    print(f"Extraction: {n_ok}/{len(results)} ok | {avg_t:.1f}s/ECG")
    return results


def load_ecg_model_results(nb_name, cache_key, model_names):
    """Load cached results for multiple models. Returns {model: results}."""
    from utils.core import load_nb_cache, has_nb_cache, set_cache_model
    out = {}
    for m in model_names:
        set_cache_model(m)
        if has_nb_cache(nb_name, cache_key):
            cached = load_nb_cache(nb_name, cache_key)
            out[m] = cached["results"]
    return out


def run_ecg_triage_cached(nb_name, cache_key, use_cache, genecg_dir, triage_map,
                          prompt, schema, base_url, model, api_key=None):
    """Run binary triage on GenECG samples with caching."""
    from utils.core import infer_image_structured, save_nb_cache, load_nb_cache, has_nb_cache
    from tqdm.notebook import tqdm

    if use_cache and has_nb_cache(nb_name, cache_key):
        cached = load_nb_cache(nb_name, cache_key)
        results = cached["results"]
        print(f"Cached triage -- {len(results)} samples")
        return results

    with open(Path(genecg_dir) / "meta.json") as f:
        meta = json.load(f)

    results = []
    for entry in tqdm(meta, desc="Triage"):
        img_path = Path(genecg_dir) / entry["file"]
        if not img_path.exists():
            continue
        img = Image.open(img_path).convert("RGB")
        eid = entry["file"].replace(".png", "")
        gt_label = entry["label_name"]
        gt_triage = triage_map[gt_label]
        try:
            r = infer_image_structured(img, prompt, schema, base_url=base_url, model=model, api_key=api_key)
            r.update({"ecg_id": eid, "gt_label": gt_label, "gt_triage": gt_triage})
            results.append(r)
        except Exception as e:
            results.append({"ecg_id": eid, "gt_label": gt_label, "gt_triage": gt_triage, "error": str(e), "data": None})

    save_nb_cache(nb_name, cache_key, {"results": results})
    print(f"Triage: {sum(1 for r in results if r.get('data'))} successful")
    return results


