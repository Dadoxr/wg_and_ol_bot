import os, sys, time, gspread, gspread_dataframe, pandas as pd
sys.path.append(os.getcwd())

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.models.join import get_influencers_data_from_table
from src.configs.utils import send_message, add_to_context_user_data, parting_message
from src.configs.texts import send_no_card_to_user_text, confirm_spam_message_text
from src.configs.kb import to_main_kb
from src.configs.config import ADMIN_ID, GOOGLE_SHEET_NAME, GOOGLE_SHEETS_CREDENTIALS
from src.models.card import Card
from src.models.user import User


async def admin_utils_send_card_fn(update, context) -> None:
    '''Позволяет админу отправить карту. '''
    
    data = update.effective_message.text.split('##')

    number, date, cvv = data[1].strip(), data[2].strip(), data[3].strip()
    uid, payment_id = data[4].strip(), data[5].strip()

    card = (await Card.get_data(payment_id=payment_id))[0]
    card.card_details = f'{number}, {date}, {cvv}'
    await card.update(card_details = f'{number} ## {date} ## {cvv}')
    
    await context.bot.send_message(
        chat_id=uid, 
        text=await send_no_card_to_user_text(number, date, cvv), parse_mode='MARKDOWN'
    )


async def admin_utils_make_spam_message_fn(update, context) -> None:
    '''Позволяет админу создать сообщение для отправки спама. '''

    data = update.effective_message.text.split('##')
    
    type_message = data[1].lower().strip()
    quiz_message = data[2]
    keyboard = data[3]
    to_whom = data[4].lower().strip()

    if type_message == 'quiz':
        quiz_variants = keyboard.split(',')
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(button.strip(), callback_data=f'poll_variant_{button.strip()}'),] for button in quiz_variants
            ]
        )
    elif type_message == 'message':
        kb = to_main_kb
    else:
        await send_message(update, context, 'Не распознал тип сообщения')
    await context.bot.send_message(chat_id=ADMIN_ID, text=quiz_message, reply_markup=kb)
    await context.bot.send_message(chat_id=ADMIN_ID, text=confirm_spam_message_text)
    await add_to_context_user_data(context, ('quiz_message', quiz_message),
                                            ('quiz_kb', kb),
                                            ('to_whom', to_whom))



async def admin_utils_send_spam_message_fn(update, context) -> None:
    '''Позволяет админу отправить спам-сообщение, после чего отправляет отчет админу'''

    data = context.user_data
    quiz_message, quiz_kb, to_whom = data.get('quiz_message', None), data.get('quiz_kb', None), data.get('to_whom', None)
    
    sended_message = []
    error_sended_message = []
    users = []
    msg = update.effective_message.text.lower()
    
    if msg == 'ok':
        if to_whom == 'всем':
            users = await User.get_data()
        elif to_whom == 'инф':
            users = await User.get_data(is_influencer=True)
        elif to_whom == 'без инф':
            users = await User.get_data(is_influencer=False)
        else:
            for user in to_whom.split(','):
                user = await User.get_data(uid=int(user))
                users.append([user])
        
        if users:
            for row in users:
                row = row[0]
                try:
                    await context.bot.send_message(chat_id=row.uid, text=quiz_message, reply_markup=quiz_kb)
                    sended_message.append(f'{row.uid}, @{row.username}\n')
                    time.sleep(1)
                except Exception as error: 
                    error_sended_message.append(f'{row.uid}, @{row.username} -> {error}\n\n')
                    time.sleep(1)
            await context.bot.send_message(chat_id=ADMIN_ID,text=f'Успешные\n\n')
            rebase_sended_message = parting_message(sended_message)
            for message in rebase_sended_message:
                if message:
                    await context.bot.send_message(chat_id=ADMIN_ID, text=f'{message}')
                    time.sleep(1)

            await context.bot.send_message(chat_id=ADMIN_ID, text='Не успешные\n\n')
            rebase_error_sended_message = parting_message(error_sended_message)
            for message in rebase_error_sended_message:
                if message:
                    await context.bot.send_message(chat_id=ADMIN_ID, text=f'{message}')
                    time.sleep(1)
    await context.bot.send_message(chat_id=ADMIN_ID, text=f'Всего: {len(users)}\
                            \n\nОбработано: {len(sended_message)+len(error_sended_message)}\
                            \nУспешные: {len(sended_message)}\
                            \nНе успешные: : {len(error_sended_message)}''')


async def admin_utils_make_influencer_report_fn() -> str:
    '''Формирует отчет в Google Sheet по инфлюенсерам и возвращает ссылку на отчет'''
    
    headers, influencers = await get_influencers_data_from_table()
    if influencers:
        # Инициализация клиента Google Sheets API
        gc = gspread.service_account(filename=GOOGLE_SHEETS_CREDENTIALS)

        # Создание нового листа или открытие существующего
        spreadsheet = gc.open(GOOGLE_SHEET_NAME)
        worksheet = spreadsheet.worksheet('influencers')

        # Запись результатов в лист Google Sheets
        df = pd.DataFrame(influencers, columns=headers)
        await gspread_dataframe.set_with_dataframe(worksheet, df)
        return spreadsheet.url
    return 'Таблица пустая'

