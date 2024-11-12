## Input Format

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

Provide input in JSON Lines format, where each line is a JSON object representing a text document along with any optional parameters.

```
{"text": "Text document 1"}
{"text": "Text document 2"}
```


### Important Parameter

- **masking_policy**: `str`

    Users can select a masking policy to determine how sensitive entities are handled:

    - **masked**: Default policy that masks entities with their type.

      Example: "My name is Mike. I was admitted to the hospital yesterday."  
      -> "My name is `<PATIENT>`. I was admitted to the hospital yesterday."

    - **obfuscated**: Replaces sensitive entities with random values of the same type.

      Example: "My name is Mike. I was admitted to the hospital yesterday."  
      -> "My name is `Barbaraann Share`. I was admitted to the hospital yesterday."

    
You can specify these parameters in the input as follows:

```json
{
    "text": [
        "Text document 1",
        "Text document 2",
        ...
    ],
    "masking_policy": "masked",
}
```
