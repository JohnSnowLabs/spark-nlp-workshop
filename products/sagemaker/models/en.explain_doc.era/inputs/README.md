## Input Format

To use the model for text prediction, you need to provide input in one of the following supported formats:

### Format 1: Array of Text Documents

Use an array containing multiple text documents. Each element represents a separate text document.

```json

{
    "text": [
        
        "She is admitted to The John Hopkins Hospital 2 days ago with a history of gestational diabetes mellitus diagnosed. She denied pain and any headache. She was seen by the endocrinology service and she was discharged on 03/02/2018 on 40 units of insulin glargine, 12 units of insulin lispro, and metformin 1000 mg two times a day. She had close follow-up with endocrinology post discharge.",
        "Mike has cancer."
    ]
}
```

### Format 2: Single Text Document

Provide a single text document as a string.

```json
{
    "text": "She is admitted to The John Hopkins Hospital 2 days ago with a history of gestational diabetes mellitus diagnosed. She denied pain and any headache. She was seen by the endocrinology service and she was discharged on 03/02/2018 on 40 units of insulin glargine, 12 units of insulin lispro, and metformin 1000 mg two times a day. She had close follow-up with endocrinology post discharge."
}
```