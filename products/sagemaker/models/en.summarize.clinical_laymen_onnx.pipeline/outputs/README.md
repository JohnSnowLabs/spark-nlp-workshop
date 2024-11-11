## Output Format


### JSON Format

```json
{
    "summary": [
        "Summarized text for document 1",
        "Summarized text for document 2",
        ...
    ]
}
```
Each element within the "summary" array represents a summarized text for the respective documents. 



### JSON Lines (JSONL) Format


```
{"summary": "Summarized text for document 1"}
{"summary": "Summarized text for document 2"}
```

The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text.