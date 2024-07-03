## Output Format

### JSON Format

```json
{
    "rxnorm_predictions": [
        {
            "document": "Text of the document 1",
            "ner_chunk": "Named Entity 1",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label 1",
            "ner_confidence": Score,
            "rxnorm_code": code,
            "rxnorm_resolution": "resolved text",
            "rxnorm_confidence": Score,
        },
        {
            "document": "Text of the document 1",
            "ner_chunk": "Named Entity 2",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label 2",
            "ner_confidence": Score,
            "rxnorm_code": code,
            "rxnorm_resolution": "resolved text",
            "rxnorm_confidence": Score,
        },
        ...
    ],

    "icd10cm_predictions": [
        {
            "document": "Text of the document 1",
            "ner_chunk": "Named Entity 1",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label 1",
            "ner_confidence": Score,
            "icd10cm_code": code,
            "icd10cm_resolution": "resolved text",
            "icd10cm_confidence": Score,
        },
        {
            "document": "Text of the document 1",
            "ner_chunk": "Named Entity 2",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label 2",
            "ner_confidence": Score,
            "icd10cm_code": code,
            "icd10cm_resolution": "resolved text",
            "icd10cm_confidence": Score,
        },
        ...
    ]
}


```

#### Explanation of Fields

- **rxnorm_predictions**: An array containing rxnorm predictions for each input document.

    - **document**: The original input text for which predictions are made.

    - **ner_chunk**: Named entity recognized in the document.

    - **begin**: Starting character index of the named entity chunk within the document.

    - **end**: Ending character index of the named entity chunk within the document.

    - **ner_label**: Label assigned to the named entity.

    - **ner_confidence**: Confidence score associated with Named Entity Recognition.

    - **rxnorm_code**: RxNorm code associated with the prediction.

    - **rxnorm_resolution**: This field shows the most similar term found in the RxNorm taxonomy.

    - **rxnorm_confidence**: Confidence score associated with the rxnorm_code.


- **icd10cm_predictions**: An array containing icd10cm predictions for each input document.

    - **document**: The original input text for which predictions are made.

    - **ner_chunk**: Named entity recognized in the document.

    - **begin**: Starting character index of the named entity chunk within the document.

    - **end**: Ending character index of the named entity chunk within the document.

    - **ner_label**: Label assigned to the named entity.

    - **ner_confidence**: Confidence score associated with Named Entity Recognition.

    - **icd10cm_code**: ICD-10-CM code associated with the prediction.

    - **icd10cm_resolution**: This field shows the most similar term found in the ICD-10-CM taxonomy.

    - **icd10cm_confidence**: Confidence score associated with the icd10cm_code.



### JSON Lines (JSONL) Format

```
{"rxnorm_predictions": [{"ner_chunk": "Named Entity 1", "begin": Start Index, "end": End Index, "ner_label": "Label 1", "ner_confidence": Score, "rxnorm_code": code, "rxnorm_resolution": "resolved text", "rxnorm_confidence": Score}, {"ner_chunk": "Named Entity 2", "begin": Start Index, "end": End Index, "ner_label": "Label 2", "ner_confidence": Score, "rxnorm_code": code, "rxnorm_resolution": "resolved text", "rxnorm_confidence": Score}, ...], "icd10cm_predictions": [{"ner_chunk": "Named Entity 1", "begin": Start Index, "end": End Index, "ner_label": "Label 1", "ner_confidence": Score, "icd10cm_code": code, "icd10cm_resolution": "resolved text", "icd10cm_confidence": Score}, {"ner_chunk": "Named Entity 2", "begin": Start Index, "end": End Index, "ner_label": "Label 2", "ner_confidence": Score, "icd10cm_code": code, "icd10cm_resolution": "resolved text", "icd10cm_confidence": Score}, ...]}
```

The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text.