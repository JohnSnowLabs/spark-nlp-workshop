# How to Deploy Your Spark NLP Image to OpenShift

## 1. Cloning this Repo & Creating a new Repo

Since building an app for OpenShift from a local directory mandates additional configurations, we will build the app from a GitHub repo to keep it simple. 

This repo does not contain required keys for `license.json` due to security reasons. Hence, cloning this repo and creating a new one is the way to go in this tutorial:

`git clone <this repo>`

`license.json` is empty. You should overwrite it with your own license with both OCR and Healthcare secret and license keys. 
The following fields are required, and should be present in your license(s). if not, please contact JSL team at support@johnsnowlabs.com.
```
{
    "AWS_ACCESS_KEY_ID": "",
    "AWS_SECRET_ACCESS_KEY": "",
    "SPARK_OCR_LICENSE": "",
    "SPARK_OCR_SECRET": "",
    "PUBLIC_VERSION": "",
    "OCR_VERSION": "",
    "SPARK_NLP_LICENSE": "",
    "SECRET": "",
    "JSL_VERSION": ""
}
```

Now you can create your own private repo. For details, please check: https://docs.github.com/en/get-started/quickstart/create-a-repo

From now on, we will be using the repo you just created with required keys inside `license.json`

## 2. Logging in OpenShift and Starting to Build

Log in the cluster using Openshift CLI:

`oc login https://<your URL> --username <your username> --password <your password>`

After seeing `Login Succeeded` output, now we can add credentials of a user who can access to the repo that we just created in Step 1.

On the left side of the webpage, under `Workloads` section, please hit the `Secrets` tab. Then create `Create` > `Source secret`. 
You can either set basic authentication or SSH. I used username and token.

After setting the `Source secret`, we can create a new app in the cluster. Repo URL and the source secret are required:

`oc new-app https://github.com/XXXXX/sparknlp_openshift.git --source-secret=<your secret>`

Output should be similar to this:
```
--> Found container image 52daacd (13 months old) from Docker Hub for "continuumio/miniconda3:4.9.2"

    * An image stream tag will be created as "miniconda3:4.9.2" that will track the source image
    * A Docker build using source code from https://github.com/egenc/sparknlp_openshift.git will be created
      * The resulting image will be pushed to image stream tag "sparknlpopenshift:latest"
      * Every time "miniconda3:4.9.2" changes a new build will be triggered
      * WARNING: this source repository may require credentials.
                 Create a secret with your git credentials and use 'oc set build-secret' to assign it to the build config.

--> Creating resources ...
    imagestream.image.openshift.io "miniconda3" created
    imagestream.image.openshift.io "sparknlpopenshift" created
    buildconfig.build.openshift.io "sparknlpopenshift" created
    deployment.apps "sparknlpopenshift" created
--> Success
    Build scheduled, use 'oc logs -f buildconfig/sparknlpopenshift' to track its progress.
    Run 'oc status' to view your app.
```

## 3. Monitoring process from UI

To see how image building and containerization going, please go to `Workloads` > `Pods` section. Your `build` will be visible. 
Please click on the pod and select `Logs` tab to see command line and outputs. It will result as `Completed` after a while.

When the build is completed, there will be another pod under `Pods` section. Basically, one is for building the app and the other is for serving it.

First pod is build, and second pod is for deployment. Please check the second pod's Logs to see the output. It is working fine if it is giving the following output: 

```
Spark NLP Version : 3.4.0
Spark NLP_JSL Version : 3.4.0
ner_model_finder download started this may take some time.
Approx size to download 148.6 MB
[ | ]ner_model_finder download started this may take some time.
Approximate size to download 148.6 MB
Download done! Loading the resource.
[ / ][ — ][OK!]
----------------------------------------------------------------------------------------------------
{'model_names': ["['ner_posology', 'ner_posology_large', 'ner_posology_small', 'ner_posology_greedy', 'ner_drugs_large',  'ner_posology_experimental', 'ner_drugs_greedy', 'ner_ade_clinical', 'ner_jsl_slim', 'ner_posology_healthcare', 'ner_ade_healthcare', 'jsl_ner_wip_modifier_clinical', 'ner_ade_clinical', 'ner_jsl_greedy', 'ner_risk_factors']"]}
----------------------------------------------------------------------------------------------------
```
**!!!WARNING!!!**
Since the `Dockerfile` does not contain  continuous operations (i.e. model serving), it might throw a `CrashLoopBackOff` error. Please modify the scripts and configs according to your goal.

## 4. Any doubt?
Write us to support@johnsnowlabs.com
