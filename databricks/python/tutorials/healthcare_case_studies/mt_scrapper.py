import requests
from bs4 import BeautifulSoup
import os
import re

def get_mt_samples(medical_speciality="", path = ".", n = None):

    """
    Download Transcribed Medical Transcription Sample Reports and Examples from
    'www.mtsamples.com'. 

    ## Parameters

    Medical_Speciality: str
      One of the following specialities:
      'Allergy_Immunology'
      'Autopsy'
      'Bariatrics'
      'Cardiovascular_Pulmonary'
      'Chiropractic'
      'Consult_History_and_Phy.'
      'Cosmetic_Plastic_Surgery'
      'Dentistry'
      'Dermatology'
      'Diets_and_Nutritions'
      'Discharge_Summary'
      'Emergency_Room_Reports'
      'Endocrinology'
      'ENT_Otolaryngology'
      'Gastroenterology'
      'General_Medicine'
      'Hematology_Oncology'
      'Hospice_Palliative_Care'
      'IME'
      'Lab_Medicine_Pathology'
      'Letters'
      'Nephrology'
      'Neurology'
      'Neurosurgery'
      'Obstetrics_Gynecology'
      'Office_Notes'
      'Ophthalmology'
      'Orthopedic'
      'Pain_Management'
      'Pediatrics_Neonatal'
      'Physical_Medicine_Rehab'
      'Podiatry'
      'Psychiatry_Psychology'
      'Radiology'
      'Rheumatology'
      'Sleep_Medicine'
      'SOAP_Chart_Progress_Notes'
      'Speech_Language'
      'Surgery'
      'Urology'
        
    path = str
      Path to save samples.
    
    n = int
      Number of samples to be scrapped.
    
    """
    
    URL = "https://mtsamples.com/site/pages/sitemap.asp"
    page = requests.get(URL)
    mt_soup = BeautifulSoup(page.text, 'html.parser')
    sample_types_map = {}
    type_samples = {}
    for link in mt_soup.find_all('a', href=True):
        if link['href'][:23]=="/site/pages/sample.asp?":
            s = link['href']
            sample_type = re.search(r'type=(.*?)&sample', s).group(1)
            sample_number = re.search(r'sample=(.*?)$', s).group(1)
            sample_clean = re.sub(r" / | - | ", "_", sample_type).split("-")[1]
            if sample_clean not in sample_types_map.keys():
                sample_types_map[sample_clean] = {}
                sample_types_map[sample_clean]['type'] = re.sub(" ", "%20", sample_type)
                sample_types_map[sample_clean]['samples'] = []
            sample_types_map[sample_clean]['samples'].append(re.sub(" ", "%20", sample_number))
    
    download_path = path + f"/{medical_speciality}"  
    
    try:
        os.makedirs(download_path)
    except:
        None
    
    for no, sample_url in enumerate(sample_types_map[medical_speciality]['samples'][:n]):
        url = f"https://mtsamples.com/site/pages/sample.asp?type={sample_types_map[medical_speciality]['type']}&sample={sample_url}"
        #print(url)
        
        page = requests.get(url)
        mt_soup_speciality = BeautifulSoup(page.text, 'html.parser')

        mt_hilightBold_text = mt_soup_speciality.find(class_='hilightBold').text.replace('(adsbygoogle = window.adsbygoogle || []).push({});', ' ')
        unwanted_parts = [mt_soup_speciality.find_all(class_='row my-2')[1].text,
                          mt_soup_speciality.find(class_='alert alert-info my-4').text,
                          mt_soup_speciality.find(class_='mt-5 mb-2').text]

        for t in unwanted_parts:
            mt_hilightBold_text = mt_hilightBold_text.replace(t, '')
        mt_hilightBold_text = re.sub("\n+\s*", "\n", mt_hilightBold_text)
        with open(f'{download_path}/{medical_speciality}_{no:02}.txt', 'w', encoding='UTF8') as f:
            f.write(mt_hilightBold_text)
        
    print(f"{no + 1} samples from {medical_speciality} is downloaded to folder : '{download_path}'")