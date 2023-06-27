import requests

# Function to take the addressId and return the client name
def get_client_name(addressId):
    
    api_url="https://api.datacapstats.io/api/getVerifiedClients?limit=none"

    try:
        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            data = data['data']
            
            for entry in data:
                if addressId ==  entry.get('addressId'):
                    if entry.get('name') is not None: 
                        return entry['name']
                    else:
                        return addressId
        else:
            print("Error, failed to get client name from the API: ", response.status_code)
            return addressId
    except requests.exceptions.Timeout:
        print("API timeout")
    except requests.exceptions.RequestException as e:
        print("An error occurred during the API request:", e)