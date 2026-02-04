# -*- coding: utf-8 -*-
import logging
import sqlite3
import zipfile
import random, time, asyncio
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime, timedelta
from aiogram.utils.markdown import quote_html
import config as cfg
from time import gmtime
from time import strptime
from decimal import Decimal
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, User as TGUser
from aiogram.dispatcher.storage import FSMContext
from typing import Union
from peewee import Model, CharField, SqliteDatabase, DoesNotExist, IntegerField
from aiogram.dispatcher.middlewares import BaseMiddleware
import keyboards as kb
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
from threading import Thread
from pycoingecko import CoinGeckoAPI
from aiogram.types import ContentType, Message
from time import gmtime, strptime, strftime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.utils.exceptions import Throttled
from ling import rate_limit

api = CoinGeckoAPI()

scheduler =AsyncIOScheduler(timezone="Europe/Moscow")

class IsAdminFilter(BoundFilter):
    key = "is_admin"
    
    def __init__(self, is_admin):
          	 self.is_admin = is_admin
    
    async def check(self, message: types.Message):
          	 member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
          	 return member.is_chat_admin()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=cfg.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
class dialog(StatesGroup):
	spam = State()
	

dp.filters_factory.bind(IsAdminFilter)

connect = sqlite3.connect("db.db")
cursor = connect.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id BIGINT,
    name STRING,
    status STRING,
    rubs INT,
    bacs INT,
    games INT,
    last_bonus INT,
    limitperedachi INT,
    viptime INT,
    c INT
)
""")

cursor.execute("""CREATE TABLE IF NOT EXISTS bot(
    chat_id INT,
    user_id INT,
    last_stavka INT
)
""")

cursor.execute("""CREATE TABLE IF NOT EXISTS casino(
    rub INT DEFAULT 100000,
    dol INT DEFAULT 20
)
""")

cursor.execute("""CREATE TABLE IF NOT EXISTS torch(
	user_id BIGINT,
	id1 INT DEFAULT 0,
	id2 INT DEFAULT 0,
	id3 INT DEFAULT 0,
	level INT DEFAULT 1,
	casa INT DEFAULT 0,
	time INT DEFAULT 0
)
""")

async def anti_flood():
    return

@dp.callback_query_handler(lambda c: c.data == "checker")
async def channel(callback_query: types.CallbackQuery):
    usid = callback_query.from_user.id
    rubs = cursor.execute("SELECT rubs from users where user_id = ?",(usid,)).fetchone()
    rubs = int(rubs[0])
    name = cursor.execute("SELECT name from users where user_id = ?",(usid,)).fetchone()
    name = str(name[0])
    some_var = await bot.get_chat_member(-1001899529812, usid)
    c = cursor.execute("SELECT c FROM users WHERE user_id = ?",(usid,)).fetchone()
    c = int(c[0])
    if c == 1:
       await bot.send_message(callback_query.message.chat.id, f"ℹ️ <a href='tg://user?id={usid}'>{name}</a>, вы не можете выполнить задание повторно!", parse_mode='html')
       return

    if some_var.status == 'member' or some_var.status == 'administrator' or some_var.status == 'creator':
       await bot.send_message(callback_query.message.chat.id, f"✅ <a href='tg://user?id={usid}'>{name}</a>, вы успешно выполнили задание! \n🎁 На ваш баланс зачислено: 15.000 ₽", parse_mode='html')
       cursor.execute(f'UPDATE users SET rubs = {rubs + 15000}  WHERE user_id = ?', (usid,))
       cursor.execute(f'UPDATE users SET check = {1}  WHERE user_id = ?', (usid,))
       connect.commit()            
    else:
       await bot.send_message(callback_query.message.chat.id, f"🚫 | <a href='tg://user?id={usid}'>{name}</a>, вы не подписались на наш канал!", parse_mode='html')             

@dp.message_handler(text=["Задание", "задание"])
async def teth(message):
       msg = message
       user_id = msg.from_user.id
       name = cursor.execute("SELECT name from users where user_id = ?", (message.from_user.id,)).fetchone()
       name = str(name[0])
       c = cursor.execute("SELECT c FROM users WHERE user_id = ?",(message.from_user.id,)).fetchone()
       c = int(c[0])
       if c == 0:
          await bot.send_message(message.chat.id, f"💰 <a href='tg://user?id={user_id}'>{name}</a>, за подписку на наш канал вы получите 15.000 ₽ на свой баланс", parse_mode='html', reply_markup=kb.channel)
       if c == 1:
          await bot.send_message(message.chat.id, f"ℹ️ <a href='tg://user?id={user_id}'>{name}</a>, вы не можете выполнить задание повторно!", parse_mode='html')

@dp.message_handler(content_types=["text"], text=["пинг", "Пинг"])
@dp.throttled(anti_flood, rate=1)
async def ping(message: types.Message):
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    a = time.time()
    bot_message = await message.answer(f'⚙ Проверка пинга....')
    if bot_message:
          	 b = time.time()
          	 await bot_message.edit_text(f'Пинг: <b>{round((b - a) * 1000)}</b> ms\nОЗУ: <b>{mem}</b>%\nCPU: <b>{cpu}</b>%', parse_mode='html')


@dp.message_handler(text=['барыга', 'Барыга'])
@dp.throttled(anti_flood, rate=1)
async def donate(message):
	chat_id = message.chat.id
	user_id = message.from_user.id
	bacs = cursor.execute("SELECT bacs from users where user_id = ?", (message.from_user.id,)).fetchone()
	bacs = int(bacs[0])
	status = cursor.execute("SELECT status from users where user_id = ?", (message.from_user.id,)).fetchone()
	status = str(status[0])
	if status == "Block":
		return
	else:
		await bot.send_message(chat_id, f"""📋 Здаров друг, выбирай товар по душе.

 Баксы » <b>💵 {bacs}</b>

<b>1000 ₽</b> - <b>💵 10</b> 
<b>10.000 ₽</b> - <b>💵 75</b> 
<b>50.000 ₽</b> - <b>💵 300</b> 
<b>100.000 ₽</b> - <b>💵 500</b> 
<b>500.000 ₽</b> - <b>💵 1100</b> 

<b><i>VIP</i></b> - <b>💵 300</b>  <i>(30 Дней)</i>""", parse_mode='html', reply_markup=kb.donat)

@dp.callback_query_handler(text='vipbuy')
@dp.throttled(anti_flood, rate=1)
async def craft_resurs3(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    name = cursor.execute("SELECT name from users where user_id = ?", (callback.from_user.id,)).fetchone()
    name = str(name[0])
    period = 2592000
    get = cursor.execute("SELECT viptime FROM users WHERE user_id = ?", (callback.from_user.id,)).fetchone()
    viptime = f"{int(get[0])}"
    stavkatime = time.time() - float(viptime)

    bacs = cursor.execute("SELECT bacs from users where user_id = ?",(callback.from_user.id,)).fetchone()
    bacs = int(bacs[0])

    status = cursor.execute("SELECT status from users where user_id = ?",(callback.from_user.id,)).fetchone()
    status = str(status[0])
    if status == "Vip":
    	await callback.message.answer(f"У вас уже есть <b><i>VIP</i></b> статус")
    if bacs >= 200:
       await callback.message.answer( f"💸 <a href='tg://user?id={user_id}'>{name}</a>, вы успешно купили <b><i>VIP</i></b> статус на 30 дней", parse_mode='html' )
       cursor.execute(f'UPDATE users SET status = "Vip" WHERE user_id = {user_id}')
       cursor.execute(f'UPDATE users SET viptime=? WHERE user_id=?', (time.time(), user_id,))
       cursor.execute(f'UPDATE users SET bacs = {bacs - 200} WHERE user_id = {user_id}')
       connect.commit()
    else:
       await callback.message.answer( f"🆘 <a href='tg://user?id={user_id}'>{name}</a>, ошибка! У вас нехватает 💵", parse_mode='html' )

@dp.callback_query_handler(text='bal5')
@dp.throttled(anti_flood, rate=1)
async def craft_resurs3(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    name = cursor.execute("SELECT name from users where user_id = ?", (callback.from_user.id,)).fetchone()
    name = str(name[0])

    bacs = cursor.execute("SELECT bacs from users where user_id = ?",(callback.from_user.id,)).fetchone()
    bacs = int(bacs[0])
    
    rubs = cursor.execute("SELECT rubs from users where user_id = ?",(callback.from_user.id,)).fetchone()
    rubs = int(rubs[0])
    
    if bacs >= 1100:
       await callback.message.answer( f"💸 <a href='tg://user?id={user_id}'>{name}</a>, вы успешно купили игровую валюту в сумме 500.000 ₽", parse_mode='html' )
       cursor.execute(f'UPDATE users SET rubs = {rubs + 500000} WHERE user_id = {user_id}')
       cursor.execute(f'UPDATE users SET bacs = {bacs - 1100} WHERE user_id = {user_id}') 
       connect.commit()
    else:
       await callback.message.answer( f"🆘 <a href='tg://user?id={user_id}'>{name}</a>, ошибка! У вас нехватает 💵", parse_mode='html' )

@dp.callback_query_handler(text='bal4')
@dp.throttled(anti_flood, rate=1)
async def craft_resurs3(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    name = cursor.execute("SELECT name from users where user_id = ?", (callback.from_user.id,)).fetchone()
    name = str(name[0])

    rubs = cursor.execute("SELECT rubs from users where user_id = ?",(callback.from_user.id,)).fetchone()
    rubs = int(rubs[0])
    
    bacs = cursor.execute("SELECT bacs from users where user_id = ?", (callback.from_user.id,)).fetchone()
    bacs = int(bacs[0])
    
    if bacs >= 500:
       await callback.message.answer( f"💸 <a href='tg://user?id={user_id}'>{name}</a>, вы успешно купили игровую валюту в сумме 100.000 ₽", parse_mode='html' )
       cursor.execute(f'UPDATE users SET rubs = {rubs + 100000} WHERE user_id = {user_id}')
       cursor.execute(f'UPDATE users SET bacs = {bacs - 500} WHERE user_id = {user_id}') 
       connect.commit()
    else:
       await callback.message.answer( f"🆘 <a href='tg://user?id={user_id}'>{name}</a>, ошибка! У вас нехватает 💵", parse_mode='html' )

@dp.callback_query_handler(text='bal3')
@dp.throttled(anti_flood, rate=1)
async def craft_resurs3(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    name = cursor.execute("SELECT name from users where user_id = ?", (callback.from_user.id,)).fetchone()
    name = str(name[0])

    rubs = cursor.execute("SELECT rubs from users where user_id = ?",(callback.from_user.id,)).fetchone()
    rubs = int(rubs[0])
    
    bacs = cursor.execute("SELECT bacs from users where user_id = ?", (callback.from_user.id,)).fetchone()
    bacs = int(bacs[0])
    
    if bacs >= 300:
       await callback.message.answer( f"💸 <a href='tg://user?id={user_id}'>{name}</a>, вы успешно купили игровую валюту в сумме 50.000 ₽", parse_mode='html' )
       cursor.execute(f'UPDATE users SET runs = {rubs + 50000} WHERE user_id = {user_id}')
       cursor.execute(f'UPDATE users SET bacs = {bacs - 300} WHERE user_id = {user_id}') 
       connect.commit()
    else:
       await callback.message.answer( f"🆘 <a href='tg://user?id={user_id}'>{name}</a>, ошибка! У вас нехватает 💵", parse_mode='html' )

@dp.callback_query_handler(text='bal2')
@dp.throttled(anti_flood, rate=1)
async def craft_resurs3(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    name = cursor.execute("SELECT name from users where user_id = ?", (callback.from_user.id,)).fetchone()
    name = str(name[0])

    rubs = cursor.execute("SELECT rubs from users where user_id = ?",(callback.from_user.id,)).fetchone()
    rubs = int(rubs[0])
    
    bacs = cursor.execute("SELECT bacs from users where user_id = ?", (callback.from_user.id,)).fetchone()
    bacs = int(bacs[0])
    
    if bacs >= 75:
       await callback.message.answer( f"💸 <a href='tg://user?id={user_id}'>{name}</a>, вы успешно купили игровую валюту в сумме 10.000 ₽", parse_mode='html' )
       cursor.execute(f'UPDATE users SET rubs = {rubs + 10000} WHERE user_id = {user_id}')
       cursor.execute(f'UPDATE users SET bacs = {bacs - 75} WHERE user_id = {user_id}') 
       connect.commit()
    else:
       await callback.message.answer( f"🆘 <a href='tg://user?id={user_id}'>{name}</a>, ошибка! У вас нехватает 💵", parse_mode='html' )

@dp.callback_query_handler(text='bal1')
@dp.throttled(anti_flood, rate=1)
async def craft_resurs3(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    name = cursor.execute("SELECT name from users where user_id = ?", (callback.from_user.id,)).fetchone()
    name = str(name[0])

    rubs = cursor.execute("SELECT rubs from users where user_id = ?",(callback.from_user.id,)).fetchone()
    rubs = int(rubs[0])
    
    bacs = cursor.execute("SELECT bacs from users where user_id = ?", (callback.from_user.id,)).fetchone()
    bacs = int(bacs[0])
    
    if bacs >= 10:
       await callback.message.answer( f"💸 <a href='tg://user?id={user_id}'>{name}</a>, вы успешно купили игровую валюту в сумме 1.000", parse_mode='html' )
       cursor.execute(f'UPDATE users SET rubs = {rubs + 1000} WHERE user_id = {user_id}')
       cursor.execute(f'UPDATE users SET bacs = {bacs - 10} WHERE user_id = {user_id}') 
       connect.commit()
    else:
       await callback.message.answer( f"🆘 <a href='tg://user?id={user_id}'>{name}</a>, ошибка! У вас нехватает 💵", parse_mode='html' )


@dp.message_handler(lambda t: t.text.startswith("Дать"))
@dp.throttled(anti_flood, rate=1)
async def startswith(message):
          	reply2 = message.reply_to_message.from_user.id
          	user_id = message.from_user.id
          	name = message.from_user.full_name 
          	rname =  message.reply_to_message.from_user.full_name 
          	reply = message.from_user.id
          	reply_name = message.reply_to_message.from_user.get_mention(as_html=True)
          	reply_user_id = message.reply_to_message.from_user.id
          	win = ['🙂', '😋', '😄', '🤑', '😃']
          	rwin = random.choice(win)
          	loser = ['😔', '😕', '😣', '😞', '😢']
          	rloser = random.choice(loser)
          	perevod = float(message.text.split()[1])
          	c = Decimal(perevod)
          	c2 = round(c)
          	c2 = '{:,}'.format(c2).replace(',', '.')
          	print(f' перевел: {perevod} игроку {rname}')

          	cursor.execute(f'SELECT user_id FROM users WHERE user_id = "{user_id}"')
          	rubs = cursor.execute("SELECT rubs from users where user_id = ?", (message.from_user.id,)).fetchone()
          	rubs = round(int(rubs[0]))
          	rubs2 = cursor.execute("SELECT rubs from users where user_id = ?", (message.reply_to_message.from_user.id,)).fetchone()
          	rubs2 = round(rubs2[0])
          	limitperedachi = cursor.execute("SELECT limitperedachi from users where user_id = ?", (message.from_user.id,)).fetchone()
          	limitperedachi = int(limitperedachi[0])
          	status = cursor.execute("SELECT status from users where user_id = ?", (message.from_user.id,)).fetchone()
          	if status[0] == "Block":
          	   return
          	if not message.reply_to_message:
          	   await message.reply("Эта команда должна быть ответом на сообщение!")
          	   return
          	
          	if reply_user_id == user_id:
          	   await message.reply_to_message.reply(f'Вы не можете передать деньги сами себе! {rloser}', parse_mode='html')
          	   return
          	if status[0] == "Player" and limitperedachi-perevod >= 0:
          	   if perevod > 0:
          	   	if rubs >= perevod:
          	   		await message.reply_to_message.reply(f'💵 Вы передали {c2} игроку {rname}', parse_mode='html')
          	   		cursor.execute(f'UPDATE users SET rubs = {rubs - perevod} WHERE user_id = "{user_id}"') 
          	   		cursor.execute(f'UPDATE users SET rubs = {rubs2 + perevod} WHERE user_id = "{reply_user_id}"')
          	   		cursor.execute(f'UPDATE users SET limitperedachi = {limitperedachi - perevod} WHERE user_id = "{user_id}"')
          	if status[0] == "Player" and limitperedachi-perevod <= 0:
          	   await message.reply(f'💵 Вы уже передали дневную норму или же превышаете лимит дневную норму, лимит можно найти в профиле', parse_mode='html')
          	if status[0] == "Vip":
          	   if perevod > 0:
          	   	if rubs >= perevod:
          	   		await message.reply_to_message.reply(f'💵 Вы передали {c2} игроку {rname}', parse_mode='html')
          	   		cursor.execute(f'UPDATE users SET rubs = {rubs - perevod} WHERE user_id = "{user_id}"') 
          	   		cursor.execute(f'UPDATE users SET rubs = {rubs2 + perevod} WHERE user_id = "{reply_user_id}"')
          	   admin_id = cfg.owner_id
          	   await bot.send_message(admin_id, f"💸 | <a href='tg://user?id={user_id}'>{name}</a> передал {c2} игроку <a href='tg://user?id={reply_user_id}'>{rname}</a> {rwin}", parse_mode='html')

          	if perevod <= 0:
          	   await message.reply( f'<a href="tg://user?id={reply}">{name}</a>, нельзя перевести отрицательное число! {rloser}', parse_mode='html')  
          	if status[0] == "Admin":
          	   if perevod > 0:
          	   	if rubs >= perevod:
          	   		await message.reply_to_message.reply(f'💵 Вы передали {c2} игроку {rname}', parse_mode='html')
          	   		cursor.execute(f'UPDATE users SET rubs = {rubs - perevod} WHERE user_id = "{user_id}"') 
          	   		cursor.execute(f'UPDATE users SET rubs = {rubs2 + perevod} WHERE user_id = "{reply_user_id}"')
          	   admin_id = cfg.owner_id
          	   await bot.send_message(admin_id, f"💸 | <a href='tg://user?id={user_id}'>{name}</a> передал {c2} игроку <a href='tg://user?id={reply_user_id}'>{rname}</a> {rwin}", parse_mode='html')

          	if perevod <= 0:
          	   await message.reply( f'<a href="tg://user?id={reply}">{name}</a>, нельзя перевести отрицательное число! {rloser}', parse_mode='html')  
          	if status[0] == "Owner":
          	   if perevod > 0:
          	   	if rubs >= perevod:
          	   		await message.reply_to_message.reply(f'💵 Вы передали {c2} игроку {rname}', parse_mode='html')
          	   		cursor.execute(f'UPDATE users SET rubs = {rubs - perevod} WHERE user_id = "{user_id}"') 
          	   		cursor.execute(f'UPDATE users SET rubs = {rubs2 + perevod} WHERE user_id = "{reply_user_id}"')
          	   admin_id = cfg.owner_id
          	   await bot.send_message(admin_id, f"💸 | <a href='tg://user?id={user_id}'>{name}</a> передал {c2} игроку <a href='tg://user?id={reply_user_id}'>{rname}</a> {rwin}", parse_mode='html')

          	if perevod <= 0:
          	   await message.reply( f'<a href="tg://user?id={reply}">{name}</a>, нельзя перевести отрицательное число! {rloser}', parse_mode='html')  

@dp.message_handler(lambda t: t.text.startswith("дать"))
@dp.throttled(anti_flood, rate=1)
async def startswith(message):
          	reply2 = message.reply_to_message.from_user.id
          	user_id = message.from_user.id
          	name = message.from_user.full_name 
          	rname =  message.reply_to_message.from_user.full_name 
          	reply = message.from_user.id
          	reply_name = message.reply_to_message.from_user.get_mention(as_html=True)
          	reply_user_id = message.reply_to_message.from_user.id
          	win = ['🙂', '😋', '😄', '🤑', '😃']
          	rwin = random.choice(win)
          	loser = ['😔', '😕', '😣', '😞', '😢']
          	rloser = random.choice(loser)
          	perevod = float(message.text.split()[1])
          	c = Decimal(perevod)
          	c2 = round(c)
          	c2 = '{:,}'.format(c2).replace(',', '.')
          	print(f' перевел: {perevod} игроку {rname}')

          	cursor.execute(f'SELECT user_id FROM users WHERE user_id = "{user_id}"')
          	rubs = cursor.execute("SELECT rubs from users where user_id = ?", (message.from_user.id,)).fetchone()
          	rubs = round(int(rubs[0]))
          	rubs2 = cursor.execute("SELECT rubs from users where user_id = ?", (message.reply_to_message.from_user.id,)).fetchone()
          	rubs2 = round(rubs2[0])
          	limitperedachi = cursor.execute("SELECT limitperedachi from users where user_id = ?", (message.from_user.id,)).fetchone()
          	limitperedachi = int(limitperedachi[0])
          	status = cursor.execute("SELECT status from users where user_id = ?", (message.from_user.id,)).fetchone()
          	if status[0] == "Block":
          	   return
          	if not message.reply_to_message:
          	   await message.reply("Эта команда должна быть ответом на сообщение!")
          	   return
          	
          	if reply_user_id == user_id:
          	   await message.reply_to_message.reply(f'Вы не можете передать деньги сами себе! {rloser}', parse_mode='html')
          	   return
          	if status[0] == "Player" and limitperedachi-perevod >= 0:
          	   if perevod > 0:
          	   	if rubs >= perevod:
          	   		await message.reply_to_message.reply(f'💵 Вы передали {c2} игроку {rname}', parse_mode='html')
          	   		cursor.execute(f'UPDATE users SET rubs = {rubs - perevod} WHERE user_id = "{user_id}"') 
          	   		cursor.execute(f'UPDATE users SET rubs = {rubs2 + perevod} WHERE user_id = "{reply_user_id}"')
          	   		cursor.execute(f'UPDATE users SET limitperedachi = {limitperedachi - perevod} WHERE user_id = "{user_id}"')
          	if status[0] == "Player" and limitperedachi-perevod <= 0:
          	   await message.reply(f'💵 Вы уже передали дневную норму или же превышаете лимит дневную норму, лимит можно найти в профиле', parse_mode='html')
          	if status[0] == "Vip":
          	   if perevod > 0:
          	   	if rubs >= perevod:
          	   		await message.reply_to_message.reply(f'💵 Вы передали {c2} игроку {rname}', parse_mode='html')
          	   		cursor.execute(f'UPDATE users SET rubs = {rubs - perevod} WHERE user_id = "{user_id}"') 
          	   		cursor.execute(f'UPDATE users SET rubs = {rubs2 + perevod} WHERE user_id = "{reply_user_id}"')
          	   admin_id = cfg.owner_id
          	   await bot.send_message(admin_id, f"💸 | <a href='tg://user?id={user_id}'>{name}</a> передал {c2} игроку <a href='tg://user?id={reply_user_id}'>{rname}</a> {rwin}", parse_mode='html')

          	if perevod <= 0:
          	   await message.reply( f'<a href="tg://user?id={reply}">{name}</a>, нельзя перевести отрицательное число! {rloser}', parse_mode='html')  
          	if status[0] == "Admin":
          	   if perevod > 0:
          	   	if rubs >= perevod:
          	   		await message.reply_to_message.reply(f'💵 Вы передали {c2} игроку {rname}', parse_mode='html')
          	   		cursor.execute(f'UPDATE users SET rubs = {rubs - perevod} WHERE user_id = "{user_id}"') 
          	   		cursor.execute(f'UPDATE users SET rubs = {rubs2 + perevod} WHERE user_id = "{reply_user_id}"')
          	   admin_id = cfg.owner_id
          	   await bot.send_message(admin_id, f"💸 | <a href='tg://user?id={user_id}'>{name}</a> передал {c2} игроку <a href='tg://user?id={reply_user_id}'>{rname}</a> {rwin}", parse_mode='html')

          	if perevod <= 0:
          	   await message.reply( f'<a href="tg://user?id={reply}">{name}</a>, нельзя перевести отрицательное число! {rloser}', parse_mode='html')  
          	if status[0] == "Owner":
          	   if perevod > 0:
          	   	if rubs >= perevod:
          	   		await message.reply_to_message.reply(f'💵 Вы передали {c2} игроку {rname}', parse_mode='html')
          	   		cursor.execute(f'UPDATE users SET rubs = {rubs - perevod} WHERE user_id = "{user_id}"') 
          	   		cursor.execute(f'UPDATE users SET rubs = {rubs2 + perevod} WHERE user_id = "{reply_user_id}"')
          	   admin_id = cfg.owner_id
          	   await bot.send_message(admin_id, f"💸 | <a href='tg://user?id={user_id}'>{name}</a> передал {c2} игроку <a href='tg://user?id={reply_user_id}'>{rname}</a> {rwin}", parse_mode='html')

          	if perevod <= 0:
          	   await message.reply( f'<a href="tg://user?id={reply}">{name}</a>, нельзя перевести отрицательное число! {rloser}', parse_mode='html')  

@dp.message_handler(commands=['sql'])
@dp.throttled(anti_flood, rate=1)
async def sql(message: types.Message):

    if message.from_user.id == cfg.owner_id:
        try:
            cursor.execute(message.text[message.text.find(' '):])
            connect.commit()
            a = time.time()
            bot_msg = await message.answer(f'🕘Please wait while me doing SQL request', parse_mode="Markdown")
            if bot_msg:
                b = time.time()
                await bot_msg.edit_text(f"🚀*SQL Запрос был выполнен за {round((b - a) * 1000)} ms*",
                                        parse_mode="Markdown")
        except Exception as e:
            connect.rollback()
            await message.answer(f"❌ Возникла ошибка при изменении\n⚠️ Ошибка: {e}")
    else:
        await message.answer("❌ *Эта команда доступна только создателю бота*",parse_mode="Markdown")

@dp.message_handler(text=['Админ', 'админ'])
@dp.throttled(anti_flood, rate=1)
async def admin(message: types.Message):
	name = message.from_user.full_name
	status = cursor.execute("SELECT status from users where user_id = ?",(message.from_user.id,)).fetchone()
	status = str(status[0])
	
	if status == "Admin":
		await bot.send_message(message.chat.id, f"{name}, войдите в админ меню 🆘", reply_markup=kb.adminaccept)
		
	if status == "Owner":
		await bot.send_message(message.chat.id, f"{name}, войдите в админ меню 🆘", reply_markup=kb.adminaccept)


@dp.callback_query_handler(lambda x: x.data == "ac")
@dp.throttled(anti_flood, rate=1)
async def adminm(call: types.CallbackQuery):
    name = call.from_user.full_name
    reply = call.from_user.id     
    status = cursor.execute("SELECT status from users where user_id = ?", (call.from_user.id,)).fetchone()
    status = str(status[0])
    if status == 'Admin':
       await call.message.edit_text(f'''✅ <b>УСПЕШНЫЙ ВХОД В АДМИН МЕНЮ</b>

❗️ Права администратора: <b>Admin</b>

➖➖➖➖➖➖➖➖➖➖➖➖➖➖
🔐 Категории

👥 <b>Статистика бота</b>
📝 <b>Админ команды</b>

➖➖➖➖➖➖➖➖➖➖➖➖➖➖
↘️ Выбери одну из категорий''', parse_mode='html', reply_markup=kb.adminmenu)
       return

    if status == 'Owner':
       await call.message.edit_text(f'''✅ <b>УСПЕШНЫЙ ВХОД В АДМИН МЕНЮ</b>

❗️ Права администратора: <b>Owner</b>

➖➖➖➖➖➖➖➖➖➖➖➖➖➖
🔐 Категории

👥 <b>Статистика бота</b>

➖➖➖➖➖➖➖➖➖➖➖➖➖➖
↘️ Выбери одну из категорий''', parse_mode='html', reply_markup=kb.adminmenu)
       return
       
@dp.callback_query_handler(lambda x: x.data == "sadmin")
@dp.throttled(anti_flood, rate=1)
async def stats(call: types.CallbackQuery):

   sqlite_select_query2 = '''SELECT * from users where status = \"Block\"'''
   cursor.execute(sqlite_select_query2)
   records = cursor.fetchall()

   sqlite_select_query2 = '''SELECT * from users where status = \"Admin\"'''
   cursor.execute(sqlite_select_query2)
   records2 = cursor.fetchall()
   
   sqlite_select_query2 = '''SELECT * from users where status = \"Rab\"'''
   cursor.execute(sqlite_select_query2)
   records4 = cursor.fetchall()

   sqlite_select_query2 = '''SELECT * from users'''
   cursor.execute(sqlite_select_query2)
   us = cursor.fetchall()
  
   cursor.execute(f"SELECT status FROM users")
   status = cursor.fetchall()
   cursor.execute(f"SELECT user_id FROM users")
   users = cursor.fetchall()
   usid = call.from_user.id
   list = cursor.execute(f"SELECT * FROM users")
   status = cursor.execute("SELECT status from users where user_id = ?",(call.from_user.id,)).fetchone()
   status = str(status[0])
   if status in ['Owner', 'Admin']:
      await call.message.edit_text(f"""
🔍 Статистика бота

🔓 Основа
         👤 Игроков: {len(us)}

🛑 Администрация
         📛 Заблокировано: {len(records)}
         👮‍♂ ADMIN: {len(records2)}
         🥋 OWNER: {len(records4)}""", reply_markup=kb.naz)

@dp.message_handler(commands=['ban_id'])
@dp.throttled(anti_flood, rate=1)
async def start_cmd(message):
    name = cursor.execute("SELECT name from users where user_id = ?", (message.from_user.id,)).fetchone()
    name = str(name[0])
    msg = message
    user_id = msg.from_user.id
    reply_user_id = int(message.text.split()[1])

    status = cursor.execute("SELECT status from users where user_id = ?", (message.from_user.id,)).fetchone()
    status = str(status[0])
    if status == "Owner":
    	       await bot.send_message(message.chat.id, f"🚀 {name}, вы заблокировали аккаунт игроку <b>{reply_user_id}</b>", parse_mode='html')
    	       cursor.execute(f'UPDATE users SET status = "Block"  WHERE user_id = {reply_user_id}')
    	       connect.commit()
    	       return

@dp.message_handler(commands=['owner_id'])
@dp.throttled(anti_flood, rate=1)
async def start_cmd(message):
    name = cursor.execute("SELECT name from users where user_id = ?", (message.from_user.id,)).fetchone()
    name = str(name[0])
    msg = message
    user_id = msg.from_user.id
    reply_user_id = int(message.text.split()[1])

    status = cursor.execute("SELECT status from users where user_id = ?", (message.from_user.id,)).fetchone()
    status = str(status[0])
    if user_id == cfg.owner_id:
    	       await bot.send_message(message.chat.id, f"🚀 {name}, вы выдали разработчика игроку <b>{reply_user_id}</b>", parse_mode='html')
    	       cursor.execute(f'UPDATE users SET status = "Owner"  WHERE user_id = {reply_user_id}')
    	       connect.commit()
    	       return

@dp.message_handler(commands=['admin'])
@dp.throttled(anti_flood, rate=1)
async def start_cmd(message):
    name = cursor.execute("SELECT name from users where user_id = ?", (message.from_user.id,)).fetchone()
    name = str(name[0])
    msg = message
    user_id = msg.from_user.id
    reply_user_id = message.reply_to_message.from_user.id

    status = cursor.execute("SELECT status from users where user_id = ?", (message.from_user.id,)).fetchone()
    status = str(status[0])
    if user_id == cfg.owner_id:
    	       await bot.send_message(message.chat.id, f"🚀 {name}, вы выдали админа игроку <b>{reply_user_id}</b>", parse_mode='html')
    	       cursor.execute(f'UPDATE users SET status = "Admin"  WHERE user_id = {reply_user_id}')
    	       connect.commit()
    	       return


@dp.message_handler(commands=['owner'])
@dp.throttled(anti_flood, rate=1)
async def start_cmd(message):
    name = cursor.execute("SELECT name from users where user_id = ?", (message.from_user.id,)).fetchone()
    name = str(name[0])
    msg = message
    user_id = msg.from_user.id
    reply_user_id = message.reply_to_message.from_user.id

    status = cursor.execute("SELECT status from users where user_id = ?", (message.from_user.id,)).fetchone()
    status = str(status[0])
    if user_id == cfg.owner_id:
    	       await bot.send_message(message.chat.id, f"🚀 {name}, вы выдали разработчика игроку <b>{reply_user_id}</b>", parse_mode='html')
    	       cursor.execute(f'UPDATE users SET status = "Owner"  WHERE user_id = {reply_user_id}')
    	       connect.commit()
    	       return

@dp.message_handler(commands=['admin_id'])
@dp.throttled(anti_flood, rate=1)
async def start_cmd(message):
    name = cursor.execute("SELECT name from users where user_id = ?", (message.from_user.id,)).fetchone()
    name = str(name[0])
    msg = message
    user_id = msg.from_user.id
    reply_user_id = int(message.text.split()[1])

    status = cursor.execute("SELECT status from users where user_id = ?", (message.from_user.id,)).fetchone()
    status = str(status[0])
    if user_id == cfg.owner_id:
    	       await bot.send_message(message.chat.id, f"🚀 {name}, вы выдали админа игроку <b>{reply_user_id}</b>", parse_mode='html')
    	       cursor.execute(f'UPDATE users SET status = "Admin"  WHERE user_id = {reply_user_id}')
    	       connect.commit()
    	       return

@dp.message_handler(commands=['status_id'])
@dp.throttled(anti_flood, rate=1)
async def start_cmd(message):
    name = cursor.execute("SELECT name from users where user_id = ?", (message.from_user.id,)).fetchone()
    name = str(name[0])
    msg = message
    user_id = msg.from_user.id
    reply_user_id = int(message.text.split()[1])

    status = cursor.execute("SELECT status from users where user_id = ?", (message.from_user.id,)).fetchone()
    status = str(status[0])
    if user_id == cfg.owner_id:
    	       await bot.send_message(message.chat.id, f"🚀 {name}, вы забрали статус у <b>{reply_user_id}</b>", parse_mode='html')
    	       cursor.execute(f'UPDATE users SET status = "Player"  WHERE user_id = {reply_user_id}')
    	       connect.commit()
    	       return

@dp.message_handler(commands=['unban_id'])
@dp.throttled(anti_flood, rate=1)
async def start_cmd(message):
    name = cursor.execute("SELECT name from users where user_id = ?", (message.from_user.id,)).fetchone()
    name = str(name[0])
    msg = message
    user_id = msg.from_user.id
    reply_user_id = int(message.text.split()[1])

    status = cursor.execute("SELECT status from users where user_id = ?", (message.from_user.id,)).fetchone()
    status = str(status[0])
    if status == "Owner":
    	       await bot.send_message(message.chat.id, f"🚀 {name}, вы разблокировали аккаунт игроку <b>{reply_user_id}</b>", parse_mode='html')
    	       cursor.execute(f'UPDATE users SET status = "Player"  WHERE user_id = {reply_user_id}')
    	       connect.commit()
    	       return

@dp.message_handler(text=["б", "Б", "Баланс", "баланс"])
@dp.throttled(anti_flood, rate=1)
async def rubs(message):
    user_id = message.from_user.id
    rubs = cursor.execute("SELECT rubs from users where user_id = ?",(message.from_user.id,)).fetchone()
    rubs = int(rubs[0])
    bacs = cursor.execute("SELECT bacs from users where user_id = ?", (message.from_user.id,)).fetchone()
    bacs = int(bacs[0])
    status = cursor.execute("SELECT status from users where user_id = ?",(message.from_user.id,)).fetchone()
    status = str(status[0])
    name = cursor.execute("SELECT name from users where user_id = ?", (message.from_user.id,)).fetchone()
    name = str(name[0])
    last_bonus = cursor.execute("SELECT last_bonus from users where user_id = ?",(message.from_user.id,)).fetchone()
    last_bonus = int(last_bonus[0])
    from utils import scor_summ
    rubs2 = await scor_summ(rubs)
    bacs2 = await scor_summ(bacs)
    if status == "Block":
    	return
    if last_bonus == 0:
    	if status == "Player":
    		await bot.send_message(message.chat.id, f"<b><i>Игрок</i></b> ➪ <a href='tg://user?id={user_id}'>{name}</a>\nБаланс: <b>₽ {rubs2}</b>\nБаксы: 💵 <b>{bacs2}</b>", parse_mode='html', reply_markup=kb.bonuska)
    	if status == "Vip":
    		await bot.send_message(message.chat.id, f"♦<b><i>VIP</i></b> ➪ <a href='tg://user?id={user_id}'>{name}</a>\nБаланс: <b>₽ {rubs2}</b>\nБаксы: 💵 <b>{bacs2}</b>", reply_markup=kb.bonuska)
    	if status == "Admin":
    		await bot.send_message(message.chat.id, f"🔹<b><i>ADMIN</i></b> ➪ <a href='tg://user?id={user_id}'>{name}</a>\nБаланс: <b>₽ {rubs2}</b>\nБаксы: 💵 <b>{bacs2}</b>", parse_mode='html', reply_markup=kb.bonuska)
    	if status == "Owner":
    		await bot.send_message(message.chat.id, f"🔸<b><i>OWNER</i></b> ➪ <a href='tg://user?id={user_id}'>{name}</a>\nБаланс: <b>₽ {rubs2}</b>\nБаксы: 💵 <b>{bacs2}</b>", parse_mode='html', reply_markup=kb.bonuska)
    if last_bonus >= 1:
    	if status == "Player":
    		await bot.send_message(message.chat.id, f"<b><i>Игрок</i></b> ➪ <a href='tg://user?id={user_id}'>{name}</a>\nБаланс: <b>₽ {rubs2}</b>\nБаксы: 💵 <b>{bacs2}</b>", parse_mode='html')
    	if status == "Vip":
    		await bot.send_message(message.chat.id, f"♦<b><i>VIP</i></b> ➪ <a href='tg://user?id={user_id}'>{name}</a>\nБаланс: <b>₽ {rubs2}</b>\nБаксы: 💵 <b>{bacs2}</b>", parse_mode='html')
    	if status == "Admin":
    		await bot.send_message(message.chat.id, f"🔹<b><i>ADMIN</i></b> ➪ <a href='tg://user?id={user_id}'>{name}</a>\nБаланс: <b>₽ {rubs2}</b>\nБаксы: 💵 <b>{bacs2}</b>", parse_mode='html')
    	if status == "Owner":
    		await bot.send_message(message.chat.id, f"🔸<b><i>OWNER</i></b> ➪ <a href='tg://user?id={user_id}'>{name}</a>\nБаланс: <b>₽ {rubs2}</b>\nБаксы: 💵 <b>{bacs2}</b>", parse_mode='html')
#<b><i>VIP</i></b>
@dp.callback_query_handler(text='bonus')
@dp.throttled(anti_flood, rate=2)
async def craft_resurs3(callback: types.CallbackQuery):
          	 user_id = callback.from_user.id
          	 name = callback.from_user.full_name
          	 win = ['🙂', '😋', '😄', '🤑', '😃']
          	 rwin = random.choice(win)
          	 loser = ['😔', '😕', '😣', '😞', '😢']
          	 rloser = random.choice(loser)
          	 period = 86400
          	 status = cursor.execute("SELECT status from users where user_id = ?",(callback.from_user.id,)).fetchone()
          	 status = str(status[0])
          	 rubs = cursor.execute("SELECT rubs from users where user_id = ?", (callback.from_user.id,)).fetchone()
          	 rubs = int(rubs[0])
          	 bacs = cursor.execute("SELECT bacs from users where user_id = ?", (callback.from_user.id,)).fetchone()
          	 bacs = int(bacs[0])
          	 get = cursor.execute("SELECT last_bonus FROM users WHERE user_id = ?", (user_id,)).fetchall()
          	 last_bonus = f'{int(get[0][0])}'        
          	 bonustime = time.time() - float(last_bonus)
          	 reply = callback.from_user.id
          	 prize = random.randint(1, 2)
          	 rating_bonus = random.randint(200, 1000)
          	 rating_bonus2 = '{:,}'.format(rating_bonus)
          	 rating_bonus3 = '{:,}'.format(rating_bonus*2)
          	 money_bonus = random.randint(500000000, 5000000000)
          	 money_bonus2 = '{:,}'.format(money_bonus).replace(',', '.')
          	 connect.commit()
          	 rubs2 = '{:,}'.format(rubs).replace(',', '.')
          	 xuy = ["20", "30", "40"]
          	 expe3 = random.choice(xuy)
          	 if bonustime > period:
          	     if status == "Vip":
          	     	if prize == 1:
          	     		cursor.execute(f'UPDATE users SET rubs = {rubs + rating_bonus*2}  WHERE user_id = ?', (user_id,))
          	     		cursor.execute(f'UPDATE users SET last_bonus=? WHERE user_id=?', (time.time(), user_id,))
          	     		connect.commit()
          	     		await callback.message.answer(f'🎁 <a href="tg://user?id={reply}">{name}</a>, ты получил бонус в размере <b>{str(rating_bonus3)}</b> <b><i>VIP X2</i></b>', parse_mode='html')

          	     	if prize == 2:
          	     		cursor.execute(f'UPDATE users SET rubs = {rubs + rating_bonus*2}  WHERE user_id = ?', (user_id,))
          	     		cursor.execute(f'UPDATE users SET last_bonus=? WHERE user_id=?', (time.time(), user_id,))
          	     		connect.commit()
          	     		await callback.message.answer(f'🎁 <a href="tg://user?id={reply}">{name}</a>, ты получил бонус в размере <b>{str(rating_bonus3)}</b> <b><i>VIP X2</i></b>', parse_mode='html')
          	     if status == "Player":
          	     	if prize == 1:
          	     		cursor.execute(f'UPDATE users SET rubs = {rubs + rating_bonus}  WHERE user_id = ?', (user_id,))
          	     		cursor.execute(f'UPDATE users SET last_bonus=? WHERE user_id=?', (time.time(), user_id,))
          	     		connect.commit()
          	     		await callback.message.answer(f'🎁 <a href="tg://user?id={reply}">{name}</a>, ты получил бонус в размере <b>{str(rating_bonus2)}</b>', parse_mode='html')

          	     	if prize == 2:
          	     		cursor.execute(f'UPDATE users SET rubs = {rubs + rating_bonus}  WHERE user_id = ?', (user_id,))
          	     		cursor.execute(f'UPDATE users SET last_bonus=? WHERE user_id=?', (time.time(), user_id,))
          	     		connect.commit()
          	     		await callback.message.answer(f'🎁 <a href="tg://user?id={reply}">{name}</a>, ты получил бонус в размере <b>{str(rating_bonus2)}</b>', parse_mode='html')

          	     if status == "Admin":
          	     	if prize == 1:
          	     		cursor.execute(f'UPDATE users SET rubs = {rubs + rating_bonus}  WHERE user_id = ?', (user_id,))
          	     		cursor.execute(f'UPDATE users SET last_bonus=? WHERE user_id=?', (time.time(), user_id,))
          	     		connect.commit()
          	     		await callback.message.answer(f'🎁 <a href="tg://user?id={reply}">{name}</a>, ты получил бонус в размере <b>{str(rating_bonus2)}</b>', parse_mode='html')

          	     	if prize == 2:
          	     		cursor.execute(f'UPDATE users SET rubs = {rubs + rating_bonus}  WHERE user_id = ?', (user_id,))
          	     		cursor.execute(f'UPDATE users SET last_bonus=? WHERE user_id=?', (time.time(), user_id,))
          	     		connect.commit()
          	     		await callback.message.answer(f'🎁 <a href="tg://user?id={reply}">{name}</a>, ты получил бонус в размере <b>{str(rating_bonus2)}</b>', parse_mode='html')

          	     if status == "Owner":
          	     	if prize == 1:
          	     		cursor.execute(f'UPDATE users SET rubs = {rubs + rating_bonus}  WHERE user_id = ?', (user_id,))
          	     		cursor.execute(f'UPDATE users SET last_bonus=? WHERE user_id=?', (time.time(), user_id,))
          	     		connect.commit()
          	     		await callback.message.answer(f'🎁 <a href="tg://user?id={reply}">{name}</a>, ты получил бонус в размере <b>{str(rating_bonus2)}</b>', parse_mode='html')

          	     	if prize == 2:
          	     		cursor.execute(f'UPDATE users SET rubs = {rubs + rating_bonus}  WHERE user_id = ?', (user_id,))
          	     		cursor.execute(f'UPDATE users SET last_bonus=? WHERE user_id=?', (time.time(), user_id,))
          	     		connect.commit()
          	     		await callback.message.answer(f'🎁 <a href="tg://user?id={reply}">{name}</a>, ты получил бонус в размере <b>{str(rating_bonus2)}</b>', parse_mode='html')
          	     	else:
          	     		await callback.message.answer(f'ℹ️ <a href="tg://user?id={reply}">{name}</a>, ты уже получал сегодня бонус!', parse_mode='html')

@dp.callback_query_handler(lambda c: c.data == "botof")
@dp.throttled(anti_flood, rate=1)
async def ok(callback_query: types.CallbackQuery):
   usid = callback_query.from_user.id
   if usid == cfg.owner_id:
   	await callback_query.message.delete()
   	time.sleep(1)
   	await bot.send_message(callback_query.message.chat.id, f'Выключение бота...')
   	dp.stop_polling()

@dp.message_handler(text=['помощь', 'Помощь'])
@dp.throttled(anti_flood, rate=1)
async def help(message):
	chat_id = message.chat.id
	status = cursor.execute("SELECT status from users where user_id = ?",(message.from_user.id,)).fetchone()
	status = str(status[0])
	if status == "Block":
		return
	else:
		await bot.send_message(chat_id, f"""💰 Баланс/б » выведет ваш баланс
📝 Профиль/п » покажет ваш профиль
🎰 Слоты » игра на деньги
💰 Дать » передать деньги игроку
🗯 Чат » список чатов
🎯 Барыга » товары за 💵""")

@dp.message_handler(text=['беседа', 'Беседа', 'чат', 'Чат'])
@dp.throttled(anti_flood, rate=1)
async def chats(message):
	chat_id = message.chat.id
	await bot.send_message(chat_id, f"""📚 <b><a href="https://t.me/waivegamechat">Waive Game Chat</a>
✏ <a href="https://t.me/waivegamedev">Waive » DEV</a></b>""", parse_mode = 'html')

@dp.message_handler(text=['профиль', 'Профиль', 'п', 'П'])
@dp.throttled(anti_flood, rate=1)
async def profile(message):
    status = cursor.execute("SELECT status from users where user_id = ?",(message.from_user.id,)).fetchone()
    status = str(status[0])
    user_id = message.from_user.id
    name = cursor.execute("SELECT name from users where user_id = ?", (message.from_user.id,)).fetchone()
    name = str(name[0])
    chat_id = message.chat.id
    rubs = cursor.execute("SELECT rubs from users where user_id = ?",(message.from_user.id,)).fetchone()
    rubs = int(rubs[0])
    games = cursor.execute("SELECT games from users where user_id = ?",(message.from_user.id,)).fetchone()
    games = int(games[0])	
    bacs = cursor.execute("SELECT bacs from users where user_id = ?",(message.from_user.id,)).fetchone()
    bacs = int(bacs[0])
    get = cursor.execute("SELECT viptime FROM users WHERE user_id=?", (message.from_user.id,)).fetchall()
    mtime = f"{int(get[0][0])}"
    times = time.time() - float(mtime)
    limitperedachi = cursor.execute("SELECT limitperedachi from users where user_id = ?",(message.from_user.id,)).fetchone()
    vremya = strftime("%j дней %H часов %M минут", gmtime(times))
    limitperedachi = int(limitperedachi[0])
    limitperedachi=10000-limitperedachi
    limitp = '{:,}'.format(limitperedachi).replace(',', '.')
    rubs2 = '{:,}'.format(rubs).replace(',', '.')
    bacs2 = '{:,}'.format(bacs).replace(',', '.')
    games2 = '{:,}'.format(games).replace(',', '.')
    if status == "Block":
    	return
    if status == "Player":
    	await bot.send_message(chat_id, f"""🗯 Ник » <b>{name}</b>
🆔 User ID » <b>{user_id}</b>

💰 Баланс » <b>₽ {rubs2}</b>
💵 Баксы » <b>💵 {bacs2}</b>
🏵 Статус » Игрок
🎯 Сыграно игр » <b>{games2}</b>

💱 Передано: <b>{limitp}/10.000</b>""", parse_mode='html')
    	return
    if status == "Vip":
    	await bot.send_message(chat_id, f"""🗯 Ник » <b>{name}</b>
🆔 User ID » <b>{user_id}</b>

💰 Баланс » <b>₽ {rubs2}</b>
💵 Баксы » <b>💵 {bacs2}</b>
🏵 Статус » <b><i>VIP</i></b>
🎯 Сыграно игр » <b>{games2}</b>

💱 Безлимит на передачу""", parse_mode='html')
    	return
    else:
    	await bot.send_message(chat_id, f"""🗯 Ник » <b>{name}</b>
🆔 User ID » <b>{user_id}</b>

💰 Баланс » <b>₽ {rubs2}</b>
💵 Баксы » <b>💵 {bacs2}</b>
🎯 Сыграно игр » <b>{games2}</b>""", parse_mode='html')

@dp.message_handler(lambda t: t.text.startswith("+бакс"))
@dp.throttled(anti_flood, rate=1)
async def startswith(message):
          	reply2 = message.reply_to_message.from_user.id       
          	message = message
          	name = message.from_user.full_name
          	reply = message.from_user.id
          	reply_name = message.reply_to_message.from_user.get_mention(as_html=True)
          	win = ['🙂', '😋', '😄', '🤑', '😃']
          	rwin = random.choice(win)
          	perevod = float(message.text.split()[1])
          	reply_user_id = message.reply_to_message.from_user.id
          	user_id = message.from_user.id
          	user_id = message.from_user.id
          	status = cursor.execute("SELECT status from users where user_id = ?",(message.from_user.id,)).fetchone()
          	bacs2 = cursor.execute("SELECT bacs from users where user_id = ?", (message.reply_to_message.from_user.id,)).fetchone()
          	bacs2 = round(bacs2[0])
          	if user_id == cfg.owner_id:
          	   await message.reply(f'💰 Вы выдали 💵{c2}', parse_mode='html')
          	   cursor.execute(f'UPDATE users SET bacs = {bacs2 + perevod} WHERE user_id = "{reply_user_id}"')
          	   connect.commit()



@dp.message_handler(text=["инфо", "Инфо", 'info', "Info"])
@dp.throttled(anti_flood, rate=1)
async def teht(message):
          	status = cursor.execute("SELECT status from users where user_id = ?",(message.from_user.id,)).fetchone()
          	status = str(status[0])
          	reply_status = cursor.execute("SELECT status from users where user_id = ?",(message.reply_to_message.from_user.id,)).fetchone()
          	reply_status = str(reply_status[0])
          	bacs = cursor.execute("SELECT bacs from users where user_id = ?",(message.reply_to_message.from_user.id,)).fetchone()
          	bacs = int(bacs[0])
          	reply_user_id = message.reply_to_message.from_user.id        
          	limitperedachi = cursor.execute("SELECT limitperedachi from users where user_id = ?",(message.reply_to_message.from_user.id,)).fetchone()
          	limitperedachi = int(limitperedachi[0])
          	limitperedachi=10000-limitperedachi
          	limitp = '{:,}'.format(limitperedachi).replace(',', '.')
          	chat_id = message.chat.id
          	rubs = cursor.execute("SELECT rubs from users where user_id = ?",(message.reply_to_message.from_user.id,)).fetchone()
          	rubs = round(int(rubs[0]))
          	if reply_status == "Admin":
          		statuus = 'Администратор 🏆'
          	if reply_status == "Rab":
          		statuus = 'Разработчик 👑'
          	if reply_status == "Player":
          		statuus = "💤 Игрок"
          	if reply_status == "Block":
          		statuus = "Заблокирован"
          	games = cursor.execute("SELECT games from users where user_id = ?",(message.reply_to_message.from_user.id,)).fetchone()
          	games = int(games[0])
          	if status == "Admin" or status == "Owner" or user_id == cfg.owner_id:
          		if reply_status == "Vip":
          			          			await bot.send_message(message.chat.id, f'''🆔 User ID » <b>{reply_user_id}</b>

💰 Баланс » <b>₽ {rubs}</b>
💵 Баксы » <b>💵 {bacs}</b>
🎯 Сыграно игр » <b>{games}

💱 Безлимит на передачу
₽ {reply_status}</b>''', parse_mode='html')
          		else:
          			await bot.send_message(message.chat.id, f'''🆔 User ID » <b>{reply_user_id}</b>

💰 Баланс » <b>₽ {rubs}</b>
💵 Баксы » <b>💵 {bacs}</b>
🎯 Сыграно игр » <b>{games}

💱 Передано: <b>{limitp}/10.000</b>
₽ {reply_status}</b>''', parse_mode='html')

@dp.message_handler(commands=["info_id"])
@dp.throttled(anti_flood, rate=1)
async def teht(message):
          	reply_user_id = int(message.text.split()[1])
          	status = cursor.execute(f"SELECT status from users where user_id = {reply_user_id}").fetchone()
          	status = str(status[0])
          	reply_status = cursor.execute(f"SELECT status from users where user_id = {reply_user_id}").fetchone()
          	reply_status = str(reply_status[0])
          	rubs = cursor.execute(f"SELECT rubs from users where user_id = {reply_user_id}").fetchone()
          	rubs = int(rubs[0])       
          	limitperedachi = cursor.execute(f"SELECT limitperedachi from users where user_id = {reply_user_id}").fetchone()
          	limitperedachi = int(limitperedachi[0])
          	limitperedachi=10000-limitperedachi
          	limitp = '{:,}'.format(limitperedachi).replace(',', '.')
          	chat_id = message.chat.id
          	rubs = cursor.execute(f"SELECT rubs from users where user_id = {reply_user_id}").fetchone()
          	rubs = round(int(rubs[0]))
          	if reply_status == "Admin":
          		statuus = 'Администратор 🏆'
          	if reply_status == "Rab":
          		statuus = 'Разработчик 👑'
          	if reply_status == "Player":
          		statuus = "💤 Игрок"
          	if reply_status == "Block":
          		statuus = "Заблокирован"
          	games = cursor.execute(f"SELECT games from users where user_id = {reply_user_id}").fetchone()
          	games = int(games[0])
          	if status == "Admin" or status == "Owner" or user_id == cfg.owner_id:
          		if reply_status == "Vip":
          			          			await bot.send_message(message.chat.id, f'''🆔 User ID » <b>{reply_user_id}</b>

💰 Баланс » <b>{rubs} ₽</b>
💵 Баксы » <b>{rubs}</b>
🎯 Сыграно игр » <b>{games}

💱 Безлимит на передачу
{reply_status}</b>''', parse_mode='html')
          		else:
          			await bot.send_message(message.chat.id, f'''🆔 User ID » <b>{reply_user_id}</b>

💰 Баланс » <b>{rubs} ₽</b>
💵 Баксы » <b>{rubs}</b>
🎯 Сыграно игр » <b>{games}

💱 Передано: <b>{limitp}/10.000</b>
{reply_status}</b>''', parse_mode='html')

@dp.message_handler(text=["обнулить", "Обнулить"])
async def teht(message):
          	message = message
          	
          	reply_name = message.reply_to_message.from_user.get_mention(as_html=True)
          	win = ['🙂', '😋', '😄', '🤑', '😃']
          	rwin = random.choice(win)
          	reply_user_id = message.reply_to_message.from_user.id
          	user_id = message.from_user.id
          	status = cursor.execute("SELECT status from users where user_id = ?",(message.from_user.id,)).fetchone()
          	if status[0] == "Admin":
          	   await message.reply(f'💰 Вы обнулили аккаунт игрока', parse_mode='html')
          	   cursor.execute(f'UPDATE users SET rubs = {500} WHERE user_id = "{reply_user_id}"')
          	   cursor.execute(f'UPDATE users SET games = {0} WHERE user_id = "{reply_user_id}"')
          	   cursor.execute(f'UPDATE users SET last_bonus = {0} WHERE user_id = "{reply_user_id}"')
          	   cursor.execute(f'UPDATE users SET limitperedachi = {10000} WHERE user_id = "{reply_user_id}"')
          	   connect.commit()
          	if status[0] == "Owner":
          	   await message.reply(f'💰 Вы обнулили аккаунт игрока', parse_mode='html')
          	   cursor.execute(f'UPDATE users SET rubs = {500} WHERE user_id = "{reply_user_id}"')
          	   cursor.execute(f'UPDATE users SET games = {0} WHERE user_id = "{reply_user_id}"')
          	   cursor.execute(f'UPDATE users SET last_bonus = {0} WHERE user_id = "{reply_user_id}"')
          	   cursor.execute(f'UPDATE users SET limitperedachi = {10000} WHERE user_id = "{reply_user_id}"')
          	   connect.commit()

@dp.message_handler(lambda t: t.text.startswith("забрать"))
async def startswith(message):
          	reply2 = message.reply_to_message.from_user.id       
          	message = message
          	reply = message.from_user.id
          	reply_name = message.reply_to_message.from_user.get_mention(as_html=True)
          	win = ['🙂', '😋', '😄', '🤑', '😃']
          	rwin = random.choice(win)
          	perevod = float(message.text.split()[1])
          	reply_user_id = message.reply_to_message.from_user.id
          	user_id = message.from_user.id
          	c = Decimal(perevod)
          	c2 = round(c)
          	c2 = '{:,}'.format(c2).replace(',', '.')
          	status = cursor.execute("SELECT status from users where user_id = ?",(message.from_user.id,)).fetchone()
          	rubs2 = cursor.execute("SELECT rubs from users where user_id = ?", (message.reply_to_message.from_user.id,)).fetchone()
          	rubs2 = round(rubs2[0])
          	if status[0] == 'Owner':
          	   await message.reply(f'💰 Вы забрали {c2}', parse_mode='html')
          	   cursor.execute(f'UPDATE users SET rubs = {rubs2 - perevod} WHERE user_id = "{reply_user_id}"')
          	   connect.commit()
          	if status[0] == "Admin":
          	   await message.reply(f'💰 Вы забрали {c2}', parse_mode='html')
          	   cursor.execute(f'UPDATE users SET rubs = {rubs2 - perevod} WHERE user_id = "{reply_user_id}"')

          	   connect.commit()

@dp.message_handler(lambda t: t.text.startswith("Забрать"))
async def startswith(message):
          	reply2 = message.reply_to_message.from_user.id       
          	message = message
          	reply = message.from_user.id
          	reply_name = message.reply_to_message.from_user.get_mention(as_html=True)
          	win = ['🙂', '😋', '😄', '🤑', '😃']
          	rwin = random.choice(win)
          	perevod = float(message.text.split()[1])
          	reply_user_id = message.reply_to_message.from_user.id
          	user_id = message.from_user.id
          	c = Decimal(perevod)
          	c2 = round(c)
          	c2 = '{:,}'.format(c2).replace(',', '.')
          	status = cursor.execute("SELECT status from users where user_id = ?",(message.from_user.id,)).fetchone()
          	rubs2 = cursor.execute("SELECT rubs from users where user_id = ?", (message.reply_to_message.from_user.id,)).fetchone()
          	rubs2 = round(rubs2[0])
          	if status[0] == 'Owner':
          	   await message.reply(f'💰 Вы забрали {c2}', parse_mode='html')
          	   cursor.execute(f'UPDATE users SET rubs = {rubs2 - perevod} WHERE user_id = "{reply_user_id}"')
          	   connect.commit()
          	if status[0] == "Admin":
          	   await message.reply(f'💰 Вы забрали {c2}', parse_mode='html')
          	   cursor.execute(f'UPDATE users SET rubs = {rubs2 - perevod} WHERE user_id = "{reply_user_id}"')

          	   connect.commit()

@dp.message_handler(lambda t: t.text.startswith("Выдать"))
async def startswith(message):
          	reply2 = message.reply_to_message.from_user.id       
          	message = message
          	reply = message.from_user.id
          	reply_name = message.reply_to_message.from_user.get_mention(as_html=True)
          	win = ['🙂', '😋', '😄', '🤑', '😃']
          	rwin = random.choice(win)
          	perevod = float(message.text.split()[1])
          	reply_user_id = message.reply_to_message.from_user.id
          	user_id = message.from_user.id
          	c = Decimal(perevod)
          	c2 = round(c)
          	c2 = '{:,}'.format(c2).replace(',', '.')
          	status = cursor.execute("SELECT status from users where user_id = ?",(message.from_user.id,)).fetchone()
          	rubs2 = cursor.execute("SELECT rubs from users where user_id = ?", (message.reply_to_message.from_user.id,)).fetchone()
          	rubs2 = round(rubs2[0])
          	if status[0] == 'Owner':
          	   await message.reply(f'💰 Вы выдали {c2}', parse_mode='html')
          	   cursor.execute(f'UPDATE users SET rubs = {rubs2 + perevod} WHERE user_id = "{reply_user_id}"')
          	   connect.commit()
          	if status[0] == "Admin":
          	   await message.reply(f'💰 Вы выдали {c2}', parse_mode='html')
          	   cursor.execute(f'UPDATE users SET rubs = {rubs2 + perevod} WHERE user_id = "{reply_user_id}"')

          	   connect.commit()

@dp.message_handler(lambda t: t.text.startswith("выдать"))
async def startswith(message):
          	reply2 = message.reply_to_message.from_user.id       
          	message = message
          	reply = message.from_user.id
          	reply_name = message.reply_to_message.from_user.get_mention(as_html=True)
          	win = ['🙂', '😋', '😄', '🤑', '😃']
          	rwin = random.choice(win)
          	perevod = float(message.text.split()[1])
          	reply_user_id = message.reply_to_message.from_user.id
          	user_id = message.from_user.id
          	c = Decimal(perevod)
          	c2 = round(c)
          	c2 = '{:,}'.format(c2).replace(',', '.')
          	status = cursor.execute("SELECT status from users where user_id = ?",(message.from_user.id,)).fetchone()
          	rubs2 = cursor.execute("SELECT rubs from users where user_id = ?", (message.reply_to_message.from_user.id,)).fetchone()
          	rubs2 = round(rubs2[0])
          	if status[0] == 'Owner':
          	   await message.reply(f'💰 Вы выдали {c2}', parse_mode='html')
          	   cursor.execute(f'UPDATE users SET rubs = {rubs2 + perevod} WHERE user_id = "{reply_user_id}"')
          	   connect.commit()
          	if status[0] == "Admin":
          	   await message.reply(f'💰 Вы выдали {c2}', parse_mode='html')
          	   cursor.execute(f'UPDATE users SET rubs = {rubs2 + perevod} WHERE user_id = "{reply_user_id}"')

          	   connect.commit()

@dp.message_handler(text=["слоты", "Слоты"])
@dp.throttled(anti_flood, rate=1)
async def casino1(message):
	user_id = message.from_user.id
	chat_id = message.chat.id
	rub = cursor.execute("SELECT rub from casino").fetchone()
	rub = int(rub[0])
	dol = cursor.execute("SELECT dol from casino").fetchone()
	dol = int(dol[0])
	emoji = ["🔋", "💣", "💵", "💎"]
	r1 = random.choice(emoji)
	r2 = random.choice(emoji)
	r3 = random.choice(emoji)
	from utils import scor_summ
	dol2 = await scor_summ(dol)
	rub2 = await scor_summ(rub)
	await bot.send_message(chat_id, f"""
		   🎰 Казино – Slots 🎰
		   
💵 {dol}     джекпоты    {rub2} ₽

            | {r1} | {r2} | {r3} |
             
             Крути барабан""", reply_markup=kb.casino)

@dp.callback_query_handler(lambda x: x.data == "cas_rub")
@dp.throttled(anti_flood, rate=1)
async def casino(call: types.CallbackQuery):
	user_id = call.from_user.id
	rub = cursor.execute("SELECT rub from casino").fetchone()
	rub = int(rub[0])
	dol = cursor.execute("SELECT dol from casino").fetchone()
	dol = int(dol[0])
	rubs = cursor.execute("SELECT rubs from users where user_id = ?", (call.from_user.id,)).fetchone()
	rubs = int(rubs[0])
	bacs = cursor.execute("SELECT bacs from users where user_id = ?", (call.from_user.id,)).fetchone()
	bacs = int(bacs[0])
	emoji = ["💣", "💵", "🔫", "🔑", "💎", "🔋", "⭐️"]
	bonus = ["1000", "2000", "5000"]
	chance_3 = -0.80
	chance_2 = -0.65
	if rub > 175000:
	   chance_3 = 0.10   # 5% на 3 в ряд
	   chance_2 = 0   # 0% на 2 одинаковых
	elif rub > 150000:
		chance_3 = -0.10   # -10%
		chance_2 = -0.45   # -45%
	roll = random.random()
	if roll < chance_3:
		r1 = r2 = r3 = random.choice(emoji)
	elif roll < chance_3 + chance_2:
		same = random.choice(emoji)
		diff = random.choice([e for e in emoji if e != same])
		pattern = random.choice([1, 2, 3])
		if pattern == 1:
			r1, r2, r3 = same, same, diff
		elif pattern == 2:
			r1, r2, r3 = same, diff, same
		else:
			r1, r2, r3 = diff, same, same

# обычный спин
	else:
		r1 = random.choice(emoji)
		r2 = random.choice(emoji)
		r3 = random.choice(emoji)
	itog1 = "Не повезло :("
	itog2 = "Вы выиграли ₽ 10k"
	itog3 = "Вы выиграли ₽ 5k"
	itog4 = "Вы выиграли 💵 1"
	itog5 = "Вы выиграли ₽ 25k"
	itog6 = "Вы выиграли 💵 5"
	itog7 = "Джекпот ₽{rub}"
	rb = random.randint(1, 5)
	from utils import scor_summ
	dol2 = await scor_summ(dol)
	rub2 = await scor_summ(rub + 1000)
	rb2 = await scor_summ(rb*1000)
	if rubs >= 10000:
		if r1 == r2 == r3:
			await call.message.edit_text(f"""
		   🎰 Казино – Slots 🎰
		   
💵 {dol2}     джекпоты    ₽ 100k

            | {r1} | {r2} | {r3} |
             
         Джекпот ₽ {rub2}""", reply_markup=kb.casino)
			cursor.execute(f'UPDATE users SET rubs ={rubs + rub} WHERE user_id={user_id}')
			cursor.execute(f'UPDATE casino SET rub = 100000')
			connect.commit()
			return
		if r1 == r2 or r2 == r3 or r1 == r3:
			await call.message.edit_text(f"""
		   🎰 Казино – Slots 🎰
		   
💵 {dol2}     джекпоты    ₽ {rub2}

            | {r1} | {r2} | {r3} |
             
         Вы выиграли ₽ {rb2}""", reply_markup=kb.casino)
			cursor.execute(f'UPDATE users SET rubs ={rubs + rb*1000} WHERE user_id={user_id}')
			cursor.execute(f'UPDATE casino SET rub = {rub + 1000}')
			connect.commit()
			return
			
		else:
			await call.message.edit_text(f"""
		   🎰 Казино – Slots 🎰
		   
💵 {dol2}     джекпоты    ₽ {rub2}

            | {r1} | {r2} | {r3} |
             
             {itog1}""", reply_markup=kb.casino)
			cursor.execute(f'UPDATE users SET rubs = {rubs - 10000} WHERE user_id={user_id}')
			cursor.execute(f'UPDATE casino SET rub = {rub + 1000}')
			connect.commit()
			return
	await call.message.edit_text(f"""
		   🎰 Казино – Slots 🎰
		   
💵 {dol + 1}     джекпоты    {rub} ₽

            | {r1} | {r2} | {r3} |
             
             Не хватает ₽""", reply_markup=kb.casino)

@dp.callback_query_handler(lambda x: x.data == "cas_dol")
@dp.throttled(anti_flood, rate=0.4)
async def casino(call: types.CallbackQuery):
	user_id = call.from_user.id
	rub = cursor.execute("SELECT rub from casino").fetchone()
	rub = int(rub[0])
	dol = cursor.execute("SELECT dol from casino").fetchone()
	dol = int(dol[0])
	rubs = cursor.execute("SELECT rubs from users where user_id = ?", (call.from_user.id,)).fetchone()
	rubs = int(rubs[0])
	bacs = cursor.execute("SELECT bacs from users where user_id = ?", (call.from_user.id,)).fetchone()
	bacs = int(bacs[0])
	emoji = ["💣", "💵", "🔫", "🔑", "💎", "🔋", "⭐️"]
	bonus = ["1", "2", "3"]
	chance_3 = -0.75
	chance_2 = -0.65
	if dol > 80:
	   chance_3 = 0.05   # 25% на 3 в ряд
	   chance_2 = 0   # 55% на 2 одинаковых
	elif dol > 40:
		chance_3 = -0.10   # 10%
		chance_2 = -0.45   # 30%
	roll = random.random()
	if roll < chance_3:
		r1 = r2 = r3 = random.choice(emoji)
	elif roll < chance_3 + chance_2:
		same = random.choice(emoji)
		diff = random.choice([e for e in emoji if e != same])
		pattern = random.choice([1, 2, 3])
		if pattern == 1:
			r1, r2, r3 = same, same, diff
		elif pattern == 2:
			r1, r2, r3 = same, diff, same
		else:
			r1, r2, r3 = diff, same, same

# обычный спин
	else:
		r1 = random.choice(emoji)
		r2 = random.choice(emoji)
		r3 = random.choice(emoji)
    
	itog1 = "Не повезло :("
	itog2 = "Вы выиграли ₽10k"
	itog3 = "Вы выиграли ₽5k"
	itog4 = "Вы выиграли 💵 1"
	itog5 = "Вы выиграли ₽25k"
	itog6 = "Вы выиграли 💵 5"
	itog7 = "Джекпот 💵{dol}"
	rb = random.choice(bonus)
	
	from utils import scor_summ
	dol2 = await scor_summ(dol)
	rub2 = await scor_summ(rub)
	rb2 = await scor_summ(rb)
	if rubs >= 10000:
		if r1 == r2 == r3:
			await call.message.edit_text(f"""
		   🎰 Казино – Slots 🎰
		   
💵 20     джекпоты    {rub} ₽

            | {r1} | {r2} | {r3} |
             
             Джекпот 💵 {dol}""", reply_markup=kb.casino)
			cursor.execute(f'UPDATE users SET bacs ={bacs + dol} WHERE user_id={user_id}')
			cursor.execute(f'UPDATE casino SET dol = 20')
			connect.commit()
			return
		if r1 == r2 or r1 == r3 or r2 == r3:
			await call.message.edit_text(f"""
		   🎰 Казино – Slots 🎰
		   
💵 {dol + 1}     джекпоты    {rub} ₽

            | {r1} | {r2} | {r3} |
             
             Вы выиграли 💵 {rb}""", reply_markup=kb.casino)
			cursor.execute(f'UPDATE users SET bacs ={bacs + rb} WHERE user_id={user_id}')
			cursor.execute(f'UPDATE casino SET dol = {dol + 1}')
			connect.commit()
			return

		else:
			await call.message.edit_text(f"""
		   🎰 Казино – Slots 🎰
		   
💵 {dol + 1}     джекпоты    {rub} ₽

            | {r1} | {r2} | {r3} |
             
             {itog1}""", reply_markup=kb.casino)
			cursor.execute(f'UPDATE users SET bacs = {bacs - 2} WHERE user_id={user_id}')
			cursor.execute(f'UPDATE casino SET dol = {dol + 1}')
			connect.commit()
			return
	else:
		await call.message.edit_text(f"""
		   🎰 Казино – Slots 🎰
		   
💵 {dol + 1}     джекпоты    {rub} ₽

            | {r1} | {r2} | {r3} |
             
             Не хватает 💵""", reply_markup=kb.casino)

@dp.message_handler(text=["Купить точку 1", "купить точку 1"])
@dp.throttled(anti_flood, rate=0.3)
async def torch(message):
	user_id = message.from_user.id
	chat_id = message.chat.id
	rubs = cursor.execute("SELECT rubs from users WHERE user_id = ?", (user_id,)).fetchone()
	rubs = int(rubs[0])
	bacs = cursor.execute("SELECT bacs from users WHERE user_id = ?", (user_id,)).fetchone()
	bacs = int(bacs[0])
	id1 = cursor.execute("SELECT id1 from torch WHERE user_id = ?", (user_id,)).fetchone()
	id1 = int(id1[0])
	id2 = cursor.execute("SELECT id2 from torch WHERE user_id = ?", (user_id,)).fetchone()
	id2 = int(id2[0])
	id3 = cursor.execute("SELECT id3 from torch WHERE user_id = ?", (user_id,)).fetchone()
	id3 = int(id3[0])
	loser = ['😔', '😕', '😣', '😞', '😢']
	rloser = random.choice(loser)
	balance = cursor.execute("SELECT balance from users where user_id = ?",(message.from_user.id,)).fetchone()
	balance = round(int(balance[0]))
	name = cursor.execute("SELECT name from users where user_id = ?", (user_id,)).fetchone()
	c = 1
	if id1 == 0:
		if rubs >= 500:
			await bot.send_message(message.chat.id, f"🖥 | <a href='tg://user?id={user_id}'>{name}</a>, ты поставил точку 'Ларёк' 🎉", parse_mode='html')
			cursor.execute(f'UPDATE users SET rubs = {rubs-500} WHERE user_id = "{user_id}"') 
			cursor.execute(f'UPDATE torch SET id1 = {1} WHERE user_id = {user_id}') 
			cursor.execute(f'UPDATE torch SET level = {1} WHERE user_id = "{user_id}"')
			connect.commit()    
		else:
			await bot.send_message(message.chat.id, f"{rloser} | <a href='tg://user?id={user_id}'>{name}</a>, у тебя не хватает ₽ лавэ", parse_mode='html')
		if id1 == 1:
			await bot.send_message(message.chat.id, f"ℹ️ | <a href='tg://user?id={user_id}'>{user_name}</a>, у тебя уже есть эта точка {rloser}", parse_mode='html')
			return
	
@dp.message_handler(text=["Купить точку 2", "купить точку 2"])
@dp.throttled(anti_flood, rate=0.3)
async def torch(message):
	user_id = message.from_user.id
	chat_id = message.chat.id
	rubs = cursor.execute("SELECT rubs from users WHERE user_id = ?", (user_id,)).fetchone()
	rubs = int(rubs[0])
	bacs = cursor.execute("SELECT bacs from users WHERE user_id = ?", (user_id,)).fetchone()
	bacs = int(bacs[0])
	id1 = cursor.execute("SELECT id1 from torch WHERE user_id = ?", (user_id,)).fetchone()
	id1 = int(id1[0])
	id2 = cursor.execute("SELECT id2 from torch WHERE user_id = ?", (user_id,)).fetchone()
	id2 = int(id2[0])
	id3 = cursor.execute("SELECT id3 from torch WHERE user_id = ?", (user_id,)).fetchone()
	id3 = int(id3[0])
	loser = ['😔', '😕', '😣', '😞', '😢']
	rloser = random.choice(loser)
	balance = cursor.execute("SELECT balance from users where user_id = ?",(message.from_user.id,)).fetchone()
	balance = round(int(balance[0]))
	name = cursor.execute("SELECT name from users where user_id = ?", (user_id,)).fetchone()
	c = 1
	if id2 == 0:
		if rubs >= 10000:
			await bot.send_message(message.chat.id, f"🖥 | <a href='tg://user?id={user_id}'>{name}</a>, ты поставил точку 'Шиномонтажка' 🎉", parse_mode='html')
			cursor.execute(f'UPDATE users SET rubs = {rubs-10000} WHERE user_id = "{user_id}"') 
			cursor.execute(f'UPDATE torch SET id2 = {1} WHERE user_id = {user_id}') 
			cursor.execute(f'UPDATE torch SET level = {1} WHERE user_id = "{user_id}"')
			connect.commit()    
		else:
			await bot.send_message(message.chat.id, f"{rloser} | <a href='tg://user?id={user_id}'>{name}</a>, у тебя не хватает ₽ лавэ", parse_mode='html')
		if id2 == 1:
			await bot.send_message(message.chat.id, f"ℹ️ | <a href='tg://user?id={user_id}'>{user_name}</a>, у тебя уже есть эта точка {rloser}", parse_mode='html')
			return

@dp.message_handler(text=["Купить точку 3", "купить точку 3"])
@dp.throttled(anti_flood, rate=0.3)
async def torch(message):
	user_id = message.from_user.id
	chat_id = message.chat.id
	rubs = cursor.execute("SELECT rubs from users WHERE user_id = ?", (user_id,)).fetchone()
	rubs = int(rubs[0])
	bacs = cursor.execute("SELECT bacs from users WHERE user_id = ?", (user_id,)).fetchone()
	bacs = int(bacs[0])
	id1 = cursor.execute("SELECT id1 from torch WHERE user_id = ?", (user_id,)).fetchone()
	id1 = int(id1[0])
	id2 = cursor.execute("SELECT id2 from torch WHERE user_id = ?", (user_id,)).fetchone()
	id2 = int(id2[0])
	id3 = cursor.execute("SELECT id3 from torch WHERE user_id = ?", (user_id,)).fetchone()
	id3 = int(id3[0])
	loser = ['😔', '😕', '😣', '😞', '😢']
	rloser = random.choice(loser)
	balance = cursor.execute("SELECT balance from users where user_id = ?",(message.from_user.id,)).fetchone()
	balance = round(int(balance[0]))
	name = cursor.execute("SELECT name from users where user_id = ?", (user_id,)).fetchone()
	if id3 == 0:
		if rubs >= 100000:
			await bot.send_message(message.chat.id, f"🖥 | <a href='tg://user?id={user_id}'>{name}</a>, ты поставил точку 'Кафэ' 🎉", parse_mode='html')
			cursor.execute(f'UPDATE users SET rubs = {rubs-100000} WHERE user_id = "{user_id}"') 
			cursor.execute(f'UPDATE torch SET id3 = {1} WHERE user_id = {user_id}') 
			cursor.execute(f'UPDATE torch SET level = {1} WHERE user_id = "{user_id}"')
			connect.commit()    
		else:
			await bot.send_message(message.chat.id, f"{rloser} | <a href='tg://user?id={user_id}'>{name}</a>, у тебя не хватает ₽ лавэ", parse_mode='html')
		if id3 == 1:
			await bot.send_message(message.chat.id, f"ℹ️ | <a href='tg://user?id={user_id}'>{user_name}</a>, у тебя уже есть эта точка {rloser}", parse_mode='html')
			return

@dp.message_handler()
@dp.throttled(anti_flood, rate=0.2)
async def start(message):
    user_id = message.from_user.id
    cursor.execute(f"SELECT user_id FROM users WHERE user_id = '{user_id}'")
    if cursor.fetchone() is None:
    	await bot.send_message(message.chat.id, f'''Привет, я игровой бот <b><i>waive</i></b>, подробнее можно узнать командой «<code>помощь</code>»''', parse_mode='html', reply_markup=kb.star)
    text = message.text.lower()
    words = message.text
    for word in text:
        	if word in words:
        	  user_id = message.from_user.id
        	  chat_id = message.chat.id
        	  status = "Player"
        	  nams = "Игрок"
        	  name = message.from_user.full_name
        	  cursor.execute(f'SELECT user_id FROM users WHERE user_id = "{user_id}"')
        	  if cursor.fetchone() is None:
        	  	cursor.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (user_id, nams, status, 500, 0, 0, 0, 10000, 0, 0))
        	  	connect.commit()
        	  	cursor.execute("INSERT INTO bot VALUES(?, ?, ?);", (chat_id, 0, 0))

        	  	connect.commit()
        	  	cursor.execute("INSERT INTO torch VALUES(?, ?, ?, ?, ?, ?, ?);", (user_id, 0, 0, 0, 1, 0, 0))

        	  	connect.commit()
    if message.forward_from != None:
       return
    else:
       pass
    if status == "Vip":
     get = cursor.execute("SELECT viptime FROM users WHERE user_id = ?", (message.from_user.id,)).fetchone()
     period = 2592000
     viptime = f"{int(get[0])}"
     stavkatime = time.time() - float(viptime)
     status = cursor.execute("SELECT status from users where user_id = ?",(message.from_user.id,)).fetchone()
     status = str(status[0])
     if stavkatime > period:
      await bot.send_message(chat_id, f"Срок действия <b><i>VIP</i></b> статуса стёк", parse_mode='html')
      cursor.execute(f'UPDATE users SET status = "Player" WHERE user_id = "{user_id}"')
    	
    	
async def cd_limit():

    cursor.execute(
        f"UPDATE users SET limitperedachi = 10000 WHERE status='Player'")

def schedule2r():
    scheduler.add_job(cd_limit,'interval', hours=6)
    scheduler.start()
    try:
        asyncio.get_event_loop().run_forever()
    except:
        pass

async def on_startup(_):
    schedule2r()
    await bot.send_message(chat_id=cfg.owner_id,text=f"""<b>🪄 Бот запущен!</b>
<code>{datetime.now().strftime("%d.%m.%y %H:%M:%S")}</code>""", parse_mode='html')
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)