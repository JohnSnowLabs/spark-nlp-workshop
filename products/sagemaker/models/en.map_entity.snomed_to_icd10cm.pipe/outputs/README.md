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
            "icd10cm_code": "ICD10-CM Code",
        },
        {
            "text": "Input text",
            "snomed_code": "SNOMED Code",
            "begin": Start Index,
            "end": End Index,
            "icd10cm_code": "ICD10-CM Code",
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

  - **icd10cm_code**: The corresponding ICD10-CM code for the SNOMED code.


### JSON Lines (JSONL) Format

```
{"predictions": [{"snomed_code": "SNOMED Code", "begin": Start Index, "end": End Index, "icd10cm_code": "ICD10-CM Code"}, {"snomed_code": "SNOMED Code", "begin": Start Index, "end": End Index, "icd10cm_code": "ICD10-CM Code"}, ...]}
{"predictions": [{"snomed_code": "SNOMED Code", "begin": Start Index, "end": End Index, "icd10cm_code": "ICD10-CM Code"}, {"snomed_code": "SNOMED Code", "begin": Start Index, "end": End Index, "icd10cm_code": "ICD10-CM Code"}, ...]}
```

The JSON Lines format consists of individual JSON objects, where each object represents predictions for a single input text.