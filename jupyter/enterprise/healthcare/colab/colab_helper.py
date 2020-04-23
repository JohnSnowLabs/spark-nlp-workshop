# Fundamental Import and installation of Java
import os, shutil
from google.colab import drive

# Licensed Environment Setup
def setup_license_from_gdrive(mount_path, colab_path, aws_credentials_filename, license_filename):
    aws_dir = "~/.aws"
    if not os.path.exists(aws_dir):
        os.makedirs(aws_dir)
    shutil.copyfile(os.path.join(mount_path, colab_path, aws_credentials_filename),os.path.join(aws_dir, "credentials"))
    with open(os.path.join(mount_path, colab_path, license_filename), "r") as f:
        license = f.readline().replace("\n","")
        os.environ["JSL_NLP_LICENSE"] = license
    with open(os.path.join(mount_path, colab_path, secret_filename), "r") as f:
        secret = f.readline().replace("\n","")
    return secret

