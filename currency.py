
import json
import requests


def get_currency():
    """Получение котировок курса валют"""
    req = requests.get('https://api.hh.ru/dictionaries', verify=False)
    data = req.content.decode() # Декодируем его ответ, чтобы Кириллица отображалась корректно
    req.close()
    det = json.loads(data)
    currency_rate = {}
    det = det['currency']
    for cur in det:
        currency_rate[cur['code']] = cur['rate']
    return currency_rate