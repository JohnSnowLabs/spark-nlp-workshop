import io
import base64
import json
from io import BytesIO
from PIL import Image
from IPython.display import display, HTML, clear_output
import ipywidgets as widgets
import json



def show_structured_extraction_comparison(
    image_sources, 
    schema_paths, 
    results, 
    duration_ms_list, 
    markdown_texts, 
    title="Structured Data Extraction Demo"
):
    """
    Display images, markdown, schemas, and structured predictions side-by-side with metrics
    Renders one image at a time to avoid blocking
    
    Args:
        image_sources: Single PIL Image/path or list of PIL Images/paths
        schema_paths: Single path/JSON string or list of paths/JSON strings to schemas
        results: Single result dict or list of result dicts from vLLM endpoint
        duration_ms_list: Single duration (scalar) or list of durations in milliseconds
                         If scalar, it will be used for all images (e.g., batch job total time)
        markdown_texts: Single markdown string or list of markdown strings
        title: Optional title for the comparison
    """
    # Normalize inputs to lists
    if not isinstance(image_sources, list):
        image_sources = [image_sources]
    if isinstance(schema_paths, str):
        schema_paths = [schema_paths]
    if isinstance(results, dict):
        results = [results]
    if isinstance(markdown_texts, str):
        markdown_texts = [markdown_texts]
    
    # Handle duration_ms_list - if scalar, replicate for all images
    if isinstance(duration_ms_list, (int, float)):
        duration_ms_list = [duration_ms_list] * len(image_sources)
    
    num_imgs = len(image_sources)
    
    # Display title first
    display(HTML(f"""
    <div style="font-family: Arial, sans-serif; max-width: 2000px;">
        <h2 style="margin-bottom: 20px; color: #333;">{title}</h2>
    </div>
    """))
    
    # Render each image individually
    for idx, (image_source, schema_source, result, duration_ms, markdown_text) in enumerate(
        zip(image_sources, schema_paths, results, duration_ms_list, markdown_texts), 1
    ):
        # Extract filename for display (without extension)
        if isinstance(image_source, str):
            from pathlib import Path
            filename_display = Path(image_source).stem
        else:
            filename_display = f"Image {idx}"
        
        # Extract prediction text
        prediction_text = result['choices'][0]['message']['content']
        
        # Pretty print the JSON prediction
        try:
            prediction_json = json.loads(prediction_text)
            formatted_prediction = json.dumps(prediction_json, indent=2)
        except:
            formatted_prediction = prediction_text
        
        # Load and format schema - handle both file path and JSON string
        try:
            # First, try to parse as JSON string
            schema = json.loads(schema_source)
        except (json.JSONDecodeError, TypeError):
            # If that fails, treat it as a file path
            try:
                with open(schema_source, 'r') as f:
                    schema = json.load(f)
            except:
                # If both fail, use the raw string
                schema = schema_source
        
        try:
            formatted_schema = json.dumps(schema, indent=2)
        except:
            formatted_schema = str(schema)
        
        # Load image (handle both PIL Image and file path)
        if isinstance(image_source, Image.Image):
            img = image_source
        else:
            img = Image.open(image_source)
        
        img_width, img_height = img.size
        
        # Optimize image size before base64 encoding
        MAX_WIDTH = 800
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / img.width
            new_size = (MAX_WIDTH, int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert image to base64 with optimization
        buffered = BytesIO()
        if img.mode == 'RGBA':
            img.save(buffered, format="PNG", optimize=True)
            img_format = "png"
        else:
            # Convert to RGB if needed and use JPEG for better compression
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(buffered, format="JPEG", quality=85, optimize=True)
            img_format = "jpeg"
        
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Extract metrics from response
        usage = result.get('usage', {})
        prompt_tokens = usage.get('prompt_tokens', 'N/A')
        completion_tokens = usage.get('completion_tokens', 'N/A')
        total_tokens = usage.get('total_tokens', 'N/A')
        
        # Calculate tokens per second
        if duration_ms and completion_tokens != 'N/A':
            tokens_per_sec = (completion_tokens / duration_ms) * 1000
            tps_str = f"{tokens_per_sec:.1f} tok/s"
        else:
            tps_str = "N/A"
        
        # Character and line counts
        json_char_count = len(formatted_prediction)
        json_line_count = len(formatted_prediction.split('\n'))
        markdown_char_count = len(markdown_text)
        markdown_line_count = len(markdown_text.split('\n'))
        
        # Format duration
        duration_str = f"{duration_ms:.0f}ms" if duration_ms else "N/A"
        
        # Create section HTML with 4 columns for this single image
        section_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 2000px;">
            <div style="display: flex; gap: 15px; margin-bottom: 30px; padding: 20px; background: white; border: 2px solid #e0e0e0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <!-- Image Panel -->
                <div style="flex: 0 0 22%; max-width: 22%;">
                    <h3 style="margin-top: 0; color: #555; font-size: 14px;">📸 {filename_display}</h3>
                    <img src="data:image/{img_format};base64,{img_str}" 
                         style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 10px;">
                    
                    <!-- Image Metrics -->
                    <div style="background: #f5f5f5; padding: 10px; border-radius: 4px; font-size: 12px;">
                        <div><strong>Dimensions:</strong> {img_width} × {img_height}px</div>
                    </div>
                </div>
                
                <!-- Markdown Panel -->
                <div style="flex: 1; min-width: 0;">
                    <h3 style="margin-top: 0; color: #555; font-size: 14px;">📝 Markdown Output</h3>
                    <div style="background: #f0f8ff; padding: 12px; border: 1px solid #b0d4ff; border-radius: 4px; 
                                max-height: 400px; overflow-y: auto; white-space: pre-wrap; 
                                font-family: 'Courier New', monospace; font-size: 11px; line-height: 1.4; margin-bottom: 10px;">
{markdown_text}
                    </div>
                    
                    <!-- Markdown Metrics -->
                    <div style="background: #f5f5f5; padding: 10px; border-radius: 4px; font-size: 12px;">
                        <div><strong>Characters:</strong> {markdown_char_count}</div>
                        <div><strong>Lines:</strong> {markdown_line_count}</div>
                    </div>
                </div>
                
                <!-- JSON Panel -->
                <div style="flex: 1; min-width: 0;">
                    <h3 style="margin-top: 0; color: #555; font-size: 14px;">✅ JSON Output</h3>
                    <div style="background: #f9f9f9; padding: 12px; border: 1px solid #ddd; border-radius: 4px; 
                                max-height: 400px; overflow-y: auto; white-space: pre-wrap; 
                                font-family: 'Courier New', monospace; font-size: 11px; line-height: 1.4; margin-bottom: 10px;">
{formatted_prediction}
                    </div>
                    
                    <!-- JSON Metrics -->
                    <div style="background: #f5f5f5; padding: 10px; border-radius: 4px; font-size: 12px;">
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-bottom: 6px;">
                            <div><strong>Characters:</strong> {json_char_count}</div>
                            <div><strong>Lines:</strong> {json_line_count}</div>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; padding-top: 6px; border-top: 1px solid #ddd;">
                            <div><strong>⏱️ Duration:</strong> <span style="color: #0066cc;">{duration_str}</span></div>
                            <div><strong>Speed:</strong> <span style="color: #00aa00;">{tps_str}</span></div>
                            <div><strong>Tokens:</strong> {total_tokens:,}</div>
                        </div>
                    </div>
                </div>
                
                <!-- Schema Panel -->
                <div style="flex: 1; min-width: 0;">
                    <h3 style="margin-top: 0; color: #555; font-size: 14px;">📋 JSON Schema</h3>
                    <div style="background: #fff8e1; padding: 12px; border: 1px solid #ffd54f; border-radius: 4px; 
                                max-height: 400px; overflow-y: auto; white-space: pre-wrap; 
                                font-family: 'Courier New', monospace; font-size: 11px; line-height: 1.4;">
{formatted_schema}
                    </div>
                </div>
            </div>
        </div>
        """
        
        # Display this image immediately
        display(HTML(section_html))
        
        # Force flush to ensure rendering happens
        import sys
        sys.stdout.flush()




def setup_streaming_display(img_path, schema_path, max_height='600px'):
    """
    Set up the 3-column layout and return the output widget for streaming.
    
    Args:
        img_path: Path to input image
        schema_path: Path to JSON schema file
        max_height: Maximum height for scrollable sections (default: '600px')
        
    Returns:
        output_widget: The Output widget to stream into
    """
    # Load data
    img_pil = Image.open(img_path)
    schema_data = json.loads(json.load(open(schema_path)))
    
    # Convert PIL image to base64
    buffered = BytesIO()
    img_pil.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Create widgets with height limits
    img_widget = widgets.HTML(f'<img src="data:image/png;base64,{img_str}" style="max-width:400px;">')
    schema_widget = widgets.HTML(f'<pre style="max-height:{max_height}; overflow-y:auto;">{json.dumps(schema_data, indent=2)}</pre>')
    output_widget = widgets.Output(layout=widgets.Layout(max_height=max_height, overflow_y='auto'))
    
    # Create sections
    img_section = widgets.VBox([
        widgets.HTML('<h3>Input Image</h3>'),
        img_widget
    ])
    
    schema_section = widgets.VBox([
        widgets.HTML('<h3>Input Schema</h3>'),
        schema_widget
    ])
    
    output_section = widgets.VBox([
        widgets.HTML('<h3>Model Response</h3>'),
        output_widget
    ])
    
    # Display layout
    display(widgets.HBox([img_section, schema_section, output_section]))
    
    return output_widget


###### WIDGETS

UNIFIED_COOL_SAMPLES = {
    # Format: (dataset_name, index, description)
    'omni_5': ('omni', 5, "lab_order"),
    'omni_7': ('omni', 7, "drivers_license"),
    'omni_9': ('omni', 9, "invoice_scan"),
    'omni_10': ('omni', 10, "fiscal_invoice"),
    'omni_17': ('omni', 17, "payment_check"),
    'omni_18': ('omni', 18, "financial_liquidity_chart"),
    'omni_19': ('omni', 19, "scanned_receipt"),
    'omni_39': ('omni', 39, "photo_receipt"),
    'omni_36': ('omni', 36, "handwritten_table"),
    'omni_47': ('omni', 47, "nutrients_food_package_photo"),
    'omni_48': ('omni', 48, "cigarette_specification_noisy_scan"),
    'omni_45': ('omni', 45, "excel_screenshot"),
    'omni_51': ('omni', 51, "car_specs_website_screenshot"),
    'omni_61': ('omni', 61, "nutrients_food_package_photo_2"),
    'omni_67': ('omni', 67, "demographic_data_chart_metrics"),
    'omni_69': ('omni', 69, "employee_data_sustainability_report"),
    'omni_998': ('omni', 998, "petition_signature"),
    'omni_996': ('omni', 996, "lease_agreement"),
    'omni_990': ('omni', 990, "us_tax_return_form"),
    'omni_988': ('omni', 988, "us_tax_return_form_2"),
    'omni_887': ('omni', 887, "portfolio_account_overview"),
    'omni_883': ('omni', 883, "nutritional_table"),
    'omni_882': ('omni', 882, "quarterly_transactions_insights"),
    'omni_880': ('omni', 880, "hand_drawn_table"),
    'omni_879': ('omni', 879, "staff_schedule"),
    'omni_877': ('omni', 877, "new_patient_form"),
    'omni_876': ('omni', 876, "lease_agreement_form"),
    'omni_853': ('omni', 853, "drivers_license_california"),
    'omni_845': ('omni', 845, "medical_equipment_inspection_checklist"),
    'omni_843': ('omni', 843, "medical_equipment_inspection_checklist_2"),
    'omni_842': ('omni', 842, "patents_document_table"),
    'omni_834': ('omni', 834, "portfolio_holding_statement"),
    'omni_827': ('omni', 827, "medical_staff_shift_schedule"),
    'omni_826': ('omni', 826, "chase_long_transaction_report"),
    'omni_824': ('omni', 824, "medical_staff_shift_schedule_2"),
}


def create_ocr_demo_widget(endpoint_name, extract_func):
    """
    Create an interactive OCR demo widget with drag-and-drop file upload
    
    Args:
        endpoint_name: SageMaker endpoint name
        extract_func: Function to call for extraction (extract_structured_data_from_image)
    """
    
    # Default generic document classifier schema
    default_schema = """{
  "document_type": "string (e.g., invoice, receipt, medical report, form, license, contract)",
  "document_metadata": {
    "document_number": "string (document/reference/ID number if present)",
    "issue_date": "string (date in ISO format YYYY-MM-DD)",
    "expiry_date": "string (expiry/due date if applicable)",
    "issuer": "string (organization/person who issued the document)",
    "recipient": "string (person/organization receiving the document)"
  },
  "key_entities": {
    "people": ["list of person names mentioned"],
    "organizations": ["list of organizations mentioned"],
    "locations": ["list of locations/addresses mentioned"],
    "amounts": ["list of monetary amounts with currency"]
  },
  "document_summary": "string (2-3 sentence summary of document content)",
  "extracted_fields": {
    "field_name": "field_value (add any document-specific fields as key-value pairs)"
  },
  "confidence_notes": "string (any unclear or low-confidence extractions)"
}"""
    
    # Create widgets
    upload_widget = widgets.FileUpload(
        accept='image/*',
        multiple=False,
        description='Upload Image',
        button_style='info',
        icon='upload'
    )
    
    # JSON Schema input (mandatory with default)
    schema_input = widgets.Textarea(
        value=default_schema,
        placeholder='Define JSON schema for extraction',
        description='JSON Schema:',
        layout=widgets.Layout(width='800px', height='300px'),
        style={'description_width': '100px'}
    )
    
    extract_button = widgets.Button(
        description='Extract Data',
        button_style='success',
        icon='play',
        layout=widgets.Layout(width='150px')
    )
    
    clear_button = widgets.Button(
        description='Clear',
        button_style='warning',
        icon='trash',
        layout=widgets.Layout(width='150px')
    )
    
    reset_schema_button = widgets.Button(
        description='Reset Schema',
        button_style='info',
        icon='refresh',
        layout=widgets.Layout(width='150px')
    )
    
    output = widgets.Output()
    
    def on_extract_click(b):
        with output:
            clear_output(wait=True)
            
            if not upload_widget.value:
                display(HTML('<div style="color: red; padding: 10px;">⚠️ Please upload an image first!</div>'))
                return
            
            if not schema_input.value.strip():
                display(HTML('<div style="color: red; padding: 10px;">⚠️ JSON Schema is required! Please provide a schema.</div>'))
                return
            
            try:
                # Get uploaded image
                uploaded_file = upload_widget.value[0]
                image_bytes = uploaded_file['content']
                pil_image = Image.open(io.BytesIO(image_bytes))
                
                # Get schema
                schema = schema_input.value.strip()
                
                # Extract data
                display(HTML('<div style="color: blue; padding: 10px;">🔄 Processing image with schema...</div>'))
                result, duration, markdown_prediction = extract_func(
                    pil_image, 
                    schema, 
                    endpoint_name
                )
                
                clear_output(wait=True)
                show_structured_extraction_comparison(pil_image, schema, result, duration, markdown_prediction)
                
            except Exception as e:
                clear_output(wait=True)
                display(HTML(f'<div style="color: red; padding: 10px;">❌ Error: {str(e)}</div>'))
                import traceback
                print(traceback.format_exc())
    
    def on_clear_click(b):
        upload_widget.value = ()
        with output:
            clear_output()
    
    def on_reset_schema_click(b):
        schema_input.value = default_schema
        with output:
            clear_output()
            display(HTML('<div style="color: green; padding: 10px;">✅ Schema reset to default</div>'))
    
    extract_button.on_click(on_extract_click)
    clear_button.on_click(on_clear_click)
    reset_schema_button.on_click(on_reset_schema_click)
    
    # Layout
    display(HTML("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h2 style="color: white; margin: 0;">🔍 Interactive Structured OCR Demo</h2>
        <p style="color: #f0f0f0; margin: 5px 0 0 0;">Upload any document image to extract structured data using JSON schemas</p>
    </div>
    """))
    
    display(HTML("""
    <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin-bottom: 15px; border-radius: 4px;">
        <strong>💡 Tip:</strong> Customize the JSON schema below to match your document structure. 
        The default schema works as a generic document classifier that extracts metadata, entities, and key fields.
    </div>
    """))
    
    display(widgets.VBox([
        upload_widget,
        schema_input,
        widgets.HBox([extract_button, clear_button, reset_schema_button]),
        output
    ]))


# Helper function to get image and schema from unified samples
def get_image_and_schema_from_unified(key, omni_ds):
    """Get PIL image and JSON schema from unified sample key"""
    dataset_name, idx, description = UNIFIED_COOL_SAMPLES[key]
    return omni_ds['test'][idx]['image'], omni_ds['test'][idx]['json_schema']


def create_benchmark_widget(omni_dataset, endpoint_name, extract_func):
    """
    Run benchmark on selected samples with repeat options
    
    Args:
        omni_dataset: OMNI dataset
        endpoint_name: SageMaker endpoint name
        extract_func: Function to call for extraction (extract_structured_data_from_image)
    """
    
    # Create options
    sample_options = [(f"OMNI #{data[1]}: {data[2]}", key) 
                      for key, data in UNIFIED_COOL_SAMPLES.items()]
    
    sample_selector = widgets.SelectMultiple(
        options=sample_options,
        description='Samples:',
        rows=10,
        layout=widgets.Layout(width='500px')
    )
    
    # Repeat selector
    repeat_selector = widgets.IntSlider(
        value=1,
        min=1,
        max=10,
        step=1,
        description='Repeats:',
        continuous_update=False,
        orientation='horizontal',
        layout=widgets.Layout(width='400px'),
        style={'description_width': '80px'}
    )
    
    run_button = widgets.Button(
        description='Run Benchmark',
        button_style='danger',
        icon='chart-bar',
        layout=widgets.Layout(width='200px')
    )
    
    progress = widgets.IntProgress(
        min=0,
        max=100,
        description='Progress:',
        bar_style='info',
        orientation='horizontal',
        layout=widgets.Layout(width='500px')
    )
    
    # Results output
    results_output = widgets.Output()
    
    def on_run_click(b):
        with results_output:
            clear_output(wait=True)
            
            if not sample_selector.value:
                display(HTML('<div style="color: red; padding: 10px;">⚠️ Please select samples!</div>'))
                return
            
            selected_keys = list(sample_selector.value)
            num_samples = len(selected_keys)
            num_repeats = repeat_selector.value
            total_iterations = num_samples * num_repeats
            
            durations = []
            token_counts = []
            char_counts = []
            
            progress.max = total_iterations
            progress.value = 0
            display(progress)
            
            # Run benchmark with repeats
            for repeat in range(num_repeats):
                for i, key in enumerate(selected_keys):
                    pil_image, schema = get_image_and_schema_from_unified(key, omni_dataset)
                    result, duration, markdown_prediction = extract_func(pil_image, schema, endpoint_name)
                    
                    durations.append(duration)
                    token_counts.append(result['usage']['completion_tokens'])
                    char_counts.append(len(result['choices'][0]['message']['content']))
                    
                    progress.value = repeat * num_samples + i + 1
            
            # Calculate statistics
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            avg_tokens = sum(token_counts) / len(token_counts)
            avg_tps = sum(token_counts) / sum(d/1000 for d in durations)
            total_chars = sum(char_counts)
            
            clear_output(wait=True)
            
            # Display results
            display(HTML(f"""
            <div style="background: white; padding: 20px; border-radius: 8px; border: 2px solid #4CAF50;">
                <h2 style="color: #4CAF50; margin-top: 0;">📈 Benchmark Results</h2>
                
                <div style="background: #e8f5e9; padding: 12px; border-radius: 5px; margin-bottom: 15px;">
                    <strong>Configuration:</strong> {num_samples} sample{"s" if num_samples > 1 else ""} × {num_repeats} repeat{"s" if num_repeats > 1 else ""} = {total_iterations} total runs
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0;">
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #2196F3;">{total_iterations}</div>
                        <div style="color: #666;">Total Runs</div>
                    </div>
                    
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #FF9800;">{avg_duration:.0f}ms</div>
                        <div style="color: #666;">Avg Duration</div>
                    </div>
                    
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #4CAF50;">{avg_tps:.1f}</div>
                        <div style="color: #666;">Avg Tokens/sec</div>
                    </div>
                    
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #9C27B0;">{min_duration:.0f}ms</div>
                        <div style="color: #666;">Min Duration</div>
                    </div>
                    
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #F44336;">{max_duration:.0f}ms</div>
                        <div style="color: #666;">Max Duration</div>
                    </div>
                    
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #00BCD4;">{avg_tokens:.0f}</div>
                        <div style="color: #666;">Avg Tokens</div>
                    </div>
                    
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #607D8B;">{total_chars:,}</div>
                        <div style="color: #666;">Total Characters</div>
                    </div>
                    
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #795548;">{sum(durations)/1000:.1f}s</div>
                        <div style="color: #666;">Total Time</div>
                    </div>
                    
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #009688;">{sum(token_counts):,}</div>
                        <div style="color: #666;">Total Tokens</div>
                    </div>
                </div>
            </div>
            """))
    
    run_button.on_click(on_run_click)
    
    display(HTML("""
    <div style="background: linear-gradient(135deg, #FA8BFF 0%, #2BD2FF 90%); 
                padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h2 style="color: white; margin: 0;">⚡ Performance Benchmark</h2>
        <p style="color: #f0f0f0; margin: 5px 0 0 0;">Test model performance across multiple samples with repeats</p>
    </div>
    """))
    
    display(widgets.VBox([
        sample_selector,
        repeat_selector,
        run_button
    ]))
    
    display(results_output)


def create_random_explorer_widget(omni_dataset, endpoint_name, extract_func):
    """
    Show random samples from OMNI dataset
    
    Args:
        omni_dataset: OMNI dataset
        endpoint_name: SageMaker endpoint name
        extract_func: Function to call for extraction (extract_structured_data_from_image)
    """
    
    random_button = widgets.Button(
        description='🎲 Random Sample',
        button_style='info',
        layout=widgets.Layout(width='200px')
    )
    
    output = widgets.Output()
    
    def on_random_click(b):
        with output:
            clear_output(wait=True)
            
            import random
            
            # Random index from OMNI dataset
            idx = random.randint(0, len(omni_dataset['test']) - 1)
            
            display(HTML(f'<div style="color: blue; padding: 10px;">🔄 Processing OMNI sample #{idx}...</div>'))
            
            pil_image = omni_dataset['test'][idx]['image']
            schema = omni_dataset['test'][idx]['json_schema']
            
            result, duration, markdown_prediction = extract_func(pil_image, schema, endpoint_name)
            
            clear_output(wait=True)
            
            display(HTML(f"""
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 5px solid #2196F3;">
                <h3 style="margin: 0; color: #1976D2;">🎲 Random Sample: OMNI #{idx}</h3>
            </div>
            """))
            
            show_structured_extraction_comparison(pil_image, schema, result, duration, markdown_prediction)
    
    random_button.on_click(on_random_click)
    
    display(HTML("""
    <div style="background: linear-gradient(135deg, #FEC163 0%, #DE4313 100%); 
                padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h2 style="color: white; margin: 0;">🎲 Random Sample Explorer</h2>
        <p style="color: #f0f0f0; margin: 5px 0 0 0;">Discover random samples from OMNI dataset</p>
    </div>
    """))
    
    display(widgets.VBox([
        random_button,
        output
    ]))

def create_batch_comparison_widget(omni_dataset, endpoint_name, extract_func):
    """
    Create widget to compare multiple samples side-by-side
    
    Args:
        omni_dataset: OMNI dataset
        endpoint_name: SageMaker endpoint name
        extract_func: Function to call for extraction (extract_structured_data_from_image)
    """
    
    # Create options
    sample_options = [(f"OMNI #{data[1]}: {data[2]}", key) 
                      for key, data in UNIFIED_COOL_SAMPLES.items()]
    
    sample_selector = widgets.SelectMultiple(
        options=sample_options,
        description='Samples:',
        rows=10,
        layout=widgets.Layout(width='500px')
    )
    
    compare_button = widgets.Button(
        description='Compare Selected',
        button_style='primary',
        icon='columns',
        layout=widgets.Layout(width='200px')
    )
    
    output = widgets.Output()
    
    def on_compare_click(b):
        with output:
            clear_output(wait=True)
            
            if not sample_selector.value:
                display(HTML('<div style="color: red; padding: 10px;">⚠️ Please select at least one sample!</div>'))
                return
            
            selected_keys = list(sample_selector.value)
            
            # Show initial processing message
            display(HTML(f'<div style="color: blue; padding: 10px;">🔄 Processing {len(selected_keys)} image{"s" if len(selected_keys) > 1 else ""}...</div>'))
            
            # Collect all results first
            all_results = []
            for i, key in enumerate(selected_keys, 1):
                pil_image, schema = get_image_and_schema_from_unified(key, omni_dataset)
                _, idx, desc = UNIFIED_COOL_SAMPLES[key]
                
                result, duration, markdown_prediction = extract_func(pil_image, schema, endpoint_name)
                
                all_results.append({
                    'image': pil_image,
                    'schema': schema,
                    'result': result,
                    'duration': duration,
                    'markdown': markdown_prediction,
                    'idx': idx,
                    'desc': desc,
                    'num': i
                })
            
            # Clear processing message and display all results at once
            clear_output(wait=True)
            
            # Display all results
            for i, res in enumerate(all_results):
                if i > 0:
                    display(HTML('<hr style="margin: 40px 0; border: 2px solid #e0e0e0;">'))
                
                display(HTML(f"""
                <div style="background: #f3e5f5; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 5px solid #9C27B0;">
                    <h3 style="margin: 0; color: #7B1FA2;">Sample {res['num']}/{len(all_results)}: OMNI #{res['idx']} - {res['desc']}</h3>
                </div>
                """))
                
                show_structured_extraction_comparison(
                    res['image'], 
                    res['schema'], 
                    res['result'], 
                    res['duration'], 
                    res['markdown']
                )
            
            # Summary at the end
            display(HTML(f"""
            <div style="background: #e8f5e9; padding: 15px; border-radius: 8px; margin-top: 30px; border-left: 5px solid #4CAF50;">
                <strong>✅ Completed:</strong> Processed {len(all_results)} sample{"s" if len(all_results) > 1 else ""} successfully
            </div>
            """))
    
    compare_button.on_click(on_compare_click)
    
    display(HTML("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h2 style="color: white; margin: 0;">📊 Batch Sample Comparison</h2>
        <p style="color: #f0f0f0; margin: 5px 0 0 0;">Select multiple samples to compare results</p>
    </div>
    """))
    
    display(widgets.VBox([
        sample_selector,
        compare_button,
        output
    ]))