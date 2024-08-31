
import telebot
from telebot import types
import schedule
import time
import os
import random
from telebot.types import CallbackQuery
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from persiantools.jdatetime import JalaliDateTime

TOKEN = "6306083951:AAEpFDifX6H-sxwig2WS3Q-OgmDjeuDdhxg"
bot = telebot.TeleBot(TOKEN)

user_accounts = {}

menu_stack = []

user_data = {}

# تعریف دیکشنری برای نگه‌داری وضعیت تکمیل مراحل توسط کاربران
user_completed_steps = {}

# تعریف دیکشنری برای نگه‌داری وضعیت مشاوره توسط کاربران
user_consultation_states = {}

# تعریف دیکشنری برای ذخیره پیام‌های کاربران
user_messages = {}

# تاریخ فعال‌سازی گروه‌های درسی
activation_date = datetime(2024, 9, 23)  # تاریخ 1 مهر 1402

# ایجاد یک شیء تاریخ شمسی
shamsi_date_time = JalaliDateTime.now()
shamsi_date = shamsi_date_time.strftime("%Y-%m-%d %H:%M:%S")

user_stats = {
    'total_users': 0,
    'start_commands_total': 0,
    'chart_requests_total': 0,
    'user_data': {}  # شناسه کاربر: آمار
}

# تعیین گروه‌هایی که می‌خواهید ربات در آن ادمین باشد
#allowed_group_ids = [-1001732405225, -971926020, -1001920870599, -4081988621, -1001735421246, -1001810640578]

@bot.message_handler(func=lambda message: message.chat.type in ["group", "supergroup"])
def handle_group_messages(message):
    # پیام‌های دریافتی از گروه‌ها را نادیده بگیرید
    pass

@bot.message_handler(func=lambda message: message.chat.type in ["group", "supergroup"], commands=["start"])
def handle_group_start(message):
    # پاسخ به دستور /start در گروه‌ها را نادیده بگیرید
    pass

@bot.message_handler(commands=["start"])
def handle_start(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    user_chat_id = message.chat.id
    if user_id not in user_stats['user_data']:
        user_first_name = message.from_user.first_name or "ناشناس"
        user_last_name = message.from_user.last_name or ""
        user_username = message.from_user.username

        user_name = f"{user_first_name} {user_last_name}"
        bot.send_message(user_chat_id, f"سلام {user_name} عزیز! به ربات تلگرامی ارشد کامپیوتر خوش آمدید.")

    bot.send_message(user_chat_id, "لطفاً منو مورد نظر خود را انتخاب کنید:", reply_markup=main_menu_keyboard())

    if user_id not in user_stats['user_data']:
        user_stats['user_data'][user_id] = {
            'user_name': user_name,
            'user_first_name': user_first_name,
            'user_last_name': user_last_name,
            'user_username': user_username,
            'user_chat_id': user_chat_id,
            'start_commands': 0,
            'chart_requests': 0,
            # آمار‌های دیگر را اضافه کنید...
        }
        user_stats['total_users'] += 1

    user_stats['user_data'][user_id]['start_commands'] += 1
    user_stats['start_commands_total'] += 1

def show_admin_stats(message):
    admin_id = 253236793  # آیدی تلگرام شما

    total_users = user_stats['total_users']  # تعداد کل کاربران
    start_commands_total = user_stats['start_commands_total']  # تعداد کل دستورهای /start
    chart_requests_total = user_stats['chart_requests_total']  # تعداد کل درخواست‌های نمایش چارت

    stats_message = f"آمار کلی ربات:\nتعداد کل کاربران: {total_users}\n"
    stats_message += f"تعداد کل دستورهای /start: {start_commands_total}\n"
    stats_message += f"تعداد کل درخواست‌های نمایش چارت: {chart_requests_total}\n"

    for user_id, stats in user_stats['user_data'].items():
        user_name = stats['user_name']
        user_first_name = stats['user_first_name']
        user_last_name = stats['user_last_name']
        user_username = stats['user_username']

        stats_message += f"کاربر {user_name} با شناسه {user_id}:\n"
        stats_message += f"  نام: {user_first_name}\n"
        stats_message += f"  فامیل: {user_last_name}\n"
        stats_message += f"  آیدی حروفی: {user_username}\n"

    bot.send_message(admin_id, stats_message)

@bot.message_handler(commands=["stats"])
def show_stats_command(message):
    show_admin_stats(message)  # ارسال پیام به تابع show_admin_stats با ورودی پیام کاربر


@bot.message_handler(func=lambda message: message.text == 'بازگشت به منوی اصلی')
def back_to_main_menu(message):
    bot.send_message(message.chat.id, "منو اصلی:", reply_markup=main_menu_keyboard())

# تابع برای بررسی متن نامعتبر
def is_invalid_text(message_text):
    # لیست منوها
    valid_menus = ['گروه های درسی', 'پشتیبانی', 'چارت درسی',
                    'مشاوره انتخاب واحد', 'درباره ما', 'راهنما',
                      "منوی مدیر:" , "مهندسی کامپیوتر", 'مهندسی فناوری اطلاعات'
                       ,'هوش مصنوعی', 'نرم افزار','پردازش موازی', 'معماری سیستم های کامپیوتری' ,'بازگشت به منو چارت درسی' ,
                        'شبکه های کامپیوتری' ,'تجارت الکترونیکی','دانلود چارت نرم افزار','دانلود چارت ',
                        "اینستاگرام توسعه دهنده" ,"تماس با توسعه دهنده", "کانال ارشد کامپیوتر" ,"راهنما چارت درسی",
                         "راهنما گروه های درسی","دانلود چارت تجارت الکترونیکی","دانلود چارت تجارت الکترونیکی", "دانلود چارت شبکه های کامپیوتری"
                         ,"دانلود چارت معماری سیستم های کامپیوتری","دانلود چارت هوش مصنوعی",
                          "کانال و گروه ارشد کامپیوتر",'بازگشت به منو قبلی', "/admin", "/stats","/send",
                          'آزمون نرم افزار','امنیت شبکه پیشرفته','رایانش ابری','ارزیابی سیستم های کامپیوتری','رایانش تکاملی' ]

    # بررسی اینکه متن در لیست منوها قرار دارد یا نه
    return message_text not in valid_menus

@bot.message_handler(func=lambda message: is_invalid_text(message.text))
def handle_invalid_text(message):
    bot.send_message(message.chat.id, "پیام نامعتبر! لطفاً از منوها برای ارسال پیام استفاده کنید.")

    bot.send_message(message.chat.id, "منو اصلی:", reply_markup=main_menu_keyboard())


def main_menu_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton('پشتیبانی'), telebot.types.KeyboardButton('گروه های درسی'), telebot.types.KeyboardButton('چارت درسی'))
    keyboard.add(telebot.types.KeyboardButton('مشاوره انتخاب واحد'), telebot.types.KeyboardButton('درباره ما'), telebot.types.KeyboardButton('راهنما'))  # اضافه کردن دکمه‌های منوی جدید
    return keyboard

def group_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('رایانش ابری'), types.KeyboardButton('آزمون نرم افزار'))
    keyboard.add(types.KeyboardButton('رایانش تکاملی'), types.KeyboardButton('پردازش موازی'))
    keyboard.add(types.KeyboardButton('ارزیابی سیستم های کامپیوتری'), types.KeyboardButton('امنیت شبکه پیشرفته'))
    keyboard.add(types.KeyboardButton('بازگشت به منوی اصلی'))
    return keyboard


@bot.message_handler(func=lambda message: message.text == 'مهندسی کامپیوتر')
def engineering_selected(message):
    engineering_menu(message)

@bot.message_handler(func=lambda message: message.text == 'مهندسی فناوری اطلاعات')
def it_engineering_selected(message):
    it_engineering_menu(message)

# تابع نمایش منوی مشاوره انتخاب واحد
def consultation_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('مشاوره انتخاب واحد'))
    return keyboard

def support_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('لغو ارسال پیام و بازگشت به منوی اصلی'))
    return keyboard

@bot.message_handler(func=lambda message: message.text == 'پشتیبانی')
def support_menu_selected(message):
    user_id = message.from_user.id
    user_messages.setdefault(user_id, {'support_messages': [], 'consultation_messages': []})

    bot.send_message(message.chat.id, "لطفاً پیام خود را ارسال کنید.", reply_markup=support_menu_keyboard())
    bot.register_next_step_handler(message, process_support_message)



@bot.message_handler(func=lambda message: message.text == 'مشاوره انتخاب واحد')
def consultation_menu_selected(message):
    user_id = message.from_user.id
    user_messages.setdefault(user_id, {'support_messages': [], 'consultation_messages': []})

    bot.send_message(message.chat.id, "لطفاً پیام خود را برای تیم مشاوره انتخاب واحد ارسال کنید:", reply_markup=support_menu_keyboard())
    bot.register_next_step_handler(message, process_consultation_message)


@bot.message_handler(func=lambda message: message.text in ['گروه های درسی', 'پشتیبانی', 'بازگشت به منوی اصلی'])
def menu_selected(message):
    rules_message = ""  # تعریف اولیه متغیر rules_message
    if message.text == 'گروه های درسی':
        current_date = datetime.now()
        if current_date < activation_date:
           bot.send_message(message.chat.id, "این بخش به صورت موقت در دسترس نمی باشد.")
           bot.send_message(message.chat.id, " منو اصلی:", reply_markup=main_menu_keyboard())
   #     else:
            # ارسال پیام قوانین به کاربر
    #        rules_message = """
#قوانین عضویت در گروه های مجموعه ارشد کامپیوتر TJ:

#۱-گروه‌ها و کانال‌های تحت پوشش این ربات هیچ وابستگی به دانشگاه ندارند و به صورت شخصی اداره می‌شوند لذا هرگونه شکایت توسط مدیران مجموعه بررسی می‌شود.

#۲-گروه‌ها برای استفاده دانشجویان ارشد دانشگاه آزاد واحد تهران جنوب ساخته شده است. لذا اگر دانشجوی این دانشگاه نیستید از عضویت در گروه ها بپرهیزید.

#۳-به دلیل جلوگیری از تبدیل شدن گروه‌ها به بنگاه‌های تبلیغاتی ، از ارسال هرگونه پیام تبلیغاتی در گروه به شدت خودداری فرمایید.در صورت مشاهده برخورد می‌شود.
#--->> در صورت نیاز به تبلیغات هدفمند با مدیریت مجموعه تماس بگیرید.

#۴-ارسال محتوای ضداخلاقی ،فحاشی و ایجاد مزاحمت برای افراد گروه در هریک از گروه‌های مطلق به مجموعه ارشد کامپیوتر منجر به قطع دسترسی فرد خاطی به کل مجموعه خواهد شد.

#۵-از ارائه هویت خود به کسانی که ادعای ادمین بودن می کنند اکیدا خوداری کنید و موارد مشابه را حتما گزارش دهید.

#ت و جلب رضایت هر چه بیشتر شما از هر چیزی برای ما مهم تر است.
#پیشاپیش بخاطر همکاری در رسیدن به این هدف از شما تشکر می کنیم.🙏🌹

   #     """
      #      keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
       #     button_agree = types.KeyboardButton('موافقم')
       #     button_back = types.KeyboardButton('بازگشت به منوی اصلی')
         #   keyboard.add(button_agree)
       #     keyboard.add(button_back)
       #     bot.send_message(message.chat.id, rules_message, reply_markup=keyboard)
            # ثبت درخواست کاربر برای تایید قوانین
      #      bot.register_next_step_handler(message, process_rules_confirmation)


# تابع برای پردازش تایید قوانین توسط کاربر
def process_rules_confirmation(message):
    if message.text == 'موافقم':
        # ارسال منوانتخاب گروه‌های درسی به کاربر
        bot.send_message(message.chat.id, "کدام گروه درسی را انتخاب می‌کنید؟", reply_markup=group_menu_keyboard())
    elif message.text == 'بازگشت به منوی اصلی':
        # ارسال منوی اصلی به کاربر
        bot.send_message(message.chat.id, "منو اصلی:", reply_markup=main_menu_keyboard())


# تابع ایجاد منوی Inline برای مدیر
def admin_inline_menu():
    markup = InlineKeyboardMarkup()
    send_message_button = InlineKeyboardButton("ارسال پیام به کاربر", callback_data="send_message")
    show_support_button = InlineKeyboardButton("نمایش پیام‌های پشتیبانی", callback_data="show_support")
    show_consultation_button = InlineKeyboardButton("نمایش پیام‌های مشاوره", callback_data="show_consultation")
    show_responded_messages_button = InlineKeyboardButton("پیام‌های پاسخ داده شده", callback_data="show_responded_messages")
    markup.row(send_message_button)
    markup.row(show_support_button, show_consultation_button)
    markup.row(show_responded_messages_button)  # اضافه کردن دکمه نمایش پیام‌های پاسخ داده شده
    return markup

# تابع نمایش منوی مدیر در بخش اصلی
@bot.message_handler(commands=["admin"])
def admin_menu(message):
    admin_id = 253236793  # آیدی تلگرام شما
    if message.from_user.id == admin_id:
        bot.send_message(admin_id, "منو مدیر:", reply_markup=admin_inline_menu())

@bot.callback_query_handler(func=lambda call: call.data == 'show_support')
def show_support_messages_callback(call):
    admin_id = call.from_user.id
    show_support_messages(admin_id)

@bot.callback_query_handler(func=lambda call: call.data == 'show_consultation')
def show_consultation_messages_callback(call):
    admin_id = call.from_user.id
    show_consultation_messages(admin_id)

# تابع برای نمایش پیام‌های پشتیبانی به مدیر
def show_support_messages(admin_id):
   for user_id, messages in user_messages.items():
    for index, support_message in enumerate(messages['support_messages']):
        first_name = support_message['first_name']
        last_name = support_message['last_name']
        time = support_message['time']
        message_text = support_message['message']
        user_message = f"پیام از مدیر:\n\nکاربر: {first_name} {last_name}\n"
        user_message += f"زمان ارسال: {time}\n\n"
        user_message += message_text


        markup = InlineKeyboardMarkup()
        reply_button = InlineKeyboardButton("پاسخ", callback_data=f"reply_{user_id}_support_{index}")
        markup.add(reply_button)

        bot.send_message(admin_id, user_message, reply_markup=markup)

def process_support_message(message):
    if message.text == 'لغو ارسال پیام و بازگشت به منوی اصلی':
        # عملیات لغو ارسال پیام و بازگشت به منو اصلی
        bot.send_message(message.chat.id, "لغو ارسال پیام و بازگشت به منوی اصلی:", reply_markup=main_menu_keyboard())
    else:
        user_id = message.from_user.id
        user_data = user_stats['user_data'].get(user_id, {})
        user_first_name = user_data.get('user_first_name', 'نام ناشناخته')
        user_last_name = user_data.get('user_last_name', 'فامیلی ناشناخته')
        user_username = user_data.get('user_username', 'نام کاربری ناشناخته')
        user_gender = user_data.get('user_gender', 'جنسیت ناشناخته')
        user_birthdate = user_data.get('user_birthdate', 'تاریخ تولد ناشناخته')
        user_profile_link = user_data.get('user_profile_link', 'لینک پروفایل ناشناخته')
        current_time = JalaliDateTime.now().strftime("%Y-%m-%d %H:%M:%S")

        user_messages[user_id]['support_messages'].append({
            'message': message.text,
            'time': current_time,
            'first_name': user_first_name,
            'last_name': user_last_name,
            'user_id': user_id,
            'user_username': user_username,
            'user_gender': user_gender,
            'user_birthdate': user_birthdate,
            'user_profile_link': user_profile_link
        })

        admin_id = 253236793
        admin_message = f"پیام از {user_first_name} {user_last_name}:\n\n"
        admin_message += f"زمان ارسال: {current_time}\n"
        admin_message += f"نام کاربری: {user_username}\n"
        admin_message += f"جنسیت: {user_gender}\n"
        admin_message += f"تاریخ تولد: {user_birthdate}\n"
        admin_message += f"لینک پروفایل: {user_profile_link}\n\n"
        admin_message += message.text

        bot.send_message(admin_id, admin_message)

        markup = InlineKeyboardMarkup()
        reply_button = InlineKeyboardButton("پاسخ", callback_data=f"reply_{user_id}_support_{len(user_messages[user_id]['support_messages']) - 1}")
        markup.add(reply_button)

        bot.send_message(message.chat.id, "ممنون از ارسال پیام شما. پیام شما به پشتیبانی ارسال شد.")
        bot.send_message(message.chat.id, "منو اصلی:", reply_markup=main_menu_keyboard())


def show_consultation_messages(admin_id):
    for user_id, messages in user_messages.items():
        for index, consultation_message in enumerate(messages['consultation_messages']):
            first_name = consultation_message['first_name']
            last_name = consultation_message['last_name']
            time = consultation_message['time']
            message_text = consultation_message['message']
            user_message = f"پیام به تیم مشاور انتخاب واحد:\n\nکاربر: {first_name} {last_name}\n"
            user_message += f"زمان ارسال: {time}\n\n"


            # اضافه کردن پاسخ مدیر اگر وجود داشته باشد
            if 'admin_reply' in consultation_message:
                admin_reply = consultation_message['admin_reply']
                user_message += f"\n\nپاسخ مدیر:\n{admin_reply}"

            # اضافه کردن جزئیات بیشتر
            user_gender = consultation_message['user_gender']
            user_birthdate = consultation_message['user_birthdate']
            user_profile_link = consultation_message['user_profile_link']

            user_message += f"جنسیت: {user_gender}\n"
            user_message += f"تاریخ تولد: {user_birthdate}\n"
            user_message += f"لینک پروفایل: {user_profile_link}\n"
            user_message += message_text

            markup = InlineKeyboardMarkup()
            reply_button = InlineKeyboardButton("پاسخ", callback_data=f"reply_{user_id}_consultation_{index}")
            markup.add(reply_button)

            bot.send_message(admin_id, user_message, reply_markup=markup)


def process_consultation_message(message):
    if message.text == 'لغو ارسال پیام و بازگشت به منوی اصلی':
        # عملیات لغو ارسال پیام و بازگشت به منو اصلی
        bot.send_message(message.chat.id, "لغو ارسال پیام و بازگشت به منوی اصلی:", reply_markup=main_menu_keyboard())
    else:
        user_id = message.from_user.id
        user_data = user_stats['user_data'].get(user_id, {})
        user_first_name = user_data.get('user_first_name', 'نام ناشناخته')
        user_last_name = user_data.get('user_last_name', 'فامیلی ناشناخته')
        user_username = user_data.get('user_username', 'نام کاربری ناشناخته')
        user_gender = user_data.get('user_gender', 'جنسیت ناشناخته')
        user_birthdate = user_data.get('user_birthdate', 'تاریخ تولد ناشناخته')
        user_profile_link = user_data.get('user_profile_link', 'لینک پروفایل ناشناخته')
        current_time = JalaliDateTime.now().strftime("%Y-%m-%d %H:%M:%S")

        user_messages[user_id]['consultation_messages'].append({
            'message': message.text,
            'time': current_time,
            'first_name': user_first_name,
            'last_name': user_last_name,
            'user_id': user_id,
            'user_username': user_username,
            'user_gender': user_gender,
            'user_birthdate': user_birthdate,
            'user_profile_link': user_profile_link
        })

        admin_id = 253236793
        admin_message = f"پیام به تیم مشاور انتخاب واحد از طرف {user_first_name} {user_last_name}:\n\n"
        admin_message += f"زمان ارسال: {current_time}\n"
        admin_message += f"نام کاربری: {user_username}\n"
        admin_message += f"جنسیت: {user_gender}\n"
        admin_message += f"تاریخ تولد: {user_birthdate}\n"
        admin_message += f"لینک پروفایل: {user_profile_link}\n\n"
        admin_message += message.text

        bot.send_message(admin_id, admin_message)

        markup = InlineKeyboardMarkup()
        reply_button = InlineKeyboardButton("پاسخ", callback_data=f"reply_{user_id}_consultation_{len(user_messages[user_id]['consultation_messages']) - 1}")
        markup.add(reply_button)

        bot.send_message(message.chat.id, "پیام شما برای مشاوره انتخاب واحد ارسال شد.")
        bot.send_message(message.chat.id, "منو اصلی:", reply_markup=main_menu_keyboard())


@bot.callback_query_handler(lambda call: call.data.startswith('reply'))
def reply_support_callback(call):
    admin_id = call.from_user.id
    _, user_id, message_type, message_index = call.data.split('_')
    message_index = int(message_index)

    user_message = user_messages.get(int(user_id), {}).get(message_type + '_messages', [])[message_index]
    user_first_name = user_message['first_name']
    user_last_name = user_message['last_name']

    # ارسال پیام جدید به کاربر برای پاسخ
    bot.send_message(admin_id, f"پیام از {user_first_name} {user_last_name}:\n\n{user_message['message']}")
    bot.send_message(admin_id, "لطفاً پاسخ خود را ارسال کنید:")
    bot.register_next_step_handler_by_chat_id(admin_id, process_admin_reply, user_id, message_type, message_index)


def process_admin_reply(message, user_id, message_type, message_index):
    admin_id = message.from_user.id

    # تشخیص نوع پیام بر اساس message_type
    if message_type == 'support':
        message_title = "✅پیام از مدیر:"
    elif message_type == 'consultation':
        message_title = "⚜️پیام از تیم مشاوره انتخاب واحد:"

    # ارسال پاسخ به کاربر
    bot.send_message(int(user_id), f"{message_title}\n\n{message.text}")

    # ذخیره پاسخ در لیست پیام‌های پاسخ داده شده
    responded_message = user_messages[int(user_id)][message_type + '_messages'][int(message_index)]
    responded_message['admin_reply'] = message.text

    # ارسال پیام موفقیت به مدیر
    bot.send_message(admin_id, f"پیام شما به کاربر ارسال شد.")


@bot.callback_query_handler(func=lambda call: call.data == 'show_responded_messages')
def show_responded_messages_callback(call):
    admin_id = call.from_user.id
    show_responded_messages(admin_id)


def show_responded_messages(admin_id):
    for user_id, messages in user_messages.items():
        for index, support_message in enumerate(messages['support_messages']):
            if 'admin_reply' in support_message:
                first_name = support_message['first_name']
                last_name = support_message['last_name']
                time = support_message['time']
                message_text = support_message['message']
                admin_reply = support_message['admin_reply']

                user_message = f"پیام از مدیر به {first_name} {last_name}:\n\n"
                user_message += f"زمان ارسال: {time}\n\n"
                user_message += f"متن پیام: {message_text}\n\n"
                user_message += f"پاسخ مدیر:\n{admin_reply}"

                bot.send_message(admin_id, user_message)



@bot.message_handler(func=lambda message: message.text == 'بازگشت به منو چارت درسی')
def back_to_chart_menu(message):
    show_chart_menu(message)

def show_chart_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    engineering_menu_button = types.KeyboardButton('مهندسی کامپیوتر')
    it_engineering_menu_button = types.KeyboardButton('مهندسی فناوری اطلاعات')
    back_to_main_menu_button = types.KeyboardButton('بازگشت به منوی اصلی')
    markup.row(it_engineering_menu_button, engineering_menu_button)
    markup.row(back_to_main_menu_button)
    bot.send_message(message.chat.id, "لطفاً رشته خود را انتخاب کنید:", reply_markup=markup)

def engineering_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    ai_button = types.KeyboardButton('هوش مصنوعی')
    software_button = types.KeyboardButton('نرم افزار')
    memari_button = types.KeyboardButton('معماری سیستم های کامپیوتری')
    back_to_chart_menu_button = types.KeyboardButton('بازگشت به منوی چارت درسی')
    markup.row(ai_button, software_button)
    markup.row(memari_button)
    markup.row(back_to_chart_menu_button)
    bot.send_message(message.chat.id, "لطفاً گرایش خود را انتخاب کنید:", reply_markup=markup)



def it_engineering_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    network_button = types.KeyboardButton('شبکه های کامپیوتری')
    e_commerce_button = types.KeyboardButton('تجارت الکترونیکی')
    back_to_chart_menu_button = types.KeyboardButton('بازگشت به منوی چارت درسی')
    markup.row(network_button, e_commerce_button)
    markup.row(back_to_chart_menu_button)
    bot.send_message(message.chat.id, "لطفاً گرایش مهندسی فناوری اطلاعات خود را انتخاب کنید:", reply_markup=markup)


# ایجاد دیکشنری برای نگه‌داری نام گرایش و لینک تصویر
chart_images = {
    'نرم افزار': 'https://www.uplooder.net/img/image/45/d2e430e6c97f8d976c263d982a177823/Software-Chart-CArshad.png',
    'هوش مصنوعی': 'https://www.uplooder.net/img/image/61/a33bc4dba2fdddab4159a8fde7e12b96/Artificial-Intelligence-Chart-CArshad.png',
    'معماری سیستم های کامپیوتری': 'https://www.uplooder.net/img/image/29/190ab3461d595ff868d49fdfc0b03482/Computer-Systems-Architecture-Chart-CArshad.png',
    'شبکه های کامپیوتری': 'https://www.uplooder.net/img/image/76/6c468d6d98d8e3668ba60478ad0cc9e8/Computer-Network-Chart-CArshad.png',
    'تجارت الکترونیکی': 'https://www.uplooder.net/img/image/6/0d40cbad4c183fda720706d92755ed4d/Commerce-Trends-Chart-CArshad.png'
}

@bot.message_handler(func=lambda message: message.text in chart_images.keys())
def select_chart(message):
    chart_name = message.text
    bot.send_message(message.chat.id, f"شما چارت '{chart_name}' را انتخاب کرده‌اید.")

    if chart_name in chart_images:
        bot.send_photo(message.chat.id, chart_images[chart_name])

    # اضافه کردن گزینه دانلود به منو
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    download_button = types.KeyboardButton(f'دانلود چارت {chart_name}')
    back_to_chart_menu_button = types.KeyboardButton('بازگشت به منو چارت درسی')
    markup.row(download_button)
    markup.row(back_to_chart_menu_button)
    bot.send_message(message.chat.id, "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)


# دستور نمایش منوی چارت درسی پس از انتخاب گزینه "چارت درسی"
@bot.message_handler(func=lambda message: message.text == 'چارت درسی')
def chart_menu(message):
    show_chart_menu(message)

    # ذخیره نام گزینه منوی چارت درسی در متغیر موقت برای استفاده در توابع بعدی
    menu_stack.append("chart_menu")

# منو دانلود چارت
@bot.message_handler(func=lambda message: message.text.startswith('دانلود چارت'))
def download_chart(message):
    chart_name = message.text.replace('دانلود چارت ', '')  # دریافت نام چارت
    chart_image_url = None

    if chart_name == 'نرم افزار':
        chart_image_url = 'https://www.uplooder.net/img/image/45/d2e430e6c97f8d976c263d982a177823/Software-Chart-CArshad.png'
    elif chart_name == 'هوش مصنوعی':
        chart_image_url = 'https://www.uplooder.net/img/image/61/a33bc4dba2fdddab4159a8fde7e12b96/Artificial-Intelligence-Chart-CArshad.png'
    elif chart_name == 'معماری سیستم های کامپیوتری':
        chart_image_url = 'https://www.uplooder.net/img/image/29/190ab3461d595ff868d49fdfc0b03482/Computer-Systems-Architecture-Chart-CArshad.png'
    elif chart_name == 'شبکه های کامپیوتری':
        chart_image_url = 'https://www.uplooder.net/img/image/76/6c468d6d98d8e3668ba60478ad0cc9e8/Computer-Network-Chart-CArshad.png'
    elif chart_name == 'تجارت الکترونیکی':
        chart_image_url = 'https://www.uplooder.net/img/image/6/0d40cbad4c183fda720706d92755ed4d/Commerce-Trends-Chart-CArshad.png'

    if chart_image_url:
        bot.send_document(message.chat.id, chart_image_url)  # ارسال فایل به کاربر (استفاده از لینک آنلاین برای دانلود)


def help_menu_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton('راهنما گروه های درسی'), telebot.types.KeyboardButton('راهنما چارت درسی'))
    keyboard.row(telebot.types.KeyboardButton('بازگشت به منوی اصلی'))  # اضافه کردن کلید "بازگشت به منواصلی" به ردیف جدید
    return keyboard


@bot.message_handler(func=lambda message: message.text == 'راهنما')
def help_menu(message):
    bot.send_message(message.chat.id, "منو راهنما:", reply_markup=help_menu_keyboard())

@bot.message_handler(func=lambda message: message.text == 'راهنما گروه های درسی')
def help_chart_menu(message):
    response = """راهنما گروه های درسی:\n
 برای حفظ امتیت گروه های درسی و دانشجویی و برای جلوگیری از بعضی مشکلات و سوءاستفاده برخی کاربران از گروه‌های درسی و دانشجویی، فرایند ارائه لینک فقط برای کاربران تایید شده صورت می گیرد.

برای تایید حساب و همچنین استفاده از لینک‌های این ربات لازم است روی دکمه "ارسال شماره تلفن" کلیک کرده و شماره تلفن خود را با ربات به اشتراک بگذارید.

تنها کاربران با شماره تلفن ایران امکان استفاده از ربات را دارند.

شماره شما به هیچ عنوان ذخیره نمی شود و صرفا همین یکبار توسط ربات مورد سنجش قرار می گیرد

و برای حفظ امنیت گروه های درسی و دانشجویی لینک های گروه ها فقط مختص ورود شما می باشد و بعد از چند دقیقه غیر فعال می شوند ،به همین دلیل در صورت غیر فعال شدن لینک می توانید مجدد درخواست دریافت لینک دهید.
    """
    bot.send_message(message.chat.id, response, reply_markup=help_menu_keyboard())

@bot.message_handler(func=lambda message: message.text == 'راهنما چارت درسی')
def help_chart_menu(message):
    bot.send_message(message.chat.id, """راهنمای چارت درسی:\n
شما می توانید با انتخاب منو "چارت درسی"
به چارت های درسی تمام گرایش های ارشد، رشته مهندسی کامپیوتر و رشته مهندسی فناوری اطلاعات دانشگاه تهران جنوب دسترسی پیدا کنید.
و از طریق گزینه "دانلود" چارت مورد نظر خود را دریافت کنید.

                     """, reply_markup=help_menu_keyboard())


def about_menu_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton('کانال و گروه ارشد کامپیوتر'), telebot.types.KeyboardButton('تماس با توسعه دهنده'))
    keyboard.row(telebot.types.KeyboardButton('بازگشت به منوی اصلی'))  # اضافه کردن کلید "بازگشت به منوی اصلی" به ردیف جدید
    return keyboard


@bot.message_handler(func=lambda message: message.text == 'کانال و گروه ارشد کامپیوتر')
def open_channel(message):
    # ایجاد دکمه‌های inline برای لینک کانال و گروه
    channel_button = types.InlineKeyboardButton('کانال ارشد کامپیوتر', url='https://t.me/CArshad')
    group_button = types.InlineKeyboardButton('گروه ارشد کامپیوتر', url='https://t.me/CArshaad')  # جایگزین XXXXXXXXXXXXXXXXXX با لینک گروه واقعی شما شود

    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(channel_button)
    inline_markup.add(group_button)

    bot.send_message(message.chat.id, "برای مشاهده کانال و گروه ارشد کامپیوتر روی دکمه‌های زیر بزنید.", reply_markup=inline_markup)

# دستور برای اکانت اینستاگرام توسعه دهنده
@bot.message_handler(func=lambda message: message.text == 'تماس با توسعه دهنده')
def open_chat_with_developer(message):
    # ایجاد دکمه inline برای ورود به چت با توسعه دهنده
    contact_developer_button = types.InlineKeyboardButton('پیام به توسعه دهنده', url='https://t.me/iman588')
    instagram_button = types.InlineKeyboardButton('اینستاگرام توسعه دهنده', url='https://www.instagram.com/iman588/')

    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(contact_developer_button)
    inline_markup.add(instagram_button)

    bot.send_message(message.chat.id, "برای ارسال پیام به توسعه دهنده یا مشاهده اینستاگرام توسعه‌دهنده، از دکمه‌های زیر استفاده کنید.", reply_markup=inline_markup)


@bot.message_handler(func=lambda message: message.text == 'درباره ما')
def about_menu(message):
    bot.send_message(message.chat.id, """منو درباره ما:\n
در ربات ارشد کامپیوتر به امکانات زیر دسترسی دارید:

۱-چارت درسی تمامی گرایش های ارشد مهندسی کامپیوتر و مهندسی فناوری اطلاعات با امکان دانلود

۲-لینک گروه های درسی ارشد کامپیوتر با الگوریتم ویژه و غیر قابل دسترس افراد متفرقه

۳-پشتیبانی مستقیم ربات
---> هرگونه مشکل ،سؤال ،انتقاد و پیشنهادی دارید می توانید با پشتیبانی در میان بگذارید در سریع تر زمان جواب شما داده خواهد شد.

مجموعه ارشد کامپیوتر TJ با هدف تسهیل و ساده‌تر کردن مسیر یادگیری شما، تمام تلاش خود را برای کاهش مشکلات و موانع در مسیر تحصیلی‌تان انجام می‌دهد. از  اینکه در این مسیر کنار ما هستید کمال قدردانی را داریم. 🌹🌱

با تشکر
ایمان شاهقلیان-@iman588
طراح ربات و مدیریت مجموعه ارشد کامپیوتر              """, reply_markup=about_menu_keyboard())


# group_chat_ids = {
  #  'آزمون نرم افزار': -905339162,
  #  'رایانش ابری': -1001813717145,
  #  'پردازش موازی': -1001920870599,
   # 'امنیت شبکه پیشرفته': -1001769484991,
   # 'ارزیابی سیستم های کامپیوتری': -1001735421246,
  #  'رایانش تکاملی': -1001732405225
#}

# تابع برای تولید لینک جدید گروه
# def generate_new_group_link(group_chat_id):
  #  try:
   #     new_link = bot.export_chat_invite_link(group_chat_id)
   #     return new_link
   # except Exception as e:
  #      print(f"An error occurred while generating the group link: {e}")
   #     return None


# تابع برای ارسال لینک گروه به کاربر
# def send_group_link_to_user(message, group_name):
  #  user_id = message.from_user.id
  #  group_chat_id = group_chat_ids.get(group_name)
  #  if group_chat_id is not None:
   #     group_link = generate_new_group_link(group_chat_id)
   #     group_info = bot.get_chat(group_chat_id)
   #     group_title = group_info.title
  #      bot.send_message(user_id, f"لینک گروه '{group_title}': {group_link}")
   # else:
  #      bot.send_message(user_id, "گروه مورد نظر یافت نشد.")

# تابع برای تغییر لینک گروه
# def change_group_link_and_notify():
 #  for group_name, group_chat_id in group_chat_ids.items():
   #     new_group_link = generate_new_group_link(group_chat_id)

# زمان‌بندی تغییر لینک گروه
# schedule.every(2).minutes.do(change_group_link_and_notify)

# تابع برای اجرای زمان‌بندی
# def scheduler():
 #   while True:
    #    schedule.run_pending()
    #    time.sleep(1)

# رشته غیرقابل توقف برای اجرای برنامه‌های زمان‌بندی شده و شروع ربات
# import threading
# schedule_thread = threading.Thread(target=scheduler)
# schedule_thread.start()

# تابع برای بررسی شماره تلفن ایرانی بودن
# def is_iranian_phone_number(phone_number):
    # اینجا می‌توانید منطق خودتان برای بررسی شماره ایرانی بودن اضافه کنید
    # به طور مثال، بررسی پیشوند کد کشوری
 #   iranian_prefixes = ["+98", "0098", "98"]
 #   for prefix in iranian_prefixes:
  #      if phone_number.startswith(prefix):
   #         return True
  #  return False

# دستور برای بازگشت به منوی قبلی
@bot.message_handler(func=lambda message: message.text == 'بازگشت به منو قبلی')
def back_to_group_menu(message):
    bot.send_message(message.chat.id, "منو گروه‌های درسی:", reply_markup=group_menu_keyboard())

bot.polling()

#@bot.message_handler(func=lambda message: message.text in group_chat_ids.keys())
#def select_group(message):
  #  group_name = message.text
  #  user_id = message.from_user.id
  #  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  #  item = types.KeyboardButton('ارسال شماره تلفن', request_contact=True)
  #  back_button = types.KeyboardButton('بازگشت به منو قبلی')
   # markup.row(item)
  #  markup.row(back_button)
#   bot.send_message(message.chat.id, """
#برای دریافت لینک گروه، لطفاً شماره تلفن خود را ارسال کنید.

#--> برای حفظ امتیت گروه های درسی و دانشجویی و برای جلوگیری از بعضی مشکلات و سوءاستفاده برخی کاربران، فرایند ارائه لینک فقط برای کاربران تایید شده صورت می گیرد.

#برای تایید حساب و همچنین استفاده از لینک‌های این ربات لازم است روی دکمه "ارسال شماره تلفن" کلیک کرده و شماره تلفن خود را با ربات به اشتراک بگذارید.

#تنها کاربران با شماره تلفن ایران امکان استفاده از ربات را دارند.

#شماره شما به هیچ عنوان ذخیره نمی شود و صرفا توسط ربات مورد سنجش قرار می گیرد.
#                     """
#                     , reply_markup=markup)

    # ذخیره نام گروه در متغیر موقت برای استفاده در تابع بعدی
#    menu_stack.append(group_name)


# دستور برای دریافت شماره تلفن از کاربر و ارسال لینک به او
#@bot.message_handler(content_types=['contact'])
#def get_contact(message):
 #   user_id = message.from_user.id
 #   if message.contact is not None:
  #      if is_iranian_phone_number(message.contact.phone_number):
  #          if user_completed_steps.get(user_id):
                # کاربر قبلاً تایید و مراحل را تکمیل کرده است، بنابراین لینک گروه را ارسال کنید
    #            send_group_link_to_user(message, menu_stack[-1])
    #        else:
                # کاربر تازه شماره تلفن خود را تایید کرده
     #           user_completed_steps[user_id] = True
     #           send_group_link_to_user(message, menu_stack[-1])
      #          bot.send_message(user_id, "شماره تلفن شما تایید شد. ")
                # حذف منوی ارسال شماره از مرحله‌ها
      #          if 'group_menu' in menu_stack:
       #             menu_stack.remove('group_menu')
       #     return
      #  else:
       #     bot.reply_to(message, "لینک گروه فقط برای شماره‌های ایرانی ارسال می‌شود.")



# مرحله 1: دریافت آیدی عددی کاربر
@bot.message_handler(commands=['send'])
def ask_for_user_id(message):
    chat_id = message.chat.id
    print("دستور /send دریافت شد")  # برای گزارش‌گیری
    msg = bot.reply_to(message, "لطفاً آیدی عددی کاربر را وارد کنید:")
    bot.register_next_step_handler(msg, process_user_id_step)

def process_user_id_step(message):
    chat_id = message.chat.id
    user_id = message.text

    # ذخیره آیدی عددی کاربر
    user_data[chat_id] = {'user_id': user_id}

    # مرحله 2: دریافت پیشوند پیام
    msg = bot.reply_to(message, "لطفاً پیشوند پیام (مثلاً 'از طرف تیم ...') را وارد کنید:")
    bot.register_next_step_handler(msg, process_prefix_step)

def process_prefix_step(message):
    chat_id = message.chat.id
    prefix = message.text

    # ذخیره پیشوند پیام
    user_data[chat_id]['prefix'] = prefix

    # مرحله 3: دریافت متن پیام
    msg = bot.reply_to(message, "لطفاً متن پیام را وارد کنید:")
    bot.register_next_step_handler(msg, process_message_text_step)

def process_message_text_step(message):
    chat_id = message.chat.id
    message_text = message.text

    # ذخیره متن پیام
    user_data[chat_id]['message_text'] = message_text

    # ارسال پیام به کاربر مورد نظر
    send_message_to_user(chat_id)

def send_message_to_user(chat_id):
    try:
        user_id = user_data[chat_id]['user_id']
        prefix = user_data[chat_id]['prefix']
        message_text = user_data[chat_id]['message_text']

        # ترکیب پیشوند با متن پیام
        full_message = f"{prefix}\\n\\n{message_text}"

        # ارسال پیام به کاربر مورد نظر
        bot.send_message(user_id, full_message)
        bot.send_message(chat_id, f"پیام با موفقیت به کاربر {user_id} ارسال شد.")
    except Exception as e:
        bot.send_message(chat_id, f"خطا در ارسال پیام: {str(e)}")

if __name__ == "__main__":
    bot.polling(none_stop=True)
