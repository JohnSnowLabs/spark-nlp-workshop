# Medical LLM Medium — Input Format

```json
{
    "messages": [
        {"role": "system", "content": "You are an expert medical AI assistant."},
        {"role": "user",   "content": "<medical question>"}
    ],
    "stream": false
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `messages` | array | Yes | Conversation messages |
| `stream` | boolean | No | `false` for batch transform. `true` for real-time streaming. |
| `model` | string | No | Accepted but ignored. Inference parameters are fixed server-side. |

The `system` message is optional. If omitted, a default medical system prompt is applied.

Inference parameters (temperature, top_p, max_tokens, etc.) are fixed server-side and cannot be overridden per request.
