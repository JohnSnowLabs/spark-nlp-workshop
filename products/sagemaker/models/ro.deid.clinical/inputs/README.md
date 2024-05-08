## Input Format

To use the pipeline model, you need to provide input in one of the following supported formats:

### Format 1: Array of Text Documents

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

### Format 2: Single Text Document

Provide a single text document as a string.

```json
{
    "text": "Single text document"
}
```


### Format 3: JSON Lines (JSONL):

Provide input in JSON Lines format, where each line is a JSON object representing a text document along with any optional parameters.

```
{"text": "Text document 1"}
{"text": "Text document 2"}
```


### Important Parameters

- **masking_policy**: `str`

    Users can select a masking policy to determine how sensitive entities are handled:

    Example: "**LABORATOR RADStrada AbabeidaSacueni, 354573i, 3545730265-21011065-210110 ,OFFICE@SMURDICE@SMURD**"

    - **masked**: Default policy that masks entities with their type.

      -> 'LABORATOR RADIOLOGIE, `<STREET>`, `<CITY>`, `<ZIP>` , TEL : `<PHONE>` , E-MAIL: `<EMAIL>`'

    - **obfuscated**: Replaces sensitive entities with random values of the same type.

      -> 'LABORATOR RADIOLOGIE, `Intrarea Diaconescu`, `Aiud`, `302784` , TEL : `0263 144 119` , E-MAIL: `jeneltudor@email.ro`'

    - **masked_fixed_length_chars**: Masks entities with a fixed length of asterisks (\*).

      -> 'LABORATOR RADIOLOGIE, `****`, `****`, `****` , TEL : `****` , E-MAIL: `****`'

    - **masked_with_chars**: Masks entities with asterisks (\*).

      -> 'LABORATOR RADIOLOGIE, [`***********`], [`*****`], [`****`] , TEL : [`*********`] , E-MAIL: [`**********`]'

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