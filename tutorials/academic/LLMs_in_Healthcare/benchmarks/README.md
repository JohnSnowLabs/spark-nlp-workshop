# Introduction

This folder contains files and data for generating and evaluating predictions for a selected NLP task using benchmark datasets. Benchmarks are generated using GPT3.5 API and JSL Models.

## Purpose

The purpose of this folder is to provide a streamlined pipeline for generating and evaluating predictions for selected entity types. The folder includes the following files:

- `README.md`: A brief guide on how to use the files and data in this folder.
- `workbench/`: Main folder that contains the modules, nbs and sources for generating and evaluating predictions.
- `data/`: A directory that contains the raw data (with sentences and ground truths).
- `workbench/prompts/`: A directory that contains prompts for the entity extraction task.
- `workbench/processed_data/`: A directory that contains the processed data (saved as CSV and Excel files).
- `workbench/eval_results/`: A directory that contains evaluation results (saved as a JSON file).

## Audience

This folder is intended for data scientists, machine learning engineers, and researchers who are working with natural language processing (NLP), entity recognition and classification tasks in healtcare domain.

## Getting Started

### Installation

1. Clone the repository to your local machine.
2. Install the required Python packages.
3. Add openapi_key as explained below

### Usage

1. Open one of the nbs in workbench for your preferred task.
2. Run the cells in the notebook in sequential order.
3. In the task selection cell, select an entity type for prediction generation.
4. In the evaluation cell, select an entity type for benchmark evaluation.
5. In the root directory of your project, create a file named `config/creds.yaml` if it does not exist.
6. Add the following line of code to the `config/creds.yaml` file:

```yaml
openai_key: "INSERT_YOUR_OPENAI_KEY_HERE"
```
7. Replace the text INSERT_YOUR_OPENAI_KEY_HERE with your own OpenAI key. Make sure to enclose your key in double quotation marks.
8. Save the config/creds.yaml file in the root directory of your project.


## Notes
-  Notebooks assume:
  * That the raw data is stored in a pickle file in the data/ directory.
  * The prompts for the entity extraction and classification tasks are stored in the prompts/ directory.
- The processed data will be saved as a CSV and Excel file in the processed_data/ directory.
- The evaluation results will be saved as a JSON file in the eval_results/ directory.
