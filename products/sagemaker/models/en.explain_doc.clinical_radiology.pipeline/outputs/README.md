# Output Format

The model produces predictions at two distinct output levels: chunk, document and relational.

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
        ...
    ]
}

```

If the assertion parameter is set to true:

```json
{
    "predictions": [
        {
            "document": "Text of the document 1",
            "ner_chunk": "Named Entity 2",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "Label 2",
            "confidence": Score,
            "assertion": Assertion status,
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

    - **confidence**: Confidence score associated with the prediction.

    - **assertion**: Assertion status (determined through filtration based on specific columns `assertion_begin`, `assertion_end` from the assertion output and `begin`, `end` for chunk output level for each document.)





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
            "confidence": [Score 1, Score 2, ...]
        },
        ...
    ]
}
```



If the assertion parameter is set to true:


```json
{
    "predictions": [
        {
            "document": "Text of the document 1",
            "ner_chunk": ["Named Entity 1", "Named Entity 2", ...],
            "begin": [Start Index 1, Start Index 2, ...],
            "end": [End Index 1, End Index 2, ...],
            "ner_label": ["Label 1", "Label 2", ...],
            "confidence": [Score 1, Score 2, ...],
            "assertion": ["Assertion status 1", "Assertion status 2", ...],
            "assertion_begin": [Assertion Start Index 1, Assertion Start Index 2, ...],
            "assertion_end": [Assertion End Index 1, Assertion End Index 2, ...],

        },
        ...
    ]
}
```


#### Explanation of Fields:

- **predictions**: An array containing predictions for each input document.

    - **document**:  The original input text for which predictions are made.

    - **ner_chunk**: An array containing named entities recognized in the document. Named entities represent specific pieces of information such as medical conditions, treatments, or personal details.

    - **begin**: An array indicating the starting character index of each named entity chunk within the document. It represents the position where the named entity is found in the text.

    - **end**: An array indicating the ending character index of each named entity chunk within the document. It signifies the end position of the named entity in the text.

    - **ner_label**: An array containing labels assigned to each named entity.

    - **confidence**: An array representing the confidence score associated with each named entity.

    - **assertion**: An array containing assertion status corresponding to `assertion_begin` and `assertion_end`

    - **assertion_begin**: An array indicating the starting character index of chunk within the document for the assertion status.

    - **assertion_end**: An array indicating the Ending character index of chunk within the document for the assertion status.


## Output Levels: Relational

The output format consists of a JSON object with the following structure:

```json
{
    "predictions": [
        {
            "document": "Text of the document 1",
            "relation": ["Relation Type 1", "Relation Type 2", ...],
            "ner_chunk1": ["Named Entity 1", "Named Entity 2", ...],
            "ner_chunk1_begin": [Start Index 1, Start Index 2, ...],
            "ner_chunk1_end": [End Index 1, End Index 2, ...],
            "ner_label1": ["Label 1", "Label 2", ...],
            "ner_chunk2": ["Named Entity 1", "Named Entity 2", ...],
            "ner_chunk2_begin": [Start Index 1, Start Index 2, ...],
            "ner_chunk2_end": [End Index 1, End Index 2, ...],
            "ner_label2": ["Label 1", "Label 2", ...],
            "confidence": [Score 1, Score 2, ...]
        },
        ...
    ]
}
```

## Explanation of Fields

- **predictions**: An array containing predictions for each input document.

    - **document**: The original input text for which predictions are made.

    - **relation**: An array containing the types of relations identified between named entities in the document.

    - **ner_chunk1**: An array containing the first set of named entities involved in the relations.

    - **ner_chunk1_begin**: An array indicating the starting character index of each occurrence of the first set of named entities within the document.

    - **ner_chunk1_end**: An array indicating the ending character index of each occurrence of the first set of named entities within the document.

    - **ner_label1**: An array containing labels assigned to each occurrence of the first set of named entities.

    - **ner_chunk2**: An array containing the second set of named entities involved in the relations.

    - **ner_chunk2_begin**: An array indicating the starting character index of each occurrence of the second set of named entities within the document.

    - **ner_chunk2_end**: An array indicating the ending character index of each occurrence of the second set of named entities within the document.

    - **ner_label2**: An array containing labels assigned to each occurrence of the second set of named entities.

    - **confidence**: An array representing the confidence score associated with each relation prediction.



