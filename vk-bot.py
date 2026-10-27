import os
import random

import vk_api as vk
from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def echo(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1, 1000),
    )


def send_keyboard(event, vk_api):
    keyboard = VkKeyboard()

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button('Мой счёт')

    vk_api.messages.send(
        user_id=event.user_id,
        message='Здравствуйте',
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )

def main():
    load_dotenv()
    vk_session = vk.VkApi(token=os.environ['VK_TOKEN'])
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text.lower() in ('/start', 'start', 'начать'):
                send_keyboard(event, vk_api)
            else:
                echo(event, vk_api)


if __name__ == '__main__':
    main()