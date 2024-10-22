### Input Format

To use the model, you need to provide input in one of the following supported formats:

#### Format 1: Single Input

Provide a single input as a JSON object.

```json
{
    "input_text": "input text"
}
```

Alternatively, you can provide a dictionary containing the keys `context` and `question`.

```json
{
    "input_text": {"context": "Context", "question": "Question"},
    "template": "open_book_qa"
}
```

#### Format 2: Multiple Inputs

Provide multiple inputs as a JSON array.

```json
{
    "input_text": [
        "input text 1",
        "input text 2"
    ]
}
```

Alternatively, you can provide an array of dictionaries, where each dictionary contains the keys `context` and `question`.

```json
{
    "input_text": [
        {"context": "Context 1", "question": "Question 1"},
        {"context": "Context 2", "question": "Question 2"}
    ],
    "template": "open_book_qa"
}
```

**Note**: If you provide dictionaries, you can specify the template as `open_book_qa`. If you don't select any template, it will concatenate both strings with a newline.


#### Format 3: JSON Lines (JSONL):

Provide input in JSON Lines format, where each line is a JSON object.
```
{"input_text": "input text 1"}
{"input_text": "input text 2"}
```


### Important Parameters

**Required Parameter:**
- **`input_text`**: The input text(s) provided to the model.
  - **Type**: `Union[str, dict, List[str], List[dict]]`
  - **Constraints**: Provide a string for a single text or a list of strings for multiple inputs. Additionally, you can also provide a dictionary or a list containing multiple dictionaries with keys `context` and `question`. If you select the `open_book_qa` template, the model will format the input accordingly. If no template is selected, the `context` and `question` strings will be concatenated with a newline.

**Optional Parameters for JSON Input Format:**
- **`max_new_tokens`**: The maximum number of tokens the model should generate as output. (*Can be passed as an environment variable when initializing the SageMaker Transformer object for batch inference.*)
  - **Type**: `int`
  - **Default**: `1024`
  - **Constraints**: Must be a positive integer greater than 0.

- **`temperature`**: The temperature parameter controlling the randomness of token generation. (*Can be passed as an environment variable when initializing the SageMaker Transformer object for batch inference.*)
  - **Type**: `float`
  - **Default**: `0.2`
  - **Constraints**: Must be a float between 0.0 and 1.0.

- **`repetition_penalty`**: The repetition penalty parameter that penalizes new tokens based on whether they appear in the prompt and the generated text so far. Values > 1 encourage the model to use new tokens, while values < 1 encourage the model to repeat tokens. (*Can be passed as an environment variable when initializing the SageMaker Transformer object for batch inference.*)
  - **Type**: `float`
  - **Default**: `1.0`
  - **Constraints**: Must be a float greater than 0 and less than or equal to 2.
  
- **`template`**: You can select the predefined template.
  - **Type**: `str`
  - **Default**: `None`
  

You can pick one of the following templates:
```json
{
    "summarization": "Summarize the following document:\n## Document Start ##\n{context}\n## Document End ##",
    "open_book_qa": "Answer the following question based on the given context:\n## Context Start ##\n{context}\n## Context End ##\n## Question Start ##\n{question}\n## Question End ##",
    "closed_book_qa": "Answer the following question:\n## Question Start ##\n{question}\n## Question End ##",
}
```
You can select any of these templates according to your use case. We perform string formatting, then pass it to the chat template.

If no template is provided, we take your `input_text` as it is and do not perform any formatting, directly passing your input to the chat template.

> **Parameter Priority**: User-provided parameters are given priority, followed by environment variables, and finally default values.

---

### Model Configuration

| Parameter                  | Value     | Description                                                                                                                                                                                                                                                                                                                               |
|----------------------------|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **`dtype`**                | `float16` | The data type for the model weights and activations.                                                                                                                                                                                                                                                                                      |
| **`max_model_len`**        | Variable  | This indicates that your input and the model response combined should come under this limit (`input + output <= max_model_len`). This is determined based on total available GPU memory: <ul><li>More than 58 GB GPU memory : 32,768 tokens</li><li>Less than 58 GB GPU memory: Default: 16,384 tokens.</li></ul> |
| **`tensor_parallel_size`** | Variable  | The number of GPUs to use for distributed execution with tensor parallelism.                                                                                                                                                                                                                                                              |

Other than the parameters mentioned above, we are utilizing the default parameters specified for the `LLM` class in the [VLLM documentation](https://docs.vllm.ai/en/latest/dev/offline_inference/llm.html).

#### Instance-Specific `max_model_len` Values

| Instance Type       | GPU Model  | Number of GPUs | Total GPU Memory (GB) | max_model_len   |
|---------------------|------------|----------------|-----------------------|-----------------| 
| `ml.g5.2xlarge`     | NVIDIA A10G| 1              | 24                    | 16,384          |
| `ml.g4dn.12xlarge`  | NVIDIA T4  | 4              | 64                    | 32,768          |


Total Memory values are approximate. Usable memory may be slightly less. For pricing details, visit the [Amazon SageMaker pricing page](https://aws.amazon.com/sagemaker/pricing/).
