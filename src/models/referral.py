import os, sys
sys.path.append(os.getcwd())

from sqlalchemy.types import INTEGER, BIGINT, FLOAT 
from sqlalchemy import Column, ForeignKey, select, update

from src.configs.config import INFLUENCER_TYPE 
from src.configs.logging import easy_error_handler
from src.db.db import session_scope
from src.models.base import Base



class Referral(Base):

    __tablename__ ='referrals'
    id = Column(INTEGER, autoincrement=True, primary_key=True)
    influencer_id = Column(BIGINT, ForeignKey('users.uid'))
    referral_id = Column(BIGINT, ForeignKey('users.uid'))
    influencer_percent = Column(FLOAT)
    referral_percent = Column(FLOAT)
    

    def __init__(self, influencer_id: int, referral_id: int, influencer_percent: float, referral_percent: float) -> None:
        self.influencer_id = influencer_id
        self.referral_id = referral_id
        self.influencer_percent = influencer_percent
        self.referral_percent = referral_percent
    
    def __repr__(self):
        return '<%s(id=%s, influencer_id=%s, referral_id=%s, influencer_percent=%s, referral_percent=%s)>' %(
            self.__class__.__name__, self.id, self.influencer_id, self.referral_id, self.influencer_percent, self.referral_percent
        )


    @classmethod
    @easy_error_handler
    async def get_data(cls, influencer_id: int=None, referral_id: int=None) -> list[object | None]:
        '''Получение данных с таблицы '''

        async with session_scope() as async_session:
            query = None
            if not any([influencer_id, referral_id]):
                query = select(cls)
            elif all([influencer_id, referral_id]):
                query = select(cls).where(cls.influencer_id==influencer_id, cls.referral_id==referral_id)
            elif influencer_id:
                query = select(cls).where(cls.influencer_id==influencer_id)
            elif referral_id:
                query = select(cls).where(cls.referral_id==referral_id)
            
            if query:
                referrals = await async_session.execute(query)
                referrals = [result[0] for result in referrals.all()]
                return referrals
            return []
            
        
    @classmethod
    @easy_error_handler
    async def add_data(cls, influencer_id: int, referral_id: int, influencer_type: int) -> object:
        '''Добавление данных с таблицы '''

        async with session_scope() as async_session:
            new_referral = Referral(influencer_id, 
                                    referral_id,
                                    INFLUENCER_TYPE[influencer_type]['influencer'], 
                                    INFLUENCER_TYPE[influencer_type]['referral']
            )
            async_session.add(new_referral)
            return new_referral
    

    @easy_error_handler
    async def update(self, influencer_percent: float=None, referral_percent: float=None) -> None:
        '''Обновление сущности в таблице '''

        async with session_scope() as async_session:
            if influencer_percent is not None:
                await async_session.execute(
                    update(Referral)
                    .where(Referral.id == self.id)
                    .values(influencer_percent=influencer_percent)
                )
            elif referral_percent is not None:
                await async_session.execute(
                    update(Referral)
                    .where(Referral.id == self.id)
                    .values(referral_percent=referral_percent)
                )