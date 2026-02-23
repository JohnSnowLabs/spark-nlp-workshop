## Input Format  
The model is exposed via a [VLLM server](https://docs.vllm.ai/en/latest/)
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
    "temperature": 0.6  
}  
```  

For additional parameters:  
- [ChatCompletionRequest](https://github.com/vllm-project/vllm/blob/v0.13.0/vllm/entrypoints/openai/protocol.py#L525)  
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
- [CompletionRequest](https://github.com/vllm-project/vllm/blob/v0.13.0/vllm/entrypoints/openai/protocol.py#L1010)  
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
    "temperature": 0.1
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
    "temperature": 0.1
}
```

Reference:
- [Multimodal Inputs](https://docs.vllm.ai/en/latest/features/multimodal_inputs.html)

---  



### 4. Structured Output (JSON Schema)

Force the model to output valid JSON matching a specific schema using `response_format`.

#### Example with Schema
```json
{
    "model": "/opt/ml/model",
    "messages": [
        {
            "role": "system",
            "content": "Extract patient information as JSON."
        },
        {
            "role": "user",
            "content": "Patient John Doe, age 45, has hypertension."
        }
    ],
    "temperature": 0.0,
    "max_tokens": 512,
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "patient_info",
            "strict": true,
            "schema": {
                "type": "object",
                "required": ["name", "age", "conditions"],
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "conditions": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        }
    }
}
```

Reference:
- [Structured Outputs (vLLM)](https://docs.vllm.ai/en/latest/features/structured_outputs.html)
- [JSON Schema](https://json-schema.org/)
- [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)





### Important Notes:
- **Streaming Responses:** Add `"stream": true` to your request payload to enable streaming
- **Model Path Requirement:** Always set `"model": "/opt/ml/model"` (SageMaker's fixed model location)






