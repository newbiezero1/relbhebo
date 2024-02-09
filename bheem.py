"""Parser bheem message"""


class BheemParser:
    def __init__(self):
        self.trade = {
            'pair': '',
            'side': '',
            'entry': [],
            'sl': '',
            'tp': '',
            'risk': 0.5,
        }
        self.alert = {
            'pair': '',
            'action': '',
            'value': '',
        }
        self.alert_action_ignore = ['filled', 'stopped', 'update']
        self.alert_action = ['move_sl', 'close', 'cancel']
        return

    def find_risk(self, line: str) -> None:
        """Find the risk for trade"""
        """example: ARKM - Short (0.25R)"""
        if line.lower().find('0.25r') >= 0:
            self.trade['risk'] = 0.25
        elif line.lower().find('0.5r') >= 0:
            self.trade['risk'] = 0.5

    def find_pair(self, line: str) -> None:
        """find pair in line and save to data"""
        """example: **ETH/SPOT - LONG**"""
        """example: RNDR - Long (0.5R)"""
        if line.lower().find("spot") > 0 or line.lower().find("perp") > 0:
            data = line.split("/")
            self.trade["pair"] = data[0].replace('*', '').lower()
            return
        if line.lower().find('- long'):
            data = line.split(" ")
            self.trade["pair"] = data[0].lower()

    def find_side(self, line: str) -> None:
        """find side in line and save to data"""
        """example: **ETH/SPOT - LONG**"""
        if line.lower().find("long") > 0:
            self.trade["side"] = "long"
        elif line.lower().find("short") > 0:
            self.trade["side"] = "short"
        elif line.lower().find("limit") > 0:
            # recognize by potential sl level
            if line.lower().find("close below"):
                self.trade["side"] = "long"

    def format_entry(self, entry: str) -> list:
        """format list entry point"""
        if entry.find("/"):
            return entry.split("/")
        if entry == 'cmp':
            return ['cmp']
        return []

    def find_entry(self, line: str) -> None:
        """find entry point in line and save to data"""
        """example: Entry: 2052.32/1985.78"""
        if line.lower().find("entry") >= 0:
            data = line.lower().split("entry: ")
            self.trade["entry"] = self.format_entry(data[1].strip())
            return

    def find_sl(self, line: str) -> None:
        """find sl point in line and save to data"""
        """example: SL: 1903.99 | SSL: H1 1.393"""
        if line.lower().find("ssl:") >= 0:
            if line.lower().find("close below ") >= 0:
                data = line.lower().split("close below ")
                self.trade["sl"] = data[1].split(" ")[0].strip()
                return
            if line.lower().find("ssl: h") >= 0:
                data = line.split(" ")
                self.trade["sl"] = data[-1]
                if self.trade["sl"].lower().find("h") >= 0:
                    self.trade["sl"] = ''
                return
        if line.lower().find("sl") >= 0:
            data = line.lower().split("sl: ")
            self.trade["sl"] = data[1].split(" ")[0].strip()
            return

    def find_tp(self, line: str) -> None:
        """find tp point in line and save to data"""
        """example: TP: 2415.2"""
        if line.lower().find("tp") >= 0:
            data = line.lower().split("tp: ")
            self.trade["tp"] = data[1].strip()
            return

    def find_in_many_line(self, lines: list) -> None:
        """find any needes in many line and save to data"""
        """ message example
                **ETH/SPOT - LONG**
                Entry: 2052.32/1985.78
                SL: 1903.99
                TP: 2415.2
                <@&1202381806989754378>"""
        for line in lines:
            self.find_risk(line)
            if not self.trade['pair']:
                self.find_pair(line)
            if not self.trade['side']:
                self.find_side(line)
            if not self.trade['entry']:
                self.find_entry(line)
            if not self.trade['sl']:
                self.find_sl(line)
            if not self.trade['tp']:
                self.find_tp(line)

    def find_in_one_line(self, line: str) -> None:
        """find any needes in one line and save to data"""
        """ message example SUI long CMP/1.45 SL: 1.4275 <@&1202381806989754378>"""
        data = line.split(" ")
        # start find pair
        # if first word cmp high syntax and origin maybe this pair name
        if data[0].isupper():
            self.trade['pair'] = data[0].lower()

        # start find side
        self.find_side(line)

        # start find entry
        for part in data:
            # entry point can be separated by /
            if part.find("/") >= 0:
                self.trade['entry'] = self.format_entry(part)
            # entry point can be just CMP
            if part.lower().find("cmp") >= 0:
                self.trade['entry'] = self.format_entry(part.lower())

        # start find sl
        self.find_sl(line)
        return

    def parse_alert_message_data(self, message: str) -> dict:
        """parse bheem alerts message"""
        message = message.strip()
        data = message.split(" ")
        # first find pair else broken alert
        if data[0].isupper():
            # pair maybe first and upper
            self.alert["pair"] = data[0].lower().strip(":")
        elif message.lower().find("for") >= 0:
            # maybe 'close for BTC'
            self.alert['pair'] = data[data.index('for')+1]
        else:
            # cant recognize pair
            return self.alert
        # value is other
        self.alert['value'] = data[2].lower()
        # action must be second
        self.alert["action"] = data[1].lower().replace(',', '')
        if message.lower().find("sl") >= 0:
            if message.lower().find("sl updated to h") >= 0:
                self.alert["action"] = 'update'
            elif message.lower().find("once it touch") >= 0:
                self.alert['action'] = 'update'
            else:
                self.alert["action"] = "move_sl"
            self.alert["value"] = "be"
        elif message.lower().find("closed") >= 0 or message.lower().find("booked") >= 0:
            self.alert["action"] = "close"
            self.alert["value"] = "be"
        elif message.lower().find("cancelled") >= 0 or message.lower().find("canceled") >= 0:
            self.alert["action"] = "cancel"
        return self.alert

    def parse_trade_message_data(self, message: str) -> dict:
        """parse bheem message"""
        # remove server tag
        message = message.replace('<@&1202381806989754378>','').strip()
        lines = message.split("\n")
        if len(lines) == 1:
            # one line message
            self.find_in_one_line(lines[0])
        else:
            # many line message
            self.find_in_many_line(lines)

        return self.trade

    def check_trade_data(self) -> bool:
        """"Check all required params"""
        if not self.trade['pair']:
            return False
        if not self.trade['side']:
            return False
        if not self.trade['entry']:
            return False
        return True

    def check_alert_data(self) -> bool:
        """Check all action i know"""
        if self.alert["action"] in self.alert_action_ignore or self.alert["action"] in self.alert_action:
            return True
        else:
            return False

    def check_alert_action(self) -> bool:
        """Check currecnt action for continue work"""
        if self.alert["action"] in self.alert_action:
            return True
        return False

    @staticmethod
    def find_trade_data_in_limit(pair: str, entries: list, message: str) -> str:
        """find needed pair in limit orders section and return SL and TP"""
        limit_section = message.split('limit orders')
        limit_orders = limit_section[1].split("\n\n")
        for order in limit_orders:
            if order.find(pair + "/") >= 0:
                current_order = False
                for entry in entries:
                    if order.find(str(entry)) >= 0:
                        current_order = True
                if not current_order:
                    continue
                order = order.replace('entry :', 'entry:')
                order = order.replace('sl :', 'sl:')
                order = order.replace('tp :', 'tp:')
                return order
        return ''
