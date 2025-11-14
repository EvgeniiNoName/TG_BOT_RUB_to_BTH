import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time, re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from logger_setup import logger

url_cny = 'https://ru.myfin.by/bank/rshb/currency/krasnoyarsk'
url_union_pay = 'https://www.unionpayintl.com/cn/rate/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def rnd(x):
    res = float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    logger.debug("rnd: %s -> %s", x, res)
    return res

def download_page(url):
    logger.info("Скачиваю страницу: %s", url)
    try:
        req = requests.get(url, headers=headers)
        if req.status_code != 200:
            logger.error("Ошибка %s при скачивании %s", req.status_code, url)
            return None
        logger.info("HTML загружен успешно")
        return req.text
    except Exception as e:
        logger.exception("Ошибка при скачивании страницы: %s", e)
        return None

def extract_data_from_html(src):
    logger.debug("extract_data_from_html START")
    soup = BeautifulSoup(src, 'lxml')
    row = next((tr for tr in soup.find_all('tr') if tr.find('a') and 'Юань' in tr.find('a').text), None)
    if not row:
        logger.warning("Не найдена строка с Юанем")
        return None

    tds = row.find_all('td')
    if len(tds) < 3:
        logger.warning("Недостаточно данных в строке")
        return None

    raw_rub_per_cny = float(tds[2].get_text(strip=True))
    rub_per_cny = rnd(raw_rub_per_cny)
    cny_per_rub = rnd(1 / rub_per_cny)
    logger.info("RUB→CNY: %s, CNY→RUB: %s", rub_per_cny, cny_per_rub)
    return rub_per_cny, cny_per_rub

def download_baht(url):
    logger.info("Получаю курс CNY→THB через Selenium")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'baseCurrencys'))).click()
        time.sleep(1)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#baseOPT a[val='THB']"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'transactionCurrencys'))).click()
        time.sleep(1)
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#tranOPT a[val='CNY']"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.huilv-submit a'))).click()
        time.sleep(2)

        res_div = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'resultDiv')))
        text = res_div.text
        match = re.search(r'1CNY\s*=\s*([\d.,]+)\s*THB', text)
        if match:
            cny_to_thb = rnd(float(match.group(1).replace(',', '')))
            logger.info("CNY→THB: %s", cny_to_thb)
            return cny_to_thb
        logger.warning("Не удалось найти курс CNY→THB")
        return None
    except Exception as e:
        logger.exception("Ошибка при получении курса CNY→THB: %s", e)
        return None
    finally:
        driver.quit()

def convert(rub_per_cny, cny_to_thb):
    rub_to_thb = rnd(cny_to_thb / rub_per_cny)
    thb_to_rub = rnd(1 / rub_to_thb)
    logger.info("RUB→THB: %s, THB→RUB: %s", rub_to_thb, thb_to_rub)
    return rub_to_thb, thb_to_rub

def conversion_rate():
    logger.info("conversion_rate START")
    html = download_page(url_cny)
    rub_per_cny, cny_per_rub = extract_data_from_html(html)
    cny_to_thb = download_baht(url_union_pay)
    rub_to_thb, thb_to_rub = convert(rub_per_cny, cny_to_thb)
    request_time = datetime.now()
    logger.info("conversion_rate END")
    return rub_to_thb, thb_to_rub, request_time, cny_to_thb, cny_per_rub, rub_per_cny
