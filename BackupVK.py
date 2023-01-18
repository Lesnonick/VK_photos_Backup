import settings
import yandexuploader
import vkphoto
from logger import upload_logger

if __name__ == '__main__':
    vk = vkphoto.VkDownload(settings.vk_token)
    ya = yandexuploader.YaUploader(settings.ya_TOKEN)
    try:
        url_base = vk.get_vk_profile_photos(settings.vk_id)
        ya.upload_from_internet(url_base)
    except Exception as e:
        upload_logger.error(e)
        print('В ходе работы программы возникла ошибка!')



