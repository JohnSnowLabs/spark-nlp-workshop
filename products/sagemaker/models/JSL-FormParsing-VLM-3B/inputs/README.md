## Input Format  

### Chat Completion  

#### Example Payload

##### Online Image Example

```json  
{
    "model": "/opt/ml/model",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "url": "https://raw.githubusercontent.com/JohnSnowLabs/visual-nlp-workshop/7f5eec01dd96897dccb064d1e42a4ef2e90083a0/jupyter/data/funsd/83823750.png"
                }
            ]
        }
    ]
} 
```  

For additional parameters:  
- [ChatCompletionRequest](https://github.com/vllm-project/vllm/blob/v0.7.3/vllm/entrypoints/openai/protocol.py#L212)  
- [OpenAI's Chat API](https://platform.openai.com/docs/api-reference/chat/create)  

---  


##### Offline Image Example (Base64)
```json
{
    "model": "/opt/ml/model",
    "messages": [
        {"role": "system", "content": "You are a helpful medical assistant."},
        {
            "role": "user",
            "content": [
                {
                 "type": "image_url",
                 "image_url": "data:image/jpeg;base64,..."
                }
            ]
        }
    ]
}
```

Reference:
- [vLLM Vision Language Models Documentation](https://docs.vllm.ai/en/v0.6.2/models/vlm.html)

---  

### Important Notes:
- **Model Path Requirement:** Always set `"model": "/opt/ml/model"` (SageMaker's fixed model location)
