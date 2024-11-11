## Output Format

### JSON Format

```json
{
    "predictions": [
        {
            "text": "Input text",
            "mesh_code": "MESH Code",
            "begin": Start Index,
            "end": End Index,
            "umls_code": "UMLS Code",
        },
        {
            "text": "Input text",
            "mesh_code": "MESH Code",
            "begin": Start Index,
            "end": End Index,
            "umls_code": "UMLS Code",
        },
        ...
    ]
}

```

#### Explanation of Fields

- **predictions**: An array containing predictions for each input text.

  - **text**: The input text provided for mapping.

  - **mesh_code**: The corresponding MESH code in the input text.

  - **begin**: Start index of the MESH code within the input text.

  - **end**: End index of the MESH code within the input text.

  - **umls_code**: The corresponding UMLS code for the MESH code.


### JSON Lines (JSONL) Format

```
{"predictions": [{"mesh_code": "MESH Code", "begin": Start Index, "end": End Index, "umls_code": "UMLS Code"}, {"mesh_code": "MESH Code", "begin": Start Index, "end": End Index, "umls_code": "UMLS Code"}, ...]}
{"predictions": [{"mesh_code": "MESH Code", "begin": Start Index, "end": End Index, "umls_code": "UMLS Code"}, {"mesh_code": "MESH Code", "begin": Start Index, "end": End Index, "umls_code": "UMLS Code"}, ...]}
```

The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text.