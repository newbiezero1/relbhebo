import sys

import requests

import config
import util
from notifyer import Notifyer
from bybit import Bybit
from discord_client import DiscordClient

def get_last_command() -> dict:
    """Get updates and check id in saved file"""
    response = requests.get(f'https://api.telegram.org/bot{config.tg_api_key}/getUpdates?offset=-1')
    data = response.json()["result"][0]
    old_id = util.get_content_file(config.files_list["tg_bot_message"])
    new_id = data["update_id"]
    if old_id != str(new_id):
        util.set_content_file(config.files_list["tg_bot_message"], new_id)
        return data["message"]
    else:
        return {}


message = get_last_command()
if not message:
    sys.exit()
# get users chat id
allowed_chat_id=[]
for user in config.users.values():
    allowed_chat_id.append(user["tg_chat_id"])

# check if i dont know user -> exit
if message["from"]["id"] not in allowed_chat_id:
    sys.exit("You are not allowed to")
# check cmd
cmd = message["text"]
if cmd not in config.tg_bot_cmd_list:
    sys.exit()

user = util.get_user_by_chat_id(int(message["from"]["id"]))
notifyer = Notifyer(user["tg_chat_id"])

if cmd == "/my_active":
    try:
        bybit = Bybit(user)
    except Exception as e:
        util.error(f'can\'t connect to bybit api, user: *{user["name"]}*')
    open_positions = bybit.get_open_positions()
    open_orders = bybit.get_open_orders()
    notifyer.send_my_active(open_positions, open_orders)
elif cmd == "/ahmed_active":
    client = DiscordClient(config.discord_token)
    message = client.fetch_messages(config.bheem_channels["active"])
    notifyer.send_message(message[0]["content"])
