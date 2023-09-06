import os, sys
sys.path.append(os.getcwd())

from datetime import datetime
from sqlalchemy.types import INTEGER, BIGINT, TEXT, TIMESTAMP, BOOLEAN
from sqlalchemy import Column, select

from src.configs.logging import easy_error_handler
from src.db.db import session_scope
from src.models.base import Base


class User(Base):

    __tablename__ = 'users'
    uid = Column(BIGINT, primary_key=True)
    username = Column(TEXT)
    fullname = Column(TEXT)
    begin_date = Column(TIMESTAMP)
    amount_now = Column(INTEGER)
    total_earned = Column(INTEGER)
    is_influencer = Column(BOOLEAN)
    is_admin = Column(BOOLEAN)

    def __init__(self, uid: int, username: str, first_name: str, last_name: str, 
                  amount_now=0, total_earned=0, is_influencer=False, is_admin=False, begin_date=datetime.now()) -> None:
        
        self.uid = uid
        self.username = username
        fullname = f'{first_name if first_name is not None else ""} {last_name if last_name is not None else ""}'
        self.fullname = fullname if fullname != '' else None
        self.begin_date = begin_date
        self.amount_now = amount_now
        self.total_earned = total_earned
        self.is_influencer = is_influencer
        self.is_admin = is_admin


    def __repr__(self) -> str:
        return '<%s(uid=%s, username=%s, fullname=%s, begin_date=%s, amount_now=%s, total_earned=%s, is_influencer=%s, is_admin=%s)>' % (
            self.__class__.__name__, self.uid, self.username, self.fullname, self.begin_date, self.amount_now, self.total_earned, self.is_influencer, self.is_admin)
        

    @classmethod
    @easy_error_handler
    async def get_data(cls, uid: int=None, is_influencer: bool=None) -> list[object | None]:
        '''Получение данных с таблицы '''

        async with session_scope() as async_session:
            query = None
            if not any([uid is not None, is_influencer is not None]):
                query = select(cls)
            elif all([uid is not None, is_influencer is not None]):
                query = select(cls).where(cls.uid==uid, cls.is_influencer==is_influencer)
            elif uid is not None:
                query = select(cls).where(cls.uid==uid)
            elif is_influencer is not None:
                query = select(cls).where(cls.is_influencer==is_influencer)
            
            if query:
                users = await async_session.execute(query) 
                users = [result[0] for result in users.all()]
                return users
            return []
        

    @classmethod
    @easy_error_handler
    async def add_data(cls, uid: int, username: str, first_name='', last_name='') -> object:
        '''Добавление данных с таблицы '''

        async with session_scope() as async_session:
            new_user = cls(uid, username, first_name, last_name) 
            async_session.add(new_user)
            return new_user




