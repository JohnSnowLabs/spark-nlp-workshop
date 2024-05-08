## Output Format

### JSON Format

```json
{
    "predictions": [
        {
            "text": "Input text",
            "rxnorm_code": "RxNorm Code",
            "mesh_code": "MeSH Code",
        },
        {
            "text": "Input text",
            "rxnorm_code": "RxNorm Code",
            "mesh_code": "MeSH Code",
        },
        ...
    ]
}

```

#### Explanation of Fields

- **predictions**: An array containing predictions for each input text.

  - **text**: The input text provided for mapping.

  - **rxnorm_code**: The corresponding RxNorm code for the input text.

  - **mesh_code**: The corresponding MeSH code for the input text.


### JSON Lines (JSONL) Format

```
{"predictions": [{"rxnorm_code": "RxNorm Code", "mesh_code": "MeSH Code"}, {"rxnorm_code": "RxNorm Code", "mesh_code": "MeSH Code"}, ...]}
```

The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text. The structure of each object is similar to the JSON format explained above.