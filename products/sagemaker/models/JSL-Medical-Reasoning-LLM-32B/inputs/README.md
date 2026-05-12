## Input Format

### 1. Chat Completion — Thinking ON

```json
{
    "model": "/opt/ml/model",
    "messages": [
        {"role": "system", "content": "You are a helpful medical assistant."},
        {"role": "user", "content": "What should I do if I have a fever?"}
    ],
    "max_tokens": 8192,
    "temperature": 1.0,
    "top_p": 0.95,
    "presence_penalty": 1.5,
    "top_k": 20,
    "chat_template_kwargs": {"enable_thinking": true}
}
```

### 2. Chat Completion — Thinking OFF

```json
{
    "model": "/opt/ml/model",
    "messages": [
        {"role": "system", "content": "You are a helpful medical assistant."},
        {"role": "user", "content": "What should I do if I have a fever?"}
    ],
    "max_tokens": 8192,
    "temperature": 0.7,
    "top_p": 0.8,
    "presence_penalty": 1.5,
    "top_k": 20,
    "chat_template_kwargs": {"enable_thinking": false}
}
```

For additional parameters:  
- [ChatCompletionRequest](https://github.com/vllm-project/vllm/blob/v0.17.0/vllm/entrypoints/openai/chat_completion/protocol.py#L150)

### 3. Text Completion

```json
{
    "model": "/opt/ml/model",
    "prompt": "<|im_start|>system\nYou are a helpful medical assistant.<|im_end|>\n<|im_start|>user\n{question}<|im_end|>\n<|im_start|>assistant\n<think>\n",
    "max_tokens": 8192,
    "temperature": 1.0,
    "top_p": 0.95,
    "presence_penalty": 1.5,
    "top_k": 20
}
```

Reference:  
- [CompletionRequest](https://github.com/vllm-project/vllm/blob/v0.17.0/vllm/entrypoints/openai/completion/protocol.py#L42)

### 4. Image + Text Inference

```json
{
    "model": "/opt/ml/model",
    "messages": [
        {"role": "system", "content": "You are a helpful medical assistant."},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What does this medical image show?"},
                {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
            ]
        }
    ],
    "max_tokens": 8192,
    "temperature": 0.7,
    "top_p": 0.8,
    "presence_penalty": 1.5,
    "top_k": 20
}
```
Reference:
- [Multimodal Inputs](https://docs.vllm.ai/en/v0.10.1.1/features/multimodal_inputs.html)

### Important Notes:
- **Thinking ON**: use `temperature=1.0, top_p=0.95` and `"chat_template_kwargs": {"enable_thinking": true}`
- **Thinking OFF**: use `temperature=0.7, top_p=0.8` and `"chat_template_kwargs": {"enable_thinking": false}`
- **Thinking toggle** is only supported in chat completions. For text completions, thinking is controlled via the prompt (see examples below).
- **Streaming**: Add `"stream": true` to your request payload to enable streaming.
- **Model Path**: Always set `"model": "/opt/ml/model"` (SageMaker's fixed model location).