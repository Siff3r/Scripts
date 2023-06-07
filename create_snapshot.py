import pytz
import re
import requests
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

username = '[os-username]'
password = '[os-password]'

def send_email(subject, body, to, gmail_user, gmail_pwd):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = gmail_user
    msg['To'] = to

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_pwd)
        server.send_message(msg)
        server.close()
        print('Email sent!')
    except Exception as e:
        print('Failed to send email:', e)

def create_snapshot(index_name, snapshot_name, auth, verify=False):
    """Creates a snapshot for the given index"""
    url = f"https://opensearch01:9200/_snapshot/my-fs-repository/{snapshot_name}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "indices": index_name,
        "ignore_unavailable": True,
        "include_global_state": False
    }
    response = requests.put(url, auth=auth, headers=headers, json=payload, verify=False)
    print(response.text)
    if response.status_code != 200:
        print(f"Failed to create snapshot for {index_name}. Status code: {response.status_code}")
        send_email('Snapshot creation failed', f'Failed to create snapshot for {index_name}. Status code: {response.status_code}', '[recipient-email]', '[sender-email]', '[sender-password]')
        return False
    return True

def get_indices():
    # Replace with the actual username and password
    username = 'os-username'
    password = 'os-password'

    # URL of your Elasticsearch instance
    url = 'https://opensearch01:9200/_cat/indices?v=true&pretty'

    # Make the GET request to Elasticsearch
    response = requests.get(url, auth=(username, password), verify=False)
    # Check that the request was successful
    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code}")
        return

    # Split the response into lines
    lines = response.text.split("\n")

    # Initialize an empty dictionary to store the indices and their creation date
    indices = []

    # Loop over each line
    for line in lines:
        # Split the line into words
        words = line.split()

        # If the line has words and the first word is "green", it's an index
        if words and words[0] == 'green':
            # The index name is the third word
            index = words[2]

            # Extract the base name and the rotation number using a regex
            match = re.match(r"(.*?)_(\d+)", index)

            # If the index name matches the pattern
            if match:
                base_name, rotation_number = match.groups()

                if base_name == 'firewall':
                    # Get the creation date of the index
                    response = requests.get(f"https://opensearch01:9200/{index}/_settings", auth=(username, password), verify=False)
                    creation_date = response.json()[index]['settings']['index']['creation_date']

                    # Convert the creation date to a datetime object
                    creation_date = datetime.fromtimestamp(int(creation_date) / 1000.0)

                    # Convert the datetime object to the desired timezone
                    creation_date = pytz.utc.localize(creation_date).astimezone(pytz.timezone('US/Eastern'))

                    # Format the datetime object as a string
                    creation_date_formatted = creation_date.strftime("%Y-%m-%d_%I%M%p").lower()

                    # Add the index to the list as a tuple of base name, rotation number (as an integer), and full index name
                    indices.append((base_name, int(rotation_number), creation_date_formatted, index))

    # Sort the list of indices
    # This will sort by base name first, then rotation number
    indices.sort(key=lambda x: x[1])

    # Return the sorted list of indices
    return indices

indices = get_indices()

# Keep the most recent 9 indices
indices_to_keep = indices[-9:]

# Create a snapshot for the older indices
for base_name, rotation_number, creation_date, index in indices:
    if (base_name, rotation_number, creation_date, index) not in indices_to_keep:
        if create_snapshot(index, creation_date, (username, password)):
            print(f"Created snapshot for {base_name}_{rotation_number}: {creation_date}")
            send_email('[OpenSearch] Snapshot created successfully!', f'Snapshot created for {base_name}_{rotation_number}: {creation_date}.', '[recipient-email]', '[sender-email]', '[sender-password]')
