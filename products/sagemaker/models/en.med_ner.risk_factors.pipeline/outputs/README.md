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
            },
            {
                "ner_chunk": "Named entity chunk",
                "begin": Start_Index,
                "end": End_Index,
                "ner_label": "Label",
                "ner_confidence": "Confidence_Score",
            }
            // Additional predictions for input 1...
        ],
         // Additional predictions for other inputs...
    ]
}

```


### JSON Lines (JSONL) Format

```
{"predictions": [{"ner_chunk": "Named entity chunk", "begin": Start_Index, "end": End_Index, "ner_label": "Label", "ner_confidence": "Confidence_Score"}, ...]}
{"predictions": [{"ner_chunk": "Named entity chunk", "begin": Start_Index, "end": End_Index, "ner_label": "Label", "ner_confidence": "Confidence_Score"}, ...]}
```

The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text.


### Explanation of Fields

  - **ner_chunk**: The text of the entity.
  - **begin**: The index of the beginning of the entity in the text.
  - **end**: The index of the end of the entity in the text.
  - **ner_label**: The label of the entity, as determined by the NER model.
  - **ner_confidence**: The confidence score of the NER model in identifying this entity.