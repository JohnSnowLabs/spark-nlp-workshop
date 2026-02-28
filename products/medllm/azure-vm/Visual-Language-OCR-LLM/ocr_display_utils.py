import json
import sys
import base64
import requests
import ipywidgets as widgets
from io import BytesIO
from pathlib import Path
from PIL import Image as PILImage
from IPython.display import display, HTML


def show_ocr_comparison(image_sources, results, duration_ms_list, title="OCR Prediction"):
    """
    Display images and OCR predictions side-by-side with metrics.
    """
    if not isinstance(image_sources, list):
        image_sources = [image_sources]
    if isinstance(results, dict):
        results = [results]
    if isinstance(duration_ms_list, (int, float)):
        duration_ms_list = [duration_ms_list] * len(image_sources)

    num_imgs = len(image_sources)

    display(HTML(f'''<div style="font-family: Arial, sans-serif; max-width: 1600px;">
        <h2 style="margin-bottom: 20px; color: #333;">{title}</h2></div>'''))

    for idx, (image_source, result, duration_ms) in enumerate(zip(image_sources, results, duration_ms_list), 1):
        prediction_text = result["choices"][0]["message"]["content"]

        img = image_source if isinstance(image_source, PILImage.Image) else PILImage.open(image_source)
        img_width, img_height = img.size

        MAX_WIDTH = 800
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / img.width
            img = img.resize((MAX_WIDTH, int(img.height * ratio)), PILImage.Resampling.LANCZOS)

        buffered = BytesIO()
        if img.mode == "RGBA":
            img.save(buffered, format="PNG", optimize=True)
            img_format = "png"
        else:
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(buffered, format="JPEG", quality=85, optimize=True)
            img_format = "jpeg"
        img_str = base64.b64encode(buffered.getvalue()).decode()

        usage = result.get("usage", {})
        completion_tokens = usage.get("completion_tokens", "N/A")
        total_tokens = usage.get("total_tokens", "N/A")
        tps_str = f"{(completion_tokens / duration_ms) * 1000:.1f} tok/s" if duration_ms and completion_tokens != "N/A" else "N/A"
        duration_str = f"{duration_ms:.0f}ms" if duration_ms else "N/A"
        char_count = len(prediction_text)
        line_count = len(prediction_text.split("\n"))
        word_count = len(prediction_text.split())
        total_tokens_fmt = f"{total_tokens:,}" if isinstance(total_tokens, int) else total_tokens

        section_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 1600px;">
            <div style="display: flex; gap: 20px; margin-bottom: 30px; padding: 20px; background: white;
                        border: 2px solid #e0e0e0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="flex: 0 0 auto; max-width: 50%;">
                    <h3 style="margin-top: 0; color: #555;">📸 Image {idx if num_imgs > 1 else ''}</h3>
                    <img src="data:image/{img_format};base64,{img_str}"
                         style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 15px;">
                    <div style="background: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 13px;">
                        <div><strong>Dimensions:</strong> {img_width} × {img_height}px</div>
                    </div>
                </div>
                <div style="flex: 1; min-width: 0;">
                    <h3 style="margin-top: 0; color: #555;">📝 Extracted Text</h3>
                    <div style="background: #f9f9f9; padding: 15px; border: 1px solid #ddd; border-radius: 4px;
                                max-height: 400px; overflow-y: auto; white-space: pre-wrap;
                                font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.5; margin-bottom: 15px;">
{prediction_text}
                    </div>
                    <div style="background: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 13px;">
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 8px;">
                            <div><strong>Characters:</strong> {char_count}</div>
                            <div><strong>Words:</strong> {word_count}</div>
                            <div><strong>Lines:</strong> {line_count}</div>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; padding-top: 8px; border-top: 1px solid #ddd;">
                            <div><strong>⏱️ Duration:</strong> <span style="color: #0066cc;">{duration_str}</span></div>
                            <div><strong>Speed:</strong> <span style="color: #00aa00;">{tps_str}</span></div>
                            <div><strong>Tokens Processed:</strong> {total_tokens_fmt}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        display(HTML(section_html))
        sys.stdout.flush()


def stream_response(url, payload, img_path):
    """
    Display image + live-updating Textarea side by side.
    Tokens are appended to the widget as they arrive — true real-time streaming.
    """
    # Load and encode image
    img_pil = PILImage.open(img_path)
    buffered = BytesIO()
    img_pil.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    img_html = (
        '<div>'
        '<h3 style="margin:0 0 8px 0;color:#555;">\U0001f4f8 Input Image</h3>'
        f'<img src="data:image/png;base64,{img_str}" '
        'style="max-width:480px;border:1px solid #ddd;border-radius:4px;">'
        '</div>'
    )
    img_widget = widgets.HTML(img_html)

    # Textarea updates its .value in-place — browser re-renders each token live
    text_widget = widgets.Textarea(
        value="",
        placeholder="Waiting for response...",
        layout=widgets.Layout(width="600px", height="500px"),
        disabled=True,
    )
    label = widgets.HTML('<h3 style="margin:0 0 8px 0;color:#555;">\U0001f4dd Extracted Text (live)</h3>')
    output_section = widgets.VBox([label, text_widget])

    display(widgets.HBox([img_widget, output_section],
                         layout=widgets.Layout(gap="30px")))

    # Stream and append each token directly to widget value
    response = requests.post(url, json=payload, stream=True)
    accumulated = ""
    for chunk in response.iter_lines():
        if not chunk:
            continue
        decoded = chunk.decode("utf-8")
        if not decoded.startswith("data: "):
            continue
        data = decoded[len("data: "):]
        if data.strip() == "[DONE]":
            break
        try:
            parsed = json.loads(data)
            choice = parsed.get("choices", [{}])[0]
            content = choice.get("delta", {}).get("content") or choice.get("text")
            if content:
                accumulated += content
                text_widget.value = accumulated  # triggers live browser update
        except (KeyError, json.JSONDecodeError):
            continue
