## Output Format

### JSON Format

```json
{
    "predictions": [
        {
            "text": "Input text",
            "rxnorm_code": "RxNorm Code",
            "begin": Start Index,
            "end": End Index,
            "mesh_code": "MeSH Code",
        },
        {
            "text": "Input text",
            "rxnorm_code": "RxNorm Code",
            "begin": Start Index,
            "end": End Index,
            "mesh_code": "MeSH Code",
        },
        ...
    ]
}

```

#### Explanation of Fields

- **predictions**: An array containing predictions for each input text.

  - **text**: The input text provided for mapping.

  - **rxnorm_code**: The corresponding RxNorm code in the input text.

  - **begin**: Start index of the RxNorm code within the input text.

  - **end**: End index of the RxNorm code within the input text.

  - **mesh_code**: The corresponding MeSH code for the RxNorm code.


### JSON Lines (JSONL) Format

```
{"predictions": [{"rxnorm_code": "RxNorm Code", "begin": Start Index, "end": End Index, "mesh_code": "MeSH Code"}, {"rxnorm_code": "RxNorm Code", "begin": Start Index, "end": End Index, "mesh_code": "MeSH Code"}, ...]}
{"predictions": [{"rxnorm_code": "RxNorm Code", "begin": Start Index, "end": End Index, "mesh_code": "MeSH Code"}, {"rxnorm_code": "RxNorm Code", "begin": Start Index, "end": End Index, "mesh_code": "MeSH Code"}, ...]}
```

The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text.