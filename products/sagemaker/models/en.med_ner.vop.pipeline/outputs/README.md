Let's explain each of output columns:


## document
Refers to the complete text being analyzed by the pipeline, encompassing all content subjected to entity recognition.

**Example:** "Maria is a 20-year-old girl who was diagnosed with hyperthyroidism 1 month ago."

## ner_chunk
A substring from the document text identified as a named entity.

**Example:** `20-year-old`

## begin
The starting position of the named entity within the document text.

**Example:** `11`

## end
The ending position of the named entity within the document text.

**Example:** `21`

## ner_label
The category or type of the named entity recognized in the text, classified according to a predefined taxonomy of entity types. This classification aids in understanding the entity's role or nature within the document context.

**Example:** `Age`

## confidence
The confidence level the model has in its identification and classification of the named entity. Confidence scores are usually between 0 and 1, with a higher number indicating greater certainty. A score nearing 1 suggests high confidence in the analysis.

**Example:** `0.9618`

