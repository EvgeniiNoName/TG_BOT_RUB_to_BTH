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
from decimal import Decimal, ROUND_HALF_UP


# ------------------------------- #
#   Математическое округление     #
# ------------------------------- #

def rnd(x):
    """Округление HALF_UP до 2 знаков"""
    return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


# URL
url_cny = 'https://ru.myfin.by/bank/rshb/currency/krasnoyarsk'
url_union_pay = 'https://www.unionpayintl.com/cn/rate/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


# --------------------- #
#   Скачивание HTML     #
# --------------------- #

def download_page(url):
    print(f'Скачиваю: {url}')
    req = requests.get(url, headers=headers)
    print(f'Статус ответа: {req.status_code}')

    if req.status_code != 200:
        print(f'Ошибка {req.status_code}')
        return None

    print('HTML загружен успешно')
    return req.text


# --------------------- #
#   Извлечение RUB→CNY  #
# --------------------- #

def extract_data_from_html(src):
    soup = BeautifulSoup(src, 'lxml')

    row = None
    for tr in soup.find_all('tr'):
        a_tag = tr.find('a')
        if a_tag and 'Юань' in a_tag.text:
            row = tr
            break

    if not row:
        print("Не найдена строка с Юанем")
        return None

    tds = row.find_all('td')
    if len(tds) < 3:
        print("Недостаточно данных в строке")
        return None

    raw_rub_per_cny = float(tds[2].get_text(strip=True))
    rub_per_cny = rnd(raw_rub_per_cny)
    print(f'RUB→CNY (продажа): {rub_per_cny}')

    cny_per_rub = rnd(1 / rub_per_cny)
    print(f'CNY→RUB: {cny_per_rub}')

    return rub_per_cny, cny_per_rub


# --------------------- #
#   Извлечение CNY→THB  #
# --------------------- #

def download_baht(url):
    print('выполняю def download_baht')
    print('def download_baht: Получаю курс CNY→THB через Selenium...')

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'baseCurrencys'))
        ).click()
        time.sleep(1)

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#baseOPT a[val='THB']"))
        ).click()

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'transactionCurrencys'))
        ).click()
        time.sleep(1)

        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#tranOPT a[val='CNY']"))
        ).click()

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.huilv-submit a'))
        ).click()

        time.sleep(2)

        res_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'resultDiv'))
        )

        text = res_div.text
        match = re.search(r'1CNY\s*=\s*([\d.,]+)\s*THB', text)

        if match:
            raw_value = float(match.group(1).replace(',', ''))
            cny_to_thb = rnd(raw_value)
            print(f'def download_baht: CNY→THB: {cny_to_thb}')
            return cny_to_thb
        else:
            print('def download_baht: Не удалось найти курс CNY→THB')
            return None

    finally:
        driver.quit()


# --------------------- #
#   Правильный расчёт   #
# --------------------- #

def convert(rub_per_cny, cny_to_thb):
    raw = cny_to_thb / rub_per_cny
    rub_to_thb = rnd(raw)
    print(f'RUB→THB: {rub_to_thb}')
    thb_to_rub = rnd(1 / rub_to_thb)
    print(f'THB→RUB: {thb_to_rub}')
    return rub_to_thb, thb_to_rub


# --------------------- #
#   Главная функция     #
# --------------------- #

def conversion_rate():
    print('=== conversion_rate START ===')

    html = download_page(url_cny)
    rub_per_cny, cny_per_rub = extract_data_from_html(html)

    cny_to_thb = download_baht(url_union_pay)

    rub_to_thb, thb_to_rub = convert(rub_per_cny, cny_to_thb)

    request_time = datetime.now()

    print('=== conversion_rate END ===')

    return rub_to_thb, thb_to_rub, request_time, cny_to_thb, cny_per_rub, rub_per_cny


