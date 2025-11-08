import json
from datetime import datetime, timedelta
from convert import conversion_rate
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE_DIR, 'rate_cache.json')


def timeout():
    # Если есть кэш
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)
            rate = data.get('rate')
            request_time = datetime.fromisoformat(data.get('time'))
            thb = data.get('thb')
            cny = data.get('cny')
            onv_cny = data.get('onv_cny')

            if datetime.now() - request_time < timedelta(hours=1):
                return rate, request_time, thb, cny, onv_cny

    # Новый запрос
    rate, request_time, thb, cny, onv_cny = conversion_rate()

    # Сохраняем кэш со всеми значениями
    with open(CACHE_FILE, 'w') as f:
        json.dump({
            'rate': rate,
            'time': request_time.isoformat(),
            'thb': thb,
            'cny': cny,
            'onv_cny': onv_cny
        }, f, ensure_ascii=False)

    return rate, request_time, thb, cny, onv_cny


def calculation(res, baht):
    """
    Функция принимает курс (res) и сумму в батах (baht),
    возвращает строку с красиво отформатированным результатом.
    """
    try:
        baht = float(str(baht).replace(',', '.'))
    except ValueError:
        return None

    rub = round(baht / res, 2)

    # Форматирование чисел по русскому стандарту
    baht_str = f"{baht:,.2f}".replace(",", " ").replace(".", ",")
    rub_str = f"{rub:,.2f}".replace(",", " ").replace(".", ",")

    return f"💰 {baht_str} бат = {rub_str} рублей"


def main():
    res, request_time, thb, cny, onv_cny = timeout()
    print(f'Курс RUB→THB: {res}')
    print(f'Курс THB→RUB: {round(1 / res, 2)}')
    if cny and onv_cny:
        print(f'Курс RUB→CNY: {onv_cny}')
        print(f'Курс CNY→RUB: {cny}')
    if thb:
        print(f'Курс CNY→THB: {thb}')


if __name__ == '__main__':
    main()
