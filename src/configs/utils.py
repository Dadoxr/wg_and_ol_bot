import sys, os, aiohttp
sys.path.append(os.getcwd())

from base64 import b64decode
from zlib import decompress
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from src.configs.config import *
from src.configs.logging import easy_error_handler, logger
from src.models.user import User
from src.models.referral import Referral


@easy_error_handler
async def add_to_context_user_data(context, *args) -> None:
    '''Добавляет в контект данные '''

    for arg in args:
        if isinstance(arg, tuple):
            variable, value = arg
        else:
            variable, value = arg, None

        if variable:
            if context.user_data.get(variable) is None or context.user_data[variable] != value:
                if value is not None:
                    context.user_data[variable] = value
        else:
            logger.warning(f"Warning: Unrecognized variable '{variable}'")


@easy_error_handler
async def send_message(update, context, text, kb=None) -> None:
    '''Определяет текст ли был или коллбэк и отправляет сообщение'''

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, parse_mode='MARKDOWN', disable_web_page_preview=True,reply_markup=kb)
    else:
        await context.bot.send_message(chat_id=update.effective_user.id, text=text, parse_mode='MARKDOWN', disable_web_page_preview=True, reply_markup=kb)
        

@easy_error_handler
async def get_usd_to_rub_rate() -> float | None:
    ''' Парсинг валюты '''

    async with aiohttp.ClientSession() as session:
        async with session.get(CURRENCY_URL) as response:
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')
            table = soup.find('table', class_='data')
            rows = table.find_all('tr')
            for row in rows:
                columns = row.find_all('td')
                if len(columns) < 5:
                    continue
                if columns[1].text == 'USD':
                    rate = float(columns[4].text.replace(',', '.'))
                    return rate
            return None


@easy_error_handler
async def get_user_from_all(update, context) -> object:
    '''Ищет юзера в контектсте, базе данных или создает его с проверкой реферала, а затем сохраняет в контекст'''

    user = context.user_data.get('user', None) or await User.get_data(uid=update.effective_user.id)
    user = user[0] if user and type(user) is list else user
    if not user:
        user = update.effective_user

        # добавляем юзера
        new_user = await User.add_data(user.id, user.username, user.first_name, user.last_name) 
        
        # добавляем инфлюенсера
        influencer = update.effective_message.text.split(' ')
        if len(influencer) > 1:
            # расшифровка реферальной ссылки
            influencer = influencer[1].split('--')

            influencer_id = int(decompress(b64decode(influencer[0])).decode()) ^ int(ENCRYPT_KEY)
            timestamp = datetime.fromtimestamp(int(decompress(b64decode(influencer[1])).decode()) ^ int(ENCRYPT_KEY))
            influencer_type = int(influencer[2])
            
            if not influencer_id == user.id: # если юзер не добавляет сам себя в инфлюенсеры
                # юзер есть в базе и реферальная ссылка активна
                if await User.get_data(uid=influencer_id) and timestamp + timedelta(days=REFERRAL_LINK_LIVE) > datetime.now():
                    await Referral.add_data(influencer_id, user.id, influencer_type)
        user = new_user if new_user else user
    else:
        user_data = update.effective_user
        if user.username is None and user_data.username is not None:
            user.username = user_data.username
        if user_data.first_name is not None or user_data.last_name is not None:
            user.fullname = f'{user_data.first_name} {user_data.last_name if user_data.last_name is not None else ""}'
    await add_to_context_user_data(context, ('user', user)) if not context.user_data.get('user', None) else None
    return user


@easy_error_handler
async def check_str_to_float(update) -> bool:
    '''Проверяет строку на float'''

    try:
        num = float(update.effective_message.text)
        return num > MIN_AMOUNT
    except ValueError as e:
        logger.warning(e)
        return False
    

async def parting_message(message_list) -> list[str]:
    '''Делит большое сообщение на куски и сохраняет в лист'''

    new_message_list = []
    message = ""
    for part in message_list:
        if len(message) + len(part) <= 3500:
            message += part
        else:
            new_message_list.append(message)
            message = part
    if message:
        new_message_list.append(message)
    return new_message_list


@easy_error_handler
async def send_doc(uid, context, filename, config) -> None:
    '''Создает документ и отправляет пользователю, после удаляет его'''

    with open(filename, 'w') as file:
        file.write(config)
    with open(filename, 'rb') as document:
        await context.bot.send_document(uid, document)

    os.remove(filename)


@easy_error_handler
async def wg(command, link, uid=None) -> str:
    '''Flask. Запрашивает сервер wg на add, on, off, delete, debug VPN конфигураций'''

    if command == 'debug':
        data = {'command': command, 'sudo_password': WG_SERVER_SUDO_PASSWD}
    else:
        data = {'command': command, 'user_id': f'uid{uid}', 'sudo_password': WG_SERVER_SUDO_PASSWD}
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{link}/command', json=data, auth=aiohttp.BasicAuth(WG_SERVER_API_NAME, WG_SERVER_API_PASSWD)) as response:
            if response.status == 200:
                response_from_server = await response.json()
                result = response_from_server.get('result', None)
                return result
            else:
                return f'Request failed with status code {response.status}'

