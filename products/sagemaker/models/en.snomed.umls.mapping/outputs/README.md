## Output Format

### JSON Format

```json
{
    "predictions": [
        {
            "text": "Input text",
            "snomed_code": "SNOMED Code",
            "begin": Start Index,
            "end": End Index,
            "umls_code": "UMLS Code",
        },
        {
            "text": "Input text",
            "snomed_code": "SNOMED Code",
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

  - **snomed_code**: The corresponding SNOMED code in the input text.

  - **begin**: Start index of the SNOMED code within the input text.

  - **end**: End index of the SNOMED code within the input text.

  - **umls_code**: The corresponding UMLS code for the SNOMED code.


### JSON Lines (JSONL) Format

```
{"predictions": [{"snomed_code": "SNOMED Code", "begin": Start Index, "end": End Index, "umls_code": "UMLS Code"}, {"snomed_code": "SNOMED Code", "begin": Start Index, "end": End Index, "umls_code": "UMLS Code"}, ...]}
{"predictions": [{"snomed_code": "SNOMED Code", "begin": Start Index, "end": End Index, "umls_code": "UMLS Code"}, {"snomed_code": "SNOMED Code", "begin": Start Index, "end": End Index, "umls_code": "UMLS Code"}, ...]}
```

The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text.