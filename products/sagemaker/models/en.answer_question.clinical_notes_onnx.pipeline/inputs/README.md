## Input Format

To use the model, you need to provide input in one of the following supported formats:

### Format 1: Array of Text Documents

```json
{
    "context": [
        "Context 1",
        "Context 2"
    ],
    "question": [
        "Question 1",
        "Question 2"
    ]
}
```

### Format 2: Single Text Document


```json
{"context": "Context", "question": "Question"}
```

### Format 3: JSON Lines (JSONL):

Provide input in JSON Lines format, where each line is a JSON object representing a single input.

```
{"context": "Context 1", "question": "Question 1"}
{"context": "Context 2", "question": "Question 2"}
```