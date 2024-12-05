## Output Format


## JSON Format

```json
{
    "predictions": [
        [
            {
                "ner_chunk": "Named entity chunk",
                "begin": Start_Index,
                "end": End_Index,
                "ner_label": "Label",
                "ner_confidence": "Confidence_Score",
                "code": "Code",
                "resolution": "Resolution",
                "all_k_codes": "Code1:::Code2:::Code3:::...",
                "all_k_resolutions": "Resolution1:::Resolution2:::Resolution3:::...",
                "all_k_distances": "Distance1:::Distance2:::Distance3:::...",
            },
            {
                "ner_chunk": "Named entity chunk",
                "begin": Start_Index,
                "end": End_Index,
                "ner_label": "Label",
                "ner_confidence": "Confidence_Score",
                "code": "Code",
                "resolution": "Resolution",
                "all_k_codes": "Code1:::Code2:::Code3:::...",
                "all_k_resolutions": "Resolution1:::Resolution2:::Resolution3:::...",
                "all_k_distances": "Distance1:::Distance2:::Distance3:::...",
            }
            // Additional predictions for input 1...
        ],
         // Additional predictions for other inputs...
    ]
}

```


### JSON Lines (JSONL) Format

```
{"predictions": [{"ner_chunk": "Named entity chunk", "begin": Start_Index, "end": End_Index, "ner_label": "Label", "ner_confidence": "Confidence_Score", "code": "Code", "resolution": "Resolution", "all_k_codes": "Code1:::Code2:::Code3:::...", "all_k_resolutions": "Resolution1:::Resolution2:::Resolution3:::...", "all_k_distances": "Distance1:::Distance2:::Distance3:::..."}, ...]}
{"predictions": [{"ner_chunk": "Named entity chunk", "begin": Start_Index, "end": End_Index, "ner_label": "Label", "ner_confidence": "Confidence_Score", "code": "Code", "resolution": "Resolution", "all_k_codes": "Code1:::Code2:::Code3:::...", "all_k_resolutions": "Resolution1:::Resolution2:::Resolution3:::...", "all_k_distances": "Distance1:::Distance2:::Distance3:::..."}, ...]}
```

The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text.


### Explanation of Fields

  - **ner_chunk**: The text of the entity.
  - **begin**: The index of the beginning of the entity in the text.
  - **end**: The index of the end of the entity in the text.
  - **ner_label**: The label of the entity, as determined by the NER model.
  - **ner_confidence**: The confidence score of the NER model in identifying this entity.
  - **code**: The code of the term.
  - **resolution**: The resolved text of the term.
  - **all_k_codes**: All the codes found found in HCPCS taxonomy, separated by three colons (`:::`), sorted from most to least similar.
  - **all_k_resolutions**: All the terms found in HCPCS taxonomy, separated by three colons (`:::`), sorted from most to least similar.
  - **all_k_distances**: All k distances, separated by three colons (`:::`), corresponding to each resolution.