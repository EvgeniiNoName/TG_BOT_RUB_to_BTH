import telebot
from telebot import types
from main import timeout, calculation
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения состояния пользователя
user_states = {}

# Главное меню
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Показать курс', 'Конвертировать баты')
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        'Привет! 👋\nЯ показываю курс RUB↔THB по карте UnionPay и могу конвертировать баты в рубли.',
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()

    # --- 1. Показать курс ---
    if text == 'Показать курс':
        # Сразу отправляем сообщение "ожидайте"
        waiting_msg = bot.send_message(
            chat_id, '⏳ Пожалуйста, подождите, получаю данные...')

        # Получаем все значения из кэша или нового запроса
        rate, request_time, thb, cny, onv_cny = timeout()
        bot.delete_message(chat_id, waiting_msg.message_id)

        # Формируем текст сообщения с промежуточными и конечными курсами
        msg_text = f"📊 Курс по состоянию на {request_time.strftime('%d.%m.%Y %H:%M')}:\n"

        if onv_cny:
            msg_text += f"1 CNY = {onv_cny} RUB\n"

        if thb:
            msg_text += f"1 CNY = {thb} THB: \n"
            
        msg_text += "-------------------\n"
        msg_text += f"1 RUB = {rate} THB\n"
        msg_text += f"1 THB = {round(1 / rate, 2)} RUB"

        bot.send_message(chat_id, msg_text)

    # --- 2. Начало конвертации ---
    elif text == 'Конвертировать баты':
        bot.send_message(chat_id, 'Введите сумму в батах:')
        user_states[chat_id] = 'awaiting_baht'

    # --- 3. Пользователь вводит сумму ---
    elif user_states.get(chat_id) == 'awaiting_baht':
        rate, _, _, _, _ = timeout()  # Получаем только rate для конверсии
        result = calculation(rate, text)
        if result:
            bot.send_message(chat_id, result, reply_markup=main_menu())
        else:
            bot.send_message(chat_id, '❗ Пожалуйста, введите число.')
        user_states.pop(chat_id, None)

    # --- 4. На случай других сообщений ---
    else:
        bot.send_message(
            chat_id,
            'Выберите действие:',
            reply_markup=main_menu())



if __name__ == '__main__':
    print('Бот запущен...')
    bot.infinity_polling()
