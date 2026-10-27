import os
import random

import redis
import vk_api as vk
from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from quiz_utils import load_all_questions, normalize, get_short_answer


def send_keyboard(event, vk_api):
    keyboard = VkKeyboard()
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счёт')
    return keyboard.get_keyboard()


def send(vk_api, user_id, text, keyboard=None):
    vk_api.messages.send(
        user_id=user_id,
        message=text,
        random_id=random.randint(1, 1000000),
        keyboard=keyboard,
    )


def send_new_question(vk_api, user_id, db, quiz):
    question = random.choice(list(quiz.keys()))
    db.set(f'vk-{user_id}', question)
    send(vk_api, user_id, question)


def handle_event(event, vk_api, db, quiz):
    user_id = event.user_id
    text = event.text
    key = f'vk-{user_id}'

    if text.lower() in ('/start', 'start', 'начать'):
        send(vk_api, user_id, 'Здравствуйте', keyboard=get_keyboard())
    elif text == 'Новый вопрос':
        send_new_question(vk_api, user_id, db, quiz)
    elif text == 'Сдаться':
        question = db.get(key)
        if question is None:
            send(vk_api, user_id, 'Сначала нажми «Новый вопрос»')
            return
        send(vk_api, user_id, f'Правильный ответ: {quiz[question]}')
        send_new_question(vk_api, user_id, db, quiz)
    elif text == 'Мой счёт':
        send(vk_api, user_id, 'Счёт пока не подсчитывается')
    else:
        question = db.get(key)
        if question is None:
            send(vk_api, user_id, 'Нажми «Новый вопрос», чтобы начать')
            return
        if normalize(text) == get_short_answer(quiz[question]):
            db.delete(key)
            send(
                vk_api,
                user_id,
                'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»',
            )
        else:
            send(vk_api, user_id, 'Неправильно… Попробуешь ещё раз?')


def main():
    load_dotenv()
    db = redis.Redis(
        host=os.environ['REDIS_HOST'],
        port=int(os.environ['REDIS_PORT']),
        password=os.environ.get('REDIS_PASSWORD'),
        decode_responses=True,
    )
    quiz = load_all_questions('quiz-questions')

    vk_session = vk.VkApi(token=os.environ['VK_TOKEN'])
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            handle_event(event, vk_api, db, quiz)


if __name__ == '__main__':
    main()