"""
Dataset loading utilities for document processing demos.

Extracted from demo_utils.py — contains functions for loading images from
HuggingFace datasets, local folders, medical image collections, and
curated RAG intro datasets. Also includes schema comparison benchmarking.
"""

import json
from pathlib import Path

from PIL import Image


__all__ = [
    "run_schema_comparison",
    "load_gt_sources",
    "load_hf_dataset",
    "load_hf_mix",
    "load_medical_mix",
    "load_rag_intro_dataset",
    "build_derm_index",
]


def run_schema_comparison(subset, images, nb_name, use_cache, infer_fn, n=8,
                          target_formats=None):
    """Pick diverse docs from an OCR benchmark subset, run per-doc schema extraction.

    Returns (indices, images, schemas, predictions, labels) ready for display.
    """
    from utils.core import has_nb_cache, load_nb_cache, save_nb_cache
    if target_formats is None:
        target_formats = ["DRIVER_LICENSE", "BANK_CHECK", "PHOTO_RECEIPT",
                          "SHIPPING_INVOICE", "SCANNED_FORM", "FORM", "TABLE", "CHART"]

    # Pick one doc per format type
    indices, seen = [], set()
    for i in range(len(subset)):
        fmt = json.loads(subset[i]["metadata"] or "{}").get("format", "")
        if fmt not in seen and (fmt in target_formats or len(indices) < n):
            indices.append(i); seen.add(fmt)
        if len(indices) >= n:
            break

    # Load per-doc schemas
    schemas, labels = [], []
    for i in indices:
        schema = json.loads(subset[i]["json_schema"])
        fmt = json.loads(subset[i]["metadata"] or "{}").get("format", "unknown")
        title = schema.get("title", fmt.replace("_", " ").title())
        schemas.append(schema)
        labels.append(f"{title} ({len(schema.get('properties', {}))} fields)")

    # Run inference (cached)
    cache_key = "schema_comparison"
    if use_cache and has_nb_cache(nb_name, cache_key):
        preds = load_nb_cache(nb_name, cache_key)["domain_results"]
        print(f"Cached -- {len(preds)} comparisons")
    else:
        from tqdm.notebook import tqdm
        preds = []
        for j, idx in enumerate(tqdm(indices, desc="Comparing schemas")):
            clean = {k: v for k, v in schemas[j].items() if k not in ("$schema", "title")}
            try:
                out = infer_fn(images[idx],
                               "Extract all information from this document according to the schema.",
                               clean)
                preds.append(out["data"])
            except Exception as e:
                preds.append({"_error": str(e)})
        save_nb_cache(nb_name, cache_key, {"domain_results": preds, "indices": indices})

    return indices, [images[i] for i in indices], schemas, preds, labels


def load_gt_sources(sources, seed=42):
    """Load images from local folders with GT labels for benchmarking.

    sources : list of (folder_path, id_prefix, n, gt_document_type, gt_routing_department)
    Returns : (images, ids, gt_map)  where gt_map = {doc_id: {document_type, routing_department}}
    """
    import random as _rng
    _rng.seed(seed)
    imgs, ids, gt_map = [], [], {}
    for folder, prefix, n, gt_type, gt_dept in sources:
        files = []
        for ext in ('*.png', '*.jpg', '*.jpeg', '*.tif', '*.tiff'):
            files.extend(Path(folder).rglob(ext))
        _rng.shuffle(files)
        loaded = 0
        for fpath in files:
            if loaded >= n:
                break
            try:
                img = Image.open(fpath).convert("RGB")
                doc_id = f"{prefix}-{loaded:04d}"
                imgs.append(img)
                ids.append(doc_id)
                gt_map[doc_id] = {"document_type": gt_type, "routing_department": gt_dept}
                loaded += 1
            except Exception:
                continue
        print(f"  [ok] {Path(folder).name:<35}: {loaded} docs -> GT={gt_type}")
    # shuffle all together
    combined = list(zip(imgs, ids))
    _rng.shuffle(combined)
    imgs, ids = zip(*combined) if combined else ([], [])
    print(f"\nTotal: {len(imgs)} documents, {len(gt_map)} with GT")
    return list(imgs), list(ids), gt_map


def load_hf_dataset(name, n, split="test", image_field="image", id_field="id"):
    """Load n images + IDs from a HuggingFace dataset. Returns (subset, images, ids)."""
    from datasets import load_dataset
    subset = load_dataset(name, split=f"{split}[:{n}]")
    images = [d[image_field] for d in subset]
    ids = [d.get(id_field, i) for i, d in enumerate(subset)]
    print(f"Loaded {len(images)} images from {name}")
    return subset, images, ids


def load_hf_mix(sources, n_total):
    """Load images from multiple sources (HF datasets or local folders).

    sources : list of tuples, each either:
        HF:    (hf_name, split, fraction, id_prefix[, image_field])
        Local: (local_path, split_or_None, fraction, id_prefix)
               Detected when Path(source[0]).is_dir().
               Recursively globs *.png / *.jpg / *.jpeg, random-samples n.
    n_total : total docs to return across all sources.
    Returns : (imgs, ids)
    """
    import random as _rng
    from datasets import load_dataset as _load

    imgs, ids = [], []
    for source in sources:
        ds_name, split, fraction, prefix = source[:4]
        image_field = source[4] if len(source) > 4 else "image"

        n = min(max(1, round(n_total * fraction)), n_total - len(imgs))
        if n <= 0:
            break

        # ── Local directory ───────────────────────────────────────────────
        if Path(ds_name).is_dir():
            try:
                files = []
                for ext in ('*.png', '*.jpg', '*.jpeg'):
                    files.extend(Path(ds_name).rglob(ext))
                _rng.shuffle(files)
                loaded = 0
                for f in files:
                    if loaded >= n:
                        break
                    try:
                        img = Image.open(f).convert("RGB")
                        if img.size[0] < 10 or img.size[1] < 10:
                            continue
                        imgs.append(img)
                        ids.append(f"{prefix}-{loaded:04d}")
                        loaded += 1
                    except Exception:
                        continue
                print(f"  [ok] {Path(ds_name).name:<30}: {loaded} docs (local)")
            except Exception as e:
                print(f"  [warn] {Path(ds_name).name:<30}: skipped ({e})")
            continue

        # ── HF dataset ────────────────────────────────────────────────────
        try:
            ds = _load(ds_name, split=f"{split}[:{n}]")
            for i, row in enumerate(ds):
                imgs.append(row[image_field])
                ids.append(f"{prefix}-{i:04d}")
            print(f"  [ok] {ds_name.split('/')[-1]:<30}: {len(ds)} docs")
        except Exception as e:
            print(f"  [warn] {ds_name.split('/')[-1]:<30}: skipped ({e})")

    return imgs[:n_total], ids[:n_total]


def load_medical_mix(n_total=100, seed=42, hw_frac=0.10, omni_frac=0.45,
                     dataset_root=None):
    """Load mixed medical dataset: handwritten forms + OmniMedVQA + MedXpertQA.

    Returns (images, ids, doc_types, gt_list) — ready for extraction.
    """
    import random as _rng
    from collections import defaultdict, Counter

    _rng.seed(seed)
    root = Path(dataset_root) if dataset_root else Path(__file__).parent.parent / "dataset"

    n_hw   = max(1, round(n_total * hw_frac))
    n_omni = round(n_total * omni_frac)
    n_mxqa = n_total - n_hw - n_omni

    all_images, all_ids, doc_types, all_gt = [], [], [], []

    # ── OmniMedVQA GT lookup ─────────────────────────────────────────────
    omni_gt_lookup = {}
    qa_dir = root / "OmniMedVQA" / "QA_information" / "Open-access"
    omni_root = root / "OmniMedVQA" / "Images"
    if qa_dir.exists():
        for qa_file in qa_dir.glob("*.json"):
            try:
                import json as _json
                for entry in _json.loads(qa_file.read_text()):
                    ip = entry.get("image_path", "")
                    parts = ip.split("/")
                    source = parts[1] if len(parts) >= 3 else ""
                    omni_gt_lookup[(source, parts[-1])] = {
                        k: entry.get(k, "") for k in
                        ("dataset", "modality_type", "question_type",
                         "question", "gt_answer",
                         "option_A", "option_B", "option_C", "option_D")
                    }
            except Exception:
                pass

    # ── Part 1: Handwritten forms ────────────────────────────────────────
    hw_folder = root / "handwriting-ocr-data"
    hw_files = sorted(hw_folder.glob("*.png")) + sorted(hw_folder.glob("*.jpg"))
    for idx, path in enumerate(_rng.sample(hw_files, min(n_hw, len(hw_files)))):
        try:
            all_images.append(Image.open(path).convert("RGB"))
            all_ids.append(f"HW-{idx:04d}")
            doc_types.append("handwritten_form")
            all_gt.append({"source": "handwritten_form", "filename": path.name})
        except Exception:
            pass

    # ── Part 2: OmniMedVQA (stratified by source) ───────────────────────
    by_source = defaultdict(list)
    for ext in ("*.png", "*.jpg"):
        for p in omni_root.rglob(ext):
            by_source[p.relative_to(omni_root).parts[0]].append(p)
    per_src = max(1, (n_omni // max(len(by_source), 1)) + 1)
    candidates = []
    for files in by_source.values():
        candidates.extend(_rng.sample(files, min(per_src, len(files))))
    _rng.shuffle(candidates)

    loaded = 0
    for path in candidates:
        if loaded >= n_omni:
            break
        try:
            img = Image.open(path).convert("RGB")
            if img.size[0] < 10 or img.size[1] < 10:
                continue
            all_images.append(img)
            all_ids.append(f"OMNI-{loaded:04d}")
            top = path.relative_to(omni_root).parts[0]
            doc_types.append(top)
            all_gt.append(omni_gt_lookup.get((top, path.name),
                                             {"source": top, "filename": path.name}))
            loaded += 1
        except Exception:
            continue

    # ── Part 3: MedXpertQA (streamed from HF) ───────────────────────────
    try:
        from datasets import load_dataset as _hf_load
        print(f"  Streaming MedXpertQA ({n_mxqa} images)...")
        ds = _hf_load("Voxel51/MedXpertQA", split="train", streaming=True)
        loaded = 0
        for row in ds:
            if loaded >= n_mxqa:
                break
            try:
                img = row["image"].convert("RGB")
                if img.size[0] < 10 or img.size[1] < 10:
                    continue
                all_images.append(img)
                all_ids.append(f"MXQA-{loaded:04d}")
                doc_types.append("medxpert_qa")
                all_gt.append({"source": "medxpert_qa"})
                loaded += 1
            except Exception:
                continue
    except Exception as e:
        print(f"  [warn] MedXpertQA unavailable: {e}")

    # ── Shuffle & report ─────────────────────────────────────────────────
    combined = list(zip(all_images, all_ids, doc_types, all_gt))
    _rng.shuffle(combined)
    if combined:
        all_images, all_ids, doc_types, all_gt = map(list, zip(*combined))
    else:
        all_images, all_ids, doc_types, all_gt = [], [], [], []

    counts = Counter(
        "Handwritten" if i.startswith("HW") else
        "OmniMedVQA"  if i.startswith("OMNI") else "MedXpertQA"
        for i in all_ids)
    gt_qa = sum(1 for g in all_gt if g.get("question"))
    print(f"Loaded {len(all_images)}/{n_total}: "
          + ", ".join(f"{k} {v}" for k, v in counts.items())
          + (f" ({gt_qa} with QA GT)" if gt_qa else ""))

    return all_images, all_ids, doc_types, all_gt


def load_rag_intro_dataset(dataset_root=None):
    """Load curated dataset for RAG intro: ~235 docs across 13 classes.

    Returns (images, ids, doc_types).
    """
    root = Path(dataset_root) if dataset_root else Path(__file__).parent.parent

    all_images, all_ids, doc_types = [], [], []

    def _load_glob(directory, patterns, n, doc_type, id_prefix):
        files = []
        for pat in patterns:
            files.extend(sorted(directory.rglob(pat)))
        for p in files[:n]:
            try:
                all_images.append(Image.open(p).convert("RGB"))
                all_ids.append(f"{id_prefix}-{p.stem}")
                doc_types.append(doc_type)
            except Exception:
                pass

    # 1. Clinical notes — 20 mtsamples (all grouped as one class)
    mts_dir = root / "cache" / "chart_samples" / "mtsamples"
    if mts_dir.exists():
        import json as _json
        mts_meta = _json.loads((mts_dir / "meta.json").read_text())
        for entry in mts_meta[:20]:
            try:
                img = Image.open(mts_dir / entry["file"]).convert("RGB")
                all_images.append(img)
                all_ids.append(f"MTS-{entry['file'].split('.')[0]}")
                doc_types.append("clinical_note")
            except Exception:
                pass

    # 2. Handwritten prescriptions (30)
    hw_dir = root / "dataset" / "handwriting-ocr-data"
    _load_glob(hw_dir, ["*.jpg", "*.png"], 30, "prescription", "HW")

    # 3. Curated medical imaging (8 sources, 20 each = 160)
    omni_root = root / "dataset" / "OmniMedVQA" / "Images"
    curated_sources = [
        ("Chest X-Ray PA",       "chest_xray",   20),
        ("Fitzpatrick 17k",      "skin_lesion",  20),
        ("Diabetic Retinopathy", "fundus",        20),
        ("Blood Cell",           "blood_smear",   20),
        ("Mura",                 "msk_xray",      20),
        ("Chest CT Scan",        "ct_scan",       15),
        ("Retinal OCT-C8",       "retinal_oct",   15),
        ("Knee Osteoarthritis",  "knee_xray",     15),
    ]
    for source_name, doc_type, n in curated_sources:
        src_dir = omni_root / source_name
        if not src_dir.exists():
            continue
        _load_glob(src_dir, ["*.png", "*.jpg", "*.jpeg"], n, doc_type,
                   f"OMNI-{source_name[:8].replace(' ','-')}")

    # 4. Consent forms (20)
    consent_dir = root / "cache" / "chart_samples" / "consent_forms"
    _load_glob(consent_dir, ["*.png", "*.jpg"], 20, "consent_form", "FORM")

    # 5. OMR scanned forms (20)
    omr_dir = root / "cache" / "chart_samples" / "omr_scanned"
    _load_glob(omr_dir, ["*.png", "*.jpg"], 20, "omr_form", "OMR")

    # 6. ECG samples (20)
    ecg_dir = root / "cache" / "ecg_samples" / "genecg"
    if ecg_dir.exists():
        _load_glob(ecg_dir, ["*.png", "*.jpg"], 20, "ecg", "ECG")

    from collections import Counter
    counts = Counter(doc_types)
    print(f"Loaded {len(all_images)} docs across {len(counts)} classes: "
          + ", ".join(f"{v} {k}" for k, v in counts.most_common()))

    # Validate: every class must have >= 15 docs
    for cls, cnt in counts.items():
        if cnt < 15:
            print(f"[warn] '{cls}' has only {cnt} docs (minimum 15)")

    return all_images, all_ids, doc_types




def build_derm_index(isic_with_gt, isic_by_class, classes_ordered, *,
                     nb_name, use_cache, index_per_class=60):
    """Build FAISS index for derm RAG: hold out 10 query images, index the rest."""
    import random, faiss
    import numpy as np
    from tqdm.notebook import tqdm
    from PIL import Image
    from utils.core import embed_images_batch, has_nb_cache, load_nb_cache, save_nb_cache

    QUERY_CLS = classes_ordered  # 1 held-out per class (all 8)
    held_paths, held_gt, used = [], [], set()
    for cls in QUERY_CLS:
        for p in random.sample([p for p in isic_by_class[cls] if p not in used], min(1, len([p for p in isic_by_class[cls] if p not in used]))):
            held_paths.append(p); held_gt.append(cls); used.add(p)

    idx_paths, idx_gt = [], []
    for cls in classes_ordered:
        pool = [p for p, g in isic_with_gt if g == cls and p not in used]
        chosen = random.sample(pool, min(index_per_class, len(pool)))
        idx_paths.extend(chosen); idx_gt.extend([cls] * len(chosen))

    imgs = [Image.open(p).convert("RGB") for p in tqdm(idx_paths, desc="Loading")]

    if use_cache and has_nb_cache(nb_name, "image_embeddings"):
        embs = np.array(load_nb_cache(nb_name, "image_embeddings")["embeddings"], dtype=np.float32)
    else:
        embs = embed_images_batch(imgs, batch_size=4)
        save_nb_cache(nb_name, "image_embeddings", {"embeddings": embs.tolist()})

    ix = faiss.IndexFlatIP(embs.shape[1])
    ix.add(embs)
    print(f"Index: {ix.ntotal} vectors, {embs.shape[1]}d | Held-out: {len(held_paths)}")
    return held_paths, held_gt, used, idx_paths, idx_gt, imgs, ix
