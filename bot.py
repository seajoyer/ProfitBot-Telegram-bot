#-*- coding: utf-8 -*-
import telebot
import random
import mysql.connector
import os
import base64
import asyncio
import datetime
from time import sleep
from telebot import types
import configparser
import pickle
import time
from telethon import events
from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import GetHistoryRequest
from telethon import connection

import cherrypy
import config

WEBHOOK_HOST = '212.86.115.80'
WEBHOOK_PORT = 443
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_SSL_CERT = '/home/Dmitry/upload/ProfitBot/webhook_cert.pem'
WEBHOOK_SSL_PRIV = '/home/Dmitry/upload/ProfitBot/webhook_pkey.pem'

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.token)

bot = telebot.TeleBot(config.token)

users = {}

class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            # Эта функция обеспечивает проверку входящего сообщения
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)

db = mysql.connector.connect(host='localhost', database='ProfitBot', user='user', password='88password04')
cursor = db.cursor()

qw = "SELECT distinct `user_id` FROM `users` where `user_id` = 653376416"
cursor.execute(qw)
result = cursor.fetchall()
if len(result) == 0:
    qw = """INSERT INTO `ProfitBot`.`users` (`id`, `user_id`, `status`, `msg_id1`, `msg_id2`) VALUES( NULL, 653376416, 'owner', 0, 0)"""
    cursor.execute(qw)
    db.commit()
else:
    qw = """UPDATE `users` SET `status` = 'owner'  WHERE `user_id` = 653376416"""
    cursor.execute(qw)
    db.commit()

qw = "SELECT distinct `user_id` FROM `users`"
cursor.execute(qw)
result = cursor.fetchall()
for item in result:
    qw = "SELECT distinct `status` FROM `users` WHERE `user_id` = %d"%(item)
    cursor.execute(qw)
    status = cursor.fetchall()[0][0]
    qw = "SELECT distinct `msg_id1` FROM `users` WHERE `user_id` = %d"%(item)
    cursor.execute(qw)
    msg_id1 = cursor.fetchall()[0][0]
    qw = "SELECT distinct `msg_id2` FROM `users` WHERE `user_id` = %d"%(item)
    cursor.execute(qw)
    msg_id2 = cursor.fetchall()[0][0]

    users[item[0]] = {'action': '', 'status': status, 'msg_id1' : msg_id1, 'msg_id2': msg_id2, 'distribution': {'action': '', 'text': '', 'picture': '', 'buttons': '', 'success': 0, 'fail': 0}}


before = datetime.datetime.now() - datetime.timedelta(seconds = 30)

async def wait_time(time):
    await asyncio.sleep(time)

def get_stat(price, type):
    if os.stat("/home/Dmitry/upload/ProfitBot/channel_messages.pickle").st_size == 0:

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(wait_time(2))
        loop.close()

    with open('/home/Dmitry/upload/ProfitBot/channel_messages.pickle', 'rb') as outfile:
        all_messages = pickle.load(outfile)

    result = {'female_goro': '', 'male_goro': '', 'female_facts': '', 'male_facts': ''}   # список всех сообщений
    total_messages = 10
    total_count_limit = 8  # поменяйте это значение, если вам нужны не все сообщения
    try:
        result['male_facts'] = all_messages[0].split(' ')
    except:
        result['male_facts'] = 'ошибка'
    try:
        result['female_goro'] = all_messages[1].split(' ')
    except:
        result['female_goro'] = 'ошибка'
    try:
        result['male_goro'] = all_messages[2].split(' ')
    except:
        result['male_goro'] = 'ошибка'
    try:
        result['female_facts'] = all_messages[3].split(' ')
    except:
        result['female_facts'] = 'ошибка'

    res = {'female_goro_cov': [], 'male_goro_cov': [], 'female_facts_cov': [], 'male_facts_cov': [], 'female_goro_per': [], 'male_goro_per': [], 'female_facts_per': [], 'male_facts_per': []}

    for i in result['female_facts']:
        if i.find('\nПдп') != -1:
            res['female_facts_cov'].append(int(i.replace('\nПдп', '').replace("'", '')))

    for i in result['male_facts']:
        if i.find('\nПдп') != -1:
            res['male_facts_cov'].append(int(i.replace('\nПдп', '').replace("'", '')))

    for i in result['female_goro']:
        if i.find('\nПдп') != -1:
            res['female_goro_cov'].append(int(i.replace('\nПдп', '').replace("'", '')))

    for i in result['male_goro']:
        if i.find('\nПдп') != -1:
            res['male_goro_cov'].append(int(i.replace('\nПдп', '').replace("'", '')))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    for i, item in enumerate(result['female_facts']):
        if result['female_facts'][result['female_facts'].index(item)-1] == '\n👥:':
            res['female_facts_per'].append(int(item.replace(',', '').replace("'", '')))

    for i, item in enumerate(result['male_facts']):
        if result['male_facts'][result['male_facts'].index(item)-1] == '\n👥:':
            res['male_facts_per'].append(int(item.replace(',', '').replace("'", '')))

    for i, item in enumerate(result['female_goro']):
        if result['female_goro'][result['female_goro'].index(item)-1] == '\n👥:':
            res['female_goro_per'].append(int(item.replace(',', '').replace("'", '')))

    for i, item in enumerate(result['male_goro']):
        if result['male_goro'][result['male_goro'].index(item)-1] == '\n👥:':
            res['male_goro_per'].append(int(item.replace(',', '').replace("'", '')))



    if res['female_facts_per'].count(0) != 0:
        res['female_facts_per'] = int(round(sum(res['female_facts_per'])/(12-res['female_facts_per'].count(0))*res['female_facts_per'].count(0) + sum(res['female_facts_per']), 0))
    else:
        res['female_facts_per'] = sum(res['female_facts_per'])

    if res['male_facts_per'].count(0) != 0:
        res['male_facts_per'] = int(round(sum(res['male_facts_per'])/(12-res['male_facts_per'].count(0))*res['male_facts_per'].count(0) + sum(res['male_facts_per']), 0))
    else:
        res['male_facts_per'] = sum(res['male_facts_per'])

    if res['female_goro_per'].count(0) != 0:
        res['female_goro_per'] = int(round(sum(res['female_goro_per'])/(12-res['female_goro_per'].count(0))*res['female_goro_per'].count(0) + sum(res['female_goro_per']), 0))
    else:
        res['female_goro_per'] = sum(res['female_goro_per'])

    if res['male_goro_per'].count(0) != 0:
        res['male_goro_per'] = int(round(sum(res['male_goro_per'])/(12-res['male_goro_per'].count(0))*res['male_goro_per'].count(0) + sum(res['male_goro_per']), 0))
    else:
        res['male_goro_per'] = sum(res['male_goro_per'])



    if res['female_facts_cov'].count(0) != 0:
        res['female_facts_cov'] = int(round(sum(res['female_facts_cov'])/(12-res['female_facts_cov'].count(0))*res['female_facts_cov'].count(0) + sum(res['female_facts_cov']), 0))
    else:
        res['female_facts_cov'] = sum(res['female_facts_cov'])

    if res['male_facts_cov'].count(0) != 0:
        res['male_facts_cov'] = int(round(sum(res['male_facts_cov'])/(12-res['male_facts_cov'].count(0))*res['male_facts_cov'].count(0) + sum(res['male_facts_cov']), 0))
    else:
        res['male_facts_cov'] = sum(res['male_facts_cov'])

    if res['female_goro_cov'].count(0) != 0:
        res['female_goro_cov'] = int(round(sum(res['female_goro_cov'])/(12-res['female_goro_cov'].count(0))*res['female_goro_cov'].count(0) + sum(res['female_goro_cov']), 0))
    else:
        res['female_goro_cov'] = sum(res['female_goro_cov'])

    if res['male_goro_cov'].count(0) != 0:
        res['male_goro_cov'] = int(round(sum(res['male_goro_cov'])/(12-res['male_goro_cov'].count(0))*res['male_goro_cov'].count(0) + sum(res['male_goro_cov']), 0))
    else:
        res['male_goro_cov'] = sum(res['male_goro_cov'])

    if type == 'stat':
        try:
            statistic = 'обновлено <code>' + datetime.datetime.now().strftime("%d.%m.%y %H:%M") + '</code>' + '<u>\nСетка Фактов по знакам Зодиака:</u>\n     <code>М ЦА</code>\n         👁: <b>%d</b>\n         👥: <b>%d</b>\n         <code>ERR</code>: <b>%d&#37;</b>\n     <code>Ж ЦА</code>\n         👁: <b>%d</b>\n         👥: <b>%d</b>\n         <code>ERR</code>: <b>%d&#37;</b>\n|   <code>Мца+Жца:</code>\n|       👁: <b>%d</b>\n|       👥: <b>%d</b>\n|       <code>ERR</code>: <b>%d&#37;</b>\n<u>Сетка Гороскопов:</u>\n     <code>М ЦА</code>\n         👁: <b>%d</b>\n         👥: <b>%d</b>\n         <code>ERR</code>: <b>%d&#37;</b>\n     <code>Ж ЦА</code>\n         👁: <b>%d</b>\n         👥: <b>%d</b>\n         <code>ERR</code>: <b>%d&#37;</b>\n|   <code>Мца+Жца:</code>\n|       👁: <b>%d</b>\n|       👥: <b>%d</b>\n|       <code>ERR</code>: <b>%d&#37;</b>\n\n<u>Всё вместе:</u>\n| 👁: <b>%d</b>\n| 👥: <b>%d</b>\n| <code>ERR</code>: <b>%d&#37;</b>'%(res['male_facts_cov'], res['male_facts_per'], int(round(res['male_facts_cov']/res['male_facts_per']*100, 0)), res['female_facts_cov'], res['female_facts_per'], int(round(res['female_facts_cov']/res['female_facts_per']*100, 0)), res['male_facts_cov']+res['female_facts_cov'], res['male_facts_per']+res['female_facts_per'], int(round((res['male_facts_cov']+res['female_facts_cov'])/(res['male_facts_per']+res['female_facts_per'])*100, 0)), res['male_goro_cov'], res['male_goro_per'], int(round(res['male_goro_cov']/res['male_goro_per']*100, 0)), res['female_goro_cov'], res['female_goro_per'], int(round(res['female_goro_cov']/res['female_goro_per']*100, 0)), res['male_goro_cov']+res['female_goro_cov'], res['male_goro_per']+res['female_goro_per'], int(round((res['male_goro_cov']+res['female_goro_cov'])/(res['male_goro_per']+res['female_goro_per'])*100, 0)), res['male_goro_cov']+res['female_goro_cov'] + res['male_facts_cov']+res['female_facts_cov'], res['male_goro_per']+res['female_goro_per'] + res['male_facts_per']+res['female_facts_per'], int(round((res['male_goro_cov']+res['female_goro_cov'] + res['male_facts_cov']+res['female_facts_cov'])/(res['male_goro_per']+res['female_goro_per'] + res['male_facts_per']+res['female_facts_per'])*100)))

            return(statistic)
        except:
            return('⚠️Ошибка, попробуйте снова через 30 секунд')
    elif type == 'price':
        try:
            res_price = str(price) + ' CPM<u>\nСетка Фактов по знакам Зодиака:</u>\n     <code>М ЦА = </code><b>%d</b>\n     <code>Ж ЦА = </code><b>%d</b>\n     <code>Мца+Жца = </code><b>%d</b>\n<u>Сетка Гороскопов:</u>\n     <code>М ЦА = </code><b>%d</b>\n     <code>Ж ЦА = </code><b>%d</b>\n     <code>Мца+Жца = </code><b>%d</b>\n\n<u>Всё вместе</u> = <b>%d</b>'%(res['male_facts_cov']/1000*price, res['female_facts_cov']/1000*price, (res['male_facts_cov']+res['female_facts_cov'])/1000*price, res['male_goro_cov']/1000*price, res['female_goro_cov']/1000*price, (res['male_goro_cov']+res['female_goro_cov'])/1000*price, (res['male_facts_cov']+res['female_facts_cov'] + res['male_goro_cov']+res['female_goro_cov'])/1000*price)
            return(res_price)
        except:
            return('⚠️Ошибка, попробуйте снова через 30 секунд')






@bot.message_handler(commands=['start'])
def trusted(message):
    global users
    if message.chat.id not in users.keys():
        qw = "SELECT distinct `user_id` FROM `users` where `user_id` = %d"%(message.chat.id)
        cursor.execute(qw)
        result = cursor.fetchall()
        if len(result) != 0:
            qw = "SELECT distinct `status` FROM `users` WHERE `user_id` = %d"%(message.chat.id)
            cursor.execute(qw)
            status = cursor.fetchall()[0][0]
            qw = "SELECT distinct `msg_id1` FROM `users` WHERE `user_id` = %d"%(message.chat.id)
            cursor.execute(qw)
            msg_id1 = cursor.fetchall()[0][0]
            qw = "SELECT distinct `msg_id2` FROM `users` WHERE `user_id` = %d"%(message.chat.id)
            cursor.execute(qw)
            msg_id2 = cursor.fetchall()[0][0]

            users[message.chat.id] = {'action': '', 'status': status, 'msg_id1': msg_id1, 'msg_id2': msg_id2, 'distribution': {'action': '', 'text': '', 'picture': '', 'buttons': '', 'success': 0, 'fail': 0}}
        else:
            qw = """INSERT INTO `ProfitBot`.`users` (`id`, `user_id`, `msg_id1`, `msg_id2`) VALUES( NULL, %d, 0, 0)""" %(message.chat.id)
            cursor.execute(qw)
            db.commit()
            users[message.chat.id] = {'action': '', 'status': 'member', 'msg_id1': 0, 'msg_id2': 0, 'distribution': {'action': '', 'text': '', 'picture': '', 'buttons': '', 'success': 0, 'fail': 0}}

    key = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.row('Аналитика', 'Стоимость')
    if users[message.chat.id]['status'] == 'owner' or users[message.chat.id]['status'] == 'admin':
        key.row('Админка')
    bot.send_message(message.chat.id, 'Привет!\nЭтот бот поможет вам сделать расчет стоимости рекламы в каналах:\n@vp_reklama_goro\n@vp_reklama_facts\nпо всем вопросам - @kristyday', reply_markup = key)


@bot.message_handler(func=lambda c:True, content_types=['text'])
def info_message(message):
    global users
    if message.chat.id not in users.keys():
        qw = "SELECT distinct `user_id` FROM `users` where `user_id` = %d"%(message.chat.id)
        cursor.execute(qw)
        result = cursor.fetchall()
        if len(result) != 0:
            qw = "SELECT distinct `status` FROM `users` WHERE `user_id` = %d"%(message.chat.id)
            cursor.execute(qw)
            status = cursor.fetchall()[0][0]
            qw = "SELECT distinct `msg_id1` FROM `users` WHERE `user_id` = %d"%(message.chat.id)
            cursor.execute(qw)
            msg_id1 = cursor.fetchall()[0][0]
            qw = "SELECT distinct `msg_id2` FROM `users` WHERE `user_id` = %d"%(message.chat.id)
            cursor.execute(qw)
            msg_id2 = cursor.fetchall()[0][0]

            users[message.chat.id] = {'action': '', 'status': status, 'msg_id1': msg_id1, 'msg_id2': msg_id2, 'distribution': {'action': '', 'text': '', 'picture': '', 'buttons': '', 'success': 0, 'fail': 0}}

        else:
            qw = """INSERT INTO `ProfitBot`.`users` (`id`, `user_id`, `msg_id1`, `msg_id2`) VALUES( NULL, %d, 0, 0)""" %(message.chat.id)
            cursor.execute(qw)
            db.commit()
            users[message.chat.id] = {'action': '', 'status': 'member', 'msg_id1' : 0, 'msg_id2' : 0, 'distribution': {'action': '', 'text': '', 'picture': '', 'buttons': '', 'success': 0, 'fail': 0}}

    if message.text == '⚡️МОЛОТ ТОРА⚡️' and users[message.chat.id]['status'] == 'owner':
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text="Назначить админа",callback_data="Set_admin")
        but_2 = types.InlineKeyboardButton(text="Уволить админа",callback_data="Lay_off_admin")
        but_3 = types.InlineKeyboardButton(text="список суперпользователей",callback_data="Adm_list")
        key.add(but_1, but_2)
        key.add(but_3)
        users[message.chat.id]['msg_id1'] = bot.send_message(message.chat.id, 'Чем займемся сегодня?', reply_markup = key).message_id
        qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[message.chat.id]['msg_id1'], message.chat.id)
        cursor.execute(qw)
        db.commit()

    if users[message.chat.id]['action'] == 'Lay_off_admin' and users[message.chat.id]['status'] == 'owner':
        if message.text.isdigit() and len(message.text) > 4:
            qw = "SELECT distinct `user_id` FROM `users` WHERE `user_id` = %d"%(int(message.text))
            cursor.execute(qw)
            result = cursor.fetchall()
            if len(result) == 0:
                key = types.InlineKeyboardMarkup()
                but_1 = types.InlineKeyboardButton(text="отмена",callback_data="ADMStop")
                key.add(but_1)
                bot.send_message(message.chat.id, 'Увы, но такого у нас нет(\nПопробуйте снова:', reply_markup = key)
            else:
                qw = """UPDATE `users` SET `status` = 'member'  WHERE `user_id` = %d """ %(int(message.text))
                cursor.execute(qw)
                db.commit()
                bot.send_message(message.chat.id, str(message.text) + ' теперь простой пользователь.')
                users[message.chat.id]['action'] = ''

    if users[message.chat.id]['action'] == 'Set_admin' and users[message.chat.id]['status'] == 'owner':
        if message.text.isdigit() and len(message.text) > 4:
            qw = "SELECT distinct `user_id` FROM `users` WHERE `user_id` = %d"%(int(message.text))
            cursor.execute(qw)
            result = cursor.fetchall()
            if len(result) == 0:
                key = types.InlineKeyboardMarkup()
                but_1 = types.InlineKeyboardButton(text="отмена",callback_data="ADMStop")
                key.add(but_1)
                bot.send_message(message.chat.id, 'Увы, но такого у нас нет(\nПопробуйте снова:', reply_markup = key)
            else:
                key = types.InlineKeyboardMarkup()
                but_1 = types.InlineKeyboardButton(text="назначить!",callback_data="Upgrade_admin" + str(message.text))
                but_2 = types.InlineKeyboardButton(text="отмена",callback_data="ADMStop")
                key.add(but_1, but_2)
                users[message.chat.id]['msg_id1'] = bot.send_message(message.chat.id, 'Уверен что хочешь назначить админом <code>%s</code>?'%(message.text), parse_mode = 'HTML', reply_markup = key).message_id

    if message.text == 'назад':
        users[message.chat.id]['action'] = ''
        key = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        key.row('Аналитика', 'Стоимость')
        if users[message.chat.id]['status'] == 'owner' or users[message.chat.id]['status'] == 'admin':
            key.row('Админка')
        bot.send_message(message.chat.id, 'Главное меню', reply_markup = key)

    if message.text == 'Рассылка' and users[message.chat.id]['status'] == 'owner' and users[message.chat.id]['action'] == '' or message.text == 'Рассылка' and users[message.chat.id]['status'] == 'admin' and users[message.chat.id]['action'] == '':
        users[message.chat.id]['distribution']['action'] = ''
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text="Только текст",callback_data="ADMText")
        but_2 = types.InlineKeyboardButton(text="С картинкой",callback_data="ADMPhoto")
        but_3 = types.InlineKeyboardButton(text="отмена",callback_data="ADMStop")
        key.add(but_1, but_2)
        key.add(but_3)
        users[message.chat.id]['msg_id1'] = bot.send_message(message.chat.id, 'Тип поста:', reply_markup=key).message_id
        qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[message.chat.id]['msg_id1'], message.chat.id)
        cursor.execute(qw)
        db.commit()

    if users[message.chat.id]['status'] == 'owner' and users[message.chat.id]['distribution']['action'] == 'Check_buttons' or users[message.chat.id]['status'] == 'admin' and users[message.chat.id]['distribution']['action'] == 'Check_buttons':
        try:
            bot.edit_message_reply_markup(message.chat.id, users[message.chat.id]['msg_id1'], reply_markup = '')
        except:
            pass
        names = []
        urls = []

        if users[message.chat.id]['distribution']['buttons'] == '' and users[message.chat.id]['distribution']['buttons'] != 'None':
            users[message.chat.id]['distribution']['buttons'] = message.text
            try:
                for pare in users[message.chat.id]['distribution']['buttons'].split('\n'):
                    names.append(pare.split(' - ')[0]) #неверно заданы кнопки
                    urls.append(pare.split(' - ')[1]) #неверно заданы кнопки
                    key = types.InlineKeyboardMarkup()
                    key2 = types.InlineKeyboardMarkup()
                    for name, url in zip(names, urls):
                        key.add(types.InlineKeyboardButton(text = name, url = url))
                    key2.add(types.InlineKeyboardButton('ОТПРАВИТЬ', callback_data = 'ADMSend'))
                    key2.add(types.InlineKeyboardButton(text="отмена",callback_data = "ADMStop"))

                if users[message.chat.id]['distribution']['picture'] == '':
                    bot.send_message(message.chat.id, text = str(users[message.chat.id]['distribution']['text']), parse_mode = 'HTML', reply_markup=key)
                else:
                    bot.send_photo(message.chat.id, photo = users[message.chat.id]['distribution']['picture'] ,caption = str(users[message.chat.id]['distribution']['text']), parse_mode = 'HTML', reply_markup=key)

                users[message.chat.id]['msg_id1'] = bot.reply_to(message, text = 'Отправить сообщение всем пользователям бота?', reply_markup=key2).message_id
                qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[message.chat.id]['msg_id1'], message.chat.id)
                cursor.execute(qw)
                db.commit()
                users[message.chat.id]['distribution']['action'] = ''

            except Exception as e:
                bot.send_message(message.chat.id, 'Скорее всего неверно заданы кнопки, повторите ввод.\n\n<code>' + str(e) + '</code>\n\nЕсли кнопки заданы верно, сообщи @Garison_777', parse_mode = 'HTML')
                users[message.chat.id]['distribution']['buttons'] = ''

        elif users[message.chat.id]['distribution']['buttons'] == 'None':
            try:
                bot.edit_message_reply_markup(message.chat.id, users[message.chat.id]['msg_id1'], reply_markup = '')
            except:
                pass
            key = types.InlineKeyboardMarkup()
            but_1 = types.InlineKeyboardButton(text="ОТПРАВИТЬ",callback_data="ADMSend")
            but_2 = types.InlineKeyboardButton(text="отмена",callback_data="ADMStop")
            key.add(but_1)
            key.add(but_2)
            if users[message.chat.id]['distribution']['picture'] == '':
                bot.edit_message_text(chat_id = message.chat.id, message_id = users[message.chat.id]['msg_id1'], text = str(users[message.chat.id]['distribution']['text']), parse_mode = 'HTML')
                bot.reply_to(message, text = 'Отправить сообщение всем пользователям бота?', parse_mode = 'HTML', reply_markup=key)

            else:
                bot.send_photo(message.chat.id, photo = users[message.chat.id]['distribution']['picture'], caption = str(users[message.chat.id]['distribution']['text']), parse_mode = 'HTML')
                bot.reply_to(message, text = 'Отправить сообщение всем пользователям бота?', parse_mode = 'HTML', reply_markup=key)

    if users[message.chat.id]['distribution']['action'] == 'Check_text' and users[message.chat.id]['status'] == 'owner' or users[message.chat.id]['distribution']['action'] == 'Check_text' and users[message.chat.id]['status'] == 'admin':
        try:
            bot.edit_message_reply_markup(message.chat.id, users[message.chat.id]['msg_id1'], reply_markup = '')
        except:
            pass
        try:
            users[message.chat.id]['distribution']['text'] = message.text
            bot.send_message(1007846976, users[message.chat.id]['distribution']['text'], parse_mode= 'HTML')
            key = types.InlineKeyboardMarkup()
            but_1 = types.InlineKeyboardButton(text="Без кнопок",callback_data="No_but")
            key.add(but_1)
            users[message.chat.id]['msg_id1'] = bot.send_message(message.chat.id, "Текст добавлен, пришли кнопки в формате\n\n<code>Текст кнопки - ссылка</code>\n\n(каждая кнопка с новой строки)", parse_mode= 'HTML', reply_markup=key).message_id
            qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[message.chat.id]['msg_id1'], message.chat.id)
            cursor.execute(qw)
            db.commit()
            users[message.chat.id]['distribution']['action'] = 'Check_buttons'
        except Exception as e:
            bot.send_message(message.chat.id, 'Скорее всего ошибка в синтаксисе HTML, повторите ввод.\n\n<code>' + str(e) + '</code>\n\nЕсли ошибки нет, сообщи @Garison_777', parse_mode = 'HTML')


    if message.text == 'Админка' and users[message.chat.id]['status'] == 'owner' and users[message.chat.id]['action'] == '' or message.text == 'Админка' and users[message.chat.id]['status'] == 'admin' and users[message.chat.id]['action'] == '':
        key = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        key.row('Рассылка')
        if users[message.chat.id]['status'] == 'owner':
            key.row('⚡️МОЛОТ ТОРА⚡️')
        key.row('назад')
        bot.send_message(message.chat.id, 'Главное меню администратора', reply_markup = key)

    if message.text == 'Аналитика' and users[message.chat.id]['action'] == '':

        users[message.chat.id]['msg_id1'] = ''
        users[message.chat.id]['msg_id2'] = ''

        delta = datetime.timedelta(seconds = 30)
        now = datetime.datetime.now()
        global before
        users[message.chat.id]['msg_id1'] = bot.send_message(message.chat.id, 'Подготавливаю статистику, может занять до 10 секунд...').message_id
        qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[message.chat.id]['msg_id1'], message.chat.id)
        cursor.execute(qw)
        db.commit()
        if before + delta >= now:

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(wait_time(3))
            loop.close()

            key = types.InlineKeyboardMarkup()
            but_1 = types.InlineKeyboardButton(text="↻", callback_data="Overload")
            key.add(but_1)
            users[message.chat.id]['msg_id1'] = bot.edit_message_text(chat_id=message.chat.id, message_id=users[message.chat.id]['msg_id1'], text=get_stat(0, 'stat'), reply_markup = key, parse_mode= 'HTML').message_id
            qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[message.chat.id]['msg_id1'], message.chat.id)
            cursor.execute(qw)
            db.commit()

        else:
            before = datetime.datetime.now()

            bot.send_message(1007846976, 'Overload')

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(wait_time(9))
            loop.close()

            key = types.InlineKeyboardMarkup()
            but_1 = types.InlineKeyboardButton(text="↻", callback_data="Overload")
            key.add(but_1)
            users[message.chat.id]['msg_id1'] = bot.edit_message_text(chat_id=message.chat.id, message_id=users[message.chat.id]['msg_id1'], text=get_stat(0, 'stat'), reply_markup = key, parse_mode= 'HTML').message_id
            qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[message.chat.id]['msg_id1'], message.chat.id)
            cursor.execute(qw)
            db.commit()

            before = datetime.datetime.now()

    if users[message.chat.id]['action'] == 'price':
        if message.text.isdigit() and int(message.text) <= 10000 and int(message.text) >= 1:

            delta = datetime.timedelta(seconds = 30)
            now = datetime.datetime.now()
            users[message.chat.id]['msg_id1'] = bot.send_message(message.chat.id, 'Идет расчет, может занять до 10 секунд...').message_id
            qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[message.chat.id]['msg_id1'], message.chat.id)
            cursor.execute(qw)
            db.commit()
            if before + delta >= now:

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(wait_time(3))
                loop.close()

                users[message.chat.id]['msg_id1'] = bot.edit_message_text(chat_id=message.chat.id, message_id=users[message.chat.id]['msg_id1'], text=get_stat(int(message.text), 'price'), parse_mode= 'HTML').message_id
                qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[message.chat.id]['msg_id1'], message.chat.id)
                cursor.execute(qw)
                db.commit()
            else:
                before = datetime.datetime.now()

                bot.send_message(1007846976, 'Overload')

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(wait_time(9))
                loop.close()

                users[message.chat.id]['msg_id1'] = bot.edit_message_text(chat_id=message.chat.id, message_id=users[message.chat.id]['msg_id1'], text=get_stat(int(message.text), 'price'), parse_mode= 'HTML').message_id
                qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[message.chat.id]['msg_id1'], message.chat.id)
                cursor.execute(qw)
                db.commit()

                before = datetime.datetime.now()

            users[message.chat.id]['action'] = ''
        else:
            bot.send_message(message.chat.id, 'Неверное значение, повторите ввод:')

    if message.text == 'Стоимость' and users[message.chat.id]['action'] == '':
        key = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        key.row('назад')
        bot.send_message(message.chat.id, 'Введи расчетную чену за 1000 просмотров (CPM):', reply_markup = key)
        users[message.chat.id]['action'] = 'price'


@bot.callback_query_handler(func=lambda c:True)
def inline(c):
    global users
    if c.message.chat.id not in users.keys():
        qw = "SELECT distinct `user_id` FROM `users` where `user_id` = %d"%(c.message.chat.id)
        cursor.execute(qw)
        result = cursor.fetchall()
        if len(result) != 0:
            qw = "SELECT distinct `status` FROM `users` WHERE `user_id` = %d"%(c.message.chat.id)
            cursor.execute(qw)
            status = cursor.fetchall()[0][0]
            qw = "SELECT distinct `msg_id1` FROM `users` WHERE `user_id` = %d"%(c.message.chat.id)
            cursor.execute(qw)
            msg_id1 = cursor.fetchall()[0][0]
            qw = "SELECT distinct `msg_id2` FROM `users` WHERE `user_id` = %d"%(c.message.chat.id)
            cursor.execute(qw)
            msg_id2 = cursor.fetchall()[0][0]

            users[c.message.chat.id] = {'action': '', 'status': status, 'msg_id1': msg_id1, 'msg_id2': msg_id2, 'distribution': {'action': '', 'text': '', 'picture': '', 'buttons': '', 'success': 0, 'fail': 0}}
        else:
            qw = """INSERT INTO `ProfitBot`.`users` (`id`, `user_id`, `msg_id1`, `msg_id2`) VALUES( NULL, %d, 0, 0)""" %(c.message.chat.id)
            cursor.execute(qw)
            db.commit()
            users[c.message.chat.id] = {'action': '', 'status': 'member', 'msg_id1': 0, 'msg_id2': 0, 'distribution': {'action': '', 'text': '', 'picture': '', 'buttons': '', 'success': 0, 'fail': 0}}

    if c.data == 'Adm_list' and users[c.message.chat.id]['status'] == 'owner':
        qw = "SELECT `user_id`, `status` FROM `users` WHERE `status` <> 'member'"
        cursor.execute(qw)
        result = cursor.fetchall()
        adm_list = 'Все суперпользователи:'
        for item in result:
            adm_list += '\n' + str(item[0]) + ' - ' + str(item[1])
        bot.edit_message_text(chat_id=c.message.chat.id, message_id=users[c.message.chat.id]['msg_id1'], text=adm_list)

    if c.data == 'Without_text' and users[c.message.chat.id]['status'] == 'owner' or c.data == 'Without_text' and users[c.message.chat.id]['status'] == 'admin':
        users[c.message.chat.id]['msg_id1'] = bot.send_message(c.message.chat.id, "Пришли кнопки в формате\n\n<code>Текст кнопки - ссылка</code>\n\n(каждая кнопка с новой строки)", parse_mode= 'HTML').message_id
        qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[c.message.chat.id]['msg_id1'], c.message.chat.id)
        cursor.execute(qw)
        db.commit()
        users[c.message.chat.id]['distribution']['action'] = 'Check_buttons'

    if c.data == "ADMPhoto" and users[c.message.chat.id]['status'] == 'owner' or c.data == "ADMPhoto" and users[c.message.chat.id]['status'] == 'admin':
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text="отмена",callback_data="ADMStop")
        key.add(but_1)
        users[c.message.chat.id]['msg_id1'] = bot.edit_message_text(chat_id = c.message.chat.id, message_id = users[c.message.chat.id]['msg_id1'], text = "Пришли изображение", reply_markup = key).message_id
        users[c.message.chat.id]['distribution']['action'] = 'Check_picture'
        qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[c.message.chat.id]['msg_id1'], c.message.chat.id)
        cursor.execute(qw)
        db.commit()

    if c.data == "Lay_off_admin" and users[c.message.chat.id]['status'] == 'owner':
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text="отмена",callback_data="ADMStop")
        key.add(but_1)
        bot.edit_message_text(chat_id=c.message.chat.id, message_id=users[c.message.chat.id]['msg_id1'], text='Кого уволишь?', reply_markup = key)
        users[c.message.chat.id]['action'] = 'Lay_off_admin'

    if c.data.find("Upgrade_admin") != -1 and users[c.message.chat.id]['status'] == 'owner':
        qw = """UPDATE `users` SET `status` = 'admin'  WHERE `user_id` = %d """ %(int(c.data[13:]))
        cursor.execute(qw)
        db.commit()
        bot.edit_message_text(chat_id=c.message.chat.id, message_id=users[c.message.chat.id]['msg_id1'], text=str(c.data[13:]) + ' назначен администратором.')
        bot.send_message(int(c.data[13:]), 'Поздравляю, вы теперь администратор!\nЧто бы изменения вступили в силу, отправьте /start')
        users[c.message.chat.id]['action'] = ''

    if c.data == 'ADMSend' and users[c.message.chat.id]['status'] == 'owner' or c.data == 'ADMSend' and users[c.message.chat.id]['status'] == 'admin':
        bot.delete_message(chat_id = c.message.chat.id, message_id = c.message.message_id)
        bot.answer_callback_query(callback_query_id=c.id, show_alert=True, text="Рассылка началась⏳")
        qw = "SELECT `user_id` FROM `users`"
        cursor.execute(qw)
        result = cursor.fetchall()
        names = []
        urls = []
        print(users[c.message.chat.id]['distribution']['buttons'])
        if users[c.message.chat.id]['distribution']['buttons'] != '':
            for pare in users[c.message.chat.id]['distribution']['buttons'].split('\n'):
                try:
                    names.append(pare.split(' - ')[0])
                    urls.append(pare.split(' - ')[1])
                    key = types.InlineKeyboardMarkup()
                    for name, url in zip(names, urls):
                        key.add(types.InlineKeyboardButton(text = name, url = url))
                except:
                    bot.send_message(c.message.chat.id, 'Вероятно, бот был перезагружен, вам придется снова ввести все данные для рассылки((\nЕсли проблема осталась, сообщите @Garison_777')
        else:
            key = ''

        for user_id in result:
            if user_id[0] != c.message.chat.id:

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(wait_time(0.04))
                loop.close()
                try:
                    if users[c.message.chat.id]['distribution']['picture'] != '':
                        bot.send_photo(user_id[0], photo = users[c.message.chat.id]['distribution']['picture'], caption = users[c.message.chat.id]['distribution']['text'], parse_mode = 'HTML', reply_markup=key)
                    else:
                        bot.send_message(user_id[0], users[c.message.chat.id]['distribution']['text'], parse_mode = 'HTML', reply_markup=key)
                    users[c.message.chat.id]['distribution']['success'] += 1
                except Exception as e:
                    bot.send_message(c.message.chat.id, e)
                    users[c.message.chat.id]['distribution']['fail'] += 1

        bot.send_message(c.message.chat.id, 'Рассылка завершина!\nУспешно: <b>%d</b> - <b>%d</b>&#37;\nЗаблокировали бота: <b>%d</b> - <b>%d</b>&#37;\n\nПользователей в базе: <b>%d</b>'%(users[c.message.chat.id]['distribution']['success']+1, round((users[c.message.chat.id]['distribution']['success']+1)/len(result)*100, 1), users[c.message.chat.id]['distribution']['fail'], round(users[c.message.chat.id]['distribution']['fail']/len(result)*100, 1), len(result)), parse_mode = 'HTML')
        users[c.message.chat.id]['distribution']['success'] = 0
        users[c.message.chat.id]['distribution']['fail'] = 0



    if c.data == 'Set_admin' and users[c.message.chat.id]['status'] == 'owner':
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text="отмена",callback_data="ADMStop")
        key.add(but_1)
        bot.edit_message_text(chat_id=c.message.chat.id, message_id=users[c.message.chat.id]['msg_id1'], text='Кого назначишь?', reply_markup = key)
        users[c.message.chat.id]['action'] = 'Set_admin'

    if c.data == 'No_but' and users[c.message.chat.id]['status'] == 'owner' and users[c.message.chat.id]['action'] == '' or c.data == 'No_but' and users[c.message.chat.id]['status'] == 'admin' and users[c.message.chat.id]['action'] == '':
        users[c.message.chat.id]['distribution']['action'] = ''
        users[c.message.chat.id]['distribution']['buttons'] == 'None'
        users[c.message.chat.id]['distribution']['buttons'] == 'None'
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text="ОТПРАВИТЬ",callback_data="ADMSend")
        but_2 = types.InlineKeyboardButton(text="отмена",callback_data="ADMStop")
        key.add(but_1)
        key.add(but_2)
        if users[c.message.chat.id]['distribution']['picture'] == '':
            bot.edit_message_text(chat_id = c.message.chat.id, message_id = users[c.message.chat.id]['msg_id1'], text = str(users[c.message.chat.id]['distribution']['text']), parse_mode = 'HTML')
            bot.reply_to(c.message, text = 'Отправить сообщение всем пользователям бота?', parse_mode = 'HTML', reply_markup=key)

        else:
            bot.send_photo(c.message.chat.id, photo = users[c.message.chat.id]['distribution']['picture'], caption = str(users[c.message.chat.id]['distribution']['text']), parse_mode = 'HTML')
            bot.reply_to(c.message, text = 'Отправить сообщение всем пользователям бота?', parse_mode = 'HTML', reply_markup=key)

    if c.data == 'ADMText' and users[c.message.chat.id]['status'] == 'owner' and users[c.message.chat.id]['action'] == '' or c.data == 'ADMText' and users[c.message.chat.id]['status'] == 'admin' and users[c.message.chat.id]['action'] == '':
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text="отмена",callback_data="ADMStop")
        key.add(but_1)
        users[c.message.chat.id]['msg_id1'] = bot.edit_message_text(chat_id = c.message.chat.id, message_id = users[c.message.chat.id]['msg_id1'], text = "Пришли текст одним сообщением (форматирование с помощью HTML)", reply_markup=key).message_id
        qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[c.message.chat.id]['msg_id1'], c.message.chat.id)
        cursor.execute(qw)
        db.commit()
        users[c.message.chat.id]['distribution']['action'] = 'Check_text'

    if c.data == 'ADMStop' and users[c.message.chat.id]['status'] == 'owner' or c.data == 'ADMStop' and users[c.message.chat.id]['status'] == 'admin':
        users[c.message.chat.id] = {'action': '', 'status': users[c.message.chat.id]['status'], 'msg_id1': 0, 'msg_id2': 0, 'distribution': {'action': '', 'text': '', 'picture': '', 'buttons': '', 'success': 0, 'fail': 0}}
        bot.delete_message(chat_id = c.message.chat.id, message_id = c.message.message_id)
        key = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        key.row('Рассылка')
        if users[c.message.chat.id]['status'] == 'owner':
            key.row('⚡️МОЛОТ ТОРА⚡️')
        key.row('назад')
        bot.send_message(c.message.chat.id, 'Главное меню администратора', reply_markup=key)

    if c.data == "Overload" and users[c.message.chat.id]['action'] == '':
        now = datetime.datetime.now()
        global before
        delta = datetime.timedelta(seconds = 30)
        if users[c.message.chat.id]['msg_id2'] != '':
            try:
                users[c.message.chat.id]['msg_id1'] = bot.edit_message_reply_markup(chat_id=c.message.chat.id, message_id=users[c.message.chat.id]['msg_id1'], reply_markup = '').message_id
                qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[c.message.chat.id]['msg_id1'], c.message.chat.id)
                cursor.execute(qw)
                db.commit()

                users[c.message.chat.id]['msg_id2'] = bot.edit_message_text(chat_id=c.message.chat.id, message_id=users[c.message.chat.id]['msg_id2'], text='Загрузка...').message_id
                qw = """UPDATE `users` SET `msg_id2` = %d  WHERE `user_id` = %d """ %(users[c.message.chat.id]['msg_id2'], c.message.chat.id)
                cursor.execute(qw)
                db.commit()

            except:
                pass

        else:
            try:
                users[c.message.chat.id]['msg_id1'] = bot.edit_message_reply_markup(chat_id=c.message.chat.id, message_id=users[c.message.chat.id]['msg_id1'], reply_markup = '').message_id
                qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[c.message.chat.id]['msg_id1'], c.message.chat.id)
                cursor.execute(qw)
                db.commit()
            except:
                pass
            users[c.message.chat.id]['msg_id2'] = bot.send_message(c.message.chat.id, text='Загрузка...').message_id
            qw = """UPDATE `users` SET `msg_id2` = %d  WHERE `user_id` = %d """ %(users[c.message.chat.id]['msg_id2'], c.message.chat.id)
            cursor.execute(qw)
            db.commit()

        if before + delta < now:
            before = datetime.datetime.now()

            bot.send_message(1007846976, 'Overload')

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(wait_time(9))
            loop.close()

            bot.answer_callback_query(callback_query_id=c.id, show_alert=False, text="Обновлено✅")

            key = types.InlineKeyboardMarkup()
            but_1 = types.InlineKeyboardButton(text="↻", callback_data="Overload")
            key.add(but_1)

            if users[c.message.chat.id]['msg_id1'] != '' and users[c.message.chat.id]['msg_id2'] != '':
                try:
                    if users[c.message.chat.id]['msg_id1'].text != get_stat(0, 'stat'):
                        users[c.message.chat.id]['msg_id1'] = bot.edit_message_text(chat_id=c.message.chat.id, message_id=users[c.message.chat.id]['msg_id1'], text=get_stat(0, 'stat'), reply_markup = key, parse_mode= 'HTML').message_id
                        qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[c.message.chat.id]['msg_id1'], c.message.chat.id)
                        cursor.execute(qw)
                        db.commit()
                except:
                    users[c.message.chat.id]['msg_id1'] = bot.edit_message_text(chat_id=c.message.chat.id, message_id=users[c.message.chat.id]['msg_id1'], text=get_stat(0, 'stat'), reply_markup = key, parse_mode= 'HTML').message_id
                    qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[c.message.chat.id]['msg_id1'], c.message.chat.id)
                    cursor.execute(qw)
                    db.commit()
                users[c.message.chat.id]['msg_id2'] = bot.edit_message_text(chat_id=c.message.chat.id, message_id=users[c.message.chat.id]['msg_id2'], text='Обновлено!').message_id
                qw = """UPDATE `users` SET `msg_id2` = %d  WHERE `user_id` = %d """ %(users[c.message.chat.id]['msg_id2'], c.message.chat.id)
                cursor.execute(qw)
                db.commit()

            else:
                try:
                    if users[c.message.chat.id]['msg_id1'].text != get_stat(0, 'stat'):
                        users[c.message.chat.id]['msg_id1'] = bot.edit_message_text(chat_id=c.message.chat.id, message_id=users[c.message.chat.id]['msg_id2'], text=get_stat(0, 'stat'), reply_markup = key, parse_mode= 'HTML').message_id
                        qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[c.message.chat.id]['msg_id1'], c.message.chat.id)
                        cursor.execute(qw)
                        db.commit()
                except:
                    users[c.message.chat.id]['msg_id1'] = bot.edit_message_text(chat_id=c.message.chat.id, message_id=users[c.message.chat.id]['msg_id2'], text=get_stat(0, 'stat'), reply_markup = key, parse_mode= 'HTML').message_id
                    qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[c.message.chat.id]['msg_id1'], c.message.chat.id)
                    cursor.execute(qw)
                    db.commit()
                users[c.message.chat.id]['msg_id2'] = bot.send_message(c.message.chat.id, text='Обновлено!').message_id
                qw = """UPDATE `users` SET `msg_id2` = %d  WHERE `user_id` = %d """ %(users[c.message.chat.id]['msg_id2'], c.message.chat.id)
                cursor.execute(qw)
                db.commit()

            before = datetime.datetime.now()
        else:

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(wait_time(3))
            loop.close()

            bot.answer_callback_query(callback_query_id=c.id, show_alert=False, text="Обновлено✅")

            key = types.InlineKeyboardMarkup()
            but_1 = types.InlineKeyboardButton(text="↻", callback_data="Overload")
            key.add(but_1)

            if users[c.message.chat.id]['msg_id1'] != '' and users[c.message.chat.id]['msg_id2'] != '':
                try:
                    users[c.message.chat.id]['msg_id1'] = bot.edit_message_text(chat_id=c.message.chat.id, message_id=users[c.message.chat.id]['msg_id1'], text=get_stat(0, 'stat'), reply_markup = key, parse_mode= 'HTML').message_id
                    qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[c.message.chat.id]['msg_id1'], c.message.chat.id)
                    cursor.execute(qw)
                    db.commit()

                except:
                    pass
                users[c.message.chat.id]['msg_id2'] = bot.edit_message_text(chat_id=c.message.chat.id, message_id=users[c.message.chat.id]['msg_id2'], text='Обновлено!').message_id
                qw = """UPDATE `users` SET `msg_id2` = %d  WHERE `user_id` = %d """ %(users[c.message.chat.id]['msg_id2'], c.message.chat.id)
                cursor.execute(qw)
                db.commit()

            else:
                try:
                    users[c.message.chat.id]['msg_id1'] = bot.edit_message_text(chat_id=c.message.chat.id, message_id=users[c.message.chat.id]['msg_id2'], text=get_stat(0, 'stat'), reply_markup = key, parse_mode= 'HTML').message_id
                    qw = """UPDATE `users` SET `msg_id1` = %d  WHERE `user_id` = %d """ %(users[c.message.chat.id]['msg_id1'], c.message.chat.id)
                    cursor.execute(qw)
                    db.commit()

                except:
                    pass
                users[c.message.chat.id]['msg_id2'] = bot.send_message(c.message.chat.id, text='Обновлено!').message_id
                qw = """UPDATE `users` SET `msg_id2` = %d  WHERE `user_id` = %d """ %(users[message.chat.id]['msg_id2'], c.message.chat.id)
                cursor.execute(qw)
                db.commit()


@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    global users
    bot.edit_message_reply_markup(message.chat.id, users[message.chat.id]['msg_id1'], reply_markup = '')
    if users[message.chat.id]['distribution']['action'] == 'Check_picture' and users[message.chat.id]['status'] == 'owner' or users[message.chat.id]['distribution']['action'] == 'Check_picture' and users[message.chat.id]['status'] == 'admin':
        print('!')
        try:
            users[message.chat.id]['distribution']['picture'] = message.photo[0].file_id
            bot.reply_to(message,"Фото успешно добавлено✅")
            key = types.InlineKeyboardMarkup()
            but_1 = types.InlineKeyboardButton(text="без текста",callback_data="Without_text")
            but_2 = types.InlineKeyboardButton(text="отмена",callback_data="ADMStop")
            key.add(but_1)
            key.add(but_2)
            users[message.chat.id]['msg_id1'] = bot.send_message(message.chat.id, "Пришли текст одним сообщением (форматирование с помощью HTML)", reply_markup=key)
            users[message.chat.id]['distribution']['action'] = 'Check_text'
        except Exception as e:
            bot.reply_to(message, str(e) + '\n\nПришли картинку снова, если ошибка останется, сообщи @Garison_777')



# Снимаем вебхук перед повторной установкой (избавляет от некоторых проблем)
bot.remove_webhook()

 # Ставим заново вебхук
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Указываем настройки сервера CherryPy
cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})

 # Собственно, запуск!
cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})





# bot.polling(none_stop=True)

