# Output Format

## JSON Format

```json
{
  "predictions": [
    [
      {
        "begin": Start_Index,
        "end": End_Index,
        "ner_chunk": "Named entity chunk",
        "ner_label": "Label",
        "ner_confidence": "Confidence_Score",
        "concept_code": "Concept_Code",
        "resolution": "Resolution",
        "score": Cosine_Distance_Score_for_Resolution,
        "all_codes": ["Code1", "Code2", "Code3", ...],
        "concept_name_detailed": [
          "Resolution1 [Ground Truth Mapping 1]",
          "Resolution2 [Ground Truth Mapping 2]",
          "Resolution3 [Ground Truth Mapping 3]",
          ...
        ],
        "domain_id": ["Domain1", "Domain2", "Domain3", ...],
        "all_resolutions": ["Resolution1", "Resolution2", "Resolution3", ...],
        "all_score": [Score1, Score2, Score3, ...]
      }
      // Additional predictions for input 1...
    ],
    // Additional predictions for other inputs...
  ]
}
```

## JSON Lines (JSONL) Format

```json
{"predictions": [{"begin": Start_Index, "end": End_Index, "ner_chunk": "Named entity chunk", "ner_label": "Label", "ner_confidence": "Confidence_Score", "concept_code": "Concept_Code", "resolution": "Resolution", "score": Cosine_Distance_Score_for_Resolution, "all_codes": ["Code1", "Code2", "Code3", ...], "concept_name_detailed": ["Resolution1 [Ground Truth Mapping 1]", "Resolution2 [Ground Truth Mapping 2]", ...], "domain_id": ["Domain1", "Domain2", "Domain3", ...], "all_resolutions": ["Resolution1", "Resolution2", "Resolution3", ...], "all_score": [Score1, Score2, Score3, ...]}]}
{"predictions": [{"begin": Start_Index, "end": End_Index, "ner_chunk": "Named entity chunk", "ner_label": "Label", "ner_confidence": "Confidence_Score", "concept_code": "Concept_Code", "resolution": "Resolution", "score": Cosine_Distance_Score_for_Resolution, "all_codes": ["Code1", "Code2", "Code3", ...], "concept_name_detailed": ["Resolution1 [Ground Truth Mapping 1]", "Resolution2 [Ground Truth Mapping 2]", ...], "domain_id": ["Domain1", "Domain2", "Domain3", ...], "all_resolutions": ["Resolution1", "Resolution2", "Resolution3", ...], "all_score": [Score1, Score2, Score3, ...]}]}
```

The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text.

---

## Explanation of Fields

- **ner_chunk**: Detected NER chunk.
- **begin**: NER chunk begin index.
- **end**: NER chunk end index.
- **ner_label**: NER chunk label.
- **ner_confidence**: NER chunk confidence score.
- **concept_code**: Resolution code of the NER chunk.
- **resolution**: Resolution of the NER chunk.
- **score**: Cosine distance score of the resolution.
- **all_resolutions**: All the other possible resolutions of the NER chunk.
- **all_codes**: Codes of the resolutions in `all_resolutions` (in the same order).
- **concept_name_detailed**: Resolution of the NER chunk and the ground truth of the resolution code. The ground truth resolution of the code can be found in the brackets (`[...]`).
- **domain_id**: Domain(s) associated with the resolution(s).
- **all_score**: All the cosine distance scores of the `all_resolutions`.
