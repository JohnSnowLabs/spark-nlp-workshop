## Input Format  

### 1. Chat Completion  

#### Example Payload  
```json  
{  
    "model": "/opt/ml/model",  
    "messages": [  
        {"role": "system", "content": "You are a helpful medical assistant."},  
        {"role": "user", "content": "What should I do if I have a fever and body aches?"}  
    ],  
    "max_tokens": 1024,  
    "temperature": 0.7  
}  
```  

For additional parameters:  
- [ChatCompletionRequest](https://github.com/vllm-project/vllm/blob/v0.8.5/vllm/entrypoints/openai/protocol.py#L232)  
- [OpenAI's Chat API](https://platform.openai.com/docs/api-reference/chat/create)  

---  

### 2. Text Completion  

#### Single Prompt Example  
```json  
{  
    "model": "/opt/ml/model",  
    "prompt": "How can I maintain good kidney health?",  
    "max_tokens": 512,  
    "temperature": 0.6  
}  
```  

#### Multiple Prompts Example  
```json  
{  
    "model": "/opt/ml/model",  
    "prompt": [  
        "How can I maintain good kidney health?",  
        "What are the best practices for kidney care?"  
    ],  
    "max_tokens": 512,  
    "temperature": 0.6  
}  
```  

Reference:  
- [CompletionRequest](https://github.com/vllm-project/vllm/blob/v0.8.5/vllm/entrypoints/openai/protocol.py#L730)  
- [OpenAI's Completions API](https://platform.openai.com/docs/api-reference/completions/create)  

---  

### 3. Image + Text Inference

The model supports both online (direct URL) and offline (base64-encoded) image inputs.

#### Online Image Example
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
    "max_tokens": 2048,
    "temperature": 0.15
}
```

#### Offline Image Example (Base64)
```json
{
    "model": "/opt/ml/model",
    "messages": [
        {"role": "system", "content": "You are a helpful medical assistant."},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What does this medical image show?"},
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
            ]
        }
    ],
    "max_tokens": 2048,
    "temperature": 0.15
}
```

Reference:
- [vLLM Vision Language Models Documentation](https://docs.vllm.ai/en/v0.6.2/models/vlm.html)

---  

### Important Notes:
- **Streaming Responses:** Add `"stream": true` to your request payload to enable streaming
- **Model Path Requirement:** Always set `"model": "/opt/ml/model"` (SageMaker's fixed model location)