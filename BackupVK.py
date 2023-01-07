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
    def __init__(self, version, token, vk_id):
        self.version = version
        self.token = token
        self.vk_id = vk_id

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

    def get_vk_profile_photos(self, photos_num):
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'user_id': self.vk_id,
            'access_token': self.token,
            'v': self.version,
            'album_id': 'profile',
            'extended': '1',
            'count': photos_num,
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
                date = Unixdate_to_date(item['date'])
                sizes = sorted(item['sizes'], key=self.sort_size)
                url_base[sizes[-1]['url']] = likes, date, sizes[-1]['type']
            return url_base

    def filename(self, photo_properties):
        return f'{photo_properties[0]}_{photo_properties[1]}.jpg'


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
        folder_path = f'{yandex_path}/id_{folder_name}_VK_backup'
        params = {
            'path': folder_path
        }
        response = requests.put(request_url, params=params, headers=self.get_headers()).json()
        if 'error' in response.keys():
            upload_logger.error('Ya.disk: ' + response['message'])
            return False
        else:
            return folder_path

    def get_status(self, request_url):
        params = {}
        response = requests.get(request_url, params=params, headers=self.get_headers())
        return response.json()['status']

    def filepath(self, path, name):
        return f'{path}/{name}'


upload_logger = logging.getLogger('Upload_logger')
upload_logger.setLevel(logging.INFO)
upload_handler = logging.FileHandler("Upload_logger.log", mode="w")
upload_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
upload_handler.setFormatter(upload_formatter)
upload_logger.addHandler(upload_handler)

if __name__ == '__main__':
    vk = VkDownload(settings.version, settings.vk_token, settings.vk_id)
    url_base = vk.get_vk_profile_photos(settings.photos_num)
    if url_base:
        upload_logger.info("All links was received")
        ya = YaUploader(settings.ya_TOKEN)
        folder_path = ya.new_folder('disk:', settings.vk_id)
        if folder_path:
            to_json = []
            for link, photo_properties in tqdm(url_base.items(), ncols=100, colour='blue',
                                               bar_format='Загрузка: {l_bar}{bar} Осталось примерно: {remaining}'):
                filename = vk.filename(photo_properties)
                filepath = ya.filepath(folder_path, filename)
                size = photo_properties[2]
                status = ya.upload_from_internet(link, filepath)
                upload_logger.info(f"{link} status: {status}")
                to_json.append({'filename': filename, 'link': link, 'size': size})
            with open('files_info.json', 'w') as f:
                f.write(json.dumps(to_json))
        else:
            print('Произошла ошибка при работе с API Яндекс.Диска. Подробнее в файле Upload_logger.log')
    else:
        print('Произошла ошибка при работе с API VK. Подробнее в файле Upload_logger.log')
