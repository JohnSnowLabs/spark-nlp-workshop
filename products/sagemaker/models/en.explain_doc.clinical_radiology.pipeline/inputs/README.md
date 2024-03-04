## Input Format

To use the pipeline model, you need to provide input in one of the following supported formats:

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

### Important Parameters 

- #### Output Levels

  The pipeline produces predictions at 3 distinct output levels:

  - document
  - chunk
  - relational

  Note: By default, the output level is chunk.

- #### Assertion

   DataType: `bool` 

  This parameter is only used with output levels document and chunk. It determines whether to include assertion status in the output.



You can specify the desired output level in the input as follows:

```json
{
    "text": [
        "Text document 1",
        "Text document 2",
        ...
    ],
    "output_level": "chunk",
    "assertion": True
}