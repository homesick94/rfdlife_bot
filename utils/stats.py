# !/usr/bin/env python
# _*_ coding: utf-8 _*_
import re
from collections import Counter
from datetime import datetime

import config
from utils.common_utils import bold, link, my_bot
from utils.data_manager import my_data


def stats(message):
    users_count = len(my_data.list_users())
    alerts_count = 0

    for chat_id, user in my_data.data.items():
        alerts_count += len(user.get('alert_users', []))

    with open(config.FileLocation.bot_logs, 'r', encoding='utf-8') as file:
        file_text = file.read()
        users = re.findall('(?:User )(\d+)(?:.*called)', file_text)
        commands = re.findall('(?:User.*called )(/\w*)(?:\s)', file_text)

    user_counter = Counter(users)
    user_id = str(message.from_user.id)
    user_commands_count = user_counter[user_id]
    user_pos = user_counter.most_common().index((user_id, user_commands_count)) + 1
    all_commands_count = sum(user_counter.values())

    commands_counter = Counter(commands)
    commands_most = commands_counter.most_common(3)

    days_from_birthday = (datetime.today() - datetime(year=2018, month=2, day=9)).days

    text = f'Бот родился 9 февраля 2018 и сегодня его {bold(days_from_birthday)} день!\n' \
           f'Пользователей бота: {bold(users_count)}\n' \
           f'Команд вызвано: {bold(all_commands_count)}\n' \
           f'Суммарно отслеживаемых сотрудников: {bold(alerts_count)}\n\n'

    text += 'Вы использовали {} команд и находитесь на {} месте, вызвав {}% команд\n\n' \
            ''.format(bold(user_commands_count),
                      bold(user_pos),
                      bold(round(100 * user_commands_count / all_commands_count, 2)))

    text += 'Топ 3 команды по вызовам:\n' \
            '  1. {} — {}\n' \
            '  2. {} — {}\n' \
            '  3. {} — {}\n'.format(commands_most[0][0], bold(commands_most[0][1]),
                                    commands_most[1][0], bold(commands_most[1][1]),
                                    commands_most[2][0], bold(commands_most[2][1]))

    my_bot.reply_to(message, text, parse_mode='HTML')


def users(message):
    with open(config.FileLocation.bot_logs, 'r', encoding='utf-8') as file:
        file_text = file.read()
        users = re.findall('(?:User )(\d+)(?:.*called)', file_text)

    user_counter = Counter(users)

    text = 'Список пользователей бота:\n\n'
    count = 1
    for user_id, user in my_data.data.items():
        user_commands_count = user_counter[user_id]
        text += '{}. {} — {}\n'.format(count, link(user['who'], user_id), user_commands_count)
        count += 1
    my_bot.reply_to(message, "{}".format(text), parse_mode="HTML")


def commands(message):
    with open(config.FileLocation.bot_logs, 'r', encoding='utf-8') as file:
        file_text = file.read()
        commands = re.findall('(?:User.*called )(/\w*)(?:\s)', file_text)

    commands_counter = Counter(commands)
    commands_most = commands_counter.most_common()

    text = 'Список команд бота:\n\n'
    count = 1
    for cmd in commands_most:
        text += '{}. {} — {}\n'.format(count, *cmd)
        count += 1
    my_bot.reply_to(message, "{}".format(text), parse_mode="HTML")
