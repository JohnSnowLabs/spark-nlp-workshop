# Output formats
  
These are the deidentified outputs we got for the given inputs

## out1

`masked output`

{
    "predictions": [
       "Name : `<PATIENT>`, Record date: `<DATE>`, # `<DEVICE>`.  Dr. `<DOCTOR>`,  E-MAIL: `<EMAIL>`."
    ]
}


## out2

`obfuscated output`

{
    "predictions": [
        "Name : `Lynne Logan`, Record date: `2093-01-25`, # `L3157974`.  Dr. `Sherlon Handing`,  E-MAIL: `Marvin@yahoo.com`."
    ]
}



## out3

`masked_fixed_length_chars output`

{
    "predictions": [
        "Name : `****`, Record date: `****`, # `****`.  Dr. `****`,  E-MAIL: `****`."
    ]
}



## out4

`masked_with_chars output`

{
    "predictions": [
        "Name : `[**************]`, Record date: `[********]`, # `[****]`.  Dr. `[********]`,  E-MAIL: `[*************]`."
    ]
}
