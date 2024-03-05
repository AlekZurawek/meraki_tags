import csv
import requests

# Constants
API_KEY = 'insert your api key here'
ORGANIZATION_ID = 'insert your org id here'
BASE_URL = 'https://api.meraki.com/api/v1'
NETWORKS_ENDPOINT = f'/organizations/{ORGANIZATION_ID}/networks'
CSV_FILE_PATH = 'network_with_ids.csv'

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

def update_network_ids_in_csv(networks):
    # Read the existing CSV file with network IDs
    with open(CSV_FILE_PATH, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        fieldnames = reader.fieldnames  # Assume 'networkId' column already exists

    # Create a dictionary to map network names to network IDs
    network_name_to_id = {network['name']: network['id'] for network in networks}

    # Write the updated CSV file with network IDs
    with open(CSV_FILE_PATH, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            # Only update networkId if it's missing or set to 'Not Found'
            if not row.get('networkId') or row['networkId'] == 'Not Found':
                network_id = network_name_to_id.get(row['Site Name'])
                row['networkId'] = network_id if network_id else 'Not Found'
            writer.writerow(row)

def update_network_tags():
    with open(CSV_FILE_PATH, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            network_id = row['networkId']
            if network_id and network_id != 'Not Found':
                tags = [row['Tag 1'], row['Tag 2'], row['Tag 3']]
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
        update_network_ids_in_csv(networks)
        update_network_tags()
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
