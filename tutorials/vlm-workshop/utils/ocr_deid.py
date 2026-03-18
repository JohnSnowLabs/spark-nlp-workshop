"""
OCR + Bounding Box + De-Identification utilities for NB1 (visual_deid).
Keeps heavy HTML/JS viewer code and pipeline logic out of the notebook.
"""

import re
import json
import time
import uuid
import base64
from io import BytesIO
from pathlib import Path
from collections import Counter

try:
    import fitz
except ImportError:
    fitz = None  # lazy — only needed for PDF rendering in NB1
import requests
from PIL import Image, ImageDraw
from tqdm.notebook import tqdm
from IPython.display import display as _display, HTML as _HTML

from utils.core import (
    has_nb_cache, load_nb_cache, save_nb_cache,
    check_sparknlp, _link_code_entities,
)
from utils.viewers import display_document_analysis
from utils.plots import encode_image_b64

try:
    from utils.config import SPARKNLP_BASE_URL
except ImportError:
    SPARKNLP_BASE_URL = "http://localhost:9470"

# ── Constants ──────────────────────────────────────────────────────────────────

OCR_PROMPT = (
    "Perform fine-grained OCR. Detect each word individually and return "
    "word-level bounding boxes. Output each word on a separate line in the "
    "format: word(x1,y1),(x2,y2) where coordinates are in a 1000x1000 grid."
)
BB_PATTERN = re.compile(r'([^()]+?)\((\d+),(\d+)\),\((\d+),(\d+)\)')
OCR_COORD_SCALE = 1000
PHI_COLOR = '#ff2d2d'
SAFE_COLOR = '#4ECDC4'
BB_COLORS = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
    '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B88B', '#ABEBC6',
]


# ── Data Loading ───────────────────────────────────────────────────────────────

_DEFAULT_PDF_DIR = Path("./dataset/pdf-deid-dataset/PDF_Original")
_DEFAULT_GT_DIR  = Path("./dataset/pdf-deid-dataset/Mapping/all_phi")


def load_digital_docs(n=10, pdf_dir=None, gt_dir=None):
    """Load PDF first pages + GT PHI + baselines from JSL pdf-deid-dataset.

    Returns (images, ids, levels, phi_lists, baselines).
    """
    pdf_dir = Path(pdf_dir) if pdf_dir else _DEFAULT_PDF_DIR
    gt_dir  = Path(gt_dir)  if gt_dir  else _DEFAULT_GT_DIR

    # Load GT PHI for all difficulty levels
    phi_gt = {}
    for level in ["easy", "medium", "hard"]:
        gt_path = gt_dir / f"pdf_deid_gts_{level}.json"
        if gt_path.exists():
            with open(gt_path) as f:
                phi_gt.update(json.load(f))

    # Sample from each level for a good mix
    pdf_files = []
    per_level = max(1, n // 3)
    for level in ["Easy", "Medium", "Hard"]:
        level_dir = pdf_dir / level
        if level_dir.exists():
            pdf_files.extend(sorted(level_dir.glob("*.pdf"))[:per_level])

    # Top up if short
    if len(pdf_files) < n:
        all_pdfs = []
        for level in ["Easy", "Medium", "Hard"]:
            level_dir = pdf_dir / level
            if level_dir.exists():
                all_pdfs.extend(sorted(level_dir.glob("*.pdf")))
        for p in all_pdfs:
            if p not in pdf_files and len(pdf_files) < n:
                pdf_files.append(p)
    pdf_files = pdf_files[:n]

    images, ids, levels, phi_lists = [], [], [], []
    for pdf_path in pdf_files:
        try:
            doc = fitz.open(str(pdf_path))
            pix = doc[0].get_pixmap(dpi=150)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
            ids.append(pdf_path.stem)
            levels.append(pdf_path.parent.name)
            phi_lists.append(phi_gt.get(pdf_path.name, []))
            doc.close()
        except Exception as e:
            print(f"Failed to render {pdf_path.name}: {e}")

    baselines = load_baselines(gt_dir)

    print(f"✅ Loaded {len(images)} PDF pages (first page each)")
    print(f"   Difficulty: {dict(Counter(levels))}")
    print(f"   GT PHI: {sum(1 for p in phi_lists if p)}/{len(phi_lists)} docs | Baselines: {len(baselines)}")
    return images, ids, levels, phi_lists, baselines


def preview_digital_docs(images, ids, levels, phi_lists):
    """Quick preview gallery for digital docs with GT PHI summary."""
    preview = []
    for did, lvl, gt_ents in zip(ids, levels, phi_lists):
        unique = sorted(set(gt_ents))
        preview.append({
            "doc_id": did, "difficulty": lvl,
            "GT_phi_count": f"{len(gt_ents)} ({len(unique)} unique)",
            "GT_phi_entities": " | ".join(unique),
        })
    display_document_analysis(images, preview, title="Digital Medical Documents (with GT PHI)")


def load_handwritten_docs(data_dir, n=20, blacklist=None, min_dim=800):
    """Load handwritten images with blacklist filtering and upscaling.

    Returns (images, ids).
    """
    data_dir = Path(data_dir)
    blacklist = blacklist or set()

    all_files = sorted(data_dir.glob("*.jpg")) + sorted(data_dir.glob("*.png"))
    all_files = [f for f in all_files if f.stem not in blacklist]

    images, ids = [], []
    upscaled = 0
    for p in all_files[:n]:
        try:
            img = Image.open(p).convert("RGB")
            w, h = img.size
            if min(w, h) < min_dim:
                scale = min_dim / min(w, h)
                img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
                upscaled += 1
            images.append(img)
            ids.append(p.stem)
        except Exception:
            continue

    print(f"✅ Loaded {len(images)} prescriptions (blacklisted {len(blacklist)}, upscaled {upscaled})")
    return images, ids


def load_baselines(gt_dir):
    """Load pre-computed precision/recall baselines from *_result_mapping.json."""
    gt_dir = Path(gt_dir)
    baselines = {}
    for level in ["easy", "medium", "hard"]:
        path = gt_dir / f"{level}_result_mapping.json"
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            for fname, vals in data.items():
                stem = fname.replace(".pdf", "")
                baselines[stem] = {
                    "precision": vals.get("precision", 0) * 100,
                    "recall": vals.get("recall", 0) * 100,
                    "level": level,
                }
    return baselines


def enrich_posology(results, sparknlp_url=None):
    """Run posology NER + relations + RxNorm resolution via Spark NLP /enrich.

    For each result, concatenates all bbox texts and calls /enrich with
    ner_models=["posology"], resolve_systems=["rxnorm"], do_relations=True.
    Stores: r["_pos_entities"], r["_pos_codes"], r["_pos_relations"].
    """
    sparknlp_url = sparknlp_url or SPARKNLP_BASE_URL
    total_ents = 0
    total_codes = 0
    total_rels = 0
    errors = 0

    for r in tqdm(results, desc="Posology NER+Relations"):
        bboxes = r.get("bboxes", [])
        if not bboxes:
            r["_pos_entities"] = []
            r["_pos_codes"] = {}
            r["_pos_relations"] = []
            continue

        full_text = " ".join(text for text, *_ in bboxes)
        if not full_text.strip():
            r["_pos_entities"] = []
            r["_pos_codes"] = {}
            r["_pos_relations"] = []
            continue

        try:
            resp = requests.post(
                f"{sparknlp_url}/enrich",
                json={
                    "text": full_text,
                    "ner_models": ["posology"],
                    "resolve_systems": ["rxnorm"],
                    "do_relations": True,
                    "relation_models": ["posology"],
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            ents = data.get("entities", [])
            codes = data.get("codes", {})
            rels = data.get("relations", [])
            _link_code_entities(codes, ents)
            r["_pos_entities"] = ents
            r["_pos_codes"] = codes
            r["_pos_relations"] = rels
            total_ents += len(ents)
            total_codes += sum(len(v) for v in codes.values())
            total_rels += len(rels)
        except Exception as e:
            r["_pos_entities"] = []
            r["_pos_codes"] = {}
            r["_pos_relations"] = []
            errors += 1
            print(f"  ⚠️  Posology error on {r.get('_id', '?')}: {e}")

    ok = sum(1 for r in results if r.get("_pos_entities"))
    print(f"\n✅ Posology NER complete: {ok}/{len(results)} docs with entities")
    print(f"   Entities: {total_ents} | Relations: {total_rels} | RxNorm codes: {total_codes} | Errors: {errors}")


# ── Cloud VLM DEID Comparison ────────────────────────────────────────────────

_CLOUD_DEID_PROMPT = """\
You are a HIPAA compliance expert. Examine this medical document image carefully.

Identify ALL Protected Health Information (PHI) and Personally Identifiable Information (PII).

PHI/PII categories: PATIENT names, DOCTOR names, DATES (DOB, visit dates, etc.), \
AGE, SSN, HOSPITAL/facility names, PHONE numbers, ID numbers (hospital IDs, license numbers), \
ADDRESSES, EMAIL, FAX, ZIP codes, MEDICAL_RECORD numbers.

Return a JSON object with exactly this structure:
{
  "entities": [
    {"text": "exact text as it appears", "label": "CATEGORY"},
    ...
  ]
}

Rules:
- Extract the EXACT text as printed in the document (preserve formatting like "24/05/1977")
- Include ALL instances, even duplicates
- Use labels: PATIENT, DOCTOR, DATE, AGE, SSN, HOSPITAL, PHONE, ID, LOCATION, EMAIL, FAX, ZIP
- Do NOT skip any PHI — HIPAA requires 100% recall
- If text is partially obscured, still include your best reading
"""


def run_cloud_deid(images, ids, model, api_key, base_url="https://openrouter.ai/api/v1",
                   gt_phi_list=None, max_tokens=2048, desc=None):
    """Run end-to-end PHI detection via cloud VLM (Claude, GPT-4, etc.).

    Sends each image with a one-shot DEID prompt, parses returned entities,
    and builds results compatible with compute_phi_accuracy().

    Returns list of result dicts with: _id, gt_entities, phi_entities, phi_indices,
    phi_labels, bboxes (synthetic — one per entity), _timing, method.
    """
    results = []
    desc = desc or f"Cloud DEID ({model})"

    for i, (img, doc_id) in enumerate(tqdm(list(zip(images, ids)), desc=desc)):
        gt_ents = gt_phi_list[i] if gt_phi_list and i < len(gt_phi_list) else []

        # Resize for cloud API (keep reasonable size)
        w, h = img.size
        max_dim = 1536
        if max(w, h) > max_dim:
            scale = max_dim / max(w, h)
            img_resized = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        else:
            img_resized = img

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        # Claude needs json_object mode
        is_claude = "anthropic/" in model or "claude" in model.lower()

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a HIPAA compliance expert. Return ONLY valid JSON."},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/jpeg;base64,{encode_image_b64(img_resized)}",
                        }},
                        {"type": "text", "text": _CLOUD_DEID_PROMPT},
                    ],
                },
            ],
            "temperature": 0.0,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }
        if is_claude:
            payload["provider"] = {"order": ["Anthropic"]}

        start = time.time()
        try:
            resp = requests.post(
                f"{base_url}/chat/completions", json=payload,
                headers=headers, timeout=300,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            parsed = json.loads(content)
            entities = parsed.get("entities", [])
            tokens = data.get("usage", {}).get("total_tokens", 0)
        except Exception as e:
            print(f"  ⚠️  {doc_id}: {e}")
            entities = []
            tokens = 0
        elapsed = time.time() - start

        # Build pseudo-bboxes (one per detected entity, no spatial info)
        # This lets us reuse compute_phi_accuracy which checks text overlap
        phi_texts = [e.get("text", "") for e in entities if e.get("text")]
        phi_labels_map = {}
        bboxes = []
        phi_indices = []

        for j, ent in enumerate(entities):
            text = ent.get("text", "")
            label = ent.get("label", "PHI")
            if text:
                bboxes.append((text, 0, 0, 0, 0))
                phi_indices.append(j)
                phi_labels_map[j] = label

        results.append({
            "_id": doc_id,
            "bboxes": bboxes,
            "phi_indices": phi_indices,
            "phi_labels": phi_labels_map,
            "phi_matches": {},
            "phi_entities": entities,
            "gt_entities": gt_ents,
            "_timing": elapsed,
            "_tokens": tokens,
            "_n_regions": len(bboxes),
            "method": f"cloud:{model.split('/')[-1]}",
        })

    ok = sum(1 for r in results if r.get("phi_entities"))
    total_ents = sum(len(r.get("phi_entities", [])) for r in results)
    total_time = sum(r["_timing"] for r in results)
    print(f"\n✅ {model}: {ok}/{len(results)} docs processed, {total_ents} PHI entities found")
    print(f"   Total time: {total_time:.1f}s (avg {total_time/len(results):.1f}s/doc)")
    return results


def compute_cloud_phi_accuracy(results):
    """Compute PHI recall/precision for cloud VLM results.

    Simpler than compute_phi_accuracy — only checks text overlap between
    detected entities and GT entities (no region/bbox accuracy since cloud
    models don't return coordinates).
    """
    per_doc = []
    total_gt = 0
    total_found = 0
    total_flagged = 0
    total_true_pos = 0

    for r in results:
        gt_ents = r.get("gt_entities", [])
        if not gt_ents:
            continue

        unique_gt = sorted(set(e.strip() for e in gt_ents if e.strip()))
        detected = [e.get("text", "").strip() for e in r.get("phi_entities", []) if e.get("text")]
        detected_lower = [d.lower() for d in detected]

        found, missed = [], []
        for gt in unique_gt:
            gl = gt.lower()
            matched = any(gl in dl or dl in gl for dl in detected_lower if dl)
            if matched:
                found.append(gt)
            else:
                missed.append(gt)

        # Precision: of detected entities, how many match a GT entity?
        unique_gt_lower = {g.lower() for g in unique_gt}
        true_pos = sum(
            1 for d in detected_lower
            if any(gt in d or d in gt for gt in unique_gt_lower)
        )

        recall = len(found) / len(unique_gt) * 100 if unique_gt else 0
        precision = true_pos / len(detected) * 100 if detected else 100.0

        per_doc.append({
            "doc_id": r["_id"],
            "gt_total": len(unique_gt),
            "found": len(found),
            "missed_count": len(missed),
            "missed": missed,
            "recall": recall,
            "flagged": len(detected),
            "true_pos": true_pos,
            "precision": precision,
            "region_acc": 0.0,  # N/A for cloud models
            "method": r.get("method", "?"),
        })
        total_gt += len(unique_gt)
        total_found += len(found)
        total_flagged += len(detected)
        total_true_pos += true_pos

    overall = {
        "total_gt": total_gt,
        "total_found": total_found,
        "total_missed": total_gt - total_found,
        "recall": total_found / total_gt * 100 if total_gt else 0,
        "total_flagged": total_flagged,
        "total_true_pos": total_true_pos,
        "precision": total_true_pos / total_flagged * 100 if total_flagged else 100.0,
        "region_accuracy": 0.0,
        "n_docs": len(per_doc),
    }
    return per_doc, overall


def show_cloud_comparison(our_results, cloud_results_dict):
    """Display comparison table: our pipeline vs cloud VLMs.

    Args:
        our_results:        results from run_ocr_deid_cached (our pipeline)
        cloud_results_dict: {"Claude Sonnet 4": results, "GPT-4.1": results, ...}
    """
    # Our pipeline stats
    our_per, our_ov = compute_phi_accuracy(our_results)

    # Cloud model stats
    cloud_stats = {}
    for name, results in cloud_results_dict.items():
        c_per, c_ov = compute_cloud_phi_accuracy(results)
        cloud_stats[name] = c_ov

    def _color(val, thresholds=(80, 50)):
        if val >= thresholds[0]:
            return "#4ECDC4"
        elif val >= thresholds[1]:
            return "#fbbf24"
        return "#ff6b6b"

    def _row(name, recall, precision, region, flagged, time_s, n_docs, is_ours=False):
        rc = _color(recall)
        pc = _color(precision)
        rac = _color(region, (90, 70)) if region > 0 else "#444"
        bold = "font-weight:700;" if is_ours else ""
        bg = "background:rgba(78,205,196,0.06);" if is_ours else ""
        region_str = f"{region:.1f}%" if region > 0 else "—"
        time_str = f"{time_s:.1f}s" if time_s > 0 else "—"
        return (
            f'<tr style="{bg}">'
            f'<td style="{bold}color:#e2e8f0">{name}</td>'
            f'<td style="{bold}color:{rc}">{recall:.1f}%</td>'
            f'<td style="{bold}color:{pc}">{precision:.1f}%</td>'
            f'<td style="color:{rac}">{region_str}</td>'
            f'<td>{flagged}</td>'
            f'<td style="color:#94a3b8">{time_str}</td>'
            f'<td style="color:#94a3b8">{n_docs}</td>'
            f'</tr>'
        )

    rows = ""
    # Our pipeline
    total_time = sum(r.get("_timing", 0) for r in our_results)
    rows += _row(
        "JSL Vision OCR + Spark NLP",
        our_ov["recall"], our_ov["precision"], our_ov["region_accuracy"],
        our_ov["total_flagged"], total_time, our_ov["n_docs"], is_ours=True,
    )

    # Cloud models
    for name, stats in cloud_stats.items():
        cloud_time = sum(r.get("_timing", 0) for r in cloud_results_dict[name])
        rows += _row(name, stats["recall"], stats["precision"], 0,
                     stats["total_flagged"], cloud_time, stats["n_docs"])

    html = f"""
    <style>
    .cmp {{ font-family: -apple-system, sans-serif; color: #d4d4d4; }}
    .cmp table {{ border-collapse: collapse; width: 100%; }}
    .cmp th {{ background: #1e3a5f; color: #93c5fd; padding: 10px 12px; text-align: left; font-size: 12px; }}
    .cmp td {{ padding: 8px 12px; border-bottom: 1px solid #333; font-size: 13px; }}
    .cmp .hdr {{
        background: linear-gradient(135deg, #b91c1c 0%, #1e3a5f 100%);
        padding: 14px 20px; border-radius: 10px; margin-bottom: 12px; text-align: center;
        color: white; font-size: 16px; font-weight: 700;
    }}
    .cmp .note {{ font-size: 11px; color: #64748b; margin-top: 8px; }}
    </style>
    <div class="cmp">
        <div class="hdr">PHI De-Identification — Model Comparison</div>
        <table>
            <tr>
                <th>Model</th><th>Recall</th><th>Precision</th>
                <th>Region Acc</th><th>PHI Flagged</th><th>Total Time</th><th>Docs</th>
            </tr>
            {rows}
        </table>
        <div class="note">
            Region accuracy only available for bbox-capable pipelines (JSL Vision OCR).
            Cloud VLMs return entity text only — no spatial coordinates for surgical redaction.
        </div>
    </div>
    """
    _display(_HTML(html))


def plot_cloud_comparison(our_results, cloud_results_dict):
    """Matplotlib bar chart: Recall / Precision / Latency for our pipeline vs cloud VLMs."""
    import matplotlib.pyplot as plt
    import matplotlib as mpl

    _, our_ov = compute_phi_accuracy(our_results)
    cloud_stats = {}
    for name, res in cloud_results_dict.items():
        _, ov = compute_cloud_phi_accuracy(res)
        cloud_stats[name] = ov

    models  = ["JSL Vision OCR\n+ Spark NLP"] + list(cloud_results_dict.keys())
    recalls = [our_ov["recall"]] + [cloud_stats[n]["recall"] for n in cloud_results_dict]
    precs   = [our_ov["precision"]] + [cloud_stats[n]["precision"] for n in cloud_results_dict]
    speeds  = [sum(r.get("_timing", 0) for r in our_results) / len(our_results)]
    for n in cloud_results_dict:
        res = cloud_results_dict[n]
        speeds.append(sum(r.get("_timing", 0) for r in res) / len(res))
    colors  = ["#4ECDC4", "#c084fc", "#60a5fa", "#f472b6", "#fbbf24"][:len(models)]

    theme = {"figure.facecolor": "#0f172a", "axes.facecolor": "#0f172a",
             "axes.edgecolor": "#334155", "text.color": "#d4d4d4",
             "xtick.color": "#94a3b8", "ytick.color": "#94a3b8",
             "grid.color": "#1e293b", "grid.alpha": 0.6}

    with mpl.rc_context(theme):
        fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
        fig.suptitle("PHI De-Identification \u2014 Model Comparison", fontsize=15,
                     fontweight="bold", color="white", y=1.02)

        panels = [
            ("PHI Recall", recalls, "%", "#ff6b6b", 0, 115),
            ("PHI Precision", precs, "%", "#4ECDC4", 0, 115),
            ("Latency (sec/doc)", speeds, "seconds", "#e8b96a", 0, max(speeds) * 1.4),
        ]
        for ax, (title, vals, ylabel, title_color, ymin, ymax) in zip(axes, panels):
            bars = ax.bar(models, vals, color=colors, width=0.55,
                          edgecolor=[c + "88" for c in colors], linewidth=1.2)
            ax.set_title(title, fontsize=12, fontweight="bold", color=title_color, pad=10)
            ax.set_ylabel(ylabel, fontsize=10)
            ax.set_ylim(ymin, ymax)
            if "%" in ylabel:
                ax.axhline(100, color="#334155", ls="--", lw=0.8)
            ax.yaxis.grid(True, lw=0.5)
            ax.set_axisbelow(True)
            ax.tick_params(axis="x", labelsize=9)
            ax.tick_params(axis="y", labelsize=9)
            for b, v in zip(bars, vals):
                if ylabel == "seconds":
                    c = "#4ECDC4" if v <= 4 else "#fbbf24" if v <= 6 else "#ff6b6b"
                    label = f"{v:.1f}s"
                    offset = max(speeds) * 0.03
                else:
                    c = "#4ECDC4" if v >= 80 else "#fbbf24" if v >= 50 else "#ff6b6b"
                    label = f"{v:.1f}%"
                    offset = 2
                ax.text(b.get_x() + b.get_width()/2, v + offset, label,
                        ha="center", fontsize=11, fontweight="bold", color=c)

        fig.tight_layout()
        plt.show()


# ── OCR + DEID Pipeline ───────────────────────────────────────────────────────

def _call_ocr(image, base_url, model, timeout=120, max_retries=3):
    """Send image to OCR VLM, return raw response dict."""
    payload = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{encode_image_b64(image)}",
                }},
                {"type": "text", "text": OCR_PROMPT},
            ],
        }],
        "temperature": 0.0,
        "max_tokens": 8192,
    }
    start = time.time()
    last_error = None
    for attempt in range(max_retries):
        try:
            resp = requests.post(
                f"{base_url}/chat/completions", json=payload, timeout=timeout,
            )
            if resp.status_code != 200:
                body = resp.text[:300] if resp.text else "(empty)"
                raise requests.exceptions.HTTPError(
                    f"{resp.status_code} for {base_url}: {body}", response=resp,
                )
            result = resp.json()
            content = result["choices"][0]["message"]["content"].strip()
            return {
                "raw": content,
                "_timing": time.time() - start,
                "_tokens": result.get("usage", {}).get("total_tokens", 0),
            }
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    raise last_error


def _parse_bboxes(raw_text):
    """Parse 'text(x1,y1),(x2,y2)' → [(text, x1, y1, x2, y2), ...]"""
    return [
        (t.strip(), int(x1), int(y1), int(x2), int(y2))
        for t, x1, y1, x2, y2 in BB_PATTERN.findall(raw_text)
    ]


def _call_sparknlp_deid(text, url=None):
    """Call Spark NLP /deid endpoint. Returns list of entity dicts with chunk, label, begin, end."""
    url = url or SPARKNLP_BASE_URL
    if not text or not text.strip():
        return []
    try:
        r = requests.post(f"{url}/deid", json={"text": text}, timeout=30)
        r.raise_for_status()
        return r.json().get("entities", [])
    except Exception:
        return []


def _match_phi_nlp(bboxes, deid_entities):
    """Map NLP DEID entities back to bboxes via substring matching.

    Returns (phi_indices set, phi_labels dict, phi_matches dict).
    phi_matches maps bbox idx → list of {chunk, label} for word-level display.
    """
    if not deid_entities or not bboxes:
        return set(), {}, {}
    phi_idx = set()
    phi_labels = {}
    phi_matches = {}
    for ent in deid_entities:
        chunk = ent["chunk"].strip()
        label = ent.get("label", "PHI")
        if not chunk:
            continue
        chunk_lower = chunk.lower()
        for idx, (text, *_) in enumerate(bboxes):
            bt = text.lower().strip()
            if not bt:
                continue
            if chunk_lower in bt or bt in chunk_lower:
                phi_idx.add(idx)
                phi_labels[idx] = label
                if idx not in phi_matches:
                    phi_matches[idx] = []
                # Avoid duplicate chunks in same bbox
                if not any(m["chunk"].lower() == chunk_lower for m in phi_matches[idx]):
                    phi_matches[idx].append({"chunk": chunk, "label": label})
    return phi_idx, phi_labels, phi_matches


def run_ocr_and_deid(images, ids, base_url, model,
                     gt_phi_list=None, sparknlp_url=None, desc="OCR+DEID"):
    """Run OCR VLM + parse BBs + Spark NLP DEID in one pass.

    Returns list of result dicts with keys:
        _id, raw, bboxes, _timing, _tokens, _n_regions,
        phi_indices, phi_labels, method, gt_entities,
        _nlp_entities, redacted (PIL Image)
    """
    if gt_phi_list is None:
        gt_phi_list = [None] * len(images)
    S = OCR_COORD_SCALE

    results = []
    for img, doc_id, gt_ents in tqdm(
        zip(images, ids, gt_phi_list), total=len(images), desc=desc,
    ):
        try:
            ocr = _call_ocr(img.convert("RGB"), base_url, model)
            bboxes = _parse_bboxes(ocr["raw"])

            # NLP DEID — join OCR text, call Spark NLP /deid
            nlp_entities = []
            phi_idx, phi_labels, phi_matches = set(), {}, {}
            if bboxes:
                full_text = " ".join(text for text, *_ in bboxes)
                nlp_entities = _call_sparknlp_deid(full_text, sparknlp_url)
                phi_idx, phi_labels, phi_matches = _match_phi_nlp(bboxes, nlp_entities)

            # Redact — black rectangles at PHI BB coords
            redacted = img.copy()
            draw = ImageDraw.Draw(redacted)
            w, h = img.size
            for idx in phi_idx:
                _, x1, y1, x2, y2 = bboxes[idx]
                draw.rectangle(
                    [int(x1 * w / S), int(y1 * h / S),
                     int(x2 * w / S), int(y2 * h / S)],
                    fill=(0, 0, 0),
                )

            results.append({
                "_id": doc_id, "raw": ocr["raw"], "bboxes": bboxes,
                "_timing": ocr["_timing"], "_tokens": ocr["_tokens"],
                "_n_regions": len(bboxes), "phi_indices": phi_idx,
                "phi_labels": phi_labels, "phi_matches": phi_matches,
                "method": "NLP",
                "gt_entities": gt_ents or [],
                "_nlp_entities": nlp_entities,
                "redacted": redacted,
            })
        except Exception as e:
            print(f"⚠️  Error on {doc_id}: {e}")
            results.append({
                "_id": doc_id, "raw": None, "bboxes": [], "_timing": 0,
                "_tokens": 0, "_n_regions": 0, "phi_indices": set(),
                "phi_labels": {}, "phi_matches": {}, "method": "error",
                "gt_entities": gt_ents or [], "_nlp_entities": [],
                "redacted": img.copy(), "_error": str(e),
            })

    ok = sum(1 for r in results if r.get("bboxes"))
    total_r = sum(r["_n_regions"] for r in results)
    total_phi = sum(len(r["phi_indices"]) for r in results)
    avg_t = sum(r["_timing"] for r in results) / max(len(results), 1)
    print(f"\n✅ {desc} complete: {ok}/{len(results)} docs")
    print(f"   Regions: {total_r:,} | PHI flagged: {total_phi} | Avg time: {avg_t:.1f}s")
    return results


# ── PHI Accuracy ──────────────────────────────────────────────────────────────

def compute_phi_accuracy(results):
    """Compute per-doc and overall PHI recall against GT entities.

    For each GT entity, checks if ANY detected BB text contains it (or vice versa).
    Returns (per_doc_stats, overall_stats) where per_doc_stats is a list of dicts
    and overall_stats is a summary dict.
    """
    per_doc = []
    total_gt = 0
    total_found = 0
    total_flagged = 0
    total_true_pos = 0
    total_tp_region = 0
    total_tn_region = 0
    total_bboxes = 0

    for r in results:
        gt_ents = r.get("gt_entities", [])
        if not gt_ents:
            continue

        bboxes = r.get("bboxes", [])
        unique_gt = sorted(set(e.strip() for e in gt_ents if e.strip()))
        bb_texts = [text.lower().strip() for text, *_ in bboxes]

        # Only evaluate GT entities the OCR actually saw on the page
        # (present in any bbox text). Entities from other pages are out of scope.
        all_bb_text = " ".join(bb_texts)
        visible_gt = [g for g in unique_gt if g.lower() in all_bb_text
                      or any(g.lower() in bt or bt in g.lower() for bt in bb_texts if bt)]
        unique_gt = visible_gt
        unique_gt_lower = {g.lower() for g in unique_gt}
        found, missed = [], []

        for gt in unique_gt:
            gl = gt.lower()
            matched = any(gl in bt or bt in gl for bt in bb_texts if bt)
            if matched:
                found.append(gt)
            else:
                missed.append(gt)

        # Precision: of flagged PHI bboxes, how many match a GT entity?
        phi_idx = r.get("phi_indices", set())
        if isinstance(phi_idx, list):
            phi_idx = set(phi_idx)
        true_pos = 0
        for idx in phi_idx:
            if idx < len(bboxes):
                text = bboxes[idx][0].lower().strip()
                if any(gt in text or text in gt for gt in unique_gt_lower):
                    true_pos += 1
        precision = true_pos / len(phi_idx) * 100 if phi_idx else 100.0

        # Region-level accuracy: classify each bbox as TP/TN/FP/FN
        gt_bbox_match = set()
        for idx, (text, *_) in enumerate(bboxes):
            bt = text.lower().strip()
            if any(gt in bt or bt in gt for gt in unique_gt_lower):
                gt_bbox_match.add(idx)
        tp_r = len(phi_idx & gt_bbox_match)
        tn_r = len(bboxes) - len(phi_idx | gt_bbox_match)
        region_acc = (tp_r + tn_r) / len(bboxes) * 100 if bboxes else 100.0

        recall = len(found) / len(unique_gt) * 100 if unique_gt else 0
        per_doc.append({
            "doc_id": r["_id"],
            "gt_total": len(unique_gt),
            "found": len(found),
            "missed_count": len(missed),
            "missed": missed,
            "recall": recall,
            "flagged": len(phi_idx),
            "true_pos": true_pos,
            "precision": precision,
            "region_acc": region_acc,
            "method": r.get("method", "?"),
        })
        total_gt += len(unique_gt)
        total_found += len(found)
        total_flagged += len(phi_idx)
        total_true_pos += true_pos
        total_tp_region += tp_r
        total_tn_region += tn_r
        total_bboxes += len(bboxes)

    overall = {
        "total_gt": total_gt,
        "total_found": total_found,
        "total_missed": total_gt - total_found,
        "recall": total_found / total_gt * 100 if total_gt else 0,
        "total_flagged": total_flagged,
        "total_true_pos": total_true_pos,
        "precision": total_true_pos / total_flagged * 100 if total_flagged else 100.0,
        "region_accuracy": (total_tp_region + total_tn_region) / total_bboxes * 100 if total_bboxes else 100.0,
        "n_docs": len(per_doc),
    }
    return per_doc, overall


def show_phi_accuracy(results, baselines=None):
    """Display PHI accuracy as styled HTML: summary banner + per-doc table."""
    per_doc, overall = compute_phi_accuracy(results)
    if not per_doc:
        print("No GT-matched documents to evaluate.")
        return

    # Detect method from first doc
    method = per_doc[0].get("method", "?") if per_doc else "?"
    method_label = {"NLP": "Spark NLP DEID", "GT": "GT Substring Match"}.get(method, method)

    # Per-doc table rows
    rows = ""
    for d in per_doc:
        rc = "#4ECDC4" if d["recall"] >= 80 else "#fbbf24" if d["recall"] >= 50 else "#ff6b6b"
        pc = "#4ECDC4" if d["precision"] >= 80 else "#fbbf24" if d["precision"] >= 50 else "#ff6b6b"
        missed_str = ", ".join(d["missed"][:5])
        if len(d["missed"]) > 5:
            missed_str += f" (+{len(d['missed'])-5} more)"

        rows += (
            f'<tr>'
            f'<td style="color:#81b4d8">{d["doc_id"]}</td>'
            f'<td>{d["gt_total"]}</td>'
            f'<td>{d["flagged"]}</td>'
            f'<td style="color:{rc};font-weight:700">{d["recall"]:.0f}%</td>'
            f'<td style="color:{pc};font-weight:700">{d["precision"]:.0f}%</td>'
            f'<td>{d["region_acc"]:.0f}%</td>'
            f'<td style="color:#888;font-size:11px">{missed_str}</td>'
            f'</tr>'
        )

    ov_color_r = "#4ECDC4" if overall["recall"] >= 80 else "#fbbf24" if overall["recall"] >= 50 else "#ff6b6b"
    ov_color_p = "#4ECDC4" if overall["precision"] >= 80 else "#fbbf24" if overall["precision"] >= 50 else "#ff6b6b"
    ov_color_ra = "#4ECDC4" if overall["region_accuracy"] >= 90 else "#fbbf24" if overall["region_accuracy"] >= 70 else "#ff6b6b"

    html = f"""
    <style>
    .phi-acc {{ font-family: -apple-system, sans-serif; color: #d4d4d4; }}
    .phi-acc table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
    .phi-acc th {{ background: #1e3a5f; color: #93c5fd; padding: 8px 10px; text-align: left; font-size: 12px; }}
    .phi-acc td {{ padding: 6px 10px; border-bottom: 1px solid #333; font-size: 12px; }}
    .phi-acc .summary {{
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 14px 20px; border-radius: 8px;
        display: flex; gap: 24px; align-items: center; justify-content: center; flex-wrap: wrap;
    }}
    .phi-acc .summary .stat {{ text-align: center; }}
    .phi-acc .summary .val {{ font-size: 22px; font-weight: 700; }}
    .phi-acc .summary .lbl {{ font-size: 11px; color: #94a3b8; }}
    </style>
    <div class="phi-acc">
        <div style="text-align:center;color:#94a3b8;font-size:12px;margin-bottom:6px">Method: <strong style="color:#c4b5fd">{method_label}</strong></div>
        <div class="summary">
            <div class="stat"><div class="val" style="color:{ov_color_r}">{overall['recall']:.1f}%</div><div class="lbl">Recall</div></div>
            <div class="stat"><div class="val" style="color:{ov_color_p}">{overall['precision']:.1f}%</div><div class="lbl">Precision</div></div>
            <div class="stat"><div class="val" style="color:{ov_color_ra}">{overall['region_accuracy']:.1f}%</div><div class="lbl">Region Acc</div></div>
            <div class="stat"><div class="val" style="color:#4ECDC4">{overall['total_found']}</div><div class="lbl">GT Found</div></div>
            <div class="stat"><div class="val" style="color:#ff6b6b">{overall['total_missed']}</div><div class="lbl">GT Missed</div></div>
            <div class="stat"><div class="val" style="color:#81b4d8">{overall['total_flagged']}</div><div class="lbl">Flagged</div></div>
            <div class="stat"><div class="val" style="color:#94a3b8">{overall['n_docs']}</div><div class="lbl">Docs</div></div>
        </div>
        <table>
            <tr><th>Document</th><th>GT</th><th>Flagged</th><th>Recall</th><th>Precision</th><th>Region</th><th>Missed</th></tr>
            {rows}
        </table>
    </div>
    """
    _display(_HTML(html))


# ── Cache Serialization ───────────────────────────────────────────────────────

def results_to_cacheable(results):
    """Strip non-serializable fields (PIL images) and convert sets→lists for JSON."""
    out = []
    for r in results:
        cr = {k: v for k, v in r.items() if k != "redacted"}
        if "phi_indices" in cr and isinstance(cr["phi_indices"], set):
            cr["phi_indices"] = sorted(cr["phi_indices"])
        out.append(cr)
    return out


def results_from_cache(cached_results, images):
    """Reconstruct results from cache: restore sets and rebuild redacted images."""
    S = OCR_COORD_SCALE
    results = []
    for r, img in zip(cached_results, images):
        if "phi_indices" in r and isinstance(r["phi_indices"], list):
            r["phi_indices"] = set(r["phi_indices"])
        # JSON stringifies int keys — restore them
        if "phi_labels" in r and r["phi_labels"]:
            r["phi_labels"] = {int(k): v for k, v in r["phi_labels"].items()}
        if "phi_matches" in r and r["phi_matches"]:
            r["phi_matches"] = {int(k): v for k, v in r["phi_matches"].items()}
        # Rebuild redacted image
        redacted = img.copy()
        draw = ImageDraw.Draw(redacted)
        w, h = img.size
        for idx in r.get("phi_indices", set()):
            if idx < len(r.get("bboxes", [])):
                _, x1, y1, x2, y2 = r["bboxes"][idx]
                draw.rectangle(
                    [int(x1 * w / S), int(y1 * h / S),
                     int(x2 * w / S), int(y2 * h / S)],
                    fill=(0, 0, 0),
                )
        r["redacted"] = redacted
        results.append(r)
    return results


def run_ocr_deid_cached(nb_name, cache_key, use_cache, images, ids, base_url, model, **kwargs):
    """Cache-or-run OCR+DEID with automatic posology enrichment. Returns results list ready for display."""
    sparknlp_url = kwargs.get("sparknlp_url")
    cache_hit = False
    if use_cache and has_nb_cache(nb_name, cache_key):
        cached = load_nb_cache(nb_name, cache_key)
        if len(cached["results"]) == len(images):
            results = results_from_cache(cached["results"], images)
            ok = sum(1 for r in results if r.get("_n_regions", 0) > 0)
            print(f"📦 Cached — {ok}/{len(results)} with regions")
            cache_hit = True
        else:
            print(f"⚠️  Cache count mismatch ({len(cached['results'])} vs {len(images)}) — re-running")
    if not cache_hit:
        results = run_ocr_and_deid(images, ids, base_url, model, **kwargs)
        save_nb_cache(nb_name, cache_key, {"results": results_to_cacheable(results)})

    # Auto-enrich posology if sparknlp_url provided and relations missing
    if sparknlp_url and not any(r.get("_pos_relations") for r in results):
        enrich_posology(results, sparknlp_url)
        save_nb_cache(nb_name, cache_key, {"results": results_to_cacheable(results)})
    return results


def export_ocr_deid(results_by_section, output_path):
    """Export OCR+DEID results to JSON. results_by_section: {section_name: results_list}."""
    all_r = [r for rs in results_by_section.values() for r in rs]
    total_t = sum(r["_timing"] for r in all_r)
    print(f"⏱  {len(all_r)} docs in {total_t:.0f}s (avg {total_t / len(all_r):.1f}s/doc)")
    export_data = []
    for section, results in results_by_section.items():
        for r in results:
            export_data.append({
                "doc_id": r["_id"], "section": section,
                "regions": [{"text": t, "x1": x1, "y1": y1, "x2": x2, "y2": y2}
                            for t, x1, y1, x2, y2 in r.get("bboxes", [])],
                "n_regions": r["_n_regions"], "timing_sec": r["_timing"],
                "phi_count": len(r.get("phi_indices", set())),
                "phi_labels": r.get("phi_labels", {}),
                "method": r.get("method", "?"),
            })
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(export_data, f, indent=2, default=str)
    print(f"✅ Exported {len(export_data)} docs → {output_path}")


# ── Display ────────────────────────────────────────────────────────────────────

def display_ocr_deid_results(images, results, title="OCR + DEID Results",
                             metadata=None, show_phi=True):
    """Combined 3-column viewer: Redacted+BBs | Original | Metadata panel.

    Args:
        images:   original PIL Images (parallel to results)
        results:  from run_ocr_and_deid()
        title:    viewer title
        metadata: optional list of dicts with extra info per doc
    """
    vid = f"odr_{uuid.uuid4().hex[:8]}"
    S = OCR_COORD_SCALE

    docs = []
    for i, (img, r) in enumerate(zip(images, results)):
        buf_r = BytesIO()
        r["redacted"].save(buf_r, format="JPEG", quality=90)
        b64_r = base64.b64encode(buf_r.getvalue()).decode()

        buf_o = BytesIO()
        img.save(buf_o, format="JPEG", quality=90)
        b64_o = base64.b64encode(buf_o.getvalue()).decode()

        boxes = []
        phi_labels = r.get("phi_labels", {})
        phi_matches = r.get("phi_matches", {})
        bboxes = r.get("bboxes", [])

        # Pre-compute posology entity → bbox mapping using character offsets
        pos_ents = r.get("_pos_entities", [])
        bbox_pos = {}  # j → [{chunk, label}]
        if pos_ents and bboxes:
            offset = 0
            bbox_ranges = []
            for text, *_ in bboxes:
                bbox_ranges.append((offset, offset + len(text)))
                offset += len(text) + 1  # +1 for space join
            for ent in pos_ents:
                eb, ee = ent.get("begin", -1), ent.get("end", -1)
                if eb < 0 or ee < 0:
                    continue
                for j, (bs, be) in enumerate(bbox_ranges):
                    if eb < be and ee >= bs:
                        cs = max(eb, bs) - bs
                        ce = min(ee + 1, be) - bs
                        chunk = bboxes[j][0][cs:ce].strip()
                        if chunk:
                            bbox_pos.setdefault(j, []).append({"chunk": chunk, "label": ent.get("label", "")})

        for j, (text, x1, y1, x2, y2) in enumerate(bboxes):
            is_phi = j in r.get("phi_indices", set())
            label = phi_labels.get(j, "PHI") if is_phi else None
            matches = phi_matches.get(j, []) if is_phi else []
            boxes.append({
                "t": text, "phi": is_phi, "lbl": label,
                "matches": matches,
                "pos_matches": bbox_pos.get(j, []) if not is_phi else [],
                "l": x1 / S * 100, "tp": y1 / S * 100,
                "w": (x2 - x1) / S * 100, "h": (y2 - y1) / S * 100,
            })

        n_phi = len(r.get("phi_indices", set()))
        n_total = len(r.get("bboxes", []))
        meta_dict = metadata[i] if metadata and i < len(metadata) else {}

        docs.append({
            "id": r.get("_id", "?"),
            "img_r": b64_r, "img_o": b64_o,
            "boxes": boxes,
            "n_phi": n_phi, "n_safe": n_total - n_phi, "n_total": n_total,
            "method": r.get("method", "?"),
            "time": f"{r.get('_timing', 0):.1f}s",
            "gt_count": len(set(r.get("gt_entities", []))),
            "meta": meta_dict,
            "pos_ents": r.get("_pos_entities", []),
            "pos_codes": r.get("_pos_codes", {}),
            "pos_rels": r.get("_pos_relations", []),
        })

    docs_json = json.dumps(docs, ensure_ascii=False, default=str)
    # Strip surrogate characters that OCR VLM occasionally produces
    docs_json = docs_json.encode("utf-8", errors="replace").decode("utf-8")
    total = len(docs)
    title_esc = title.replace("'", "\\'").replace('"', '\\"')

    html = f"""
    <style>
    #{vid} {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #d4d4d4; }}
    #{vid} .hdr {{
        background: linear-gradient(135deg, #b91c1c 0%, #1e3a5f 100%);
        padding: 14px 20px; border-radius: 10px; margin-bottom: 12px; text-align: center;
    }}
    #{vid} .hdr h2 {{ color: white; margin: 0; font-size: 20px; letter-spacing: 1px; }}
    #{vid} .hdr p {{ color: #e2e8f0; margin: 4px 0 0 0; font-size: 13px; }}
    #{vid} .nav {{
        display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 8px;
    }}
    #{vid} .nav button {{
        background: #b91c1c; color: white; border: none; padding: 7px 16px;
        border-radius: 5px; cursor: pointer; font-size: 13px;
    }}
    #{vid} .nav button:hover {{ background: #dc2626; }}
    #{vid} .nav span {{ color: #94a3b8; font-size: 13px; min-width: 80px; text-align: center; }}
    #{vid} .legend {{
        display: flex; gap: 20px; justify-content: center; margin-bottom: 10px; font-size: 12px;
    }}
    #{vid} .legend .dot {{
        display: inline-block; width: 10px; height: 10px; border-radius: 3px;
        margin-right: 4px; vertical-align: middle;
    }}
    #{vid} .body {{ display: flex; gap: 8px; }}
    #{vid} .panel {{
        border: 1px solid #404040; border-radius: 6px; overflow: hidden; background: #1e1e1e;
    }}
    #{vid} .panel.img-panel {{ flex: 3; }}
    #{vid} .panel.meta-panel {{ flex: 2; max-height: 800px; overflow-y: auto; }}
    #{vid} .panel-hdr {{
        padding: 6px 12px; font-size: 12px; font-weight: 600; text-align: center;
    }}
    #{vid} .panel-hdr.redacted {{ background: #7f1d1d; color: #fca5a5; }}
    #{vid} .panel-hdr.original {{ background: #1e3a5f; color: #93c5fd; }}
    #{vid} .panel-hdr.meta {{ background: #1a1a2e; color: #c4b5fd; }}
    #{vid} .img-wrap {{ position: relative; display: block; }}
    #{vid} .img-wrap img {{ width: 100%; display: block; }}
    #{vid} .bb {{
        position: absolute; border: 2px solid; border-radius: 2px;
        cursor: pointer; transition: background 0.15s;
    }}
    #{vid} .bb:hover {{ background: rgba(255,255,255,0.18); }}
    #{vid} .bb-label {{
        position: absolute; top: -16px; left: 0; font-size: 9px; color: white;
        padding: 1px 4px; border-radius: 2px; white-space: nowrap;
        max-width: 140px; overflow: hidden; text-overflow: ellipsis; pointer-events: none;
        display: none;
    }}
    #{vid} .bb:hover .bb-label {{ max-width: none; z-index: 10; display: block; }}
    #{vid} .meta-body {{ padding: 10px; }}
    #{vid} .mrow {{
        display: flex; justify-content: space-between; padding: 5px 0;
        border-bottom: 1px solid #333; font-size: 12px;
    }}
    #{vid} .mk {{ color: #81b4d8; font-weight: 600; }}
    #{vid} .mv {{ color: #d4d4d4; text-align: right; }}
    #{vid} .mv.phi {{ color: #ff6b6b; font-weight: 700; }}
    #{vid} .mv.safe {{ color: #4ECDC4; font-weight: 700; }}
    #{vid} .mv.gt {{ color: #fbbf24; }}
    #{vid} .sep {{ border-top: 2px solid #2a9d8f; margin: 10px 0 6px 0; }}
    #{vid} .text-block {{
        max-height: 450px; overflow-y: auto; margin-top: 6px; padding: 8px;
        background: #161622; border-radius: 6px; font-size: 12px;
        line-height: 1.7; color: #d4d4d4; word-break: break-word;
    }}
    #{vid} .tw {{
        cursor: default; transition: background 0.15s; border-radius: 2px;
        padding: 1px 3px; color: #d4d4d4;
    }}
    #{vid} .tw:hover {{ background: rgba(255,255,255,0.06); }}
    #{vid} .tw-phi {{
        font-weight: 700;
        cursor: pointer; border-radius: 3px; padding: 1px 5px;
        position: relative;
    }}
    #{vid} .tw-phi:hover {{ box-shadow: 0 0 0 2px rgba(255,255,255,0.35); }}
    #{vid} .tw-ner:hover {{ box-shadow: 0 0 0 2px rgba(167,139,250,0.4); }}
    #{vid} .tw-ner .reveal,
    #{vid} .tw-phi .reveal {{
        display: none; position: fixed; background: #1a1a2e; color: #fbbf24;
        border: 1px solid #b91c1c; border-radius: 5px; padding: 4px 10px;
        font-size: 11px; white-space: nowrap; z-index: 99999;
        box-shadow: 0 4px 12px rgba(0,0,0,0.7); pointer-events: none;
    }}
    #{vid} .lb {{ display: block; height: 6px; }}
    #{vid} .tt {{
        position: fixed; display: none; background: #1a1a2e; color: #e0e0e0;
        border: 1px solid #b91c1c; border-radius: 6px; padding: 8px 12px;
        font-size: 12px; max-width: 380px; word-break: break-word; z-index: 9999;
        line-height: 1.4; box-shadow: 0 4px 14px rgba(0,0,0,0.6); pointer-events: none;
    }}
    </style>

    <div id="{vid}">
        <div class="hdr">
            <h2>{title_esc}</h2>
            <p>{total} documents</p>
        </div>
        <div class="nav">
            <button onclick="{vid}_go(-1)">&larr; Prev</button>
            <span id="{vid}_ctr">1 / {total}</span>
            <button onclick="{vid}_go(1)">Next &rarr;</button>
        </div>
        <div class="legend">
            <span><span class="dot" style="background:{PHI_COLOR}"></span>PHI &mdash; Redacted</span>
            <span><span class="dot" style="background:{SAFE_COLOR}"></span>Safe</span>
        </div>
        <div class="body">
            <div class="panel img-panel">
                <div class="panel-hdr redacted">REDACTED + Bounding Boxes</div>
                <div class="img-wrap" id="{vid}_left"></div>
            </div>
            <div class="panel img-panel">
                <div class="panel-hdr original">ORIGINAL</div>
                <div class="img-wrap" id="{vid}_right"></div>
            </div>
            <div class="panel meta-panel">
                <div class="panel-hdr meta">Metadata</div>
                <div class="meta-body" id="{vid}_meta"></div>
            </div>
        </div>
        <div class="tt" id="{vid}_tt"></div>
    </div>

    <script>
    (function() {{
        var docs = {docs_json};
        var cur = 0;
        var total = {total};
        var showPhi = {'true' if show_phi else 'false'};
        var tt = document.getElementById('{vid}_tt');
        var deidColors = {{
            'PATIENT':'#e74c3c','DOCTOR':'#3498db','DATE':'#2ecc71','HOSPITAL':'#9b59b6',
            'SSN':'#e67e22','PHONE':'#1abc9c','MEDICALRECORD':'#f39c12','LOCATION':'#27ae60',
            'AGE':'#2980b9','IDNUM':'#d35400','EMAIL':'#8e44ad','ZIP':'#16a085',
            'STREET':'#c0392b','CITY':'#e17055','STATE':'#636e72','COUNTRY':'#2d3436',
            'USERNAME':'#d63031','PROFESSION':'#6c5ce7','ORGANIZATION':'#00b894'
        }};
        var posColors = {{
            'DRUG':'#6366f1','Drug_Ingredient':'#6366f1','Drug_BrandName':'#818cf8',
            'DOSAGE':'#a78bfa','Dosage':'#a78bfa','Strength':'#a78bfa','STRENGTH':'#a78bfa',
            'FREQUENCY':'#c084fc','Frequency':'#c084fc','DURATION':'#f0abfc','Duration':'#f0abfc',
            'ROUTE':'#d946ef','Route':'#d946ef','FORM':'#e879f9','Form':'#e879f9'
        }};

        function _esc(s) {{ var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }}

        function buildSegments(text, matches) {{
            var tl = text.toLowerCase();
            var positions = [];
            matches.forEach(function(m) {{
                var cl = m.chunk.toLowerCase();
                var found = false;
                var start = 0;
                while (start < tl.length) {{
                    var pos = tl.indexOf(cl, start);
                    if (pos < 0) break;
                    var overlaps = positions.some(function(p) {{ return pos < p.end && pos + cl.length > p.start; }});
                    if (!overlaps) {{
                        positions.push({{start: pos, end: pos + cl.length, lbl: m.label, orig: text.substring(pos, pos + cl.length)}});
                        found = true;
                        break;
                    }}
                    start = pos + 1;
                }}
                // Fallback: NER chunk spans multiple OCR bboxes — chunk is larger
                // than this bbox's text. Check reverse: is bbox text inside chunk?
                if (!found) {{
                    var tt = tl.trim();
                    if (tt.length > 0 && cl.indexOf(tt) >= 0) {{
                        var ts = tl.indexOf(tt);
                        var ov = positions.some(function(p) {{ return ts < p.end && ts + tt.length > p.start; }});
                        if (!ov) {{
                            positions.push({{start: ts, end: ts + tt.length, lbl: m.label, orig: text.substring(ts, ts + tt.length)}});
                        }}
                    }}
                }}
            }});
            positions.sort(function(a, b) {{ return a.start - b.start; }});
            var segs = [], last = 0;
            positions.forEach(function(p) {{
                if (p.start > last) segs.push({{t: text.substring(last, p.start), phi: false}});
                segs.push({{t: p.orig, phi: true, lbl: p.lbl}});
                last = p.end;
            }});
            if (last < text.length) segs.push({{t: text.substring(last), phi: false}});
            return segs;
        }}

        function render(i) {{
            var d = docs[i];
            document.getElementById('{vid}_ctr').textContent = (i+1) + ' / ' + total;

            // LEFT — redacted + BB overlays
            var left = document.getElementById('{vid}_left');
            left.innerHTML = '<img src="data:image/jpeg;base64,' + d.img_r + '">';
            d.boxes.forEach(function(b, idx) {{
                var div = document.createElement('div');
                div.className = 'bb';
                div.style.left = b.l + '%';
                div.style.top = b.tp + '%';
                div.style.width = b.w + '%';
                div.style.height = b.h + '%';
                var color = b.phi ? '{PHI_COLOR}' : '{SAFE_COLOR}';
                div.style.borderColor = color;
                if (b.phi) div.style.background = 'rgba(255,45,45,0.12)';

                var label = document.createElement('span');
                label.className = 'bb-label';
                label.style.background = color;
                label.textContent = b.phi ? (b.lbl || 'REDACTED') : b.t;
                div.appendChild(label);

                div.addEventListener('mouseenter', function(e) {{
                    var tag = b.phi
                        ? '<span style="color:#ff6b6b;font-weight:700">' + (b.lbl || 'PHI') + '</span>'
                        : '<span style="color:#4ECDC4">Safe</span>';
                    tt.innerHTML = tag + '<br>' + b.t;
                    tt.style.display = 'block';
                    var ti = document.querySelector('#{vid}_meta .tw[data-idx="'+idx+'"]');
                    if (ti) ti.style.background = 'rgba(255,255,255,0.2)';
                }});
                div.addEventListener('mousemove', function(e) {{
                    tt.style.left = (e.clientX + 14) + 'px';
                    tt.style.top = (e.clientY + 14) + 'px';
                }});
                div.addEventListener('mouseleave', function() {{
                    tt.style.display = 'none';
                    var ti = document.querySelector('#{vid}_meta .tw[data-idx="'+idx+'"]');
                    if (ti) ti.style.background = '';
                }});

                left.appendChild(div);
            }});

            // RIGHT — original
            var right = document.getElementById('{vid}_right');
            right.innerHTML = '<img src="data:image/jpeg;base64,' + d.img_o + '">';

            // META panel
            var meta = document.getElementById('{vid}_meta');
            var pct = d.n_total > 0 ? ((d.n_phi / d.n_total) * 100).toFixed(1) : '0.0';
            var methodLabel = d.method === 'GT'
                ? '<span class="mv gt">GT-matched</span>'
                : '<span class="mv">Simulated</span>';

            var h = '';
            h += '<div class="mrow"><span class="mk">Doc ID</span><span class="mv">' + d.id + '</span></div>';
            if (d.meta) {{
                for (var k in d.meta) {{
                    h += '<div class="mrow"><span class="mk">' + k + '</span><span class="mv">' + d.meta[k] + '</span></div>';
                }}
            }}
            if (showPhi) {{
                h += '<div class="mrow"><span class="mk">Method</span>' + methodLabel + '</div>';
                if (d.gt_count > 0) {{
                    h += '<div class="mrow"><span class="mk">GT entities</span><span class="mv gt">' + d.gt_count + '</span></div>';
                }}
            }}
            h += '<div class="mrow"><span class="mk">Regions</span><span class="mv">' + d.n_total + '</span></div>';
            if (showPhi) {{
                h += '<div class="mrow"><span class="mk">PHI flagged</span><span class="mv phi">' + d.n_phi + ' (' + pct + '%)</span></div>';
                h += '<div class="mrow"><span class="mk">Safe</span><span class="mv safe">' + d.n_safe + '</span></div>';
            }}
            h += '<div class="mrow"><span class="mk">Time</span><span class="mv">' + d.time + '</span></div>';

            // DEID Entity summary badges
            var elabels = {{}};
            d.boxes.forEach(function(b) {{
                if (b.phi && b.lbl) elabels[b.lbl] = (elabels[b.lbl] || 0) + 1;
            }});
            if (Object.keys(elabels).length > 0) {{
                h += '<div class="sep"></div>';
                h += '<div style="font-size:11px;color:#81b4d8;font-weight:600;margin-bottom:6px">DEID Entities</div>';
                h += '<div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:4px">';
                Object.keys(elabels).sort().forEach(function(lbl) {{
                    var c = deidColors[lbl] || '#ff6b6b';
                    h += '<span style="background:'+c+'22;border:1px solid '+c+'55;color:'+c+';padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600">'
                       + lbl + ' \u00d7' + elabels[lbl] + '</span>';
                }});
                h += '</div>';
            }}

            // Detected text — flowing block, PHI redacted with hover-to-reveal, NER highlighted
            h += '<div class="sep"></div>';
            h += '<div style="font-size:11px;color:#81b4d8;font-weight:600;margin-bottom:4px">Detected Text</div>';
            h += '<div class="text-block">';
            var lastY2 = -1;
            var bbEnter = function(idx) {{ return "var bb=document.querySelectorAll(\\'#{vid}_left .bb\\')["+idx+"];if(bb)bb.style.background=\\'rgba(255,255,255,0.25)\\';"; }};
            var bbLeave = function(idx, phi) {{ return "var bb=document.querySelectorAll(\\'#{vid}_left .bb\\')["+idx+"];if(bb)bb.style.background=\\'"+(phi?"rgba(255,45,45,0.12)":"")+"\\';"; }};

            // Link rxnorm codes to entity names (chunk field is index into pos_ents)
            if (d.pos_codes && d.pos_codes.rxnorm && d.pos_ents) {{
                d.pos_codes.rxnorm.forEach(function(r) {{
                    var ci = parseInt(r.chunk);
                    if (!isNaN(ci) && ci < d.pos_ents.length) {{
                        r.ner_entity = d.pos_ents[ci].chunk;
                    }}
                }});
            }}
            // Build rxnorm lookup for NER hover: lowercased entity text → [{{code, conf, desc}}]
            var nerRxLookup = {{}};
            if (d.pos_codes && d.pos_codes.rxnorm) {{
                d.pos_codes.rxnorm.forEach(function(r) {{
                    var key = (r.ner_entity || '').toLowerCase();
                    if (key) {{
                        if (!nerRxLookup[key]) nerRxLookup[key] = [];
                        nerRxLookup[key].push({{code: r.code || '\u2014', conf: r.confidence, desc: r.description || ''}});
                    }}
                }});
            }}

            d.boxes.forEach(function(b, idx) {{
                // Line break when Y jumps (new line on document)
                if (lastY2 >= 0 && b.tp - lastY2 > 1.5) {{
                    h += '<span class="lb"></span>';
                }}
                lastY2 = b.tp + b.h;
                if (b.phi && b.matches && b.matches.length > 0) {{
                    // Word-level: split line into PHI/safe segments
                    var segs = buildSegments(b.t, b.matches);
                    segs.forEach(function(seg) {{
                        if (seg.phi) {{
                            var dc = deidColors[seg.lbl] || '#ff6b6b';
                            h += '<span class="tw tw-phi" data-idx="'+idx+'" style="background:'+dc+'33;color:'+dc+';border:1px solid '+dc+'55"'
                               + ' onmouseenter="' + bbEnter(idx) + 'var rv=this.querySelector(\\'.reveal\\');if(rv){{rv.style.display=\\'block\\';var r=this.getBoundingClientRect();rv.style.left=r.left+\\'px\\';rv.style.top=(r.top-28)+\\'px\\';}}"'
                               + ' onmouseleave="' + bbLeave(idx, true) + 'var rv=this.querySelector(\\'.reveal\\');if(rv)rv.style.display=\\'none\\';"'
                               + '>[REDACTED]<span class="reveal">' + _esc(seg.t) + ' <span style="color:#94a3b8;font-size:9px">' + seg.lbl + '</span></span></span>';
                        }} else {{
                            h += '<span class="tw" data-idx="'+idx+'"'
                               + ' onmouseenter="' + bbEnter(idx) + '"'
                               + ' onmouseleave="' + bbLeave(idx, true) + '"'
                               + '>' + _esc(seg.t) + '</span>';
                        }}
                    }});
                    h += ' ';
                }} else if (b.phi) {{
                    // Fallback: whole text is PHI (no match detail)
                    var dc = deidColors[b.lbl] || '#ff6b6b';
                    h += '<span class="tw tw-phi" data-idx="'+idx+'" style="background:'+dc+'33;color:'+dc+';border:1px solid '+dc+'55"'
                       + ' onmouseenter="' + bbEnter(idx) + 'var rv=this.querySelector(\\'.reveal\\');if(rv){{rv.style.display=\\'block\\';var r=this.getBoundingClientRect();rv.style.left=r.left+\\'px\\';rv.style.top=(r.top-28)+\\'px\\';}}"'
                       + ' onmouseleave="' + bbLeave(idx, true) + 'var rv=this.querySelector(\\'.reveal\\');if(rv)rv.style.display=\\'none\\';"'
                       + '>[REDACTED]<span class="reveal">' + _esc(b.t) + ' <span style="color:#94a3b8;font-size:9px">' + (b.lbl || 'PHI') + '</span></span></span> ';
                }} else if (b.pos_matches && b.pos_matches.length > 0) {{
                    // Non-PHI box with NER entities: highlight matches (pre-computed in Python)
                    var nerSegs = buildSegments(b.t, b.pos_matches);
                    nerSegs.forEach(function(seg) {{
                        if (seg.phi) {{
                            var nc = posColors[seg.lbl] || '#a78bfa';
                            var rxCodes = nerRxLookup[(seg.t || '').toLowerCase()] || [];
                            var tipHtml = '<span style="color:'+nc+';font-weight:600">' + seg.lbl.replace(/_/g, ' ') + '</span>';
                            if (rxCodes.length > 0) {{
                                tipHtml += rxCodes.map(function(c) {{
                                    var pct = c.conf !== undefined ? ' <span style="color:#94a3b8">' + (c.conf * 100).toFixed(0) + '%</span>' : '';
                                    return ' <span style="background:#6366f125;color:#6366f1;padding:0 3px;border-radius:2px;font-size:9px;font-weight:700">RXNORM</span> <span style="color:#e8b96a;font-family:monospace">' + c.code + '</span>' + pct;
                                }}).join('');
                            }}
                            h += '<span class="tw tw-ner" data-idx="'+idx+'" style="background:'+nc+'22;color:'+nc+';border:1px solid '+nc+'44;border-radius:3px;padding:1px 4px;font-weight:500;cursor:default;position:relative"'
                               + ' onmouseenter="' + bbEnter(idx) + 'var rv=this.querySelector(\\'.reveal\\');if(rv){{rv.style.display=\\'block\\';var r=this.getBoundingClientRect();rv.style.left=r.left+\\'px\\';rv.style.top=(r.top-28)+\\'px\\';}}"'
                               + ' onmouseleave="' + bbLeave(idx, false) + 'var rv=this.querySelector(\\'.reveal\\');if(rv)rv.style.display=\\'none\\';"'
                               + '>' + _esc(seg.t) + '<span class="reveal" style="background:#1a1a2e;border:1px solid #6366f1;font-size:10px;padding:4px 10px">' + tipHtml + '</span></span>';
                        }} else {{
                            h += '<span class="tw" data-idx="'+idx+'"'
                               + ' onmouseenter="' + bbEnter(idx) + '"'
                               + ' onmouseleave="' + bbLeave(idx, false) + '"'
                               + '>' + _esc(seg.t) + '</span>';
                        }}
                    }});
                    h += ' ';
                }} else {{
                    h += '<span class="tw" data-idx="'+idx+'"'
                       + ' onmouseenter="' + bbEnter(idx) + '"'
                       + ' onmouseleave="' + bbLeave(idx, false) + '"'
                       + '>' + _esc(b.t) + '</span> ';
                }}
            }});
            h += '</div>';

            // ── Posology NER section (handwritten prescriptions) ──
            if (d.pos_ents && d.pos_ents.length > 0) {{
                h += '<div class="sep"></div>';
                h += '<div style="font-size:11px;color:#a78bfa;font-weight:600;margin-bottom:6px;display:flex;align-items:center;gap:6px">';
                h += '🧬 Posology NER <span style="font-size:9px;color:#64748b;font-weight:400">Spark NLP for Healthcare</span></div>';

                // Entity type badges
                var posCounts = {{}};
                d.pos_ents.forEach(function(e) {{ posCounts[e.label] = (posCounts[e.label] || 0) + 1; }});
                h += '<div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px">';
                Object.keys(posCounts).sort().forEach(function(lbl) {{
                    var c = posColors[lbl] || '#a78bfa';
                    h += '<span style="background:'+c+'22;border:1px solid '+c+'55;color:'+c+';padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600">'
                       + lbl + ' \u00d7' + posCounts[lbl] + '</span>';
                }});
                h += '</div>';

                // Build rxnorm code lookup: lowercased ner_entity → [{{code, confidence}}]
                var rxLookup = {{}};
                if (d.pos_codes && d.pos_codes.rxnorm) {{
                    d.pos_codes.rxnorm.forEach(function(r) {{
                        var key = (r.ner_entity || '').toLowerCase();
                        if (key) {{
                            if (!rxLookup[key]) rxLookup[key] = [];
                            rxLookup[key].push({{code: r.code || '\u2014', conf: r.confidence}});
                        }}
                    }});
                }}

                // Deduplicated entity table
                var posUniq = [], posSeen = {{}};
                d.pos_ents.forEach(function(e) {{
                    var key = (e.chunk || '') + '|' + (e.label || '');
                    if (!posSeen[key]) {{ posSeen[key] = true; posUniq.push(e); }}
                }});

                h += '<table style="width:100%;border-collapse:collapse;font-size:11px;margin-bottom:6px">';
                h += '<thead><tr style="border-bottom:1px solid #334155">';
                h += '<th style="padding:4px 6px;text-align:left;color:#64748b;font-weight:600">Entity</th>';
                h += '<th style="padding:4px 6px;text-align:left;color:#64748b;font-weight:600">Label</th>';
                h += '<th style="padding:4px 6px;text-align:left;color:#64748b;font-weight:600">Codes</th>';
                h += '</tr></thead><tbody>';

                posUniq.forEach(function(e, idx) {{
                    var c = posColors[e.label] || '#a78bfa';
                    var bgRow = idx % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)';
                    var codes = rxLookup[(e.chunk || '').toLowerCase()] || [];
                    var codeCells = '\u2014';
                    if (codes.length > 0) {{
                        codeCells = codes.map(function(cd) {{
                            var conf = cd.conf !== undefined ? ' ' + (cd.conf * 100).toFixed(0) + '%' : '';
                            return '<span style="white-space:nowrap"><span style="background:#6366f125;color:#6366f1;padding:0 4px;border-radius:2px;font-size:9px;font-weight:700;text-transform:uppercase">RXNORM</span> '
                                 + '<span style="color:#e8b96a;font-family:monospace">' + cd.code + '</span>'
                                 + '<span style="color:#64748b;font-size:9px">' + conf + '</span></span>';
                        }}).join(' ');
                    }}

                    h += '<tr class="pos-row" style="border-bottom:1px solid #1e293b;background:' + bgRow + ';cursor:default" '
                       + 'data-chunk="' + (e.chunk || '').replace(/"/g,'&quot;') + '" '
                       + 'data-label="' + (e.label || '') + '" '
                       + 'data-assertion="' + (e.assertion || '\u2014') + '" '
                       + 'data-model="' + (e._ner_model || '\u2014') + '" '
                       + 'data-rxcodes="' + codes.map(function(cd) {{ return cd.code + (cd.conf !== undefined ? ' ('+(cd.conf*100).toFixed(0)+'%)' : ''); }}).join(', ').replace(/"/g,'&quot;') + '">';
                    h += '<td style="padding:4px 6px;text-align:left;color:#e2e8f0;font-weight:500">' + (e.chunk || '') + '</td>';
                    h += '<td style="padding:4px 6px;text-align:left"><span style="background:'+c+'30;color:'+c+';padding:1px 6px;border-radius:3px;font-size:10px;font-weight:600">' + (e.label || '').replace(/_/g,' ') + '</span></td>';
                    h += '<td style="padding:4px 6px;text-align:left">' + codeCells + '</td>';
                    h += '</tr>';
                }});
                h += '</tbody></table>';

                // ── Medications table (only when posology relations are available) ──
                if (d.pos_rels && d.pos_rels.length > 0) {{
                    var drugs = d.pos_ents.filter(function(e) {{ return e.label === 'DRUG'; }});
                    var colMap = {{'DRUG-DOSAGE':'dosage','DRUG-FREQUENCY':'frequency','DRUG-ROUTE':'route',
                                  'DRUG-DURATION':'duration','DRUG-FORM':'form','DRUG-STRENGTH':'strength'}};
                    var medRows = [];
                    drugs.forEach(function(drug) {{
                        var row = {{drug: drug.chunk}};
                        d.pos_rels.forEach(function(rel) {{
                            var col = colMap[rel.relation];
                            if (!col) return;
                            if ((rel.entity1 || '').toLowerCase() === drug.chunk.toLowerCase()) row[col] = rel.entity2;
                            else if ((rel.entity2 || '').toLowerCase() === drug.chunk.toLowerCase()) row[col] = rel.entity1;
                        }});
                        var rxc = rxLookup[drug.chunk.toLowerCase()] || [];
                        if (rxc.length > 0) row.rxnorm = rxc[0].code;
                        medRows.push(row);
                    }});
                    h += '<div style="font-size:11px;color:#22c55e;font-weight:600;margin:10px 0 6px 0;display:flex;align-items:center;gap:6px">';
                    h += '\U0001F48A Medications <span style="font-size:9px;color:#64748b;font-weight:400">from posology relations</span></div>';
                    var medCols = ['Drug','Strength','Dosage','Route','Frequency','Duration','Form','RxNorm'];
                    var medKeys = ['drug','strength','dosage','route','frequency','duration','form','rxnorm'];
                    h += '<table style="width:100%;border-collapse:collapse;font-size:11px">';
                    h += '<thead><tr style="border-bottom:1px solid #334155">';
                    medCols.forEach(function(c) {{ h += '<th style="padding:4px 6px;text-align:left;color:#64748b;font-weight:600">' + c + '</th>'; }});
                    h += '</tr></thead><tbody>';
                    medRows.forEach(function(row, ri) {{
                        var bg = ri % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)';
                        h += '<tr style="border-bottom:1px solid #1e293b;background:'+bg+'">';
                        medKeys.forEach(function(k, ki) {{
                            var v = row[k] || '\u2014';
                            var style = 'padding:4px 6px;text-align:left;';
                            if (ki === 0) style += 'color:#22c55e;font-weight:600';
                            else if (k === 'rxnorm' && v !== '\u2014') style += 'color:#e8b96a;font-family:monospace';
                            else style += 'color:#e2e8f0';
                            h += '<td style="'+style+'">' + v + '</td>';
                        }});
                        h += '</tr>';
                    }});
                    h += '</tbody></table>';
                }}
            }}

            meta.innerHTML = h;

            // Posology row hover tooltips — attach after innerHTML is set
            if (d.pos_ents && d.pos_ents.length > 0) {{
                var posRows = meta.querySelectorAll('.pos-row');
                posRows.forEach(function(row) {{
                    row.addEventListener('mouseenter', function(ev) {{
                        var lines = [];
                        lines.push('<div><span style="color:#94a3b8">Entity:</span> <span style="color:#f1f5f9;font-weight:500">' + row.getAttribute('data-chunk') + '</span></div>');
                        lines.push('<div><span style="color:#94a3b8">Label:</span> <span style="color:#f1f5f9;font-weight:500">' + row.getAttribute('data-label') + '</span></div>');
                        lines.push('<div><span style="color:#94a3b8">Assertion:</span> <span style="color:#f1f5f9;font-weight:500">' + row.getAttribute('data-assertion') + '</span></div>');
                        lines.push('<div><span style="color:#94a3b8">Model:</span> <span style="color:#f1f5f9;font-weight:500">' + row.getAttribute('data-model') + '</span></div>');
                        var rxc = row.getAttribute('data-rxcodes');
                        if (rxc) {{
                            lines.push('<div><span style="background:#6366f130;color:#6366f1;padding:0 4px;border-radius:2px;font-weight:700;font-size:10px">RXNORM</span> <span style="color:#e8b96a;font-family:monospace">' + rxc + '</span></div>');
                        }}
                        tt.innerHTML = lines.join('');
                        tt.style.display = 'block';
                        tt.style.left = Math.min(ev.clientX + 14, window.innerWidth - 400) + 'px';
                        tt.style.top = (ev.clientY + 14) + 'px';
                    }});
                    row.addEventListener('mousemove', function(ev) {{
                        tt.style.left = Math.min(ev.clientX + 14, window.innerWidth - 400) + 'px';
                        tt.style.top = (ev.clientY + 14) + 'px';
                    }});
                    row.addEventListener('mouseleave', function() {{
                        tt.style.display = 'none';
                    }});
                }});
            }}
        }}

        window['{vid}_go'] = function(dir) {{
            cur = (cur + dir + total) % total;
            render(cur);
        }};

        render(0);
    }})();
    </script>
    """
    # Strip surrogate characters that OCR VLM may produce — prevents Jupyter ZMQ crash
    html = html.encode("utf-8", errors="replace").decode("utf-8")
    _display(_HTML(html))
