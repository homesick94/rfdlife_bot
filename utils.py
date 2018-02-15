#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import pickle
import re
import threading
from builtins import any
from datetime import datetime
from os import path

import telebot

import config
import tokens

# Инициализация бота
my_bot = telebot.TeleBot(tokens.bot, threaded=False)
my_bot_name = '@' + my_bot.get_me().username

global_lock = threading.Lock()
message_dump_lock = threading.Lock()


def commands_handler(cmnds, inline=False):
    def wrapped(message):
        if not message.text:
            return False
        split_message = re.split(r'[^\w@/]', message.text.lower())
        if not inline:
            s = split_message[0]
            return ((s in cmnds)
                    or (s.endswith(my_bot_name) and s.split('@')[0] in cmnds))
        else:
            return any(cmnd in split_message
                       or cmnd + my_bot_name in split_message
                       for cmnd in cmnds)

    return wrapped


def curr_time():
    return datetime.now().strftime('%d/%m/%Y %H:%M:%S')


def user_name(user):
    first_name = user.first_name
    last_name = ' ' + user.last_name if isinstance(user.last_name, str) else ''
    return first_name + last_name


def user_info(user):
    # Required fields
    user_id = str(user.id)
    first_name = user.first_name
    # Optional fields
    last_name = ' ' + user.last_name if isinstance(user.last_name, str) else ''
    username = ', @' + user.username if isinstance(user.username, str) else ''
    language_code = ', ' + user.language_code if isinstance(user.language_code, str) else ''
    # Output
    return user_id + ' (' + first_name + last_name + username + language_code + ')'


def chat_info(chat):
    if chat.type == 'private':
        return 'private'
    else:
        return chat.type + ': ' + chat.title + ' (' + str(chat.id) + ')'


def action_log(text):
    print("{}\n{}\n".format(curr_time(), text))


def user_action_log(message, text):
    print("{}, {}\nUser {} {}\n".format(curr_time(), chat_info(message.chat), user_info(message.from_user), text))


def is_command():
    def wrapped(message):
        if not message.text or not message.text.startswith('/'):
            return False
        return True

    return wrapped


def command_with_delay(delay=10):
    def my_decorator(func):
        def wrapped(message):
            now = datetime.now().timestamp()
            diff = now - func.last_call if hasattr(func, 'last_call') else now
            if diff < delay:
                user_action_log(message, "called {} after {} sec, delay is {}".format(func, round(diff), delay))
                return
            func.last_call = now

            return func(message)

        return wrapped

    return my_decorator


def bot_admin_command(func):
    def wrapped(message):
        if message.from_user.id in config.admin_ids:
            return func(message)
        return

    return wrapped


def is_non_zero_file(file_path):
    return path.isfile(file_path) and path.getsize(file_path) > 0


def value_from_file(file_name, default=0):
    value = default
    if path.isfile(file_name):
        global_lock.acquire()
        with open(file_name, 'r', encoding='utf-8') as file:
            file_data = file.read()
            if file_data.isdigit():
                value = int(file_data)
        global_lock.release()
    return value


def value_to_file(file_name, value):
    global_lock.acquire()
    with open(file_name, 'w+', encoding='utf-8') as file:
        file.write(str(value))
    global_lock.release()


def dump_messages(all_messages):
    groups = {}
    for message in all_messages:
        dump_filename = config.dump_dir + 'dump_' + message.chat.type + '_' + str(message.chat.id) + '.pickle'
        if dump_filename in groups:
            lst = groups[dump_filename]
        else:
            lst = []
            groups[dump_filename] = lst
        lst.append(message)

    message_dump_lock.acquire()
    for dump_filename, messages in groups.items():
        if path.isfile(dump_filename):
            f = open(dump_filename, 'rb+')
            try:
                file_messages = pickle.load(f)
            except EOFError:
                file_messages = []
            file_messages.extend(messages)
            f.seek(0)
            f.truncate()
        else:
            f = open(dump_filename, 'xb')
            file_messages = messages
        pickle.dump(file_messages, f, pickle.HIGHEST_PROTOCOL)
        f.close()
    message_dump_lock.release()


def bold(text, mode="html"):
    if mode.lower() == "html":
        return "<b>{}</b>".format(text)
    if mode.lower() == "markdown":
        return "*{}*".format(text)


def link(text, user_id, mode="html"):
    if mode.lower() == "html":
        return "<a href=\"tg://user?id={0}\">{1}</a>".format(user_id, text)
    if mode.lower() == "markdown":
        return "[{1}](tg://user?id={0})".format(user_id, text)