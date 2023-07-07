def int_client_id(client_id):
    if client_id.startswith("f"):
        return client_id[1:].strip()
    return client_id.strip()
