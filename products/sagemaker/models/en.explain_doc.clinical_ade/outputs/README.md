
## Explaining the Output

### Assertion Prediction

This segment of the analysis aims to identify and specify the assertions made about entities within the text. It assesses the context to determine the status or condition attributed to each recognized entity.

#### Document

Refers to the complete body of text analyzed. The model scans this text to detect and interpret entities based on the provided information.

- **Example**: "Used Crestor for 10+ years with frequent muscle aches and fatigue. Doctor recently changed me to Naproxen, now experiencing less frequent muscle soreness."

#### Chunk

Highlights a segment of the document identified as containing an entity. This could range from drug names to medical terms or conditions.

- **Example**: `Crestor`

#### Entity

Classifies the identified chunk into a predefined category, aiding in the understanding of its role or significance within the text.

- **Example**: `DRUG`

#### Assertion

Describes the assertion made regarding the entity, such as its presence, absence, or any condition relevant to the context of the document.

- **Example**: `present`

### Relation Prediction

This part of the output deals with the identification and classification of relationships between entities recognized within the text, focusing on how these entities interact or relate to each other.

#### Document

This is the same as in assertion predictions, referring to the entire text under analysis.

#### Chunk_1 and Chunk_2

Represent the text segments where entities involved in a relationship are identified. These chunks are analyzed to understand the nature of their interaction.

- **Example**: chunk_1: `Crestor`, chunk_2: `muscle aches`

#### Entity_1 and Entity_2

These specify the categories of the identified chunks, helping to clarify the relationship by classifying each entity according to its nature.

- **Example**: entity_1: `DRUG`, entity_2: `ADE` (Adverse Drug Event)

#### Relation

Specifies the presence (1) or absence (0) of a relationship between two entities.

- **Example**: `1` 


