<p align="center">
  <a href="https://johnsnowlabs.com"><img src="https://nlp.johnsnowlabs.com/assets/images/logo.png" width="300"/></a>
</p>

<p align="center">
  <a href="https://colab.research.google.com/github/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/vlm-workshop/"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>
  <a href="https://github.com/JohnSnowLabs/spark-nlp/blob/master/LICENSE"><img src="https://img.shields.io/github/license/JohnSnowLabs/spark-nlp.svg" alt="License"/></a>
  <a href="https://sparknlp.slack.com"><img src="https://img.shields.io/badge/Slack-join-green.svg?logo=slack" alt="Slack"/></a>
</p>

# Benchmarking Medical VLMs: 10 Clinical Use Cases for Automated Document Understanding

> Transform unstructured visual data — handwritten intake forms, pathology slides, ECG tracings, invoices — into structured, regulatory-grade JSON in seconds. Fully on-prem, no patient data leaves your environment.

This repository contains **9 interactive notebooks** demonstrating zero-shot structured extraction across medical and financial document types using John Snow Labs Medical Visual Language Models, OCR, NLP, and image embeddings.

---

## Notebooks

| # | Notebook | Use Cases | Key Result |
|:-:|----------|-----------|------------|
| 1 | [Visual De-Identification](1.visual_deid.ipynb) | PHI redaction from scanned clinical forms + handwritten Rx extraction | **100% PHI recall** (494/494 entities), 3.1 sec/doc |
| 2 | [Visual Document Mining & Routing](2.visual_document_mining_and_routing.ipynb) | Automated chart sorting + intake form routing by clinical urgency | **71.6% doc-type accuracy**, < 5 sec/doc |
| 3 | [Medical RAG](3.medical_rag.ipynb) | Cross-modal search engine: text, image, and hybrid queries over 10 doc types | **115 docs indexed**, sub-second retrieval, VLM + OCR + NLP integration |
| 4 | [Dermatology RAG](4.dermatology_rag.ipynb) | Skin lesion classification + visual case matching + ICD-10 coding | **8-class classification**, binary malignant screening, Precision@5 |
| 5 | [Radiology RAG](5.radiology_rag.ipynb) | CXR finding classification + MSK body part identification + radiology NER | **80% retrieval Precision@5**, 95% pneumonia recall |
| 6 | [Pathology RAG](6.pathology_rag.ipynb) | Breast cancer screening + tissue classification + WBC typing + ICD-O coding | **2,962 images indexed**, 3 pathology workflows |
| 7 | [ECG Waveform Analysis](7.ecg_waveform_analysis.ipynb) | Extract cardiac measurements from scanned paper ECGs | **MAE ±8.5 bpm HR**, matches Claude Sonnet and GPT-4.1 |
| 8 | [KYC Identity Verification](8.kyc_id_verification.ipynb) | Multilingual ID document extraction + transliteration (10 countries) | **81.2% expiry date accuracy**, 21 fields extracted |
| 9 | [Invoice & Expense Intelligence](9.invoice_expense_processing.ipynb) | Invoice extraction + multilingual receipts + policy violation detection | **99% vendor accuracy**, matches Claude Sonnet 4 |

---

## Architecture

All models run on-prem via **JSL Docker containers + vLLM** — no cloud API calls with patient data.



### Models

| Model | What It Does | Port |
|-------|-------------|:----:|
| InternVL 1B | Fast VLM — structured extraction | 9460 |
| jsl_vision_ocr_parsing_1_0 | OCR with pixel-level bounding boxes | 9461 |
| JSL-MedicalVL 7B | Medical VLM — balanced | 9462 |
| jsl_vision_embed_crossmodal_1.0 | Image embeddings (1024-dim) for visual similarity | 9464 |
| JSL-MedicalVL 30B | Flagship medical VLM — matches GPT-4.1 / Claude | 9465 |
| jsl_vision_ocr_1.0 | Best accuracy VLM — structured extraction | 9466 |
| Spark NLP for Healthcare | NER, ICD-10/RxNorm/SNOMED coding, DEID, relations | 9470 |
| sbiobert | Clinical text embeddings (768-dim) for semantic search | via 9470 |

---

## Quick Start

### 1. Clone

```bash
git clone https://github.com/JohnSnowLabs/spark-nlp-workshop.git
cd spark-nlp-workshop/visual-llm-workshop
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Model Servers

All models are served via [vLLM](https://github.com/vllm-project/vllm) with OpenAI-compatible APIs. See [`docs/infra.md`](docs/infra.md) for full setup instructions.

### 4. Run Notebooks

```bash
jupyter lab
```

Open any notebook — cached results are included, so notebooks render fully without running inference. Set `USE_CACHE = False` to re-run with your own models.

---

## Accuracy vs Enterprise Models

jsl_vision_ocr_1.0 was benchmarked against Claude Sonnet 4 and GPT-4.1 on invoice extraction:

| Metric | jsl_vision_ocr_1.0 | Claude Sonnet 4 | GPT-4.1 |
|--------|:---:|:---:|:---:|
| Vendor name (SROIE) | **99%** | 82% | failed |
| Total amount (SROIE) | **100%** | **100%** | failed |
| Item name match (CORD) | **98%** | 93% | failed |

JSL-MedicalVL 30B matches Claude Sonnet and GPT-4.1 on ECG measurement extraction — fully on-prem.

---

## Datasets

All notebooks use publicly available datasets from Hugging Face and local synthetic data. See [`docs/datasets.md`](docs/datasets.md) for the full registry with links, licenses, and sample counts.

Key datasets:
- [JSL pdf-deid-dataset](https://github.com/JohnSnowLabs/pdf-deid-dataset) — 50 synthetic medical PDFs with PHI ground truth
- [SROIE-2019](https://huggingface.co/datasets/rth/sroie-2019-v2) — 973 receipts with vendor/date/total GT
- [CORD-v2](https://huggingface.co/datasets/naver-clova-ix/cord-v2) — 1,000 multilingual receipts with menu item GT
- [ISIC2019](https://huggingface.co/datasets/MKZuziak/ISIC_2019_224) — 25K dermoscopy images, 8 diagnostic classes
- [NIH Chest X-ray](https://huggingface.co/datasets/alkzar90/NIH-Chest-X-ray-dataset) — 112K X-rays, 14 disease classes
- [GenECG](https://huggingface.co/datasets/edcci/GenECG) — 43K synthetic 12-lead ECG paper tracings
- [OmniMedVQA](https://huggingface.co/datasets/OpenGVLab/OmniMedVQA) — 118K medical images, 42 modalities
- [MIDV-2020](https://arxiv.org/abs/2107.00396) — 3,000 identity documents, 10 countries

---

## Project Structure

```
├── 1.visual_deid.ipynb                          # PHI redaction
├── 2.visual_document_mining_and_routing.ipynb   # Chart sorting + routing
├── 3.medical_rag.ipynb                          # Cross-modal medical search
├── 4.dermatology_rag.ipynb                      # Skin lesion RAG
├── 5.radiology_rag.ipynb                        # CXR + MSK X-ray RAG
├── 6.pathology_rag.ipynb                        # Histopathology + blood RAG
├── 7.ecg_waveform_analysis.ipynb                # Paper ECG digitization
├── 8.kyc_id_verification.ipynb                  # Multilingual ID extraction
├── 9.invoice_expense_processing.ipynb           # Invoice + expense automation

```

---

## Links

| | |
|---|---|
| **John Snow Labs** | [johnsnowlabs.com](https://www.johnsnowlabs.com/) |
| **Models Hub** | [nlp.johnsnowlabs.com/models](https://nlp.johnsnowlabs.com/models) |
| **Spark NLP** | [github.com/JohnSnowLabs/spark-nlp](https://github.com/JohnSnowLabs/spark-nlp) |
| **Schedule a Demo** | [johnsnowlabs.com/schedule-a-demo](https://www.johnsnowlabs.com/schedule-a-demo/) |
| **Slack** | [spark-nlp.slack.com](https://join.slack.com/t/spark-nlp/shared_invite/zt-198dipu77-L3UWNe_AJ8xqDk0ivmih5Q) |
| **Applied AI Summit** | [nlpsummit.org](https://www.nlpsummit.org) |

---

## License

This project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). Individual datasets may have their own licenses.
