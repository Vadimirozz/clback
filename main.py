# Строчка 175, 9, 12, 13, 15, 16 Поменять данные на свои.

import telebot 
from telebot import types
import sqlite3
import threading
import time

BOT_TOKEN = "6469730797:AAE9RHOw4xZUUvsotUYMkRtZvk_1JliJXgE"
bot = telebot.TeleBot(BOT_TOKEN)

channel_id = '@cryptochannel123456' # канал телеграм на который надо подписаться
chat_id = '@cryptochat123456' # чат телеграм, на который надо подписаться

twitter_account = "https://twitter.com/elonmusk" # Адрес аккаунта, на который надо подписаться
retweet = "https://inlnk.ru/Bpz0xZ" # адрес твита, который надо ретвитнуть

pressed_buttons = {} # Отслеживаем состояние кнопок (проверка подписки, ретвита и тд)
complete_sub = {} # Отслеживаем, подписан ли человек
complete_retweet = {} # Отслеживаем, сделал ли человек ретвит


# Функция для создания соединения с базой данных SQLite
def create_connection():
    return sqlite3.connect('users.db')

# Функция для сохранения адреса криптокошелька в базе данных
def save_wallet_address(user_id, wallet_address):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO wallets (user_id, wallet_address) VALUES (?, ?)", (user_id, wallet_address))
    conn.commit()
    conn.close()

# Функция для получения адреса криптокошелька из базы данных
def get_wallet_address(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT wallet_address FROM wallets WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

# Создаем таблицу для хранения адресов криптокошельков и ID пользователей
def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS wallets
                      (user_id INTEGER PRIMARY KEY, wallet_address TEXT)''')
    conn.close()

create_table()

# Переменная состояния для отслеживания диалога с пользователем
user_state = {}

# Функция для проверки подписки пользователя
def check_subscription(user_id):
    try:
        user_channels = bot.get_chat_member(channel_id, user_id)
        user_chat = bot.get_chat_member(chat_id, user_id)
        return user_channels.status == 'member' and user_chat.status == 'member'
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        return False


@bot.message_handler(commands=['adminsubs'])
def handle_admin(message):
    # Создаем подключение к базе данных
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        # Запрашиваем количество подписчиков из базы данных
        cursor.execute("SELECT COUNT(*) FROM wallets")
        count = cursor.fetchone()[0]
        bot.reply_to(message, f"Количество зарегистрированных кошельков: {count}")


@bot.message_handler(commands=['display'])
def display_wallet_addresses(message):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wallets")
    rows = cursor.fetchall()
    conn.close()

    if rows:
        addresses_string = "Содержимое базы данных:\n"
        for row in rows:
            user_id, wallet_address = row
            addresses_string += f"User ID: {user_id}, Wallet Address: {wallet_address}\n"
        bot.reply_to(message, addresses_string)
    else:
        bot.send_message(chat_id, "База данных пуста.")



@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    item_subscribe = types.KeyboardButton('/subscribe')
    markup.add(item_subscribe)
    bot.send_message(message.chat.id, "Hi. Click /subscribe to get our community bonuses.", reply_markup=markup)

@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    print("subscribe")
    subscribe_markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton(text='👾Channel', url='https://t.me/cryptochannel123456')
    btn2 = types.InlineKeyboardButton(text='💬Chat', url='https://t.me/cryptochat123456')
    btn3 = types.InlineKeyboardButton(text='🐦Twitter', callback_data="twitter_button")
    subscribe_markup.add(btn1, btn2)
    subscribe_markup.add(btn3)
    btn4 = types.InlineKeyboardButton(text='Check: 🌀', callback_data="check")
    subscribe_markup.add(btn4)

    bot.send_message(message.chat.id, "Subscribe and get free coins of our project!", reply_markup=subscribe_markup)

# Обработчик сообщений, в котором пользователь отправляет адрес кошелька
@bot.message_handler(func=lambda message: message.from_user.id in user_state and user_state[message.from_user.id] == 'awaiting_wallet_address')
def handle_wallet_address(message):
    user_id = message.from_user.id
    wallet_address = message.text

    # Сохраняем адрес криптокошелька пользователя в базе данных
    save_wallet_address(user_id, wallet_address)
    bot.send_message(message.chat.id, "Your crypto wallet address has been successfully saved!")

    # Удаляем состояние ожидания адреса кошелька
    del user_state[user_id]



#все callbacks для кнопок. markup менять не следует. Некоторые из них дублируются, тк бот изменяет сообщения после изменения состояния кнопок.
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    markup2 = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton(text='👾Channel', url='https://t.me/cryptochannel123456')
    btn2 = types.InlineKeyboardButton(text='💬Chat', url='https://t.me/cryptochat123456')
    btn3 = types.InlineKeyboardButton(text='🐦Twitter', url='https://twitter.com/elonmusk', callback_data="twitter_button")
    markup2.add(btn1, btn2)
    markup2.add(btn3)
    btn4 = types.InlineKeyboardButton(text='✅', callback_data="none")
    markup2.add(btn4)

    markup_l = types.InlineKeyboardMarkup(row_width=True)
    markup_a = types.InlineKeyboardMarkup(row_width=True)
    btn_l = types.InlineKeyboardButton(text='👍', callback_data='accept_sub')
    btn_a = types.InlineKeyboardButton(text='✅', callback_data="none")
    markup_l.add(btn_l)
    markup_a.add(btn_a)

    markup_l_r = types.InlineKeyboardMarkup(row_width=True)
    markup_a_r = types.InlineKeyboardMarkup(row_width=True)
    btn_l_r = types.InlineKeyboardButton(text='👍', callback_data='accept_retweet')
    btn_a_r = types.InlineKeyboardButton(text='✅', callback_data="none")
    markup_l_r.add(btn_l_r)
    markup_a_r.add(btn_a_r)

    markup_menu = types.InlineKeyboardMarkup(row_width=2)
    sub_btn = types.InlineKeyboardButton(text='Subscribe', callback_data='sub_menu')
    retweet_btn = types.InlineKeyboardButton(text='Retweet', callback_data="retweet_menu")
    markup_menu.add(sub_btn, retweet_btn)

    if call.data in ['twitter_button']:
        bot.answer_callback_query(call.id, "Subscribe and retweet!")
        bot.send_message(call.message.chat.id, "Subscribe and retweet!", reply_markup=markup_menu)

        chat_id = call.message.chat.id
        if chat_id not in pressed_buttons:
            pressed_buttons[chat_id] = set()
        pressed_buttons[chat_id].add(call.data)

    if call.data == 'check':
        chat_id = call.message.chat.id
        allowed_user_id = 6935055453 # Поменяйте на айди человека, на которого сделан бот в botfather
        if check_subscription(call.from_user.id) and complete_sub.get(chat_id) == {"accept_sub"} and complete_retweet.get(chat_id) == {"accept_retweet"} or call.from_user.id == allowed_user_id:
            bot.answer_callback_query(call.id, "You're already subscribed to the channel and chat!")
            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Subscribe and get free coins of our project!", reply_markup=markup2)
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id + 1)
                user_state[call.from_user.id] = 'awaiting_wallet_address'  # Устанавливаем состояние ожидания адреса кошелька
                after_checkup(call.message)
            except telebot.apihelper.ApiTelegramException as e:
                bot.send_message(call.message.chat.id, "Something went wrong... Refresh the bot using the /start command.")
                del complete_sub[chat_id]
                del complete_retweet[chat_id]
                print(f"Error editing message: {e}")
        else:
            bot.answer_callback_query(call.id, "Please subscribe to the channel and chat")


    if call.data == 'accept_sub':
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Our Twitter: {twitter_account} - Subscribe so you don't miss project updates!", reply_markup=markup_a)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error editing message: {e}")

        chat_id = call.message.chat.id
        if chat_id not in complete_sub:
            complete_sub[chat_id] = set()
        complete_sub[chat_id].add(call.data)

        time.sleep(1)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


    if call.data == 'accept_retweet':
        user_state[call.from_user.id] = 'awaiting_key_word'
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"You will need to retweet this post: {retweet}", reply_markup=markup_a)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error editing message: {e}")

        chat_id = call.message.chat.id
        if chat_id not in complete_retweet:
            complete_retweet[chat_id] = set()
        complete_retweet[chat_id].add(call.data)

        time.sleep(1)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


    if call.data == 'sub_menu':
        bot.send_message(call.message.chat.id, f"Our Twitter: {twitter_account} - Subscribe so you don't miss project updates!", reply_markup=markup_l)

    if call.data == 'retweet_menu':
        bot.send_message(call.message.chat.id, f"You will need to retweet this post: {retweet}", reply_markup=markup_l_r)


# Функция, которая отправляет сообщение пользователю после проверки
def after_checkup(message):
    first_name = message.chat.first_name
    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f"<strong>{first_name}, you have been successfully verified!</strong> Send your crypto wallet address for tokenization🎁", parse_mode="HTML")
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Error editing message: {e}")


while True:
    try:
        bot.polling()
    except Exception as e:
        print(f"Ошибка при выполнении polling: {e}")
