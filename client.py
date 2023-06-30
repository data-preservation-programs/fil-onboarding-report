import requests


api_url = "https://api.datacapstats.io/api/getVerifiedClients?limit=none"
    

response = None
response = requests.get(api_url)
data = response.json()
data = data['data']


result = {}



def get_client_name_by_client_id(client_id):
    if client_id in result:
        return result[client_id]
    
    if response.status_code == 200:
        
        client_names = ""

        for entry in data:
            addressId = entry.get('addressId')
            name = entry.get('name')
            orgName = entry.get('orgName') 

            if addressId == client_id:

                client_names = name
                
                #check if the orgName has a name in case the name is empty
                if name == "":
                    client_names = orgName 
                if name =="" and orgName =="":
                    client_names = client_id
                break
          
                
     
        if client_names != "" :
            result[client_id] = client_names
            return client_names

        # If the client_id is not found in the data
        return client_id
    
    else:
        print("Error: Failed to get client name from the API. Status code:", response.status_code)
        return client_id
