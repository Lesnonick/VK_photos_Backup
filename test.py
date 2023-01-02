import requests
import settings

class YaUploader:
    base_host = 'https://cloud-api.yandex.net/'

    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json/',
            'Authorization': self.token
        }

    def folder_list(self, yandex_path):
        uri = 'v1/disk/resources'
        request_url = self.base_host + uri
        params = {
            'path': yandex_path,
            'fields': '_embedded.items.name',
            'limit': '100000000000'
        }
        response = requests.get(request_url, params=params, headers=self.get_headers())
        names_list = list(response.json()['_embedded']['items'])
        names = []
        for name in names_list:
            names.extend(list(name.values()))
        return names


    def file_delete(self, yandex_path):
        uri = 'v1/disk/resources'
        request_url = self.base_host + uri
        params = {
            'path': yandex_path
        }
        response = requests.delete(request_url, params=params, headers=self.get_headers())


ya = YaUploader(settings.ya_TOKEN)
print(ya.folder_list(''))
