import asyncio
from db.engine import async_session
from sqlalchemy import select, column
from sqlalchemy.orm import joinedload
from db.models.models import Room, Question, Context, Answer, Keyword
from typing import Union


async def check_tables(room_id: int = 0):
    async with async_session() as session:
        stmt = select(Question).join(Context).join(Room).where(Room.id_room == room_id).options(joinedload(Question.answer))  # type: ignore
        result = await session.execute(stmt)
        questions = result.unique().scalars().all()

        for question in questions:
            print(str(question.q_number) + question.question)
            for answer in question.answer:
                print(answer.answer)


# async def check_answers(room_id: int = 0, number_q: int = 0):
#     async with async_session() as session:
#         stmt = (select(Answer, Keyword)
#                 .join(Question, Answer.id_question == Question.id_question)
#                 .join(Context, Question.id_context == Context.id_context)
#                 .join(Room, Context.id_room == Room.id_room)
#                 .join(Keyword, Question.id_question == Keyword.id_question)
#                 .where(Room.id_room == room_id, Question.q_number == number_q)  # type: ignore
#                 )
#         result = await session.execute(stmt)
#         answer_keyword = result.unique().first()
#         if answer_keyword:
#             answer, keyword = answer_keyword

# asyncio.run(check_answers())
