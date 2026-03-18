#!/usr/bin/env python3
"""
Download all datasets required by json-ocr-demo notebooks.

Usage:
    python setup/download_datasets.py              # download everything
    python setup/download_datasets.py --nb 7       # only NB7 datasets
    python setup/download_datasets.py --list       # show what would be downloaded

Datasets are downloaded to:
    dataset/     — large local datasets (OmniMedVQA, pdf-deid, handwriting, MIDV-2020)
    cache/       — pre-processed subsets (ECG, chart samples, PTB-XL+)
    cache/hf/    — HuggingFace dataset cache (auto-managed by `datasets` library)

Some datasets are JSL-proprietary or synthetically generated and cannot be
auto-downloaded. These are marked [MANUAL] and instructions are printed.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Project root = parent of setup/
ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT / "dataset"
CACHE_DIR = ROOT / "cache"
HF_CACHE = CACHE_DIR / "hf"


# ── Dataset definitions ──────────────────────────────────────────────────────

DATASETS = {
    # ── NB1: Visual DEID ──────────────────────────────────────────────────
    "pdf-deid-dataset": {
        "nb": [1],
        "path": DATASET_DIR / "pdf-deid-dataset",
        "source": "github",
        "url": "https://github.com/JohnSnowLabs/pdf-deid-dataset.git",
        "description": "50 synthetic medical PDFs with PHI ground truth",
    },
    "handwriting-ocr-data": {
        "nb": [1, 3],
        "path": DATASET_DIR / "handwriting-ocr-data",
        "source": "manual",
        "description": "129 synthetic handwritten prescription images [JSL internal]",
    },

    # ── NB2: Document Mining ──────────────────────────────────────────────
    "ocr-benchmark": {
        "nb": [2],
        "path": HF_CACHE,
        "source": "hf",
        "hf_id": "getomni-ai/ocr-benchmark",
        "description": "1K diverse document images for OCR benchmarking",
    },

    # ── NB3: Medical RAG ──────────────────────────────────────────────────
    "OmniMedVQA": {
        "nb": [3, 4, 5, 6],
        "path": DATASET_DIR / "OmniMedVQA",
        "source": "hf_zip",
        "hf_repo": "foreverbeliever/OmniMedVQA",
        "hf_file": "OmniMedVQA.zip",
        "description": "118K+ medical images across 42 modalities (~10GB zip from HF)",
    },
    "MedXpertQA": {
        "nb": [3],
        "path": HF_CACHE,
        "source": "hf",
        "hf_id": "Voxel51/MedXpertQA",
        "description": "Medical QA with images (streamed at runtime)",
    },
    "chart-samples-mtsamples": {
        "nb": [3],
        "path": CACHE_DIR / "chart_samples" / "mtsamples",
        "source": "hf",
        "hf_id": "gamino/wiki_medical_terms",
        "description": "Medical transcriptions rendered as document images",
        "postprocess": "render_mtsamples",
    },
    "chart-samples-omr": {
        "nb": [3],
        "path": CACHE_DIR / "chart_samples" / "omr_scanned",
        "source": "hf",
        "hf_id": "saurabh1896/OMR-scanned-documents",
        "description": "Scanned patient intake/consent/health assessment forms",
    },
    "chart-samples-consent": {
        "nb": [3],
        "path": CACHE_DIR / "chart_samples" / "consent_forms",
        "source": "manual",
        "description": "20 synthetic consent forms [generated locally]",
    },

    # ── NB4: Dermatology RAG ──────────────────────────────────────────────
    "HAM10000": {
        "nb": [4],
        "path": HF_CACHE,
        "source": "hf",
        "hf_id": "marmal88/skin_cancer",
        "description": "10K skin lesion dermoscopy images (7 classes)",
    },

    # ── NB7: ECG Waveform ────────────────────────────────────────────────
    "GenECG": {
        "nb": [7],
        "path": CACHE_DIR / "ecg_samples" / "genecg",
        "source": "hf",
        "hf_id": "edcci/GenECG",
        "description": "Synthetic 12-lead ECG paper tracings (43K images, CC-BY-4.0)",
        "postprocess": "subset_genecg",
    },
    "ECGBench": {
        "nb": [7],
        "path": CACHE_DIR / "ecg_samples" / "ecgbench_extended",
        "source": "hf",
        "hf_id": "PULSE-ECG/ECGBench",
        "hf_config": "ptb-test",
        "description": "11K ECG images with expert QA pairs",
        "postprocess": "subset_ecgbench",
    },
    "PTB-XL-plus": {
        "nb": [7],
        "path": CACHE_DIR / "ptbxl_plus",
        "source": "manual",
        "url": "https://physionet.org/content/ptb-xl/1.0.3/",
        "description": "PTB-XL+ 12SL features CSV (requires PhysioNet credentialed access). "
                       "Sign up at physionet.org, request access, then: "
                       "wget -r -N -c -np -nH --cut-dirs=3 -P cache/ptbxl_plus/ "
                       "https://physionet.org/files/ptb-xl/1.0.3/output/",
    },

    # ── NB8: KYC ─────────────────────────────────────────────────────────
    "MIDV-2020": {
        "nb": [8],
        "path": DATASET_DIR / "MIDV2020",
        "source": "manual",
        "url": "https://doi.org/10.18287/2412-6179-CO-756",
        "description": "3K identity document images (10 countries). "
                       "Download from http://l3i-share.univ-lr.fr/MIDV2020/midv2020.html",
    },

    # ── NB9: Invoice/Expense (all HF, auto-downloaded by load_hf_mix) ───
    "SROIE-2019": {
        "nb": [9],
        "path": HF_CACHE,
        "source": "hf",
        "hf_id": "rth/sroie-2019-v2",
        "description": "973 Malaysian/English receipts with NER GT",
    },
    "invoices-receipts-ocr": {
        "nb": [9],
        "path": HF_CACHE,
        "source": "hf",
        "hf_id": "mychen76/invoices-and-receipts_ocr_v1",
        "description": "2.2K invoices with OCR bboxes",
    },
    "multi-doc-classification": {
        "nb": [9],
        "path": HF_CACHE,
        "source": "hf",
        "hf_id": "rikeshVertex/invoice-receipt-cheque-bankstatement-dataset",
        "description": "4.2K mixed docs (invoice/receipt/cheque/bank statement)",
    },
    "hq-invoices": {
        "nb": [9],
        "path": HF_CACHE,
        "source": "hf",
        "hf_id": "Voxel51/high-quality-invoice-images-for-ocr",
        "description": "8K synthetic B2B invoices",
    },
    "scanned-receipts": {
        "nb": [9],
        "path": HF_CACHE,
        "source": "hf",
        "hf_id": "Voxel51/scanned_receipts",
        "description": "715 scanned receipts",
    },
    "korean-receipts": {
        "nb": [9],
        "path": HF_CACHE,
        "source": "hf",
        "hf_id": "Kratos-AI/Korean_Receipts_Dataset",
        "description": "20 Korean receipt images",
    },
    "CORD-v2": {
        "nb": [9],
        "path": HF_CACHE,
        "source": "hf",
        "hf_id": "naver-clova-ix/cord-v2",
        "description": "1K Korean receipts + invoices with full GT (CC-BY-4.0)",
    },
    "tezba-invoices": {
        "nb": [9],
        "path": HF_CACHE,
        "source": "hf",
        "hf_id": "gurudal/tezba-invoice-images",
        "description": "51K invoice images (diversity, no annotations)",
    },
    "mall-receipts": {
        "nb": [9],
        "path": HF_CACHE,
        "source": "hf",
        "hf_id": "CC1984/mall_receipt_extraction_dataset",
        "description": "1.8K Chinese receipts (ZARA, UNIQLO, WeChat Pay)",
    },
    "bank-statements": {
        "nb": [9],
        "path": HF_CACHE,
        "source": "hf",
        "hf_id": "tusharshah2006/bank_statements_transactions",
        "description": "149 scanned Indian bank statements with row-level GT",
    },
}


# ── Download functions ───────────────────────────────────────────────────────

def download_hf(ds_info):
    """Pre-cache a HuggingFace dataset."""
    hf_id = ds_info["hf_id"]
    config = ds_info.get("hf_config")
    print(f"  Downloading {hf_id} via HuggingFace datasets...")
    try:
        from datasets import load_dataset
        kwargs = {"cache_dir": str(HF_CACHE)}
        if config:
            kwargs["name"] = config
        # Just load to trigger caching — use first split available
        ds = load_dataset(hf_id, split="test", **kwargs)
        print(f"  [ok] {hf_id}: {len(ds)} rows cached")
        return True
    except Exception as e:
        # Try train split
        try:
            ds = load_dataset(hf_id, split="train", **kwargs)
            print(f"  [ok] {hf_id}: {len(ds)} rows cached")
            return True
        except Exception:
            pass
        print(f"  [warn] {hf_id}: {e}")
        return False


def download_hf_zip(ds_info):
    """Download a single zip file from a HuggingFace dataset repo and extract it."""
    path = ds_info["path"]
    repo = ds_info["hf_repo"]
    filename = ds_info["hf_file"]
    if path.exists() and any(path.iterdir()):
        print(f"  [skip] {path.name} already exists ({sum(1 for _ in path.rglob('*') if _.is_file())} files)")
        return True
    print(f"  Downloading {repo}/{filename} via huggingface_hub...")
    try:
        from huggingface_hub import hf_hub_download
        zip_path = hf_hub_download(
            repo_id=repo, filename=filename,
            repo_type="dataset", cache_dir=str(HF_CACHE),
        )
        print(f"  Extracting to {path}...")
        import zipfile
        path.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Extract — handle nested root dir (zip may contain OmniMedVQA/ prefix)
            members = zf.namelist()
            # Check if all files share a common prefix dir
            prefixes = set(m.split('/')[0] for m in members if '/' in m)
            if len(prefixes) == 1:
                prefix = prefixes.pop() + '/'
                for member in members:
                    if member.startswith(prefix) and member != prefix:
                        target = path / member[len(prefix):]
                        if member.endswith('/'):
                            target.mkdir(parents=True, exist_ok=True)
                        else:
                            target.parent.mkdir(parents=True, exist_ok=True)
                            with zf.open(member) as src, open(target, 'wb') as dst:
                                shutil.copyfileobj(src, dst)
            else:
                zf.extractall(path)
        n_files = sum(1 for _ in path.rglob('*') if _.is_file())
        print(f"  [ok] Extracted {n_files} files to {path}")
        return True
    except Exception as e:
        print(f"  [fail] {e}")
        return False


def download_github(ds_info):
    """Clone a GitHub repo into the dataset directory."""
    path = ds_info["path"]
    url = ds_info["url"]
    if path.exists() and any(path.iterdir()):
        print(f"  [skip] {path.name} already exists")
        return True
    print(f"  Cloning {url}...")
    try:
        subprocess.run(["git", "clone", "--depth=1", url, str(path)],
                       check=True, capture_output=True, text=True)
        print(f"  [ok] Cloned to {path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  [fail] git clone: {e.stderr.strip()}")
        return False


def show_manual(ds_info, name):
    """Print instructions for manual download."""
    path = ds_info["path"]
    if path.exists() and any(path.iterdir()):
        print(f"  [skip] {path.name} already exists ({sum(1 for _ in path.rglob('*') if _.is_file())} files)")
        return True
    url = ds_info.get("url", "N/A")
    print(f"  [MANUAL] {name}")
    print(f"           Target: {path}")
    print(f"           Source: {url}")
    print(f"           {ds_info['description']}")
    return False


def check_exists(ds_info):
    """Check if a dataset already exists on disk."""
    path = ds_info["path"]
    if ds_info["source"] == "hf":
        # HF datasets are auto-downloaded at runtime, just check cache exists
        return True
    if path.exists() and path.is_dir() and any(path.iterdir()):
        return True
    return False


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Download datasets for json-ocr-demo")
    parser.add_argument("--nb", type=int, nargs="+", help="Only download for specific notebook(s)")
    parser.add_argument("--list", action="store_true", help="List datasets without downloading")
    parser.add_argument("--skip-hf", action="store_true", help="Skip HuggingFace downloads (they auto-download at runtime)")
    args = parser.parse_args()

    os.chdir(ROOT)
    DATASET_DIR.mkdir(exist_ok=True)
    CACHE_DIR.mkdir(exist_ok=True)
    HF_CACHE.mkdir(exist_ok=True)

    # Filter by notebook if requested
    datasets = DATASETS
    if args.nb:
        datasets = {k: v for k, v in DATASETS.items()
                    if any(n in v["nb"] for n in args.nb)}

    print(f"Datasets: {len(datasets)} total\n")

    status = {"ok": 0, "skip": 0, "manual": 0, "fail": 0}

    for name, info in datasets.items():
        exists = check_exists(info)
        nbs = ", ".join(f"NB{n}" for n in info["nb"])
        tag = f"[{info['source']}]"

        if args.list:
            marker = "OK" if exists else "MISSING"
            print(f"  [{marker}] {name:30s} {tag:10s} {nbs:20s} {info['description'][:60]}")
            continue

        print(f"\n{name} ({nbs}):")

        if info["source"] == "hf":
            if args.skip_hf:
                print(f"  [skip] HF datasets auto-download at runtime")
                status["skip"] += 1
            elif download_hf(info):
                status["ok"] += 1
            else:
                status["fail"] += 1

        elif info["source"] == "hf_zip":
            if args.skip_hf:
                print(f"  [skip] --skip-hf")
                status["skip"] += 1
            elif download_hf_zip(info):
                status["ok"] += 1
            else:
                status["fail"] += 1

        elif info["source"] == "github":
            if download_github(info):
                status["ok"] += 1
            else:
                status["fail"] += 1

        elif info["source"] == "manual":
            if show_manual(info, name):
                status["skip"] += 1
            else:
                status["manual"] += 1

        elif info["source"] == "physionet":
            if info["path"].exists() and any(info["path"].iterdir()):
                print(f"  [skip] {info['path'].name} already exists")
                status["skip"] += 1
            else:
                show_manual(info, name)
                status["manual"] += 1

    if not args.list:
        print(f"\n{'='*60}")
        print(f"Done: {status['ok']} downloaded, {status['skip']} skipped, "
              f"{status['manual']} need manual download, {status['fail']} failed")


if __name__ == "__main__":
    main()
