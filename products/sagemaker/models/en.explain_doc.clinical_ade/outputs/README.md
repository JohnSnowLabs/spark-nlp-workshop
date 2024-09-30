## Output Format


## JSON Format

```json
[
    {
        "ner_predictions": [
            {
                "ner_chunk": "Named entity chunk",
                "begin": Start Index,
                "end": End Index,
                "ner_label": "Label",
                "ner_confidence": "Confidence Score"
            },
            // Additional predictions for input 1...
        ],
        "assertion_predictions": [
            {
                "ner_chunk": "Named entity chunk",
                "begin": Start Index,
                "end": End Index,
                "ner_label": "Label",
                "assertion": "Assertion status",
            },
            // Additional predictions for input 1...
        ],
        "relation_predictions": [
            {
                "ner_chunk1": "Named entity chunk 1",
                "ner_chunk1_begin": Start Index,
                "ner_chunk1_end": End Index,
                "ner_label1": "Label 1",
                "ner_chunk2": "Named entity chunk 2",
                "ner_chunk2_begin": Start Index,
                "ner_chunk2_end": End Index,
                "ner_label2": "Label 2",
                "relation": "Relation Type",
                "relation_confidence": "Confidence Score"
            },
            // Additional predictions for input 1...
        ],
        "classification_predictions": [
            {
                "sentence": "sentence",
                "begin": Start Index,
                "end": End Index,
                "class": "label",
                "class_confidence": "Confidence Score"
            },
            // Additional predictions for input 1...
        ],
    }
    // Additional predictions for other inputs...
]

```


### JSON Lines (JSONL) Format

```
{"ner_predictions": [{"ner_chunk": "Named Entity 1", "begin": Start Index, "end": End Index, "ner_label": "Label 1", "ner_confidence": Score}, {"ner_chunk": "Named Entity 2", "begin": Start Index, "end": End Index, "ner_label": "Label 2", "ner_confidence": Score}, ...], "assertion_predictions": [{"ner_chunk": "Named Entity 2", "begin": Start Index, "end": End Index, "ner_label": "Label 2", "assertion": "Assertion status"}, ...], "relation_predictions": [{"ner_chunk1": "Named Entity 1", "ner_chunk1_begin": Start Index, "ner_chunk1_end": End Index, "ner_label1": "Label 1", "ner_chunk2": "Named Entity 2", "ner_chunk2_begin": Start Index, "ner_chunk2_end": End Index, "ner_label2": "Label 2", "relation": "Relation Type", "relation_confidence": Score}, ...], "classification_predictions": [{"sentence": "Sentence 1", "begin": Start Index, "end": End Index, "class": "label", "class_confidence": Score},{"sentence": "Sentence 2", "begin": Start Index, "end": End Index, "class": "label", "class_confidence": Score}, ...]}
{"ner_predictions": [{"ner_chunk": "Named Entity 1", "begin": Start Index, "end": End Index, "ner_label": "Label 1", "ner_confidence": Score}, {"ner_chunk": "Named Entity 2", "begin": Start Index, "end": End Index, "ner_label": "Label 2", "ner_confidence": Score}, ...], "assertion_predictions": [{"ner_chunk": "Named Entity 2", "begin": Start Index, "end": End Index, "ner_label": "Label 2", "assertion": "Assertion status"}, ...], "relation_predictions": [{"ner_chunk1": "Named Entity 1", "ner_chunk1_begin": Start Index, "ner_chunk1_end": End Index, "ner_label1": "Label 1", "ner_chunk2": "Named Entity 2", "ner_chunk2_begin": Start Index, "ner_chunk2_end": End Index, "ner_label2": "Label 2", "relation": "Relation Type", "relation_confidence": Score}, ...], "classification_predictions": [{"sentence": "Sentence 1", "begin": Start Index, "end": End Index, "class": "label", "class_confidence": Score},{"sentence": "Sentence 2", "begin": Start Index, "end": End Index, "class": "label", "class_confidence": Score}, ...]}
```

The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text.


### Explanation of Fields

#### NER Predictions

- **ner_chunk**: The text of the entity.

- **begin**: Starting index of the named entity chunk within the document.

- **end**: Ending index of the named entity chunk within the document.

- **ner_label**: The label of the entity, as determined by the NER model.

- **ner_confidence**: Confidence score associated with the NER prediction.


#### Relation Predictions

- **ner_chunk1**: First named entity involved in the relation.

- **ner_chunk1_begin**: Starting index of the first named entity chunk within the document.

- **ner_chunk1_end**: Ending index of the first named entity chunk within the document.

- **ner_label1**: Label assigned to the first named entity.

- **ner_chunk2**: Second named entity involved in the relation.

- **ner_chunk2_begin**: Starting index of the second named entity chunk within the document.

- **ner_chunk2_end**: Ending index of the second named entity chunk within the document.

- **ner_label2**: Label assigned to the second named entity.

- **relation**: Type of relation identified.

- **relation_confidence**: Confidence score associated with the relation prediction.

## Classification Predictions
- **sentence**: The extracted sentence from the document.

- **begin**: The starting character index of the sentence within the document.

- **end**: The ending character index of the sentence within the document.

- **class**: The predicted label for the corresponding sentence.

- **class_confidence**: The confidence score associated with the predicted class, indicating the model's certainty in its prediction.
