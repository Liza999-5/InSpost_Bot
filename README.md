database.py

init_db -> создает 3 таблицы nutrition(для состояния юзера типо сколько уже съел), meals(все блюда(вот тут важно что хранятся все блюда, я просто выбираю из них те что относятся к юзеру по его id и за сегоднящний день по date)), daily_goals(норма для каждого юзера)

checkIsTodayCreate -> создает запись о состоянии клиента(nutrition) если она не создана

getNorm -> делает запроос к бд и возвращает норму кбжу(массив из 4 переменных) для юзера

setNorm -> а эта штука задает норму

get_daily_stats -> возвращает текующее состояние за день по калориям юзера и блюда которые он съел

add_meal -> добавляет блюдо в таблицу

convert.py

from googletrans import Translator -> переводчик на русский/английский чтоб делать запросы и возвращать правильный результат

convertTxt -> делает запрос по апи по блюду который пользователь ввел вручную

converImage -> аналогично только с картинкой

обе функции возвращают кбжу и функция для картинки дополнительно возвращает название блюда

app.py

get_stat_message -> возвращает красивую статистику со смайликами и тд

get_date -> возвращает сегодняшнюю дату в формате "13 мая"

my_goals_message -> возвращает красивые цели питания со смайликами тд

get_history -> возвращает красивую историю блюд со смайликами тд

calculate_bmr -> считает базовый метаболизм (нужен для формулы сан жерона)

@bot.message_handler(commands=["start"])
def send_welcome(message) -> приветствует юзера по команде start, добавляет панельку в которой можно понажимать кнопки

@bot.message_handler(func=lambda message: message.text == "📊 Мой день") -> для обработки вывода статистики. Сюда человек попадает когда нажимает кнопку

@bot.message_handler(func=lambda message: message.text == "🎯 Цели") -> тоже самое только с целями

@bot.message_handler(func=lambda message: message.text == "📅 История") -> тоже самое только с историей прима пищи

@bot.message_handler(func=lambda message: message.text == "✏️ Добавить блюдо") -> Начинает диалог по дабовлению блюда

@bot.callback_query_handler(func=lambda call: call.data == 'addmeal') -> если вручную добавляет

@bot.callback_query_handler(func=lambda call: call.data == 'addmealimg') -> если через фото

@bot.callback_query_handler(func=lambda call: call.data == 'setNorm') -> задать цель

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) is not None) -> обработка добавления блюда, функции для бд, convert

@bot.message_handler(content_types=['photo']) -> для фотки

@bot.callback_query_handler(func=lambda call: call.data == 'setAutoNorm')-> задача цели через анкету. старт диалога

@bot.callbackquery_handler(func=lambda call: call.data.startswith('gender\*')) -> пол

@bot.message_handler(func=lambda m: m.chat.id in user_data and 'gender' in user_data[m.chat.id] and 'age' not in user_data[m.chat.id]) -> возраст

@bot.message_handler(func=lambda m: m.chat.id in user_data and 'height' not in user_data[m.chat.id]) -> рост

@bot.message_handler(func=lambda m: m.chat.id in user_data and 'weight' not in user_data[m.chat.id]) -> вес

ask_activity -> активность

@bot.callback_query_handler(func=lambda call: call.data.startswith('act\*')) -> ее обработка и нацонец предподсчет всех данных для задания нормы
