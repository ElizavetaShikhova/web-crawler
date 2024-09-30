Возможные команды:
* запуск краулера: `python main.py crawler-start`. Но перед этим надо обязательно установить URL, с которого краулер 
  начнет обход
* Установка начального URL: `python main.py crawler_set_start_url <URL>`. Замените <URL> на желаемый начальный URL.
* Установка разрешенного домена: `python main.py crawler_set_domain <domain>`. Замените <domain> на желаемый домен, 
  внутри которого можно будет сканировать.
* Сброс состояния: `python main.py crawler_reset`
* Возможность обновлять уже скаченные страницы: `python main.py crawler-set-update <bool>` (Чтобы включить, поставьте 
  true)
* Установка временного интервала для обновления страницы (в секундах): `python main.py crawler-set-update-interval 
  <seconds>`
* Установка лимита на размер изображения (в байтах). Если на страницы изображения большего размера, то страница не 
  будет скачена: `python main.py crawler-set-possible_image_size <size>`