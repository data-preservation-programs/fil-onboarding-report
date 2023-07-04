def int_client_id(client):
    if client.startswith("f"):
        return client[1:].strip()
    return client.strip()

