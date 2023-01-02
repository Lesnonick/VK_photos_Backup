import json
import requests
import settings
import logging
import datetime
from tqdm import tqdm


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
            'extended': '1',
            'count': 1000
        }
        res = requests.get(URL, params=params).json()
        items = res['response']['items']
        url_base = {}
        # for item in tqdm(items): ПРОГРЕСС-БАР убран за ненадобностью (50000 ит/се = моментально для пользователя)
        for item in items:
            likes = item['likes']['count']
            date = Unixdate_to_date(item['date'])
            sizes = sorted(item['sizes'], key=self.sort_size)
            url_base[sizes[-1]['url']] = likes, date, sizes[-1]['type']
            # url_base[date] = likes, date Для проверки ERROR в логгинге
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
        operation_id = response.json()['href']
        status = self.get_status(operation_id)
        while status == 'in-progress':
            status = self.get_status(operation_id)
            if status == 'failed':
                status = self.upload_from_internet(url, yandex_path)
        return status

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
        response = requests.post(request_url, params=params, headers=self.get_headers())

    def get_status(self, request_url):
        params = {}
        response = requests.get(request_url, params=params, headers=self.get_headers())
        return response.json()['status']


upload_logger = logging.getLogger('Upload_logger')
upload_logger.setLevel(logging.INFO)
upload_handler = logging.FileHandler("Upload_logger.log", mode="w")
upload_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
upload_handler.setFormatter(upload_formatter)
upload_logger.addHandler(upload_handler)

if __name__ == '__main__':
    vk = VkDownload(settings.version, settings.vk_token, settings.id)
    url_base = vk.get_VK_profile_photos()
    ya = YaUploader(settings.ya_TOKEN)
    upload_logger.info("All links was received")
    folder_path = ya.new_folder('disk:', '/id' + str(settings.id) + '_VK_backup')
    likes_date = {}
    to_json = []
    for link, value in tqdm(url_base.items(), ncols=100, colour='blue',
                            bar_format='Загрузка: {l_bar}{bar}{r_bar} Осталось примерно: {remaining}'):
        likes, date, size = value[0], value[1], value[2]
        short_name = f'{likes}.jpg'
        if likes in likes_date.keys():
            long_name = f'{likes}_{date}.jpg'
            new_name = f'{likes}_{likes_date[likes]}.jpg'
            status = ya.upload_from_internet(link, folder_path + '/' + long_name)
            upload_logger.info(f"{link} status: {status}")
            to_json.append({'filename': long_name, 'link': link, 'size': size})
            for file in to_json:
                if file['filename'] == short_name:
                    ya.rename_file(folder_path, short_name, new_name)
                    file['filename'] = new_name
        else:
            status = ya.upload_from_internet(link, folder_path + '/' + short_name)
            upload_logger.info(f"{link} status: {status}")
            to_json.append({'filename': short_name, 'link': link, 'size': size})
            likes_date[likes] = date
    with open('files_info.json', 'w') as f:
        f.write(json.dumps(to_json))
