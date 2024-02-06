import json

import config
from discord_client import DiscordClient
from bheem import BheemParser
import util
from notifyer import Notifyer
from bybit import Bybit


def check_alert():
    """Check new alerts and action"""
    all_messages = client.fetch_messages(config.bheem_channels["alerts"])
    new_message = util.check_new_message(all_messages, config.files_list["bheem_alerts"])
    if new_message:
        bheem = BheemParser()
        bheem.parse_alert_message_data(new_message)
        for user in config.users.values():
            notifyer = Notifyer(user["tg_chat_id"])
            if bheem.check_alert_data():
                notifyer.new_alert(bheem.alert, new_message)
                # update trade
                if user["autotrade_enabled"] and bheem.check_alert_action():
                    try:
                        bybit = Bybit(user)
                    except Exception as e:
                        util.error(f'can\'t connect to bybit api, user: *{user["name"]}*', finish=False)
                        continue
                    bybit.set_alert_data(bheem.alert)
                    report = bybit.update_trade()
                    if bybit.api_error_flag:
                        util.error(f'Error: {bybit.api_error_msg}', finish=False)
                        continue
                    notifyer.alert_report(report)
            else:
                notifyer.broken_message(new_message)


def check_trades():
    """Check new trades and make trade"""
    #all_messages = client.fetch_messages(config.bheem_channels["trades"])
    #new_message = util.check_new_message(all_messages, config.files_list['bheem_trades'])
    new_message = ''' RNDR - Long (0.5R)
Entry: 3.9650
SL: 3.740
TP: 4.3873

<@&1202381806989754378>'''
    if new_message:
        bheem = BheemParser()
        bheem.parse_trade_message_data(new_message.strip())
        for user in config.users.values():
            notifyer = Notifyer(user["tg_chat_id"])

            if bheem.check_trade_data():
                # check sl in trade
                if not bheem.trade["sl"]:
                    util.save_lost_sl_trade(bheem.trade)
                    notifyer.lost_sl(bheem.trade, new_message)
                    continue
                # notify in tg about new message
                notifyer.new_trade(bheem.trade, new_message)
                # make trade if this user enable autotrade
                if user["autotrade_enabled"]:
                    try:
                        bybit = Bybit(user)
                    except Exception as e:
                        util.error(f'can\'t connect to bybit api, user: *{user["name"]}*', finish=False)
                        continue
                    bybit.set_trade_data(bheem.trade)
                    bybit.make_trade()
                    if bybit.api_error_flag:
                        util.error(f'Error: {bybit.api_error_msg}', finish=False)
                        continue
                    for order in bybit.orders:
                        notifyer.place_order(order)
            else:
                notifyer.broken_message(new_message)


def check_rekt_updates():
    all_messages = client.fetch_messages(config.rekt_channels["trades"])
    new_message = util.check_new_message(all_messages, config.files_list['rekt_trades'])
    if new_message:
        new_message = '*REKT:*\n' + new_message
        for user in config.users.values():
            notifyer = Notifyer(user["tg_chat_id"])
            notifyer.send_message(new_message)


def check_lost_sl_trades():
    """Fetch saved trades and check bheem active branch"""
    saved_trades = json.loads(util.get_content_file(config.files_list['lost_sl_trades']).strip())
    message_active = client.fetch_messages(config.bheem_channels["active"])[0]["content"].lower()
    new_saved_trades = []
    util.set_content_file(config.files_list['lost_sl_trades'], json.dumps(new_saved_trades))
    for trade in saved_trades:
        order = BheemParser.find_trade_data_in_limit(trade['pair'], message_active)
        if not order:
            new_saved_trades.append(trade)
            util.set_content_file(config.files_list['lost_sl_trades'], json.dumps(new_saved_trades))
            continue
        bheem = BheemParser()
        bheem.parse_trade_message_data(order)
        bheem.trade['entry'] = trade['entry']
        for user in config.users.values():
            notifyer = Notifyer(user["tg_chat_id"])

            if bheem.check_trade_data():
                # check sl in trade
                if not bheem.trade["sl"]:
                    util.save_lost_sl_trade(bheem.trade)
                    notifyer.lost_sl(bheem.trade, order)
                    continue
                # notify in tg about new message
                notifyer.new_saved_trade(bheem.trade, order)
                # make trade if this user enable autotrade
                if user["autotrade_enabled"]:
                    try:
                        bybit = Bybit(user)
                    except Exception as e:
                        util.error(f'can\'t connect to bybit api, user: *{user["name"]}*', finish=False)
                        continue
                    bybit.set_trade_data(bheem.trade)
                    bybit.make_trade()
                    if bybit.api_error_flag:
                        util.error(f'Error: {bybit.api_error_msg}', finish=False)
                        continue
                    for order in bybit.orders:
                        notifyer.place_order(order)
            else:
                notifyer.broken_message(order)
    # save new trades
    util.set_content_file(config.files_list['lost_sl_trades'], json.dumps(new_saved_trades))


client = DiscordClient(config.discord_token)
# bheem alerts section
check_alert()
# bheem trade section
check_trades()
# rekt trades section
check_rekt_updates()
# check lost sl trades
check_lost_sl_trades()
