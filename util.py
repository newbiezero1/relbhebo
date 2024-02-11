"""Other functions"""
import sys
import json
import requests

import config
from notifyer import Notifyer


def error(message: str, finish: bool = True) -> None:
    """ Print error or another error trigger"""
    # send error to admins tg
    admins_chat_ids = []
    for user in config.users.values():
        if user["is_admin"]:
            admins_chat_ids.append(user["tg_chat_id"])
    for chat_id in admins_chat_ids:
        notifyer = Notifyer(chat_id)
        notifyer.send_error(message)
    if finish:
        sys.exit()


def get_content_file(filename: str) -> str:
    """ return content from file"""
    try:
        with open(filename) as f:
            data = f.read().strip()
    except FileNotFoundError:
        error("File not found : " + filename)
    return data


def set_content_file(filename: str, content: str) -> None:
    """write new content to file"""
    try:
        with open(filename, "w") as f:
            f.write(str(content))
    except FileNotFoundError:
        error("File not found : " + filename)


def check_new_message(messages: list, history_file: str) -> dict:
    """load all messages from channel and check in file"""
    # sort by chronology
    messages.reverse()

    history_messages = json.loads(get_content_file(history_file))
    new_history_messages = []
    new_message = {"content": ''}
    for message in messages:
        new_history_messages.append(message["id"])
        if message["id"] in history_messages:
            continue
        # skip img post
        if not message["content"]:
            continue
        new_message = message
        break
    # save new id in file
    #set_content_file(history_file, json.dumps(new_history_messages))
    return new_message


def save_lost_sl_trade(trade: dict) -> None:
    """Save broke trade in file for later use"""
    trades = json.loads(get_content_file(config.files_list['lost_sl_trades']))
    trades.append(trade)
    set_content_file(config.files_list['lost_sl_trades'], json.dumps(trades))


def get_user_by_chat_id(chat_id: int) -> dict:
    """Return user by id"""
    for user in config.users.values():
        if user["tg_chat_id"] == chat_id:
            return user
    return {}
