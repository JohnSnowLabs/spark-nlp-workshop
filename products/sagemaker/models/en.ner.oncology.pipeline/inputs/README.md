# Input Format

To use the model for text prediction, you need to provide input in one of the following supported formats:

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

Additionally, the model produces predictions at two distinct output levels:

- **Document**: Predictions are generated for entire documents.
- **Chunk**: Predictions are generated for smaller chunks within documents.

By default, the output level is set to `chunk`.

You can specify the desired output level in the input as follows:

```json
{
    "text": [
        "Text document 1",
        "Text document 2",
        ...
    ],
    "output_level": "document"
}
