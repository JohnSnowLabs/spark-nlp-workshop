## Output Format

The output consists of a JSON object with the following structure:

```json

{
    "document": "Transcribed text of the document",
    "segments": [
        {
            "speaker": "SPEAKER_ID",
            "begin": Start Timestamp,
            "end": End Timestamp,
            "text": "Transcribed text for the segment."
        },
        ...
    ],
    "ner_predictions": [
        {
            "ner_chunk": "Named Entity",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label",
            "ner_confidence": Score
        },
        ...
    ],
    "assertion_predictions": [
        {
            "ner_chunk": "Named Entity",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label",
            "assertion": "Assertion status",
        },
        ...
    ],
    "relation_predictions": [
        {
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

## Document 

**document** : original transcribed text of the document.


## Segments

An array containing segmented transcriptions, providing details such as speaker IDs, start and end timestamps, and the transcribed text for each segment.

- **speaker**: The ID or label assigned to the speaker.
- **begin**: The start timestamp of the segment.
- **end**: The end timestamp of the segment.
- **text**: The transcribed text for the segment.


## NER Predictions

An array containing NER predictions for each input document.

- **ner_chunk**: Named entity recognized in the document.

- **begin**: Starting character index of the named entity chunk within the document.

- **end**: Ending character index of the named entity chunk within the document.

- **ner_label**: Label assigned to the named entity.

- **ner_confidence**: Confidence score associated with the ner prediction.

## Assertion Predictions

An array containing assertions for each input document.

- **ner_chunk**: Named entity associated with the assertion.

- **begin**: Starting character index of the named entity chunk within the document.

- **end**: Ending character index of the named entity chunk within the document.

- **ner_label**: Label assigned to the named entity.

- **assertion**: Assertion status.

## Relation Predictions

An array containing relations between named entities within each input document.

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