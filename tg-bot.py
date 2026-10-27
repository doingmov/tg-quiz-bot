import os
import random
import redis


from enum import Enum, auto
from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler


class State(Enum):
    NEW_QUESTION = auto()
    SOLUTION_ATTEMPT = auto()


def load_questions(path):
    with open(path, 'r', encoding='KOI8-R') as file:
        content = file.read()

    questions_and_answers = {}
    question = None

    for block in content.split('\n\n'):
        block = block.strip()
        if block.startswith('Вопрос'):
            question = block.split(':', 1)[1].strip().replace('\n', '')
        elif block.startswith('Ответ') and question:
            answer = block.split(':', 1)[1].strip().replace('\n', '')
            questions_and_answers[question] = answer
            question = None

    return questions_and_answers


def load_all_questions(folder):
    all_questions = {}
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        all_questions.update(load_questions(path))
    return all_questions


def normalize(text):
    text = text.lower().replace('ё', 'е')
    return ' '.join(text.split()).strip(' .,!?"«»')


def get_short_answer(answer):
    short = answer.split('.')[0].split('(')[0]
    return normalize(short) or normalize(answer)


def start(update, context):
    keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счёт'],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text('Здравствуйте', reply_markup=reply_markup)
    return State.NEW_QUESTION


def handle_new_question_request(update, context):
    user_id = update.effective_user.id
    quiz = context.bot_data['quiz']
    db = context.bot_data['redis']

    question = random.choice(list(quiz.keys()))
    db.set(f'tg-{user_id}', question)
    update.message.reply_text(question)
    return State.SOLUTION_ATTEMPT


def handle_solution_attempt(update, context):
    user_id = update.effective_user.id
    quiz = context.bot_data['quiz']
    db = context.bot_data['redis']

    question = db.get(f'tg-{user_id}')
    correct_answer = get_short_answer(quiz[question])

    if normalize(update.message.text) == correct_answer:
        update.message.reply_text(
            'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        )
        return State.NEW_QUESTION

    update.message.reply_text('Неправильно… Попробуешь ещё раз?')
    return State.SOLUTION_ATTEMPT


def main():
    load_dotenv()
    token = os.environ['TELEGRAM_TOKEN']

    db = redis.Redis(
        host=os.environ['REDIS_HOST'],
        port=int(os.environ['REDIS_PORT']),
        password=os.environ.get('REDIS_PASSWORD'),
        decode_responses=True,
    )

    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.bot_data['quiz'] = load_all_questions('quiz-questions')
    dispatcher.bot_data['redis'] = db

    new_question_button = Filters.regex('^Новый вопрос$')
    any_button = Filters.regex('^(Новый вопрос|Сдаться|Мой счёт)$')

    conversation = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            State.NEW_QUESTION: [
                MessageHandler(new_question_button, handle_new_question_request),
            ],
            State.SOLUTION_ATTEMPT: [
                MessageHandler(new_question_button, handle_new_question_request),
                MessageHandler(
                    Filters.text & ~Filters.command & ~any_button,
                    handle_solution_attempt,
                ),
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    dispatcher.add_handler(conversation)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()