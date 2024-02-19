# Input format
  
  
{"**text**": "Input Text that is to be Deidentified",
"**masking_policy**":"Deidentification-Policy we want to follow" (`masked`, if nothing specified)

}

We tried to check the different masking policies with these 4 inputs.

## Input1

masking_policy = `masked` (default)

{"text": "Name : Hendrickson, Ora, Record date: 2093-01-13, # 719435. Dr. John Green,  E-MAIL: green@gmail.com."}



## Input2

masking_policy = `obfuscated`

{"text": "Name : Hendrickson, Ora, Record date: 2093-01-13, # 719435. Dr. John Green,  E-MAIL: green@gmail.com.", "masking_policy":"obfuscated"},


## Input3

masking_policy = `masked_fixed_length_chars`

{"text": "Name : Hendrickson, Ora, Record date: 2093-01-13, # 719435. Dr. John Green,  E-MAIL: green@gmail.com.", "masking_policy":"masked_fixed_length_chars"}



## Input4

masking_policy = `masked_with_chars`

{"text": "Name : Hendrickson, Ora, Record date: 2093-01-13, # 719435. Dr. John Green,  E-MAIL: green@gmail.com.", "masking_policy":"masked_with_chars"}
