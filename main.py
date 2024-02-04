import config
from discord_client import DiscordClient
from bheem import BheemParser
import util
from notifyer import Notifyer
from bybit import Bybit

client = DiscordClient(config.discord_token)
# bheem alerts section

all_messages = client.fetch_messages(config.bheem_channels["alerts"])
new_message = util.check_new_message(all_messages, config.files_list["bheem_alerts"])
if new_message:
    bheem = BheemParser()
    bheem.parse_alert_message_data(new_message)
    for user in config.users.values():
        notifyer = Notifyer(user["tg_chat_id"])
        if bheem.check_alert_data():
            pass
        else:
            notifyer.broken_message(new_message)

# bheem trade section
all_messages = client.fetch_messages(config.bheem_channels["trades"])
new_message = util.check_new_message(all_messages, config.files_list['bheem_trades'])
if new_message:
    bheem = BheemParser()
    bheem.parse_trade_message_data(new_message)
    for user in config.users.values():
        notifyer = Notifyer(user["tg_chat_id"])

        if bheem.check_trade_data():
            # notify in tg about new message
            notifyer.new_trade(bheem.trade, new_messages)

            # make trade if this user enable autotrade
            if user["autotrade_enabled"]:
                try:
                    bybit = Bybit(user)
                except Exception as e:
                    util.error(f'can\'t connect to bybit api, user: *{user["name"]}*', finish=False)
                    continue
                bybit.set_trade_data(bheem.trade)
                bybit.make_trade()
                for order in bybit.orders:
                    notifyer.place_order(order)
        else:
            notifyer.broken_message(new_message)
