"""
KYC Demo utilities for NB2 (kyc_id_verification).
Keeps heavy HTML/JS viewer code out of the notebook.
"""

import json
import uuid
import base64
from io import BytesIO
from pathlib import Path
from difflib import SequenceMatcher
from PIL import Image, ImageDraw, ImageFont


# ============================================================================
# DATASET LOADING
# ============================================================================

_BB_COLORS = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
    '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B88B', '#ABEBC6',
]


def load_midv_dataset(midv_root, splits=('templates', 'photo'), samples_per=1):
    """Load MIDV-2020 images across all doc types and splits.

    Returns:
        (images, paths, metadata) — parallel lists
    """
    midv_root = Path(midv_root)
    doc_types = sorted(d.name for d in (midv_root / 'templates' / 'images').iterdir() if d.is_dir())

    images, paths, metadata = [], [], []
    for doc_type in doc_types:
        for split in splits:
            img_dir = midv_root / split / 'images' / doc_type
            if not img_dir.exists():
                continue
            for img_path in sorted(img_dir.glob('*.jpg'))[:samples_per]:
                images.append(Image.open(img_path).convert("RGB"))
                paths.append(img_path)
                metadata.append({
                    'doc_type': doc_type,
                    'split': split,
                    'filename': img_path.name,
                    'country': doc_type.split('_')[0].upper(),
                })

    print(f"✅ Loaded {len(images)} documents "
          f"({len(doc_types)} countries × {len(splits)} splits × {samples_per}/combo)")
    return images, paths, metadata


def build_annotated_preview(images, paths, metadata, midv_root, photo_matches=None, max_docs=30):
    """Build annotated preview images + rich metadata docs for display_document_analysis().

    Draws bounding boxes (all fields for templates, face-only for photos)
    and attaches GT field values + photo match info.

    Returns:
        (preview_images, preview_docs)
    """
    midv_root = Path(midv_root)
    anno_cache = {}
    preview_images, preview_docs = [], []

    for img, path, meta in zip(images[:max_docs], paths[:max_docs], metadata[:max_docs]):
        split, doc_type, filename = meta['split'], meta['doc_type'], meta['filename']

        # Load annotations (cached)
        cache_key = (split, doc_type)
        if cache_key not in anno_cache:
            anno_cache[cache_key] = _load_via_regions(midv_root, split, doc_type)
        regions = anno_cache[cache_key].get(filename, [])

        # Resize + draw BBs
        small = img.resize((img.width // 4, img.height // 4), Image.LANCZOS)
        annotated, field_info = _draw_bbs(small, regions, split)
        preview_images.append(annotated)

        # Build metadata doc
        doc = {
            'country': meta['country'],
            'doc_type': doc_type,
            'split': split,
            'filename': filename,
            'annotated_fields': len(regions),
        }
        for fn, fv, _ in field_info:
            if fv:
                doc[fn] = fv

        # Photo match info
        if split == 'photo' and photo_matches:
            match = photo_matches.get((doc_type, filename))
            if match:
                doc['matched_scan'] = match.get('matched_scan', 'N/A')
                doc['match_similarity'] = f"{match.get('similarity', 0):.3f}"
                for k, v in match.get('scan_data', {}).items():
                    if v and not k.startswith('_'):
                        doc[f'GT_{k}'] = v
            else:
                doc['matched_scan'] = 'no match'

        preview_docs.append(doc)

    return preview_images, preview_docs


def _load_via_regions(midv_root, split, doc_type):
    """Load VIA annotations as raw regions → {filename: [regions]}."""
    anno_file = Path(midv_root) / split / 'annotations' / f'{doc_type}.json'
    if not anno_file.exists():
        return {}
    with open(anno_file) as f:
        data = json.load(f)
    result = {}
    for img_data in data['_via_img_metadata'].values():
        result[img_data['filename']] = img_data['regions']
    return result


def _draw_bbs(img, regions, split):
    """Draw bounding boxes on image. Templates: all fields. Photos: face only."""
    img = img.copy()
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 9)
    except Exception:
        font = ImageFont.load_default()

    field_info = []
    for idx, region in enumerate(regions):
        shape = region.get('shape_attributes', {})
        attrs = region.get('region_attributes', {})
        field_name = attrs.get('field_name', '')
        field_value = attrs.get('value', '')

        if split == 'photo' and field_name not in ('face', 'photo', 'signature'):
            field_info.append((field_name, field_value, None))
            continue

        if shape.get('name') == 'rect':
            x, y = shape['x'] // 4, shape['y'] // 4
            w, h = shape['width'] // 4, shape['height'] // 4
            color = _BB_COLORS[idx % len(_BB_COLORS)]
            draw.rectangle([x, y, x + w, y + h], outline=color, width=2)
            bbox = draw.textbbox((x, y - 14), field_name, font=font)
            draw.rectangle(bbox, fill=color)
            draw.text((x, y - 14), field_name, fill='white', font=font)
            field_info.append((field_name, field_value, color))
        else:
            field_info.append((field_name, field_value, None))

    return img, field_info


# ============================================================================
# PHOTO GT LOADING — uses photo_scan_matches.json
# ============================================================================

# scan_data field names → GT_FIELDS used in accuracy calculation
_SCAN_TO_GT = {
    'surname': 'surname',
    'given_names': 'name',
    'birth_date': 'birth_date',
    'sex': 'gender',
    'document_number': 'number',
    'expiry_date': 'expiry_date',
    'issue_date': 'issue_date',
    'nationality': 'nationality',
    'birth_place': 'birth_place',
    'authority': 'authority',
    'mrz_line1': 'mrz_line0',
    'mrz_line2': 'mrz_line1',
}


def load_photo_matches(matches_path):
    """Load photo_scan_matches.json and index by (doc_type, filename).

    Returns:
        dict: {(doc_type, photo_filename): match_record, ...}
    """
    path = Path(matches_path)
    if not path.exists():
        return {}
    with open(path) as f:
        data = json.load(f)
    index = {}
    for doc_type, matches in data.items():
        for m in matches:
            index[(doc_type, m['photo'])] = m
    return index


def photo_gt_from_match(match_record):
    """Convert a photo_scan_matches record into a GT dict
    with field names matching GT_FIELDS.

    Args:
        match_record: single entry from photo_scan_matches.json

    Returns:
        dict with keys like 'surname', 'name', 'birth_date', etc.
    """
    scan_data = match_record.get('scan_data', {})
    gt = {}
    for scan_field, gt_field in _SCAN_TO_GT.items():
        val = scan_data.get(scan_field, '')
        if val:
            gt[gt_field] = val
    return gt


def load_gt_for_doc(meta, midv_root, photo_matches=None, anno_cache=None):
    """Load GT for a document — uses annotations for templates, photo matches for photos.

    Args:
        meta: dict with 'split', 'doc_type', 'filename'
        midv_root: Path to MIDV2020 root
        photo_matches: dict from load_photo_matches() (needed for photo split)
        anno_cache: optional dict cache for annotations {(split, doc_type): gt_by_file}

    Returns:
        dict of {field_name: gt_value}
    """
    split = meta['split']
    doc_type = meta['doc_type']
    filename = meta['filename']

    if split == 'photo' and photo_matches:
        match = photo_matches.get((doc_type, filename))
        if match:
            return photo_gt_from_match(match)
        return {}

    # Templates / scans: load from VIA annotations
    if anno_cache is not None:
        cache_key = (split, doc_type)
        if cache_key not in anno_cache:
            anno_cache[cache_key] = _load_via_annotations(midv_root, split, doc_type)
        return anno_cache[cache_key].get(filename, {})

    return _load_via_annotations(midv_root, split, doc_type).get(filename, {})


def _load_via_annotations(midv_root, split, doc_type):
    """Load VIA-format annotations → {filename: {field: value}}."""
    anno_file = Path(midv_root) / split / 'annotations' / f'{doc_type}.json'
    if not anno_file.exists():
        return {}
    with open(anno_file) as f:
        data = json.load(f)
    gt_by_file = {}
    for img_data in data['_via_img_metadata'].values():
        fields = {}
        for region in img_data['regions']:
            fn = region['region_attributes'].get('field_name', '')
            fv = region['region_attributes'].get('value', '')
            if fn and fv:
                fields[fn] = fv
        gt_by_file[img_data['filename']] = fields
    return gt_by_file


# ============================================================================
# KYC PREDICTIONS VIEWER — 3-column table (Field | Prediction | Ground Truth)
# ============================================================================

def normalize(s):
    """Normalize string for fuzzy comparison."""
    if not s:
        return ""
    return str(s).lower().strip().replace(' ', '').replace('.', '').replace('-', '').replace(',', '')


def build_table_data(kyc_results, midv_root, photo_matches=None, gt_fields=None):
    """Build per-doc table rows for the predictions viewer.

    Args:
        kyc_results: list of inference results (each has 'data' and '_meta')
        midv_root: Path to MIDV2020
        photo_matches: dict from load_photo_matches()
        gt_fields: list of field names to validate against GT

    Returns:
        list of list-of-dicts, one per document.
        Each row: {'field': str, 'pred': str, 'gt': str, 'match': 'good'|'bad'|'neutral'}
    """
    if gt_fields is None:
        gt_fields = [
            'surname', 'name', 'birth_date', 'gender', 'number', 'expiry_date',
            'issue_date', 'nationality', 'id_number', 'birth_place', 'authority',
            'mrz_line0', 'mrz_line1',
        ]

    anno_cache = {}
    docs_table_data = []
    translatable = {'surname', 'name', 'birth_place', 'nationality', 'authority'}

    for result in kyc_results:
        if not result or 'data' not in result:
            docs_table_data.append([])
            continue

        extracted = result['data']
        meta = result.get('_meta', {})

        gt = load_gt_for_doc(meta, midv_root, photo_matches, anno_cache)

        rows = []
        # Metadata rows
        rows.append({'field': 'country', 'pred': meta.get('country', ''), 'gt': '', 'match': 'neutral'})
        rows.append({'field': 'split', 'pred': meta.get('split', ''), 'gt': '', 'match': 'neutral'})

        # Collect all fields: model output + GT fields not returned by model
        seen_keys = set()
        all_keys = list(extracted.keys()) + [f for f in gt_fields if f not in extracted]

        for key in all_keys:
            if key.startswith('_') or key.endswith('_en') or key in seen_keys:
                continue
            seen_keys.add(key)

            value = extracted.get(key)
            pred_str = str(value) if value else ""
            if key in translatable and f"{key}_en" in extracted and extracted[f"{key}_en"]:
                pred_str += f" [EN: {extracted[f'{key}_en']}]"

            gt_val = gt.get(key, '')
            if gt_val:
                sim = SequenceMatcher(None, normalize(str(value) if value else ""), normalize(gt_val)).ratio()
                match = 'good' if sim > 0.7 else 'bad'
            else:
                match = 'neutral'

            rows.append({'field': key, 'pred': pred_str, 'gt': gt_val, 'match': match})

        docs_table_data.append(rows)

    return docs_table_data


def display_kyc_predictions(kyc_images, kyc_results, midv_root,
                            photo_matches=None, gt_fields=None):
    """Render the interactive 3-column predictions viewer.

    Args:
        kyc_images: list of PIL Images
        kyc_results: list of inference results
        midv_root: Path to MIDV2020
        photo_matches: dict from load_photo_matches()
        gt_fields: optional list of GT field names
    """
    from IPython.display import display, HTML

    table_data = build_table_data(kyc_results, midv_root, photo_matches, gt_fields)

    # Convert images to base64
    images_b64 = []
    for img in kyc_images:
        buf = BytesIO()
        img.save(buf, format="PNG")
        images_b64.append(base64.b64encode(buf.getvalue()).decode())

    vid = f"tbl_{uuid.uuid4().hex[:8]}"
    table_json = json.dumps(table_data)
    images_json = json.dumps(images_b64)
    total = len(kyc_images)

    html = _build_kyc_viewer_html(vid, images_json, table_json, total)
    display(HTML(html))


def _build_kyc_viewer_html(vid, images_json, table_json, total):
    """Build the full HTML/CSS/JS for the KYC predictions viewer."""
    return f"""
<style>
#{vid} {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: #d4d4d4;
}}
#{vid} .header {{
    background: linear-gradient(135deg, #6d28d9 0%, #2a9d8f 100%);
    padding: 20px 30px;
    border-radius: 12px;
    margin-bottom: 16px;
    text-align: center;
}}
#{vid} .header h1 {{
    color: white; margin: 0; font-size: 28px; letter-spacing: 2px;
}}
#{vid} .header p {{
    color: #e2e8f0; margin: 8px 0 0 0; font-size: 14px;
}}
#{vid} .nav {{
    display: flex; align-items: center; justify-content: center; gap: 12px;
    margin-bottom: 16px;
}}
#{vid} .nav button {{
    background: #334155; color: #d4d4d4; border: 1px solid #475569;
    padding: 8px 18px; border-radius: 6px; cursor: pointer; font-size: 14px;
}}
#{vid} .nav button:hover {{ background: #475569; }}
#{vid} .nav span {{ color: #94a3b8; font-size: 14px; min-width: 100px; text-align: center; }}
#{vid} .content {{
    display: flex; gap: 20px; align-items: flex-start;
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
    background: #1e293b; color: #8ecae6; padding: 10px 12px;
    text-align: left; border-bottom: 2px solid #6d28d9;
    font-weight: 600; text-transform: uppercase; font-size: 12px; letter-spacing: 1px;
}}
#{vid} td {{
    padding: 7px 12px; border-bottom: 1px solid #334155;
    vertical-align: top; word-break: break-word; text-align: left;
}}
#{vid} tr.good td {{ background: rgba(16, 185, 129, 0.08); }}
#{vid} tr.bad td {{ background: rgba(239, 68, 68, 0.10); }}
#{vid} tr.neutral td {{ background: transparent; }}
#{vid} td.field-name {{
    color: #81b4d8; font-weight: 600; white-space: nowrap; width: 130px;
}}
#{vid} td.pred {{ color: #d4d4d4; }}
#{vid} td.gt {{ color: #a7c4bc; }}
#{vid} tr.bad td.pred {{ color: #fca5a5; }}
#{vid} tr.bad td.gt {{ color: #f87171; }}
#{vid} tr.good td.field-name::after {{
    content: ' ✓'; color: #7bc47f; font-size: 11px;
}}
#{vid} tr.bad td.field-name::after {{
    content: ' ✗'; color: #ef4444; font-size: 11px;
}}
</style>

<div id="{vid}">
    <div class="header">
        <h1>MODEL PREDICTIONS</h1>
        <p>Structured extraction vs MIDV-2020 ground truth &mdash; Field | Prediction | Ground Truth</p>
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


# ============================================================================
# HIGH-LEVEL PIPELINE HELPERS
# ============================================================================

_FIELD_ALIASES = {
    'surname':      ['surname', 'last_name', 'family_name'],
    'name':         ['name', 'given_names', 'first_name', 'given_name'],
    'birth_date':   ['birth_date', 'date_of_birth', 'dob'],
    'id_number':    ['id_number', 'personal_number', 'number'],
    'number':       ['number', 'document_number', 'card_number', 'id_number'],
    'nationality':  ['nationality'],
    'gender':       ['gender', 'sex'],
    'authority':    ['authority', 'issuing_authority'],
    'issue_date':   ['issue_date', 'date_of_issue'],
    'expiry_date':  ['expiry_date', 'date_of_expiry', 'expiration_date'],
    'birth_place':  ['birth_place', 'place_of_birth'],
    'mrz_line0':    ['mrz_line0'],
    'mrz_line1':    ['mrz_line1'],
}


def find_best_value(extracted_data, gt_field, gt_value):
    """Return best matching value from extracted_data for a GT field.

    Handles swapped fields (e.g. id_number/number) and common aliases.
    Falls back to direct key lookup; returns None if no candidate found.
    """
    if extracted_data.get(gt_field):
        return extracted_data[gt_field]

    best_val, best_sim = None, 0.0
    for alias in _FIELD_ALIASES.get(gt_field, [gt_field]):
        val = extracted_data.get(alias)
        if val:
            sim = SequenceMatcher(None, normalize(str(val)), normalize(gt_value)).ratio()
            if sim > best_sim:
                best_sim = sim
                best_val = val
    return best_val


def run_kyc_extraction(infer_fn, images, paths, metadata, prompt, schema, timeout=30):
    """Run structured KYC extraction over a list of images.

    Args:
        infer_fn:  ``infer_image_structured`` callable from the notebook
        images:    list of PIL Images
        paths:     list of Path objects (used for error messages)
        metadata:  list of metadata dicts — each is stored as result['_meta']
        prompt:    user prompt string
        schema:    JSON-schema dict (passed to infer_fn)
        timeout:   per-image inference timeout in seconds

    Returns:
        list of result dicts (or None on failure), length == len(images)
    """
    from tqdm.auto import tqdm

    print("🔄 Processing KYC documents with structured schema extraction...")
    print("=" * 80)

    results = []
    for img, path, meta in tqdm(zip(images, paths, metadata), total=len(images), desc="🔐 Extracting"):
        try:
            result = infer_fn(img, prompt, schema, timeout=timeout)
            result['_meta'] = meta
            results.append(result)
        except Exception as e:
            print(f"⚠️  Error on {path.name}: {e}")
            results.append(None)

    success = sum(1 for r in results if r is not None)
    print(f"\n✅ Extraction complete: {success}/{len(images)} ({100 * success / len(images):.1f}%)")

    # Quick peek at first successful extraction
    for r in results:
        if r and 'data' in r:
            print(f"\n📄 Sample ({r['_meta']['doc_type']}, {r['_meta']['split']}):")
            for k, v in r['data'].items():
                if v and not k.endswith('_en'):
                    print(f"   {k}: {v}")
            break

    return results


def run_kyc_accuracy(kyc_results, midv_root, gt_fields, photo_matches=None):
    """Compute field-level accuracy of KYC results against MIDV-2020 ground truth.

    Args:
        kyc_results:   output of run_kyc_extraction()
        midv_root:     Path to MIDV2020 root directory
        gt_fields:     list of field names to validate (e.g. GT_FIELDS)
        photo_matches: dict from load_photo_matches() (needed for photo split)

    Returns:
        (field_stats, per_doc_details, all_field_scores)
        - field_stats:      {field: {'correct': int, 'total': int, 'similarities': list}}
        - per_doc_details:  list of per-doc comparison dicts
        - all_field_scores: flat list of similarity floats (all fields, all docs)
    """
    midv_root = Path(midv_root)
    anno_cache = {}
    field_stats = {}
    per_doc_details = []
    all_field_scores = []

    for result in kyc_results:
        if not result or '_meta' not in result or 'data' not in result:
            continue

        meta = result['_meta']
        extracted = result['data']
        gt = load_gt_for_doc(meta, midv_root, photo_matches, anno_cache)

        doc_detail = {
            'doc': f"{meta['doc_type']}/{meta['split']}/{meta['filename']}",
            'fields': {},
        }

        for field in gt_fields:
            if field not in gt or not gt[field]:
                continue

            ext_val_raw = find_best_value(extracted, field, gt[field])
            ext_norm = normalize(str(ext_val_raw) if ext_val_raw else "")
            gt_norm = normalize(gt[field])

            sim = SequenceMatcher(None, ext_norm, gt_norm).ratio() if ext_norm else 0.0
            ok = sim > 0.7

            stats = field_stats.setdefault(field, {'correct': 0, 'total': 0, 'similarities': []})
            stats['total'] += 1
            stats['similarities'].append(sim)
            if ok:
                stats['correct'] += 1

            all_field_scores.append(sim)
            doc_detail['fields'][field] = {
                'extracted': ext_val_raw, 'gt': gt[field],
                'sim': f"{sim:.2f}", 'ok': ok,
            }

        per_doc_details.append(doc_detail)

    return field_stats, per_doc_details, all_field_scores


def show_kyc_accuracy_table(field_stats, per_doc_details, gt_fields, all_field_scores):
    """Print field-level accuracy table + sample comparisons.

    Args:
        field_stats:       from run_kyc_accuracy()
        per_doc_details:   from run_kyc_accuracy()
        gt_fields:         list of field names (controls row order)
        all_field_scores:  from run_kyc_accuracy()
    """
    print("\n" + "=" * 80)
    print("📊 ACCURACY ANALYSIS: Extracted vs Ground Truth")
    print("=" * 80)

    print("\n📋 Field-Level Accuracy (fuzzy match > 0.7):")
    print("-" * 65)
    print(f"  {'Field':15s}   {'Accuracy':>8s}   {'Avg Sim':>8s}   {'Correct/Total':>15s}")
    print("-" * 65)
    for field in gt_fields:
        if field not in field_stats:
            continue
        s = field_stats[field]
        acc = s['correct'] / s['total'] * 100 if s['total'] else 0
        avg_sim = sum(s['similarities']) / len(s['similarities']) * 100
        print(f"  {field:15s}   {acc:6.1f}%   {avg_sim:6.1f}%   {s['correct']:>5d}/{s['total']:<5d}")

    if all_field_scores:
        n_correct = sum(1 for s in all_field_scores if s > 0.7)
        overall = n_correct / len(all_field_scores) * 100
        avg = sum(all_field_scores) / len(all_field_scores) * 100
        print("-" * 65)
        print(f"\n🎯 Overall Field Accuracy: {overall:.1f}% ({n_correct}/{len(all_field_scores)} fields)")
        print(f"📊 Average Similarity: {avg:.1f}%")

        print(f"\n📝 Sample Comparisons (first 3 docs):")
        for detail in per_doc_details[:3]:
            print(f"\n  {detail['doc']}:")
            for field, info in detail['fields'].items():
                icon = "✅" if info['ok'] else "❌"
                print(f"    {icon} {field}: '{info['extracted']}' vs GT: '{info['gt']}' (sim: {info['sim']})")


def show_kyc_analytics(kyc_results):
    """Print extraction analytics summary: success rate, languages, doc types, countries."""
    from collections import Counter

    print(f"\n{'=' * 60}")
    print("ANALYTICS SUMMARY")
    print(f"{'=' * 60}")

    success = [r for r in kyc_results if r and 'data' in r]
    print(f"\nExtraction Success: {len(success)}/{len(kyc_results)} ({100 * len(success) / len(kyc_results):.1f}%)")

    if not success:
        return

    languages = [r['data'].get('language', 'Unknown') for r in success]
    print("\nLanguages Detected:")
    for lang, count in Counter(languages).most_common():
        print(f"   {lang}: {count}")

    doc_types = [r['data'].get('document_type', 'Unknown') for r in success]
    print("\nDocument Types:")
    for dt, count in Counter(doc_types).most_common():
        print(f"   {dt}: {count}")

    with_trans = sum(
        1 for r in success
        if any(k.endswith('_en') and r['data'].get(k) for k in r['data'])
    )
    print(f"\nTranslation Coverage: {with_trans}/{len(success)} docs with English translations")

    countries = [r['_meta']['country'] for r in kyc_results if r and '_meta' in r]
    print("\nDocuments by Country:")
    for country, count in Counter(countries).most_common():
        print(f"   {country}: {count}")


# ============================================================================
# MULTI-MODEL COMPARISON
# ============================================================================

# Display-friendly model labels
_MODEL_LABELS = {
    'jsl-medical-vl-7b':            'JSL-7B',
    'jsl-medical-vl-30b':           'JSL-30B',
    'anthropic__claude-sonnet-4.6':  'Claude Sonnet 4.6',
    'anthropic__claude-opus-4.5':    'Claude Opus 4.5',
    'openai__gpt-4.1':              'GPT-4.1',
    'openai__gpt-5.4':              'GPT-5.4',
    'jsl_vision_ocr_1.0':           'JSL Vision OCR 1.0',
}


def load_kyc_model_results(nb_name, cache_key, model_names):
    """Load cached KYC results for multiple models.

    Args:
        nb_name:     notebook cache name (e.g. 'nb8_kyc')
        cache_key:   cache key (e.g. 'kyc_results')
        model_names: list of cache model names

    Returns:
        dict {model_name: results_list}
    """
    from utils.core import set_cache_model, has_nb_cache, load_nb_cache

    out = {}
    for m in model_names:
        set_cache_model(m)
        if has_nb_cache(nb_name, cache_key):
            cached = load_nb_cache(nb_name, cache_key)
            results = cached["results"]
            results = [r if r is not None and r != "null" else None for r in results]
            out[m] = results
            n = sum(1 for r in results if r is not None)
            print(f"  📦 {_MODEL_LABELS.get(m, m)}: {n}/{len(results)} docs")
        else:
            print(f"  ⚠️  {_MODEL_LABELS.get(m, m)}: no cache found")
    return out


def show_kyc_model_comparison(models_results, midv_root, gt_fields, photo_matches=None):
    """Show side-by-side accuracy comparison for multiple KYC models.

    Args:
        models_results: dict {model_name: results_list} from load_kyc_model_results()
        midv_root:      Path to MIDV2020
        gt_fields:      list of GT field names
        photo_matches:  dict from load_photo_matches()
    """
    from IPython.display import display, HTML

    # Compute accuracy per model
    model_stats = {}
    for model_name, results in models_results.items():
        fs, _, scores = run_kyc_accuracy(results, midv_root, gt_fields, photo_matches)
        model_stats[model_name] = (fs, scores)

    labels = [_MODEL_LABELS.get(m, m) for m in models_results]
    model_keys = list(models_results.keys())

    # Build HTML table
    header = "".join(f"<th>{l}</th>" for l in labels)

    rows_html = ""
    for field in gt_fields:
        cells = ""
        for mk in model_keys:
            fs = model_stats[mk][0]
            if field in fs and fs[field]['total'] > 0:
                acc = fs[field]['correct'] / fs[field]['total'] * 100
                avg_sim = sum(fs[field]['similarities']) / len(fs[field]['similarities']) * 100
                # Color: green >70, yellow >40, red <=40
                if acc > 70:
                    bg = "rgba(16,185,129,0.15)"
                elif acc > 40:
                    bg = "rgba(234,179,8,0.12)"
                else:
                    bg = "rgba(239,68,68,0.10)"
                cells += f'<td style="background:{bg}">{acc:.0f}%<br><span style="color:#8a8a8a;font-size:11px">sim {avg_sim:.0f}%</span></td>'
            else:
                cells += '<td style="color:#666">—</td>'
        rows_html += f"<tr><td style='font-weight:600;color:#81b4d8;padding:6px 12px'>{field}</td>{cells}</tr>\n"

    # Overall row
    overall_cells = ""
    for mk in model_keys:
        scores = model_stats[mk][1]
        if scores:
            n_ok = sum(1 for s in scores if s > 0.7)
            overall = n_ok / len(scores) * 100
            avg = sum(scores) / len(scores) * 100
            overall_cells += f'<td style="font-weight:700;font-size:16px">{overall:.1f}%<br><span style="color:#8a8a8a;font-size:11px">avg sim {avg:.0f}%</span></td>'
        else:
            overall_cells += '<td style="color:#666">—</td>'

    # Success rate row
    success_cells = ""
    for mk in model_keys:
        results = models_results[mk]
        n = sum(1 for r in results if r is not None and 'data' in r)
        success_cells += f'<td>{n}/{len(results)}</td>'

    html = f"""
    <style>
    .kyc-compare {{ font-family: -apple-system, sans-serif; color: #d4d4d4; }}
    .kyc-compare .hdr {{
        background: linear-gradient(135deg, #6d28d9 0%, #2a9d8f 100%);
        padding: 16px 24px; border-radius: 10px; margin-bottom: 12px; text-align: center;
    }}
    .kyc-compare .hdr h2 {{ color: white; margin: 0; font-size: 22px; letter-spacing: 1.5px; }}
    .kyc-compare table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    .kyc-compare th {{
        background: #1e293b; color: #8ecae6; padding: 10px 12px;
        text-align: left !important; border-bottom: 2px solid #6d28d9;
        font-weight: 600; font-size: 12px; letter-spacing: 1px;
    }}
    .kyc-compare td {{ padding: 6px 12px; border-bottom: 1px solid #334155; text-align: left !important; }}
    .kyc-compare tr.overall td {{ border-top: 2px solid #6d28d9; font-size: 14px; }}
    </style>
    <div class="kyc-compare">
        <div class="hdr"><h2>MODEL COMPARISON</h2></div>
        <table>
            <thead><tr><th>Field</th>{header}</tr></thead>
            <tbody>
                {rows_html}
                <tr class="overall"><td style="font-weight:700;color:#e2e8f0">Overall Accuracy</td>{overall_cells}</tr>
                <tr><td style="font-weight:600;color:#94a3b8">Extraction Success</td>{success_cells}</tr>
            </tbody>
        </table>
    </div>
    """
    display(HTML(html))


# ============================================================================
# ACCURACY CHARTS — dark-mode matplotlib
# ============================================================================

_DARK_THEME = {
    'figure.facecolor': '#0f172a',
    'axes.facecolor': '#0f172a',
    'text.color': '#e2e8f0',
    'axes.labelcolor': '#e2e8f0',
    'xtick.color': '#94a3b8',
    'ytick.color': '#94a3b8',
}

_MODEL_COLORS = {
    'anthropic__claude-sonnet-4.6': '#8b5cf6',
    'anthropic__claude-opus-4.5':   '#a78bfa',
    'openai__gpt-4.1':             '#10b981',
    'openai__gpt-5.4':             '#34d399',
    'jsl_vision_ocr_1.0':          '#f59e0b',
    'jsl-medical-vl-7b':           '#0ea5e9',
    'jsl-medical-vl-30b':          '#ec4899',
}


def _compute_split_accuracy(results, midv_root, gt_fields, photo_matches):
    """Compute accuracy split by templates vs photos."""
    anno_cache = {}
    splits = {'templates': [], 'photo': []}

    for result in results:
        if not result or '_meta' not in result or 'data' not in result:
            continue
        meta = result['_meta']
        extracted = result['data']
        split = meta['split']
        gt = load_gt_for_doc(meta, midv_root, photo_matches, anno_cache)

        for field in gt_fields:
            if field not in gt or not gt[field]:
                continue
            ext_val_raw = find_best_value(extracted, field, gt[field])
            ext_norm = normalize(str(ext_val_raw) if ext_val_raw else "")
            gt_norm = normalize(gt[field])
            sim = SequenceMatcher(None, ext_norm, gt_norm).ratio() if ext_norm else 0.0
            splits[split].append(sim)

    out = {}
    for s_name, scores in splits.items():
        if scores:
            out[s_name] = sum(1 for s in scores if s > 0.7) / len(scores) * 100
        else:
            out[s_name] = 0.0
    all_scores = splits['templates'] + splits['photo']
    out['overall'] = sum(1 for s in all_scores if s > 0.7) / len(all_scores) * 100 if all_scores else 0.0
    return out


def plot_kyc_split_accuracy(models_results, midv_root, gt_fields, photo_matches=None):
    """Bar chart: Overall / Templates / Photos accuracy per model."""
    import matplotlib.pyplot as plt
    import matplotlib
    import numpy as np
    matplotlib.rcParams.update(_DARK_THEME)

    model_keys = list(models_results.keys())
    labels = [_MODEL_LABELS.get(m, m) for m in model_keys]
    colors = [_MODEL_COLORS.get(m, '#6366f1') for m in model_keys]

    # Compute split accuracy per model
    data = {}
    for mk, results in models_results.items():
        data[mk] = _compute_split_accuracy(results, midv_root, gt_fields, photo_matches)

    categories = ['Overall', 'Templates (scan)', 'Photos (camera)']
    cat_keys = ['overall', 'templates', 'photo']
    n_models = len(model_keys)
    n_cats = len(categories)

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(n_cats)
    width = 0.8 / n_models

    for i, mk in enumerate(model_keys):
        vals = [data[mk].get(ck, 0) for ck in cat_keys]
        offset = (i - n_models / 2 + 0.5) * width
        bars = ax.bar(x + offset, vals, width * 0.9, label=labels[i],
                      color=colors[i], edgecolor='#1e293b', linewidth=0.5)
        for bar, val in zip(bars, vals):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                        f'{val:.0f}%', ha='center', va='bottom', fontsize=9,
                        color='#cbd5e1', fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=12)
    ax.set_ylabel('Accuracy (%)', fontsize=11)
    ax.set_title('KYC Accuracy: Scans vs Camera Photos', fontsize=14,
                 color='#f1f5f9', pad=12)
    ax.set_ylim(0, 105)
    ax.legend(loc='upper right', fontsize=10, facecolor='#1e293b',
              edgecolor='#334155', labelcolor='#e2e8f0')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#334155')
    ax.spines['left'].set_color('#334155')
    ax.axhline(y=50, color='#334155', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()


def plot_kyc_field_accuracy(models_results, midv_root, gt_fields, photo_matches=None):
    """Horizontal bar chart: per-field accuracy across models."""
    import matplotlib.pyplot as plt
    import matplotlib
    import numpy as np
    matplotlib.rcParams.update(_DARK_THEME)

    model_keys = list(models_results.keys())
    labels = [_MODEL_LABELS.get(m, m) for m in model_keys]
    colors = [_MODEL_COLORS.get(m, '#6366f1') for m in model_keys]

    # Compute per-field accuracy per model
    model_field_acc = {}
    for mk, results in models_results.items():
        fs, _, _ = run_kyc_accuracy(results, midv_root, gt_fields, photo_matches)
        accs = {}
        for field in gt_fields:
            if field in fs and fs[field]['total'] > 0:
                accs[field] = fs[field]['correct'] / fs[field]['total'] * 100
            else:
                accs[field] = 0.0
        model_field_acc[mk] = accs

    # Filter fields that have data for at least one model
    fields_to_show = [f for f in gt_fields
                      if any(model_field_acc[mk].get(f, 0) > 0 for mk in model_keys)]

    n_fields = len(fields_to_show)
    n_models = len(model_keys)

    fig_h = max(4, n_fields * 0.5 + 1.5)
    fig, ax = plt.subplots(figsize=(10, fig_h))

    y = np.arange(n_fields)
    height = 0.8 / n_models

    for i, mk in enumerate(model_keys):
        vals = [model_field_acc[mk].get(f, 0) for f in fields_to_show]
        offset = (i - n_models / 2 + 0.5) * height
        bars = ax.barh(y + offset, vals, height * 0.9, label=labels[i],
                       color=colors[i], edgecolor='#1e293b', linewidth=0.5)
        for bar, val in zip(bars, vals):
            if val > 0:
                ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                        f'{val:.0f}%', va='center', fontsize=8,
                        color='#cbd5e1')

    ax.set_yticks(y)
    ax.set_yticklabels(fields_to_show, fontsize=10)
    ax.set_xlabel('Accuracy (%)', fontsize=11)
    ax.set_title('Per-Field Accuracy by Model', fontsize=14,
                 color='#f1f5f9', pad=12)
    ax.set_xlim(0, 110)
    ax.legend(loc='lower right', fontsize=9, facecolor='#1e293b',
              edgecolor='#334155', labelcolor='#e2e8f0')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#334155')
    ax.spines['left'].set_color('#334155')
    ax.axvline(x=70, color='#475569', linestyle='--', linewidth=0.5, alpha=0.7)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.show()
