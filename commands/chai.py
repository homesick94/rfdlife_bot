# !/usr/bin/env python
# _*_ coding: utf-8 _*_
from datetime import datetime

from telebot import types

import config
from utils import my_bot, user_name, link


def chai_subs_notify(text, keyboard=None, me=None):
    for chat_id in config.chai_subscribers:
        try:
            if chat_id != me:
                my_bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=keyboard)
        except:
            pass


def chai(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text="Го!", callback_data="chai_go"),
                 types.InlineKeyboardButton(text="Через 5 мин", callback_data="chai_5min"))
    keyboard.add(types.InlineKeyboardButton(text="Нет, позже", callback_data="chai_no"))
    chai_subs_notify(user_name(message.from_user) + " зовет чай! ☕️", keyboard)


def chai_message(message):
    chai_subs_notify(link(user_name(message.from_user), message.from_user.id) + ": " + " ".join(message.text.split()[1:]),
                     me=message.from_user.id)


def chai_callback(call):
    msg = call.message

    if datetime.now().timestamp() - msg.date > 15 * 60:
        my_bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                 text=msg.text + "\n\n" + "Это сообщение устарело! Используй /chai.")
        my_bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Это сообщение устарело!")
        return

    text = "heh"
    if call.data == "chai_go":
        text = "✅ Ты сообщил, что сейчас придешь на кухню"
        chai_subs_notify("✅ " + link(user_name(msg.chat), msg.chat.id) + " сейчас придет на кухню!")
    elif call.data == "chai_5min":
        text = "🚗 Ты сообщил, что придешь через 5 минут"
        chai_subs_notify("5️⃣ " + link(user_name(msg.chat), msg.chat.id) + " придет через 5 минут.")
    elif call.data == "chai_no":
        text = "💔 Ты сообщил, что не придешь"
        chai_subs_notify("⛔ " + link(user_name(msg.chat), msg.chat.id) + " сейчас не хочет или не может.")

    my_bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text=msg.text, parse_mode="HTML")
    my_bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=text)