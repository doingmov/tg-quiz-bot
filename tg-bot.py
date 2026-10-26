import os
import random


from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def load_questions(path):
    with open(path, 'r', encoding='KOI8-R') as file:
        content = file.read()

    questions_and_answers = {}
    question = None

    for block in content.split('\n\n'):
        block = block.strip()
        if block.startswith('Вопрос'):
            question = block.split(':', 1)[1].strip()
        elif block.startswith('Ответ') and question:
            answer = block.split(':', 1)[1].strip()
            questions_and_answers[question] = answer
            question = None

    return questions_and_answers


def load_all_questions(folder):
    all_questions = {}
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        all_questions.update(load_questions(path))
    return all_questions


def start(update, context):
    keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счёт'],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text('Здравствуйте', reply_markup=reply_markup)


def handle_message(update, context):
    text = update.message.text

    if text == 'Новый вопрос':
        quiz = context.bot_data['quiz']
        question = random.choice(list(quiz.keys()))
        update.message.reply_text(question)
    else:
        update.message.reply_text(text)


def main():
    load_dotenv()
    token = os.environ['TELEGRAM_TOKEN']

    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.bot_data['quiz'] = load_all_questions('quiz-questions')

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, handle_message)
    )

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()