import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import re

URL_TEMPLATE = "https://codeforces.com/problemset/page/1?order=BY_SOLVED_DESC"
headers = {'Accept-Language': 'ru-RU'}


def codeforces_parser(URL_TEMPLATE=URL_TEMPLATE, headers=headers):
    """Постраничный парсинг, результат возвращается в виде двух(2 зависимые таблицы) DataFrame"""

    r = requests.get(URL_TEMPLATE, headers=headers)
    soup = bs(r.text, "html.parser")

    row_data = soup.find_all('td', {'class': 'id'})

    number = [re.sub("^\s+|\n|\r|\s+$", '', i.a.text) for i in row_data]
    name = [re.sub("^\s+|\n|\r|\s+$", '', i.find_next('td').a.text) for i in row_data]
    topics = [np.array([j.text for j in i.find_next('td').div.find_next('div').find_all('a')]) for i in row_data]
    complexity = [elem.find_next('td').find_next('td').find_next('td').span.text
                  if elem.find_next('td').find_next('td').find_next('td').span
                  else '-1' for elem in row_data]
    decisions_number = []
    for elem in row_data:
        block = elem.find_next('td').find_next('td').find_next('td').find_next('td')
        if block.a:
            decisions_number.append(re.sub("^\s+|\n|\r|\s+$", '', block.a.text)[1:])
        else:
            decisions_number.append(-1)

    topics_num = []
    topics_total = []

    for topic, num in zip(topics, number):
        for top in topic:
            topics_num.append(num)
            topics_total.append(top)

    main_data = pd.DataFrame(columns=['Number', 'Name', 'Complexity', 'Number of decisions'])
    main_data['Number'] = number
    main_data['Name'] = name
    main_data['Complexity'] = complexity
    main_data['Number of decisions'] = decisions_number

    topics_data = pd.DataFrame(columns=['Number', 'Topic'])
    topics_data['Number'] = np.array(topics_num)
    topics_data['Topic'] = np.array(topics_total)

    return main_data, topics_data