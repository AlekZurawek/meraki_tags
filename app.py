import csv
import requests

# Constants
API_KEY = 'insert api key here'
ORGANIZATION_ID = 'insert org id here'
BASE_URL = 'https://api.meraki.com/api/v1'
NETWORKS_ENDPOINT = f'/organizations/{ORGANIZATION_ID}/networks'
CSV_FILE_PATH = 'networks.csv'
CSV_OUTPUT_FILE_PATH = 'network_with_ids.csv'

# Set up headers for HTTP request
headers = {
    'X-Cisco-Meraki-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

def get_networks():
    # Make the API call to get networks
    response = requests.get(BASE_URL + NETWORKS_ENDPOINT, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f'Failed to get networks: {response.text}')

def append_network_ids_to_csv(networks):
    # Read the existing CSV file
    with open(CSV_FILE_PATH, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        fieldnames = reader.fieldnames + ['networkId']  # Add the new column

    # Create a dictionary to map network names to network IDs
    network_name_to_id = {network['name']: network['id'] for network in networks}

    # Write the new CSV file with the networkId column
    with open(CSV_OUTPUT_FILE_PATH, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            # Find the network ID using the site name
            network_id = network_name_to_id.get(row['Site Name'])
            row['networkId'] = network_id if network_id else 'Not Found'
            writer.writerow(row)

def update_network_tags():
    with open(CSV_OUTPUT_FILE_PATH, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            network_id = row['networkId']
            if network_id and network_id != 'Not Found':
                tags = [row.get('Tag 1'), row.get('Tag 2'), row.get('Tag 3')]
                tags = [tag for tag in tags if tag]  # Remove empty tags
                update_payload = {
                    'tags': tags
                }
                # Make the API call to update the network tags
                response = requests.put(f"{BASE_URL}/networks/{network_id}", headers=headers, json=update_payload)
                if response.status_code == 200:
                    print(f'Successfully updated tags for network {network_id}')
                else:
                    print(f'Failed to update tags for network {network_id}: {response.text}')

def main():
    try:
        networks = get_networks()
        append_network_ids_to_csv(networks)
        update_network_tags()
        print('Network update process completed successfully.')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
