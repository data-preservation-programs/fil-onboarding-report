import requests as re
from utils import int_client_id


class StatsClient:
    def __init__(self, api_url="https://api.datacapstats.io"):
        self.api_url = api_url
        self.verified_clients = None
        self.client_id_to_name = {}

    def _get_verified_clients(self, limit=None):
        url = self.api_url + "/api/getVerifiedClients?limit={limit}".format(limit=limit)
        resp = re.get(url)
        if resp.status_code == 200:
            return resp.json()['data']
        return None

    def calculate_client_id_to_name_map(self):
        self.verified_clients = self._get_verified_clients()

        for verified_client in self.verified_clients:
            address_id = verified_client.get('addressId')
            integer_id = int_client_id(address_id)
            name = verified_client.get('name')
            org_name = verified_client.get('orgName')

            self.client_id_to_name[integer_id] = address_id

            if name != "":
                self.client_id_to_name[integer_id] = name

            if org_name != "":
                self.client_id_to_name[integer_id] = org_name

    def get_client_name(self, integer_client_id):
        return self.client_id_to_name[integer_client_id]
