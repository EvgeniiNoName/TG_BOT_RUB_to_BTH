import telebot
from telebot import types
from main import timeout
import os
from dotenv import load_dotenv
from logger_setup import logger

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

user_states = {}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Показать курс', 'Конвертировать баты')
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        'Привет! 👋\nЯ показываю курс RUB↔THB по карте UnionPay и могу конвертировать баты в рубли.',
        reply_markup=main_menu()
    )
    logger.info("Пользователь %s запустил бота", chat_id)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()
    logger.debug("Сообщение от %s: %s", chat_id, text)

    if text == 'Показать курс':
        waiting_msg = bot.send_message(chat_id, '⏳ Пожалуйста, подождите, получаю данные...')
        try:
            rub_to_thb, thb_to_rub, request_time, cny_to_thb, cny_per_rub, rub_per_cny = timeout()
        except Exception as e:
            bot.send_message(chat_id, '❗ Ошибка при получении курса')
            logger.exception("Ошибка timeout для пользователя %s: %s", chat_id, e)
            return

        bot.delete_message(chat_id, waiting_msg.message_id)
        msg_text = (
            f"📊 Курс по состоянию на {request_time.strftime('%d.%m.%Y %H:%M')}:\n"
            f"1 CNY = {rub_per_cny} RUB\n"
            f"1 CNY = {cny_to_thb} THB\n"
            "-------------------\n"
            f"1 RUB = {rub_to_thb} THB\n"
            f"1 THB = {thb_to_rub} RUB"
        )
        bot.send_message(chat_id, msg_text)
        logger.info("Показан курс пользователю %s", chat_id)

    elif text == 'Конвертировать баты':
        bot.send_message(chat_id, 'Введите сумму в батах:')
        user_states[chat_id] = 'awaiting_baht'
        logger.info("Ожидаем сумму от пользователя %s", chat_id)

    elif user_states.get(chat_id) == 'awaiting_baht':
        try:
            _, thb_to_rub, _, _, _, _ = timeout()
            baht = float(str(text).replace(',', '.'))
            baht_str = f"{baht:,.2f}".replace(",", " ").replace(".", ",")
            rub_str = f"{baht * thb_to_rub:,.2f}".replace(",", " ").replace(".", ",")
            bot.send_message(chat_id, f"💰 {baht_str} бат = {rub_str} руб", reply_markup=main_menu())
            logger.info("Конвертация для пользователя %s: %s бат = %s руб", chat_id, baht, rub_str)
        except ValueError:
            bot.send_message(chat_id, '❗ Пожалуйста, введите число.')
            logger.warning("Неверный ввод от пользователя %s: %s", chat_id, text)
        except Exception as e:
            bot.send_message(chat_id, '❗ Произошла ошибка при конвертации')
            logger.exception("Ошибка конвертации для пользователя %s: %s", chat_id, e)
        finally:
            user_states.pop(chat_id, None)

    else:
        bot.send_message(chat_id, 'Выберите действие:', reply_markup=main_menu())
        logger.debug("Пользователь %s отправил неизвестное сообщение", chat_id)

if __name__ == '__main__':
    logger.info("Бот запущен")
    try:
        bot.infinity_polling()
    except Exception as e:
        logger.exception("Ошибка при запуске бота: %s", e)
