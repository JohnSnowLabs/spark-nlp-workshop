# Output Format

### JSON Format

```json
{
    "raw_document": [
        {
            "text": "Raw extracted text from DICOM",
            "begin": Start Index,
            "end": End Index
        }
    ],
    "document": [
        {
            "text": "Processed text from DICOM",
            "begin": Start Index,
            "end": End Index
        }
    ],
    "sentence": [
        {
            "text": "Individual sentence from document",
            "begin": Start Index,
            "end": End Index
        }, 
        {
            "text": "Individual sentence from document",
            "begin": Start Index,
            "end": End Index
        }, 
        ...
    ],
    "ner_predictions": [
        {
            "ner_chunk": "Detected PHI entity",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "PHI Label"
        },
        {
            "ner_chunk": "Detected PHI entity",
            "begin": Start Index,
            "end": End Index,
            "ner_label": "PHI Label"
        },
        ...
    ],
    "deid_metadata": {
        "Patient'sName": "anonymous",
        "PatientID": "anonymized_id",
        "InstitutionName": "anonymous",
        "StudyDate": "modified_date",
        ...
    },
    "metadata_original": {
        "Patient'sName": "ORIGINAL^NAME",
        "PatientID": "original_id", 
        "InstitutionName": "Original Institution Name",
        "StudyDate": "original_date",
        ...
    },
    "metadata_diffs": [
        "Patient'sName -> ORIGINAL^NAME | anonymous",
        "PatientID -> original_id | anonymized_id",
        "InstitutionName -> Original Institution Name | anonymous",
        "StudyDate -> original_date | modified_date",
        ...
    ]
}
```

---

## Output Structure

### `raw_document`

* **text**: Raw text as extracted from the DICOM file, prior to any processing or normalization.
* **begin**: Starting character index within the raw text.
* **end**: Ending character index within the raw text.

### `document`

* **text**: Cleaned and processed text derived from the raw DICOM content (e.g., normalized spacing, punctuation).
* **begin**: Starting character index of the processed text.
* **end**: Ending character index of the processed text.

### `sentence`

* **text**: An individual sentence extracted from the processed document.
* **begin**: Starting character index of the sentence within the document.
* **end**: Ending character index of the sentence within the document.

### `ner_predictions`

* **ner\_chunk**: The specific PHI entity text identified in the document.
* **begin**: Starting character index of the PHI entity in the document.
* **end**: Ending character index of the PHI entity.
* **ner\_label**: Label assigned to the named entity.

### `deid_metadata` (Anonymized DICOM Metadata)

* DICOM tags where PHI values have been redacted, masked, or replaced with placeholders.

### `metadata_original` (Original DICOM Metadata)

* Unmodified metadata directly extracted from the original DICOM file.

### `metadata_diffs` (Metadata Differences)

* An array of strings showing the differences between original and deidentified metadata.
* Each string follows the format: `"FieldName -> OriginalValue | DeidentifiedValue"`