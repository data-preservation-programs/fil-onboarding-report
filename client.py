import requests

class StatsClient:
    api_url = "https://api.datacapstats.io/api/getVerifiedClients?limit=none"

    def __init__(self):
        self.data = None
     
    def result(self):
        result={}
        return result

    def list_data(self):
        if not self.data:
            self.response = None
            response = requests.get(StatsClient.api_url)
            data = response.json()
            data = data['data']
        
        return self.data

    def add_client_name_by_client_id(self, client_id):
        if client_id in self.result:
            return self.result[client_id]

        if self.list_data !=None:
            client_names=""

            for entry in self.list_data():
                addressId = entry.get('addressId')
                name=entry.get('name')
                orgName = entry.get('orgName')

                if addressId==client_id:
                    client_names=name
                    
                    #check for empty values of name and orgName, if one is empty then the other one will get placed
                    if name == "":
                        client_names = orgName 
                    if name =="" and orgName =="":
                        client_names = client_id
                    break                

                if client_names !="":
                    self.result[client_id]=client_names
                    return client_names

        #return client_id if the name or orgName is not found
        else:
            print("Error: Failed to get client name from the API")
            return client_id

# def get_client_name_by_client_id(client_id):
#     if client_id in result:
#         return result[client_id]
    
#     if response.status_code == 200:
        
#         client_names = ""

#         for entry in data:
#             addressId = entry.get('addressId')
#             name = entry.get('name')
#             orgName = entry.get('orgName') 

#             if addressId == client_id:

#                 client_names = name
                
#                 #check if the orgName has a name in case the name is empty
#                 if name == "":
#                     client_names = orgName 
#                 if name =="" and orgName =="":
#                     client_names = client_id
#                 break
          
                
     
#         if client_names != "" :
#             result[client_id] = client_names
#             return client_names

#         # If the client_id is not found in the data
#         return client_id
    
#     else:
#         print("Error: Failed to get client name from the API. Status code:", response.status_code)
#         return client_id
