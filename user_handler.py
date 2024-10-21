import json
from db.get_data import get_question, get_answer_keyword
from db.insert_data import create_poll
from typing import Tuple, Union

THRESHOLD = 0.75
UPPER_THRESHOLD = 0.9


def generate_result(models, answer: str, user_message: str) -> Tuple[str, bool]:
    is_failed = False
    score = models["result"](answer, user_message)
    if score < THRESHOLD:
        res = "неверно"
        is_failed = True
    else:
        if score > UPPER_THRESHOLD:
            res = "верно"
        else:
            res = "в целом верно"

    return res, is_failed


async def process_room(last_idx: int, room_id: int, rdb):
    await rdb.set(room_id, last_idx)


async def process_answer(models, room_id: int, q_number: int, message: str) -> Union[Tuple[None, None], Tuple[str, None], Tuple[str, str]]:
    result = await get_answer_keyword(room_id, q_number)
    if not result:
        return None, None
    answer, keyword = result
    res, is_failed = generate_result(models, answer, message)
    if is_failed:
        return res, keyword
    else:
        return res, None


async def process_user(user_id: str, room_id: str, rdb) -> Tuple[str, str]:
    user_data = json.dumps({'room_id': room_id, 'user_id': user_id})
    max_idx = await rdb.get(room_id)
    received_data = await rdb.get(user_data)

    if not received_data:
        counter = "1"
        recommend = f"Опрос для {user_id} завершен. Темы рекомендаций:"
    else:
        received_data = json.loads(received_data)
        counter = received_data['counter']
        recommend = received_data['recommend']

    result = int(counter) + 1
    result_data = json.dumps({'counter': result, 'recommend': recommend})

    if int(counter) <= int(max_idx):
        await rdb.set(user_data, result_data)

    return counter, max_idx


async def process_recommend(user_id: str, room_id: str, new_recommend: str, rdb) -> None:
    user_data = json.dumps({'room_id': room_id, 'user_id': user_id})
    received_data = await rdb.get(user_data)
    received_data = json.loads(received_data)
    recommend = f"{received_data['recommend']} {new_recommend},"
    result_data = json.dumps({'counter': received_data['counter'], 'recommend': recommend})
    await rdb.set(user_data, result_data)


async def process_message(user_id: str, room_id: str, message: str, models, rdb) -> Tuple[str, str]:
    count, max_idx = await process_user(user_id, room_id, rdb)
    idx = int(count)-1
    result = await process_answer(models, int(room_id), idx, message)
    if result[1]:
        await process_recommend(user_id=user_id, room_id=room_id, new_recommend=result[1], rdb=rdb)
    if result[0]:
        msg = result[0]
    else:
        msg = f"Начало опроса для {user_id}"
    if int(count) == int(max_idx):
        user_data = json.dumps({'room_id': room_id, 'user_id': user_id})
        received_data = await rdb.get(user_data)
        recommend = json.loads(received_data)['recommend']
        poll_id = await create_poll(id_room=int(room_id), result=recommend, user_id=user_id)
        final_recommend = recommend + f"Номер Вашего результата: {poll_id}"
        return msg, final_recommend
    elif int(count) > int(max_idx):
        return "after last q", "filler"
    else:
        question = await get_question(int(room_id), int(count))
        if question:
            return msg, question
        else:
            return msg, "ошибка получения вопроса"
