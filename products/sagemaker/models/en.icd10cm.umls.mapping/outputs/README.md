## Output Format

### JSON Format

```json
{
    "predictions": [
        {
            "text": "Input text",
            "icd10cm_code": "ICD10-CM Code",
            "begin": Start Index,
            "end": End Index,
            "umls_code": "UMLS Code",
        },
        {
            "text": "Input text",
            "icd10cm_code": "ICD10-CM Code",
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

  - **icd10cm_code**: The corresponding ICD10-CM code in the input text.

  - **begin**: Start index of the ICD10-CM code within the input text.

  - **end**: End index of the ICD10-CM code within the input text.

  - **umls_code**: The corresponding UMLS code for the ICD10-CM code.


### JSON Lines (JSONL) Format

```
{"predictions": [{"icd10cm_code": "ICD10-CM Code", "begin": Start Index, "end": End Index, "umls_code": "UMLS Code"}, {"icd10cm_code": "ICD10-CM Code", "begin": Start Index, "end": End Index, "umls_code": "UMLS Code"}, ...]}
{"predictions": [{"icd10cm_code": "ICD10-CM Code", "begin": Start Index, "end": End Index, "umls_code": "UMLS Code"}, {"icd10cm_code": "ICD10-CM Code", "begin": Start Index, "end": End Index, "umls_code": "UMLS Code"}, ...]}
```

The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text.