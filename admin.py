import sys

import config
from bybit import Bybit

cmd_list = ['Display positions', 'Display orders', 'Close positions', 'Close orders']

print('''Hi admin''')
print('''If u want exit enter Q any time\n''')
print('Select user:')
for key, user in config.users.items():
    print(key)

selected_user_key = input('Username: ')
if selected_user_key == 'Q':
    sys.exit()

selected_user = config.users[selected_user_key]
while True:
    print('Select command: ')
    for key, cmd in enumerate(cmd_list):
        print(f'{key}:\t*{cmd}*')

    cmd = input('Command: ')
    if cmd == 'Q':
        sys.exit()
    selected_cmd = cmd_list[int(cmd)]

    bybit = Bybit(selected_user)
    if selected_cmd == 'Display positions':
        positions = bybit.get_open_positions()
        print('POSITIONS:')
        for key,position in enumerate(positions):
            print(f'{key}:\t{position["symbol"]}\t PNL {position["unrealisedPnl"]}')
    elif selected_cmd == 'Display orders':
        orders = bybit.get_open_orders()
        print('ORDERS:')
        for key,order in enumerate(orders):
            print(f'{key}:\t {order["symbol"]}\t {order["price"]}')