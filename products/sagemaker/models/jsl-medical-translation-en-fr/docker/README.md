

## Medical Text Translation (EN-FR)

- **Model**: `jsl-medical-translation-en-fr`
- **Model Description**: Medical text translation between English (EN) and french (FR). The model supports a maximum input length of 1024 tokens.


## Usage

To utilize this pipeline, a sample API call is as follows:

```sh
curl -X POST \
  'http://localhost:8080/invocations' \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "Primary empty sella turcica associated with diabetes insipidus and campimetric defect"
}'
```