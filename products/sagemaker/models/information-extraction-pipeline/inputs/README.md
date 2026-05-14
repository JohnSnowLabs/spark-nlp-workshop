### Input Format

The endpoint accepts `application/json` content type. The request body is a JSON object with the following fields:

#### Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `texts` | `list[str]` | No | List of plain-text strings to process inline. |
| `s3_file_path` | `str` | No | S3 URI of a single document to download and process (e.g. `s3://bucket/doc.pdf`). |
| `s3_folder_path` | `str` | No | S3 URI prefix of a folder of documents to process (e.g. `s3://bucket/docs/`). |
| `file_bytes` | `str` | No | Base64-encoded bytes of a document to process. Requires `filename`. |
| `filename` | `str` | No | Original filename for the uploaded `file_bytes` (used to determine file type). |
| `output_s3_folder_path` | `str` | No | S3 folder URI where extraction results are written. If omitted, results are returned inline. |

Exactly one of `texts`, `s3_file_path`, `s3_folder_path`, or `file_bytes` should be provided per request.

#### Supported Document Types

When using `s3_file_path`, `s3_folder_path`, or `file_bytes`, the following document formats are supported:

- PDF (`.pdf`)
- Images (`.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`)
- Microsoft Word (`.docx`)
- Microsoft PowerPoint (`.pptx`)
- Microsoft Excel (`.xlsx`)
- Plain text (`.txt`)

#### Example 1: Inline text

```json
{
  "texts": [
    "Patient is a 58-year-old male with stage III lung cancer. EGFR mutation positive. Started on erlotinib 150mg daily."
  ]
}
```

#### Example 2: Multiple inline texts

```json
{
  "texts": [
    "Patient is a 58-year-old male with stage III lung cancer. EGFR mutation positive. Started on erlotinib 150mg daily.",
    "62-year-old female with Type 2 diabetes mellitus, HbA1c 9.2%. Started metformin 500mg twice daily."
  ]
}
```

#### Example 3: S3 single file

```json
{
  "s3_file_path": "s3://your-bucket/documents/report.pdf"
}
```

#### Example 4: S3 folder

```json
{
  "s3_folder_path": "s3://your-bucket/documents/"
}
```

#### Example 5: Base64 file upload with S3 output

```json
{
  "file_bytes": "<base64-encoded file content>",
  "filename": "report.pdf",
  "output_s3_folder_path": "s3://your-bucket/output/"
}
```
