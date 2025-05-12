import telebot
from telebot import types
from dotenv import load_dotenv
import os
from database import init_db, checkIsTodayCreate, add_meal, get_daily_stats, getNorm, setNorm
from convert import convertTxt, converImage
import asyncio
import io
import datetime

# ---------ENV FILES---------
load_dotenv()
# tokenbot=YOUR_TOKEN_BOT
# API_KEY=YOUR_API_KEY_FOR_SPOONACULAR

file_db = "./db/database.db"
bot = telebot.TeleBot(os.getenv("tokenbot"))

init_db()

user_states = {}


# ------Format output functions-------

def get_stat_message(user_id):
    stats = get_daily_stats(user_id)
    goals = getNorm(user_id)
    if not stats['totals']:
        return "Сегодня пока нет данных."
    c, p, f, ch = stats['totals']
    cg, pg, fg, chg = goals
    reply = f"🎯 Ваш прогресс:\n"
    reply += f"Калории: {c:.1f}/{cg:.1f} ккал\n"
    reply += "".join(["🟩" if (i + 1) * 20 < (c / cg) * 100 else "⬜️" for i in range(5)]) + "\n\n"
    reply += f"Белки: {p:.1f}/{pg:.1f} г\n"
    reply += "".join(["🟩" if (i + 1) * 20 < (p / pg) * 100 else "⬜️" for i in range(5)]) + "\n\n"
    reply+= f"Жиры: {f:.1f}/{fg:.1f} г\n"
    reply += "".join(["🟩" if (i + 1) * 20 < (f / fg) * 100 else "⬜️" for i in range(5)]) + "\n\n"
    reply += f"Углеводы: {ch:.1f}/{chg:.1f} г\n"
    reply += "".join(["🟩" if (i + 1) * 20 < (ch / chg) * 100 else "⬜️" for i in range(5)]) + "\n\n"
    return reply

def get_date():
    months = {
        1: "января", 2: "февраля", 3: "марта",
        4: "апреля", 5: "мая", 6: "июня",
        7: "июля", 8: "августа", 9: "сентября",
        10: "октября", 11: "ноября", 12: "декабря"
    }
    today = datetime.datetime.now()
    day = today.day
    month = months[today.month]
    return f"{day} {month}"

def my_goals_message(user_id):
    goals = getNorm(user_id)
    cg, pg, fg, chg = [int(x) for x in goals]
    reply = f"🎯 Мои цели питания\n\n📊 Дневная норма:\n\n• {cg} ккал\n• {pg} г белков\n• {fg} г жиров\n• {chg} г углеводов"
    return reply

def get_history(user_id):
    stat = get_daily_stats(user_id)['meals']
    reply = f"📅 Сегодня, {get_date()}\n\n"
    if stat:
        reply += "📊Сегодня вы съели:\n"
        for x in stat:
            print(x)
            reply += '• ' + x[0] + '\n'
    else:
        reply += "Пока что вы ничего не съели"
    return reply



# ------Calc data functions------
def calculate_bmr(gender, weight, height, age):
    if gender == 'male':
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

# Команда /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📊 Мой день")
    btn2 = types.KeyboardButton("📅 История")
    btn3 = types.KeyboardButton("🎯 Цели")
    btn4 = types.KeyboardButton("✏️ Добавить блюдо")
    markup.row(btn1, btn2)
    markup.row(btn4, btn3)
    user_id = message.from_user.id
    if user_id in user_states:
        user_states[user_id] = None
    checkIsTodayCreate(user_id)
    bot.send_message(chat_id, "Привет! Напиши, что ты съел, и я скажу, сколько в этом калорий!", reply_markup=markup)
    bot.delete_message(chat_id, message.message_id)
        
        



@bot.message_handler(func=lambda message: message.text == "📊 Мой день")
def stats_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if user_id in user_states:
        user_states[user_id] = None
    reply = f"📅 Сегодня, {get_date()}\n\n" + get_stat_message(user_id)
    bot.send_message(chat_id, reply)
    bot.delete_message(chat_id, message.message_id)
    
@bot.message_handler(func=lambda message: message.text == "🎯 Цели")
def profile_stats(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if user_id in user_states:
        user_states[user_id] = None
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_save = telebot.types.InlineKeyboardButton(text="Вручную",
                                                     callback_data='setNorm')
    button_change = telebot.types.InlineKeyboardButton(text="Заполнить анкету",
                                                     callback_data='setAutoNorm')
    keyboard.add(button_save, button_change)
    bot.send_message(chat_id, my_goals_message(chat_id), reply_markup=keyboard)
    bot.delete_message(chat_id, message.message_id)

    
@bot.message_handler(func=lambda message: message.text == "📅 История")
def profile_stats(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if user_id in user_states:
        user_states[user_id] = None
    
    reply = get_history(user_id)
    bot.send_message(chat_id, reply)
    bot.delete_message(chat_id, message.message_id)

@bot.message_handler(func=lambda message: message.text == "✏️ Добавить блюдо")
def add_choose_meal(message):
    chat_id = message.chat.id
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_save = telebot.types.InlineKeyboardButton(text="Вручную",
                                                     callback_data='addmeal')
    button_change = telebot.types.InlineKeyboardButton(text="Фото",
                                                     callback_data='addmealimg')
    keyboard.add(button_save, button_change)
    bot.send_message(chat_id, "⬇️ Выбери способ чтобы добавить", reply_markup=keyboard)
    bot.delete_message(chat_id, message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'addmeal')
def add_meal_handler(call):
    bot.answer_callback_query(callback_query_id=call.id)
    message = call.message
    chat_id = message.chat.id
    user_id = call.from_user.id
    if user_id in user_states:
        user_states[user_id] = None
    user_states[user_id] = "wait_food"
    bot.send_message(chat_id, "Введи название блюда")
    
@bot.callback_query_handler(func=lambda call: call.data == 'addmealimg')
def add_meal_image_handler(call):
    bot.answer_callback_query(callback_query_id=call.id)
    message = call.message
    chat_id = message.chat.id
    user_id = call.from_user.id
    if user_id in user_states:
        user_states[user_id] = None
    user_states[user_id] = "wait_food_image"
    bot.send_message(chat_id, "Отправь фото блюда")
    
@bot.callback_query_handler(func=lambda call: call.data == 'setNorm')
def add_meal_image_handler(call):
    bot.answer_callback_query(callback_query_id=call.id)
    message = call.message
    chat_id = message.chat.id
    user_id = call.from_user.id
    if user_id in user_states:
        user_states[user_id] = None
    user_states[user_id] = "wait_norm"
    bot.send_message(chat_id, "ККАЛ/БЕЛКИ/ЖИРЫ/УГЛЕВОДЫ\nНапример:\n2380/88/66/359")


#обработка состояний
@bot.message_handler(func=lambda m: user_states.get(m.chat.id) is not None)
def meal_adding(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text.lower().strip()
    if user_id in user_states:
        if user_states.get(user_id) == "wait_food":
            kc, pr, ft, cr = asyncio.run(convertTxt(text))
            if kc != -1:
                add_meal(user_id, text, kc, pr, ft, cr)
                bot.send_message(chat_id, get_stat_message(user_id))
            else:
                bot.send_message(chat_id, "Не нашел такого блюда😭")
        elif user_states.get(user_id) == "wait_norm":
            norm = text.split('/')
            try:
                setNorm(user_id, *[int(x) for x in norm])
                bot.send_message(chat_id, "Данные получены!")
            except:
                bot.send_message(chat_id, "Кажется ты отпраавил данные в неправильном формате")
        else:
            bot.send_message(chat_id, "Не могу ответить на ваш запрос")
        user_states[user_id] = None
        
@bot.message_handler(content_types=['photo'])
def photo(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    fileID = message.photo[-1].file_id   
    file = bot.get_file(fileID)
    downloaded_file = bot.download_file(file.file_path)
    image_stream = io.BytesIO(downloaded_file)
    if user_id in user_states:
        if user_states.get(user_id) == "wait_food_image":
            name, kc, pr, ft, cr = asyncio.run(converImage(image_stream))
            if name != "undf":
                add_meal(user_id, name, kc, pr, ft, cr)
                bot.send_message(chat_id, get_stat_message(user_id))
            else:
                bot.send_message(chat_id, "Не нашел такого блюда😭")
        else:
            bot.send_message(chat_id, "Введи /help для просмотра комманд")
        user_states[user_id] = None

# ----------------setNorm--------
user_data = {}

@bot.callback_query_handler(func=lambda call: call.data == 'setAutoNorm')
def ask_gender(call):
    bot.answer_callback_query(callback_query_id=call.id)
    message = call.message
    chat_id = message.chat.id
    user_data[chat_id] = {}
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Мужской", callback_data='gender_male'),
        types.InlineKeyboardButton("Женский", callback_data='gender_female')
    )
    bot.send_message(chat_id, STEPS['gender'], reply_markup=markup)
    
    
STEPS = {
    'gender': 'Выберите пол:',
    'age': 'Введите возраст:',
    'height': 'Введите рост (см):',
    'weight': 'Введите вес (кг):',
    'activity': 'Выберите уровень активности:'
}

ACTIVITY_FACTORS = {
    'min': 1.2,
    'low': 1.375,
    'medium': 1.55,
    'high': 1.725,
    'extreme': 1.9
}

@bot.callback_query_handler(func=lambda call: call.data.startswith('gender_'))
def handle_gender(call):
    gender = 'male' if call.data == 'gender_male' else 'female'
    user_data[call.message.chat.id]['gender'] = gender
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, STEPS['age'])
    print(user_data)

@bot.message_handler(func=lambda m: m.chat.id in user_data and 'gender' in user_data[m.chat.id] and 'age' not in user_data[m.chat.id])
def handle_age(message):
    try:
        age = int(message.text)
        if age < 1 or age > 120:
            raise ValueError
        user_data[message.chat.id]['age'] = age
        bot.send_message(message.chat.id, STEPS['height'])
    except:
        bot.send_message(message.chat.id, "Введите корректный возраст (число от 1 до 120)")

@bot.message_handler(func=lambda m: m.chat.id in user_data and 'height' not in user_data[m.chat.id])
def handle_height(message):
    try:
        height = int(message.text)
        if height < 50 or height > 250:
            raise ValueError
        user_data[message.chat.id]['height'] = height
        bot.send_message(message.chat.id, STEPS['weight'])
    except:
        bot.send_message(message.chat.id, "Введите корректный рост (в см, от 50 до 250)")

@bot.message_handler(func=lambda m: m.chat.id in user_data and 'weight' not in user_data[m.chat.id])
def handle_weight(message):
    try:
        weight = int(message.text)
        if weight < 30 or weight > 300:
            raise ValueError
        user_data[message.chat.id]['weight'] = weight
        ask_activity(message)
    except:
        bot.send_message(message.chat.id, "Введите корректный вес (в кг, от 30 до 300)")

def ask_activity(message):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("Минимальная", callback_data='act_min'))
    markup.row(types.InlineKeyboardButton("Лёгкие тренировки", callback_data='act_low'))
    markup.row(types.InlineKeyboardButton("Средняя активность", callback_data='act_medium'))
    markup.row(types.InlineKeyboardButton("Высокая активность", callback_data='act_high'))
    markup.row(types.InlineKeyboardButton("Экстремальная", callback_data='act_extreme'))

    bot.send_message(message.chat.id, STEPS['activity'], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('act_'))
def handle_activity(call):
    user_id = call.message.from_user.id
    chat_id = call.message.chat.id
    act_key = call.data[4:]
    user_data[call.message.chat.id]['activity'] = ACTIVITY_FACTORS[act_key]

    bot.delete_message(chat_id, call.message.message_id)

    # Расчёт
    data = user_data[chat_id]
    bmr = calculate_bmr(data['gender'], data['weight'], data['height'], data['age'])
    calories = round(bmr * data['activity'])
    proteins = data['weight'] * 2.2
    fats = data['weight'] * 1
    carbs = round((calories - (proteins * 4 + fats * 9)) / 4)

    setNorm(user_id, calories, proteins, fats, carbs)

    bot.send_message(chat_id, my_goals_message(user_id))
        
    
if __name__ == "__main__":
    print("Запуск бота")
    bot.polling(none_stop=True)