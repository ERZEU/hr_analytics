
# import csv
import json
import pprint
import requests

from currency import get_currency

from datetime import datetime, timedelta, date
import pandas as pd
import time




def get_data_from_hh_simple(name, start, stop, page = 0, area = 113): #113 - rus
    """Подключение к серверу и получение json объекта"""

    #ua = UserAgent()
    url = 'https://api.hh.ru/vacancies'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.2.807 Yowser/2.5 Safari/537.36'#ua.random
    }

    params = {
        'text': f'NAME:{name}', # Текст фильтра. В имени должно быть слово 
        'area': area, # Поиск ощуществляется по вакансиям 
        'page': page, # Индекс страницы поиска на HH
        'per_page': 100, # Кол-во вакансий на 1 странице
        'only_with_salary': True,
        'date_from' : start,
        'date_to' : stop
    }

    req = requests.get(url=url, headers=headers, timeout=5, params=params)
    data = req.content.decode() # Декодируем его ответ, чтобы Кириллица отображалась корректно

    req.close()
    det = json.loads(data)

    return det



async def get_data_from_hh(name, start, stop, page = 0, area = 113): #113 - rus
    """Подключение к серверу и получение json объекта"""

    #ua = UserAgent()
    url = 'https://api.hh.ru/vacancies'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.2.807 Yowser/2.5 Safari/537.36'#ua.random
    }

    params = {
        'text': f'NAME:{name}', # Текст фильтра. В имени должно быть слово 
        'area': area, # Поиск ощуществляется по вакансиям 
        'page': page, # Индекс страницы поиска на HH
        'per_page': 100, # Кол-во вакансий на 1 странице
        'only_with_salary': True,
        'date_from' : start,
        'date_to' : stop
    }

    with requests.session() as session:
            req = session.get(url=url, headers=headers, timeout=5, params=params)
            data = req.content.decode() # Декодируем его ответ, чтобы Кириллица отображалась корректно
            det = json.loads(data)

    return det


# start1 = time.time()
# asyncio.run(get_data_from_hh(name="python", area=113, start="2023-03-20", stop="2023-03-22"))
# end1 = time.time() - start1
# print(end1)
# count2 = 0
# for page in range(0, pages):
#     count2 += len(asyncio.run(get_data_from_hh("python", "2023-03-20", "2023-03-22", page=page)))
# print(count2)
# end1 = time.time() - start1
# print(end1)


start2 = time.time()
pages = get_data_from_hh_simple(name="python", area=113, start="2023-03-20", stop="2023-03-22").get('pages')
count = 0
for page in range(0, pages):
    count += len(get_data_from_hh_simple("python", "2023-03-20", "2023-03-22", page=page))
print(count)
end2 = time.time() - start2
print(end2)




def prepare_salary(name, area):
    """Парсинг и формирование датасета"""
    time_now = datetime.today().strftime("%Y-%m-%d")
    time_delta = (datetime.today() - timedelta(days=5)).strftime("%Y-%m-%d")

    real_currency_rate = get_currency()
    check_size = get_data_from_hh(name=name, area=area, start=time_delta, stop=time_now)


    if check_size.get('found') != None:
        # df = pd.DataFrame(columns=["Название вакансии", "Компания", "Ссылка", "Город" ,"Время публикации", "Зарплата от", "Зарплата до", "Требования"])
        df = pd.DataFrame(columns=["Название вакансии", "Ссылка", "Город" ,"Время публикации", "Зарплата от", "Зарплата до", "cur"])
        count = 0
        while time_delta <= time_now:
            pages = get_data_from_hh(name=name, area=area, start=time_delta, stop=time_delta).get('pages')
            for page in range(0, pages):
                data = get_data_from_hh(name=name, page=page, area=area, start=time_delta, stop=time_delta)
                items = data.get('items')
                if items:
                    for vacancy in items:
                        if vacancy['salary']:
                            df.loc[count] = [vacancy['name'], 
                                        vacancy['alternate_url'],
                                        vacancy['area']['name'],
                                        str(vacancy['published_at'][:10]), 
                                        vacancy['salary']['from'] or "", 
                                        vacancy['salary']['to'] or "",
                                        vacancy['salary']['currency'] or ""] # изменение
                            if df.loc[count, 'Зарплата от'] and df.loc[count, 'cur']:
                                df.loc[count, 'Зарплата от'] = str(int(round(df.loc[count, 'Зарплата от']) / real_currency_rate[df.loc[count, 'cur']]))
                            if df.loc[count, 'Зарплата до'] and df.loc[count, 'cur']:
                                df.loc[count, 'Зарплата до'] = str(int(round(int(df.loc[count, 'Зарплата до']) / real_currency_rate[df.loc[count, 'cur']])))
                        else:
                            df.loc[count] = [vacancy['name'], vacancy['alternate_url'],
                                        vacancy['area']['name'], vacancy['published_at'][:10],
                                        "",
                                        "",
                                        ""]
                        count += 1
                        # yield mas[len(mas)-1]
                        # mas_req.append(vacancy['snippet']['requirement'])
            time_delta = (date.fromisoformat(time_delta) + timedelta(days=1)).strftime("%Y-%m-%d")
        return df



def prepare_salary2(name, area):
    """Парсинг и формирование датасета"""
    time_now = datetime.today().strftime("%Y-%m-%d")
    time_delta = (datetime.today() - timedelta(days=5)).strftime("%Y-%m-%d")

    real_currency_rate = get_currency()
    check_size = get_data_from_hh_simple(name=name, area=area, start=time_delta, stop=time_now)


    if check_size.get('found') != None:
        # df = pd.DataFrame(columns=["Название вакансии", "Компания", "Ссылка", "Город" ,"Время публикации", "Зарплата от", "Зарплата до", "Требования"])
        df = pd.DataFrame(columns=["Название вакансии", "Ссылка", "Город" ,"Время публикации", "Зарплата от", "Зарплата до", "cur"])
        count = 0
        while time_delta <= time_now:
            pages = get_data_from_hh_simple(name=name, area=area, start=time_delta, stop=time_delta).get('pages')
            for page in range(0, pages):
                data = get_data_from_hh_simple(name=name, page=page, area=area, start=time_delta, stop=time_delta)
                items = data.get('items')
                if items:
                    for vacancy in items:
                        if vacancy['salary']:
                            df.loc[count] = [vacancy['name'], 
                                        vacancy['alternate_url'],
                                        vacancy['area']['name'],
                                        str(vacancy['published_at'][:10]), 
                                        vacancy['salary']['from'] or "", 
                                        vacancy['salary']['to'] or "",
                                        vacancy['salary']['currency'] or ""] # изменение
                            if df.loc[count, 'Зарплата от'] and df.loc[count, 'cur']:
                                df.loc[count, 'Зарплата от'] = str(int(round(df.loc[count, 'Зарплата от']) / real_currency_rate[df.loc[count, 'cur']]))
                            if df.loc[count, 'Зарплата до'] and df.loc[count, 'cur']:
                                df.loc[count, 'Зарплата до'] = str(int(round(int(df.loc[count, 'Зарплата до']) / real_currency_rate[df.loc[count, 'cur']])))
                        else:
                            df.loc[count] = [vacancy['name'], vacancy['alternate_url'],
                                        vacancy['area']['name'], vacancy['published_at'][:10],
                                        "",
                                        "",
                                        ""]
                        count += 1
                        # yield mas[len(mas)-1]
                        # mas_req.append(vacancy['snippet']['requirement'])
            time_delta = (date.fromisoformat(time_delta) + timedelta(days=1)).strftime("%Y-%m-%d")
        return df



# start = time.time()
# mas = prepare_salary(name="python",area=113)
# end = time.time() - start
# print(end)
# print(len(mas.index))

# start2 = time.time()
# mas2 = prepare_salary2(name="python",area=113)
# end2 = time.time() - start2
# print(end2)
# print(len(mas2.index))


    
# def get_area(name_area):
#     """Сопоставление региона или города поиска с его id"""

#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.2.807 Yowser/2.5 Safari/537.36'
#     }
#     url = 'https://api.hh.ru/areas'
 
#     req = requests.get(url=url, headers=headers, timeout=5)

    
#     areas = json.loads(req.content.decode())
#     req.close()
#     for region in areas[0]['areas']: #поиск по регионам России
#         if re.search(name_area, region['name'], re.IGNORECASE):
#             return region['id']
#         for city in region['areas']: 
#             if re.search(name_area, city['name'], re.IGNORECASE):
#                 return city['id']


# def save(self, mas_vac): #проверено
#     with open("vacancies_russ_all.csv", mode="w", encoding='utf-8') as w_file:
#         file_writer = csv.writer(w_file, delimiter = ";", lineterminator="\r")
#         file_writer.writerow(["Название вакансии", "Ссылка", "Город" ,"Время публикации", "Зарплата от", "Зарплата до"])

#         if mas_vac:
#             for vac in mas_vac:
#                     file_writer.writerow(vac)



# получение текущего месяца и года
# time_now = datetime.today().strftime("%Y-%m-%d")
# time_delta = (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")

# d = datetime.today() - timedelta(days=30)
# print(time_now > time_delta)


# with open("vacancies_russ_all_.csv", mode="w", encoding='utf-8') as w_file:
#     file_writer = csv.writer(w_file, delimiter = ";", lineterminator="\r")
#     file_writer.writerow(["Название вакансии", "Ссылка", "Город" ,"Время публикации", "Зарплата от", "Зарплата до"])
#     for day in days:
#         mas = prepare_salary(name="разработчик",area=113, start=f'{year}-{month}-{day}', stop=f'{year}-{month}-{day}')
#         if mas:
#             for vac in mas:
#                     file_writer.writerow(vac)


# import cProfile
# cProfile.run('prepare_salary(name="python",area=113)')




