# Ожидаемый результат
Docker-образ позволяющий находить нужные торенты из базы RuTracker без подключения к интернету.

Для пользователя доступен через web-интерфейс.

Должен индексировать [xml-бэкап RuTracker](https://rutracker.org/forum/viewtopic.php?t=5591249) в собственную БД для быстрого доступа.

Путь к архиву с XML-бэкапом должен получать через ENV и отслеживать по хэш-сумме.

Сервис должен соединяться Postgres-базой и переносить в неё данные из xz-архива xml-бэкапа линия за линией с помощью `lmza.open`.
Попытки загрузки изображений в кэш-папку должны запускаться вручную или по расписанию и догружать недостающие изображения.
Поиск должен осуществляться с помощью [meilisearch](https://github.com/meilisearch/meilisearch), синхронизация индексов для поиска с PostgreSQL осуществляется [meilibridge](https://github.com/binary-touch/meilibridge).

Для выбора раздачи перед выводом результатов поиска пользователю сервис должен получать информацию о пирах и сидах раздач с помощью пакета `libtorrent`.

Для удобства предусмотреть прямое добавление раздач на сервер qbittorrent с помощью пакета `qbittorrent-api`.
## Интерфейс
Интерфейс формата SPA, состоит из 3 блоков:
### Шапка
В шапке слева находится логотип со ссылкой на главную страницу.
В центре находится поисковая строка с автодополнением из meilisearch.
Справа находятся кнопка перехода в панель администратора.
### Контент
Контент имеет одно из 4 состояний:
#### Первый заход
При заходе на главную страницу (в адресной строке `/`), пока не был введён первый запрос отображается дашборд с несколькими карточками статистики:
* Дата последнего обновления из бэкапа
* Дата указанная на бэкапе
* Количество раздач
* Количество загруженных изображений для раздач (кольцевая полоса загрузки где максимум это количество раздач)
* Число загрузок на сервере qbittorrent
* Состояние соединения с meilisearch (подключён/ошибка/не настроен)
* Состояние meilibridge (опционально)
* Размер базы данных
#### Поиск
После ввода запроса (в адресной строке `/search?q=...`).
Содержит дополнительные фильтры для поиска.
Ниже содержит таблицу результатов поиска со столбцами:
* Статус раздачи
* Каталог раздачи
* Название раздачи
* Размер раздачи (в человекочитаемых единицах измерения)
* Сиды (при наведение в подсказке дата обновления данных)
* Пиры (при наведение в подсказке дата обновления данных)
* Иконка-кнопка "Magnet-ссылка"
#### Страница раздачи
При заходе на страницу раздачи (в адресной строке `/t/<id>`).
Сверху слева содержит заголовок раздачи.
Ниже строка слева направо
* Размер раздачи
* Число сидов и пиров
* Кнопка "Magnet-ссылка"
* Кнопка "Добавить в qBitTorrent"
Ниже слева оформление, а справа изображение (если загружено).
Следом идёт свёрнутый аккордеон со списком файлов.
В самом низу продублированы данные из строки и остаток доступных данных по раздаче.
#### Панель администратора
При заходе в панель администратора (в адресной строке `/admin`).

### Подвал
При заходе на главную страницу, пока не был введён первый запрос - не отображается.
В иных случаях содержит уменьшенные копии карточек статистики блока [[#Первый заход|Контент > Первый заход]].
## API
### GET /api/stats
Запрос статистики сервера.
### GET /api/search
Поиск раздач по тексту и дополнительным фильтрам.

| Название параметра | Тип  | Значение по умолчанию | Описание                |
| ------------------ | ---- | --------------------- | ----------------------- |
| query\*            | text |                       | Текст запроса           |
| skip               | int  | 0                     | Пропуск результатов     |
| take               | int  | 50                    | Выборка для отображения |
| sorted_by          | text | 'NAME ASC'            | Вариант сортировки      |
| catalog_id         | uuid | null                  | Фильтр по каталогу      |
### GET /api/catalog
Получить список доступных разделов с их ID.

| Название параметра | Тип | Значение по умолчанию | Описание                   |
| ------------------ | --- | --------------------- | -------------------------- |
| depth              | int | 0                     | Глубина вывода подразделов |
### GET /api/torrent/\<id>
Получить информацию о раздаче по ID.

| Название параметра | Тип | Значение по умолчанию | Описание   |
| ------------------ | --- | --------------------- | ---------- |
| id\*               | int |                       | ID раздачи |
### POST /api/torrent/\<id>/to_qbittorrent
Отправить раздачу в qBitTorrent.

| Название параметра | Тип | Значение по умолчанию | Описание   |
| ------------------ | --- | --------------------- | ---------- |
| id\*               | int |                       | ID раздачи |
### GET /api/ls
Получить список файлов в директорий.

| Название параметра | Тип  | Значение по умолчанию | Описание          |
| ------------------ | ---- | --------------------- | ----------------- |
| path\*             | text |                       | Путь к директории |
### POST /api/update
Обновление базы из файла.

| Название параметра | Тип  | Значение по умолчанию | Описание     |
| ------------------ | ---- | --------------------- | ------------ |
| path\*             | text |                       | Путь к файлу |
### GET /api/update
Получить состояние процесса обновления.
# Примерная конфигурация
## Compose
```yml
services:
    yrt-db:
        container_name: yrt-db
        image: postgres
        restart: always
        environment:
            POSTGRES_USER: "${POSTGRES_USER}"
            POSTGRES_PASSWORD: "${POSTGRES_PASSWORD}"
            POSTGRES_DB: "${POSTGRES_DB}"
        networks:
            - yrt

    yrt-meilisearch:
	    container_name: yrt-meilisearch
	    image: getmeili/meilisearch:latest
	    restart: always
		networks:
			- yrt
	    environment:
		    MEILI_MASTER_KEY: "${MEILI_MASTER_KEY}"
		    MEILI_ENV: "${MEILI_ENV:-development}"
	    volumes:
		    - ./meili_data:/meili_data
              
    yrt-meilibridge:
	    depends_on:
		    yrt-db:
			    condition: service_healthy
			yrt-meilisearch:
				condition: service_healthy
	    container_name: yrt-meilibridge
	    image: binarytouch/meilibridge:latest
	    restart: always
        networks:
            - yrt
        environment:
	        POSTGRES_URL: "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@yrt-db:5432/${POSTGRES_DB}"
			MEILISEARCH_URL: "http://yrt-meilisearch:7700"
			MEILISEARCH_API_KEY: "${MEILI_MASTER_KEY}"
		volumes:
			- "${MEILIBRIDGE_CONFIG}:/etc/meilibridge/config.yaml:ro"

    yrt:
        depends_on:
            - yrt-db
        image: goodm2ice/yorutracker
        restart: always
        networks:
            - yrt
            - traefik
        environment:
            DB_HOST: yrt-db
            DB_PORT: 5432
            DB_USER: "${POSTGRES_USER}"
            DB_PASS: "${POSTGRES_PASSWORD}"
            DB_NAME: "${POSTGRES_DB}"
            ARCHIVE_PATH: /backup.xz
            WEBPORT: 3000
            
            MEILI_HOST: yrt-meilisearch
            MEILI_PORT: 7700
		    MEILI_MASTER_KEY: "${MEILI_MASTER_KEY}"
		    
		    QBITTORRENT_HOST: "${QBITTORRENT_HOST}"
		    QBITTORRENT_USER: "${QBITTORRENT_USER}$"
		    QBITTORRENT_PASS: "${QBITTORRENT_PASS}$"
        volumes:
	        - "${ARCHIVE_PATH}:/backup.xz"
	        - ./images:/tracker-images
        labels:
            - traefik.enable=true
            - traefik.docker.network=traefik

            - traefik.http.routers.yrt.rule=Host(`${SUB_DOMAIN}.${DOMAINNAME_1}`)
            - traefik.http.routers.yrt.entrypoints=https
            - traefik.http.routers.yrt.tls=true
            - traefik.http.routers.yrt.tls.certresolver=letsencrypt
            - traefik.http.routers.yrt.service=yrt
            - traefik.http.services.yrt.loadbalancer.server.port=3000

            - traefik.http.routers.yrt-local.rule=Host(`${SUB_DOMAIN}.${DOMAINNAME_2}`)
            - traefik.http.routers.yrt-local.entrypoints=https
            - traefik.http.routers.yrt-local.tls=true
            - traefik.http.routers.yrt-local.tls.certresolver=local-ca
            - traefik.http.routers.yrt-local.service=yrt

            - homepage.group=Общедоступные
            - homepage.name=YoRuTracker
            - homepage.icon=si-utorrent
            - homepage.instance.public.href=https://${SUB_DOMAIN}.${DOMAINNAME_1}
            - homepage.instance.private.href=https://${SUB_DOMAIN}.${DOMAINNAME_2}
            - homepage.description=Локальный сервис поиска торрент-трекеров

networks:
    yrt:
        internal: true
    traefik:
        external: true
```

## Dotenv
```dotenv
# Настройки для отображения в traefik и homepage
SUB_DOMAIN="rutracker"
DOMAINNAME_1="gm2d.ru"
DOMAINNAME_2="lan"
# Настройки postgress
POSTGRES_USER="<username>"
POSTGRES_PASSWORD="<password>"
DB_NAME="yorutracker"
# Настройки meilisearch
MEILI_MASTER_KEY="<very hard master key>"
# Настройки meilibridge
MEILIBRIDGE_CONFIG="./meilibridge/config.yaml"
# Настройки qbittorrent
QBITTORRENT_HOST="http://192.168.0.15:8080"
QBITTORRENT_USER="admin"
QBITTORRENT_PASS="1234"
# Настройки сервиса
ARCHIVE_PATH="/home/server/rutracker-20260425.xml.xz"
```
# Чтение файла из архива по строкам
1. Ищем секцию `<torrents>`
2. Ищем до первого появления `<torrent ...>` или `</torrents>`
3. Если это `</torrents>` - заканчиваем, иначе продолжаем
4. Читаем всё до `</torrent>` в буфер
5. Обрабатываем данные
6. Переходим к шагу 2
```python
import lzma

# path - Путь к xz файлу
# insert_data_f - Функция обрабатывающая данные в базу
def load_archive(path, insert_data_f):
	with lzma.open(path, mode='rt', encoding='utf-8') as f:
		last_line = f.readline()
		while not last_list.starts_with('<torrents'):
			if not last_line:
				raise ValueError('Файл не содержит секций с торрентами!')
			last_line = f.readline()
		while True:
			while not last_line.starts_with '<torrent' and last_line != '</torrents>':
				if not last_line:
					raise ValueError('Файл внезапно закончился!')
				last_line = f.readline()
			if last_line == '</torrents>':
				break
			buffer = [last_line]
			count = 1
			while count > 0:
				if last_line.starts_with('<torrent') and last_line.endswith('>'): # Могут быть вложенные теги torrent, недопустимо ошибочно посчитать закрытие вложенного тега за закрытие секции
					count += 1
				if last_line == '</torrent>':
					count -= 1
				elif last_line == '</torrents>':
					count = 0
				if count <= 0:
					break
				if not last_line:
					raise ValueError('Файл внезапно закончился!')
				last_line = f.readline()
				buffer.append(last_line)
			insert_data_f(buffer) # Обрабатываем данные трекера по одному, чтобы не занимать много оперативной памяти разом
		return 0
```
# Формат бэкапа
```xml
<?xml version="1.0" encoding="UTF-8"?>
<torrents>
	<torrent>
		...
	</torrent>
	...
</torrents>
```
## Формат торрента
```xml
<torrent id="{ID топика}" registred_at="{Дата регистрации в формате Y.[*]m.d H:i:s}" unixts="{Дата регистрации как unix timestamp}" size="{Размер раздачи в байтах}">  
	<title>{Название раздачи}</title>  
	<torrent hash="{Инфохеш}" tracker_id="{Номер трекера}"/>  
	<forum id="{ID форума}">{Название форума с категориями}</forum>  
	<del/>  
	<content>{Оформление раздачи}</content>  
	<dir name="{Имя каталога}">  
		<file size="{Размер в байтах}" name="{Имя файла}"/>  
	</dir>  
	<old hash="{Инфохеш старой версии}" time="{Дата старой версии в текстовом виде}" unixts="{Дата как unix timestamp}">{Заголовок старой версии}</old>  
	<dup p="{Уверенность в процентах}" id="{ID топика возможного дубля}">{Заголовок возможного дубля}</dup>  
</torrent>
```
Тег dup не обязателен и указывается только тогда, когда когда поисковый бот подозревает, что в нескольких торрентах одинаковые данные, байт в байт (имена файлов могут отличаться). Обычно уверенность "p" находится в диапазоне где-то от 7 до 11 (т.е. бот ожидает, что в 9 случаях из 10 он ошибается), но может достигать и 100 (т.е. абсолютной уверенности). Upd: теги dup временно удалены.

Как и в официальной раздаче, трекер указывается не адресом, а номером. Трекер номер 1 - это "http://bt.t-ru.org/ann?magnet". Остальные - это "http://bt{номер}.t-ru.org/ann?magnet", например, "http://bt3.t-ru.org/ann?magnet".

Теги dir могут вкладываться друг в друга. В однофайловых раздачах тег file может находиться прямо в теге torrent, без тега dir.

Тег del означает, что раздача удалена. В будущем у него появится параметр dead="true" или dead="false", в зависимости от того, остались ли пиры.

Теги old перечисляют старые версии той же раздачи.

Теги del, dup, old, dir и file отсутствуют в старой (официальной) базе.
## Формат magnet-ссылки
```
magnet:?xt=urn:btih:{hash}&dn={display_name}&tr={tracker_url}
```
* `hash` - хэш раздачи
* `display_name` - отображаемое имя (опционально)
* `tracker_url` - адрес трекера

# Архитектура БД
## MVP версия
![Схема БД](./db_schema.svg)
