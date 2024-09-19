Возможные команды:
* запуск краулера: `python main.py crawler-start`. Но перед этим надо обязательно установить URL, с которого краулер 
  начнет обход
* Установка начального URL: `python main.py crawler_set_start_url <URL>`. Замените <URL> на желаемый начальный URL.
* Установка разрешенного домена: `python main.py crawler_set_domain <domain>`. Замените <domain> на желаемый домен, 
  внутри которого можно будет сканировать.
* Сброс состояния: `python main.py crawler_reset`