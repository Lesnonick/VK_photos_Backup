# Резервное копирование фотографий из VK

## Описание программы
Данная программа предназначена для резервного копирования 
фотографий из VK в облачные хранилища или в папку на компьютере.
Это поможет сохранить данные в случае утери/кражи аккаунта.
Названием каждой скопированной фотографии является количество
лайков, поставленных пользователями VK под эту фотографию. 
Каждое изображение переносится на диск в макимально-доступном разрешении.

## Состав файлов
- BackupVK.py - основной файл, в котором реализованы функции 
копирования фотографий из VK и переноса их на диск
- settings.py - файл, в котором содержитсясправочная информация
такая как: id пользователя, у которого нужно скопировать фото,
ТОКЕНЫ VK и Яндекса (пустое поле для вводе пользователем), версия API
- test.py - файл для тестирования. На данный момент содержит
2 дополнительный функции для API Яндекса: вывод списка
файлов в папке, а также удаление файла. Функции проверены и
работают.
- Upload_logger.log - файл логгирования
- README.md - файл с информацией о программе

### Версия ALPHA 1.1
Составляется список ссылок фотографий через API VK, 
затем через API Yandex происходит копирование фотографий в новую папаку на
Яндекс.Диске.

#### Плюсы
- Достаточно быстрая работа
- Отсутствие рекурсивных алгоритмов
- Наличие наглядного прогресс-бара


#### Проблемы
- Не проверяется успешность копирования. За счёт этого
некоторые фотографии не попадают в созданную папаку. 
Как итог: потеря информации.
- Количество выгружаемых с VK фотографий ограничено 50 
(дефолтное значение для параметра "count")
- Недостоверное логирование копирования фотографий
- Нет возможности с консоли ввести ТОКЕН с Полигона Я.Диска
- Возможность резервного копирования только фотографий 
из профиля
- Возможность резервного копирования только на Я.Диск
- Нет сохранения информации о каждой фотографиив отдельный файл

### Версия BETA 1.0
Составляется список ссылок фотографий через API VK, 
затем через API Yandex происходит последовательное 
копирование фотографий в новую папаку на
Яндекс.Диске. Новая фотография не переносится на Я.Диск
пока не перенесена старая. Таким образом контроллируется 
процесс переноса каждой фотографии.

#### Плюсы
- Надежность работы
- Работа с большим количествм фотографий профиля (до 1000)
- Логирование процесса переноса фотографий
- Наличие наглядного прогресс-бара

#### Проблемы
- Небыстрая работа за счёт строгой последовательности операций
- Возможность резервного копирования только фотографий 
из профиля
- Возможность резервного копирования только на Я.Диск
- Нет сохранения информации о каждой фотографиив отдельный файл

### Дальнейшее развитие
- Добавление возможности копирования на Google.Drive
и на локальное устройство
- Добавление возможности резервного копирования не
только альбома аватарок, но также и других доступных альбомов
- Добавление сохранения информации по скаченным файлам
в отдельный json файл


