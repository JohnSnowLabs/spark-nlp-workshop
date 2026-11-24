## Output Format

Every request returns one JSON object. The object depends on what the request ran: the **decision** model, a **guard**, or the **ensemble**. The `model` field of the response names what ran.

In a batch transform job, the result of each input file is written to a file with the same name and the extension `.out` in the output folder.

---

### 1. Decision

**Fields:**

- **`model`** (string):
  Always `"Medical-DM-Small"`.
- **`answers`** (object):
  One answer for each question of the request, under the name of the question. The fields of an answer depend on the `type` of the question:

  | `type` | Fields |
  |---|---|
  | `noul` (yes/no) | **`noul`** (float): the probability that the answer is yes |
  | `choice` | **`choice`** (string): the most likely option. **`confidence`** (float): 0 when all options are equally likely, 1 when the model is certain. **`probabilities`** (object): a probability for every option |
  | `score` | **`score`** (float): the expected level, a number from 0 to the number of levels minus 1. **`probabilities`** (object): a probability for every level, under the position of the level in `criteria` (`"0"`, `"1"`, ...) |

  Probabilities are rounded to 4 decimals. The probabilities of the options of a question add up to 1.
- **`usage`** (object):
  - **`input_tokens`** (integer): Number of tokens read, over all questions.
  - **`output_tokens`** (integer): Number of answers.

**Example:**

```json
{
  "model": "Medical-DM-Small",
  "answers": {
    "severity": {
      "type": "score",
      "score": 2.9974,
      "probabilities": {
        "0": 0.0,
        "1": 0.0,
        "2": 0.0026,
        "3": 0.9974
      }
    },
    "organ": {
      "type": "choice",
      "choice": "infection",
      "confidence": 0.9957,
      "probabilities": {
        "respiratory": 0.001,
        "circulation": 0.0023,
        "kidney": 0.0002,
        "infection": 0.9965,
        "none": 0.0
      }
    },
    "anticoagulated": {
      "type": "noul",
      "noul": 0.9986
    }
  },
  "usage": {
    "input_tokens": 557,
    "output_tokens": 3
  }
}
```

---

### 2. Guard

**Fields:**

- **`model`** (string):
  The guard that ran: `"phi-guard-v0.7"` or `"phi-guard-v0.7-fast"`.
- **`default_cutoff`** (float):
  The cutoff of the guard. A score at or above it is a positive `label`.
- **`results`** (array):
  One result for each document, in the order of the request. Each result has:
  - **`id`**: The `id` of the document.
  - **`score`** (float), **`logit`** (float), **`label`** (boolean): The leak score: the probability that the document still holds an identifier, its logit, and whether it reaches the cutoff.
  - **`cutoffs`** (object): The same decision for the cutoff of the guard, as `{"<cutoff>": boolean}`.
  - **`harmful_score`** (float), **`harmful_logit`** (float), **`harmful_label`** (boolean): The same three values for a harmful leak.
  - **`level`** (integer): The exposure level, from 0 to 6: the number of `level_scores` that are 0.5 or more.
  - **`expected_level`** (float): The sum of `level_scores`.
  - **`level_scores`** (array of 6 floats), **`level_logits`** (array of 6 floats): The score and the logit of each exposure level.
  - **`raw_score`** (float), **`raw_logit`** (float), **`raw_label`** (boolean): The raw-note score, its logit, and whether it is 0.5 or more.
- **`usage`** (object):
  - **`docs`** (integer): Number of documents.
  - **`windows`** (integer): Number of text windows read.
  - **`ms`** (integer): Time to score the documents, in milliseconds.

An empty `text` has no windows: its scores are 0 and its logits are -100.

**Example:**

```json
{
  "model": "phi-guard-v0.7",
  "default_cutoff": 0.5,
  "results": [
    {
      "id": "note-001",
      "score": 0.0101,
      "logit": -4.5816,
      "label": false,
      "cutoffs": {
        "0.5": false
      },
      "harmful_score": 0.0028,
      "harmful_logit": -5.8852,
      "harmful_label": false,
      "level": 0,
      "expected_level": 0.0002,
      "level_scores": [0.0001, 0.0001, 0.0, 0.0, 0.0, 0.0],
      "level_logits": [-9.3833, -9.3833, -13.0165, -16.7451, -17.2214, -17.2214],
      "raw_score": 0.0,
      "raw_logit": -17.2178,
      "raw_label": false
    },
    {
      "id": "note-002",
      "score": 1.0,
      "logit": 13.5693,
      "label": true,
      "cutoffs": {
        "0.5": true
      },
      "harmful_score": 0.9995,
      "harmful_logit": 7.5929,
      "harmful_label": true,
      "level": 2,
      "expected_level": 1.7611,
      "level_scores": [1.0, 0.7593, 0.0018, 0.0, 0.0, 0.0],
      "level_logits": [15.171, 1.1487, -6.2951, -13.5947, -14.1753, -18.2097],
      "raw_score": 1.0,
      "raw_logit": 19.0585,
      "raw_label": true
    }
  ],
  "usage": {
    "docs": 2,
    "windows": 2,
    "ms": 94
  }
}
```

---

### 3. Ensemble

**Fields:**

- **`model`** (string):
  Always `"phi-guard-ensemble"`.
- **`guard`** (string):
  The guard of the ensemble: `"phi-guard-v0.7"` or `"phi-guard-v0.7-fast"`.
- **`aggregation`** (string):
  How the two scores were combined: `"mean_logit"`, `"mean"`, `"min"` or `"max"`.
- **`results`** (array):
  One result for each document, in the order of the request. Each result has:
  - **`id`**: The `id` of the document.
  - **`score`** (float), **`logit`** (float), **`label`** (boolean): The combined leak score of the guard and the decision model, its logit, and whether it is 0.5 or more.
  - **`harmful_score`** (float), **`harmful_logit`** (float), **`harmful_label`** (boolean): The same three values for a harmful leak.
  - **`decision`** (string): The route of the document: `"leak"` when the guard and the decision model both flag it, `"review"` when only one does, `"clean"` when neither does.
  - **`agreement`** (boolean): `true` when the guard and the decision model give the same answer.
  - **`members`** (object): The score of each model: **`guard_score`** (leak score of the guard), **`guard_harmful_score`** (harmful-leak score of the guard) and **`decision_score`** (probability of a left-over identifier from the decision model, or the `decision_score` of the request).
  - **`level`** (integer), **`level_scores`** (array of 6 floats), **`raw_score`** (float): The exposure level, its scores and the raw-note score of the guard, as in the guard output.
- **`usage`** (object):
  - **`docs`** (integer): Number of documents.
  - **`windows`** (integer): Number of text windows read by the guard.
  - **`decision_calls`** (integer): Number of documents that the decision model was asked about. A document with a `decision_score` in the request is not counted.
  - **`ms`** (integer): Time of the request in milliseconds.

**Example:**

```json
{
  "model": "phi-guard-ensemble",
  "guard": "phi-guard-v0.7",
  "aggregation": "mean_logit",
  "results": [
    {
      "id": "note-001",
      "score": 0.001,
      "logit": -6.8959,
      "label": false,
      "harmful_score": 0.0005,
      "harmful_logit": -7.5477,
      "harmful_label": false,
      "decision": "clean",
      "agreement": true,
      "members": {
        "guard_score": 0.0101,
        "guard_harmful_score": 0.0028,
        "decision_score": 0.0
      },
      "level": 0,
      "level_scores": [0.0001, 0.0001, 0.0, 0.0, 0.0, 0.0],
      "raw_score": 0.0
    },
    {
      "id": "note-002",
      "score": 1.0,
      "logit": 11.0431,
      "label": true,
      "harmful_score": 0.9997,
      "harmful_logit": 8.0549,
      "harmful_label": true,
      "decision": "leak",
      "agreement": true,
      "members": {
        "guard_score": 1.0,
        "guard_harmful_score": 0.9995,
        "decision_score": 0.9998
      },
      "level": 2,
      "level_scores": [1.0, 0.7593, 0.0018, 0.0, 0.0, 0.0],
      "raw_score": 1.0
    }
  ],
  "usage": {
    "docs": 2,
    "windows": 2,
    "decision_calls": 2,
    "ms": 114
  }
}
```

---

### Errors

A request that cannot be answered returns an HTTP status and a JSON body with the reason in `detail`. In a real-time call, `invoke_endpoint` raises a `ModelError` that holds the status and the body.

| Status | When |
|---|---|
| `400` | The body is not a JSON object, or it has none of the three shapes. The model name of a decision request is wrong. `docs` is empty or a document has no string `text`. The ids of the documents are not unique. `decision_score` is not a number from 0 to 1. `guard` or `aggregation` is not one of the accepted values |
| `404` | The guard in `model` does not exist |
| `413` | More documents than the limit of the request: 16,384 for a guard, 64 for the ensemble |
| `422` | The request does not follow the format (for example a wrong question `type` or `criteria`), or a row of a decision request (or a document of an ensemble request) is longer than 16,384 tokens. `detail` says which |
| `502`, `503`, `504` | The decision model gave an error, is not available, or did not answer in time |
