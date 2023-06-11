import json  # загружаем библиотеки
import requests  # загружаем библиотеку для запроса по url адресу
import telebot  # загружаем библиотеку телебота
from telebot import types  # загружаем библиотеку для создания кнопок
from confing import tok, api  # импортируем токен

bot = telebot.TeleBot(tok)  # токен бота
API =  api # api сайта погоды


@bot.message_handler(commands=["start"])  # создаем команду, для старта бота
def start(message):
    bot.send_message(message.chat.id,
                     f'Привет, {message.from_user.first_name}, введите текст')  # обращаемся к пользователю по первому имени


@bot.message_handler(content_types=["text"])  # получпем ответ пользователя
def get_markup(message):
    markup = types.InlineKeyboardMarkup()  # создаем  кнопки в чате
    item1 = types.InlineKeyboardButton(text='Новости', callback_data='Новости')
    item2 = types.InlineKeyboardButton(text='Посмотреть погоду', callback_data='Погода')
    item3 = types.InlineKeyboardButton(text='Курсы валют', callback_data='курсы')
    markup.row(item1, item2, item3)  # указываем на рассположение кнопок
    bot.reply_to(message, 'Выбери, чем помочь', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)  # обрабатываем кнопки
def city_message(callback):
    if callback.data == 'Погода':
        bot.send_message(callback.message.chat.id, 'Введите город: ')
        bot.register_next_step_handler(callback.message, my_weather)
    elif callback.data == 'Новости':
        markup = types.InlineKeyboardMarkup()
        item4 = types.InlineKeyboardButton(text='IT', callback_data='новости', url='https://devby.io')
        item5 = types.InlineKeyboardButton(text='Авто!', callback_data='новости авто', url='https://cars.av.by/')
        markup.row(item4, item5)
        bot.reply_to(callback.message, 'Давайте узнаем последние новости', reply_markup=markup)
    elif callback.data == 'курсы':
        markup = types.InlineKeyboardMarkup()
        item6 = types.InlineKeyboardButton(text='курсы валют', url='https://select.by/kurs/')
        markup.add(item6)
        bot.send_message(callback.message.chat.id, f'Сегодня', reply_markup=markup)
        bot.register_next_step_handler(callback.message, get_markup)


def my_weather(message):  # получаем город от пользователя
    global temp
    city = message.text.strip().lower()
    weth = requests.get(
        f'https://api.openweathermap.org/data/2.5/find?q={city}&type=like&APPID={API}&units=metric')  # отправляем запрос на сайт погоды
    try:  # проверяем на правильность написания города
        data = json.loads(weth.text)
        temp = round(data["list"][0]["main"]["temp"], 1)  # получаем температуру и округляем до десятых
        bot.send_message(message.chat.id,
                         f'Сейчас погода в: {city}  {temp} градусов')  # отправляем ответ пользователю
        image_sun = 'sun.png'
        image_cloud = 'cloud.png'
        if temp <= 15:
            file = open('./' + image_cloud, 'rb')
            bot.send_photo(message.chat.id, file)
        else:
            file = open('./' + image_sun, 'rb')
            bot.send_photo(message.chat.id, file)

    except:
        bot.send_message(message.chat.id,
                         f'Город указан не верно,введите еще раз: ')
        bot.register_next_step_handler(message, my_weather)


bot.polling(none_stop=True, interval=0)
