# Output Format

### JSON Format

```json

{
    "ner_predictions": [
        {
            "document": "Text of the document 1",
            "ner_chunk": "Named Entity 1",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label 1",
            "ner_confidence": Score
        },
        {
            "document": "Text of the document 1",
            "ner_chunk": "Named Entity 2",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label 2",
            "ner_confidence": Score
        },
        ...
    ],
    "assertion_predictions": [
        {
            "document": "Text of the document 1",
            "ner_chunk": "Named Entity 2",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label 2",
            "assertion": "Assertion status",
        },
        ...
    ],
    "relation_predictions": [
        {
            "document": "Text of the document 1",
            "ner_chunk1": "Named Entity 1",
            "ner_chunk1_begin": Start Index,
            "ner_chunk1_end": End Index,
            "ner_label1": "Label 1",
            "ner_chunk2": "Named Entity 2",
            "ner_chunk2_begin": Start Index,
            "ner_chunk2_end": End Index,
            "ner_label2": "Label 2",
            "relation": "Relation Type",
            "relation_confidence": Score
        },
        ...
    ]
}
```


## NER Predictions
An array containing NER predictions for each input document.

- **document**: The original input text for which predictions are made.

- **ner_chunk**: Named entity recognized in the document.

- **begin**: Starting character index of the named entity chunk within the document.

- **end**: Ending character index of the named entity chunk within the document.

- **ner_label**: Label assigned to the named entity.

- **ner_confidence**: Confidence score associated with the ner prediction.

## Assertion Predictions
An array containing assertions for each input document.

- **document**: The original input text for which assertions are made.

- **ner_chunk**: Named entity associated with the assertion.

- **begin**: Starting character index of the named entity chunk within the document.

- **end**: Ending character index of the named entity chunk within the document.

- **ner_label**: Label assigned to the named entity.

- **assertion**: Assertion status.

## Relation Predictions
An array containing relations between named entities within each input document.

- **document**: The original input text for which relations are identified.

- **ner_chunk1**: First named entity involved in the relation.

- **ner_chunk1_begin**: Starting character index of the first named entity chunk within the document.

- **ner_chunk1_end**: Ending character index of the first named entity chunk within the document.

- **ner_label1**: Label assigned to the first named entity.

- **ner_chunk2**: Second named entity involved in the relation.

- **ner_chunk2_begin**: Starting character index of the second named entity chunk within the document.

- **ner_chunk2_end**: Ending character index of the second named entity chunk within the document.

- **ner_label2**: Label assigned to the second named entity.

- **relations**: Type of relation identified.

- **relation_confidence**: Confidence score associated with the relation.



### JSON Lines (JSONL) Format

```
{"ner_predictions": [{"ner_chunk": "Named Entity 1", "begin": Start Index, "end": End Index, "ner_label": "Label 1", "ner_confidence": Score}, {"ner_chunk": "Named Entity 2", "begin": Start Index, "end": End Index, "ner_label": "Label 2", "ner_confidence": Score}, ...], "assertion_predictions": [{"ner_chunk": "Named Entity 2", "begin": Start Index, "end": End Index, "ner_label": "Label 2", "assertion": "Assertion status"}, ...], "relation_predictions": [{"ner_chunk1": "Named Entity 1", "ner_chunk1_begin": Start Index, "ner_chunk1_end": End Index, "ner_label1": "Label 1", "ner_chunk2": "Named Entity 2", "ner_chunk2_begin": Start Index, "ner_chunk2_end": End Index, "ner_label2": "Label 2", "relation": "Relation Type", "relation_confidence": Score}, ...]}
{"ner_predictions": [{"ner_chunk": "Named Entity 1", "begin": Start Index, "end": End Index, "ner_label": "Label 1", "ner_confidence": Score}, {"ner_chunk": "Named Entity 2", "begin": Start Index, "end": End Index, "ner_label": "Label 2", "ner_confidence": Score}, ...], "assertion_predictions": [{"ner_chunk": "Named Entity 2", "begin": Start Index, "end": End Index, "ner_label": "Label 2", "assertion": "Assertion status"}, ...], "relation_predictions": [{"ner_chunk1": "Named Entity 1", "ner_chunk1_begin": Start Index, "ner_chunk1_end": End Index, "ner_label1": "Label 1", "ner_chunk2": "Named Entity 2", "ner_chunk2_begin": Start Index, "ner_chunk2_end": End Index, "ner_label2": "Label 2", "relation": "Relation Type", "relation_confidence": Score}, ...]}
```

The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text.