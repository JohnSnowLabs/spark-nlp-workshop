

## Output Format

### JSON Format

```json
{
{
    "predictions": [
        {
            "document": "Text of the document 1",
            "ner_chunk": "Named Entity 1",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label 1",
            "ner_confidence": Score,
            "ade": "ADE",
            "rxnorm_code": "RxNorm Code",
            "action": "Action",
            "treatment": "Treatment",
            "umls_code": "UMLS Code",
            "snomed_ct_code": "SNOMED CT Code",
            "product_ndc": "Product NDC Code",
            "package_ndc": "Package NDC Code"
        },
        {
            "document": "Text of the document 1",
            "ner_chunk": "Named Entity 2",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label 2",
            "ner_confidence": Score,
            "ade": "ADE",
            "rxnorm_code": "RxNorm Code",
            "action": "Action",
            "treatment": "Treatment",
            "umls_code": "UMLS Code",
            "snomed_ct_code": "SNOMED CT Code",
            "product_ndc": "Product NDC Code",
            "package_ndc": "Package NDC Code"
        },

        {
            "document": "Text of the document 2",
            "ner_chunk": "Named Entity 1",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label 2",
            "ner_confidence": Score,
            "ade": "ADE",
            "rxnorm_code": "RxNorm Code",
            "action": "Action",
            "treatment": "Treatment",
            "umls_code": "UMLS Code",
            "snomed_ct_code": "SNOMED CT Code",
            "product_ndc": "Product NDC Code",
            "package_ndc": "Package NDC Code"
        },
        ...
    ]
}

```

#### Explanation of Fields

- **predictions**: An array containing predictions for each input document.

  - **document**: The original input text for which predictions are made.

  - **ner_chunk**: Named entity recognized in the document.

  - **begin**: Starting character index of the named entity chunk within the document.

  - **end**: Ending character index of the named entity chunk within the document.

  - **ner_label**: Label assigned to the named entity.

  - **ner_confidence**: Confidence score of the named entity recognition.

  - **ade**: Adverse Drug Event (ADE).

  - **rxnorm_code**: RxNorm code.

  - **action**: Action.

  - **treatment**: Treatment.

  - **umls_code**: UMLS code.

  - **snomed_ct_code**: SNOMED CT Code.

  - **product_ndc**: Product NDC code.

  - **package_ndc**: Package NDC code.


### JSON Lines (JSONL) Format

```
{"predictions": [{"ner_chunk": "Named Entity 1", "begin": "Start Index", "end": "End Index", "ner_label": "Label 1", "ner_confidence": "Score", "ade": "ADE", "rxnorm_code": "RxNorm Code", "action": "Action", "treatment": "Treatment", "umls_code": "UMLS Code", "snomed_ct_code": "SNOMED CT Code", "product_ndc": "Product NDC Code", "package_ndc": "Package NDC Code"}, {"ner_chunk": "Named Entity 2", "begin": "Start Index", "end": "End Index", "ner_label": "Label 2", "ner_confidence": "Score", "ade": "ADE", "rxnorm_code": "RxNorm Code", "action": "Action", "treatment": "Treatment", "umls_code": "UMLS Code", "snomed_ct_code": "SNOMED CT Code", "product_ndc": "Product NDC Code", "package_ndc": "Package NDC Code"}, ...]}
{"predictions": [{"ner_chunk": "Named Entity 1", "begin": "Start Index", "end": "End Index", "ner_label": "Label 2", "ner_confidence": "Score", "ade": "ADE", "rxnorm_code": "RxNorm Code", "action": "Action", "treatment": "Treatment", "umls_code": "UMLS Code", "snomed_ct_code": "SNOMED CT Code", "product_ndc": "Product NDC Code", "package_ndc": "Package NDC Code"}, ...]}
```


The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text.