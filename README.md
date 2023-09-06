# Бот формирует ключи доступа к WireGuard после оплаты

## Асинхронный бот, написанный на [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) и [PostgreSQL](https://github.com/postgres/postgres) с использованием [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) на движке [Asyncpg](https://magicstack.github.io/asyncpg/current) и подключенным к API [QIWI](https://developer.qiwi.com/ru/p2p-payments/#p2p-) и [Yookassa](https://yookassa.ru/developers) + серверам с настроенным [WireGuard](https://www.wireguard.com/install/) и [OutlineVPN](https://getoutline.org/ru/) c выгрузкой отчетов в [Google Sheets](https://developers.google.com/sheets/api/quickstart/python?hl=ru)

1) VPN без необходимости отключения
2) Оплата любых сервисов

# Базовые команды

## Кнопка "Start"

- Выводит приветственное сообщение, включая информацию о канале, инструкции и доступные возможности.

## Кнопка "Subscribe (VPN)"

- Отображает информацию о подписке пользователя на VPN-сервис и предлагает варианты для приобретения или создания ключа VPN.

  - Подкнопки "period_..."
    - Предоставляют пользователю выбор периода подписки (7 дней бесплатно и 1, 3, 6 или 12 месяцев).

## Кнопка "Pay Service"

- Выводит информацию о платных сервисах, включая описание, возможности и стоимость.

## Кнопка "Issue Card"

- Позволяет пользователю запросить сервисы и указать сумму.

## Кнопки "Connect VPN (Russian)" и "Connect VPN (Non-Russian)"

- Позволяют пользователю подключить VPN с конфигурациями для Российских и иностранных ресурсов соответственно. Включает инструкции для использования VPN.

## Кнопка "Bonuses"

- Отображает меню с вариантами действующих бонусов.

  - Подкнопка "Free for Advertisement"
    - Предоставляет бесплатное использование услуги в обмен на участие в рекламной активности.

## Кнопка "My Cabinet"

- Предоставляет информацию о пользователе и доступ к следующим подкомандам:

  - Подкнопка "My Configs"
    - Позволяет пользователю просматривать и управлять своими конфигурациями.

  - Подкнопка "Withdraw"
    - Предоставляет функциональность для вывода средств.

## Кнопка "Influencer Account"

- Предоставляет информацию о счете пользователя и ожидаемом приходе средств.

  - Подкнопка "Influencer Statistics"
    - Выводит статистику о рефералах, включая общее количество, количество за последние 3 месяца, активные пробные и активные подписки, а также заработанную сумму.

  - Подкнопка "Free for Advertisement"
    - Предоставляет возможность заработать бесплатное использование услуги в обмен на участие в рекламной активности.

  - Подкнопка "Get Referral Link"
    - Позволяет пользователю получить действующую или создать новую реферральную ссылку. После создания новой ссылки, пользователю предоставляется возможность предоставить канал, фотографии и видео для поста, и ссылку после модерации.

  - Подкнопка "Withdraw"
    - Предоставляет функциональность для вывода средств.

  - Подкнопка "Change Earning Type"
    - Позволяет пользователю изменить тип заработка (например, 20/10 или 30/0).

## Кнопка "Info"

- Предоставляет различную информацию, включая разделы:

  - Подкнопка "FAQ"
    - Содержит регламент защиты данных, политику конфиденциальности, информацию о сборе и использовании данных, скорости VPN и восстановлении доступа.

  - Подкнопка "Feedback"
    - Предоставляет отзывы.

  - Подкнопка "Instructions Pay Service"
    - Содержит информацию о платных сервисах, включая описание, возможности и стоимость.

  - Подкнопка "Instructions VPN"
    - Содержит инструкции, доступные для пользователей с подпиской, включая:

    - Подкнопка "Install to WireGuard"
      - Предоставляет настройки WireGuard.

    - Подкнопка "Phone Settings"
      - Предоставляет настройки телефона для решения возможных проблем.

## Кнопка "Help"

- Предоставляет информацию о текущем состоянии общения с менеджером и доступ к следующим подкомандам:

  - Подкнопка "Refund"
    - Предоставляет информацию о возможности возврата.

  - Подкнопка "Say About Problems"
    - Предоставляет возможность описать проблему или сложности, с которыми столкнулся пользователь.



# Зависимости
```python
pip install bs4 asyncpg aiohttp gspread gspread-dataframe pandas outline-vpn-api python-dotenv python-telegram-bot SQLAlchemy yookassa
```


# База данных

1)**users**

``` python
__tablename__ = 'users'
uid = Column(BIGINT, primary_key=True)
username = Column(TEXT)
fullname = Column(TEXT)
begin_date = Column(TIMESTAMP)
amount_now = Column(INTEGER)
total_earned = Column(INTEGER)
is_influencer = Column(BOOLEAN)
is_admin = Column(BOOLEAN)
```

2)**subscriptions**

``` python
__tablename__ ='subscriptions'
uid = Column(BIGINT, ForeignKey('users.uid'), primary_key=True)
last_payment_id = Column(TEXT, ForeignKey('payments.id'))
subscription_begin = Column(TIMESTAMP, default=datetime.now())
subscription_end = Column(TIMESTAMP)
```

3)**payments**

``` python
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
```

4)**referals**

``` python
__tablename__ ='referrals'
id = Column(INTEGER, autoincrement=True, primary_key=True)
influencer_id = Column(BIGINT, ForeignKey('users.uid'))
referral_id = Column(BIGINT, ForeignKey('users.uid'))
influencer_percent = Column(FLOAT)
referral_percent = Column(FLOAT)
```

5)**vpn_configs**

``` python
__tablename__ = 'vpn_configs'
id = Column(Integer, primary_key=True, autoincrement=True)
uid = Column(BIGINT, ForeignKey('users.uid'))
wg_rus_config = Column(TEXT)
wg_neth_config = Column(TEXT)
outline_rus_config = Column(TEXT)
outline_neth_config = Column(TEXT)
is_blocked = Column(BOOLEAN)
```

6)**cards**

``` python
__tablename__ = 'cards'
id = Column(INTEGER, autoincrement=True, primary_key=True)
uid = Column(BIGINT, ForeignKey('users.uid'))
payment_id = Column(TEXT, ForeignKey('payments.id'))
services = Column(TEXT)
amount_usd = Column(FLOAT)
details = Column(TEXT)
```


# Переменные окружения .env

- **API**
  - WG_SERVER_API_NAME
  - WG_SERVER_API_PASSWD
  - GOOGLE_SHEETS_CREDENTIALS
  - GOOGLE_SHEET_NAME
  - YOOKASSA_SHOPID
  - YOOKASSA_SECRET_KEY

- **DB**
  - DB_USER
  - DB_PASSWD
  - DB_HOST
  - DB_PORT
  - DB_NAME

- **Server Outline & WireGuard**
  - WG_SERVER_RUS_LINK
  - WG_SERVER_NETH_LINK
  - WG_SERVER_SUDO_PASSWD
  - OUTLINE_SERVER_RUS_LINK
  - OUTLINE_SERVER_NETH_LINK

- **Bot info**
  - ADMIN_ID
  - SERVICE_NAME
  - BOT_USERNAME
  - BOT_API_TOKEN
  - INSTAGRAM_LINK
  - CHANNEL_USERNAME 
  - FEEDBACK_LINK

- **Различные коэффициенты**
ENCRYPT_KEY, SUBSCRIPTIONCOUST, SUBSCRIPTIONTIME1, SUBSCRIPTIONTIME2,SUBSCRIPTIONTIME3, SUBSCRIPTIONTIME4, SUBSCRIPTIONDISCOUNT1, SUBSCRIPTIONDISCOUNT2, SUBSCRIPTIONDISCOUNT3, SUBSCRIPTIONDISCOUNT4, PROMOPERIOD, REFUNDPERIOD, REFUND_TRAFIC_LIMIT, CREDITING_CASHBACK_PERIOD, USER_CASHBACK1, USER_CASHBACK2, USER_CASHBACK3, USER_CASHBACK4, REFUND_COMISSION, COMISSION, MIN_AMOUNT


# Запуск 

Для запуска бота, запустите файл main.py. Убедитесь, что все зависимости установлены, переменные окружения заполнены, таблицы созданы и настроены правильно перед запуском приложения.


# Примечание

Вам так же необходимо установить на сервера OutlineVPN server и Wireguard server, настроить переадресацию и создать api для подключения бота к серверу