import os


def load_questions(path):
    with open(path, 'r', encoding='KOI8-R') as file:
        content = file.read()

    questions_and_answers = {}
    question = None

    for block in content.split('\n\n'):
        block = block.strip()
        if block.startswith('Вопрос'):
            question = block.split(':', 1)[1].strip().replace('\n', ' ')
        elif block.startswith('Ответ') and question:
            answer = block.split(':', 1)[1].strip().replace('\n', ' ')
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