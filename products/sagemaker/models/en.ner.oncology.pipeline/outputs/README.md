# Output Format

The model produces predictions at two distinct output levels: Chunk and Document.

## Output Levels: Chunk

The output at the chunk level consists of a JSON object with the following structure:

```json
{
    "predictions": [
        {
            "document": "Text of the document 1",
            "ner_chunk": "Named Entity 1",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label 1",
            "confidence": Score
        },
        {
            "document": "Text of the document 1",
            "ner_chunk": "Named Entity 2",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label 2",
            "confidence": Score
        },

        {
            "document": "Text of the document 2",
            "ner_chunk": "Named Entity 1",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label 2",
            "confidence": Score
        },
        ...
    ]
}

```

### Explanation of Fields

- **predictions**: An array containing predictions for each input document.

    - **document**: The original input text for which predictions are made.

    - **ner_chunk**: Named entity recognized in the document.

    - **begin**: Starting character index of the named entity chunk within the document.

    - **end**: Ending character index of the named entity chunk within the document.

    - **ner_label**: Label assigned to the named entity.

    - **confidence**: Confidence score associated with the prediction.


## Output Levels: Document

The output format consists of a JSON object with the following structure:

```json
{
    "predictions": [
        {
            "document": "Text of the document 1",
            "ner_chunk": ["Named Entity 1", "Named Entity 2", ...],
            "begin": [Start Index 1, Start Index 2, ...],
            "end": [End Index 1, End Index 2, ...],
            "ner_label": ["Label 1", "Label 2", ...],
            "confidence": ["Confidence 1", "Confidence 2", ...]
        },
        {
            "document": "Text of the document 2",
            "ner_chunk": ["Named Entity 1", "Named Entity 2", ...],
            "begin": [Start Index 1, Start Index 2, ...],
            "end": [End Index 1, End Index 2, ...],
            "ner_label": ["Label 1", "Label 2", ...],
            "confidence": ["Confidence 1", "Confidence 2", ...]
        }
    ]
}
```


### Explanation of Fields:

- **predictions**: An array containing predictions for each input document.

    - **document**:  The original input text for which predictions are made.

    - **ner_chunk**: An array containing named entities recognized in the document. Named entities represent specific pieces of information such as medical conditions, treatments, or personal details.

    - **begin**: An array indicating the starting character index of each named entity chunk within the document. It represents the position where the named entity is found in the text.

    - **end**: An array indicating the ending character index of each named entity chunk within the document. It signifies the end position of the named entity in the text.

    - **ner_label**: An array containing labels assigned to each named entity.

    - **confidence**: An array representing the confidence score associated with each named entity.
