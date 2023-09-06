import os, sys
sys.path.append(os.getcwd())

from datetime import datetime
from sqlalchemy.types import BIGINT, TEXT, TIMESTAMP
from sqlalchemy import Column, ForeignKey, select, update

from src.configs.logging import easy_error_handler
from src.db.db import session_scope
from src.models.base import Base


class Subscription(Base):

    __tablename__ ='subscriptions'
    uid = Column(BIGINT, ForeignKey('users.uid'), primary_key=True)
    last_payment_id = Column(TEXT, ForeignKey('payments.id'))
    subscription_begin = Column(TIMESTAMP, default=datetime.now())
    subscription_end = Column(TIMESTAMP)

    def __init__(self, uid: int, last_payment_id: int, subscription_begin: datetime, subscription_end: datetime) -> None:
        self.uid = uid
        self.last_payment_id = last_payment_id
        self.subscription_begin = subscription_begin
        self.subscription_end = subscription_end
    

    def __repr__(self):
        return '<%s(uid=%s, last_payment_id=%s, subscription_begin=%s, subscription_end=%s)>' % (
            self.__class__.__name__, self.uid, self.last_payment_id, self.subscription_begin, self.subscription_end
        )
 
    @classmethod
    @easy_error_handler
    async def get_data(cls, uid: int=None) -> list[object | None]:
        '''Получение данных с таблицы '''

        async with session_scope() as async_session:
            query = None
            if not uid:
                query = select(cls)
            elif uid:
                query = select(cls).where(cls.uid==uid)
            
            if query:
                subscribtion = await async_session.execute(query)
                subscribtion = [result[0] for result in subscribtion.all()]
                return subscribtion
            return []
        

    @classmethod
    @easy_error_handler
    async def add_data(cls, uid: int, last_payment_id: int, subscription_begin: datetime, subscription_end: datetime) -> object:
        '''Добавление данных с таблицы '''

        async with session_scope() as async_session:
            new_subscription = cls(uid, last_payment_id, subscription_begin, subscription_end) 
            async_session.add(new_subscription)
            return new_subscription


    @easy_error_handler
    async def update(self, last_payment_id: int=None, subscription_begin: datetime=None, subscription_end: datetime=None) -> None:
        '''Обновление сущности в таблице '''

        async with session_scope() as async_session:
            if last_payment_id is not None:
                await async_session.execute(
                    update(Subscription)
                    .where(Subscription.uid == self.uid)
                    .values(last_payment_id=last_payment_id)
                )
            elif subscription_begin is not None:
                await async_session.execute(
                    update(Subscription)
                    .where(Subscription.uid == self.uid)
                    .values(subscription_begin=subscription_begin)
                )
            elif subscription_end is not None:
                await async_session.execute(
                    update(Subscription)
                    .where(Subscription.uid == self.uid)
                    .values(subscription_end=subscription_end)
                )