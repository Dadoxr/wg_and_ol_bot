import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
GOOGLE_SHEET_NAME = os.getenv('GOOGLE_SHEET_NAME')

ADMIN_ID = os.getenv('ADMIN_ID')
HELP_CHAT_ID = os.getenv('HELP_CHAT_ID')
TELEGRAPH_TOKEN = os.getenv('TELEGRAPH_TOKEN')

WG_SERVER_RUS_LINK = os.getenv('WG_SERVER_RUS_LINK')
WG_SERVER_NETH_LINK = os.getenv('WG_SERVER_NETH_LINK')
WG_SERVER_SUDO_PASSWD = os.getenv('WG_SERVER_SUDO_PASSWD')
WG_SERVER_API_NAME = os.getenv('WG_SERVER_API_NAME')
WG_SERVER_API_PASSWD = os.getenv('WG_SERVER_API_PASSWD')

OUTLINE_SERVER_RUS_LINK = os.getenv('OUTLINE_SERVER_RUS_LINK')
OUTLINE_SERVER_NETH_LINK = os.getenv('OUTLINE_SERVER_NETH_LINK')


# DB_USER = os.getenv('SERVER_DB_USER')
# DB_PASSWD = os.getenv('SERVER_DB_PASSWD')
# DB_HOST = os.getenv('SERVER_DB_HOST')
# DB_PORT = os.getenv('SERVER_DB_PORT')
# DB_NAME = os.getenv('SERVER_DB_NAME')
# SERVICE_NAME = os.getenv('SERVER_SERVICE_NAME')
# BOT_USERNAME = os.getenv('SERVER_USERNAME') 
# BOT_API_TOKEN = os.getenv('SERVER_API_TOKEN')
# YOOKASSA_SHOPID = os.getenv('YOOKASSA_SHOPID')
# YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY')
# TELEGRAPH_TOKEN = os.getenv('SERVER_TELEGRAPH_TOKEN')


DB_USER = os.getenv('LOCAL_DB_USER')
DB_PASSWD = os.getenv('LOCAL_DB_PASSWD')
DB_HOST = os.getenv('LOCAL_DB_HOST')
DB_PORT = os.getenv('LOCAL_DB_PORT')
DB_NAME = os.getenv('LOCAL_DB_NAME_NEW')
SERVICE_NAME = os.getenv('TEST_SERVICE_NAME')
BOT_USERNAME = os.getenv('TEST_USERNAME') 
BOT_API_TOKEN = os.getenv('TEST_API_TOKEN')
YOOKASSA_SHOPID = os.getenv('YOOKASSA_TEST_SHOPID')
YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_TEST_SECRET_KEY')
TELEGRAPH_TOKEN = os.getenv('TEST_TELEGRAPH_TOKEN')

INSTAGRAM_LINK = os.getenv('INSTAGRAM_LINK')
CHANNEL_USERNAME = os.getenv('TELEGRAM_CHANNEL_USERNAME')

DATABASE_URI = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
ENCRYPT_KEY = os.getenv('ENCRYPT_KEY')


#ПЕРЕМЕННЫЕ В ПОДПИСКЕ
COUNTRY1 = 'Россия'
COUNTRY2 = 'Нидерланды'

#ставится лимит когда subscription сегодня 
VOLUMELIMIT = '10' 

#стоимость за 1 день в рублях
SUBSCRIPTIONCOUST = int(os.getenv('SUBSCRIPTIONCOUST')) 

#период подписки в днях
SUBSCRIPTIONTIME1 = int(os.getenv('SUBSCRIPTIONTIME1')) 
SUBSCRIPTIONTIME2 = int(os.getenv('SUBSCRIPTIONTIME2')) 
SUBSCRIPTIONTIME3 = int(os.getenv('SUBSCRIPTIONTIME3')) 
SUBSCRIPTIONTIME4 = int(os.getenv('SUBSCRIPTIONTIME4')) 

#скидка за период
SUBSCRIPTIONDISCOUNT1 = float(os.getenv('SUBSCRIPTIONDISCOUNT1')) 
SUBSCRIPTIONDISCOUNT2 = float(os.getenv('SUBSCRIPTIONDISCOUNT2')) 
SUBSCRIPTIONDISCOUNT3 = float(os.getenv('SUBSCRIPTIONDISCOUNT3')) 
SUBSCRIPTIONDISCOUNT4 = float(os.getenv('SUBSCRIPTIONDISCOUNT4')) 

ONE_MONTH_COST = round(SUBSCRIPTIONCOUST*SUBSCRIPTIONTIME1*SUBSCRIPTIONDISCOUNT1)
TREE_MONTH_COST = round(SUBSCRIPTIONCOUST*SUBSCRIPTIONTIME2*SUBSCRIPTIONDISCOUNT2)
SIX_MONTH_COST = round(SUBSCRIPTIONCOUST*SUBSCRIPTIONTIME3*SUBSCRIPTIONDISCOUNT3)
TWELVE_MONTH_COST = round(SUBSCRIPTIONCOUST*SUBSCRIPTIONTIME4*SUBSCRIPTIONDISCOUNT4)

PROMOPERIOD = int(os.getenv('PROMOPERIOD'))
REFUNDPERIOD = int(os.getenv('REFUNDPERIOD'))
REFUND_TRAFIC_LIMIT = int(os.getenv('REFUND_TRAFIC_LIMIT'))
CREDITING_CASHBACK_PERIOD = int(os.getenv('CREDITING_CASHBACK_PERIOD'))
REFERRAL_LINK_LIVE = int(os.getenv('REFERRAL_LINK_LIVE'))

USER_CASHBACK1 = float(os.getenv('USER_CASHBACK1'))
USER_CASHBACK2 = float(os.getenv('USER_CASHBACK2'))
USER_CASHBACK3 = float(os.getenv('USER_CASHBACK3'))
USER_CASHBACK4 = float(os.getenv('USER_CASHBACK4'))
INFLUENCER_TYPE = {
    1: {
        'influencer': float(os.getenv('INFLUENCER_TYPE_1_INF')), 
        'referral': float(os.getenv('INFLUENCER_TYPE_1_REF'))
        }, 
    2:{
        'influencer': float(os.getenv('INFLUENCER_TYPE_2_INF')), 
        'referral': float(os.getenv('INFLUENCER_TYPE_2_REF'))
        }
}
VPN_DATA = {
    '1_month': {
        'value': ONE_MONTH_COST, 
        'description': 'Настройка сети. Тариф №1', 
        'user_cashback_amount': USER_CASHBACK1, 
        'subscriptiontime': SUBSCRIPTIONTIME1
    },
    '3_months': {
        'value': TREE_MONTH_COST, 
        'description': 'Настройка сети. Тариф №3', 
        'user_cashback_amount': USER_CASHBACK2, 
        'subscriptiontime': SUBSCRIPTIONTIME2
    },
    '6_months': {
        'value': SIX_MONTH_COST, 
        'description': 'Настройка сети. Тариф №6', 
        'user_cashback_amount': USER_CASHBACK3, 
        'subscriptiontime': SUBSCRIPTIONTIME3
    },
    '12_months': {
        'value': TWELVE_MONTH_COST, 
        'description': 'Настройка сети. Тариф №12', 
        'user_cashback_amount': USER_CASHBACK4, 
        'subscriptiontime': SUBSCRIPTIONTIME4
    }
}

REFUND_COMISSION = float(os.getenv('REFUND_COMISSION'))
FEEDBACK_LINK = os.getenv('FEEDBACK_LINK')

# ОПЛАТА СЕРВИСА
COMISSION = float(os.getenv('COMISSION'))
CURRENCY_URL = 'https://www.cbr.ru/currency_base/daily/'
MIN_AMOUNT = float(os.getenv('MIN_AMOUNT'))

MAIN_ABOUT_US_TEXT = os.getenv('MAIN_ABOUT_US_TEXT')