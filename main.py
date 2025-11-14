import json
from datetime import datetime, timedelta
from convert import conversion_rate
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE_DIR, 'rate_cache.json')


def timeout():
    print (f'выполняю def timeout')
    # Если есть кэш
    if os.path.exists(CACHE_FILE):
        print (f'def timeout: кэш есть')
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)
            rub_to_thb = data.get('rub_to_thb')
            thb_to_rub = data.get('thb_to_rub')
            request_time = datetime.fromisoformat(data.get('time'))
            cny_to_thb = data.get('cny_to_thb')
            cny_per_rub = data.get('cny_per_rub')
            rub_per_cny = data.get('rub_per_cny')

            if datetime.now() - request_time < timedelta(hours=1):
                print (f'def timeout: с предыдущего запроса прошло меньше часа')
                return rub_to_thb, thb_to_rub, request_time, cny_to_thb, cny_per_rub, rub_per_cny

    # Новый запрос    
    rub_to_thb, thb_to_rub, request_time, cny_to_thb, cny_per_rub, rub_per_cny = conversion_rate()

    # Сохраняем кэш со всеми значениями
    with open(CACHE_FILE, 'w') as f:
        json.dump({
            'rub_to_thb': rub_to_thb,
            'thb_to_rub': thb_to_rub,
            'time': request_time.isoformat(),
            'cny_to_thb': cny_to_thb,
            'cny_per_rub': cny_per_rub,
            'rub_per_cny': rub_per_cny
        }, f, ensure_ascii=False)

    return rub_to_thb, thb_to_rub, request_time, cny_to_thb, cny_per_rub, rub_per_cny


# def calculation(thb_to_rub, baht):
#     """
#     Функция принимает курс (res) и сумму в батах (baht),
#     возвращает строку с красиво отформатированным результатом.
#     """
#     try:
#         baht = float(str(baht).replace(',', '.'))
#     except ValueError:
#         return None

#     # rub = round(baht / res, 2)

#     # # Форматирование чисел по русскому стандарту
#     # baht_str = f"{baht:,.2f}".replace(",", " ").replace(".", ",")
#     # rub_str = f"{rub:,.2f}".replace(",", " ").replace(".", ",")

#     # return f"💰 {baht_str} бат = {rub_str} рублей"

#     rub = round(baht * thb_to_rub, 2)

#     return rub, baht

