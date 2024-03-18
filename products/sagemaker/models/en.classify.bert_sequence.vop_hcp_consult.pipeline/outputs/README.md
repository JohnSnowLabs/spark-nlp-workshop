# Output Format

The output consists of a JSON object with the following structure:

```json
{
    "predictions": [
        {
            "document": "Text of the document 1",
            "prediction": "label",
            "confidence": Score
        },
        {
            "document": "Text of the document 2",
            "prediction": "label",
            "confidence": Score
        },
        ...
    ]
}
```

### Explanation of Fields

- **predictions**: An array containing predictions for each input document.

    - **document**: The original input text for which predictions are made.

    - **prediction**: The predicted label for the input document.

    - **confidence**: The confidence score associated with the prediction, indicating the model's certainty in its prediction.

