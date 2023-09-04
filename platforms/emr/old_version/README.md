### Spark-NLP for Healthcare in AWS EMR

In this page we explain how to setup Spark-NLP + Spark-NLP Healthcare in AWS EMR, using the AWS console. This configuration is already ready-to-use for **EMR Notebooks**.

### Steps
## 1. Software and Steps

You must go to the blue button "Create Cluster" on the UI. By doing that you will get directed to the "Create Cluster - Quick Options" page. Don't use the quick options, click on "**Go to advanced options**" instead. ![image](https://user-images.githubusercontent.com/25952802/156375266-a91577f6-c9db-4592-98c2-8fa05036dca7.png)

Now in Advanced Options, please pick the following selection in the checkboxes,
![image](https://user-images.githubusercontent.com/25952802/156355170-56d1ba27-4751-49d3-b929-197ab167e1d4.png)

Also in the "**Edit Software Settings**" section, enter the following for configurations:

![image](https://user-images.githubusercontent.com/25952802/156357280-510009c6-2f12-44c5-9fe0-bd38e4d86838.png)

```
[{
  "Classification": "spark-env",
  "Configurations": [{
    "Classification": "export",
    "Properties": {
      "PYSPARK_PYTHON": "/usr/bin/python3",
      "AWS_ACCESS_KEY_ID": "XYXYXYXYXYXYXYXYXYXY",
      "AWS_SECRET_ACCESS_KEY": "XYXYXYXYXYXYXYXYXYXY", 
      "SPARK_NLP_LICENSE": "XYXYXYXYXYXYXYXYXYXYXYXYXYXY"
    }
  }]
},
{
  "Classification": "spark-defaults",
    "Properties": {
      "spark.yarn.stagingDir": "hdfs:///tmp",
      "spark.yarn.preserve.staging.files": "true",
      "spark.kryoserializer.buffer.max": "2000M",
      "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
      "spark.driver.maxResultSize": "0",
      "spark.driver.memory": "32G"
    }
}]
```
**__Important__**:
Make sure that you replace all the secret information(marked here as XYXYXYXYXY) by the appropriate values that you received with your license.<br/> 

If you are having issues with the license, please contact JSL team at support@johnsnowlabs.com

## 2. Hardware
Please choose the hardware and networking configuration you prefer, or just pick the defaults.

**Important:** Keep in mind that there should be only one master node if you want to use EMR Notebooks. However, cluster can be scaled with additional slave nodes - which can be modified under `Cluster Nodes and Instances` section.
![image](https://user-images.githubusercontent.com/25952802/156366353-c2326f2f-d903-40f5-87be-92273112e262.png)


Please set EBS Volume to `50 GiB` and move to next step by clicking the "Next" blue button.<br/>
![image](https://user-images.githubusercontent.com/25952802/156357686-820d2c6d-f2c5-47ba-9140-7a60ba11cf6a.png)

## 3. General Cluster Settings
Here is where you name your cluster, and you can change the location of the cluster logs. If the location of the logs is OK for you, take note of the path so you can debug potential problems by using the logs.<br/>

Under **Tags** section, please add a `KEY: VALUE` pair with `for-use-with-amazon-emr-managed-policies` `true`
![image](https://user-images.githubusercontent.com/25952802/156359265-0e4ed417-9c5d-4301-adc6-4736c6cda225.png)

Go to the bottom of the page, and expand the `Bootstrap Actions` tab. We're gonna add an action to execute during bootstrap of the cluster. Select `Custom Action`, then press on `Configure and add`. You need to provide a path to a script on S3. The path needs to be public. Keep this in mind, no secret information can be contained there.<br/>
The script we'll used for this setup is `emr_bootstrap_v2.sh` contained in the same folder this tutorial is located on Github.<br/>

This script will install **Spark-NLP 3.4.0**, and **Spark-NLP Healthcare 3.4.0**. You'll have to edit the script if you need different versions.<br/>
After you entered the route to S3 in which you place the `emr_bootstrap_v2.sh` file, and before clicking "add" in the dialog box, you must pass an additional parameter containing the **SECRET** value you received with your license. Just paste the secret on the "Optional arguments" field in that dialog box.<br/>
![image](https://user-images.githubusercontent.com/25952802/156359956-7bd8ae16-05f3-497d-8a1e-8e869b684503.png)

## 4. Security
After selecting a `EC2 key pair` - to connect the master node with `SSH`, please select default roles and create the cluster.

## 5. Create an EMR Notebook
Please start a notebook server, connect it to the cluster you just created(be patient, it takes a while), and test with the `NLP_EMR_Setup.ipynb` that we provide in this folder.<br/>

In order to use and write files to `hdfs:///` without limitations, we need to grant sudo rights for `livy` user after SSHing to master node.

To connect master node:
```bash
~$ ssh -i <EC2 key pair>.pem hadoop@<host>.ec2
```
Please grant access when logged in via:
```bash
emr-cluster@xxx:~$ sudo usermod -a -G hdfsadmingroup livy
```
## 6. Any Doubt?
Write us to support@johnsnowlabs.com
