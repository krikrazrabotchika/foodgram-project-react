import os
from random import randrange

import telegram
from dotenv import load_dotenv
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


def wake_up(update, context):
    """Отправка сообщения при подключении бота."""
    chat = update.effective_chat
    name = update.message.chat.first_name
    username = update.message.chat.username
    try:
        context.bot.send_message(
            chat_id=chat.id,
            text=f'Демон продуктовый помошник активирован >:-Е! '
            f'{name}.{username} теперь ты подписан '
            f'на демонические покупки игредиентов!'
        )
    except Exception as error:
        AssertionError(f'{error} Ошибка отправки ответа в телеграм')


def say_no(update, context):
    """Отправка рандомного ответа в чат."""
    chat = update.effective_chat
    random_answer = randrange(6)
    answers = {
        '0': 'Не прерывай чтение заклинания!',
        '1': 'Всё так же ни чего нового...',
        '2': 'Запомни: терпение и дисциплина',
        '3': 'Я знал что ты это спросишь',
        '4': 'Мы тут не для этого собрались',
        '5': 'Чем больше вопросов тем меньше ответов',
    }
    text = answers[str(random_answer)]
    try:
        context.bot.send_message(
            chat_id=chat.id,
            text=text
        )
    except Exception as error:
        raise AssertionError(f'{error} Ошибка отправки ответа в телеграм')


def main(chat_id):
    """Основная логика работы бота."""
    updater = Updater(token=TELEGRAM_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, say_no))
    updater.start_polling()


def send_message(chat_id, message):
    """Отправка сообщения в чат."""
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=chat_id, text=message)
    except Exception as error:
        raise AssertionError(f'{error} Ошибка отправки в телеграм')

    main(chat_id)
