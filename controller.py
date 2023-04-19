import re

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from parse import get_area, prepare_salary

# from parse_async import get_data_from_day_and_page, get_area


class Function():
    def get_vac(self, name_vac, name_area):
        id_area = 113
        if name_area:
            id_area = get_area(name_area)

        # start = time.time()

        # global df
        # global count
        # count = 0
        # df = pd.DataFrame(columns=["Название вакансии", "Ссылка", "Город" ,"Время публикации", "Зарплата от", "Зарплата до", "cur"])
        # asyncio.run(get_data_from_day_and_page(name_vac, id_area))

        # end = time.time() - start
        # print(end)
        return prepare_salary(name_vac, id_area)
    
    def graph_zp(self, mas_vac):
        zp_ot = []
        zp_do = []
        for index, row in mas_vac.iterrows():
            if row['Зарплата от']:
                zp_ot.append(int(row['Зарплата от']))
            if row['Зарплата до']:
                zp_do.append(int(row['Зарплата до']))

        zp_ot = sorted(zp_ot)
        zp_do = sorted(zp_do)

        plt.plot(zp_ot)
        plt.title('График З/П')
        plt.xlabel('Количество вакансий', color='gray')
        plt.ylabel('Размер З/П',color='gray')
                
        plt.plot(zp_ot, label='З/П от')
        plt.legend()
        plt.show()

        plt.plot(zp_do, label='З/П до')
        plt.legend()
        plt.show()

    def graph_zp_region(self, mas_vac):
        region_zp = dict()
        mas_region = []
        for index, row in mas_vac.iterrows():
            if st := row['Город']:
                if st not in mas_region:
                    mas_region.append(st)
                    if (minimum := [int(row['Зарплата от']) for index, row in mas_vac.iterrows() if row['Город'] == st and row['Зарплата от']]) and (maximum := [int(row['Зарплата до']) for index, row in mas_vac.iterrows() if row['Город'] == st and row['Зарплата до']]):
                        region_zp[st] = [min(minimum), max(maximum)]

        index = np.arange(len(region_zp))

        plt.title('Минимальные и максимальные З/П по регионам')
        plt.xticks(index, list(region_zp.keys()), rotation=45, ha='right')
        plt.xlabel('Регион', color='gray')
        plt.ylabel('Уровень З/П', color='gray')

        plt.bar(index - (0.4 / 2), [i[0] for i in region_zp.values()], label='Минимальный нижний порог', width=0.4)
        plt.bar(index + (0.4 / 2), [i[1] for i in region_zp.values()], label='Максимальный верхний порог', width=0.4)
        plt.legend()
        plt.show()

    def graph_names(self, mas_vac):
        text = ''
        for index, row in mas_vac.iterrows():
            if st := row['Требования']:
                if isinstance(st, str):
                    text += st
        text = text.lower()

        pattern = r'[a-zA-Z]+'
        mas_words = re.findall(pattern,text)
        dict_words = {}
        for word in mas_words:
            dict_words[mas_words.count(word)] = word
        result = dict(sorted(dict_words.items(), key=lambda x: x[0], reverse=True))

        result_2 = dict()
        count = 0
        for key, value in result.items():
            if count <= 7:
                result_2[key] = value
                count += 1
            else:
                break

        index = np.arange(len(result_2))
        values = list(result_2)
        plt.bar(index, values)
        plt.xticks(index+0.4, list(result_2.values()))
        plt.show()

    def graph_region(self, mas_vac: pd.DataFrame):
        try:
            mas_region = []
            for index, row in mas_vac.iterrows():
                if st := row['Город']:
                    mas_region.append(st)
            temp = list(set(mas_region))
            dicter = dict()
            for item in temp:
                dicter[item] = mas_region.count(item)
            sorted_dict = dict(sorted(dicter.items(), key=lambda item: item[1], reverse=True))

            result = dict()
            count = 0
            for key, value in sorted_dict.items():
                if count <= 6:
                    result[key] = value
                    count += 1
                else:
                    break

            vals = list(result.values())
            labels = list(result.keys())
            fig, ax = plt.subplots()

            temper = tuple([0.15-0.02 for i in range(len(result))])

            ax.pie(vals, labels=labels, autopct='%1.1f%%', shadow=True, explode=temper,
                   wedgeprops={'lw': 1, 'ls': '--', 'edgecolor': "k"}, rotatelabels=True)
            ax.axis("equal")
            plt.show()
        except Exception as err:
            print(err)

    def save(self, mas_vac: pd.DataFrame):
        try:
            mas_vac.to_excel("vacancies.xlsx")
        except Exception as err:
            print(err)

