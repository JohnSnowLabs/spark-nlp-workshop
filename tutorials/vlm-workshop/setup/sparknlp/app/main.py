import json
import os
import time
import sys
import traceback

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

# ── Load license ──────────────────────────────────────────────────────────────
with open("/opt/license.json") as f:
    license_keys = json.load(f)
os.environ.update(license_keys)

# ── Start Spark NLP for Healthcare (GPU) ─────────────────────────────────────
from sparknlp_jsl import start

spark = start(license_keys["SECRET"], gpu=True)
print(f"[startup] Spark NLP session started (GPU): {spark.version}")

from sparknlp.base import *
from sparknlp.annotator import *
from sparknlp_jsl.annotator import *
from pyspark.ml import Pipeline
from sparknlp.pretrained import PretrainedPipeline

# ── Helpers ───────────────────────────────────────────────────────────────────

FAILED = {}  # track models that failed to load


def build_ner_light(ner_name, with_assertion=False):
    """Build NER LightPipeline. Optionally include assertion."""
    t0 = time.time()
    stages = [
        DocumentAssembler().setInputCol("text").setOutputCol("document"),
        SentenceDetectorDLModel.pretrained(
            "sentence_detector_dl_healthcare", "en", "clinical/models"
        )
        .setInputCols(["document"])
        .setOutputCol("sentence"),
        Tokenizer().setInputCols(["sentence"]).setOutputCol("token"),
        WordEmbeddingsModel.pretrained(
            "embeddings_clinical", "en", "clinical/models"
        )
        .setInputCols(["sentence", "token"])
        .setOutputCol("embeddings"),
        MedicalNerModel.pretrained(ner_name, "en", "clinical/models")
        .setInputCols(["sentence", "token", "embeddings"])
        .setOutputCol("ner"),
        NerConverter()
        .setInputCols(["sentence", "token", "ner"])
        .setOutputCol("ner_chunk"),
    ]
    if with_assertion:
        stages.append(
            AssertionDLModel.pretrained("assertion_dl", "en", "clinical/models")
            .setInputCols(["sentence", "ner_chunk", "embeddings"])
            .setOutputCol("assertion")
        )
    pipeline = Pipeline(stages=stages)
    model = pipeline.fit(spark.createDataFrame([[""]]).toDF("text"))
    light = LightPipeline(model)
    a = "+ assertion " if with_assertion else ""
    print(f"[startup] {ner_name} {a}loaded in {time.time()-t0:.1f}s")
    return light


def load_pretrained(pipeline_name):
    """Load a pretrained pipeline."""
    t0 = time.time()
    pp = PretrainedPipeline(pipeline_name, "en", "clinical/models")
    print(f"[startup] {pipeline_name} loaded in {time.time()-t0:.1f}s")
    return pp


def safe_load(name, loader, *args, **kwargs):
    """Load with error handling. Returns None on failure."""
    try:
        return loader(*args, **kwargs)
    except Exception as e:
        FAILED[name] = str(e)
        print(f"[startup] FAILED {name}: {e}")
        traceback.print_exc()
        return None


# ── Load NER Models ───────────────────────────────────────────────────────────
print("[startup] === Loading NER models ===")

ner_pipelines = {}
NER_CONFIGS = {
    "deid": ("ner_deid_subentity_augmented", True),
    "jsl": ("ner_jsl", True),
    "clinical": ("ner_clinical_large", True),
    "posology": ("ner_posology_large", False),
    "radiology": ("ner_radiology", True),
    "anatomy": ("ner_anatomy", False),
}
for key, (model_name, with_assert) in NER_CONFIGS.items():
    result = safe_load(f"ner/{key}", build_ner_light, model_name, with_assert)
    if result:
        ner_pipelines[key] = result

# ── Load Resolver Pipelines ──────────────────────────────────────────────────
print("[startup] === Loading resolver pipelines ===")

resolver_pipelines = {}
RESOLVER_CONFIGS = {
    "icd10": "icd10cm_rxnorm_resolver_pipeline",
    "snomed": "snomed_resolver_pipeline",
    "umls": "umls_clinical_findings_resolver_pipeline",
    "loinc": "loinc_resolver_pipeline",
}
for key, pipeline_name in RESOLVER_CONFIGS.items():
    result = safe_load(f"resolve/{key}", load_pretrained, pipeline_name)
    if result:
        resolver_pipelines[key] = result

# RxNorm — reuse icd10 pipeline (it includes both ICD-10 + RxNorm)
if "icd10" in resolver_pipelines:
    resolver_pipelines["rxnorm"] = resolver_pipelines["icd10"]
    print("[startup] rxnorm: reusing icd10cm_rxnorm_resolver_pipeline")

# ICD-O — build manually if needed
print("[startup] Building ICD-O resolver...")
try:
    t0 = time.time()
    icdo_stages = [
        DocumentAssembler().setInputCol("text").setOutputCol("document"),
        SentenceDetectorDLModel.pretrained(
            "sentence_detector_dl_healthcare", "en", "clinical/models"
        )
        .setInputCols(["document"])
        .setOutputCol("sentence"),
        Tokenizer().setInputCols(["sentence"]).setOutputCol("token"),
        WordEmbeddingsModel.pretrained(
            "embeddings_clinical", "en", "clinical/models"
        )
        .setInputCols(["sentence", "token"])
        .setOutputCol("embeddings"),
        MedicalNerModel.pretrained("ner_jsl", "en", "clinical/models")
        .setInputCols(["sentence", "token", "embeddings"])
        .setOutputCol("ner"),
        NerConverter()
        .setInputCols(["sentence", "token", "ner"])
        .setOutputCol("ner_chunk"),
        Chunk2Doc().setInputCols(["ner_chunk"]).setOutputCol("ner_chunk_doc"),
        BertSentenceEmbeddings.pretrained(
            "sbiobert_base_cased_mli", "en", "clinical/models"
        )
        .setInputCols(["ner_chunk_doc"])
        .setOutputCol("sbert_embeddings"),
        SentenceEntityResolverModel.pretrained(
            "sbiobertresolve_icdo_augmented", "en", "clinical/models"
        )
        .setInputCols(["sbert_embeddings"])
        .setOutputCol("icdo_code")
        .setDistanceFunction("EUCLIDEAN"),
    ]
    icdo_model = Pipeline(stages=icdo_stages).fit(
        spark.createDataFrame([[""]]).toDF("text")
    )
    resolver_pipelines["icdo"] = LightPipeline(icdo_model)
    print(f"[startup] ICD-O resolver loaded in {time.time()-t0:.1f}s")
except Exception as e:
    FAILED["resolve/icdo"] = str(e)
    print(f"[startup] FAILED ICD-O resolver: {e}")


# ── Load Sentence Embedding Pipeline (sbiobert) ─────────────────────────────
print("[startup] === Loading sentence embeddings ===")
try:
    t0 = time.time()
    sbert_stages = [
        DocumentAssembler().setInputCol("text").setOutputCol("document"),
        BertSentenceEmbeddings.pretrained(
            "sbiobert_base_cased_mli", "en", "clinical/models"
        )
        .setInputCols(["document"])
        .setOutputCol("sbert_embeddings"),
    ]
    sbert_model = Pipeline(stages=sbert_stages).fit(
        spark.createDataFrame([[""]]).toDF("text")
    )
    sbert_pipeline = sbert_model  # Use DataFrame transform, not LightPipeline (embeddings get stripped)
    print(f"[startup] sbiobert_base_cased_mli loaded in {time.time()-t0:.1f}s")
except Exception as e:
    FAILED["embed/text"] = str(e)
    print(f"[startup] FAILED sbiobert embeddings: {e}")
    sbert_pipeline = None
# ── Load DEID Pipeline ───────────────────────────────────────────────────────
print("[startup] === Loading DEID pipeline ===")
deid_pipeline = safe_load("deid", load_pretrained, "clinical_deidentification")

# ── Load Clinical Sections Classifier ─────────────────────────────────────────
print("[startup] === Loading sections classifier ===")
try:
    t0 = time.time()
    sec_stages = [
        DocumentAssembler().setInputCol("text").setOutputCol("document"),
        Tokenizer().setInputCols(["document"]).setOutputCol("token"),
        MedicalBertForSequenceClassification.pretrained(
            "bert_sequence_classifier_clinical_sections", "en", "clinical/models"
        )
        .setInputCols(["document", "token"])
        .setOutputCol("class"),
    ]
    sec_model = Pipeline(stages=sec_stages).fit(
        spark.createDataFrame([[""]]).toDF("text")
    )
    sections_pipeline = LightPipeline(sec_model)
    print(f"[startup] sections classifier loaded in {time.time()-t0:.1f}s")
except Exception as e:
    FAILED["classify/sections"] = str(e)
    print(f"[startup] FAILED sections classifier: {e}")
    sections_pipeline = None

# ── Load Relation Extraction ──────────────────────────────────────────────────
print("[startup] === Loading relation extraction ===")
relation_pipelines = {}

# re_clinical: Treatment↔Problem, Test↔Problem (uses ner_clinical_large)
try:
    t0 = time.time()
    re_stages = [
        DocumentAssembler().setInputCol("text").setOutputCol("document"),
        SentenceDetectorDLModel.pretrained(
            "sentence_detector_dl_healthcare", "en", "clinical/models"
        )
        .setInputCols(["document"])
        .setOutputCol("sentence"),
        Tokenizer().setInputCols(["sentence"]).setOutputCol("token"),
        WordEmbeddingsModel.pretrained(
            "embeddings_clinical", "en", "clinical/models"
        )
        .setInputCols(["sentence", "token"])
        .setOutputCol("embeddings"),
        MedicalNerModel.pretrained("ner_clinical_large", "en", "clinical/models")
        .setInputCols(["sentence", "token", "embeddings"])
        .setOutputCol("ner"),
        NerConverter()
        .setInputCols(["sentence", "token", "ner"])
        .setOutputCol("ner_chunk"),
        PerceptronModel.pretrained("pos_clinical", "en", "clinical/models")
        .setInputCols(["sentence", "token"])
        .setOutputCol("pos_tags"),
        DependencyParserModel.pretrained("dependency_conllu", "en")
        .setInputCols(["sentence", "pos_tags", "token"])
        .setOutputCol("dependencies"),
        RelationExtractionModel.pretrained("re_clinical", "en", "clinical/models")
        .setInputCols(["embeddings", "pos_tags", "ner_chunk", "dependencies"])
        .setOutputCol("relations"),
    ]
    re_model = Pipeline(stages=re_stages).fit(
        spark.createDataFrame([[""]]).toDF("text")
    )
    relation_pipelines["clinical"] = LightPipeline(re_model)
    print(f"[startup] re_clinical loaded in {time.time()-t0:.1f}s")
except Exception as e:
    FAILED["relation/clinical"] = str(e)
    print(f"[startup] FAILED re_clinical: {e}")

# posology_re: DRUG↔DOSAGE/FREQUENCY/ROUTE/FORM/STRENGTH/DURATION
# Uses PosologyREModel — a built-in rule-based model (not downloaded).
# Loaded lazily on first call to avoid OOM at startup.
_posology_re_loaded = False

def _load_posology_re():
    """Lazy-load posology_re pipeline on first use."""
    global _posology_re_loaded
    if _posology_re_loaded:
        return
    try:
        t0 = time.time()
        # "posology_re" is the correct name — returns built-in PosologyREModel()
        # "re_posology" does NOT exist and returns None
        re_model = RelationExtractionModel.pretrained("posology_re", "en", "clinical/models")
        re_pos_stages = [
            DocumentAssembler().setInputCol("text").setOutputCol("document"),
            SentenceDetectorDLModel.pretrained(
                "sentence_detector_dl_healthcare", "en", "clinical/models"
            )
            .setInputCols(["document"])
            .setOutputCol("sentence"),
            Tokenizer().setInputCols(["sentence"]).setOutputCol("token"),
            WordEmbeddingsModel.pretrained(
                "embeddings_clinical", "en", "clinical/models"
            )
            .setInputCols(["sentence", "token"])
            .setOutputCol("embeddings"),
            MedicalNerModel.pretrained("ner_posology_large", "en", "clinical/models")
            .setInputCols(["sentence", "token", "embeddings"])
            .setOutputCol("ner"),
            NerConverter()
            .setInputCols(["sentence", "token", "ner"])
            .setOutputCol("ner_chunk"),
            PerceptronModel.pretrained("pos_clinical", "en", "clinical/models")
            .setInputCols(["sentence", "token"])
            .setOutputCol("pos_tags"),
            DependencyParserModel.pretrained("dependency_conllu", "en")
            .setInputCols(["sentence", "pos_tags", "token"])
            .setOutputCol("dependencies"),
            re_model
            .setInputCols(["embeddings", "pos_tags", "ner_chunk", "dependencies"])
            .setOutputCol("relations"),
        ]
        re_pos_model = Pipeline(stages=re_pos_stages).fit(
            spark.createDataFrame([[""]]).toDF("text")
        )
        relation_pipelines["posology"] = LightPipeline(re_pos_model)
        _posology_re_loaded = True
        print(f"[lazy-load] posology_re loaded in {time.time()-t0:.1f}s")
    except Exception as e:
        print(f"[lazy-load] FAILED posology_re: {e}")

# backward compat alias
relation_pipeline = relation_pipelines.get("clinical")

# ── Startup Summary ───────────────────────────────────────────────────────────
print(f"\n[startup] === READY (GPU) ===")
print(f"  NER models:  {list(ner_pipelines.keys())}")
print(f"  Resolvers:   {list(resolver_pipelines.keys())}")
print(f"  DEID:        {'OK' if deid_pipeline else 'FAILED'}")
print(f"  Sections:    {'OK' if sections_pipeline else 'FAILED'}")
print(f"  Relations:   {list(relation_pipelines.keys()) if relation_pipelines else 'FAILED'}")
if FAILED:
    print(f"  FAILED:      {list(FAILED.keys())}")
print()


# ══════════════════════════════════════════════════════════════════════════════
# FastAPI
# ══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Spark NLP Healthcare API",
    description="NER, Resolution, DEID, Classification, and Relation Extraction for json-ocr-demo webinar",
    version="3.0.0",
)


class TextRequest(BaseModel):
    text: str


class EnrichRequest(BaseModel):
    text: str
    ner_models: List[str] = ["jsl"]
    resolve_systems: List[str] = ["icd10", "rxnorm", "snomed"]
    do_relations: bool = False
    relation_models: List[str] = []  # e.g. ["clinical", "posology"]


class BatchEnrichRequest(BaseModel):
    items: List[EnrichRequest]


class EmbedTextRequest(BaseModel):
    texts: List[str]

# ── Helper: extract NER results ──────────────────────────────────────────────

def extract_ner_results(result, has_assertion=False):
    """Parse LightPipeline fullAnnotate output into clean JSON."""
    entities = []
    chunks = result.get("ner_chunk", [])
    assertions = result.get("assertion", []) if has_assertion else []

    for i, chunk in enumerate(chunks):
        e = {
            "chunk": chunk.result,
            "label": chunk.metadata.get("entity", "UNKNOWN"),
            "begin": chunk.begin,
            "end": chunk.end,
            "sentence_id": chunk.metadata.get("sentence", "0"),
        }
        if has_assertion and i < len(assertions):
            e["assertion"] = assertions[i].result
        entities.append(e)
    return entities


def extract_resolver_results(result):
    """Parse resolver pipeline fullAnnotate output into clean JSON."""
    resolutions = []
    # Try common output column names
    for col_name in result:
        if "resolver" in col_name or "code" in col_name or "resolution" in col_name:
            for ann in result[col_name]:
                meta = ann.metadata if hasattr(ann, "metadata") else {}
                resolutions.append({
                    "chunk": meta.get("chunk", meta.get("ner_chunk", ann.result)),
                    "code": ann.result,
                    "description": meta.get("all_k_results", "").split(":::")[0] if meta.get("all_k_results") else "",
                    "confidence": float(meta.get("confidence", meta.get("all_k_distances", "0").split(":::")[0] or "0")),
                    "label": meta.get("entity", meta.get("ner_label", "")),
                })

    # Also include NER chunks for context
    ner_entities = []
    for col_name in result:
        if "ner_chunk" in col_name or col_name == "ner_chunk":
            for chunk in result[col_name]:
                ner_entities.append({
                    "chunk": chunk.result,
                    "label": chunk.metadata.get("entity", "UNKNOWN"),
                    "begin": chunk.begin,
                    "end": chunk.end,
                })
    return resolutions, ner_entities


# ── Health & Info ─────────────────────────────────────────────────────────────

@app.get("/")
@app.get("/health")
def health():
    return {
        "status": "ok",
        "gpu": True,
        "ner_models": list(ner_pipelines.keys()),
        "resolvers": list(resolver_pipelines.keys()),
        "deid": deid_pipeline is not None,
        "sections": sections_pipeline is not None,
        "relations": list(relation_pipelines.keys()),
        "failed": list(FAILED.keys()) if FAILED else [],
    }


@app.get("/models")
def models():
    return {
        "ner": {k: NER_CONFIGS[k][0] for k in ner_pipelines},
        "resolvers": {k: RESOLVER_CONFIGS.get(k, "manual") for k in resolver_pipelines},
        "deid": "clinical_deidentification" if deid_pipeline else None,
        "sections": "bert_sequence_classifier_clinical_sections" if sections_pipeline else None,
        "relations": {"clinical": "re_clinical", "posology": "re_posology"} if relation_pipelines else None,
        "failed": FAILED,
    }


# ── NER Endpoints ─────────────────────────────────────────────────────────────

@app.post("/ner/{model_name}")
def ner(model_name: str, request: TextRequest):
    """Run NER. model_name: deid|jsl|clinical|posology|radiology|anatomy"""
    if model_name not in ner_pipelines:
        raise HTTPException(404, f"NER model {model_name} not loaded. Available: {list(ner_pipelines.keys())}")

    has_assertion = NER_CONFIGS.get(model_name, (None, False))[1]
    result = ner_pipelines[model_name].fullAnnotate(request.text)[0]
    entities = extract_ner_results(result, has_assertion)
    return {"entities": entities, "entity_count": len(entities), "model": NER_CONFIGS[model_name][0]}


# ── Resolver Endpoints ────────────────────────────────────────────────────────

@app.post("/resolve/{system}")
def resolve(system: str, request: TextRequest):
    """Resolve entities to codes. system: icd10|rxnorm|snomed|umls|loinc|icdo"""
    if system not in resolver_pipelines:
        raise HTTPException(404, f"Resolver {system} not loaded. Available: {list(resolver_pipelines.keys())}")

    pipeline = resolver_pipelines[system]

    # LightPipeline (manual, e.g. ICD-O) vs PretrainedPipeline
    if isinstance(pipeline, LightPipeline):
        result = pipeline.fullAnnotate(request.text)[0]
    else:
        result = pipeline.fullAnnotate(request.text)[0]

    resolutions, ner_entities = extract_resolver_results(result)
    return {
        "resolutions": resolutions,
        "resolution_count": len(resolutions),
        "ner_entities": ner_entities,
        "system": system,
    }


# ── DEID Endpoint ─────────────────────────────────────────────────────────────

@app.post("/deid")
def deid(request: TextRequest):
    """De-identify clinical text."""
    if not deid_pipeline:
        raise HTTPException(503, "DEID pipeline not loaded")

    result = deid_pipeline.fullAnnotate(request.text)[0]
    obfuscated = result.get("obfuscated", [])
    deid_text = obfuscated[0].result if obfuscated and hasattr(obfuscated[0], "result") else request.text

    ner_chunks = result.get("ner_chunk", [])
    entities = []
    for chunk in ner_chunks:
        entities.append({
            "chunk": chunk.result,
            "label": chunk.metadata.get("entity", "UNKNOWN"),
            "begin": chunk.begin,
            "end": chunk.end,
        })

    return {
        "original": request.text,
        "deidentified": deid_text,
        "entities": entities,
        "entity_count": len(entities),
    }


# ── Sections Classifier Endpoint ──────────────────────────────────────────────

@app.post("/classify/sections")
def classify_sections(request: TextRequest):
    """Classify clinical text into section types."""
    if not sections_pipeline:
        raise HTTPException(503, "Sections classifier not loaded")

    result = sections_pipeline.fullAnnotate(request.text)[0]
    classes = result.get("class", [])
    classifications = []
    for c in classes:
        classifications.append({
            "label": c.result,
            "confidence": float(c.metadata.get("confidence", 0)),
        })
    return {"classifications": classifications}


# ── Relation Extraction Endpoint ──────────────────────────────────────────────

@app.post("/relation")
@app.post("/relation/{model_name}")
def relation(request: TextRequest, model_name: str = "clinical"):
    """Extract relations. model_name: clinical (Treatment↔Problem) | posology (Drug↔Dosage/Freq/Route)."""
    if model_name == "posology" and "posology" not in relation_pipelines:
        _load_posology_re()
    if model_name not in relation_pipelines:
        raise HTTPException(404, f"Relation model '{model_name}' not loaded. Available: {list(relation_pipelines.keys())}")

    result = relation_pipelines[model_name].fullAnnotate(request.text)[0]

    # NER entities
    entities = extract_ner_results(result, has_assertion=False)

    # Relations
    relations = []
    for rel in result.get("relations", []):
        meta = rel.metadata if hasattr(rel, "metadata") else {}
        relations.append({
            "relation": rel.result,
            "entity1": meta.get("chunk1", ""),
            "entity1_label": meta.get("entity1", ""),
            "entity2": meta.get("chunk2", ""),
            "entity2_label": meta.get("entity2", ""),
            "confidence": float(meta.get("confidence", 0)),
        })

    return {
        "entities": entities,
        "relations": relations,
        "relation_count": len(relations),
    }


# ── Combined Enrich Endpoint ─────────────────────────────────────────────────

def _resolve_one(system, text):
    """Run a single resolver. Used for parallel execution."""
    if system not in resolver_pipelines:
        return system, []
    pipeline = resolver_pipelines[system]
    ann = pipeline.fullAnnotate(text)[0]
    resolutions, _ = extract_resolver_results(ann)
    return system, resolutions


def _enrich_single(text, ner_models, resolve_systems, do_relations, relation_models=None):
    """Run all requested NER + resolvers + relations on a single text.
    Resolvers run in parallel (they are the bottleneck: ~2-3s each)."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    result = {"entities": [], "codes": {}, "relations": []}

    # NER (fast on GPU, ~0.5s each)
    for model_name in ner_models:
        if model_name not in ner_pipelines:
            continue
        has_assertion = NER_CONFIGS.get(model_name, (None, False))[1]
        ann = ner_pipelines[model_name].fullAnnotate(text)[0]
        ents = extract_ner_results(ann, has_assertion)
        for e in ents:
            e["_ner_model"] = model_name
        result["entities"].extend(ents)

    # Resolvers (slow, ~2-3s each — run in PARALLEL)
    valid_systems = [s for s in resolve_systems if s in resolver_pipelines]
    if valid_systems:
        with ThreadPoolExecutor(max_workers=len(valid_systems)) as pool:
            futures = {pool.submit(_resolve_one, s, text): s for s in valid_systems}
            for future in as_completed(futures):
                system, resolutions = future.result()
                if resolutions:
                    result["codes"][system] = resolutions

    # Relations (fast on GPU, ~0.7s each)
    # Support both do_relations (backward compat → runs "clinical") and relation_models list
    re_to_run = []
    if relation_models:
        # Lazy-load posology if requested
        if "posology" in relation_models and "posology" not in relation_pipelines:
            _load_posology_re()
        re_to_run = [m for m in relation_models if m in relation_pipelines]
    elif do_relations and relation_pipelines:
        re_to_run = ["clinical"] if "clinical" in relation_pipelines else []

    for re_name in re_to_run:
        ann = relation_pipelines[re_name].fullAnnotate(text)[0]
        for rel in ann.get("relations", []):
            meta = rel.metadata if hasattr(rel, "metadata") else {}
            result["relations"].append({
                "relation": rel.result,
                "entity1": meta.get("chunk1", ""),
                "entity1_label": meta.get("entity1", ""),
                "entity2": meta.get("chunk2", ""),
                "entity2_label": meta.get("entity2", ""),
                "confidence": float(meta.get("confidence", 0)),
                "_re_model": re_name,
            })

    return result

@app.post("/enrich")
def enrich(request: EnrichRequest):
    """Combined endpoint: run NER + resolvers + relations in one call.
    Avoids 6 separate HTTP round-trips per document."""
    return _enrich_single(request.text, request.ner_models,
                          request.resolve_systems, request.do_relations,
                          request.relation_models)


@app.post("/enrich/batch")
def enrich_batch(request: BatchEnrichRequest):
    """Batch enrichment: process multiple texts in one HTTP call."""
    results = []
    for item in request.items:
        results.append(_enrich_single(item.text, item.ner_models,
                                      item.resolve_systems, item.do_relations,
                                      item.relation_models))
    return {"results": results, "count": len(results)}


# ── Sentence Embedding Endpoint ──────────────────────────────────────────────

@app.post("/embed/text")
def embed_text(request: EmbedTextRequest):
    """Generate clinical sentence embeddings using sbiobert_base_cased_mli (768-dim)."""
    if not sbert_pipeline:
        raise HTTPException(503, "Sentence embedding pipeline not loaded")

    # Must use DataFrame transform — LightPipeline strips embedding vectors
    rows = [[t] for t in request.texts]
    df = spark.createDataFrame(rows, ["text"])
    result_df = sbert_pipeline.transform(df)
    rows = result_df.select("sbert_embeddings").collect()

    embeddings = []
    for row in rows:
        anns = row[0]
        if anns:
            vec = list(anns[0].embeddings)
            # L2 normalize
            norm = sum(x * x for x in vec) ** 0.5
            if norm > 0:
                vec = [x / norm for x in vec]
            embeddings.append(vec)
        else:
            embeddings.append([0.0] * 768)

    return {
        "embeddings": embeddings,
        "model": "sbiobert_base_cased_mli",
        "dim": 768,
    }
