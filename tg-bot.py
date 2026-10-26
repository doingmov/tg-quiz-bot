import os
from telegram import ReplyKeyboardMarkup

from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def start(update, context):
    keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счёт'],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text('Здравствуйте', reply_markup=reply_markup)


def echo(update, context):
    update.message.reply_text(update.message.text)


def main():
    load_dotenv()
    token = os.environ['TELEGRAM_TOKEN']

    updater = Updater(token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()