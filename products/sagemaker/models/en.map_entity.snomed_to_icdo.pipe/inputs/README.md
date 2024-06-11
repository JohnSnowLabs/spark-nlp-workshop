## Input Format

To use the model, you need to provide input in one of the following supported formats:

### Format 1: Array of Text

Provide an array containing multiple texts. Each element represents a separate text.

```json
{
    "text": [
        "Text 1",
        "Text 2",
        ...
    ]
}
```

### Format 2: Single Text

Provide a single text as a string.

```json
{
    "text": "Single text"
}
```

### Format 3: JSON Lines (JSONL):

Provide input in JSON Lines format, where each line is a JSON object representing a text document.

```
{"text": "Text document 1"}
{"text": "Text document 2"}
```