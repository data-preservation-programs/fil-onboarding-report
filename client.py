import requests


api_url = "https://api.datacapstats.io/api/getVerifiedClients?limit=none"
    

response = None
response = requests.get(api_url)
data = response.json()
data = data['data']
# except requests.exceptions.Timeout:
#     print("API timeout")
# except requests.exceptions.RequestException as e:
#     print("An error occurred during the API request:", e)

result = {}

print("data",data)

#not working fully
# def get_client_name_by_client_id(client_id):
#     if client_id in result:
#         return result[client_id]

#     for entry in data:
#         addressId = entry.get('addressId')
#         client_name = entry.get('name','test')  # use addressId as default if name is empty
#         if not client_name:
#                 return client_id
        
#         if addressId:
#             result[addressId] = client_name
            
#             if addressId == client_id:
#                 return result[client_id]  # return the result from dictionary, which might be addressId
           
#     return client_id




def get_client_name_by_client_id(client_id):
    if client_id in result:
        return result[client_id]
    
    if response.status_code == 200:
#         data = response.json()
#         data = data['data']
        
        for entry in data:
            addressId = entry.get('addressId')
            client_name = entry.get('name')

            
            if addressId not in result:
                result[addressId] = client_name
                print(client_name, "is the client name.")
         
                    
                return client_name

        # If the client_id is not found in the data
        return client_id
    
    else:
        print("Error: Failed to get client name from the API. Status code:", response.status_code)
        return client_id

# if response.status_code == 200:
#     data = response.json()
#     data = data['data']
#     for entry in data:
#         addressId = entry.get('addressId')
#         client_name = entry.get('name')
#         if addressId and client_name:
#             result[addressId] = client_name
# else:
#     print("Error: Failed to get client name from the API. Status code:", response.status_code)


# def get_client_name_by_client_id(client_id):
#     print('the client_id thats getting passed', client_id)
#     return result.get(client_id, client_id)






# Function to get client name by addressId and return the client name
# def get_client_name_by_client_id(client_id):
#     if client_id in result:
#         return result[client_id]
    
#     if response.status_code == 200:
#         data = response.json()
#         data = data['data']
        
#         for entry in data:
#             addressId = entry.get('addressId')
#             client_name = entry.get('name')

#             if addressId and client_name:
#                 if addressId not in result:
#                     result[addressId] = client_name
#                     print(client_name, "is the client name.")
         
#                     if addressId == client_id:
#                         return client_name

#         # If the client_id is not found in the data
#         return client_id
    
#     else:
#         print("Error: Failed to get client name from the API. Status code:", response.status_code)
#         return client_id
# def get_client_name_by_client_id(client_id):
#     if response.status_code==200:
#         data = response.json()
#         data =data['data']
      
#         for entry in data: 
#             addressId = entry.get('addressId') 
#             client_name= entry.get('name')

#             if addressId and client_name:
#                 if client_name not in client_id_to_name:
#                     print(client_name,"this is client name ")
#                     return client_name
                    

#         if client_id in client_id_to_name:
#             return client_id
#         else:
#             return client_id
#     else:
#         print("Error, failed to get client name from the API:", response.status_code)
#         return client_id