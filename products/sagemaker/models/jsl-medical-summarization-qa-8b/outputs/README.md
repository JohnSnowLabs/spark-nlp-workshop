## Output Format


### JSON Format

```json
{
    "response": [
        "model response for input 1",
        "model response for input 2",
        ...
    ]
}
```
Each element within the "response" array corresponds to a model response for the respective input.



### JSON Lines (JSONL) Format


```
{"response": "model response for input 1"}
{"response": "model response for input 2"}
```

The JSON Lines format consists of separate JSON objects, where each object represents a model response for the respective input.