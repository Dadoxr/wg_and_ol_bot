import os, sys
sys.path.append(os.getcwd())

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.configs.config import *
from src.configs.utils import easy_error_handler
from src.configs.texts import main_about_us_text


@easy_error_handler
async def make_pay_kb(payment: object, amount_to_card: str) -> list[object]:
    '''Создание клавиатуры для любой оплаты'''

    pay_btn = [InlineKeyboardButton('Оплатить', url=payment.confirmation.confirmation_url),]
    check_payment_btn = [InlineKeyboardButton('Проверить платеж', callback_data=f'check_payment_btn##{payment.id}##{amount_to_card}'), ]
    pay_from_account_btn = [InlineKeyboardButton('Списать со счета', callback_data=f'depit_from_account_btn##{payment.id}##{amount_to_card}'), ]
    cancel_all_btn = [InlineKeyboardButton('❌Отмена', callback_data=f'cancel_all_btn##{payment.id}##{amount_to_card}'), ]

    zero_account_pay_kb = InlineKeyboardMarkup([pay_btn, check_payment_btn, cancel_all_btn])
    part_pay_from_account_kb = InlineKeyboardMarkup([pay_btn, check_payment_btn, pay_from_account_btn, cancel_all_btn])
    
    return [zero_account_pay_kb, part_pay_from_account_kb]



######################## Н А З А Д #############################
start_btn = [InlineKeyboardButton('🔙Главная', callback_data='start_btn'), ]
to_main_kb = InlineKeyboardMarkup([start_btn,])

cancel_all_btn = [InlineKeyboardButton('❌Отмена', callback_data='cancel_all_btn'), ]
cancel_all_kb = InlineKeyboardMarkup([cancel_all_btn,])

to_my_cabinet_btn = [InlineKeyboardButton('🔙Назад', callback_data='my_cabinet_btn'), ]
to_my_cabinet_kb = InlineKeyboardMarkup([to_my_cabinet_btn,])

to_subscription_btn = [InlineKeyboardButton('🔙Назад', callback_data='subscription_btn'), ]
to_subscription_kb = InlineKeyboardMarkup([to_subscription_btn,])

to_info_btn = [InlineKeyboardButton('🔙Назад', callback_data='info_##info##_btn'), ]
to_info_kb = InlineKeyboardMarkup([to_info_btn,])

to_faq_btn = [InlineKeyboardButton('🔙Назад', callback_data='info_##faq##_btn'), ]
to_faq_kb = InlineKeyboardMarkup([to_faq_btn,])

to_instruction_vpn_btn = [InlineKeyboardButton('🔙Назад', callback_data='info_##instruction_vpn##_btn'), ]
to_instruction_vpn_kb = InlineKeyboardMarkup([to_instruction_vpn_btn,])

to_help_btn = [InlineKeyboardButton('🔙Назад', callback_data='help_##help##_btn'), ]
to_help_kb = InlineKeyboardMarkup([to_help_btn,])

to_refund_btn = [InlineKeyboardButton('🔙Назад', callback_data='help_##refund##_btn'), ]
to_refund_kb = InlineKeyboardMarkup([to_refund_btn, ])

to_subscription_yes_btn = [InlineKeyboardButton('🔙Назад', callback_data='subscription_btn'), ]
to_subscription_yes_kb = InlineKeyboardMarkup([to_subscription_yes_btn, ])


########################### I N F O #####################################
faq_btn = [InlineKeyboardButton('FAQ', callback_data='info_##faq##_btn'), ]
instruction_pay_service_btn = [InlineKeyboardButton('Оплата сервиса', callback_data='info_##instruction_pay_service##_btn'), ]
instruction_vpn_btn = [InlineKeyboardButton('Подключиение VPN', callback_data='info_##instruction_vpn##_btn'), ]
install_to_outline_btn = [InlineKeyboardButton('Настроить Outline', callback_data='info_##install_to_outline##_btn'), ]
install_to_wireguard_btn = [InlineKeyboardButton('Настроить WireGuard', callback_data='info_##install_to_wireguard##_btn'), ]
differences_between_protocols_btn = [InlineKeyboardButton('Разница протоколов', callback_data='info_##differences_between_protocols##_btn'), ]
data_protection_regulations_btn = [InlineKeyboardButton('Безопасность данных', callback_data='info_##data_protection_regulations##_btn'), ]
discord_not_work_btn = [InlineKeyboardButton('Discord не работает', callback_data='info_##discord_not_work##_btn'), ]
windows_off_btn = [InlineKeyboardButton('Проблемы c Windows', callback_data='info_##windows_off##_btn'), ]
russian_service_not_work_btn = [InlineKeyboardButton('Проблемы Российские сервисы', callback_data='info_##russian_service_not_work##_btn'), ]
collection_and_use_information_btn = [InlineKeyboardButton('Сбор данных', callback_data='info_##collection_and_use_information##_btn'), ]
feedback_btn = [InlineKeyboardButton('🗣Отзывы', url=FEEDBACK_LINK), ]
main_about_us_btn = [InlineKeyboardButton('Главное о VPN', url=main_about_us_text), ]

info_kb = InlineKeyboardMarkup([faq_btn, feedback_btn, instruction_vpn_btn, instruction_pay_service_btn, data_protection_regulations_btn, collection_and_use_information_btn, start_btn,])
instruction_vpn_kb = InlineKeyboardMarkup([install_to_outline_btn, install_to_wireguard_btn, to_info_btn])
faq_kb = InlineKeyboardMarkup([main_about_us_btn, differences_between_protocols_btn, discord_not_work_btn, windows_off_btn, russian_service_not_work_btn, to_info_btn,])


########################### M A I N #####################################
subscription_btn = [InlineKeyboardButton('🔒VPN', callback_data='subscription_btn'), ]
pay_service_btn = [InlineKeyboardButton('💵Оплата зарубежного сервиса', callback_data='pay_service_btn'), ]
bonuses_btn = [InlineKeyboardButton('🚀Бонусы', callback_data='bonuses_btn'), ]
my_cabinet_btn = [InlineKeyboardButton('🏡Мой кабинет', callback_data='my_cabinet_btn'), ]
info_btn = [InlineKeyboardButton('📔Инфо', callback_data='info_##info##_btn'), ]
help_btn = [InlineKeyboardButton('❓Помощь', callback_data='help_##help##_btn'), ]

start_kb = InlineKeyboardMarkup([subscription_btn, pay_service_btn, [bonuses_btn[0], my_cabinet_btn[0],], [info_btn[0], help_btn[0],],])


########################### S U B S C R I P T I O N #####################################
period_7_days_btn = [InlineKeyboardButton(f'✅Пробные 7 дней', callback_data='subscription_period##7_days##_btn'), ]
period_1_month_btn = [InlineKeyboardButton(f'1 месяц: {ONE_MONTH_COST} руб', callback_data='subscription_period##1_month##_btn'), ]
period_3_month_btn = [InlineKeyboardButton(f'3 месяца: {TREE_MONTH_COST} руб (-{(1-SUBSCRIPTIONDISCOUNT2)*100}%)', callback_data='subscription_period##3_months##_btn'), ]
period_6_month_btn = [InlineKeyboardButton(f'6 месяцев: {SIX_MONTH_COST} руб (-{(1-SUBSCRIPTIONDISCOUNT3)*100}%)', callback_data='subscription_period##6_months##_btn'), ]
period_12_month_btn = [InlineKeyboardButton(f'12 месяцев: {TWELVE_MONTH_COST} руб (-{(1-SUBSCRIPTIONDISCOUNT4)*100}%)', callback_data='subscription_period##12_months##_btn'), ]
make_configs_btn = [InlineKeyboardButton('Создать ключи доступа', callback_data='make_configs_btn'), ]
make_configs_outline_rus_btn = [InlineKeyboardButton('Outline Россия', callback_data='make_configs_outline_rus_btn'), ]
make_configs_outline_neth_btn = [InlineKeyboardButton('Outline Нидерланды', callback_data='make_configs_outline_neth_btn'), ]
make_configs_wireguard_rus_btn = [InlineKeyboardButton('WireGuard Россия', callback_data='make_configs_wg_rus_btn'), ]
make_configs_wireguard_neth_btn = [InlineKeyboardButton('WireGuard Нидерланды', callback_data='make_configs_wg_neth_btn'), ]
continue_vpn_btn = [InlineKeyboardButton('Продлить подписку', callback_data='continue_vpn_btn'), ]

subscription_no_kb = InlineKeyboardMarkup([period_7_days_btn, period_1_month_btn, period_3_month_btn, period_6_month_btn, period_12_month_btn, start_btn,])
subscription_yes_kb = InlineKeyboardMarkup([make_configs_btn, continue_vpn_btn, start_btn,])
make_configs_kb = InlineKeyboardMarkup([make_configs_outline_rus_btn, make_configs_outline_neth_btn, make_configs_wireguard_rus_btn, make_configs_wireguard_neth_btn, to_subscription_yes_btn,])
subscription_payment_done_kb = InlineKeyboardMarkup([instruction_vpn_btn, start_btn,])


########################### P A Y   S E R V I C E #####################################
issue_card_services_question_btn = [InlineKeyboardButton('💳Создать карту', callback_data='issue_card_services_question_btn'), ]

pay_service_kb = InlineKeyboardMarkup([issue_card_services_question_btn, start_btn,])


########################### M Y  C A B I N E T #####################################
my_cards_btn = [InlineKeyboardButton('💳Мои карты', callback_data='my_cards_btn'), ]
my_configs_btn = [InlineKeyboardButton('📄Мои конфиги', callback_data='my_configs_btn'), ]
withdraw_btn = [InlineKeyboardButton('💸Вывести', callback_data='withdraw_btn'), ]
influencer_statistics_btn = [InlineKeyboardButton('🫂Статистика инфлюенсера', callback_data='influencer_statistics_btn'), ]
get_referral_link_btn = [InlineKeyboardButton('🔗Выдать реферальную ссылку', callback_data='get_referral_link_btn'), ]

inf_one = int(INFLUENCER_TYPE[1]["influencer"] * 100)
ref_one = int(INFLUENCER_TYPE[1]["referral"] * 100)
inf_two = int(INFLUENCER_TYPE[2]["influencer"] * 100)
ref_two = int(INFLUENCER_TYPE[2]["referral"] * 100)
influencer_type_one_btn = [InlineKeyboardButton(f'{inf_one}/{ref_one}', callback_data='influencer_type_##1##_btn'), ]
influencer_type_two_btn = [InlineKeyboardButton(f'{inf_two}/{ref_two}', callback_data='influencer_type_##2##_btn'), ]

which_report_btn = [InlineKeyboardButton('Отчеты', callback_data='which_report_btn'), ]
influencer_report_btn = [InlineKeyboardButton('Инфлюенсеры', callback_data='influencer_report_btn'), ]
referral_report_btn = [InlineKeyboardButton('Рефералы', callback_data='referral_report_btn'), ]

my_cabinet_kb = InlineKeyboardMarkup([[my_cards_btn[0], my_configs_btn[0],], withdraw_btn, which_report_btn, influencer_statistics_btn, get_referral_link_btn, start_btn,])
influencer_type_kb = InlineKeyboardMarkup([influencer_type_one_btn, influencer_type_two_btn, to_my_cabinet_btn])
reports_kb = InlineKeyboardMarkup([influencer_report_btn, referral_report_btn, to_my_cabinet_btn,])

################################# H E L P ########################################
refund_btn = [InlineKeyboardButton('Возврат', callback_data='help_##refund##_btn'), ]
make_refund_btn = [InlineKeyboardButton('Оформить возврат', callback_data='make_refund_btn'), ]
problem_btn = [InlineKeyboardButton('Проблема', callback_data='help_##problem##_btn'), ]

help_kb = InlineKeyboardMarkup([refund_btn, problem_btn, start_btn,])
refund_kb = InlineKeyboardMarkup([make_refund_btn, to_help_btn,])




