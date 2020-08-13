import requests
import os
import csv
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from dotenv import load_dotenv
load_dotenv()


def get_driver(url):
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        driver.maximize_window()
        driver.get(url)
        return driver
    except:
        time.sleep(1)
        return get_driver(url)


def send_request(url):
    res = requests.get(url).text
    return BeautifulSoup(res, 'html5lib')


def write(lines, file_name):
    with open(file=file_name, encoding='utf-8', mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerows(lines)


def read(file):
    with open(file=file, encoding='utf-8', mode='r') as csv_file:
        rows = list(csv.reader(csv_file))
    return rows


def main(year, model, model_url):
    driver = get_driver(url=model_url)
    time.sleep(5)
    topics = driver.find_elements_by_css_selector('ul.TopicsList a')
    sections = []
    topic_urls = []
    for topic in topics:
        sections.append(topic.find_element_by_class_name('item-title').text.strip())
        topic_urls.append(topic.get_attribute('href'))
    for i in range(len(topic_urls)):
        section_urls = []
        section_url = topic_urls[i]
        driver.get(section_url)
        inners = driver.find_elements_by_css_selector('ul.TopicsList a')
        for inner in inners:
            if 'http' in inner.get_attribute('href'):
                last_link = inner.get_attribute('href')
            else:
                last_link = 'https://www.nissanquickguide.com/' + inner.get_attribute('href')
            if last_link not in section_urls:
                section_urls.append(last_link)
        for sec_url in section_urls:
            if 'folder' in sec_url:
                driver.get(sec_url)
                ss = driver.find_elements_by_css_selector('ul.TopicsList a')
                for s in ss:
                    if 'http' in s.get_attribute('href'):
                        s_link = s.get_attribute('href')
                    else:
                        s_link = 'https://www.nissanquickguide.com/' + s.get_attribute('href')
                    if s_link not in section_urls:
                        section_urls.append(s_link)
        for section_u in section_urls:
            if 'folder' in section_u:
                continue
            line = [year, 'Nissan', model, sections[i], section_u]
            print(line)
            write(lines=[line], file_name='{}.csv'.format(year))
    if driver:
        driver.quit()


def detail(year, temp_file):
    if year == 2020:
        records = read(temp_file)
        for record in records:
            try:
                driver = get_driver(record[4])
                time.sleep(10)
                title = driver.find_element_by_class_name('topic-title').text.strip()
                video_url = driver.find_element_by_tag_name('video').get_attribute('src')
                post_img = driver.find_element_by_class_name('vjs-poster').get_attribute('style').replace('background-image: url("', '').replace('");', '')
                line = [year, 'Nissan', record[2], record[3], title, video_url, post_img]
                print(line)
                write(lines=[line], file_name='Nissan_{}_How_To.csv'.format(year))
            except NoSuchElementException:
                print('No', record[4])
            if driver:
                driver.quit()
    else:
        records = read(temp_file)
        count = 0
        for record in records:
            if count < 879:
                count = count + 1
                continue
            try:
                driver = get_driver(record[4])
                time.sleep(10)
                title = driver.find_element_by_class_name('topic-title').text.strip()
                video_url = driver.find_element_by_tag_name('video').get_attribute('src')
                post_img = driver.find_element_by_class_name('vjs-poster').get_attribute('style').replace(
                    'background-image: url("', '').replace('");', '')
                line = [year, 'Nissan', record[2], record[3], title, video_url, post_img]
                print(line)
                write(lines=[line], file_name='Nissan_{}_How_To.csv'.format(year))
            except NoSuchElementException:
                print('No', record[4])
            if driver:
                driver.quit()


def read_html(filename):
    with open(file=filename, encoding='utf-8', mode='r') as file:
        return file.read()


def get_models():
    from bs4 import BeautifulSoup
    for year in range(2019, 2021):
        file = '{}.html'.format(year)
        temp_file = '{}.csv'.format(year)
        if year == 2020:
            content = read_html(filename=file)
            soup = BeautifulSoup(content, 'html5lib')
            wrappers = soup.select('.group .list a')
            for wrapper in wrappers:
                model_name = wrapper.text.strip()
                model_link = 'https://www.nissanquickguide.com/' + wrapper['href'].replace('explore', 'browse/folder/')
                main(year=year, model=model_name, model_url=model_link)
            detail(year=year, temp_file=temp_file)
        else:
            detail(year=year, temp_file=temp_file)


def gather():
    records = []
    for year in range(2014, 2021):
        file_name = 'Nissan_{}_How_To.csv'.format(year)
        rows = read(file=file_name)
        for row in rows:
            if row not in records:
                print(row)
                records.append(row)
    write(lines=records, file_name='Nissan_How_To.csv')


if __name__ == '__main__':
    base_url = 'https://www.nissanquickguide.com/#/guide/2020/sentra/browse/folder/'
    gather()

