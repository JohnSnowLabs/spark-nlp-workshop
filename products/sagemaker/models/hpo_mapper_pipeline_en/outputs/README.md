## Output Format

### JSON Format

```json
{
    "predictions": [
        [
            {
                "ner_chunk": "Named entity chunk",
                "begin": Start_Index,
                "end": End_Index,
                "ner_label": "Label",
                "assertion": "Assertion status",
                "assertion_confidence": "Confidence Score",
                "code": "Code"
            },
            {
                "ner_chunk": "Named entity chunk",
                "begin": Start_Index,
                "end": End_Index,
                "ner_label": "Label",
                "assertion": "Assertion status",
                "assertion_confidence": "Confidence Score",
                "code": "Code"
            }
            // Additional predictions for input 1...
        ],
        // Additional predictions for other inputs...
    ]
}
```

### JSON Lines (JSONL) Format

```
{"predictions": [{"ner_chunk": "Named entity chunk", "begin": Start_Index, "end": End_Index, "ner_label": "Label", "assertion": "Assertion status", "assertion_confidence": "Confidence Score", "code": "Code"}, ...]}
{"predictions": [{"ner_chunk": "Named entity chunk", "begin": Start_Index, "end": End_Index, "ner_label": "Label", "assertion": "Assertion status", "assertion_confidence": "Confidence Score", "code": "Code"}, ...]}
```

The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text.

### Explanation of Fields

- **ner_chunk**: The text of the entity.
- **begin**: The index of the beginning of the entity in the text.
- **end**: The index of the end of the entity in the text.
- **ner_label**: The label of the entity, as determined by the NER model.
- **assertion**: Assertion status.
- **assertion_confidence**: Confidence score associated with the assertion prediction.
- **code**: The code of the term.