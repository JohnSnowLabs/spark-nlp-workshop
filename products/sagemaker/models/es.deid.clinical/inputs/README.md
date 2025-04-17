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

### Important Parameters

- **masking_policy**: `str`

    Users can select a masking policy to determine how sensitive entities are handled:

    Example: "**Nombre: Danilo. Apellidos: Ramos Portillo. NHC: 4376372. NASS: 35 61051794 56. Domicilio: Calle Fernando Higueras, 27, 7B.**"

    - **masked**: Default policy that masks entities with their type.

      -> 'Nombre: `<PATIENT>`. Apellidos: `<PATIENT>`. NHC: `<SSN>`. NASS: `<ID>`. Domicilio: `<PATIENT>`, `<AGE>`, 7B.'

    - **obfuscated**: Replaces sensitive entities with random values of the same type.

      -> 'Nombre: `Aurora Garrido Paez`.Apellidos: `Antonio González Cuevas`.NHC: `BBBBBBBBQR648597`.NASS: `48.124.111S`. Domicilio: `Aurora Garrido Paez`, `36`, 7B.'

    - **masked_fixed_length_chars**: Masks entities with a fixed length of asterisks (\*).

      -> 'Nombre: `****`. Apellidos: `****`. NHC: `****`. NASS: `****`. Domicilio: `****`, `****`, 7B.'

    - **masked_with_chars**: Masks entities with asterisks (\*).

      -> 'Nombre: [`****`]. Apellidos: [`************`]. NHC: [`*****`]. NASS: [`************`]. Domicilio: [`*********************`], `**`, 7B.'

- **sep**: `str`

    Separator used to join subparts within each prediction.

    By default, the separator is set to a single space (" "), but users can specify any other separator as needed. Necessary because the model outputs predictions as separate subparts, and the chosen separator is used to join them into coherent text.

    The separator must be one of the following characters: space (' '), newline ('\n'), comma (','), tab ('\t'), or colon (':').
    
You can specify these parameters in the input as follows:

```json
{
    "text": [
        "Text document 1",
        "Text document 2",
        ...
    ],
    "masking_policy": "masked",
    "sep": " ",
}
```