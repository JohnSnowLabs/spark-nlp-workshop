### Output Format

The endpoint returns `application/json`. The response body is a JSON object with the following fields:

#### Top-level Fields

| Field | Type | Description |
|---|---|---|
| `consumed_units` | `int` | Number of billable inference units consumed by the request. |
| `predictions` | `object` | Map of `doc_id` to extraction result. One entry per input document. |

#### Per-document Fields (`predictions.<doc_id>`)

| Field | Type | Description |
|---|---|---|
| `doc_id` | `str` | Document identifier. For inline `texts` inputs: `doc_0`, `doc_1`, etc. For file inputs: the original filename. |
| `note_text` | `str` | Full extracted plain text of the document. |
| `note_json` | `object` | Structured extraction result containing tables, pictures, sections, and extraction metadata. |
| `output_s3_uri` | `str` | S3 URI of the written result file. **Only present when `output_s3_folder_path` was provided in the request.** This is the URI of the specific result file, not a folder — distinct from the `output_s3_folder_path` input field. |

#### `note_json` Fields

| Field | Type | Description |
|---|---|---|
| `tables` | `list[object]` | Extracted tables from the document. Empty for plain text inputs. |
| `pictures` | `list[object]` | Extracted images or figures from the document. Empty for plain text inputs. |
| `sections` | `object` | Document sections keyed by section heading, each value is a list of strings. Empty for plain text inputs. |
| `extraction_info` | `object` | Metadata about the extraction process. |
| `extraction_info.engine` | `str` | Extraction engine used. One of `"text"` (plain text pass-through), `"adaptive"` (auto-selected), `"docling"` (document parsing), `"granite"` (vision model). |
| `extraction_info.pages` | `int` | Number of pages processed. |

#### `note_json.tables[]` Fields

| Field | Type | Description |
|---|---|---|
| `table_name` | `str` | Auto-generated table identifier (e.g. `"table_1"`). |
| `page_number` | `int` | Page on which the table appears. |
| `markdown` | `str` | Table rendered as a Markdown string. |
| `headers` | `list[str]` | Column header values. |
| `rows` | `list[list[str]]` | Table rows, each a list of cell values. |
| `header_context` | `str` | Section heading or surrounding context for the table. |
| `source` | `str` | Extraction source (e.g. `"adaptive"`). |

#### `note_json.pictures[]` Fields

| Field | Type | Description |
|---|---|---|
| `picture_name` | `str` | Auto-generated image identifier (e.g. `"image_1"`). |
| `page_number` | `int` | Page on which the image appears. |
| `caption` | `str` | Caption text associated with the image. |
| `description` | `str` | Model-generated description of the image content (if available). |
| `bbox` | `list[int]` | Bounding box coordinates `[x0, y0, x1, y1]` in pixels. |
| `source` | `str` | Extraction source (e.g. `"adaptive"`). |

---

#### Example: Plain text input (no `output_s3_folder_path`)

Plain text inputs produce `engine: "text"` with empty tables, pictures, and sections.

```json
{
  "consumed_units": 1,
  "predictions": {
    "doc_0": {
      "doc_id": "doc_0",
      "note_text": "Patient is a 58-year-old male with stage III lung cancer. EGFR mutation positive. Started on erlotinib 150mg daily.",
      "note_json": {
        "tables": [],
        "pictures": [],
        "sections": {},
        "extraction_info": {
          "engine": "text",
          "pages": 1
        }
      }
    }
  }
}
```

#### Example: Document file input (with `output_s3_folder_path`)

Document inputs (PDF, image, Word, etc.) may produce tables, pictures, and sections depending on document content.
`output_s3_uri` is present because `output_s3_folder_path` was set in the request.

```json
{
  "consumed_units": 1,
  "predictions": {
    "report.pdf": {
      "doc_id": "report.pdf",
      "note_text": "# Clinical Report\n\nPatient: John Doe...",
      "note_json": {
        "tables": [
          {
            "table_name": "table_1",
            "page_number": 2,
            "markdown": "| Lab Test | Value | Unit |\n|---|---|---|\n| HbA1c | 9.2 | % |",
            "headers": ["Lab Test", "Value", "Unit"],
            "rows": [["HbA1c", "9.2", "%"]],
            "header_context": "Laboratory Results",
            "source": "adaptive"
          }
        ],
        "pictures": [
          {
            "picture_name": "image_1",
            "page_number": 1,
            "caption": "Figure 1: Chest X-Ray",
            "description": "",
            "bbox": [50, 100, 400, 600],
            "source": "adaptive"
          }
        ],
        "sections": {
          "Chief Complaint": ["Patient presents with shortness of breath."],
          "Assessment": ["Stage III lung cancer.", "EGFR mutation positive."]
        },
        "extraction_info": {
          "engine": "adaptive",
          "pages": 3
        }
      },
      "output_s3_uri": "s3://your-bucket/output/report.json"
    }
  }
}
```
