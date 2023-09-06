import sys, os, yookassa 
sys.path.append(os.getcwd())

from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler
from base64 import b64encode
from zlib import compress

from src.configs.logging import logging, main_error_handler, is_admin
from src.configs.utils import get_user_from_all, check_str_to_float, send_doc, send_message, add_to_context_user_data
from src.configs.admin_utils import (
    admin_utils_make_influencer_report_fn, 
    admin_utils_send_card_fn,
    admin_utils_make_spam_message_fn, 
    admin_utils_send_spam_message_fn
)
from src.configs.texts import *
from src.configs.kb import *
from src.models.join import get_entered, get_promo_active, get_subscription_active, get_sum_influencer_amount
from src.models.subscription import Subscription
from src.models.payment import Payment
from src.models.card import Card
from src.models.referral import Referral
from src.models.vpnconfig import VPNConfig


print('Запуск бота')
logging.info('Запуск бота')

########################## Н А Ч А Л О ###########################

@main_error_handler
async def start_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Обработчик команды /start, проверяет наличие подписки и формирует первое сообщениев'''

    await get_user_from_all(update, context)

    subscription = await Subscription.get_data(uid=update.effective_user.id)
    subscription_end = subscription[0].subscription_end if subscription else subscription

    if subscription and subscription_end > datetime.now():
        tip = f'\n\n✅Подписка АКТИВНА до {subscription_end.strftime("%d.%m.%Y")}'
    else:
        tip = f'\n\n⭕Подписка НЕ АКТИВНА'
    await send_message(update, context, start_text + tip, start_kb)


# ----------------- BONUSES ---------------------

@main_error_handler
async def bonuses_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Отображает меню с вариантами действующих бонусов '''
    
    await send_message(update, context, bonuses_no_text, to_main_kb)


# ------------------ VPN --------------------

@main_error_handler
async def subscription_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Отображает информацию о подписке пользователя и выводит варианты купить или создать ключ'''
    
    subscription = await Subscription.get_data(uid=update.effective_user.id)
    subscription_end = subscription[0].subscription_end if subscription else subscription

    if update.callback_query.data != 'continue_vpn_btn' and subscription and subscription_end >= datetime.now():
        await send_message(update, context, subscription_yes_text , subscription_yes_kb)
    else:
        await send_message(update, context, subscription_no_text, subscription_no_kb)

CHECK_PAYMENT_FN = 1
@main_error_handler
async def subscription_period_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Отображает информацию о периоде подписки и предлагает сделать пробное предложение. '''
    
    subscription_period = update.callback_query.data.split('##')[1]
    if subscription_period == '7_days':
        subscription = await Subscription.get_data(uid=update.effective_chat.id)
        if not subscription:
            time_now = datetime.now()
            await Subscription.add_data(update.effective_user.id, None, time_now, time_now + timedelta(days=PROMOPERIOD))
            await send_message(update, context, subscription_promo_done_text, subscription_payment_done_kb)
        else:
            await send_message(update, context, subscription_promo_done_before_text, to_subscription_kb)
    else:
        payment = await Payment.produce_payment(update)
        await add_to_context_user_data(context,('payment', payment))

        text, kb = await Payment.get_offer(update, context)
        await send_message(update, context, text, kb)
        return CHECK_PAYMENT_FN

             
@main_error_handler
async def make_configs_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Отображает информацию о создании VPN-конфигураций и предлагает пользователю выбор конфигурации. '''
    
    data = update.callback_query.data
    if data == 'make_configs_btn':
        await send_message(update, context, make_configs_text, make_configs_kb)
    else:
        user = await get_user_from_all(update, context)
        
        columns = {
            'make_configs_wg_rus_btn': 'wg_rus_config', 
            'make_configs_wg_neth_btn': 'wg_neth_config',
            'make_configs_outline_rus_btn': 'outline_rus_config', 
            'make_configs_outline_neth_btn': 'outline_neth_config'  
        }
        column_name = columns.get(data, 'None')     
        
        configs = await VPNConfig.get_data(user.uid)
        config = getattr(configs[0], column_name) if configs and hasattr(configs[0], column_name) else None

        if not config:
            config = await VPNConfig.make_config(user, data)
            await VPNConfig.add_data(user, config, column_name, configs)

        if data in ('make_configs_wg_rus_btn', 'make_configs_wg_neth_btn'):
            name = f'w{user.uid}_rus.conf' if data == 'make_configs_wg_rus_btn' else f'w{user.uid}_neth.conf'
            await send_doc(user.uid, context, name, config)
            await send_message(update, context, install_to_wireguard_text, to_main_kb) 
        else:
            await context.bot.send_message(chat_id=user.uid, text=config.split('##')[1])
            await send_message(update, context, install_to_outline_text, to_main_kb) 
    


# ------------------ PAY SERVICE --------------------
ISSUE_CARD_SUM_QUESTION_FN, ISSUE_CARD_PAYMENT_FN, ISSUE_CARD_SEND_TO_MANAGER_FN = range(3)
@main_error_handler
async def pay_service_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Отображает меню оплаты услуг. '''
    
    await send_message(update, context, pay_service_text, pay_service_kb)


@main_error_handler
async def issue_card_services_question_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Запрашивает сервисы для оплаты. '''
    
    await send_message(update, context, issue_card_services_question_text, cancel_all_kb)
    return ISSUE_CARD_SUM_QUESTION_FN


@main_error_handler
async def issue_card_sum_question_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Запрашивает сумму для оплаты карты. '''
    
    await add_to_context_user_data(context,('services', update.message.text))
    await send_message(update, context, issue_card_sum_question_text, cancel_all_kb)
    return ISSUE_CARD_PAYMENT_FN


@main_error_handler
async def issue_card_payment_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):   
    '''Обрабатывает оплату выпуска карты и отправляет предложение оплаты. '''
         
    if not await check_str_to_float(update):
        await send_message(update, context, not_isinstance_text)
    else:
        payment = await Payment.produce_payment(update)
        await add_to_context_user_data(context,('payment', payment), ('amount_to_card', update.effective_message.text))

        text, kb = await Payment.get_offer(update, context)

        await send_message(update, context, text, kb)
        return ISSUE_CARD_SEND_TO_MANAGER_FN


# ------------------ CHECK PAYMENTS --------------------

@main_error_handler
async def depit_from_account_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Списание со счета (amount_now) внутри бота и формирование новой платежной ссылки'''
    payment_id, amount_to_card = update.callback_query.data.split('##')[1:]
    payment_status = await Payment.get_payment_status(payment_id)
    if payment_status == 'succeeded':
        check_payment_btn = [InlineKeyboardButton(
            'Проверить платеж', 
            callback_data=f'check_payment_btn##{payment_id}##{amount_to_card}'
            ),
        ]
        check_payment_kb = InlineKeyboardMarkup([check_payment_btn])
        await send_message(update, context, can_not_cancael_paid_bill_text, check_payment_kb) 
    else:
        amount_now = int(await get_user_from_all(update, context).amount_now)

        await Payment.cancel_payment(payment_id)
        payment_old = Payment.get_data(payment_id=payment_id)[0]
        pay_sum = payment_old.pay_sum - amount_now
        
        payment_new = await Payment.produce_payment(update, pay_sum)
        await add_to_context_user_data(context,('payment', payment_new))

        text, kb = await Payment.get_offer(update, context)
        await send_message(update, context, text, kb)
        return CHECK_PAYMENT_FN


@main_error_handler
async def check_payment_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Проверяет статус оплаты и выполняет соответствующие действия после оплаты. '''

    services = context.user_data.get('services', 'Не описаны')
    payment_id, amount_to_card = update.callback_query.data.split('##')[1:]
    payment_status = await Payment.get_payment_status(payment_id)

    if payment_status == 'succeeded':
        user = update.effective_user
        payment = (await Payment.get_data(payment_id=payment_id))[0]
        await payment.update(status = 'succeeded')
        
        if payment.type == 'card':
            card = await Card.add_data(update.effective_user.id, payment_id, services, amount_to_card)

            await send_message(update, context, issue_card_payment_done_text, to_main_kb)
            await context.bot.send_message(
                chat_id=HELP_CHAT_ID, 
                text=await issue_card_send_to_manager_text(
                    user.username, 
                    user.id, 
                    card.amount_usd, 
                    payment.pay_sum, 
                    card.services, 
                    payment.id
                )
            )
        else:
            referral = await Referral.get_data(referral_id=user.id)

            if referral:
                influencer_cashback_amount = referral[0].influencer_percent * VPN_DATA[payment.type]['value']
                user_cashback_amount = (VPN_DATA[payment.type]['user_cashback_amount'] + referral[0].referral_percent) * VPN_DATA[payment.type]['value']
                
                await payment.update(influencer_amount = influencer_cashback_amount)
                await referral[0].update(referral_percent = 0)
            else:
                user_cashback_amount = (VPN_DATA[payment.type]['user_cashback_amount']) * VPN_DATA[payment.type]['value']
            
            await payment.update(user_cashback_amount = user_cashback_amount)
            
            subscription = context.user_data.get('subscription', None) or await Subscription.get_data(uid=update.effective_user.id)
            
            if subscription:
                subscription_end = subscription[0].subscription_end if subscription[0].subscription_end > datetime.now() else datetime.now()
                
                await subscription[0].update(last_payment_id = payment.id)
                await subscription[0].update(subscription_begin = datetime.now())
                await subscription[0].update(subscription_end = subscription_end + timedelta(days=VPN_DATA[payment.type]['subscriptiontime']))
                
                configs = await VPNConfig.get_data(user.id)
                await configs[0].on_configs() if configs else None
            else:
                await Subscription.add_data(user.id, payment.id, datetime.now(), datetime.now() + timedelta(days=VPN_DATA[payment.type]['subscriptiontime']))
            
            credit_date = (datetime.now() + timedelta(days=CREDITING_CASHBACK_PERIOD)).strftime('%d.%m.%Y')
            await send_message(update, context, subscription_payment_done_text % (user_cashback_amount, credit_date), subscription_payment_done_kb)

        return ConversationHandler.END
    await update.callback_query.answer(text=f"Платеж не оплачен", show_alert=True)



# ------------------ MY CABINET --------------------
@main_error_handler
async def my_cabinet_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Отображает информацию о пользовательском кабинете, включая сумму и кэшбэк. '''
    
    user = await get_user_from_all(update, context)
    payments = await Payment.get_data(
        uid=update.effective_user.id, 
        pay_date=datetime.now() - timedelta(days=CREDITING_CASHBACK_PERIOD)
    )

    user_cashback_amount = sum([i.user_cashback_amount for i in payments]) if payments else 0
    
    await send_message(update, context, await my_cabinet_text(
        user.fullname, 
        user.amount_now,
        user_cashback_amount
        ), my_cabinet_kb)


@main_error_handler
async def my_cards_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Отправляет пользователю его действующие карты, включая номер, дату и cvv. '''
    
    cards = await Card.get_data(uid=update.effective_user.id)
    if cards:
        for card in cards:
            if card.details:
                number, date, cvv = card.details.split('##')
                await context.bot.send_message(
                    chat_id=update.effective_user.id, 
                    text=await send_yes_card_to_user_text(number, date, cvv)
                )
            else:
                await context.bot.send_message(
                    chat_id=update.effective_user.id, 
                    text=await send_no_card_to_user_text(card.services, card.amount_usd)
                )
    else:
        await update.callback_query.answer(text=cards_no_text, show_alert=True)


@main_error_handler
async def my_configs_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Отправляет пользователю его VPN-конфигурации, если есть, иначе сообщение об отсутствии '''
    
    configs = await VPNConfig.get_data(uid=update.effective_user.id)
    
    if configs and any(configs[0].wg_rus_config
                       or configs[0].wg_neth_config 
                       or configs[0].outline_rus_config 
                       or configs[0].outline_neth_config
                       ):
        await update.callback_query.answer()
        user = await get_user_from_all(update, context)

        await send_doc(user.uid, context, f'w{user.uid}_rus.conf', configs[0].wg_rus_config) if configs[0].wg_rus_config else None
        await send_doc(user.uid, context, f'w{user.uid}_neth.conf', configs[0].wg_neth_config) if configs[0].wg_neth_config else None

        await context.bot.send_message(chat_id=user.uid, text=configs[0].outline_rus_config) if configs[0].outline_rus_config else None
        await context.bot.send_message(chat_id=user.uid, text=configs[0].outline_neth_config) if configs[0].outline_neth_config else None
    else:
        await update.callback_query.answer(text=configs_no_text, show_alert=True)
       

@main_error_handler
async def withdraw_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Отображает информацию о возможности вывода средств. '''
    
    user = await get_user_from_all(update, context)
    
    if user.amount_now >= 3000:
        await send_message(update, context, withdraw_text, to_my_cabinet_kb)
    else:
        await update.callback_query.answer(text=withdraw_not_enough_text, show_alert=True)


@main_error_handler
async def get_referral_link_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Запрашивает тип реферальной ссылки у пользователя. '''
    
    await send_message(update, context, ask_influencer_type_text, influencer_type_kb)


@main_error_handler
async def make_referral_link_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Создает и отправляет реферральную ссылку пользователю.  '''
    
    influencer_id = b64encode(compress(str(417368206 ^ int(ENCRYPT_KEY)).encode())).decode()
    timestamp = b64encode(compress(str(int(datetime.now().timestamp()) ^ int(ENCRYPT_KEY)).encode())).decode()
    influencer_type = int(update.callback_query.data.split('##')[1])

    date_to_end_of_link = datetime.now() + timedelta(days=REFERRAL_LINK_LIVE)
    influencer_link = f'Ссылка будет активна до {(date_to_end_of_link).strftime("%d.%m.%Y %H:%M")}.\
                        \n\nt.me/{BOT_USERNAME}?start={influencer_id}--{timestamp}--{influencer_type}'
    
    await context.bot.send_message(chat_id=update.effective_user.id, text=influencer_link)


@main_error_handler
async def influencer_statistics_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Отображает статистику реферральной программы пользователя. '''
    
    promo_active = await get_promo_active(update.effective_user.id)
    subscription_active = await get_subscription_active(update.effective_user.id)

    uid = update.effective_user.id
    date_one = datetime(datetime.now().year, datetime.now().month - 1 , 1)
    date_two = datetime(datetime.now().year, datetime.now().month , 1)
    entered_last_month = await get_entered(uid, date_one, date_two)
    
    date_one = datetime(datetime.now().year, datetime.now().month , 1)
    date_two = datetime(datetime.now().year, datetime.now().month + 1 , 1)
    entered_now_month = await get_entered(uid, date_one, date_two)

    referral_all = await Referral.get_data(influencer_id=update.effective_user.id)

    will_earn = await get_sum_influencer_amount(influencer_id=update.effective_user.id)
    total_earn = (await get_user_from_all(update, context)).total_earned

    await send_message(update, context, influencer_statistics_text % (len(promo_active), len(subscription_active), 
                                                                      len(entered_last_month), len(entered_now_month), 
                                                                      len(referral_all), will_earn, total_earn), to_my_cabinet_kb)


# ------------------ INFO --------------------
@main_error_handler
async def info_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Отображает информацию о различных темах, таких как инструкции, FAQ и т. д. '''
    
    data = update.callback_query.data.split('##')[1]
    data_list = {
        'info': [info_text, info_kb],
        'faq': [faq_text, faq_kb],
        'instruction_pay_service': [instruction_pay_service_text, to_info_kb],
        'instruction_vpn': [instruction_vpn_text, instruction_vpn_kb],
        'install_to_outline': [install_to_outline_text, to_instruction_vpn_kb],
        'install_to_wireguard': [install_to_wireguard_text, to_instruction_vpn_kb],
        'differences_between_protocols': [differences_between_protocols_text, to_faq_kb],
        'data_protection_regulations': [data_protection_regulations_text, to_info_kb],
        'discord_not_work': [discord_not_work_text, to_faq_kb],
        'windows_off': [windows_off_text, to_faq_kb],
        'russian_service_not_work': [russian_service_not_work_text, to_faq_kb],
        'collection_and_use_information': [collection_and_use_information_text, to_info_kb]
    }
    text = data_list.get(data)
    if data_list.get(data):
        await send_message(update, context, text[0], text[1])
    else:
        await cancel_fn(update, context)


# ------------------ HELP --------------------
@main_error_handler
async def help_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Отображает меню с вариантами помощи пользователю. '''
    
    data = update.callback_query.data.split('##')[1]

    if data == 'help':
        await send_message(update, context, help_text, help_kb)
        return ConversationHandler.END
    elif data == 'refund':
        await send_message(update, context, refund_text, refund_kb)
        return ConversationHandler.END
    elif data == 'problem':
        await send_message(update, context, problem_text, cancel_all_kb)
        return PROBLEM_FN
    else:
        await cancel_fn(update, context)


MAKE_REFUND_REASON = 1
@main_error_handler
async def make_refund_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Проверяет возможность возврата подписки и выводит информацию о причинах невозможности, если они есть. '''
    
    subscription = await Subscription.get_data(update.effective_user.id)
    reason = 'Нет подписок'

    if subscription:
        is_active_subscription = subscription[0].subscription_end >= datetime.now()
        can_do_refund = subscription[0].subscription_begin >= datetime.now() - timedelta(days=REFUNDPERIOD)
        reason = 'Подписка не активна' if not is_active_subscription else 'Период возврата прошел'

        if is_active_subscription and can_do_refund:
            payment = await Payment.get_data(payment_id=subscription[0].last_payment_id)
            reason = 'Нет оплаченных платежей'
                
            if payment and payment[0].status == 'succeeded':
                await send_message(update, context, refund_done_text, cancel_all_kb)
                await add_to_context_user_data(context, ('payment', payment[0]))
                return MAKE_REFUND_REASON
    await send_message(update, context, refund_no_text % (reason), to_refund_kb)


@main_error_handler
async def make_refund_reason_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Получает и сохраняет причину возврата платежа. '''
    
    payment = context.user_data.get('payment', None)
    if payment:
        await payment.update(refund_reason = update.effective_message.text)
    await send_message(update, context, refund_reason_text, to_main_kb)
    return ConversationHandler.END


PROBLEM_FN = 1
@main_error_handler
async def problem_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Отправляет сообщение с проблемой в чат поддержки. '''
    
    help_text = update.effective_message.text
    uid = update.effective_user.id
    username = update.effective_user.username
    await context.bot.send_message(chat_id=HELP_CHAT_ID, text=problem_to_help_chat_text % (username, uid, help_text))
    await send_message(update, context, problem_done_text, to_main_kb)
    return ConversationHandler.END


######################### A D M I N ########################

@is_admin
async def spam_tip_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Отправка админу структуры сообщения для отправки сообщения пользователям '''
    
    await send_message(update, context, spam_tip_text, to_main_kb)


@is_admin
async def send_card_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Позволяет админу отправить карту. '''
    
    await admin_utils_send_card_fn(update, context)
    

SEND_SPAM_MESSAGE_FN = 1
@is_admin
async def make_spam_message_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Позволяет админу создать сообщение для отправки спама. '''
    
    await admin_utils_make_spam_message_fn(update, context)
    return SEND_SPAM_MESSAGE_FN


@is_admin
async def send_spam_message_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Позволяет админу отправить спам-сообщение. '''
    
    await admin_utils_send_spam_message_fn(update, context)
    return ConversationHandler.END


@is_admin
async def which_report_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Отпрвляет список отчетов на выбор'''

    await send_message(update, context, which_report_text, reports_kb)


@is_admin
async def report_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Запрашивает ссылку на отчет по инфлюенсерам и отправляет ее админу'''
    if update.callback_query.data == 'influencer_report_btn':
        spreadsheet = await admin_utils_make_influencer_report_fn()
        text = f"Таблица с инфлюенсерами. Лист 1{spreadsheet}"
    else:
        text = 'Неизвестный запрос'
    await send_message(update, context, text, to_my_cabinet_kb)


# ----------------------------------------------------------------
@main_error_handler
async def cancel_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Отменяет текущий ConversationHandler и платеж, если он ожидает подтверждения. '''

    if '##' in update.callback_query.data:
        payment_id, amount_to_card = update.callback_query.data.split('##')[1:]
        payment_status = await Payment.get_payment_status(payment_id) 
        if payment_status == 'succeeded':
            check_payment_btn = [InlineKeyboardButton('Проверить платеж', callback_data=f'check_payment_btn##{payment_id}##{amount_to_card}'), ]
            check_payment_kb = InlineKeyboardMarkup([check_payment_btn])
            await send_message(update, context, can_not_cancael_paid_bill_text, check_payment_kb)            
        elif payment_status == 'waiting_for_capture':
            await Payment.cancel_payment(payment_id)    
            await send_message(update, context, cancel_text)
            context.user_data.clear()
            return ConversationHandler.END
    else:
        await send_message(update, context, cancel_text)
        context.user_data.clear()
        return ConversationHandler.END


@main_error_handler
async def any_message_fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Прием любого текста'''

    await send_message(update, context, any_message_text)


############################ H A N D L E R S ###############################
def _add_handlers(application):

    issue_card_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(issue_card_services_question_fn, pattern='issue_card_services_question_btn')],
        states={ISSUE_CARD_SUM_QUESTION_FN: [MessageHandler(filters.TEXT, issue_card_sum_question_fn)],
                ISSUE_CARD_PAYMENT_FN: [MessageHandler(filters.TEXT, issue_card_payment_fn)],
                ISSUE_CARD_SEND_TO_MANAGER_FN: [CallbackQueryHandler(check_payment_fn, pattern='check_payment_btn' )],
                },
        fallbacks=[CallbackQueryHandler(cancel_fn, pattern="cancel_all_btn")],
        name="issue_card",
        allow_reentry=True,)
    application.add_handler(issue_card_handler)

    send_spam_message_handler = ConversationHandler(
        entry_points=[CommandHandler('make_spam_message', make_spam_message_fn)],
        states={SEND_SPAM_MESSAGE_FN: [MessageHandler(filters.ALL, send_spam_message_fn)],},
        fallbacks=[CallbackQueryHandler(cancel_fn, pattern="cancel_all_btn")],
        name="spam_message",
        allow_reentry=True,)
    application.add_handler(send_spam_message_handler)

    subscription_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(subscription_period_fn, pattern='subscription_period')],
        states={CHECK_PAYMENT_FN: [CallbackQueryHandler(check_payment_fn, pattern='check_payment_btn' )],},
        fallbacks=[CallbackQueryHandler(cancel_fn, pattern="cancel_all_btn")],
        name="subscription",
        allow_reentry=True,)
    application.add_handler(subscription_handler)

    refund_reason_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(make_refund_fn, pattern='make_refund_btn')],
        states={MAKE_REFUND_REASON: [MessageHandler(filters.TEXT, make_refund_reason_fn )],},
        fallbacks=[CallbackQueryHandler(cancel_fn, pattern="cancel_all_btn")],
        name="refund_reason",
        allow_reentry=True,)
    application.add_handler(refund_reason_handler)
    
    problem_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(help_fn, pattern='help')],
        states={PROBLEM_FN: [MessageHandler(filters.TEXT, problem_fn)],},
        fallbacks=[CallbackQueryHandler(cancel_fn, pattern="cancel_all_btn")],
        name="problem",
        allow_reentry=True,)
    application.add_handler(problem_handler)

    application.add_handler(CommandHandler('start', start_fn))
    application.add_handler(CommandHandler('spam_tip', spam_tip_fn))
    application.add_handler(CommandHandler('send_card', send_card_fn))

    application.add_handler(CallbackQueryHandler(start_fn, pattern='start_btn'))
    application.add_handler(CallbackQueryHandler(subscription_fn, pattern='subscription_btn'))
    application.add_handler(CallbackQueryHandler(subscription_fn, pattern='continue_vpn_btn'))
    application.add_handler(CallbackQueryHandler(make_configs_fn, pattern='make_configs_btn'))
    application.add_handler(CallbackQueryHandler(make_configs_fn, pattern='make_configs_outline_rus_btn'))
    application.add_handler(CallbackQueryHandler(make_configs_fn, pattern='make_configs_outline_neth_btn'))
    application.add_handler(CallbackQueryHandler(make_configs_fn, pattern='make_configs_wg_rus_btn'))
    application.add_handler(CallbackQueryHandler(make_configs_fn, pattern='make_configs_wg_neth_btn'))
    application.add_handler(CallbackQueryHandler(my_cabinet_fn, pattern='my_cabinet_btn'))
    application.add_handler(CallbackQueryHandler(pay_service_fn, pattern='pay_service_btn'))
    application.add_handler(CallbackQueryHandler(cancel_fn, pattern="cancel_all_btn"))
    application.add_handler(CallbackQueryHandler(depit_from_account_fn, pattern="depit_from_account_btn"))
    application.add_handler(CallbackQueryHandler(check_payment_fn, pattern='check_payment_btn' ))
    application.add_handler(CallbackQueryHandler(my_cards_fn, pattern='my_cards_btn'))
    application.add_handler(CallbackQueryHandler(withdraw_fn, pattern='withdraw_btn'))
    application.add_handler(CallbackQueryHandler(info_fn, pattern='info'))
    application.add_handler(CallbackQueryHandler(my_configs_fn, pattern='my_configs_btn'))
    application.add_handler(CallbackQueryHandler(get_referral_link_fn, pattern='get_referral_link_btn'))
    application.add_handler(CallbackQueryHandler(make_referral_link_fn, pattern='influencer_type'))
    application.add_handler(CallbackQueryHandler(influencer_statistics_fn, pattern='influencer_statistics_btn'))
    application.add_handler(CallbackQueryHandler(bonuses_fn, pattern='bonuses_btn'))
    application.add_handler(CallbackQueryHandler(which_report_fn, pattern='which_report_btn'))
    application.add_handler(CallbackQueryHandler(report_fn, pattern='influencer_report_btn'))
    application.add_handler(CallbackQueryHandler(report_fn, pattern='referral_report_btn'))

    application.add_handler(MessageHandler(filters.TEXT, any_message_fn))


def main():
    yookassa.Configuration.configure(YOOKASSA_SHOPID, YOOKASSA_SECRET_KEY)
    application = ApplicationBuilder().token(BOT_API_TOKEN).build()
    _add_handlers(application)
    print('Бот запущен')
    logging.info('Бот запущен')

    application.run_polling(allowed_updates=Update.ALL_TYPES)

############################ M A I N ####################################
if __name__ == '__main__':
    main()

    




