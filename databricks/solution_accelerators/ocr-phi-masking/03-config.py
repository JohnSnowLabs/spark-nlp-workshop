# Databricks notebook source
class SolAccUtil:
  def __init__(self,project_name,base_path=None):
    if base_path!=None:
      self.base_path=base_path
    else:
      user=dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().apply('user')
      self.base_path = f'/home/{user}/hls'
    
    
    self.project_name = project_name.strip().replace(' ','-')
    self.data_path=f'{self.base_path}/{self.project_name}/data'
    self.delta_path=f'{self.base_path}/{self.project_name}/delta'
    
    dbutils.fs.mkdirs(self.base_path)
    dbutils.fs.mkdirs(self.data_path)
    dbutils.fs.mkdirs(self.delta_path)
    
  def load_remote_data(self,url,unpack=False):
    import requests
    fname=url.split('/')[-1]
    r = requests.get(url)
    open(f'/dbfs{self.data_path}/{fname}','wb').write(r.content)
    if unpack:
      import tarfile
    # open file
      file = tarfile.open(f'/dbfs{self.data_path}/{fname}')
      file.extractall(f'/dbfs{self.data_path}')
      file.close()
      
    self.display_data()
    
  def print_paths(self):
    html_str = f"""<p>
    <b>base_path</b> = <i>{self.base_path}</i><br>
    <b>data_path</b> [where your raw data will be stored]= <i>{self.data_path}</i> <br>
    <b>delta_path</b> [where your delta tables will be stored] = <i>{self.delta_path}</i> <br>
    </p>"""
    displayHTML(html_str)
    
  def display_data(self):
    print('*'*100)
    print(f'data available in {self.data_path} are:')
    print('*'*100)
    files=dbutils.fs.ls(f'{self.data_path}')
    if len(files)==0:
      print('no data available, please run load_remote_data(<url for the data>)')
    else:
      display(files)

# COMMAND ----------

# MAGIC %md
# MAGIC You have access to `SolAccUtil` class. By initializing this class, you create paths where you store synthetically generated raw data, root path for your delta tables and download data for testing.