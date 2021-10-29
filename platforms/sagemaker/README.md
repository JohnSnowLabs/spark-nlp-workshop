## Instructions for running Spark-NLP Healthcare in SageMaker
+ Open JupyterLab.
+ Use Conda Python 3 kernel.
+ Upload your JSON credentials file to the root '/' folder.
+ Upload `NLP_SageMaker_Setup.ipynb` to the root, and follow the steps there.
+ Most of the interesting models will require a ml.t3.xlarge instance or more. 

### Known Issues
In some aws instances the localhost is not properly resolved. Check, `cat /etc/hosts`. You should see an entry like this,
```
127.0.0.1	name_of_host
```
If there's not such an entry, create one, and replace name_of_host, with the value returned by the `hostname` command.

