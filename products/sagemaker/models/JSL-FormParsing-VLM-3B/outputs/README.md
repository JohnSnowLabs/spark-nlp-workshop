## Output Format

The model returns a structured JSON response in the following format:

```json
{
    "id": "<unique_identifier>",
    "created": <unix_timestamp>,
    "model": "/opt/ml/model",
    "object": "chat.completion",
    "output": [
        {
            "text": "<extracted_text>",
            "label": "<field_type>",
            "children": [
                {
                    "text": "<extracted_value>",
                    "label": "<value_type>"
                }
            ]
        },
        ...
    ]
}
```

---

### Field Descriptions

- **`id`**: Unique identifier for the completion (string).
- **`created`**: Unix timestamp of when the completion was created (integer).
- **`model`**: Path to the model used (fixed as `/opt/ml/model` for SageMaker) (string).
- **`object`**: Type of object returned (always `chat.completion`) (string).
- **`output`**: Array of objects representing extracted fields and their values.