import json
from datetime import datetime, timedelta
from convert import conversion_rate
import os

CACHE_FILE = "rate_cache.json"

def timeout():
    # Если есть кэш
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
            rate = data["rate"]
            request_time = datetime.fromisoformat(data["time"])
            
            if datetime.now() - request_time < timedelta(hours=1):
                return rate, request_time

    # Новый запрос
    rate, request_time = conversion_rate()

    # Сохраняем кэш
    with open(CACHE_FILE, "w") as f:
        json.dump({"rate": rate, "time": request_time.isoformat()}, f)

        

    return rate, request_time

def calculation(res):
    baht = input("Введите сумму в батах: ")
    try:
        baht = float(baht)  # преобразуем в число
    except ValueError:
        print("Неверный ввод. Введите число.")
        return

    rub = round(baht / res, 2)  # 1 THB = 1/res RUB
    print(f"{baht} бат = {rub} рублей")


def main():
    res, request_time = timeout()
    print(f"Курс 1 RUB = {res} THB")
    print(f"Курс 1 THB = {round(1 / res, 2)} RUB")
    

if __name__ == "__main__":
    main()