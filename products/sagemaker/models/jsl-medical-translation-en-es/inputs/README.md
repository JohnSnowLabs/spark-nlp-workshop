# Input Format

To use the model, you need to provide input in one of the following supported formats:

### Format 1: Array of Text Documents

Use an array containing multiple text documents. Each element represents a separate text document.

```json
{
    "text": [
        "Text document 1",
        "Text document 2",
        ...
    ]
}
```

### Format 2: Single Text Document

Provide a single text document as a string.

```json
{
    "text": "Single text document"
}
```

### Format 3: JSON Lines (JSONL):

Provide input in JSON Lines format, where each line is a JSON object representing a text document.

```
{"text": "Text document 1"}
{"text": "Text document 2"}
```


## Using the Model Package

This model package can be used to translate text from English to Spanish or vice versa. To specify the translation direction, set the `TRANSLATION_DIRECTION` environment variable. The possible values for `TRANSLATION_DIRECTION` are:

- `'en_to_es'` for translating English to Spanish
- `'es_to_en'` for translating Spanish to English

If `TRANSLATION_DIRECTION` is not provided, the default value `'en_to_es'` will be used.