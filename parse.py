import csv
import json
import requests
# from fake_useragent import UserAgent
import re
from currency import get_currency

from datetime import datetime, timedelta, date
import pandas as pd
import time


def get_data_from_hh(name, start, stop, page=0, area=113):  # 113 - rus
    """Подключение к серверу и получение json объекта"""

    # ua = UserAgent()
    url = 'https://api.hh.ru/vacancies'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.2.807 Yowser/2.5 Safari/537.36'
        # ua.random
    }

    params = {
        'text': f'NAME:{name}',  # Текст фильтра. В имени должно быть слово
        'area': area,  # Поиск ощуществляется по вакансиям
        'page': page,  # Индекс страницы поиска на HH
        'per_page': 100,  # Кол-во вакансий на 1 странице
        'only_with_salary': False,
        'date_from': start,
        'date_to': stop
    }

    req = requests.get(url=url, headers=headers, timeout=5, params=params, verify=False)
    data = req.content.decode()  # Декодируем его ответ, чтобы Кириллица отображалась корректно
    print(req.status_code)
    req.close()
    det = json.loads(data)

    return det


def prepare_salary(name, area):
    """Парсинг и формирование датасета"""
    time_now = datetime.today().strftime("%Y-%m-%d")
    time_delta = (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")

    real_currency_rate = get_currency()
    check_size = get_data_from_hh(name=name, area=area, start=time_delta, stop=time_now)

    if check_size.get('found') is not None:
        df = pd.DataFrame(columns=["Компания", "Название вакансии", "Ссылка", "Город", "Время публикации", "Зарплата от", "Зарплата до", "cur", "Требования"])
        #df = pd.DataFrame(columns=["Название вакансии", "Ссылка", "Город", "Время публикации", "Зарплата от", "Зарплата до", "cur"])
        count = 0
        if check_size.get('found') > 2000:
            while time_delta <= time_now:
                pages = get_data_from_hh(name=name, area=area, start=time_delta, stop=time_delta).get('pages')
                for page in range(0, pages):
                    data = get_data_from_hh(name=name, page=page, area=area, start=time_delta, stop=time_delta)
                    items = data.get('items')
                    if items:
                        for vacancy in items:
                            if vacancy['salary']:
                                df.loc[count] = [vacancy['employer']['name'],
                                                 vacancy['name'],
                                                 vacancy['alternate_url'],
                                                 vacancy['area']['name'],
                                                 str(vacancy['published_at'][:10]),
                                                 vacancy['salary']['from'] or "",
                                                 vacancy['salary']['to'] or "",
                                                 vacancy['salary']['currency'] or "",
                                                 vacancy['snippet']['requirement']
                                                 ]  # изменение
                                if df.loc[count, 'Зарплата от'] and df.loc[count, 'cur']:
                                    df.loc[count, 'Зарплата от'] = str(
                                        int(round(df.loc[count, 'Зарплата от']) / real_currency_rate[
                                            df.loc[count, 'cur']]))
                                elif df.loc[count, 'Зарплата до'] and df.loc[count, 'cur']:
                                    df.loc[count, 'Зарплата до'] = str(int(round(
                                        int(df.loc[count, 'Зарплата до']) / real_currency_rate[df.loc[count, 'cur']])))

                            else:
                                df.loc[count] = [vacancy['employer']['name'],
                                                 vacancy['name'],
                                                 vacancy['alternate_url'],
                                                 vacancy['area']['name'],
                                                 vacancy['published_at'][:10],
                                                 "",
                                                 "",
                                                 "",
                                                 vacancy['snippet']['requirement']
                                                 ]
                            count += 1
                            # yield mas[len(mas)-1]
                            # mas_req.append(vacancy['snippet']['requirement'])
                time_delta = (date.fromisoformat(time_delta) + timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            pages = get_data_from_hh(name=name, area=area, start=time_delta, stop=time_now).get('pages')
            for page in range(0, pages):
                data = get_data_from_hh(name=name, page=page, area=area, start=time_delta, stop=time_now)
                items = data.get('items')
                if items:
                    for vacancy in items:
                        if vacancy['salary']:
                            df.loc[count] = [vacancy['employer']['name'],
                                             vacancy['name'],
                                             vacancy['alternate_url'],
                                             vacancy['area']['name'],
                                             str(vacancy['published_at'][:10]),
                                             vacancy['salary']['from'] or "",
                                             vacancy['salary']['to'] or "",
                                             vacancy['salary']['currency'] or "",
                                             vacancy['snippet']['requirement']
                                             ]  # изменение
                            if df.loc[count, 'Зарплата от'] and df.loc[count, 'cur']:
                                df.loc[count, 'Зарплата от'] = str(
                                    int(round(df.loc[count, 'Зарплата от']) / real_currency_rate[df.loc[count, 'cur']]))
                            if df.loc[count, 'Зарплата до'] and df.loc[count, 'cur']:
                                df.loc[count, 'Зарплата до'] = str(int(round(
                                    int(df.loc[count, 'Зарплата до']) / real_currency_rate[df.loc[count, 'cur']])))
                        else:
                            df.loc[count] = [vacancy['employer']['name'],
                                             vacancy['name'],
                                             vacancy['alternate_url'],
                                             vacancy['area']['name'],
                                             vacancy['published_at'][:10],
                                             "",
                                             "",
                                             "",
                                             vacancy['snippet']['requirement']
                                             ]
                        count += 1
        return df


def get_area(name_area):
    """Сопоставление региона или города поиска с его id"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.2.807 Yowser/2.5 Safari/537.36'
    }
    url = 'https://api.hh.ru/areas'

    req = requests.get(url=url, headers=headers, timeout=5, verify=False)

    areas = json.loads(req.content.decode())
    req.close()
    for region in areas[0]['areas']:  # поиск по регионам России
        if re.search(name_area, region['name'], re.IGNORECASE):
            return region['id']
        for city in region['areas']:
            if re.search(name_area, city['name'], re.IGNORECASE):
                return city['id']
