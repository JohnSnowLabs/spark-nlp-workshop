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
            "umls_code": "UMLS Code",
        },
        {
            "text": "Input text",
            "rxnorm_code": "RxNorm Code",
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

  - **rxnorm_code**: The corresponding RxNorm code in the input text.

  - **begin**: Start index of the RxNorm code within the input text.

  - **end**: End index of the RxNorm code within the input text.

  - **umls_code**: The corresponding UMLS code for the RxNorm code.


### JSON Lines (JSONL) Format

```
{"predictions": [{"rxnorm_code": "RxNorm Code", "begin": Start Index, "end": End Index, "umls_code": "UMLS Code"}, {"rxnorm_code": "RxNorm Code", "begin": Start Index, "end": End Index, "umls_code": "UMLS Code"}, ...]}
{"predictions": [{"rxnorm_code": "RxNorm Code", "begin": Start Index, "end": End Index, "umls_code": "UMLS Code"}, {"rxnorm_code": "RxNorm Code", "begin": Start Index, "end": End Index, "umls_code": "UMLS Code"}, ...]}
```

The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text.