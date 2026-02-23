import io
import base64
from io import BytesIO
from PIL import Image
from IPython.display import display, HTML, clear_output
import ipywidgets as widgets
import base64





def show_ocr_comparison(image_sources, results, duration_ms_list, title="OCR Prediction"):
    """
    Display images and OCR predictions side-by-side with metrics
    Renders one image at a time to avoid blocking
    
    Args:
        image_sources: Single PIL Image/path or list of PIL Images/paths
        results: Single result dict or list of result dicts from vLLM endpoint
        duration_ms_list: Single duration (scalar) or list of durations in milliseconds
                         If scalar, it will be used for all images (e.g., batch job total time)
        title: Optional title for the comparison
    """
    # Normalize inputs to lists
    if not isinstance(image_sources, list):
        image_sources = [image_sources]
    if isinstance(results, dict):
        results = [results]
    
    # Handle duration_ms_list - if scalar, replicate for all images
    if isinstance(duration_ms_list, (int, float)):
        duration_ms_list = [duration_ms_list] * len(image_sources)
    
    num_imgs = len(image_sources)
    
    # Display title first
    display(HTML(f"""
    <div style="font-family: Arial, sans-serif; max-width: 1600px;">
        <h2 style="margin-bottom: 20px; color: #333;">{title}</h2>
    </div>
    """))
    
    # Render each image individually
    for idx, (image_source, result, duration_ms) in enumerate(zip(image_sources, results, duration_ms_list), 1):
        # Extract prediction text
        prediction_text = result['choices'][0]['message']['content']
        
        # Load image (handle both PIL Image and file path)
        if isinstance(image_source, (Image.Image)):
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
        
        # Extract model info
        finish_reason = result['choices'][0].get('finish_reason', 'N/A')
        
        # Character and line count
        char_count = len(prediction_text)
        line_count = len(prediction_text.split('\n'))
        word_count = len(prediction_text.split())
        
        # Format duration
        duration_str = f"{duration_ms:.0f}ms" if duration_ms else "N/A"
        
        # Create section HTML for this single image
        section_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 1600px;">
            <div style="display: flex; gap: 20px; margin-bottom: 30px; padding: 20px; background: white; border: 2px solid #e0e0e0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <!-- Image Panel -->
                <div style="flex: 0 0 auto; max-width: 50%;">
                    <h3 style="margin-top: 0; color: #555;">📸 Image {idx if num_imgs > 1 else ''}</h3>
                    <img src="data:image/{img_format};base64,{img_str}" 
                         style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 15px;">
                    
                    <!-- Image Metrics -->
                    <div style="background: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 13px;">
                        <div><strong>Dimensions:</strong> {img_width} × {img_height}px</div>
                    </div>
                </div>
                
                <!-- Prediction Panel -->
                <div style="flex: 1; min-width: 0;">
                    <h3 style="margin-top: 0; color: #555;">📝 Extracted Text</h3>
                    <div style="background: #f9f9f9; padding: 15px; border: 1px solid #ddd; border-radius: 4px; 
                                max-height: 400px; overflow-y: auto; white-space: pre-wrap; 
                                font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.5; margin-bottom: 15px;">
{prediction_text}
                    </div>
                    
                    <!-- Text Metrics -->
                    <div style="background: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 13px;">
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 8px;">
                            <div><strong>Characters:</strong> {char_count}</div>
                            <div><strong>Words:</strong> {word_count}</div>
                            <div><strong>Lines:</strong> {line_count}</div>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; padding-top: 8px; border-top: 1px solid #ddd;">
                            <div><strong>⏱️ Duration:</strong> <span style="color: #0066cc;">{duration_str}</span></div>
                            <div><strong>Speed:</strong> <span style="color: #00aa00;">{tps_str}</span></div>
                            <div><strong>Tokens Processed:</strong> {total_tokens:,}</div>
                        </div>
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


def setup_ocr_stream_display(img_path, prompt, max_height='600px', max_width='500px'):
    """
    Set up the 3-column layout for OCR (image + prompt + output) and return the output widget for streaming.
    
    Args:
        img_path: Path to input image
        prompt: OCR prompt text
        max_height: Maximum height for scrollable sections (default: '600px')
        max_width: Maximum width for text sections (default: '500px')
        
    Returns:
        output_widget: The Output widget to stream into
    """
    # Load image
    img_pil = Image.open(img_path)
    
    # Convert PIL image to base64
    buffered = BytesIO()
    img_pil.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Create widgets with height AND width limits
    img_widget = widgets.HTML(f'<img src="data:image/png;base64,{img_str}" style="max-width:400px;">')
    
    prompt_widget = widgets.HTML(
        f'<pre style="max-height:{max_height}; max-width:{max_width}; overflow-y:auto; overflow-x:auto; white-space:pre-wrap; word-wrap:break-word;">{prompt}</pre>'
    )
    
    output_widget = widgets.Output(
        layout=widgets.Layout(
            max_height=max_height, 
            max_width=max_width,
            overflow_y='auto',
            overflow_x='auto'
        )
    )
    
    # Create sections with constrained widths
    img_section = widgets.VBox([
        widgets.HTML('<h3>Input Image</h3>'),
        img_widget
    ], layout=widgets.Layout(max_width='420px'))
    
    prompt_section = widgets.VBox([
        widgets.HTML('<h3>Prompt</h3>'),
        prompt_widget
    ], layout=widgets.Layout(max_width=max_width))
    
    output_section = widgets.VBox([
        widgets.HTML('<h3>Model Response</h3>'),
        output_widget
    ], layout=widgets.Layout(max_width=max_width))
    
    # Display layout
    display(widgets.HBox([img_section, prompt_section, output_section]))
    
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
    'medocr_0': ('medocr', 0, "grocery_receipt_photo"),
    'medocr_3': ('medocr', 3, "lab_test_blood_count"),
    'medocr_4': ('medocr', 4, "pathologist_lab_report"),
    'medocr_5': ('medocr', 5, "blood_count_table_handwritten"),
    'medocr_17': ('medocr', 17, "microbiology_culture_report_scan"),
    'medocr_21': ('medocr', 21, "haematology_blood_count"),
    'medocr_22': ('medocr', 22, "haematology_report_trauma_center"),
    'medocr_28': ('medocr', 28, "haematology_blood_count_diagnostic_report_noisy_scan"),
    'medocr_40': ('medocr', 40, "hormones_and_markers_report_noisy_scan"),
    'medocr_47': ('medocr', 47, "serology_and_immunology_report_scan"),
    'medocr_49': ('medocr', 49, "pathology_biochemistry_report_scan"),
    'medocr_54': ('medocr', 54, "serology_immunity_report_scan"),
    'medocr_70': ('medocr', 70, "pathologist_lab_report_2"),
    'medocr_99': ('medocr', 99, "blood_liver_test"),
    'medocr_104': ('medocr', 104, "hematology_report_photo"),
    'medocr_114': ('medocr', 114, "hematology_report_scan"),
    'medocr_117': ('medocr', 117, "urine_examination_report_scan"),
    'medocr_128': ('medocr', 128, "liver_kidney_report_scan"),
    'medocr_168': ('medocr', 168, "urine_culture_report"),
    'medocr_169': ('medocr', 169, "haematology_report"),
    'medocr_187': ('medocr', 187, "widal_test_report"),
    'medocr_194': ('medocr', 194, "liver_report"),
    'medocr_198': ('medocr', 198, "pathologist_report"),
    'medocr_221': ('medocr', 221, "biochemistry_report"),
    'medocr_223': ('medocr', 223, "liver_function_test_report"),
    'medocr_230': ('medocr', 230, "haematology_report_2"),
    'medocr_234': ('medocr', 234, "complete_blood_count_report"),
}

def create_ocr_demo_widget(endpoint_name, prompt, invoke_endpoint_func):
    """
    Create an interactive OCR demo widget with drag-and-drop file upload
    
    Args:
        endpoint_name: SageMaker endpoint name
        prompt: Optional custom prompt (uses default if None)
    """
    if prompt is None:
        prompt = "Extract all the text in this image"
    
    # Create widgets
    upload_widget = widgets.FileUpload(
        accept='image/*',
        multiple=False,
        description='Upload Image',
        button_style='info',
        icon='upload'
    )
    
    prompt_input = widgets.Textarea(
        value=prompt,
        placeholder='Enter extraction prompt',
        description='Prompt:',
        layout=widgets.Layout(width='600px', height='80px')
    )
    
    extract_button = widgets.Button(
        description='Extract Text',
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
    
    output = widgets.Output()
    
    def on_extract_click(b):
        with output:
            clear_output(wait=True)
            
            if not upload_widget.value:
                display(HTML('<div style="color: red; padding: 10px;">⚠️ Please upload an image first!</div>'))
                return
            
            try:
                # Get uploaded image
                # uploaded_file = list(upload_widget.value.values())[0]
                uploaded_file = upload_widget.value[0]  # Changed from list(upload_widget.value.values())[0]

                image_bytes = uploaded_file['content']
                pil_image = Image.open(io.BytesIO(image_bytes))
                
                # Extract text
                display(HTML('<div style="color: blue; padding: 10px;">🔄 Processing image...</div>'))
                result, duration = invoke_endpoint_func(
                    pil_image, 
                    endpoint_name, 
                    prompt_input.value
                )
                
                clear_output(wait=True)
                show_ocr_comparison(pil_image, result, duration, title="Your OCR Result")
                
            except Exception as e:
                clear_output(wait=True)
                display(HTML(f'<div style="color: red; padding: 10px;">❌ Error: {str(e)}</div>'))
    
    def on_clear_click(b):
        upload_widget.value = ()
        with output:
            clear_output()
    
    extract_button.on_click(on_extract_click)
    clear_button.on_click(on_clear_click)
    
    # Layout
    display(HTML("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h2 style="color: white; margin: 0;">🔍 Interactive OCR Demo</h2>
        <p style="color: #f0f0f0; margin: 5px 0 0 0;">Upload any image to extract text instantly</p>
    </div>
    """))
    
    display(widgets.VBox([
        upload_widget,
        prompt_input,
        widgets.HBox([extract_button, clear_button]),
        output
    ]))


# Helper function to get image from unified samples
def get_image_from_unified(key, omni_ds, medocr_ds):
    """Get PIL image from unified sample key"""
    dataset_name, idx, description = UNIFIED_COOL_SAMPLES[key]
    if dataset_name == 'omni':
        return omni_ds['test'][idx]['image']
    else:
        return medocr_ds['test'][idx]['image']
def create_benchmark_widget(omni_dataset, medocr_dataset, endpoint_name, prompt, invoke_endpoint_func):
    """
    Run benchmark on selected samples with repeat options
    """
    if prompt is None:
        prompt = "Extract all the text in this image"
    
    # Create options with dataset prefix
    sample_options = [(f"{key.split('_')[0].upper()} #{data[1]}: {data[2]}", key) 
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
                    pil_image = get_image_from_unified(key, omni_dataset, medocr_dataset)
                    result, duration = invoke_endpoint_func(pil_image, endpoint_name, prompt)
                    
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

# =============================================================================
# 4. UPDATED RANDOM EXPLORER - SAMPLES FROM ENTIRE DATASETS
# =============================================================================

def create_random_explorer_widget(omni_dataset, medocr_dataset, endpoint_name, prompt, invoke_endpoint_func ):
    """
    Show random samples from entire datasets (not just curated samples)
    """
    if prompt is None:
        prompt = "Extract all the text in this image"
    
    # Dataset selector
    dataset_selector = widgets.RadioButtons(
        options=['Both (Random)', 'OMNI Only', 'MedOCR Only'],
        description='Dataset:',
        value='Both (Random)',
        layout=widgets.Layout(width='300px')
    )
    
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
            
            # Choose dataset
            choice = dataset_selector.value
            if choice == 'OMNI Only':
                dataset_name = 'OMNI'
                dataset = omni_dataset
            elif choice == 'MedOCR Only':
                dataset_name = 'MedOCR'
                dataset = medocr_dataset
            else:  # Both (Random)
                dataset_name = random.choice(['OMNI', 'MedOCR'])
                dataset = omni_dataset if dataset_name == 'OMNI' else medocr_dataset
            
            # Random index
            idx = random.randint(0, len(dataset['test']) - 1)
            
            display(HTML(f'<div style="color: blue; padding: 10px;">🔄 Processing {dataset_name} sample #{idx}...</div>'))
            
            pil_image = dataset['test'][idx]['image']
            result, duration = invoke_endpoint_func(pil_image, endpoint_name, prompt)
            
            clear_output(wait=True)
            show_ocr_comparison(pil_image, result, duration, title=f"🎲 Random Sample: {dataset_name} #{idx}")
    
    random_button.on_click(on_random_click)
    
    display(HTML("""
    <div style="background: linear-gradient(135deg, #FEC163 0%, #DE4313 100%); 
                padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h2 style="color: white; margin: 0;">🎲 Random Sample Explorer</h2>
        <p style="color: #f0f0f0; margin: 5px 0 0 0;">Discover random samples from entire datasets</p>
    </div>
    """))
    
    display(widgets.VBox([
        dataset_selector,
        random_button,
        output
    ]))


def create_batch_comparison_widget(omni_dataset, medocr_dataset, endpoint_name, prompt, invoke_endpoint_func):
    """
    Create widget to compare multiple samples side-by-side
    """
    if prompt is None:
        prompt = "Extract all the text in this image"
    
    # Create options with dataset prefix
    sample_options = [(f"{key.split('_')[0].upper()} #{data[1]}: {data[2]}", key) 
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
            
            images = []
            results = []
            durations = []
            
            display(HTML(f'<div style="color: blue; padding: 10px;">🔄 Processing {len(sample_selector.value)} images...</div>'))
            
            for key in sample_selector.value:
                pil_image = get_image_from_unified(key, omni_dataset, medocr_dataset)
                result, duration = invoke_endpoint_func(pil_image, endpoint_name, prompt)
                images.append(pil_image)
                results.append(result)
                durations.append(duration)
            
            clear_output(wait=True)
            show_ocr_comparison(images, results, durations, title="Batch Comparison Results")
    
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
