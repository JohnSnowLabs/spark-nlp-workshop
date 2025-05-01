## Input Format  

### 1. Chat Completion  

#### Example Payload  
```json  
{  
    "model": "/opt/ml/model",  
    "messages": [  
        {"role": "system", "content": "Eres un asistente médico útil."},  
        {"role": "user", "content": "¿Qué debo hacer si tengo fiebre y dolores corporales?"}  
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
    "prompt": "¿Qué debo hacer si tengo fiebre y dolores corporales?",  
    "max_tokens": 512,  
    "temperature": 0.6  
}  
```  

#### Multiple Prompts Example  
```json  
{  
    "model": "/opt/ml/model",  
    "prompt": [  
        "¿Cómo puedo mantener una buena salud renal?",  
        "¿Cuáles son los síntomas de la hipertensión?"  
    ],  
    "max_tokens": 512,  
    "temperature": 0.6  
}  
```  

Reference:  
- [CompletionRequest](https://github.com/vllm-project/vllm/blob/v0.8.5/vllm/entrypoints/openai/protocol.py#L730)  
- [OpenAI's Completions API](https://platform.openai.com/docs/api-reference/completions/create)  

---  

### Important Notes:
- **Streaming Responses:** Add `"stream": true` to your request payload to enable streaming
- **Model Path Requirement:** Always set `"model": "/opt/ml/model"` (SageMaker's fixed model location)