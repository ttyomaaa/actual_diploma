import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Context(Base):
    __tablename__ = 'context'

    id_context = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    context = Column(String, nullable=False)
    id_room = Column(Integer, ForeignKey('room.id_room'), nullable=False)

    room = relationship('Room', back_populates='contexts')
    questions = relationship('Question', back_populates='context', lazy="selectin")


class Question(Base):
    __tablename__ = 'question'

    id_question = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    id_context = Column(Integer, ForeignKey('context.id_context'))
    q_number = Column(Integer, nullable=False)
    q_file = Column(String(1000), unique=False, nullable=True)
    question = Column(String(1000), unique=False, nullable=False)

    answer = relationship('Answer', back_populates='question', lazy="selectin")
    keyword = relationship('Keyword', back_populates='question', lazy="selectin")
    context = relationship('Context', back_populates='questions', lazy="selectin")


class Answer(Base):
    __tablename__ = 'answer'

    id_answer = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    id_context = Column(Integer, ForeignKey('context.id_context'))
    id_question = Column(Integer, ForeignKey('question.id_question'))
    answer = Column(String(1000), nullable=False)

    question = relationship('Question', back_populates='answer', lazy="selectin")


class Keyword(Base):
    __tablename__ = 'keyword'

    id_keyword = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    id_context = Column(Integer, ForeignKey('context.id_context'))
    id_question = Column(Integer, ForeignKey('question.id_question'))
    keyword = Column(String(1000), nullable=False)

    question = relationship('Question', back_populates='keyword', lazy="selectin")


class Room(Base):
    __tablename__ = 'room'

    id_room = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    published_by = Column(String(1000), nullable=False)
    created_on = Column(DateTime(), default=datetime.datetime.utcnow())

    contexts = relationship('Context', lazy="selectin")


class Poll(Base):
    __tablename__ = 'poll'

    id_poll = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    id_room = Column(Integer, ForeignKey('room.id_room'), nullable=False)
    created_on = Column(DateTime(), default=datetime.datetime.utcnow())
    result = Column(String, nullable=False)
    username = Column(String(1000), nullable=False)

