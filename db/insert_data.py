from db.engine import async_session
from db.models.models import Room, Context, Question, Answer, Keyword
from typing import List


def generate_data(models, context: str):
    poll = []
    key_output = models["keyword"](context, top_p=1.0, max_length=64)
    questions = models["question"](context)
    for question in questions:
        answer = models["answer"]({"context": context, "question": question})
        tmp_dict = {"question": question, "answer": answer, "key": key_output}
        poll.append(tmp_dict)
    return poll


async def create_room(models, published_by: str, contexts: List[str]):
    result_poll = []
    async with async_session() as session:
        room = Room(published_by=published_by)
        session.add(room)
        await session.flush()
        for text in contexts:
            context = Context(context=text, id_room=room.id_room)
            session.add(context)
            await session.flush()
            poll = generate_data(models, text)
            poll = [{**p, "context_id": context.id_context} for p in poll]
            result_poll += poll
        for idx, item in enumerate(result_poll, start=1):
            question = Question(id_context=item["context_id"], q_number=idx, question=item["question"])
            session.add(question)
            await session.flush()
            answer = Answer(id_context=item["context_id"], id_question=question.id_question, answer=item["answer"])
            session.add(answer)
            keyword = Keyword(id_context=item["context_id"], id_question=question.id_question, keyword=item["key"])
            session.add(keyword)
        await session.commit()
    return room.id_room, idx
