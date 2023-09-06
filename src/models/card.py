import os, sys
sys.path.append(os.getcwd())

from sqlalchemy.types import INTEGER, BIGINT, TEXT, FLOAT 
from sqlalchemy import Column, ForeignKey, select, update

from src.configs.logging import easy_error_handler
from src.db.db import session_scope
from src.models.base import Base


class Card(Base):

    __tablename__ = 'cards'
    id = Column(INTEGER, autoincrement=True, primary_key=True)
    uid = Column(BIGINT, ForeignKey('users.uid'))
    payment_id = Column(TEXT, ForeignKey('payments.id'))
    services = Column(TEXT)
    amount_usd = Column(FLOAT)
    details = Column(TEXT)


    def __init__(self, uid: int, payment_id: str, services: str, amount_usd: float, details: str=None) -> None:
        self.uid = uid
        self.payment_id = payment_id
        self.services = services
        self.amount_usd = float(amount_usd)
        self.details = details
    

    def __repr__(self) -> str:
        return '<%s(id=%s, uid=%s, payment_id=%s, services=%s, amount_usd=%s details=%s)>' % (
            self.__class__.__name__, self.id, self.uid, self.payment_id, self.services, self.amount_usd, self.details)


    @classmethod
    @easy_error_handler
    async def get_data(cls, uid: int=None, payment_id: int=None) -> list[object | None]:
        '''Получение данных с таблицы '''

        async with session_scope() as async_session:
            query = None
            if not any([uid, payment_id]):
                query = select(cls)
            elif all([uid, payment_id]):
                query = select(cls).where(cls.uid==uid, cls.payment_id==payment_id)
            elif uid:
                query = select(cls).where(cls.uid==uid)
            elif payment_id:
                query = select(cls).where(cls.payment_id==payment_id)
            
            if query:
                cards = await async_session.execute(query)
                cards_list = [result[0] for result in cards.all()]
                return cards_list
            return []
        

    @classmethod
    @easy_error_handler
    async def add_data(cls, uid: int, payment_id: int, services: str, amount_to_card: str) -> object:
        '''Добавление данных с таблицы '''
        
        async with session_scope() as async_session:
            new_card = cls(uid, payment_id, services, amount_to_card)
            async_session.add(new_card)
            return new_card
    

    @easy_error_handler
    async def update(self, details: str=None) -> None:
        '''Обновление сущности в таблице '''

        async with session_scope() as async_session:
            if details is not None:
                await async_session.execute(
                    update(Card)
                    .where(Card.uid == self.uid)
                    .values(details=details)
                )