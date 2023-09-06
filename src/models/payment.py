import os, sys, yookassa, uuid
sys.path.append(os.getcwd())

from sqlalchemy.types import INTEGER, BIGINT, TEXT, TIMESTAMP
from sqlalchemy import Column, ForeignKey, select, update
from datetime import datetime

from src.configs.config import VPN_DATA, COMISSION, BOT_USERNAME, REFUND_COMISSION 
from src.configs.kb import make_pay_kb, easy_error_handler
from src.configs.utils import get_user_from_all, get_usd_to_rub_rate
from src.db.db import session_scope
from src.models.base import Base


class Payment(Base):

    __tablename__ = 'payments'
    id = Column(TEXT, primary_key=True)
    uid = Column(BIGINT, ForeignKey('users.uid'))
    type = Column(TEXT)
    pay_sum = Column(INTEGER)
    status = Column(TEXT)
    pay_date = Column(TIMESTAMP)
    user_cashback_amount = Column(INTEGER)
    influencer_amount = Column(INTEGER)
    refund_id = Column(TEXT)
    refund_reason = Column(TEXT)


    def __init__(self, id: str, uid: int, type: str, pay_sum: int, status: str, 
                pay_date=datetime.now(), user_cashback_amount=0, influencer_amount=0, refund_id=None, refund_reason=None) -> None:
        self.id = id
        self.uid = uid
        self.type = type
        self.pay_sum = pay_sum
        self.status = status
        self.pay_date = pay_date
        self.user_cashback_amount = user_cashback_amount
        self.influencer_amount = influencer_amount
        self.refund_id = refund_id
        self.refund_reason = refund_reason


    def __repr__(self):
        return "<%s(id=%s, uid=%s, type=%s pay_sum=%s, status=%s, pay_date=%s, \
                    user_cashback_amount=%s, influencer_amount=%s, refund_id=%s, refund_reason=%s)>" % (
                self.__class__.__name__, self.id, self.uid, self.type, self.pay_sum, self.status, 
                self.pay_date, self.user_cashback_amount, self.influencer_amount, self.refund_id, self.refund_reason
            )


    @classmethod
    @easy_error_handler
    async def get_data(cls, uid: int=None, payment_id: int=None, pay_date: datetime=None) -> list[object | None]:
        '''Получение данных с таблицы '''

        async with session_scope() as async_session:
            query = None
            if not any([uid, payment_id]):
                query = select(cls)
            elif all([uid, payment_id]):
                query = select(cls).where(cls.uid==uid, cls.id==payment_id)
            elif all([uid, pay_date]):
                query = select(cls).where(cls.uid==uid, cls.pay_date>pay_date)
            elif uid:
                query = select(cls).where(cls.uid==uid)
            elif payment_id:
                query = select(cls).where(cls.id==payment_id)

            if query:
                payments = await async_session.execute(query)
                payments_list = [result[0] for result in payments.all()]
                return payments_list
            return []
        

    @classmethod
    @easy_error_handler
    async def add_data(cls, payments_id: int, uid: int, payment_type: int, pay_sum: int, status: str) -> object:
        '''Добавление данных с таблицы '''

        async with session_scope() as async_session:
            new_payment = cls(payments_id, uid, payment_type, pay_sum, status)
            async_session.add(new_payment)
            return new_payment


    @classmethod
    @easy_error_handler
    async def produce_payment(cls, update, pay_sum=None) -> object:
        '''Создание платежа и сохранение его в таблице '''

        if update.callback_query:
            payment_type = update.callback_query.data.split('##')[1]
            value = pay_sum or int(VPN_DATA[payment_type]['value'])
            description = VPN_DATA[payment_type]['description']
        else:
            payment_type = 'card'
            currency = await get_usd_to_rub_rate()
            value = pay_sum or int(float(update.effective_message.text) * currency * COMISSION)
            description = 'Оплата сервиса'

        idempotence_key= str(uuid.uuid4())
        payment = yookassa.Payment.create({
            'amount': {'value': value, 'currency': 'RUB'},
            'confirmation': {'type': 'redirect', 'return_url': f't.me/{BOT_USERNAME}'},
            'description': description,
            'capture' : True,
            'receipt': {'customer': {'email': 'customer@mail.ru'}, 
                        'items': [{
                            'description': description,
                            'quantity': 1.00,
                            'amount': {'value': value, 'currency': 'RUB'},
                            'vat_code': '1'
                            }]}}, 
            idempotence_key)
        
        await cls.add_data(payment.id, update.effective_user.id, payment_type, value, payment.status)
        return payment


    @staticmethod
    @easy_error_handler
    async def get_offer(update, context) -> str|object:
        '''Формирование сообщения и клавиатуры в зависимости от наличия amount_now'''

        payment = context.user_data.get('payment')
        amount_to_card = context.user_data.get('amount_to_card', '0')

        zero_account_pay_kb, part_pay_from_account_kb = await make_pay_kb(payment, amount_to_card)
        kb = part_pay_from_account_kb if user.amount_now > 0 else zero_account_pay_kb

        user = await get_user_from_all(update, context)
        text = f'К оплате: {int(payment.amount.value)} руб.\n\nБаланс счета: {user.amount_now} руб.\n\nUSD к RUB по курсу ЦБ'
        
        return text, kb



    @staticmethod
    @easy_error_handler
    async def get_payment_status(payment_id: int) -> object:
        '''Парсинг статуса платежа'''

        payment_status = yookassa.Payment.find_one(payment_id).status
        return payment_status
    

    @staticmethod
    @easy_error_handler
    async def cancel_payment(payment_id: int) -> object:
        '''Инициализирует отмену платежа (для неоплаченных)'''

        idempotence_key = str(uuid.uuid4())
        response = yookassa.Payment.cancel(payment_id, idempotence_key)
        return response
    

    @easy_error_handler
    async def get_refund(self) -> object:
        '''Инициализирует возврат средств'''

        payment = yookassa.Payment.find_one(self.id)
        refund = yookassa.Refund.create({
            'amount': {'value': int(float(payment.amount.value) * (1-REFUND_COMISSION)), 
                       'currency': payment.amount.currency},
            'payment_id': payment.id})
        return refund
    

    @easy_error_handler
    async def update(self, 
                     status: str=None, 
                     user_cashback_amount: int=None, 
                     influencer_amount: int=None, 
                     refund_id: str=None, 
                     refund_reason: str=None
        ) -> None:
        '''Обновление сущности в таблице '''

        async with session_scope() as async_session:
            if status is not None:
                await async_session.execute(
                    update(Payment)
                    .where(Payment.id == self.id)
                    .values(status=status)
                )
            elif user_cashback_amount is not None:
                await async_session.execute(
                    update(Payment)
                    .where(Payment.id == self.id)
                    .values(user_cashback_amount=user_cashback_amount)
                )
            elif influencer_amount is not None:
                await async_session.execute(
                    update(Payment)
                    .where(Payment.id == self.id)
                    .values(influencer_amount=influencer_amount)
                )
            elif refund_id is not None:
                await async_session.execute(
                    update(Payment)
                    .where(Payment.id == self.id)
                    .values(refund_id=refund_id)
                )
            elif refund_reason is not None:
                await async_session.execute(
                    update(Payment)
                    .where(Payment.id == self.id)
                    .values(refund_reason=refund_reason)
                )
            