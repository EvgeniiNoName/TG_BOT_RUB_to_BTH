import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from datetime import datetime


# URL
# url_cny = 'https://bankiros.ru/bank/rshb/currency/cny'
url_cny = 'https://ru.myfin.by/bank/rshb/currency/krasnoyarsk'
url_union_pay = 'https://www.unionpayintl.com/cn/rate/'

# Заголовки для имитации реального пользователя
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Функция для скачивания страницы


def download_page(url):
    print(f'Скачиваю: {url}')  # Отладка
    req = requests.get(url, headers=headers)
    print(f'Статус ответа: {req.status_code}')  # Показываем статус код
    if req.status_code == 200:
        print('все ОК!')
        # print(req.text)
        src = req.text
        return src
    else:
        print(f'Ошибка {req.status_code}: {url}')
        return None

# Функция для извлечения данных из HTML для поиска юаня


def extract_data_from_html(src):
    soup = BeautifulSoup(src, 'lxml')

    # ищем строку с Юанем
    row = None
    for tr in soup.find_all('tr'):
        a_tag = tr.find('a')
        if a_tag and 'Юань' in a_tag.text:
            row = tr
            break

    if not row:
        print("!!!_Не найдено значение для юаня в HTML.")
        return None

    # находим все <td> в строке
    tds = row.find_all('td')
    if len(tds) < 3:
        print("!!!_Недостаточно данных в строке.")
        return None

    cny = tds[2].get_text(strip=True)  # третий <td> — продажа
    print('Курс CNY→RUB:', cny)
    return cny



    # soup = BeautifulSoup(src, 'lxml')
    # all = soup.find_all(
    #     'div', class_='xxx-text-bold xxx-fs-24 xxx-adjustment-line-h')
    # onv_cny = all[1].find('span').get_text(strip=True)
    # print('Курс CNY→RUB: ', onv_cny)
    # cny = round(1 / float(onv_cny), 2)
    # print('Курс RUB→CNY: ', cny)
    # return cny


def download_baht(url):

    # --- Настройки Selenium ---
    options = Options()
    options.add_argument("--headless")  # без GUI
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)

        # -----------------------------
        # 1. Выбираем базовую валюту THB
        # -----------------------------
        select_base = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'baseCurrencys'))
        )
        select_base.click()
        time.sleep(1)

        thb_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#baseOPT a[val='THB']"))
        )
        thb_option.click()

        # -----------------------------
        # 2. Выбираем валюту для конверсии CNY
        # -----------------------------
        select_trans = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'transactionCurrencys'))
        )
        select_trans.click()
        time.sleep(1)

        cny_option = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#tranOPT a[val='CNY']"))
        )
        cny_option.click()

        # -----------------------------
        # 3. Нажимаем кнопку "查询"
        # -----------------------------
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.huilv-submit a'))
        )
        submit_button.click()
        time.sleep(2)

        # -----------------------------
        # 4. Получаем результат
        # -----------------------------
        res_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'resultDiv'))
        )
        text = res_div.text
        # print("Полный текст:", text)

        match = re.search(r'1CNY\s*=\s*([\d.,]+)\s*THB', text)
        if match:
            thb = round(float(match.group(1).replace(',', '')), 2)
            print('Курс CNY→THB:', thb)
            return thb
        else:
            print('Не удалось найти курс')
            return None

    finally:
        driver.quit()


def convert(cny, thb):
    cny = round(float(cny), 2)
    thb = round(float(thb), 2)
    res_convertion = round(cny * thb, 2)
    return res_convertion


# Главная логика скрипта
def conversion_rate():
    start_page = download_page(url_cny)
    if not start_page:
        return
    cny = extract_data_from_html(start_page)
    thb = download_baht(url_union_pay)
    res = convert(cny, thb)
    request_time = request_time = datetime.now()

    return res, request_time