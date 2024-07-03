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
            "mesh_code": code,
            "mesh_resolution": "resolved text",
            "mesh_confidence": Score,
        },
        {
            "document": "Text of the document 1",
            "ner_chunk": "Named Entity 2",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label 2",
            "ner_confidence": Score,
            "mesh_code": code,
            "mesh_resolution": "resolved text",
            "mesh_confidence": Score,
        },

        {
            "document": "Text of the document 2",
            "ner_chunk": "Named Entity 1",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label 2",
            "ner_confidence": Score,
            "mesh_code": code,
            "mesh_resolution": "resolved text",
            "mesh_confidence": Score,
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

    - **mesh_code**: MeSH code associated with the prediction.

    - **mesh_resolution**: This field shows the most similar term found in the MeSH taxonomy.

    - **mesh_confidence**: Confidence score associated with the mesh_code.


### JSON Lines (JSONL) Format

```
{"predictions": [{"ner_chunk": "Named Entity 1", "begin": Start Index, "end": End Index, "ner_label": "Label 1", "ner_confidence": Score, "mesh_code": code, "mesh_resolution": "resolved text", "mesh_confidence": Score}, {"ner_chunk": "Named Entity 2", "begin": Start Index, "end": End Index, "ner_label": "Label 2", "ner_confidence": Score, "mesh_code": code, "mesh_resolution": "resolved text", "mesh_confidence": Score}, ...]}
```

The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text.