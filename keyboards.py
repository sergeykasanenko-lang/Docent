from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types

channel = types.InlineKeyboardMarkup(row_width=3)
channel.add(types.InlineKeyboardButton(text='📢 Подписаться', url="https://t.me/HEKTAP_dev")) 
channel.add(types.InlineKeyboardButton(text='✅ Проверить', callback_data='checker'))

nazad = InlineKeyboardButton(text="🔙 Назад", callback_data="ac")
naz = InlineKeyboardMarkup()
naz.row(nazad)

admstats = InlineKeyboardButton(text="👥 Статистика бота", callback_data="sadmin")
admcmd = InlineKeyboardButton(text="📝 Админ команды", callback_data="admcmd")
ownermenu = InlineKeyboardButton(text="👨‍💻 Меню владельца", callback_data="omenu")
button103939 = InlineKeyboardButton(text="🔷 Выключить бота", callback_data="botof")
adminmenu = InlineKeyboardMarkup()
adminmenu.row(admstats, button103939)

accept = InlineKeyboardButton(text="✅ Войти", callback_data="ac")
adminaccept = InlineKeyboardMarkup()
adminaccept.row(accept)

cas_rub = InlineKeyboardButton(text="Крутить ₽10k", callback_data="cas_rub")
cas_dol = InlineKeyboardButton(text="Крутить 💵2", callback_data="cas_dol")
casino = InlineKeyboardMarkup()
casino.row(cas_dol, cas_rub)

bon = InlineKeyboardButton(text="🎁 Бонус", callback_data="bonus")
bonuska = InlineKeyboardMarkup().add(bon)

b1al = InlineKeyboardButton(text="1.000 ₽", callback_data="bal1")
b1al1 = InlineKeyboardButton(text="Купить", callback_data="bal1")
b2al = InlineKeyboardButton(text="10.000 ₽", callback_data="bal2")
b2al1 = InlineKeyboardButton(text="Купить", callback_data="bal2")
b3al = InlineKeyboardButton(text="50.000 ₽", callback_data="bal3")
b3al1 = InlineKeyboardButton(text="Купить", callback_data="bal3")
b4al = InlineKeyboardButton(text="100.000 ₽", callback_data="bal4")
b4al1 = InlineKeyboardButton(text="Купить", callback_data="bal4")
b5al = InlineKeyboardButton(text="500.000 ₽", callback_data="bal5")
b5al1 = InlineKeyboardButton(text="Купить", callback_data="bal5")
vi = InlineKeyboardButton(text="VIP", callback_data="vipbuy")
vib = InlineKeyboardButton(text="Купить", callback_data="vipbuy")
donat = InlineKeyboardMarkup()
donat.row(b1al, b1al1)
donat.row(b2al, b2al1)
donat.row(b3al, b3al1)
donat.row(b4al, b4al1)
donat.row(b5al, b5al1)
donat.row(vi, vib)

button10 = InlineKeyboardButton(text="Добавить бота 😄", url="https://t.me/HEKTAP_BOT?startgroup=true")
star = InlineKeyboardMarkup()
star.row(button10)