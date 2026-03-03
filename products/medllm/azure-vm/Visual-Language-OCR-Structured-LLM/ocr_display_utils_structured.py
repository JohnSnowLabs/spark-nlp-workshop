import json
import sys
import base64
from io import BytesIO
from pathlib import Path
from PIL import Image as PILImage
from IPython.display import display, HTML


def show_structured_extraction_comparison(
    image_sources, schema_sources, results, duration_ms_list, markdown_texts,
    title="Structured Data Extraction"
):
    """
    Display image, markdown, JSON output, and schema side-by-side with metrics.
    """
    if not isinstance(image_sources, list):                      image_sources   = [image_sources]
    if not isinstance(schema_sources, list):                     schema_sources  = [schema_sources]
    if not isinstance(results, list):                            results         = [results]
    if not isinstance(markdown_texts, list):                     markdown_texts  = [markdown_texts]
    if isinstance(duration_ms_list, (int, float)):
        duration_ms_list = [duration_ms_list] * len(image_sources)

    display(HTML(f'''<div style="font-family:Arial,sans-serif;max-width:2000px;">
        <h2 style="margin-bottom:20px;color:#333;">{title}</h2></div>'''))

    for idx, (image_source, schema_source, result, duration_ms, markdown_text) in enumerate(
        zip(image_sources, schema_sources, results, duration_ms_list, markdown_texts), 1
    ):
        filename_display = Path(image_source).stem if isinstance(image_source, (str, Path)) else f"Image {idx}"

        prediction_text = result["choices"][0]["message"]["content"]
        try:
            formatted_prediction = json.dumps(json.loads(prediction_text), indent=2)
        except Exception:
            formatted_prediction = prediction_text

        # Parse schema — accept dict, JSON string, or file path (PosixPath included)
        # Also handles double-encoded JSON (a JSON string stored inside a JSON file)
        if isinstance(schema_source, dict):
            schema = schema_source
        else:
            try:
                # Try direct JSON parse (schema_source is already a JSON string)
                schema = json.loads(schema_source)
            except (json.JSONDecodeError, TypeError):
                # Must be a file path — load it
                with open(schema_source) as _f:
                    raw = _f.read().strip()
                try:
                    parsed = json.loads(raw)
                    # Handle double-encoding: file contains a JSON string whose value is more JSON
                    if isinstance(parsed, str):
                        schema = json.loads(parsed)
                    else:
                        schema = parsed
                except Exception:
                    schema = raw
        try:
            formatted_schema = json.dumps(schema, indent=2)
        except Exception:
            formatted_schema = str(schema)

        img = image_source if isinstance(image_source, PILImage.Image) else PILImage.open(image_source)
        img_width, img_height = img.size
        if img.width > 800:
            r = 800 / img.width
            img = img.resize((800, int(img.height * r)), PILImage.Resampling.LANCZOS)
        buffered = BytesIO()
        if img.mode == "RGBA":
            img.save(buffered, format="PNG", optimize=True); img_format = "png"
        else:
            if img.mode != "RGB": img = img.convert("RGB")
            img.save(buffered, format="JPEG", quality=85, optimize=True); img_format = "jpeg"
        img_str = base64.b64encode(buffered.getvalue()).decode()

        usage = result.get("usage", {})
        completion_tokens = usage.get("completion_tokens", "N/A")
        total_tokens      = usage.get("total_tokens", "N/A")
        tps_str      = f"{(completion_tokens/duration_ms)*1000:.1f} tok/s" if duration_ms and completion_tokens != "N/A" else "N/A"
        duration_str = f"{duration_ms:.0f}ms" if duration_ms else "N/A"
        total_tokens_fmt = f"{total_tokens:,}" if isinstance(total_tokens, int) else str(total_tokens)
        json_chars  = len(formatted_prediction)
        json_lines  = len(formatted_prediction.split("\n"))
        md_chars    = len(markdown_text)
        md_lines    = len(markdown_text.split("\n"))

        section_html = f"""
        <div style="font-family:Arial,sans-serif;max-width:2000px;">
          <div style="display:flex;gap:15px;margin-bottom:30px;padding:20px;background:white;
                      border:2px solid #e0e0e0;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,.1);">
            <div style="flex:0 0 22%;max-width:22%;">
              <h3 style="margin-top:0;color:#555;font-size:14px;">\U0001f4f8 {filename_display}</h3>
              <img src="data:image/{img_format};base64,{img_str}"
                   style="max-width:100%;height:auto;border:1px solid #ddd;border-radius:4px;margin-bottom:10px;">
              <div style="background:#f5f5f5;padding:10px;border-radius:4px;font-size:12px;">
                <div><strong>Dimensions:</strong> {img_width} × {img_height}px</div>
              </div>
            </div>
            <div style="flex:1;min-width:0;">
              <h3 style="margin-top:0;color:#555;font-size:14px;">\U0001f4dd Markdown Output</h3>
              <div style="background:#f0f8ff;padding:12px;border:1px solid #b0d4ff;border-radius:4px;
                          max-height:400px;overflow-y:auto;white-space:pre-wrap;
                          font-family:'Courier New',monospace;font-size:11px;line-height:1.4;margin-bottom:10px;">
{markdown_text}
              </div>
              <div style="background:#f5f5f5;padding:10px;border-radius:4px;font-size:12px;">
                <div><strong>Characters:</strong> {md_chars}</div>
                <div><strong>Lines:</strong> {md_lines}</div>
              </div>
            </div>
            <div style="flex:1;min-width:0;">
              <h3 style="margin-top:0;color:#555;font-size:14px;">\u2705 JSON Output</h3>
              <div style="background:#f9f9f9;padding:12px;border:1px solid #ddd;border-radius:4px;
                          max-height:400px;overflow-y:auto;white-space:pre-wrap;
                          font-family:'Courier New',monospace;font-size:11px;line-height:1.4;margin-bottom:10px;">
{formatted_prediction}
              </div>
              <div style="background:#f5f5f5;padding:10px;border-radius:4px;font-size:12px;">
                <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:6px;margin-bottom:6px;">
                  <div><strong>Characters:</strong> {json_chars}</div>
                  <div><strong>Lines:</strong> {json_lines}</div>
                </div>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;padding-top:6px;border-top:1px solid #ddd;">
                  <div><strong>\u23f1\ufe0f Duration:</strong> <span style="color:#0066cc;">{duration_str}</span></div>
                  <div><strong>Speed:</strong> <span style="color:#00aa00;">{tps_str}</span></div>
                  <div><strong>Tokens:</strong> {total_tokens_fmt}</div>
                </div>
              </div>
            </div>
            <div style="flex:1;min-width:0;">
              <h3 style="margin-top:0;color:#555;font-size:14px;">\U0001f4cb JSON Schema</h3>
              <div style="background:#fff8e1;padding:12px;border:1px solid #ffd54f;border-radius:4px;
                          max-height:400px;overflow-y:auto;white-space:pre-wrap;
                          font-family:'Courier New',monospace;font-size:11px;line-height:1.4;">
{formatted_schema}
              </div>
            </div>
          </div>
        </div>
        """
        display(HTML(section_html))
        sys.stdout.flush()
