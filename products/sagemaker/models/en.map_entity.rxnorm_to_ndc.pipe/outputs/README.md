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
            "package_ndc": "package ndc Code",
            "product_ndc": "product ndc Code",
        },
        {
            "text": "Input text",
            "rxnorm_code": "RxNorm Code",
            "begin": Start Index,
            "end": End Index,
            "package_ndc": "package ndc Code",
            "product_ndc": "product ndc Code",
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

  - **package_ndc**: The corresponding package ndc code for the RxNorm code.

  - **product_ndc**: The corresponding product ndc code for the RxNorm code.


### JSON Lines (JSONL) Format

```
{"predictions": [{"rxnorm_code": "RxNorm Code", "begin": Start Index, "end": End Index, "package_ndc": "package ndc Code", "product_ndc": "product ndc Code"}, {"rxnorm_code": "RxNorm Code", "begin": Start Index, "end": End Index, "package_ndc": "package ndc Code", "product_ndc": "product ndc Code"}, ...]}
{"predictions": [{"rxnorm_code": "RxNorm Code", "begin": Start Index, "end": End Index, "package_ndc": "package ndc Code", "product_ndc": "product ndc Code"}, {"rxnorm_code": "RxNorm Code", "begin": Start Index, "end": End Index, "package_ndc": "package ndc Code", "product_ndc": "product ndc Code"}, ...]}
```

The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text.