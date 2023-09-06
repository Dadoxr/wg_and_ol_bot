import logging, os, sys, traceback
sys.path.append(os.getcwd())

from functools import wraps
from src.configs.config import ADMIN_ID


logging.basicConfig(filename='logs/all.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('logs/user.log')
formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formater)
logger.addHandler(handler)


def main_error_handler(func):
    '''Декоратор логинга waypoint + try except функции. Только для файла main.py'''

    @wraps(func)
    async def wrapper(update, context):
        first_name = update.effective_user.first_name
        last_name = update.effective_user.last_name
        fullname = f'{first_name} {last_name if last_name is not None else ""}'

        if update.callback_query:
            text = update.callback_query.data
        else:
            text = update.effective_message.text

        logger.info(f'ID: {update.effective_user.id}, {fullname} ==> {text}')
        
        try:
            return await func(update, context)
        except Exception as e:
            logger.warning(f"Error in file:'{func}' - func:'{func.__name__}' function: {e} in line: {traceback.format_exc()}")
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"Error in file:'{func}' - func:'{func.__name__}' function: {e} in line: {traceback.format_exc()}")
    return wrapper


def easy_error_handler(func):
    '''Декоратор try except для всех файлов кроме main.py'''

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Error in file:'{func}' - func:'{func.__name__}' function: {e} in line: {traceback.format_exc()}")
    return wrapper


def is_admin(func):
    '''Декоратор для проверки на админа'''

    @wraps(func)
    async def wrapper(*args, **kwargs):
        update = args[0]
        if int(update.effective_user.id) == int(ADMIN_ID):
            return await func(*args, **kwargs)
        else:
            context = args[1]
            await context.bot.send_message(chat_id=update.effective_user.id, text=f"Нажмите /start")
    return wrapper


