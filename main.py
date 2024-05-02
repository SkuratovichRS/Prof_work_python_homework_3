import json
import unicodedata
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers


def get_fake_headers():
    return Headers(browser="chrome",
                   os="win",
                   headers=True).generate()


class HHParser:
    def __init__(self):
        self.base_url = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
        self.pages_url = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&page='

    def get_tags(self):
        response_1 = requests.get(url=self.base_url, headers=get_fake_headers())
        page_1_data = BeautifulSoup(response_1.text, features='lxml')
        article_tags = page_1_data.find_all('div', class_='vacancy-serp-item-body')
        for i in range(1, 10):
            url = f'{self.pages_url}{str(i)}'
            response = requests.get(url=url, headers=get_fake_headers())
            page_data = BeautifulSoup(response.text, features='lxml')
            article_tags += page_data.find_all('div', class_='vacancy-serp-item-body')
        return article_tags

    def get_info(self):
        article_tags = self.get_tags()
        valid_article_tags = []
        for article_tag in article_tags:
            vacancy = article_tag.find('span', class_='serp-item__title')
            if vacancy:
                if 'django' in vacancy.text.lower() or 'flask' in vacancy.text.lower():
                    valid_article_tags.append(article_tag)
        data = []
        for article_tag in valid_article_tags:
            link_tag = article_tag.find('a', class_='bloko-link')
            link = link_tag['href']
            salary = article_tag.find(attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
            salary = unicodedata.normalize('NFKC', salary.text) if salary else None
            name = article_tag.find(attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
            name = unicodedata.normalize('NFKC', name.text) if name else None
            city = article_tag.find(attrs={'data-qa': 'vacancy-serp__vacancy-address'})
            city = unicodedata.normalize('NFKC', city.text.split()[0]) if city else None
            city = city[:-1] if "," in city else city
            data.append({'link': link,
                         'salary': salary,
                         'name': name,
                         'city': city,
                         })
        return data

    def write_info(self):
        with open('HH_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.get_info(), f, indent=4, ensure_ascii=False)


parser = HHParser()
parser.write_info()
