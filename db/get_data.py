from db.engine import async_session
from sqlalchemy import select
from db.models.models import Room, Question, Context, Answer, Keyword
from typing import Union, Tuple


async def get_question(room_id: int = 0, q_number: int = 0) -> Union[str, None]:
    async with async_session() as session:
        stmt = (select(Question)
                .join(Context)
                .join(Room)
                .where(Room.id_room == room_id)  # type: ignore
                .where(Question.q_number == q_number)  # type: ignore
                )
        result = await session.execute(stmt)
        question = result.unique().scalars().first()
        if question:
            return f"{question.q_number}. {question.question}"


async def get_answer_keyword(room_id: int = 0, number_q: int = 0) -> Union[Tuple[str, str], None]:
    async with async_session() as session:
        stmt = (select(Answer, Keyword)
                .join(Question, Answer.id_question == Question.id_question)
                .join(Context, Question.id_context == Context.id_context)
                .join(Room, Context.id_room == Room.id_room)
                .join(Keyword, Question.id_question == Keyword.id_question)
                .where(Room.id_room == room_id, Question.q_number == number_q)  # type: ignore
                )
        result = await session.execute(stmt)
        answer_keyword = result.unique().first()
        if answer_keyword:
            answer, keyword = answer_keyword
            return answer.answer, keyword.keyword
