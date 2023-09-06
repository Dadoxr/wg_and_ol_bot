import os, sys
sys.path.append(os.getcwd())

from datetime import datetime, timedelta
from sqlalchemy import and_, func, select

from src.configs.config import PROMOPERIOD 
from src.configs.logging import easy_error_handler
from src.db.db import session_scope
from src.models.payment import Payment
from src.models.referral import Referral
from src.models.subscription import Subscription
from src.models.user import User


@easy_error_handler
async def get_promo_active(uid: int) -> list[object]:
    '''Возвращает список пользователей с активным промо периодом'''

    async with session_scope() as async_session:
        users = await async_session.execute(select(Referral).join(
            Subscription, Referral.referral_id == Subscription.uid).where(
                Referral.influencer_id == uid,
                Subscription.subscription_end - Subscription.subscription_begin == timedelta(days=PROMOPERIOD),
                Subscription.subscription_end >= datetime.now(),
                Subscription.subscription_begin <= datetime.now()
            )
        )
        users = [result[0] for result in users.all()]
        return users


@easy_error_handler
async def get_subscription_active(uid: int) -> list[object]:
    '''Возвращает список пользователей с активной подпиской'''

    async with session_scope() as async_session:
        users = await async_session.execute(select(Referral).join(
            Subscription, Referral.referral_id == Subscription.uid).where(
                Referral.influencer_id == uid,
                Subscription.subscription_end - Subscription.subscription_begin > timedelta(days=PROMOPERIOD),
                Subscription.subscription_end >= datetime.now(),
                Subscription.subscription_begin <= datetime.now()
            )
        )
        users = [result[0] for result in users.all()]
        return users


@easy_error_handler
async def get_entered(uid: int, date_one: datetime, date_two: datetime) -> list[object]:
    '''Возвращает список пользователей которые подключились в определнный пероид'''

    async with session_scope() as async_session:
        users = await async_session.execute(select(User).join(
            Referral, User.uid == Referral.referral_id).where(
                Referral.influencer_id == uid, User.begin_date >= date_one, User.begin_date < date_two
            )
        )
        users = [result[0] for result in users.all()]
    return users


@easy_error_handler
async def get_sum_influencer_amount(influencer_id: int) -> int:
    '''Возвращает сумму "заработанного в ожидании" у инфлюенсера'''

    async with session_scope() as async_session:
        referrals = await async_session.execute(select(Payment).join(
            Referral, Payment.uid == Referral.referral_id).where(
                Referral.influencer_id == influencer_id
            )
        )
        referrals = [result[0] for result in referrals.all()] if referrals else []
        sum_influencer_amount = sum((x.influencer_amount for x in referrals), 0)

        return sum_influencer_amount


@easy_error_handler
async def get_influencers_data_from_table() -> object:
    '''Заполняет данные в Google Sheet данных по инфлюенсерам'''
    
    async with session_scope() as async_session:

        promo_result = await async_session.execute(
            select(func.count().label("promo"))
            .select_from(User).join(Subscription, User.uid == Subscription.uid).where(
            func.extract('days', Subscription.subscription_end - Subscription.subscription_begin) == PROMOPERIOD))

        sub_result = await async_session.execute(
            select(func.count().label("sub"))
            .select_from(User).join(Subscription, User.uid == Subscription.uid)
            .where(
                and_(func.extract('days', Subscription.subscription_end - Subscription.subscription_begin) > PROMOPERIOD, 
                    Subscription.subscription_end > datetime.now())))
 
        promo = promo_result.all()
        sub = sub_result.all()

        result = await async_session.execute(
            select(
                User.uid,
                User.username,
                User.fullname,
                func.count(Referral.referral_id).label("referrals"),
                promo.label("promo"),
                sub.label("sub"),
                (promo * 100 / func.count(Referral.referral_id)).label("enter_to_promo_ratio"),
                (sub * 100 / func.count(Referral.referral_id)).label("enter_to_sub_ratio")
            )
            .select_from(User.join(Referral, User.uid == Referral.influencer_id))
            .group_by(User.uid, User.username, User.fullname, promo, sub)
        )
        data = result.all()
        
        headers_result =  await async_session.execute(
            select(
                *[getattr(User, column_name) for column_name in User.__table__.c.keys()],
                func.count(Referral.referral_id).label("referrals"),
                promo.label("promo"),
                sub.label("sub"),
                (promo * 100 / func.count(Referral.referral_id)).label("enter_to_promo_ratio"),
                (sub * 100 / func.count(Referral.referral_id)).label("enter_to_sub_ratio")
            )
            .select_from(User.join(Referral, User.uid == Referral.influencer_id))
            .group_by(*[getattr(User, column_name) for column_name in User.__table__.c.keys()], promo, sub)
        )
        headers = headers_result.all()
        
        return headers, data
    
