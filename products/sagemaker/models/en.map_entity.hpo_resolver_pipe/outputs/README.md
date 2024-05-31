## Output Format

### JSON Format

```json
{
    "predictions": [
        {
            "document": "Text of the document 1",
            "ner_chunk": "Named Entity 1",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label 1",
            "ner_confidence": Score,
            "hpo_code": code,
            "hpo_resolution": "resolved text",
            "hpo_confidence": Score,
            "aux_labels": "other codes"
        },
        {
            "document": "Text of the document 1",
            "ner_chunk": "Named Entity 2",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label 2",
            "ner_confidence": Score,
            "hpo_code": code,
            "hpo_resolution": "resolved text",
            "hpo_confidence": Score,
            "aux_labels": "other codes"
        },

        {
            "document": "Text of the document 2",
            "ner_chunk": "Named Entity 1",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label 2",
            "ner_confidence": Score,
            "hpo_code": code,
            "hpo_resolution": "resolved text",
            "hpo_confidence": Score,
            "aux_labels": "other codes"
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

    - **ner_confidence**: Confidence score associated with Named Entity Recognition.

    - **hpo_code**: HPO code associated with the prediction.

    - **hpo_resolution**: This field shows the most similar term found in the HPO taxonomy.

    - **hpo_confidence**: Confidence score associated with the HPO code.

    - **aux_labels**: Other associated codes (MeSH, SNOMED, UMLS, ORPHA, OMIM) for the corresponding HPO code.


### JSON Lines (JSONL) Format

```
{"predictions": [{"ner_chunk": "Named Entity 1", "begin": Start Index, "end": End Index, "ner_label": "Label 1", "ner_confidence": Score, "hpo_code": code, "hpo_resolution": "resolved text", "hpo_confidence": Score, "aux_labels": "other codes"}, {"ner_chunk": "Named Entity 2", "begin": Start Index, "end": End Index, "ner_label": "Label 2", "ner_confidence": Score, "hpo_code": code, "hpo_resolution": "resolved text", "hpo_confidence": Score, "aux_labels": "other codes"}, ...]}
```

The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text. The structure of each object is similar to the JSON format explained above.