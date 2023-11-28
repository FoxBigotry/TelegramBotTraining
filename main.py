import os
import telebot
import requests
import pyodbc
import random

from telebot import types
from pytube import YouTube

token = '6442272018:AAEuXpP82RiwYIL8NDnfW1NGUG_odLXAR3k'
bot = telebot.TeleBot(token)

mySQLServer = "WIN-VLHPBSGD7PP\SQLEXPRESS01"
myDatabase = "Test_01"

class AddFilm:
    def __init__(self, name):
        self.name = name
        self.genre = None
        self.year = None
        self.country = None

AddFilm_dict = {}
def bigine(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_parrot = types.KeyboardButton('Попугай')
    button_audio = types.KeyboardButton('Достаём звук')
    button_video = types.KeyboardButton('Достаём видео')
    button_weather = types.KeyboardButton('Погода')
    button_film = types.KeyboardButton('Фильм')
    markup.add(button_parrot, button_audio, button_video, button_weather, button_film)
    bot.send_message(message.chat.id, 'Попробуй кнопочки.', reply_markup=markup)

def back_button(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = types.KeyboardButton('Назад')
    markup.add(button_back)
    bot.send_message(message.chat.id, 'Либо возвращайся назад', reply_markup=markup)

def film_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_random = types.KeyboardButton('Скажи случайный')
    button_year = types.KeyboardButton('Найти по году')
    button_genre = types.KeyboardButton('Найти по жанру')
    button_add = types.KeyboardButton('Добавить фильм')
    button_back = types.KeyboardButton('Назад')
    markup.add(button_random,button_year,button_genre,button_add,button_back)
    bot.send_message(message.chat.id, 'Что будем делать с фильмами?', reply_markup=markup)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,'Привет 🦊\nБот может\n-Повторять за тобой\n-Cкачать видео или звук видео с Youtube\n-Подсказать погоду в указанном городе\n-Помочь с выбором фильма.')
    bigine(message)
    #keyboard = types.InlineKeyboardMarkup()
    #url_button = types.InlineKeyboardButton(text='Перейти на Яндекс', url='http://ya.ru')
    #keyboard.add(url_button)

def parrot (message):
    if message.text.lower() == 'хватит':
        bot.send_message(message.chat.id, '🦜 \n Ну раз хватит , то хватит.')
        bigine(message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_stop_parrot = types.KeyboardButton('Хватит')
        markup.add(button_stop_parrot)
        bot.send_message(message.chat.id, message.text,reply_markup=markup)
        bot.register_next_step_handler(message, parrot)

def Download_video(message):
    chat_id = message.chat.id
    video_url = message.text
    if video_url.startswith('https://youtu.be/') or video_url.startswith('https://www.youtube.com'):
        youtube_video = YouTube(video_url)
        video_title = youtube_video.title
        try:
            video = youtube_video.streams.get_highest_resolution()
            video.download()
            bot.send_video(chat_id, open(f'{video.title}.mp4', 'rb'))
        except Exception as e:
            bot.send_message(chat_id, f'Произошла ошибка: {str(e)}')
        os.remove(f'{video_title}.mp4')
    elif video_url.lower() == 'назад':
        bigine(message)
    else:
        bot.send_message(chat_id,'Я не понимаю эту ссылку.Попробуй ещё раз')
        bot.register_next_step_handler(message, Download_video)

def Download_audio(message):
    chat_id = message.chat.id
    video_url = message.text
    if video_url.startswith('https://youtu.be/') or video_url.startswith('https://www.youtube.com'):
        try:
            youtube_video = YouTube(video_url)
            video_title = youtube_video.title
            audio = youtube_video.streams.filter(only_audio=True).first()
            audio.download(filename=f'{video_title}_audio')
            with open(f'{video_title}_audio', 'rb') as audio_file:
                bot.send_audio(chat_id, audio_file)
        except Exception as e:
            bot.send_message(chat_id, f'Произошла ошибка: {str(e)}')
        os.remove(f'{video_title}_audio')
    elif video_url.lower() == 'назад':
        bigine(message)
    else:
        bot.send_message(chat_id,'Я не понимаю эту ссылку.Попробуй ещё раз')
        bot.register_next_step_handler(message, Download_video)

def Check_the_weather(message):
    chat_id = message.chat.id
    city = message.text
    if city.lower() == 'назад':
        bigine(message)
    else:
        url = 'https://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347'
        try:
            weather_data = requests.get(url).json()
            temperature = round(weather_data['main']['temp'])
            temperature_feels = round(weather_data['main']['feels_like'])
            bot.send_message(chat_id,f'Сейчас в городе {city}: {str(temperature)}°C\n Ощущается как {temperature_feels}°C')
            bot.register_next_step_handler(message, Check_the_weather)
        except Exception as e:
            #bot.send_message(chat_id, f"Произошла ошибка: {str(e)}")
            bot.send_message(chat_id, 'Технические шоколадки, попробуйте снова или позже.')
            bot.register_next_step_handler(message, Check_the_weather)

def random_film(message):
    chat_id = message.chat.id
    try:
        connection = pyodbc.connect('Driver={SQL Server};'
                                'Server=' + mySQLServer + ';'
                                'Database=' + myDatabase + ';'
                                )
        dbCursor = connection.cursor()
        requestString1 = 'Select Min(FilmID) from FilmsList'
        requestString2 = 'Select Max(FilmID) from FilmsList'
        dbCursor.execute(requestString1)
        i = dbCursor.fetchone()
        i = i[0]
        dbCursor.execute(requestString2)
        j = dbCursor.fetchone()
        j = j[0]
        rn = random.randint(i, j)
        requestString3 = f'Select FilmName,FilmGenre,FilmYear,FilmСountry from FilmsList with(nolock) where FilmID={rn}'
        dbCursor.execute(requestString3)
        row = dbCursor.fetchall()
        connection.close()
        bot.send_message(chat_id,f'Посмотрите фильм: {row[0][0]}\nжанр: {row[0][1]}\nСтрана, год: {row[0][3]},{row[0][2]}')
    except Exception as e:
        #bot.send_message(chat_id, f"Произошла ошибка: {str(e)}")
        bot.send_message(chat_id, f'Технические шоколадки, попробуйте позже')


def random_year(message):
    chat_id = message.chat.id
    n_year = message.text
    if  n_year.lower() == 'меню по фильмам':
        film_menu(message)
    else:
        try:
            connection = pyodbc.connect('Driver={SQL Server};'
                                    'Server=' + mySQLServer + ';'
                                    'Database=' + myDatabase + ';'
                                    )
            dbCursor = connection.cursor()
            requestString1 = f'Select * from FilmsList with(nolock) where FilmYear={n_year}'
            dbCursor.execute(requestString1)

            if dbCursor.fetchone() is None :
                bot.send_message(chat_id, 'У меня нет фильма такого года 😔\nПопробуй ещё раз')
                bot.register_next_step_handler(message, random_year)
            else:
                requestString2 = f'Select FilmName,FilmGenre,FilmYear,FilmСountry from FilmsList with(nolock) where FilmYear={n_year}'
                dbCursor.execute(requestString2)
                row = dbCursor.fetchall()
                i = 0
                t = len(row)
                while i <= t - 1:
                    bot.send_message(chat_id,f'Посмотрите фильм: {row[i][0]}\nжанр: {row[i][1]}\nСтрана, год: {row[i][3]},{row[i][2]}')
                    i += 1
                connection.close()
        except Exception as e:
            #bot.send_message(chat_id, f"Произошла ошибка: {str(e)}")
            bot.send_message(chat_id, 'Технические шоколадки, попробуйте позже')

def random_genre(message):
    chat_id = message.chat.id
    n_genre = message.text

    if n_genre.lower() == 'меню по фильмам':
        film_menu(message)
    else :
        try:
            connection = pyodbc.connect('Driver={SQL Server};'
                                'Server=' + mySQLServer + ';'
                                'Database=' + myDatabase + ';'
                                )
            dbCursor = connection.cursor()
            requestString1 = f'Select * from FilmsList with(nolock) where FilmGenre=\'{n_genre}\''
            dbCursor.execute(requestString1)

            if dbCursor.fetchone() is None :
                bot.send_message(chat_id, 'У меня нет фильма такого жанра 😔\nПопробуй ещё раз')
                bot.register_next_step_handler(message, random_genre)
            else:
                requestString2 = f'Select FilmName,FilmGenre,FilmYear,FilmСountry from FilmsList with(nolock) where FilmGenre=\'{n_genre}\''
                dbCursor.execute(requestString2)
                row = dbCursor.fetchall()
                i = 0
                t = len(row)
                while i <= t - 1:
                    bot.send_message(chat_id,f'Посмотрите фильм: {row[i][0]}\nжанр: {row[i][1]}\nСтрана, год: {row[i][3]},{row[i][2]}')
                    i += 1
            connection.close()
        except Exception as e:
            #bot.send_message(chat_id, f"Произошла ошибка: {str(e)}")
            bot.send_message(chat_id, 'Технические шоколадки, попробуйте позже')


def add_film_name(message):
    chat_id = message.chat.id
    f_Name = message.text
    if f_Name.lower() == 'меню по фильмам':
        film_menu(message)
    else :
        try :
            chat_id = message.chat.id
            f_Name = message.text
            f_Name = AddFilm(f_Name)
            AddFilm_dict[chat_id] = f_Name
            bot.send_message(chat_id, 'Жанр')
            bot.register_next_step_handler(message, add_film_genre)
        except Exception as e:
            bot.send_message(chat_id, 'Технические шоколадки, попробуйте позже')
            bigine(message)
def add_film_genre(message):
    chat_id = message.chat.id
    f_genre = message.text
    if f_genre.lower() == 'меню по фильмам':
        film_menu(message)
    else :
        try :

            genre = AddFilm_dict[chat_id]
            genre.genre = f_genre
            bot.send_message(chat_id, 'год')
            bot.register_next_step_handler(message, add_film_year)
        except Exception as e:
            bot.send_message(chat_id, 'Технические шоколадки, попробуйте позже')
            bigine(message)
def add_film_year(message):
    chat_id = message.chat.id
    f_year = message.text
    if f_year.lower() == 'меню по фильмам':
        film_menu(message)
    else :
        try:
            if not f_year.isdigit():
                msg = bot.reply_to(message, 'Что то не так с твои годом, задай год ещё раз')
                bot.register_next_step_handler(msg, add_film_year)
                return
            year = AddFilm_dict[chat_id]
            year.year = f_year
            #test(message)
            bot.send_message(chat_id, 'Страна')
            bot.register_next_step_handler(message, add_film_counry)
        except Exception as e:
            bot.send_message(chat_id, 'Технические шоколадки, попробуйте позже')
            bigine(message)
def add_film_counry(message):
    chat_id = message.chat.id
    f_counry = message.text
    if f_counry.lower() == 'меню по фильмам':
        film_menu(message)
    else :
        try:
            counry = AddFilm_dict[chat_id]
            counry.counry = f_counry
            add_film_agreement(message)
        except Exception as e:
            bot.send_message(chat_id, 'Технические шоколадки, попробуйте позже')
            bigine(message)
def add_film_agreement(message):
    chat_id = message.chat.id
    text = message.text
    if text.lower() == 'меню по фильмам':
        film_menu(message)
    else :
        film = AddFilm_dict[chat_id]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_film_add_yes = types.KeyboardButton('Да')
        button_film_add_no = types.KeyboardButton('Нет')
        button_film_menu = types.KeyboardButton('Меню по фильмам')
        markup.add(button_film_add_yes, button_film_add_no, button_film_menu)
        bot.send_message(chat_id, f'Вы хотите добавить\nфильм под названием: {film.name}\nжанр: {film.genre}\nгод производства:{film.year}\nстрана производства:{film.counry}\n?',reply_markup=markup)

def add_film_yes(message):
    chat_id = message.chat.id
    film = AddFilm_dict[chat_id]
    try:
        connection = pyodbc.connect('Driver={SQL Server};'
                                    'Server=' + mySQLServer + ';'
                                    'Database=' + myDatabase + ';'
                                    )
        dbCursor = connection.cursor()
        requestStringAddFilm = f'insert into FilmsList (FilmName,FilmGenre,FilmYear,FilmСountry) values (\'{film.name}\',\'{film.genre}\',{film.year},\'{film.counry}\')'
        dbCursor.execute(requestStringAddFilm)
        dbCursor.commit()
        connection.close()
        bot.send_message(chat_id, 'Отлично фильм добавлен')
    except Exception as e:
        # bot.send_message(chat_id, f"Произошла ошибка: {str(e)}")
        bot.send_message(chat_id, 'Технические шоколадки, попробуйте позже')
    bigine(message)

def add_film_no(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_film_menu = types.KeyboardButton('Меню по фильмам')
    markup.add(button_film_menu)
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Судя по всему, что-то пошло не так, давайте попробуем снова\nНазвание фильма?',reply_markup=markup)
    bot.register_next_step_handler(message, add_film_name)

@bot.message_handler(content_types=['text'])
def message_reply(message):
    if message.text.lower() == 'попугай':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_stop_parrot = types.KeyboardButton('Хватит')
        markup.add(button_stop_parrot)
        bot.send_message(message.chat.id, 'Всё что скажешь повторю.\nЕсли надоест скажи или нажми кнопку "Хватит".🦜',reply_markup=markup)
        bot.register_next_step_handler(message, parrot)

    if message.text.lower() == 'достаём звук':
        bot.send_message(message.chat.id, 'Отправь мне ссылку на видео, с которого хочешь звук.')
        back_button(message)
        bot.register_next_step_handler(message, Download_audio)

    if message.text.lower() == 'достаём видео':
        bot.send_message(message.chat.id, 'Отправь мне ссылку на видео, которое хочешь скачать.')
        back_button(message)
        bot.register_next_step_handler(message, Download_video)

    if message.text.lower() == 'погода':
        bot.send_message(message.chat.id, 'В каком городе погода интересует')
        back_button(message)
        bot.register_next_step_handler(message, Check_the_weather)

    if message.text.lower() == 'фильм':
        film_menu(message)

    if message.text.lower() == 'скажи случайный':
        bot.send_message(message.chat.id, 'Не знаешь что посмотреть, как на счёт...')
        random_film(message)

    if message.text.lower() == 'найти по году':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_film_menu= types.KeyboardButton('Меню по фильмам')
        markup.add(button_film_menu)
        bot.send_message(message.chat.id, 'Какой год интересует?',reply_markup=markup)
        bot.register_next_step_handler(message,random_year)

    if message.text.lower() == 'найти по жанру':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_film_menu= types.KeyboardButton('Меню по фильмам')
        markup.add(button_film_menu)
        bot.send_message(message.chat.id, 'Какой жанр интересует?',reply_markup=markup)
        bot.register_next_step_handler(message,random_genre)

    if message.text.lower() == 'добавить фильм':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_film_menu= types.KeyboardButton('Меню по фильмам')
        markup.add(button_film_menu)
        bot.send_message(message.chat.id, 'Название фильма?',reply_markup=markup)
        bot.register_next_step_handler(message,add_film_name)

    if message.text.lower() == 'назад':
        bigine(message)

    if message.text.lower() == 'да':
        add_film_yes(message)
    if message.text.lower() == 'нет':
        add_film_no(message)
    if message.text.lower() == 'меню по фильмам':
        film_menu(message)

if __name__ =='__main__':
    bot.infinity_polling()