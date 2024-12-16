### Input Format

To use the model, provide input in one of the following formats:

#### Format 1: Single Input
Provide a single input as a JSON object.

```json
{
    "input_text": "input text",
    "params": {
        "max_new_tokens": 1024,
        "temperature": 0.7
    }
}
```

Alternatively, provide a dictionary with `context` and `question` keys.

```json
{
    "input_text": {"context": "Context", "question": "Question"},
    "params": {
        "max_new_tokens": 1024,
        "template": "open_book_qa"
    }
}
```

#### Format 2: Multiple Inputs
Provide multiple inputs as a JSON array.

```json
{
    "input_text": [
        "input text 1",
        "input text 2"
    ],
    "params": {
        "max_new_tokens": 1024,
        "temperature": 0.7
    }
}
```

Alternatively, provide an array of dictionaries with `context` and `question` keys.

```json
{
    "input_text": [
        {"context": "Context 1", "question": "Question 1"},
        {"context": "Context 2", "question": "Question 2"}
    ],
    "params": {
        "max_new_tokens": 1024,
        "template": "open_book_qa"
    }
}
```

**Note**: If you provide dictionaries, you can specify the template as `open_book_qa`. If no template is selected, `context` and `question` are concatenated with a newline.

#### Format 3: JSON Lines (JSONL)
Provide input in JSON Lines format, where each line is a JSON object.

```
{"input_text": "input text 1", "params": {"max_new_tokens": 1024}}
{"input_text": "input text 2", "params": {"max_new_tokens": 512}}
```

---

### Important Parameters

**Required Parameter:**
- **`input_text`**: The input text(s) provided to the model.
  - **Type**: `Union[str, dict, List[str], List[dict]]`
  - **Constraints**: Provide a string for a single text or a list of strings for multiple inputs. Additionally, you can provide a dictionary or a list of dictionaries with keys `context` and `question` with `open_book_qa`, and the input will be formatted accordingly before sending to the model. If no template is selected, the `context` and `question` strings will be concatenated with a newline.

**Optional Parameters (Inside `params` Key):**
- **`max_new_tokens`**: The maximum number of tokens the model should generate as output.
  - **Type**: `int`
  - **Default**: `1024`
  - **Constraints**: Must be a positive integer greater than 0.

- **`temperature`**: The temperature parameter controlling the randomness of token generation.
  - **Type**: `float`
  - **Default**: `0.7`
  - **Constraints**: Must be a float greater than or equal to 0.

- **`repetition_penalty`**: Penalizes new tokens based on whether they appear in the prompt and generated text so far. Values > 1 discourage repetition, while values < 1 encourage it.
  - **Type**: `float`
  - **Default**: `1.0`
  - **Constraints**: Must be a float in the range (0.0, 2.0].

- **`top_p`**: Controls nucleus sampling by selecting tokens with a cumulative probability of `top_p`.
  - **Type**: `float`
  - **Default**: `0.9`
  - **Constraints**: Must be a float in (0, 1].

- **`top_k`**: Limits the token selection to the `top_k` most likely tokens.
  - **Type**: `int`
  - **Default**: `50`
  - **Constraints**: Must be -1 (disable) or a positive integer.

- **`template`**: Specifies the predefined template to apply to the input text.
  - **Type**: `str`
  - **Default**: `None`

**Templates Available:**
```json
{
    "summarization": "Summarize the following document:\n## Document Start ##\n{context}\n## Document End ##",
    "open_book_qa": "Answer the following question based on the given context:\n## Context Start ##\n{context}\n## Context End ##\n## Question Start ##\n{question}\n## Question End ##",
    "closed_book_qa": "Answer the following question:\n## Question Start ##\n{question}\n## Question End ##"
}
```
If no template is provided, the `input_text` is used directly without formatting.

> **Parameter Priority**: User-provided parameters take precedence, followed by environment variables, and then default values.

---

### Model Configuration

| Parameter                  | Value     | Description                                                                                                                                                     |
|----------------------------|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **`dtype`**                | `float16` | Data type for model weights and activations.                                                                                                                   |
| **`max_model_len`**        | `32,768`  | Maximum length for input and output combined (`input + output ≤ max_model_len`).                                                                            |
| **`tensor_parallel_size`** | Variable  | Number of GPUs used for distributed execution with tensor parallelism.                                                                                          |

Other parameters use defaults from the [VLLM documentation](https://docs.vllm.ai/en/latest/dev/offline_inference/llm.html).

#### Instance-Specific `max_model_len` Values

| Instance Type       | Inference Type | Number of GPUs | Total GPU Memory (GB) | max_model_len   |
|---------------------|----------------|----------------|------------------------|-----------------|
| `ml.g4dn.12xlarge`  | Real-Time      | 4              | 64                     | 32,768          |
| `ml.g4dn.12xlarge`  | Batch          | 4              | 64                     | 32,768          |

Total memory values are approximate. Usable memory may vary slightly. For pricing, visit the [Amazon SageMaker pricing page](https://aws.amazon.com/sagemaker/pricing/).