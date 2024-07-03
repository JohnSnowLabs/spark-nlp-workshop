## Output Format

The model generates output in the following format:

```json
{
    "predictions": [
        "Output text document 1",
        "Output text document 2",
        ...
    ]
}

```
The "predictions" field contains an array where each element represents the output text corresponding to the input documents provided.


### JSON Lines (JSONL) Format

```
{"predictions": "Output text document 1"}
{"predictions": "Output text document 1"}
```

The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text.