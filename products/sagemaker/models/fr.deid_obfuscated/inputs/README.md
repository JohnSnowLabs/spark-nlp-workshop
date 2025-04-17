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

    Example: "**PRENOM : Éric, NOM : Lejeune, NUMÉRO DE SÉCURITÉ SOCIALE : 2730235238020, ADRESSE : 74 Boulevard Riou, VILLE : Sainte Annenec**"

    - **masked**: Default policy that masks entities with their type.

      -> 'PRENOM : `<PATIENT>`, NOM : `<PATIENT>`, NUMÉRO DE SÉCURITÉ SOCIALE : `<SSN>`, ADRESSE : `<STREET>`, VILLE : `<CITY>`'

    - **obfuscated**: Replaces sensitive entities with random values of the same type.

      -> 'PRENOM : `Mlle Goncalves`, NOM : `Mme Garnier-Roussel`, NUMÉRO DE SÉCURITÉ SOCIALE : `129022554007724`, ADRESSE : `avenue de Mahe`, VILLE : `Meyer-sur-Lemoine`'

    - **masked_fixed_length_chars**: Masks entities with a fixed length of asterisks (\*).

      -> 'PRENOM : `****`, NOM : `****`, NUMÉRO DE SÉCURITÉ SOCIALE : `****`, ADRESSE : `****`, VILLE : `****`'

    - **masked_with_chars**: Masks entities with asterisks (\*).

      -> 'PRENOM : [`**`], NOM : [`*****`], NUMÉRO DE SÉCURITÉ SOCIALE : [`***********`], ADRESSE : [`***************`], VILLE : [`************`]'

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