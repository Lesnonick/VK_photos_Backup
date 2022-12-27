import requests
import settings
import logging
import datetime
from pprint import pprint


def Unixdate_to_date(Unixtime):
    date = datetime.datetime.fromtimestamp(Unixtime)
    return date.strftime('%Y-%m-%d_%H.%M.%S')


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
        }
        res = requests.get(URL, params=params).json()
        items = res['response']['items']
        url_base = {}
        for item in items:
            likes = item['likes']['count']
            date = Unixdate_to_date(item['date'])
            sizes = sorted(item['sizes'], key=self.sort_size)
            url_base[sizes[-1]['url']] = likes, date
        return url_base


class YaUploader:
    base_host = 'https://cloud-api.yandex.net/'

    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json/',
            'Authorization': self.token
        }

    def upload_from_internet(self, url, yandex_path):
        uri = 'v1/disk/resources/upload/'
        request_url = self.base_host + uri
        params = {
            'url': url,
            'path': yandex_path
        }
        response = requests.post(request_url, params=params, headers=self.get_headers())

    def new_folder(self, yandex_path, folder_name):
        uri = 'v1/disk/resources/'
        request_url = self.base_host + uri
        folder_path = yandex_path + folder_name
        params = {
            'path': folder_path
        }
        requests.put(request_url, params=params, headers=self.get_headers())
        return folder_path

    def rename_file(self, yandex_path, init_name, name):
        uri = 'v1/disk/resources/move/'
        request_url = self.base_host + uri
        file_path = yandex_path + '/' + init_name
        new_file_path = yandex_path + '/' + name
        params = {
            'from': file_path,
            'path': new_file_path
        }
        requests.post(request_url, params=params, headers=self.get_headers())


download_logger = logging.getLogger(__name__)
download_logger.setLevel(logging.INFO)
download_handler = logging.FileHandler(f"{__name__}.log", mode = "w")
download_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
download_handler.setFormatter(download_formatter)
download_logger.addHandler(download_handler)

if __name__ == '__main__':
    vk = VkDownload(settings.version, settings.vk_token, settings.id)
    url_base = vk.get_VK_profile_photos()
    ya = YaUploader(settings.ya_TOKEN)
    folder_path = ya.new_folder('', '/id' + str(settings.id) + '_VK_backup')
    # ya.rename_file('', '1.jpg', '2.jpg')
    likes_number = []
    for key, value in url_base.items():
        likes, data = value[0], value[1]
        if likes in likes_number:
            ya.upload_from_internet(key, f'{folder_path}/{likes}_{data}.jpg')
            ya.rename_file(folder_path, f'{likes}.jpg', f'{likes}_{698}.jpg')
        else:
            ya.upload_from_internet(key, f'{folder_path}/{likes}.jpg')
            likes_number.append(likes)
        download_logger.info(f"The image was moved to the Ya.Disk folder by the link: {key}")