## Input Format

All requests are JSON (`application/json`) and go to the `/invocations` endpoint of the container: one request in `invoke_endpoint` for a real-time endpoint, or one file for each request in a batch transform job. The fields of the body decide what runs:

| The body has | Runs | `model` |
|---|---|---|
| `state` and `questions` | the decision model | `Medical-DM-Small` |
| `docs` | one guard | `phi-guard-v0.7` (PHI Guard v0.7) or `phi-guard-v0.7-fast` (PHI Guard v0.7 Fast) |
| `docs` | the ensemble: a guard and the decision model, combined | `phi-guard-ensemble` |

Any other body answers `400` with the three accepted shapes.

---

### 1. Decision

Answers typed questions about a medical record. For every question the model returns a probability for each option.

#### Example Payload
```json
{
    "model": "Medical-DM-Small",
    "state": {
        "age": 71,
        "sex": "female",
        "vitals": {
            "blood_pressure": "92/58",
            "heart_rate": 118,
            "temperature_c": 38.9,
            "oxygen_saturation": "91% on room air"
        },
        "labs": {
            "white_cell_count": "19.2 x10^9/L",
            "lactate": "4.1 mmol/L",
            "creatinine": "2.3 mg/dL (baseline 0.9)"
        },
        "medications": ["apixaban", "metformin", "lisinopril"],
        "complaint": "Two days of cough and fever, now confused."
    },
    "questions": {
        "severity": {
            "type": "score",
            "instructions": "How worried should the care team be about this patient right now?",
            "criteria": [
                "Stable: no concern",
                "Mild concern: watch and repeat measurements",
                "Moderate concern: needs treatment on the ward",
                "Critical: needs intensive care assessment now"
            ]
        },
        "organ": {
            "type": "choice",
            "instructions": "Which problem is the most urgent?",
            "criteria": {
                "respiratory": "Lungs and breathing",
                "circulation": "Blood pressure and perfusion",
                "kidney": "Kidney function",
                "infection": "Infection and sepsis",
                "none": "Nothing urgent"
            }
        },
        "anticoagulated": {
            "type": "noul",
            "instructions": "Is the patient taking a blood thinner?"
        }
    }
}
```

#### Fields

| Field | Description |
|---|---|
| `model` | Always `Medical-DM-Small` |
| `state` | The record. Text, a number, an object or a list. The names of the fields of an object are read as labels |
| `questions` | An object of named questions, from 1 to 64 per request. The name of a question is the key of its answer |

Each question has:

| Field | Description |
|---|---|
| `type` | `noul` (yes/no), `choice` (one option out of several) or `score` (a level on a scale) |
| `instructions` | The question, as text |
| `criteria` | For `choice`: an object with 1 to 255 options, each option name with a description. For `score`: a list of 1 to 255 level descriptions, from the lowest to the highest level. For `noul`: optional, an object with the descriptions of `true` and `false` |

A row of tokens (the record, one question and its options) must fit 16,384 tokens. A longer one answers `422` with the reason.

---

### 2. Guard

Checks de-identified documents for left-over identifiers. A guard reads whole documents.

#### Example Payload
```json
{
    "model": "phi-guard-v0.7",
    "docs": [
        {
            "id": "note-001",
            "text": "Pt [NAME] seen on [DATE] for chest pain. Troponin negative x2, ECG normal sinus rhythm. Discharged home on aspirin 81 mg daily."
        },
        {
            "id": "note-002",
            "text": "DISCHARGE SUMMARY\nPatient Maria Gonzalez, a [AGE]-year-old [GENDER], was admitted to [HOSPITAL] on [DATE] with chest pain and shortness of breath. Troponin was negative twice. Started on Lipitor 40 mg daily and aspirin 81 mg daily. Echocardiogram showed an ejection fraction of 55 percent. Follow up with cardiology in two weeks. Contact [PHONE] with any questions."
        }
    ]
}
```

#### Fields

| Field | Description |
|---|---|
| `model` | `phi-guard-v0.7` (PHI Guard v0.7) or `phi-guard-v0.7-fast` (PHI Guard v0.7 Fast). An unknown name answers `404` |
| `docs` | A list of documents, from 1 to 16,384 per request. Each document has a unique `id` (any JSON value) and a `text` (a string) |

---

### 3. Ensemble

Combines a guard and the decision model for every document.

#### Example Payload
```json
{
    "model": "phi-guard-ensemble",
    "docs": [
        {
            "id": "note-001",
            "text": "Pt [NAME] seen on [DATE] for chest pain. Troponin negative x2, ECG normal sinus rhythm. Discharged home on aspirin 81 mg daily."
        },
        {
            "id": "note-002",
            "text": "DISCHARGE SUMMARY\nPatient Maria Gonzalez, a [AGE]-year-old [GENDER], was admitted to [HOSPITAL] on [DATE] with chest pain and shortness of breath. Troponin was negative twice. Started on Lipitor 40 mg daily and aspirin 81 mg daily. Echocardiogram showed an ejection fraction of 55 percent. Follow up with cardiology in two weeks. Contact [PHONE] with any questions."
        }
    ]
}
```

#### Fields

| Field | Description |
|---|---|
| `model` | Always `phi-guard-ensemble` |
| `docs` | A list of documents as for a guard, from 1 to 64 per request. A document can also have a `decision_score` (a number from 0 to 1): the probability of a left-over identifier that you already have. The decision model is not asked for that document |
| `guard` | Optional. The guard of the ensemble: `phi-guard-v0.7` (default) or `phi-guard-v0.7-fast` |
| `aggregation` | Optional. How the two scores are combined: `mean_logit` (default), `mean`, `min` or `max` |

A document without `decision_score` is answered by the decision model of the container.

---

### Important Notes:
- **Model Name Requirement:** Always set `"model"` to one of the names above: `Medical-DM-Small`, `phi-guard-v0.7`, `phi-guard-v0.7-fast` or `phi-guard-ensemble`
- **Real-time Requests:** A real-time endpoint stops a request after 60 seconds. Send large requests as a batch transform job
- **Batch Transform:** Each input file is one request. Put one JSON body in each file
- **Patient Data:** The container does not log the content of requests
