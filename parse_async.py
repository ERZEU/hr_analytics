
import json
import requests


import pandas as pd
import time
import re
import asyncio
import aiohttp
from datetime import datetime, timedelta, date
# from currency import get_currency




df = pd.DataFrame(columns=["Название вакансии", "Ссылка", "Город" ,"Время публикации", "Зарплата от", "Зарплата до", "cur"])
count = 0

async def get_data(session, name, area, start, stop, page):
    url = 'https://api.hh.ru/vacancies'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.2.807 Yowser/2.5 Safari/537.36'#ua.random
    }

    params = {
        'text': f'NAME:{name}',     # Текст фильтра. В имени должно быть слово 
        'area': f'{area}',          # Поиск ощуществляется по вакансиям 
        'page': f'{page}',          # Индекс страницы поиска на HH
        'per_page': f'100',         # Кол-во вакансий на 1 странице
        'only_with_salary': f'False',
        'date_from' : f'{start}',
        'date_to' : f'{stop}'
    }

    async with session.get(url=url, headers=headers, params=params, timeout=5) as response:
        data_decode = await response.text()
        data = json.loads(data_decode)
        global df
        if data.get('found') != None:
            global count
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
                    else:
                        df.loc[count] = [vacancy['name'], vacancy['alternate_url'],
                                    vacancy['area']['name'], vacancy['published_at'][:10],
                                    "",
                                    "",
                                    ""]
                    count += 1
        
        


async def get_data_from_day_and_page(name, area):


    time_now = datetime.today().strftime("%Y-%m-%d")
    time_delta = (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")

    async with aiohttp.ClientSession() as session:

        tasks = []

        while time_delta <= time_now:
            url = 'https://api.hh.ru/vacancies'

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.2.807 Yowser/2.5 Safari/537.36'#ua.random
            }

            params = {
                'text': f'NAME:{name}',     # Текст фильтра. В имени должно быть слово 
                'area': f'{area}',          # Поиск ощуществляется по вакансиям 
                'page': f'0',               # Индекс страницы поиска на HH
                'per_page': f'100',         # Кол-во вакансий на 1 странице
                'only_with_salary': f'False',
                'date_from' : f'{time_delta}',
                'date_to' : f'{time_delta}'
            }
            response = await session.get(url=url, headers=headers, params=params, timeout=5)
            data = await response.text()
            pages = json.loads(data).get('pages')


            for page in range(pages):
                task = asyncio.create_task(get_data(session=session, name=name, area=area, start=time_delta, stop=time_delta, page=page))
                tasks.append(task)


            time_delta = (date.fromisoformat(time_delta) + timedelta(days=1)).strftime("%Y-%m-%d")

        await asyncio.gather(*tasks)

def get_area(name_area):
    """Сопоставление региона или города поиска с его id"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.2.807 Yowser/2.5 Safari/537.36'
    }
    url = 'https://api.hh.ru/areas'
 
    req = requests.get(url=url, headers=headers, timeout=5)

    
    areas = json.loads(req.content.decode())
    req.close()
    for region in areas[0]['areas']: #поиск по регионам России
        if re.search(name_area, region['name'], re.IGNORECASE):
            return region['id']
        for city in region['areas']: 
            if re.search(name_area, city['name'], re.IGNORECASE):
                return city['id']


# def main():
#     start = time.time()

#     asyncio.run(get_data_from_day_and_page('python',113))
#     df.to_excel("vac2.xlsx")

#     end = time.time() - start
#     print(end)

# if __name__ == "__main__":
#     main()

    #&backurl=https://kazan.hh.ru/vacancy/77236116?from=vacancy_search_list&query=python

