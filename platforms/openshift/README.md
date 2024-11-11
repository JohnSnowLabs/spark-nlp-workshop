# How to Deploy Your Spark NLP Image to OpenShift

## 1. Cloning this Repo & Creating a new Repo

Since building an app for OpenShift from a local directory mandates additional configurations, we will build the app from a GitHub repo to keep it simple. 

This repo does not contain required keys for `license.json` due to security reasons. Hence, cloning this repo and creating a new one is the way to go in this tutorial:

`git clone https://github.com/JohnSnowLabs/spark-nlp-workshop/`

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

On the left side of OpenShift UI, under `Workloads` section, please hit the `Secrets` tab. Then create `Create` > `Source secret`. 

![image](https://user-images.githubusercontent.com/25952802/151937376-803fef43-8f8a-431c-9183-252ef8bc3b0e.png)
![image](https://user-images.githubusercontent.com/25952802/151937483-5a7a2cc9-2e98-49ef-9001-70457ae0c892.png)

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

![image](https://user-images.githubusercontent.com/25952802/151937787-5460800a-bee7-441a-96d0-4ec5d41847d2.png)

Please click on the pod and select `Logs` tab to see command line and outputs. It will result as `Completed` after a while.

![image](https://user-images.githubusercontent.com/25952802/151937914-b6f47f8f-89eb-4ece-9ab6-845c90440e13.png)

When the build is completed, there will be another pod under `Pods` section. Basically, one is for building the app and the other is for serving it.

![image](https://user-images.githubusercontent.com/25952802/152180243-0239d6ca-d05b-46f6-9783-139f4c478f6c.png)

First pod is for build, and second pod is for deployment. Please check the second pod's Logs to see the output. It is working fine if it is giving the following output: 

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

## 4. Expose & Test by Getting Requests

After the successful built and a running container, we can do some testing. Let's start by exposing the app:

`oc expose service/sparknlpopenshift`

Output should be:
```
route.route.openshift.io/sparknlpopenshift exposed
```
Then:
`oc status`
outputs:
```
In project default on server https://api.sparknlp.xxxx.xxxxx.openshiftapps.com:6443

svc/openshift - kubernetes.default.svc.cluster.local
svc/kubernetes - 172.30.0.1:443 -> 6443

http://sparknlpopenshift-xxxxxxxx.apps.sxxxxxx.xxxx.xx.openshiftapps.com to pod port 8515-tcp (svc/sparknlpopenshift)
  deployment/sparknlpopenshift deploys istag/sparknlpopenshift:latest <-
    bc/sparknlpopenshift docker builds https://github.com/xxxxx/sparknlp_openshift.git on istag/miniconda3:4.9.2
    deployment #2 running for 3 minutes - 1 pod
    deployment #1 deployed 16 minutes ago


1 info identified, use 'oc status --suggest' to see details.
```
Please save the link above. Namely: `http://sparknlpopenshift-xxxxxxxx.apps.sxxxxxx.xxxx.xx.openshiftapps.com`

Now it is time to get some requests from that link:
`curl http://sparknlpopenshift-xxxxxxxx.apps.sxxxxxx.xxxx.xx.openshiftapps.com/spark`

gives versions:
```
StatusCode        : 200
StatusDescription : OK
Content           : {"Spark NLP Version":"3.4.0","Spark NLP_JSL Version":"3.4.0","App Name":"file:/tmp/xxxxx/spark-nlp-jsl-3.4.0.jar,file:///root/.ivy2/jars/com.johnsnowlabs.nlp_spa
                    rk...
RawContent        : HTTP/1.1 200 OK
                    Content-Length: 1481
                    Cache-Control: private
                    Content-Type: application/json
                    Date: Wed, 02 Feb 2022 14:17:53 GMT
...
```

Get results from a Pretrained Pipeline:
`curl http://sparknlpopenshift-xxxxxxxx.apps.sxxxxxx.xxxx.xx.openshiftapps.com/test`

returns:
```
StatusCode        : 200
StatusDescription : OK
Content           : {"model_names":["['ner_posology', 'ner_posology_large', 'ner_posology_small',
                    'ner_posology_greedy', 'ner_drugs_large',  'ner_posology_experimental', 'ner_drugs_greedy',
                    'ner_ade_clinical', 'ner_jsl_s...
RawContent        : HTTP/1.1 200 OK
                    Content-Length: 348
                    Cache-Control: private
...
```


## 5. Any doubt?
Write us to support@johnsnowlabs.com
