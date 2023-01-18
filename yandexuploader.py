import requests
import json
from logger import upload_logger
from tqdm import tqdm
from settings import vk_id

counter = 0


class YaUploader:
    base_host = 'https://cloud-api.yandex.net/'

    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json/',
            'Authorization': self.token
        }

    def _upload_photo(self, url, yandex_path):
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
                status = self._upload_photo(url, yandex_path)
        return status

    def upload_from_internet(self, url_base):
        if url_base:
            upload_logger.info("All links was received")
            yandex_path = self.new_folder('disk:', vk_id)
            if yandex_path:
                to_json = []
                for link, photo_properties in tqdm(url_base.items(), ncols=100, colour='blue',
                                                   bar_format='Загрузка: {l_bar}{bar} Осталось примерно: {remaining}'):
                    filename = self.filename(photo_properties)
                    filepath = self.filepath(yandex_path, filename)
                    size = photo_properties[2]
                    status = self._upload_photo(link, filepath)
                    upload_logger.info(f"{link} status: {status}")
                    to_json.append({'filename': filename, 'link': link, 'size': size})
                with open('files_info.json', 'w') as f:
                    f.write(json.dumps(to_json))
            else:
                print('Произошла ошибка при работе с API Яндекс.Диска. Подробнее в файле Upload_logger.log')
        else:
            print('Произошла ошибка при работе с API VK. Подробнее в файле Upload_logger.log')

    def new_folder(self, yandex_path, folder_name):
        global counter
        uri = 'v1/disk/resources/'
        request_url = self.base_host + uri
        folder_path = f'{yandex_path}/id_{folder_name}_VK_backup' if counter < 1 \
            else f'{yandex_path}/id_{folder_name}_VK_backup({counter})'
        params = {
            'path': folder_path
        }
        response = requests.put(request_url, params=params, headers=self.get_headers()).json()
        if 'error' in response.keys():
            if response['error'] == 'DiskPathPointsToExistentDirectoryError':
                counter += 1
                folder_path = self.new_folder(yandex_path, folder_name)
            else:
                upload_logger.error('Ya.disk: ' + response['error'])
                return False
        return folder_path

    #
    def get_status(self, request_url):
        params = {}
        response = requests.get(request_url, params=params, headers=self.get_headers())
        return response.json()['status']

    def filepath(self, path, name):
        return f'{path}/{name}'

    def filename(self, photo_properties):
        return f'{photo_properties[0]}_{photo_properties[1]}.jpg'
