
Let's explain each of output columns:

## document
This key refers to the full body of text that the pipeline is analyzing. It includes all the content on which entity recognition is performed. 

Example: The human KCNJ9 (Kir 3.3, GIRK3) is a member of the G-protein-activated inwardly rectifying potassium (GIRK) channel family. Here we describe the genomicorganization of the KCNJ9 locus on chromosome 1q21-23 as a candidate gene forType II diabetes mellitus in the Pima Indian population. The gene spansapproximately 7.6 kb and contains one noncoding and two coding exons separated byapproximately 2.2 and approximately 2.6 kb introns, respectively. We identified14 single nucleotide polymorphisms (SNPs), including one that predicts aVal366Ala substitution, and an 8 base-pair (bp) insertion/deletion. Ourexpression studies revealed the presence of the transcript in various humantissues including pancreas, and two major insulin-responsive tissues: fat andskeletal muscle. The characterization of the KCNJ9 gene should facilitate furtherstudies on the function of the KCNJ9 protein and allow evaluation of thepotential role of the locus in Type II diabetes.

## ner_chunk
It is a substring of the document text that has been identified as a named entity.

Example: `human`

## begin
Indicates the starting position of the named entity within the document text.

Example: `4`

## end
Indicates the ending position of the named entity within the document text.

Example: `8`

## ner_label
It specifies the category or type of the named entity that has been recognized in the text. The value assigned is a label that classifies the entity according to a predefined taxonomy of entity types. This classification helps in understanding the role or nature of the entity within the context of the document.

Example: `Organism`

## confidence
It represents the degree of certainty or confidence that the model has in its identification and classification of the named entity. Confidence scores are typically expressed as a number between 0 and 1, where a higher number indicates greater confidence. A score close to 1, suggests that the system is very certain of its analysis.

Example: `0.9996`