# Databricks notebook source
project_data_paths = {'omop-cdm-100K':"s3://hls-eng-data-public/data/rwe/all-states-90K/","omop-cdm-10K":"s3://hls-eng-data-public/data/synthea/",'psm':"s3://hls-eng-data-public/data/rwe/dbx-covid-sim/", "onc-lh":"s3://hls-eng-data-public/mt_oc_notes/"}

# COMMAND ----------

import mlflow

class SolAccUtil:
  def __init__(self,project_name,data_path=None,base_path=None):
    user=dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().apply('user')
    project_name = project_name.strip().replace(' ','-')
    self.settings = {}
    
    if base_path!=None:
      base_path=base_path
    else:
      base_path = f'/home/{user}/health-lakehouse'

    if data_path != None:
      data_path=data_path
    else:
      data_path=project_data_paths[project_name]
     
    dbutils.fs.mkdirs(base_path)
    delta_path=f'{base_path}/{project_name}/delta'
    
    experiment_name=f'/Users/{user}/{project_name}'
    if not mlflow.get_experiment_by_name(experiment_name):
      experiment_id = mlflow.create_experiment(experiment_name)
      experiment = mlflow.get_experiment(experiment_id)
    else:
      experiment = mlflow.get_experiment_by_name(experiment_name)
      
    self.settings['base_path']=base_path
    self.settings['delta_path']=delta_path
    self.settings['data_path']=data_path
    self.settings['experiment_name']=experiment.name
    self.settings['experiment_id']=experiment.experiment_id
    self.settings['artifact_location']=experiment.artifact_location
    self.settings['tags']=experiment.tags

    
  def load_remote_data(self,url,unpack=False):
    import requests
    fname=url.split('/')[-1]
    r = requests.get(url)
    print('*'*100)
    print(f'downloading file {fname} to {self.data_path}')
    print('*'*100)
    open(f'/dbfs{self.data_path}/{fname}','wb').write(r.content)
    if unpack:
      print(f'unpacking file {fname} into {self.data_path}')
      import tarfile
    # open file
      file = tarfile.open(f'/dbfs{self.data_path}/{fname}')
      file.extractall(f'/dbfs{self.data_path}')
      file.close()
    
  def print_info(self):
    _html='<p>'
    for key,val in self.settings.items():
      _html+=f'<b>{key}</b> = <i>{val}</i><br>'
    _html+='</p>'
    
    displayHTML(_html)
    
  def display_data(self):
    files=dbutils.fs.ls(f'{self.data_path}')
    if len(files)==0:
      print('no data available, please run load_remote_data(<url for the data>)')
    else:
      print('*'*100)
      print(f'data available in {self.data_path} are:')
      print('*'*100)
      display(files)