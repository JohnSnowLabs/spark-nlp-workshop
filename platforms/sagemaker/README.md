## Instructions for running Spark-NLP Healthcare in SageMaker
+ Access AWS Sagemaker in AWS.
+ Go to Notebook -> Notebook Instances

+ Create a new Notebook Instance

![image](https://user-images.githubusercontent.com/36634572/170064724-eaae2235-6d75-41cd-a0e8-277a854172c7.png)

+ This is the configuration we have used, although most of the interesting models will require a `ml.t3.xlarge` instance or more. Reserve at least 50GB of memory.

![image](https://user-images.githubusercontent.com/36634572/170065661-b39825e2-2efc-4850-a452-5f61b72000b9.png)

+ Once created, open JupyterLab.

![image](https://user-images.githubusercontent.com/36634572/170065331-0d35782d-5f89-42d1-a789-c6c6e82b83c3.png)

+ Use Conda Python 3 kernel.

![image](https://user-images.githubusercontent.com/36634572/170065757-6508dbac-adfc-4998-a7e5-63dc265f55a9.png)

+ Upload your JSON credentials file to the root '/' folder. Name it `spark_nlp_for_healthcare.json`.

![image](https://user-images.githubusercontent.com/36634572/170066019-bb58ac1e-bf2e-42c3-9a92-f6ae16e33fd7.png)

+ Upload `NLP_SageMaker_Setup.ipynb` to the root '/', all along with the license, and follow the steps there.

![image](https://user-images.githubusercontent.com/36634572/170067085-eedc1176-3d28-4dd2-ac71-402ac2b291ce.png)

+ Execute the notebook, line  by line. The first line, `Set Environment Variables` will set your license as environment vars. You will see an output similar to this one (instead of XXXX, make sure the data from your license is shown. And the versions will be different as well, depending on the license file you have uploaded).

![image](https://user-images.githubusercontent.com/36634572/170069419-a574f743-4681-482c-888c-e087511a9319.png)

+ When you get to `Download Packages`, you will see a warning at the end. Sagemaker version of PySpark is old (2.4.0). You can check if AWS has released a new version. If not, you can continue ignoring the warning. The code works even with the old Sagemaker version of Pyspark.

![image](https://user-images.githubusercontent.com/36634572/170068841-91b6131d-2879-4beb-9a1c-21b3563f60bf.png)

+ Execute the rest of the notebook. You will see the following results:

![image](https://user-images.githubusercontent.com/36634572/170070181-aeb78471-a402-4511-838f-5cc719913db0.png)

### Known Issues
+ In some aws instances the localhost is not properly resolved. Check, `cat /etc/hosts`. You should see an entry like this,
```
127.0.0.1	name_of_host
```
If there's not such an entry, create one, and replace name_of_host, with the value returned by the `hostname` command.

+ Make sure you are using a `ml.t3.xlarge` and at least 50GB of memory.

### Setting up GPU
For setting up the GPU, you will need to upgrade the CUDA driver to vesion 11(that's because of TF 2.x).
You can follow the instructions in [this blog post](https://arinzeakutekwe.medium.com/how-to-configure-nvidia-gpu-to-work-with-tensorflow-2-on-aws-sagemaker-1be98b9db464).

