import pytz
import re
import requests
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

username = ''
password = ''

def create_snapshot(index_name, snapshot_name, auth, verify=False):
    """Creates a snapshot for the given index"""
    url = f"https://opensearch01:9200/_snapshot/my-fs-repository/{snapshot_name}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "indices": index_name,
        "ignore_unavailable": True,
        "include_global_state": False
    }
    response = requests.put(url, auth=auth, headers=headers, json=payload, verify=verify)
    if response.status_code != 200:
        print(f"Failed to create snapshot for {index_name}. Status code: {response.status_code}")

def get_indices():
    url = 'https://opensearch01:9200/_cat/indices?v=true&pretty'
    response = requests.get(url, auth=(username, password), verify=False)
    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code}")
        return

    lines = response.text.split("\n")
    indices = []

    for line in lines:
        words = line.split()
        if words and words[0] == 'green':
            index = words[2]
            match = re.match(r"(.*?)_(\d+)", index)            
            if match:
                base_name, rotation_number = match.groups()

                if base_name == 'firewall':                    
                    response = requests.get(f"https://opensearch01:9200/{index}/_settings", auth=(username, password), verify=False)
                    creation_date = response.json()[index]['settings']['index']['creation_date']
                    
                    creation_date = datetime.fromtimestamp(int(creation_date) / 1000.0)
                    creation_date = pytz.utc.localize(creation_date).astimezone(pytz.timezone('US/Eastern'))
                    creation_date_formatted = creation_date.strftime("%Y-%m-%d_%I%M%p").lower()
                    
                    indices.append((base_name, int(rotation_number), creation_date_formatted, index))

    indices.sort(key=lambda x: x[1])
    
    return indices

indices = get_indices()
indices_to_keep = indices[-9:]

for base_name, rotation_number, creation_date, index in indices:
    if (base_name, rotation_number, creation_date, index) not in indices_to_keep:
        create_snapshot(index, creation_date, (username, password))
        print(f"Created snapshot for {base_name}_{rotation_number}: {creation_date}")
