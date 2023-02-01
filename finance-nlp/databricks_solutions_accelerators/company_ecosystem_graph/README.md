<img src=https://d1r5llqwmkrl74.cloudfront.net/notebooks/fsi/fs-lakehouse-logo-transparent.png width="600px">

[![POC](https://img.shields.io/badge/POC-10_days-green?style=for-the-badge)](https://databricks.com/try-databricks)

# Financial Solution Accelerator: Drawing a Company Ecosystem Graph
This accelerator will help you process Financial Annual Reports (10K filings) or even Wikipedia data about companies, using John Snow Labs Finance NLP **Named Entity Recognition, Relation Extraction and Assertion Status**, to extract the following information about companies:
- Information about the Company itself (`Trading Symbol`, `State`, `Address`, Contact Information) and other names the Company is known by (`alias`, `former name`).
- People (usually management and C-level) working in that company and their past experiences, including roles and companies
- `Acquisitions` events, including the acquisition dates. `Subsidiaries` mentioned.
- Other Companies mentioned in the report as `competitors`: we will also run a "Competitor check", to understand if another company is just in the ecosystem / supply chain of the company or it is really a competitor
- Temporality (`past`, `present`, `future`) and Certainty (`possible`) of events described, including `Forward-looking statements`.

Also, John Snow Labs provides with offline modules to check for Edgar database (**Entity Linking** to resolve an organization name to its official name and **Chunk Mappers** to map a normalized name to Edgar Database), which are quarterly updated. We will using them to retrieve the `official name of a company`, `former names`, `dates where names where changed`, etc.

___

- Juan Martinez @ John Snow Labs <juan@johnsnowlabs.com>
- <john.doe@databricks.com>

___


<img src="https://raw.githubusercontent.com/JohnSnowLabs/spark-nlp-workshop/master/tutorials/Certification_Trainings_JSL/Finance/data/solution_accelerator_ecosystem/financial_solution_accelerator.png" alt="John Snow Labs Financial Solution Accelerator" width="800"/>

___

&copy; 2022 Databricks, Inc. All rights reserved. The source in this notebook is provided subject to the Databricks License [https://databricks.com/db-license-source].  All included or referenced third party libraries are subject to the licenses set forth below.

| library                                | description             | license     | source                                              |
|----------------------------------------|-------------------------|-------------|-----------------------------------------------------|
| johnsnowlabs==4.2.3                    | Financial NLP library   | Propietary  | https://www.johnsnowlabs.com/finance-nlp/           |
| networkx==2.5                          | Knowledge Graph creation| [3-clause BSD](https://raw.githubusercontent.com/networkx/networkx/master/LICENSE.txt)|https://networkx.org/|
| decorator==5.0.9                       | Python decorators       | [2-clause BSD](https://github.com/micheles/decorator/blob/master/LICENSE.txt)| https://github.com/micheles/decorator|
| plotly==5.1.0                          | Visualization library   | [MIT](https://github.com/plotly/plotly.py/blob/master/LICENSE.txt) | https://plotly.com/                      |

## Instruction
To run this accelerator, set up JSL Partner Connect [AWS](https://docs.databricks.com/integrations/ml/john-snow-labs.html#connect-to-john-snow-labs-using-partner-connect), [Azure](https://learn.microsoft.com/en-us/azure/databricks/integrations/ml/john-snow-labs#--connect-to-john-snow-labs-using-partner-connect) and navigate to **My Subscriptions** tab. Make sure you have a valid subscription for the workspace you clone this repo into, then **install on cluster** as shown in the screenshot below, with the default options. You will receive an email from JSL when the installation completes.

<br>
<img src="https://raw.githubusercontent.com/databricks-industry-solutions/oncology/main/images/JSL_partner_connect_install.png" width=65%>

Once the JSL installation completes successfully, clone this repo into a Databricks workspace. Attach the `RUNME` notebook to any cluster and execute the notebook via `Run-All`. A multi-step-job describing the accelerator pipeline will be created, and the link will be provided. Execute the multi-step-job to see how the pipeline runs.