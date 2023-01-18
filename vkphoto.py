import requests
import datetime
import settings
from logger import upload_logger


def unixdate_to_date(unixtime):
    date = datetime.datetime.fromtimestamp(unixtime)
    return date.strftime('%Y-%m-%d_%H.%M.%S')


class VkDownload:
    def __init__(self, vk_token):
        self.version = settings.version
        self.token = vk_token

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

    def get_vk_profile_photos(self, vk_id):
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'user_id': vk_id,
            'access_token': self.token,
            'v': self.version,
            'album_id': 'profile',
            'extended': '1',
            'count': settings.photos_num,
            'rev': 1
        }
        response = requests.get(url, params=params).json()
        if 'error' in response.keys():
            upload_logger.error('VK: ' + response['error']['error_msg'])
            return False
        else:
            items = response['response']['items']
            url_base = {}
            for item in items:
                likes = item['likes']['count']
                date = unixdate_to_date(item['date'])
                sizes = sorted(item['sizes'], key=self.sort_size)
                url_base[sizes[-1]['url']] = likes, date, sizes[-1]['type']
            return url_base


