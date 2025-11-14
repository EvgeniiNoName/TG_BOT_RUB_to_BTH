import json
from datetime import datetime, timedelta
from convert import conversion_rate
import os
from logger_setup import logger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE_DIR, 'rate_cache.json')

def timeout():
    logger.debug("timeout START")
    if os.path.exists(CACHE_FILE):
        logger.debug("Кэш найден")
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)
            rub_to_thb = data.get('rub_to_thb')
            thb_to_rub = data.get('thb_to_rub')
            request_time = datetime.fromisoformat(data.get('time'))
            cny_to_thb = data.get('cny_to_thb')
            cny_per_rub = data.get('cny_per_rub')
            rub_per_cny = data.get('rub_per_cny')

            if datetime.now() - request_time < timedelta(hours=1):
                logger.debug("Используем кэш, с последнего запроса прошло меньше часа")
                return rub_to_thb, thb_to_rub, request_time, cny_to_thb, cny_per_rub, rub_per_cny

    rub_to_thb, thb_to_rub, request_time, cny_to_thb, cny_per_rub, rub_per_cny = conversion_rate()

    with open(CACHE_FILE, 'w') as f:
        json.dump({
            'rub_to_thb': rub_to_thb,
            'thb_to_rub': thb_to_rub,
            'time': request_time.isoformat(),
            'cny_to_thb': cny_to_thb,
            'cny_per_rub': cny_per_rub,
            'rub_per_cny': rub_per_cny
        }, f, ensure_ascii=False)
    logger.debug("timeout END")
    return rub_to_thb, thb_to_rub, request_time, cny_to_thb, cny_per_rub, rub_per_cny
