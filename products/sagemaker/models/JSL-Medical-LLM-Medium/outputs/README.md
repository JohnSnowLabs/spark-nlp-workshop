# Medical LLM Medium — Output Format

Responses are delivered in two modes depending on the `stream` field in the request.

---

## Non-Streaming

When `"stream": false` (default), the complete response is returned as a single JSON object.

**Fields:**

| Field | Description |
|---|---|
| `id` | Unique request identifier |
| `object` | Always `"chat.completion"` |
| `created` | Unix timestamp of the response |
| `model` | Model identifier |
| `choices[0].message.role` | Always `"assistant"` |
| `choices[0].message.reasoning` | The model's chain-of-thought reasoning (may be `null`) |
| `choices[0].message.content` | The model's final answer |
| `choices[0].finish_reason` | `"stop"` on normal completion |
| `usage.prompt_tokens` | Tokens in the input |
| `usage.completion_tokens` | Tokens generated in the response |
| `usage.total_tokens` | Sum of prompt and completion tokens |

**Example:**

```json
{
    "id": "chatcmpl-211249_b07f57",
    "object": "chat.completion",
    "created": 1778879617,
    "model": "Medical-LLM-Medium",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "reasoning": "<chain-of-thought reasoning>",
                "content": "<answer text>"
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 968,
        "completion_tokens": 1607,
        "total_tokens": 2575
    }
}
```

> The actual response also includes additional standard OpenAI-compatible fields (e.g. `tool_calls`, `logprobs`, `service_tier`) — these are present but unused (`null`/empty) and can be ignored.

---

## Streaming

When `"stream": true`, the response is delivered incrementally as Server-Sent Events (SSE). Each line is prefixed with `data:` and terminated with a newline. The stream ends with `data: [DONE]`.

Reasoning tokens are streamed first via `delta.reasoning`, followed by answer tokens via `delta.content`. Concatenate all `delta.reasoning` values to reconstruct the full reasoning, then all `delta.content` values for the final answer.

**Fields (per chunk):**

| Field | Description |
|---|---|
| `id` | Consistent identifier across all chunks in the stream |
| `object` | Always `"chat.completion.chunk"` |
| `created` | Unix timestamp |
| `model` | Model identifier |
| `choices[0].delta.reasoning` | Reasoning token fragment. Present during reasoning phase, absent otherwise. |
| `choices[0].delta.content` | Answer token fragment. Present during answer phase, absent otherwise. |
| `choices[0].finish_reason` | `null` for all chunks except the final one, where it is `"stop"` |

**Example:**

```plaintext
data: {"id":"chatcmpl-191543_c31abd","object":"chat.completion.chunk","created":1778879617,"model":"Medical-LLM-Medium","choices":[{"index":0,"delta":{"reasoning":""},"finish_reason":null}]}
data: {"id":"chatcmpl-191543_c31abd","object":"chat.completion.chunk","created":1778879617,"model":"Medical-LLM-Medium","choices":[{"index":0,"delta":{"reasoning":"Let me think"},"finish_reason":null}]}
data: {"id":"chatcmpl-191543_c31abd","object":"chat.completion.chunk","created":1778879617,"model":"Medical-LLM-Medium","choices":[{"index":0,"delta":{"reasoning":" through this..."},"finish_reason":null}]}
data: {"id":"chatcmpl-191543_c31abd","object":"chat.completion.chunk","created":1778879617,"model":"Medical-LLM-Medium","choices":[{"index":0,"delta":{"content":""},"finish_reason":null}]}
data: {"id":"chatcmpl-191543_c31abd","object":"chat.completion.chunk","created":1778879617,"model":"Medical-LLM-Medium","choices":[{"index":0,"delta":{"content":"**Correct"},"finish_reason":null}]}
data: {"id":"chatcmpl-191543_c31abd","object":"chat.completion.chunk","created":1778879617,"model":"Medical-LLM-Medium","choices":[{"index":0,"delta":{"content":" Answer:"},"finish_reason":null}]}
data: {"id":"chatcmpl-191543_c31abd","object":"chat.completion.chunk","created":1778879617,"model":"Medical-LLM-Medium","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}
data: [DONE]
```
