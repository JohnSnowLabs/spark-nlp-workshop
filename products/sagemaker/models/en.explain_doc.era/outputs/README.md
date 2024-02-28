Let's explain each of the output columns :


### `document`
**Description:** The text under analysis, offering context for the extraction.

**Example:** She is admitted to The John Hopkins Hospital 2 days ago with a history of gestational diabetes mellitus diagnosed. She denied pain and any headache. She was seen by the endocrinology service and she was discharged on 03/02/2018 on 40 units of insulin glargine, 12 units of insulin lispro, and metformin 1000 mg two times a day. She had close follow-up with endocrinology post discharge.

### `relation`
**Description:** Specifies the type of relationship identified between two entities. "

**Example:** The `AFTER` relation between the patient being "admitted" and their admission to "The John Hopkins Hospital" implies a sequence of events, where the admission precedes the involvement with the specific clinical department.

### `entity1`
**Description:** Identifies the category of the first entity in the relationship.

**Example:** The term "admitted" falls under `OCCURRENCE` denoting the event of the patient's admission to the hospital.

### `entity1_begin` & `entity1_end`
**Description:** These are numerical indicators for the starting and ending character positions of the first entity within the document, pinpointing its exact location.

**Example Positions:** Character positions from  `7-14` accurately locate "admitted" in the document.

### `chunk1`
**Description:** This is the direct text snippet from the document identified as the first entity, facilitating the extraction's specificity and accuracy.

**Example:** `admitted` is highlighted as the chunk, indicating the action of being admitted.

### `entity2`
**Description:** Similar to `entity1`, this identifies the second entity's category.

**Example:** "The John Hopkins Hospital" is categorized as `CLINICAL_DEPT` signifying the specific department responsible for the patient's care.

### `entity2_begin` & `entity2_end`
**Description:** Mark the start and end character positions of the second entity within the document, analogous to `entity1_begin` and `entity1_end` but for the second entity.

**Example Positions:** Characters from `19-43` define the placement of "The John Hopkins Hospital" in the text.

### `chunk2`
**Description:** The exact text snippet identified as the second entity, providing concrete evidence of the clinical department involved.

**Example:** `The John Hopkins Hospital` is extracted as the chunk, denoting the facility where the patient was admitted.

### `confidence`
**Description:** A numerical value indicating the confidence level in the relationship extraction and entity identification, ranging from 0 to 1. 

**Example:** The confidence score of `0.9621104` underscores the system's strong assurance in correctly identifying relationship extraction and entity identification.



