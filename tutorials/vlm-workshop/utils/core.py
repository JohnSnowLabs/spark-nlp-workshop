"""
Demo utilities for JSON-OCR notebook.
Contains all HTML generation and styling functions for clean notebook code.
Dark mode optimized with compelling use-case demonstrations.
"""

from IPython.display import display, HTML
from PIL import Image
import json
import time
import requests
import numpy as np
from pathlib import Path
from io import BytesIO
import base64
import uuid

# Re-export viewer/HTML functions from utils.viewers
from utils.viewers import *  # noqa: F401,F403
from utils.ecg import *  # noqa: F401,F403
from utils.plots import *  # noqa: F401,F403
from utils.datasets import *  # noqa: F401,F403
from utils.tax import *  # noqa: F401,F403

# ============================================================================
# SHARED SCHEMA — base fields common to all RAG notebooks
# ============================================================================

BASE_MEDICAL_FIELDS = {
    "diagnosis":          {"type": "string"},
    "findings":           {"type": "array", "items": {"type": "string"}, "maxItems": 6},
    "description":        {"type": "string"},
    "recommended_action": {"type": "string"},
    "tags":               {"type": "array", "items": {"type": "string"}, "maxItems": 8},
}


# ============================================================================
# NB CACHE — per-notebook, per-model result caching
# Storage: nb-cache/<nb-name>/<model>/data/<key>.json
# Legacy:  nb-cache/<nb-name>/data/<key>.json  (fallback read-only)
#
# Usage:
#   set_cache_model("jsl-medical-vl-30b")    # call once in NB config cell
#   save_nb_cache(NB_NAME, "results", data) # → nb-cache/<nb>/jsl-medical-vl-30b/data/results.json
#   load_nb_cache(NB_NAME, "results")       # reads model-specific, falls back to legacy
# ============================================================================

_CACHE_ROOT = Path(__file__).parent.parent / "nb-cache"
_active_model = None  # set via set_cache_model()
_query_cache_nb = None   # set via set_query_cache() for offline query embedding


def set_cache_model(model_name):
    """Set the active model for cache namespacing. Call once per NB."""
    global _active_model
    _active_model = model_name


def get_cache_model():
    """Return the active cache model name."""
    return _active_model


def set_query_cache(nb_name):
    """Enable query embedding cache for this notebook.

    Once set, embed_image/embed_text/embed_clinical_text will automatically
    cache results keyed by input content, allowing notebooks to render
    offline without embedding servers.
    """
    global _query_cache_nb
    _query_cache_nb = nb_name


def _load_query_cache(nb_name):
    """Load query embedding cache dict, or empty dict if missing."""
    if nb_name and has_nb_cache(nb_name, "query_embed_cache"):
        return load_nb_cache(nb_name, "query_embed_cache")
    return {}


def _save_query_cache(nb_name, cache):
    """Save query embedding cache dict."""
    if nb_name:
        save_nb_cache(nb_name, "query_embed_cache", cache)


def _cache_path(nb_name, key, model=None):
    """Build cache path: nb-cache/<nb>/<model>/data/<key>.json."""
    m = model or _active_model
    if m:
        return _CACHE_ROOT / nb_name / m / "data" / f"{key}.json"
    # Legacy flat path (no model set)
    return _CACHE_ROOT / nb_name / "data" / f"{key}.json"


def _legacy_cache_path(nb_name, key):
    """Old flat path for backward-compat reads."""
    return _CACHE_ROOT / nb_name / "data" / f"{key}.json"


def save_nb_cache(nb_name, key, data, *, model=None):
    """Save data to nb-cache/<nb_name>/<model>/data/<key>.json."""
    path = _cache_path(nb_name, key, model)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[cache] Cached {key} -> {path}")


def load_nb_cache(nb_name, key, *, model=None):
    """Load from cache. Tries model-specific path first, then legacy flat path."""
    path = _cache_path(nb_name, key, model)
    if path.exists():
        with open(path) as f:
            data = json.load(f)
        print(f"[cache] Loaded {key} from cache ({path})")
        return data
    # Fallback: legacy flat path (pre-model-aware cache)
    legacy = _legacy_cache_path(nb_name, key)
    if legacy != path and legacy.exists():
        with open(legacy) as f:
            data = json.load(f)
        print(f"[cache] Loaded {key} from legacy cache ({legacy})")
        return data
    return None


def has_nb_cache(nb_name, key, *, model=None):
    """Check if cache exists (model-specific or legacy)."""
    path = _cache_path(nb_name, key, model)
    if path.exists():
        return True
    legacy = _legacy_cache_path(nb_name, key)
    return legacy != path and legacy.exists()


def list_cached_models(nb_name):
    """List all models that have cached results for a notebook."""
    nb_dir = _CACHE_ROOT / nb_name
    if not nb_dir.exists():
        return []
    return sorted([
        d.name for d in nb_dir.iterdir()
        if d.is_dir() and d.name != "data" and (d / "data").exists()
    ])


def check_server(base_url, model_name, *, api_key=None):
    """Check vLLM server is reachable and requested model is available.
    Returns the confirmed model name (auto-selects first available if requested not found)."""
    from utils.config import JSL_VISION_MODEL, JSL_VISION_BACKEND, JSL_VISION_BASE_URL
    from utils.config import OPENROUTER_BASE_URL, OPENROUTER_API_KEY

    # JSL Vision alias — verify backend is available, display as local
    if model_name == JSL_VISION_MODEL:
        try:
            headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
            r = requests.get(f"{OPENROUTER_BASE_URL}/models", headers=headers, timeout=10)
            r.raise_for_status()
            available = [m.get('id') for m in r.json().get('data', [])]
            if JSL_VISION_BACKEND in available:
                print(f"\u2705 vLLM server ready \u2014 model '{JSL_VISION_MODEL}' confirmed on {JSL_VISION_BASE_URL}")
                return model_name
            else:
                raise SystemExit(f"[error] Model '{JSL_VISION_MODEL}' not available")
        except requests.exceptions.ConnectionError:
            raise SystemExit(f"[error] Cannot connect to server for {JSL_VISION_MODEL}")
        except SystemExit:
            raise
        except Exception as e:
            raise SystemExit(f"[error] Server error: {e}")

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    try:
        r = requests.get(f"{base_url}/models", headers=headers, timeout=10)
        r.raise_for_status()
        available = [m.get('id') for m in r.json().get('data', [])]
        # OpenRouter returns thousands of models; just verify ours is in the list
        is_cloud = "openrouter" in base_url.lower()
        if is_cloud:
            if model_name in available:
                print(f"\u2705 vLLM server ready \u2014 model '{model_name}' confirmed")
                return model_name
            else:
                raise SystemExit(f"[error] Model '{model_name}' not found")
        if not available:
            raise SystemExit("[error] vLLM server has no models loaded")
        if model_name in available:
            print(f"\u2705 vLLM server ready \u2014 model '{model_name}' confirmed on {base_url}")
            return model_name
        else:
            print(f"[warn] Model '{model_name}' not found. Available: {available}")
            fallback = available[0]
            print(f"   -> Auto-selected: {fallback}")
            return fallback
    except requests.exceptions.ConnectionError:
        raise SystemExit(f"[error] Cannot connect to server at {base_url}")
    except SystemExit:
        raise
    except Exception as e:
        raise SystemExit(f"[error] Server error: {e}")


# ============================================================================
# SPARK NLP HEALTHCARE — NER / RESOLUTION / CLASSIFICATION
# ============================================================================

try:
    from utils.config import SPARKNLP_BASE_URL as SPARKNLP_URL
except ImportError:
    SPARKNLP_URL = "http://localhost:9470"


def check_sparknlp(url=None):
    """Check Spark NLP HC server is reachable. Returns loaded model info."""
    url = url or SPARKNLP_URL
    try:
        r = requests.get(f"{url}/health", timeout=5)
        r.raise_for_status()
        info = r.json()
        ner_models = info.get("ner_models", [])
        resolvers = info.get("resolvers", [])
        print(f"[ok] Spark NLP HC ready -- {len(ner_models)} NER models, {len(resolvers)} resolvers on {url}")
        return info
    except requests.exceptions.ConnectionError:
        print(f"[warn] Spark NLP HC not reachable at {url} -- NLP enrichment will be skipped")
        return None
    except Exception as e:
        print(f"[warn] Spark NLP HC error: {e} -- NLP enrichment will be skipped")
        return None


def nlp_ner(text, model="jsl", url=None):
    """Run NER on text. model: jsl, clinical, posology, radiology, anatomy, deid."""
    url = url or SPARKNLP_URL
    if not text or not text.strip():
        return []
    r = requests.post(f"{url}/ner/{model}", json={"text": text}, timeout=30)
    r.raise_for_status()
    return r.json().get("entities", [])


def nlp_resolve(text, system="icd10", url=None):
    """Resolve entities to codes. system: icd10, snomed, rxnorm, loinc, icdo, umls."""
    url = url or SPARKNLP_URL
    if not text or not text.strip():
        return {"resolutions": [], "ner_entities": []}
    r = requests.post(f"{url}/resolve/{system}", json={"text": text}, timeout=30)
    r.raise_for_status()
    return r.json()


def nlp_classify_sections(text, url=None):
    """Classify clinical text into section types."""
    url = url or SPARKNLP_URL
    if not text or not text.strip():
        return {}
    r = requests.post(f"{url}/classify/sections", json={"text": text}, timeout=30)
    r.raise_for_status()
    return r.json()


def nlp_relations(text, url=None):
    """Extract clinical relations (Treatment↔Problem, Test↔Problem)."""
    url = url or SPARKNLP_URL
    if not text or not text.strip():
        return []
    r = requests.post(f"{url}/relation", json={"text": text}, timeout=30)
    r.raise_for_status()
    return r.json().get("relations", [])


def _collect_doc_text(doc):
    """Collect text from doc: prefer OCR text when available, else VLM fields."""
    # OCR text is richer for text-heavy docs (clinical notes, Rx, forms)
    if doc.get("_ocr_text"):
        return doc["_ocr_text"]
    text_parts = []
    for field in ("summary", "case_summary", "patient_summary", "chief_complaint"):
        if doc.get(field):
            text_parts.append(doc[field])
    for field in ("diagnoses", "findings", "imaging_findings"):
        val = doc.get(field)
        if val and isinstance(val, list):
            text_parts.append(_safe_join(val))
    meds = doc.get("medications") or doc.get("current_medications")
    if meds and isinstance(meds, list):
        text_parts.append(_safe_join(meds))
    return " . ".join(t for t in text_parts if t.strip())


def _link_code_entities(codes, entities):
    """Map resolver chunk indices to entity names for display."""
    for sys_codes in (codes.values() if isinstance(codes, dict) else [codes]):
        for c in sys_codes:
            idx = c.get("chunk")
            if idx is not None and str(idx).isdigit():
                ner_idx = int(idx)
                if ner_idx < len(entities):
                    c["ner_entity"] = entities[ner_idx].get("chunk", "")


def _apply_enrich_result(doc, result, do_relations=False):
    """Write /enrich result fields into a doc dict."""
    entities = result.get("entities", [])
    codes = result.get("codes", {})
    _link_code_entities(codes, entities)
    doc["_nlp_entities"] = entities
    doc["_nlp_codes"] = codes
    if do_relations:
        doc["_nlp_relations"] = result.get("relations", [])


def enrich_doc_nlp(doc, ner_models=("jsl",), resolve_systems=("icd10", "rxnorm", "snomed"),
                   do_relations=False, url=None):
    """
    Enrich a single extracted document with Spark NLP NER + entity resolution.
    Uses the combined /enrich endpoint (single HTTP call) for speed.
    Falls back to individual endpoints if /enrich is not available.
    """
    url = url or SPARKNLP_URL

    full_text = _collect_doc_text(doc)
    if not full_text.strip():
        return doc

    # Try combined /enrich endpoint first (single HTTP call vs 6+)
    try:
        r = requests.post(f"{url}/enrich", json={
            "text": full_text,
            "ner_models": list(ner_models),
            "resolve_systems": list(resolve_systems),
            "do_relations": do_relations,
        }, timeout=60)
        r.raise_for_status()
        _apply_enrich_result(doc, r.json(), do_relations)
        return doc
    except (requests.exceptions.HTTPError, KeyError):
        pass  # Fall back to individual endpoints

    # Fallback: individual endpoints
    all_entities = []
    for model in ner_models:
        try:
            entities = nlp_ner(full_text, model=model, url=url)
            for e in entities:
                e["_ner_model"] = model
            all_entities.extend(entities)
        except Exception:
            pass
    doc["_nlp_entities"] = all_entities

    all_codes = {}
    for system in resolve_systems:
        try:
            result = nlp_resolve(full_text, system=system, url=url)
            resolutions = result.get("resolutions", [])
            ner_ents = result.get("ner_entities", [])
            if resolutions:
                _link_code_entities({system: resolutions}, ner_ents)
                all_codes[system] = resolutions
        except Exception:
            pass
    doc["_nlp_codes"] = all_codes

    if do_relations:
        try:
            doc["_nlp_relations"] = nlp_relations(full_text, url=url)
        except Exception:
            doc["_nlp_relations"] = []

    return doc


def enrich_docs_nlp(docs, ner_models=("jsl",), resolve_systems=("icd10", "rxnorm", "snomed"),
                    do_relations=False, url=None, show_progress=True,
                    nb_name=None, use_cache=True):
    """
    Enrich extracted docs with NLP. Per-doc caching for resumability.
    Cached NLP results stored at nb-cache/<nb>/<model>/data/nlp/<doc_id>.json.
    """
    from tqdm.notebook import tqdm as _tqdm
    url = url or SPARKNLP_URL
    if not check_sparknlp(url):
        print("Skipping NLP enrichment (server not available)")
        return docs
    successful = [d for d in docs if d.get("_status") == "success"]
    if not successful:
        print("[warn] No successful docs to enrich")
        return docs

    # Per-doc NLP cache dir — always set up for writing, only read when use_cache
    cache_dir = None
    if nb_name:
        m = _active_model or "default"
        cache_dir = _CACHE_ROOT / nb_name / m / "data" / "nlp"
        cache_dir.mkdir(parents=True, exist_ok=True)
        n_cached_files = len(list(cache_dir.glob("*.json")))
        print(f"NLP cache: {cache_dir} ({n_cached_files} files, use_cache={use_cache})")

    cached, fresh, errors = 0, 0, 0
    print(f"Processing {len(successful)} docs...")
    iterator = successful

    for doc in iterator:
        doc_id = doc.get("doc_id", "unknown")

        # Check per-doc cache (only when use_cache is on)
        if use_cache and cache_dir:
            cache_file = cache_dir / f"{doc_id}.json"
            if cache_file.exists():
                try:
                    with open(cache_file) as f:
                        nlp_data = json.load(f)
                    doc["_nlp_entities"] = nlp_data.get("entities", [])
                    doc["_nlp_codes"] = nlp_data.get("codes", {})
                    if "relations" in nlp_data:
                        doc["_nlp_relations"] = nlp_data["relations"]
                    cached += 1
                    continue
                except Exception:
                    pass  # re-fetch if cache corrupt

        # Fetch from API
        try:
            enrich_doc_nlp(doc, ner_models=ner_models, resolve_systems=resolve_systems,
                          do_relations=do_relations, url=url)
            fresh += 1
            # Always save to per-doc cache
            if cache_dir:
                nlp_data = {"entities": doc.get("_nlp_entities", []),
                            "codes": doc.get("_nlp_codes", {})}
                if do_relations:
                    nlp_data["relations"] = doc.get("_nlp_relations", [])
                with open(cache_dir / f"{doc_id}.json", "w") as f:
                    json.dump(nlp_data, f)
        except Exception as e:
            doc["_nlp_error"] = str(e)
            errors += 1

    total = cached + fresh
    parts = []
    if cached:
        parts.append(f"{cached} cached")
    if fresh:
        parts.append(f"{fresh} fresh")
    if errors:
        parts.append(f"{errors} errors")
    print(f"[ok] NLP enrichment: {total}/{len(successful)} docs ({', '.join(parts)})")
    return docs


# ============================================================================
# IMAGE EMBEDDINGS (jsl_vision_embed_crossmodal_1.0) — port 9464
# ============================================================================

try:
    from utils.config import EMBED_BASE_URL
except ImportError:
    EMBED_BASE_URL = "http://localhost:9464"


def _query_cache_key(prefix, content):
    """Build a short deterministic cache key from content."""
    import hashlib
    if isinstance(content, str):
        h = hashlib.md5(content.encode()).hexdigest()[:12]
        # Keep first 40 chars of text for readability
        safe = content[:40].replace('"', '').replace('\n', ' ')
        return f"{prefix}__{safe}__{h}"
    # For images, hash the raw bytes
    from io import BytesIO
    buf = BytesIO()
    content.save(buf, format="PNG")
    h = hashlib.md5(buf.getvalue()).hexdigest()[:12]
    return f"{prefix}__{h}"


def embed_image(image, base_url=None):
    """Embed a PIL image via jsl_vision_embed_crossmodal_1.0. Returns 1024-dim L2-normalized vector or None."""
    import base64
    from io import BytesIO

    # Check query cache
    if _query_cache_nb:
        key = _query_cache_key("img", image)
        qcache = _load_query_cache(_query_cache_nb)
        if key in qcache:
            return np.array(qcache[key], dtype=np.float32)

    base_url = base_url or EMBED_BASE_URL
    buf = BytesIO()
    image.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    try:
        resp = requests.post(f"{base_url}/embed/image", json={"images": [b64]}, timeout=30)
        resp.raise_for_status()
        emb = np.array(resp.json()["embeddings"][0], dtype=np.float32)
        # Save to query cache
        if _query_cache_nb:
            qcache = _load_query_cache(_query_cache_nb)
            qcache[key] = emb.tolist()
            _save_query_cache(_query_cache_nb, qcache)
        return emb
    except Exception:
        print("[warn] jsl_vision_embed_crossmodal_1.0 not available — skipping image embedding")
        return None


def embed_text(text, base_url=None):
    """Embed text via jsl_vision_embed_crossmodal_1.0. Returns 1024-dim L2-normalized vector or None."""
    # Check query cache
    if _query_cache_nb:
        key = _query_cache_key("txt", text)
        qcache = _load_query_cache(_query_cache_nb)
        if key in qcache:
            return np.array(qcache[key], dtype=np.float32)

    base_url = base_url or EMBED_BASE_URL
    try:
        resp = requests.post(f"{base_url}/embed/text", json={"texts": [text]}, timeout=30)
        resp.raise_for_status()
        emb = np.array(resp.json()["embeddings"][0], dtype=np.float32)
        if _query_cache_nb:
            qcache = _load_query_cache(_query_cache_nb)
            qcache[key] = emb.tolist()
            _save_query_cache(_query_cache_nb, qcache)
        return emb
    except Exception:
        print("[warn] jsl_vision_embed_crossmodal_1.0 not available — skipping text embedding")
        return None


def embed_texts_batch(texts, base_url=None, batch_size=32, show_progress=True):
    """Embed a list of texts via jsl_vision_embed_crossmodal_1.0. Returns (N, 1024) float32 array."""
    base_url = base_url or EMBED_BASE_URL
    from tqdm.notebook import tqdm as _tqdm
    all_embs = []
    it = range(0, len(texts), batch_size)
    if show_progress:
        it = _tqdm(it, desc="Embedding texts", total=(len(texts) + batch_size - 1) // batch_size)
    for start in it:
        batch = texts[start:start + batch_size]
        resp = requests.post(f"{base_url}/embed/text", json={"texts": batch}, timeout=60)
        resp.raise_for_status()
        all_embs.extend(resp.json()["embeddings"])
    return np.array(all_embs, dtype=np.float32)


def check_embed_server(base_url=None):
    """Check jsl_vision_embed_crossmodal_1.0 embedding server is reachable."""
    base_url = base_url or EMBED_BASE_URL
    try:
        r = requests.get(f"{base_url}/health", timeout=5)
        r.raise_for_status()
        print(f"[ok] jsl_vision_embed_crossmodal_1.0 embeddings ready ({base_url})")
        return True
    except Exception:
        print(f"[warn] jsl_vision_embed_crossmodal_1.0 not available ({base_url})")
        return False


# ============================================================================
# CLINICAL TEXT EMBEDDINGS — sbiobert via Spark NLP port 9470
# ============================================================================

def embed_clinical_text(text, base_url=None):
    """Embed text via sbiobert_base_cased_mli (Spark NLP). Returns 768-dim L2-normalized vector or None."""
    # Check query cache
    if _query_cache_nb:
        key = _query_cache_key("clin", text)
        qcache = _load_query_cache(_query_cache_nb)
        if key in qcache:
            return np.array(qcache[key], dtype=np.float32)

    base_url = base_url or SPARKNLP_URL
    try:
        resp = requests.post(f"{base_url}/embed/text", json={"texts": [text]}, timeout=30)
        resp.raise_for_status()
        emb = np.array(resp.json()["embeddings"][0], dtype=np.float32)
        if _query_cache_nb:
            qcache = _load_query_cache(_query_cache_nb)
            qcache[key] = emb.tolist()
            _save_query_cache(_query_cache_nb, qcache)
        return emb
    except Exception:
        print("[warn] sbiobert not available — skipping clinical text embedding")
        return None


def embed_clinical_texts_batch(texts, base_url=None, batch_size=32, show_progress=True):
    """Embed a list of texts via sbiobert (Spark NLP). Returns (N, 768) float32 array."""
    base_url = base_url or SPARKNLP_URL
    from tqdm.notebook import tqdm as _tqdm
    all_embs = []
    it = range(0, len(texts), batch_size)
    if show_progress:
        it = _tqdm(it, desc="Embedding clinical texts", total=(len(texts) + batch_size - 1) // batch_size)
    for start in it:
        batch = texts[start:start + batch_size]
        resp = requests.post(f"{base_url}/embed/text", json={"texts": batch}, timeout=60)
        resp.raise_for_status()
        all_embs.extend(resp.json()["embeddings"])
    return np.array(all_embs, dtype=np.float32)


def embed_images_batch(images, base_url=None, batch_size=8, show_progress=True):
    """Embed a list of PIL images via jsl_vision_embed_crossmodal_1.0. Returns (N, 1024) float32 array."""
    base_url = base_url or EMBED_BASE_URL
    from tqdm.notebook import tqdm as _tqdm
    all_embs = []
    it = range(0, len(images), batch_size)
    if show_progress:
        it = _tqdm(it, desc="Embedding images", total=(len(images) + batch_size - 1) // batch_size)
    for start in it:
        batch = images[start:start + batch_size]
        b64_batch = []
        for img in batch:
            buf = BytesIO()
            # Resize large images to avoid 500 errors
            if max(img.size) > 1024:
                img = img.copy()
                img.thumbnail((1024, 1024))
            img.save(buf, format="PNG")
            b64_batch.append(base64.b64encode(buf.getvalue()).decode())
        for attempt in range(3):
            try:
                resp = requests.post(f"{base_url}/embed/image", json={"images": b64_batch}, timeout=60)
                resp.raise_for_status()
                all_embs.extend(resp.json()["embeddings"])
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(1)
    return np.array(all_embs, dtype=np.float32)


def check_clinical_embed_server(base_url=None):
    """Check sbiobert embedding endpoint is reachable via Spark NLP."""
    base_url = base_url or SPARKNLP_URL
    try:
        resp = requests.post(f"{base_url}/embed/text", json={"texts": ["test"]}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if "embeddings" not in data:
            print(f"[warn] sbiobert response missing 'embeddings' key ({base_url})")
            return False
        dim = len(data["embeddings"][0])
        if dim != 768:
            print(f"[warn] sbiobert unexpected dim={dim}, expected 768 ({base_url})")
            return False
        print(f"[ok] sbiobert clinical embeddings ready ({base_url}, dim=768)")
        return True
    except Exception:
        print(f"[warn] sbiobert not available ({base_url})")
        return False


def build_rag_index(docs, images, nb_name=None, use_cache=True):
    """Build dual FAISS index (text + image) from extracted docs.

    Returns dict with keys: text_index, image_index, text_embeddings,
    image_embeddings, searchable_texts, valid_doc_indices, valid_images.
    """
    import faiss

    # Check if we can skip server health checks (cache available for both)
    _have_text_cache = use_cache and nb_name and has_nb_cache(nb_name, "text_embeddings")
    _have_img_cache = use_cache and nb_name and has_nb_cache(nb_name, "image_embeddings")
    if not _have_img_cache:
        check_embed_server()
    if not _have_text_cache:
        check_clinical_embed_server()

    # Build searchable text per doc
    searchable_texts = []
    valid_doc_indices = []
    valid_images = []
    for i, doc in enumerate(docs):
        if doc.get("_status") != "success":
            continue
        parts = [
            f"Document Type: {doc.get('document_type', 'Unknown')}",
            f"Title: {doc.get('document_title', 'Untitled')}",
            f"Specialty: {doc.get('specialty', 'General')}",
            f"Chief Complaint: {doc.get('chief_complaint', 'N/A')}",
            f"Summary: {doc.get('summary', '')}",
            f"Diagnoses: {_safe_join(doc.get('diagnoses', []))}",
            f"Findings: {_safe_join(doc.get('findings', []))}",
            f"Medications: {_safe_join(doc.get('medications', []))}",
            f"Keywords: {_safe_join(doc.get('keywords', []))}",
        ]
        # Append OCR text when available (richer for text-heavy docs)
        if doc.get("_ocr_text"):
            parts.append(f"OCR Text: {doc['_ocr_text'][:2000]}")
        searchable_texts.append(" ".join(p for p in parts if p))
        valid_doc_indices.append(i)
        idx = doc.get("_image_idx")
        valid_images.append(images[idx] if idx is not None else None)

    if not searchable_texts:
        print("[warn] No successful docs to index")
        return {
            "text_index": None, "image_index": None,
            "text_embeddings": np.array([]), "image_embeddings": np.array([]),
            "searchable_texts": [], "valid_doc_indices": [], "valid_images": [],
        }

    # Text embeddings (sbiobert)
    if use_cache and nb_name and has_nb_cache(nb_name, "text_embeddings"):
        text_emb = np.array(load_nb_cache(nb_name, "text_embeddings")["embeddings"], dtype=np.float32)
    else:
        text_emb = embed_clinical_texts_batch(searchable_texts)
        if nb_name:
            save_nb_cache(nb_name, "text_embeddings", {"embeddings": text_emb.tolist()})

    # Image embeddings (jsl_vision_embed_crossmodal_1.0)
    if use_cache and nb_name and has_nb_cache(nb_name, "image_embeddings"):
        img_emb = np.array(load_nb_cache(nb_name, "image_embeddings")["embeddings"], dtype=np.float32)
    else:
        img_emb = embed_images_batch([im for im in valid_images if im is not None])
        if nb_name:
            save_nb_cache(nb_name, "image_embeddings", {"embeddings": img_emb.tolist()})

    # Build FAISS indices
    text_index = faiss.IndexFlatIP(text_emb.shape[1])
    text_index.add(text_emb)
    image_index = faiss.IndexFlatIP(img_emb.shape[1])
    image_index.add(img_emb)

    print(f"RAG ready -- {len(searchable_texts)} docs | "
          f"text {text_emb.shape[1]}d (sbiobert) + image {img_emb.shape[1]}d (jsl_vision_embed_crossmodal_1.0)")

    return {
        "text_index": text_index, "image_index": image_index,
        "text_embeddings": text_emb, "image_embeddings": img_emb,
        "searchable_texts": searchable_texts,
        "valid_doc_indices": valid_doc_indices,
        "valid_images": valid_images,
    }


# ============================================================================
# SHARED UTILITIES
# ============================================================================

def _safe_join(lst):
    """Join a list to string, handling items that may be dicts (model returned objects)."""
    if not lst:
        return ""
    parts = []
    for item in lst:
        if isinstance(item, dict):
            parts.append(" ".join(str(v) for v in item.values() if v))
        else:
            parts.append(str(item))
    return ", ".join(parts)


# ============================================================================
# SHARED INFERENCE — structured JSON extraction via vLLM
# ============================================================================

def _openai_strict_schema(schema):
    """Convert schema to OpenAI strict-mode format (recursive).

    OpenAI requires: all objects have additionalProperties=false and all
    properties in 'required'; nullable types use anyOf syntax.
    """
    if not isinstance(schema, dict):
        return schema
    schema = dict(schema)
    t = schema.get("type")

    # Fix nullable union types: ["string", "null"] → anyOf
    if isinstance(t, list):
        schema.pop("type")
        schema["anyOf"] = [{"type": x} for x in t]

    # Recurse into object properties
    if t == "object" or "properties" in schema:
        props = schema.get("properties", {})
        new_props = {}
        for key, spec in props.items():
            new_props[key] = _openai_strict_schema(spec)
        schema["properties"] = new_props
        schema["required"] = list(new_props.keys())
        schema["additionalProperties"] = False

    # Recurse into array items
    if "items" in schema:
        schema["items"] = _openai_strict_schema(schema["items"])

    return schema


def infer_image_structured(image, prompt, schema, *,
                           base_url=None, model=None, api_key=None,
                           system_prompt=None, max_tokens=1024,
                           timeout=300, max_retries=3):
    """Structured JSON extraction via vLLM/OpenRouter response_format json_schema.

    Uses OpenAI-compatible response_format json_schema which enforces the
    schema at the token level — every field in the schema is always present.

    Args:
        image:         PIL Image or file path
        prompt:        user prompt text
        schema:        JSON schema dict
        base_url:      server URL (default: config.VLLM_BASE_URL)
        model:         model name (default: config.VLLM_MODEL)
        api_key:       API key for cloud providers (OpenRouter, etc.)
        system_prompt: system message (default: generic document analyst)
        max_tokens:    max output tokens (default: 6144)
        timeout:       request timeout in seconds
        max_retries:   number of retries on connection errors
    """
    import time
    from utils.config import VLLM_BASE_URL, VLLM_MODEL

    if isinstance(image, str):
        image = Image.open(image)

    # Resize large images to fit within vLLM context window.
    # Images > 768px on longest side can consume 4000+ vision tokens,
    # leaving too few tokens for output when max_model_len is 8192.
    _MAX_DIM = 768
    w, h = image.size
    if max(w, h) > _MAX_DIM:
        scale = _MAX_DIM / max(w, h)
        image = image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    base_url = base_url or VLLM_BASE_URL
    model    = model or VLLM_MODEL

    # JSL Vision alias — transparently route to backend
    from utils.config import JSL_VISION_MODEL, JSL_VISION_BACKEND
    from utils.config import OPENROUTER_BASE_URL, OPENROUTER_API_KEY
    if model == JSL_VISION_MODEL:
        base_url = OPENROUTER_BASE_URL
        model = JSL_VISION_BACKEND
        api_key = api_key or OPENROUTER_API_KEY
    if system_prompt is None:
        system_prompt = (
            "You are an expert document analyst. "
            "Extract information accurately from the document image. "
            "Return all fields defined in the schema with real extracted values."
        )

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    start_time   = time.time()
    clean_schema = {k: v for k, v in schema.items() if k != "$schema"}

    # Claude via OpenRouter doesn't reliably enforce json_schema — use json_object + schema in prompt
    use_json_object = ("anthropic/" in model or "claude" in model.lower())

    # OpenAI strict mode requires ALL properties in "required" and uses
    # {"anyOf": [{"type":"string"},{"type":"null"}]} instead of {"type":["string","null"]}
    is_openai = "openai/" in model or "gpt" in model.lower()
    if is_openai:
        clean_schema = _openai_strict_schema(clean_schema)

    user_text = prompt
    if use_json_object:
        fields_desc = ", ".join(clean_schema.get("properties", {}).keys())
        user_text = f"{prompt}\n\nReturn ONLY a JSON object with these fields: {fields_desc}"
        system_prompt = "You are an expert document analyst. Return ONLY valid JSON, no markdown, no explanation."

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encode_image_b64(image)}"},
                    },
                    {"type": "text", "text": user_text},
                ],
            },
        ],
        "temperature": 0.0,
        "max_tokens":  max_tokens,
    }

    if use_json_object:
        payload["response_format"] = {"type": "json_object"}
        payload["provider"] = {"order": ["Anthropic"]}
    else:
        payload["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name":   "document_extraction",
                "strict": True,
                "schema": clean_schema,
            },
        }

    last_error = None
    for attempt in range(max_retries):
        try:
            resp = requests.post(
                f"{base_url}/chat/completions", json=payload,
                headers=headers, timeout=timeout
            )
            if resp.status_code >= 400:
                try:
                    err_body = resp.json().get("error", {}).get("message", resp.text[:300])
                except Exception:
                    err_body = resp.text[:300]
                raise RuntimeError(f"HTTP {resp.status_code}: {err_body}")
            resp.raise_for_status()
            result  = resp.json()
            choice  = result["choices"][0]
            content = choice["message"]["content"]

            if not content or not content.strip():
                raise RuntimeError("Server returned empty content")

            # Truncated output — model hit max_tokens before closing JSON
            if choice.get("finish_reason") == "length":
                raise RuntimeError(
                    f"Output truncated (hit max_tokens={max_tokens}). "
                    f"Increase max_tokens or simplify the schema."
                )

            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            parsed = json.loads(content)
            if "$schema" in parsed or "properties" in parsed:
                raise RuntimeError("Model returned schema definition instead of extracted data")

            elapsed = time.time() - start_time
            return {
                "data":    parsed,
                "_timing": elapsed,
                "_tokens": result.get("usage", {}).get("total_tokens", 0),
            }
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        except Exception as e:
            raise e

    raise last_error


# ============================================================================
# OCR — raw text extraction via jsl_vision_ocr_parsing_1_0
# ============================================================================

# Doc types that are text-heavy and benefit from OCR
OCR_DOC_TYPES = {"clinical_note", "prescription", "consent_form", "omr_form", "ecg"}

def infer_ocr_text(image, *, base_url=None, model=None, timeout=120, max_retries=3):
    """Run OCR model on an image, return raw text string.

    Uses jsl_vision_ocr_parsing_1_0 (vLLM chat endpoint on port 9461).
    """
    import time
    from utils.config import OCR_BASE_URL, OCR_MODEL

    if isinstance(image, str):
        image = Image.open(image)

    base_url = base_url or OCR_BASE_URL
    model = model or OCR_MODEL

    buf = BytesIO()
    image.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()

    payload = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                {"type": "text", "text": "OCR this document. Return all visible text, preserving layout."},
            ],
        }],
        "temperature": 0.0,
        "max_tokens": 4096,
    }

    start = time.time()
    last_error = None
    for attempt in range(max_retries):
        try:
            resp = requests.post(f"{base_url}/chat/completions", json=payload, timeout=timeout)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].strip()
            return {"text": content, "_timing": time.time() - start}
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    raise last_error


def check_ocr_server(base_url=None):
    """Check OCR model is reachable. Returns True/False."""
    from utils.config import OCR_BASE_URL, OCR_MODEL
    base_url = base_url or OCR_BASE_URL
    try:
        resp = requests.get(f"{base_url}/models", timeout=5)
        models = [m["id"] for m in resp.json().get("data", [])]
        if models:
            print(f"[ok] OCR server ready -- {models[0]} on {base_url}")
            return True
        return False
    except Exception as e:
        print(f"[warn] OCR server not available ({base_url}): {e}")
        return False


def run_ocr_batch(images, ids, extracted_docs, *,
                  nb_name=None, use_cache=False, base_url=None, model=None):
    """Run OCR on documents where VLM reported has_text=True.

    Falls back to OCR_DOC_TYPES if has_text not present in extraction.
    Returns dict {doc_id: ocr_text}. Cached under key 'ocr_texts'.
    """
    from tqdm.notebook import tqdm

    cache_key = "ocr_texts"
    if use_cache and nb_name and has_nb_cache(nb_name, cache_key):
        cached = load_nb_cache(nb_name, cache_key)
        print(f"Cached OCR -- {len(cached)} docs")
        return cached

    ocr_results = {}
    # Use VLM has_text flag when available, else fall back to doc type
    text_indices = []
    for i, doc in enumerate(extracted_docs):
        if "_error" in doc:
            continue
        has_text = doc.get("has_text")
        if has_text is True:
            text_indices.append(i)
        elif has_text is None:
            # Fallback: use doc_type heuristic
            dt = doc.get("document_type", "")
            if dt in OCR_DOC_TYPES:
                text_indices.append(i)

    if not text_indices:
        print("No text-heavy documents found -- skipping OCR")
        return ocr_results

    print(f"Running OCR on {len(text_indices)}/{len(images)} text-heavy documents...")
    for i in tqdm(text_indices, desc="OCR"):
        try:
            result = infer_ocr_text(images[i], base_url=base_url, model=model)
            ocr_results[ids[i]] = result["text"]
        except Exception as e:
            print(f"  [warn] OCR failed for {ids[i]}: {e}")

    if nb_name:
        save_nb_cache(nb_name, cache_key, ocr_results)

    print(f"[ok] OCR complete: {len(ocr_results)}/{len(text_indices)} docs")
    return ocr_results


def enrich_with_ocr(extracted_docs, images, ids, *, nb_name=None, use_cache=True):
    """One-call OCR: check server, run batch, attach _ocr_text to docs. Skips gracefully."""
    if not check_ocr_server():
        return
    ocr_texts = run_ocr_batch(images, ids, extracted_docs,
                              nb_name=nb_name, use_cache=use_cache)
    for doc in extracted_docs:
        doc_id = doc.get("doc_id", "")
        if doc_id in ocr_texts:
            doc["_ocr_text"] = ocr_texts[doc_id]
    n = sum(1 for d in extracted_docs if "_ocr_text" in d)
    print(f"OCR text attached to {n}/{len(extracted_docs)} docs")


def enrich_with_nlp(extracted_docs, *, nb_name=None, use_cache=True,
                    ner_models=('jsl', 'posology'),
                    resolve_systems=('icd10', 'rxnorm', 'snomed'),
                    do_relations=True):
    """One-call NLP: check server, run enrichment, skip gracefully on failure."""
    try:
        if not check_sparknlp():
            return
        enrich_docs_nlp(
            extracted_docs, ner_models=ner_models,
            resolve_systems=resolve_systems, do_relations=do_relations,
            nb_name=nb_name, use_cache=use_cache,
        )
    except Exception as e:
        print(f"[warn] NLP enrichment failed: {e}")


def resolve_terms_nlp(terms, system="icd10", url=None):
    """Resolve a list of clinical terms to codes via Spark NLP. Returns {term: 'CODE (desc)'}.

    Skips gracefully if server is down. Systems: icd10, snomed, icdo, rxnorm, etc.
    """
    from utils.config import SPARKNLP_BASE_URL
    url = url or SPARKNLP_BASE_URL
    if not check_sparknlp(url):
        return {}
    result = {}
    for term in terms:
        try:
            resp = requests.post(f"{url}/resolve/{system}",
                                 json={"text": term}, timeout=30)
            codes = resp.json() if resp.ok else []
            if isinstance(codes, dict):
                codes = codes.get("codes", [])
            if codes:
                best = codes[0]
                result[term] = f"{best.get('code', '?')} ({best.get('description', '')[:60]})"
            else:
                result[term] = "no match"
        except Exception as e:
            result[term] = f"error: {e}"
    return result


# ============================================================================
# CHARTS — dark-mode bar charts for notebooks
# ============================================================================

def plot_distribution(labels_or_list, counts=None, title="Distribution", total=None):
    """Dark-mode horizontal bar chart. Pass either (labels, counts) or just a flat list of values to count."""
    from collections import Counter
    if counts is None:
        # Raw list — count occurrences
        c = Counter(labels_or_list)
        labels = [k for k, _ in c.most_common()]
        counts = [v for _, v in c.most_common()]
        if total is None:
            total = len(labels_or_list)
    else:
        labels = labels_or_list
    """Dark-mode horizontal bar chart for category distributions."""
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.rcParams.update({
        'figure.facecolor': '#0f172a', 'axes.facecolor': '#0f172a',
        'text.color': '#e2e8f0', 'axes.labelcolor': '#e2e8f0',
        'xtick.color': '#94a3b8', 'ytick.color': '#94a3b8',
    })
    n = len(labels)
    fig_h = max(3, n * 0.45 + 1.2)
    fig, ax = plt.subplots(figsize=(10, fig_h))
    palette = ['#6366f1', '#14b8a6', '#f59e0b', '#ef4444', '#8b5cf6',
               '#ec4899', '#0ea5e9', '#10b981', '#f97316', '#a78bfa',
               '#22d3ee', '#fb7185', '#34d399', '#fbbf24', '#818cf8']
    bars = ax.barh(labels[::-1], counts[::-1],
                   color=[palette[i % len(palette)] for i in range(n)][::-1],
                   edgecolor='#1e293b', linewidth=0.5, height=0.6)
    ax.set_xlabel('Count', fontsize=11)
    total_str = f" ({total} total)" if total else ""
    ax.set_title(f"{title}{total_str}", fontsize=14, color='#f1f5f9', pad=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#334155')
    ax.spines['left'].set_color('#334155')
    ax.tick_params(axis='y', labelsize=10)
    x_max = max(counts) if counts else 1
    ax.set_xlim(0, x_max * 1.15)
    for bar, count in zip(bars, counts[::-1]):
        ax.text(bar.get_width() + x_max * 0.02, bar.get_y() + bar.get_height() / 2,
                str(count), va='center', fontsize=10, color='#cbd5e1', fontweight='bold')
    plt.tight_layout()
    plt.show()


def run_inference_batch(infer_fn, imgs, ids, prompt, schema, id_key="doc_id", desc="Processing", enrich_fn=None):
    """Run structured inference over a list of images.

    Args:
        enrich_fn: optional callable(data, id, idx) to add extra fields per result.
    Returns (results, df) — results is the raw list (including errors, _timing per doc),
    df contains only successful extractions as a DataFrame.
    """
    import pandas as pd
    from tqdm.notebook import tqdm

    results = []
    error_samples = []
    for i, img in enumerate(tqdm(imgs, desc=desc)):
        try:
            out  = infer_fn(img, prompt, schema)
            data = out["data"]
            data[id_key]    = ids[i]
            data["_timing"] = out["_timing"]
            if enrich_fn:
                enrich_fn(data, ids[i], i)
            results.append(data)
        except Exception as e:
            results.append({id_key: ids[i], "_error": str(e)})
            if len(error_samples) < 3:
                error_samples.append(f"  {ids[i]}: {str(e)[:200]}")

    n_errors = sum(1 for r in results if "_error" in r)
    if n_errors > 0:
        print(f"\n[warn] {n_errors}/{len(results)} failed:")
        for msg in error_samples:
            print(msg)

    df = pd.DataFrame([r for r in results if "_error" not in r])
    return results, df


def run_cached_batch(nb_name, cache_key, use_cache, infer_fn, imgs, ids, prompt, schema,
                     show_metrics=False, **kwargs):
    """Cache-or-infer wrapper around run_inference_batch.

    Supports incremental growth: if cache has fewer results than current dataset,
    keeps cached results and only infers new items (matched by id).

    Returns (results, df, timings) — loads from cache when available,
    otherwise runs inference and saves to cache.
    Extra kwargs passed to run_inference_batch (id_key, desc, enrich_fn).
    When show_metrics=True, displays a metrics card + success banner automatically.
    """
    import pandas as pd
    from IPython.display import HTML, display as _disp

    id_key = kwargs.get("id_key", "doc_id")

    if use_cache and has_nb_cache(nb_name, cache_key):
        cached = load_nb_cache(nb_name, cache_key)
        cached_results = cached["results"]

        # Incremental: if dataset grew, keep cached results, infer only new items
        cached_ids = {r.get(id_key) for r in cached_results if r.get(id_key)}
        new_indices = [i for i, doc_id in enumerate(ids) if doc_id not in cached_ids]

        if not new_indices:
            # Full cache hit
            results = cached_results
            timings = cached.get("timings", [r.get("_timing", 0) for r in results if "_error" not in r])
            n_ok = sum(1 for r in results if "_error" not in r)
            print(f"Cached -- {n_ok}/{len(results)} successful")
        else:
            # Partial cache — infer only new items
            new_imgs = [imgs[i] for i in new_indices]
            new_ids = [ids[i] for i in new_indices]
            print(f"Incremental -- {len(cached_results)} cached, {len(new_indices)} new")
            new_results, _ = run_inference_batch(infer_fn, new_imgs, new_ids, prompt, schema, **kwargs)

            # Merge: build id→result map from cache, add new results
            result_map = {r.get(id_key): r for r in cached_results}
            for r in new_results:
                result_map[r.get(id_key)] = r

            # Preserve original order
            results = [result_map.get(doc_id, {"_error": "missing", id_key: doc_id}) for doc_id in ids]
            timings = [r.get("_timing", 0) for r in results if "_timing" in r]
            save_nb_cache(nb_name, cache_key, {"results": results, "timings": timings})
    else:
        results, _ = run_inference_batch(infer_fn, imgs, ids, prompt, schema, **kwargs)
        timings = [r["_timing"] for r in results if "_timing" in r]
        save_nb_cache(nb_name, cache_key, {"results": results, "timings": timings})

    df = pd.DataFrame([r for r in results if "_error" not in r])

    if show_metrics:
        n_ok = len(df)
        total = len(results)
        elapsed = sum(timings) if timings else 0
        _disp(HTML(create_metrics_card({
            "Success": f"{n_ok}/{total}",
            "Time": f"{elapsed:.1f}s",
            "Speed": f"{total/max(elapsed,0.1):.2f} docs/s",
            "Errors": total - n_ok,
        })))
        if n_ok == total:
            _disp(HTML(create_success_banner()))

    return results, df, timings


# ============================================================================
# FULL RAG PIPELINE — extract + OCR + NLP in one call
# ============================================================================

def run_rag_extraction(images, ids, prompt, schema, *,
                       nb_name, use_cache=True, infer_fn=None,
                       ocr=True, nlp=True,
                       nlp_ner=("jsl",), nlp_resolve=("icd10", "rxnorm", "snomed"),
                       nlp_relations=False, preview=True):
    """Full RAG extraction pipeline: VLM → OCR → NLP → preview.

    Returns extracted_docs list with _ocr_text and _nlp_* fields attached.
    """
    if infer_fn is None:
        infer_fn = infer_image_structured

    # 1. VLM extraction (cached)
    extracted_docs, _, _ = run_cached_batch(
        nb_name, "extracted_docs", use_cache,
        infer_fn, images, ids, prompt, schema,
        desc="Extracting",
        enrich_fn=lambda data, doc_id, idx: data.update({"_status": "success", "_image_idx": idx}),
    )

    # 2. OCR on text-heavy docs (if has_text field present)
    if ocr:
        enrich_with_ocr(extracted_docs, images, ids, nb_name=nb_name, use_cache=use_cache)

    # 3. NLP enrichment
    if nlp:
        enrich_with_nlp(extracted_docs, nb_name=nb_name, use_cache=use_cache,
                        ner_models=nlp_ner, resolve_systems=nlp_resolve,
                        do_relations=nlp_relations)

    # 4. Diverse preview (1 per doc type)
    if preview:
        _seen, _prev = set(), []
        for j, d in enumerate(extracted_docs):
            dt = d.get("document_type", d.get("diagnosis", ""))
            idx = d.get("_image_idx", j)
            if dt not in _seen and "_error" not in d and idx < len(images):
                _seen.add(dt)
                _prev.append((idx, d))
        if _prev:
            display_document_analysis([images[idx] for idx, _ in _prev],
                                      [d for _, d in _prev])

    return extracted_docs


# ============================================================================
# RAG QUERY HELPERS — run text/image queries with minimal notebook code
# ============================================================================

def run_text_rag_queries(queries, search_fn, extracted_docs, index_images, **display_kwargs):
    """Run multiple text RAG queries, display results with full extracted doc fields.

    Args:
        queries: list of query strings, or list of (query, expected_label) tuples
        search_fn: function(query, k=5) → [(idx, score), ...] or [(idx, score, gt), ...]
        extracted_docs: list of VLM-extracted doc dicts (indexed same as FAISS)
        index_images: list of PIL images (indexed same as FAISS)
        **display_kwargs: passed to display_document_analysis
    """
    for q in queries:
        if isinstance(q, tuple):
            query_text, expected = q[0], q[1]
        else:
            query_text, expected = q, None

        results = search_fn(query_text, k=5) if 'k' in search_fn.__code__.co_varnames else search_fn(query_text, top_k=5)
        # Normalize results to (idx, score) tuples
        if results and len(results[0]) == 3:
            results = [(r[0], r[1]) for r in results]

        imgs = [index_images[idx] for idx, _ in results]
        preds = [dict(extracted_docs[idx], similarity=f"{s:.3f}") for idx, s in results]

        if expected:
            print(f'Query: "{query_text}" (expected: {expected})')
        display_document_analysis(imgs, preds, query=query_text, **display_kwargs)


def run_image_rag_queries(holdout_indices, all_images, all_gt, image_index,
                          extracted_docs, embed_image_fn, *,
                          match_key="class", query_image_key=None):
    """Run held-out image queries with precision@5, display full extracted doc fields.

    Args:
        holdout_indices: list of indices into all_images to use as queries
        all_images: full image list
        all_gt: list of GT dicts per image
        image_index: FAISS index
        extracted_docs: VLM-extracted docs (indexed same as FAISS)
        embed_image_fn: function to embed a single image
        match_key: GT dict key to check for precision (e.g., "class", "body_part", "label")
        query_image_key: if set, use this GT key as query label in display

    Returns:
        precision_scores: list of P@5 values
    """
    precision_scores = []
    for qi in holdout_indices:
        q_img = all_images[qi]
        q_gt = all_gt[qi]
        q_emb = embed_image_fn(q_img).reshape(1, -1)
        scores, ids = image_index.search(q_emb, 6)

        result_imgs, result_preds, matches = [], [], 0
        for s, idx in zip(scores[0], ids[0]):
            idx = int(idx)
            if idx == qi:
                continue
            gt = all_gt[idx]
            match = gt.get(match_key) == q_gt.get(match_key)
            if match:
                matches += 1
            doc = extracted_docs[idx] if idx < len(extracted_docs) else {}
            result_imgs.append(all_images[idx])
            result_preds.append(dict(doc, similarity=f"{s:.3f}", match="yes" if match else "no"))
            if len(result_imgs) >= 5:
                break

        p5 = matches / max(len(result_imgs), 1)
        precision_scores.append(p5)

        q_label = q_gt.get(query_image_key or match_key, "")
        display_document_analysis(
            result_imgs, result_preds,
            query=f"Image query: {q_label} (P@5={p5:.0%})",
            query_image=q_img)

    return precision_scores


def run_classification_eval(nb_name, cache_key, use_cache, infer_fn,
                            all_images, all_labels, schema, prompt,
                            n_per_class=10, seed=42, **kwargs):
    """Build balanced eval subset, run VLM classification, return results + metrics.

    Args:
        all_images: full image list
        all_labels: label per image
        schema, prompt: VLM schema and prompt
        n_per_class: images per class for eval
        seed: random seed for reproducibility

    Returns:
        (results, eval_images, eval_labels, eval_ids)
    """
    import random
    random.seed(seed)
    from collections import Counter

    classes = sorted(set(all_labels))
    eval_indices = []
    for cls in classes:
        pool = [i for i, l in enumerate(all_labels) if l == cls]
        n = min(n_per_class, len(pool))
        eval_indices.extend(random.sample(pool, n))

    eval_images = [all_images[i] for i in eval_indices]
    eval_labels = [all_labels[i] for i in eval_indices]
    eval_ids = [f"eval_{i}" for i in eval_indices]

    print(f"Eval set: {len(eval_images)} images ({len(classes)} classes, {n_per_class}/class)")

    results, _, _ = run_cached_batch(
        nb_name, cache_key, use_cache,
        infer_fn, eval_images, eval_ids,
        prompt, schema,
        desc="Classifying",
        enrich_fn=lambda data, doc_id, idx: data.update({
            "_status": "success", "_gt_label": eval_labels[idx],
        }),
        **kwargs,
    )
    return results, eval_images, eval_labels, eval_ids


def plot_confusion_matrix(y_true, y_pred, labels, title="Confusion Matrix"):
    """Plot a dark-mode confusion matrix heatmap."""
    import matplotlib.pyplot as plt
    import matplotlib
    from sklearn.metrics import confusion_matrix, classification_report

    matplotlib.rcParams.update({
        'figure.facecolor': '#0f172a', 'axes.facecolor': '#0f172a',
        'text.color': '#e2e8f0', 'axes.labelcolor': '#e2e8f0',
        'xtick.color': '#94a3b8', 'ytick.color': '#94a3b8',
    })

    cm = confusion_matrix(y_true, y_pred, labels=labels)
    fig, ax = plt.subplots(figsize=(max(6, len(labels)), max(5, len(labels) * 0.8)))
    im = ax.imshow(cm, cmap='viridis', aspect='auto')
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Ground Truth')
    ax.set_title(title, fontsize=14, color='#f1f5f9', pad=12)

    for i in range(len(labels)):
        for j in range(len(labels)):
            color = '#000000' if cm[i, j] > cm.max() / 2 else '#e2e8f0'
            ax.text(j, i, str(cm[i, j]), ha='center', va='center', color=color, fontsize=10)

    plt.colorbar(im, ax=ax, shrink=0.8)
    plt.tight_layout()
    plt.show()

    print(classification_report(y_true, y_pred, labels=labels, target_names=labels, zero_division=0))
    return cm


def display_sample_gallery(images, labels, n_per_class=2, title="Sample Gallery"):
    """Show a grid of sample images, n per class, dark mode."""
    import matplotlib.pyplot as plt
    import matplotlib
    from collections import defaultdict
    import random

    matplotlib.rcParams.update({
        'figure.facecolor': '#0f172a', 'axes.facecolor': '#0f172a',
        'text.color': '#e2e8f0',
    })

    by_class = defaultdict(list)
    for i, l in enumerate(labels):
        by_class[l].append(i)

    classes = sorted(by_class.keys())
    n_cols = n_per_class
    n_rows = len(classes)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 2.5, n_rows * 2.5))
    if n_rows == 1:
        axes = [axes]

    for row, cls in enumerate(classes):
        indices = random.sample(by_class[cls], min(n_cols, len(by_class[cls])))
        for col in range(n_cols):
            ax = axes[row][col] if n_cols > 1 else axes[row]
            if col < len(indices):
                ax.imshow(images[indices[col]])
                if col == 0:
                    ax.set_ylabel(cls, fontsize=9, color='#94a3b8')
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines[:].set_visible(False)

    fig.suptitle(title, fontsize=14, color='#f1f5f9', y=1.01)
    plt.tight_layout()
    plt.show()




def eval_accuracy(results, pred_key, gt_key, label, display_map=None):
    """Compute and display per-class accuracy table. Returns overall accuracy."""
    import pandas as pd
    from collections import Counter
    from IPython.display import display
    correct, total = Counter(), Counter()
    for r in results:
        pred = (display_map or {}).get(r.get(pred_key, ""), r.get(pred_key, ""))
        gt = r[gt_key]; total[gt] += 1; correct[gt] += (pred == gt)
    acc = sum(correct.values()) / max(sum(total.values()), 1)
    print(f"{label}: {acc:.1%} ({sum(correct.values())}/{sum(total.values())})")
    rows = [{"Class": c, "Correct": f"{correct.get(c,0)}/{total[c]}",
             "Accuracy": f"{correct.get(c,0)/total[c]:.0%}"} for c in sorted(total)]
    display(pd.DataFrame(rows).style.set_properties(**{'text-align': 'left'}).hide(axis='index'))
    return acc


def run_ham_localization(ham_ds, nb_name, use_cache, infer_fn, schema, prompt,
                         n=50, ham_dx_map=None):
    """Sample HAM10000, run VLM localization, return results + GT."""
    import random
    random.seed(42)
    sample = random.sample(
        [(i, row) for i, row in enumerate(ham_ds) if row["localization"] and row["localization"] != "unknown"], n)
    images = [row["image"].convert("RGB") for _, row in sample]
    ids = [f"HAM_{i}" for i, _ in sample]
    gt_site = [row["localization"] for _, row in sample]
    gt_dx = [(ham_dx_map or {}).get(row["dx"], row["dx"]) for _, row in sample]

    def _enrich(data, doc_id, idx):
        data.update({"_status": "success", "_image_idx": idx,
                     "_gt_site": gt_site[idx], "_gt_dx": gt_dx[idx]})

    results, _, _ = run_cached_batch(
        nb_name, "localization_results", use_cache,
        infer_fn, images, ids, prompt, schema,
        desc="Localizing", enrich_fn=_enrich)
    ok = [r for r in results if "_error" not in r]
    print(f"Localization: {len(ok)}/{len(results)} successful")
    return results, ok, sample


def accuracy_by_group(results, sample_rows, pred_key, gt_fn, group_key, display_map=None):
    """Compute accuracy broken down by a demographic group (e.g., sex, age)."""
    from collections import defaultdict
    stats = defaultdict(lambda: [0, 0])  # [correct, total]
    for r, (_, row) in zip(results, sample_rows):
        if "_error" in r:
            continue
        group = row.get(group_key) or "unknown"
        pred = (display_map or {}).get(r.get(pred_key, ""), r.get(pred_key, ""))
        gt = gt_fn(row)
        stats[group][1] += 1
        stats[group][0] += (pred == gt)
    print(f"Accuracy by {group_key}:")
    for g, (c, t) in sorted(stats.items()):
        print(f"  {g:10s}: {c}/{t} ({c/t:.0%})" if t else f"  {g:10s}: 0/0")


def plot_accuracy_comparison(task_accs, title="Model Accuracy Comparison"):
    """Bar chart comparing accuracy across models for multiple tasks.
    
    Args:
        task_accs: dict of {task_name: {model_name: accuracy_float}}
        title: chart title
    """
    import matplotlib.pyplot as plt
    import matplotlib
    import numpy as np
    matplotlib.rcParams.update({
        'figure.facecolor': '#0f172a', 'axes.facecolor': '#0f172a',
        'text.color': '#e2e8f0', 'axes.labelcolor': '#e2e8f0',
        'xtick.color': '#94a3b8', 'ytick.color': '#94a3b8',
    })
    tasks = list(task_accs.keys())
    models = list(next(iter(task_accs.values())).keys())
    colors = {'JSL-30B': '#6366f1', 'Claude': '#ec4899', 'Claude Sonnet 4': '#ec4899', 'Claude Sonnet 4.6': '#ec4899',
              'GPT-4.1': '#14b8a6', 'GPT-5.4': '#14b8a6', 'JSL-7B': '#a78bfa',
              'k-NN': '#f59e0b', 'k-NN (Embed)': '#f59e0b'}
    
    x = np.arange(len(tasks))
    w = 0.8 / len(models)
    fig, ax = plt.subplots(figsize=(max(8, len(tasks) * 2), 5))
    
    for j, model in enumerate(models):
        vals = [task_accs[t].get(model, 0) * 100 for t in tasks]
        bars = ax.bar(x + j * w - 0.4 + w/2, vals, w * 0.9,
                      label=model, color=colors.get(model, '#94a3b8'),
                      edgecolor='#1e293b', linewidth=0.5)
        for bar, val in zip(bars, vals):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f"{val:.0f}%", ha='center', va='bottom', fontsize=8, color='#cbd5e1')
    
    ax.set_xticks(x)
    ax.set_xticklabels(tasks, fontsize=10)
    ax.set_ylabel('Accuracy (%)', fontsize=11)
    ax.set_title(title, fontsize=14, color='#f1f5f9', pad=12)
    ax.set_ylim(0, 105)
    ax.legend(facecolor='#1e293b', edgecolor='#334155', labelcolor='#e2e8f0')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#334155')
    ax.spines['left'].set_color('#334155')
    plt.tight_layout()
    plt.show()


# Pre-computed benchmark results (from run_cloud_benchmark.py + k-NN experiments)
_BENCHMARK_DATA = {
    "nb4_derm": {"8-class Lesion": {"Claude Sonnet 4.6": 0.312, "GPT-5.4": 0.400, "k-NN (Embed)": 0.911}},
    "nb5_radiology": {"CXR 3-class": {"Claude Sonnet 4.6": 0.317, "GPT-5.4": 0.367, "k-NN (Embed)": 0.882},
                       "Body Part 7-class": {"Claude Sonnet 4.6": 0.771, "GPT-5.4": 0.900, "k-NN (Embed)": 0.939}},
    "nb6_pathology": {"Breast Binary": {"Claude Sonnet 4.6": 0.600, "GPT-5.4": 0.613, "k-NN (Embed)": 0.870},
                       "Tissue 9-class": {"Claude Sonnet 4.6": 0.578, "GPT-5.4": 0.622, "k-NN (Embed)": 0.783},
                       "WBC 4-class": {"Claude Sonnet 4.6": 0.500, "GPT-5.4": 0.550, "k-NN (Embed)": 0.708}},
}

def show_benchmark(nb_name):
    """Show accuracy comparison chart for a notebook. 1-liner in notebooks."""
    data = _BENCHMARK_DATA.get(nb_name)
    if not data:
        print(f"No benchmark data for {nb_name}")
        return
    title = nb_name.replace("nb4_derm", "Dermatology").replace("nb5_radiology", "Radiology").replace("nb6_pathology", "Pathology")
    plot_accuracy_comparison(data, title=f"{title} -- Classification Accuracy")
