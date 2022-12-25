import requests
import settings
from pprint import pprint
import json

class VkDownload:
    def __init__(self, version, token, id):
        self.version = version
        self.token = token
        self.id = id

    def sort_size(self, sizes):
        if sizes['type'] == 's':
            return 0
        elif sizes['type'] == 'm':
            return 1
        elif sizes['type'] == 'x':
            return 2
        elif sizes['type'] == 'y':
            return 3
        elif sizes['type'] == 'z':
            return 4
        elif sizes['type'] == 'w':
            return 5
        else:
            return -1

    def get_VK_profile_photos(self):
        URL = 'https://api.vk.com/method/photos.get'
        params = {
            'user_id': self.id,
            'access_token': self.token,
            'v': self.version,
            'album_id': 'profile',
            'extended': '1'
            #'count': 59
        }
        res = requests.get(URL, params=params).json()
        items = res['response']['items']
        url_base = []
        for item in items:
            sizes = sorted(item['sizes'], key=self.sort_size)
            url_base.append(sizes[-1]['url'])
        return url_base

if __name__ == '__main__':
    vkD = VkDownload(settings.version, settings.token, settings.id)
    print(vkD.get_VK_profile_photos())