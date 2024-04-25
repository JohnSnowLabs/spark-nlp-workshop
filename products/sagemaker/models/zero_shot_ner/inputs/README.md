## Input Format

To use the model, you need to provide input in one of the following supported formats:

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


## Important Parameters

### Inputs

- **text**: Input text or list of texts to predict named entities.
   - For JSON Lines format, the text should be a string.
   - For other formats, the text can be a list of texts or a single text document.
- **labels**: 
  - Domain-specific labels: Provide a string specifying the domain from the table below.
  - Custom labels: Provide a list of labels or a single label as a string.
  - If no value is provided, the default domain will be set to clinical.
- **threshold**: Threshold for predictions (default is 0.5).


Domain-specific labels

| Domain         | Description                              | Entities                                                                                                                                                     |
|----------------|------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| oncology       | Oncology-Specific Entities                   | Adenopathy, Age, Biomarker, Biomarker_Result, Cancer_Dx, Cancer_Score, Cancer_Surgery, Chemotherapy, Cycle_Count, Cycle_Day, Cycle_Number, Date, Death_Entity, Direction, Dosage, Duration, Frequency, Gender, Grade, Histological_Type, Hormonal_Therapy, Imaging_Test, Immunotherapy, Invasion, Line_Of_Therapy, Metastasis, Oncogene, Pathology_Result, Pathology_Test, Performance_Status, Race_Ethnicity, Radiation_Dose, Radiotherapy, Relative_Date, Response_To_Treatment, Route, Site_Bone, Site_Brain, Site_Breast, Site_Liver, Site_Lung, Site_Lymph_Node, Site_Other_Body_Part, Smoking_Status, Staging, Targeted_Therapy, Tumor_Finding, Tumor_Size, Unspecific_Therapy |
| radiology      | Radiology-related terms                  | BodyPart, Direction, Disease_Syndrome_Disorder, ImagingFindings, ImagingTest, Imaging_Technique, ManualFix, Measurements, Medical_Device, OtherFindings, Procedure, Symptom, Test, Test_Result, Units                                                                                       |
| sdoh           | Social determinants of health-related terms | Access_To_Care, Age, Alcohol, Childhood_Event, Communicable_Disease, Community_Safety, Diet, Disability, Eating_Disorder, Education, Employment, Environmental_Condition, Exercise, Family_Member, Financial_Status, Food_Insecurity, Gender, Geographic_Entity, Healthcare_Institution, Housing, Hyperlipidemia, Hypertension, Income, Insurance_Status, Language, Legal_Issues, Marital_Status, Mental_Health, Obesity, Other_Disease, Other_SDoH_Keywords, Population_Group, Quality_Of_Life, Race_Ethnicity, Sexual_Activity, Sexual_Orientation, Smoking, Social_Exclusion, Social_Support, Spiritual_Beliefs, Substance_Duration, Substance_Frequency, Substance_Quantity, Substance_Use, Transportation, Violence_Or_Abuse |
| nihss          | National Institutes of Health Stroke Scale (NIHSS) | 10_Dysarthria, 11_ExtinctionInattention, 1a_LOC, 1b_LOCQuestions, 1c_LOCCommands, 2_BestGaze, 3_Visual, 4_FacialPalsy, 5_Motor, 5a_LeftArm, 5b_RightArm, 6_Motor, 6a_LeftLeg, 6b_RightLeg, 7_LimbAtaxia, 8_Sensory, 9_BestLanguage, Measurement, NIHSS                                                                                                  |
| ade            | Adverse Drug Events (ADE)                | ADE, DRUG                                                                                                                                                   |
| clinical            | Clinical Entities                 | Admission_Discharge, Age, Alcohol, Allergen, BMI, Birth_Entity, Blood_Pressure, Cerebrovascular_Disease, Clinical_Dept, Communicable_Disease, Date, Death_Entity, Diabetes, Diet, Direction, Disease_Syndrome_Disorder, Dosage, Drug_BrandName, Drug_Ingredient, Duration, EKG_Findings, Employment, External_body_part_or_region, Family_History_Header, Fetus_NewBorn, Form, Frequency, Gender, HDL, Heart_Disease, Height, Hyperlipidemia, Hypertension, ImagingFindings, Imaging_Technique, Injury_or_Poisoning, Internal_organ_or_component, Kidney_Disease, LDL, Labour_Delivery, Medical_Device, Medical_History_Header, Modifier, O2_Saturation, Obesity, Oncological, Overweight, Oxygen_Therapy, Pregnancy, Procedure, Psychological_Condition, Pulse, Race_Ethnicity, Relationship_Status, RelativeDate, RelativeTime, Respiration, Route, Section_Header, Sexually_Active_or_Sexual_Orientation, Smoking, Social_History_Header, Strength, Substance, Substance_Quantity, Symptom, Temperature, Test, Test_Result, Time, Total_Cholesterol, Treatment, Triglycerides, VS_Finding, Vaccine, Vaccine_Name, Vital_Signs_Header, Weight |
| posology       | Drug Information related terms                   | DOSAGE, DRUG, DURATION, FORM, FREQUENCY, ROUTE, STRENGTH                                                                                                    |
| clinical_events       | Clinical events                           | PROBLEM, TEST, TREATMENT                                                                                                                                    |
| diseases       | Disease-related terms                    | Disease                                                                                                                                                     |
| chexpert       | Anatomical and Observation Entities in Chest Radiology Reports (CheXpert)                   | ANAT, OBS                                                                                                                                                   |
| risk_factors   | Risk factors-related terms               | CAD, DIABETES, FAMILY_HIST, HYPERLIPIDEMIA, HYPERTENSION, MEDICATION, OBESE, PHI, SMOKER                                                                   |
| bionlp         | Biology and genetics terms                     | Amino_acid, Anatomical_system, Cancer, Cell, Cellular_component, Developing_anatomical_structure, Gene_or_gene_product, Immaterial_anatomical_entity, Multi-tissue_structure, Organ, Organism, Organism_subdivision, Organism_substance, Pathological_formation, Simple_chemical, Tissue |
| anatomy        | Anatomy-related terms                    | Anatomical_system, Cell, Cellular_component, Developing_anatomical_structure, Immaterial_anatomical_entity, Multi-tissue_structure, Organ, Organism_subdivision, Organism_substance, Pathological_formation, Tissue                    |
| living_species | Living species-related terms             | HUMAN, SPECIES                                                                                                                                              |
| pathogen       | Pathogen, Medical Condition and Medicine related terms                   | MedicalCondition, Medicine, Pathogen                                                                                                                       |
> If you want to use domain-specific labels, provide the corresponding domain name from the table above in the `labels` field.
