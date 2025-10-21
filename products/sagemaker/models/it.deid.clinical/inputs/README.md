### Input Format

To use the model, you need to provide input in one of the following supported formats:

#### JSON Format

Provide input as JSON. We support two variations within this format:

1. **Array of Text Documents**: 
   Use an array containing multiple text documents. Each element represents a separate text document.

   ```json
   {
       "text": [
           "Text document 1",
           "Text document 2",
           ...
       ]
   }

    ```

2. **Single Text Document**:
   Provide a single text document as a string.


   ```json
    {
        "text": "Single text document"
    }
   ```

#### JSON Lines (JSONL) Format

Provide input in JSON Lines format, where each line is a JSON object representing a text document.

```
{"text": "Text document 1"}
{"text": "Text document 2"}
```

### Important Parameter

- **masking_policy**: `str`

    Users can select a masking policy to determine how sensitive entities are handled:

    Example: "**PZ: Giancarlo Binaghi, CODICE FISCALE: MVANSK92F09W408A, INDIRIZZO: Viale Burcardo 7, CITTÀ : Napoli**"

    - **masked**: Default policy that masks entities with their type.

      -> 'PZ: `<DOCTOR>`, CODICE FISCALE: `<SSN>`, INDIRIZZO: `<STREET>`, CITTÀ : `<CITY>`'

    - **obfuscated**: Replaces sensitive entities with random values of the same type.

      -> 'PZ:`Germana Maglio-Dovara`, CODICE FISCALE: `ECI-QLN77G15L455Y`, INDIRIZZO: `Viale Orlando 808`, CITTÀ : `Sesto Raimondo`'

    - **masked_fixed_length_chars**: Masks entities with a fixed length of asterisks (\*).

      -> 'PZ: `****`, CODICE FISCALE: `****`, INDIRIZZO: `****`, CITTÀ : `****`'

    - **masked_with_chars**: Masks entities with asterisks (\*).

      -> 'PZ: [`***************`], CODICE FISCALE: [`**************`], INDIRIZZO: [`**************`], CITTÀ : [`****`]'

    
You can specify these parameters in the input as follows:

```json
{
    "text": [
        "Text document 1",
        "Text document 2",
        ...
    ],
    "masking_policy": "masked",
}
```