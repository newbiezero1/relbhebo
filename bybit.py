"""Module for work with bybit"""
from pybit.unified_trading import HTTP

import util


class Bybit:
    """Class for work with bybit"""

    def __init__(self, user):
        self.user_name = user["name"]
        self.risk_percent = user["trade_risk_in_proc"]
        self.session = HTTP(api_key=user["bybit_api_key"], api_secret=user["bybit_api_secret"])
        self.api_error_flag = False
        self.balance = self.get_balance()

        # trade data
        self.trade = {}
        self.current_price = 0.0
        self.orders = []

    def get_balance(self) -> float:
        """Get USDT balance"""
        wallet_balance = self.session.get_wallet_balance(accountType="CONTRACT", coin="USDT")
        if wallet_balance["retCode"] != 0:
            self.api_error_flag = True
            util.error(f'Error retrieving wallet, user: {self.user_name}', finish=False)
            return 0
        balance = float(wallet_balance["result"]["list"][0]["coin"][0]["walletBalance"])
        return balance

    def get_current_price(self) -> None:
        """Get symbol current price"""
        data = self.session.get_mark_price_kline(symbol=self.trade["pair"], category="linear", interval=1, limit=1)
        if data["retCode"] != 0:
            util.error(f'Cant receive market data: *{self.trade["pair"]}*')
        self.current_price = float(data["result"]["list"][0][4])

    def format_big_value_to_real(self, value: float) -> float:
        """Format value as 5100 as 0.05100 if price 0.078"""
        diff = (1 / self.current_price)
        index = 1
        if diff < 10:
            index = 10
        elif diff > 10 and diff < 100:
            index = 10
        elif diff > 100 and diff < 1000:
            index = 100
        return value / (index * 1000)

    def set_trade_data(self, trade: dict) -> None:
        """Convert data from message to float format and pair spec and convert values"""
        # format pair
        self.trade["pair"] = trade["pair"].upper() + "USDT"
        if trade["side"] == "long":
            self.trade["side"] = "Buy"
        else:
            self.trade["side"] = "Sell"
        # request market price
        self.get_current_price()

        # formate entry
        self.trade["entry"] = []
        for entry in trade["entry"]:
            if entry == "cmp":
                self.trade["entry"].append("cmp")
                continue
            if self.current_price < 1 and float(entry) > 1:
                # need check msg price
                entry = self.format_big_value_to_real(float(entry))
                self.trade["entry"].append(entry)
                continue
            self.trade["entry"].append(float(entry))

        # formate sl
        if self.current_price < 1 and float(trade["sl"]):
            # need format sl to real data
            self.trade["sl"] = self.format_big_value_to_real(float(trade["sl"]))
        else:
            self.trade["sl"] = float(trade["sl"])

        # formate tp
        self.trade["tp"] = None
        if trade["tp"] and trade["tp"] != "tbd":
            if self.current_price < 1 and float(trade["tp"]):
                # need format sl to real data
                self.trade["tp"] = self.format_big_value_to_real(float(trade["tp"]))
            else:
                self.trade["tp"] = float(trade["tp"])

    def get_round_index(self, price: float) -> int:
        """round params for round qty by price"""
        round_index = 2
        if price < 10:
            round_index = 0
        if price > 10:
            round_index = 1
        if price > 1000:
            round_index = 2
        if price > 10000:
            round_index = 3
        return round_index

    def place_market_order(self, sl_size: float) -> dict:
        """Send market order"""
        amount_usdt = (self.balance * self.current_price * sl_size) / (self.current_price - self.trade["sl"])
        order = {"symbol": self.trade["pair"], "side": self.trade["side"], "orderType": "Market"}
        round_index = self.get_round_index(self.current_price)
        order["qty"] = round(amount_usdt / self.current_price, round_index)
        order["stopLoss"] = self.trade["sl"]
        order["takeProfit"] = 0
        if self.trade["tp"] and self.trade["tp"] != "tbd":
            order["takeProfit"] = self.trade["tp"]
        try:
            result = self.session.place_order(category="linear",
                                              symbol=order["symbol"],
                                              side=order["side"],
                                              orderType=order["orderType"],
                                              qty=order["qty"],
                                              stopLoss=order["stopLoss"],
                                              takeProfit=order["takeProfit"])
        except Exception as e:
            util.error(f'Error place order: {e}')
        if result["retCode"] != 0:
            util.error(f'Warning place order: {result["retMsg"]}', finish=False)
        order["result"] = result["retMsg"]
        order["orderId"] = result["result"]["orderId"]
        order["current_price"] = self.current_price
        order["price"] = "market"
        return order

    def place_limit_order(self, entry: float, sl_size: float) -> dict:
        """Send limit order"""
        amount_usdt = (self.balance * entry * sl_size) / (entry - self.trade["sl"])
        order = {"symbol": self.trade["pair"], "side": self.trade["side"], "orderType": "Limit"}

        round_index = self.get_round_index(entry)
        order["qty"] = round(amount_usdt / entry, round_index)
        order["price"] = entry
        order["stopLoss"] = self.trade["sl"]
        order["takeProfit"] = 0
        if self.trade["tp"] and self.trade["tp"] != "tbd":
            order["takeProfit"] = self.trade["tp"]
        try:
            result = self.session.place_order(category="linear",
                                              symbol=order["symbol"],
                                              side=order["side"],
                                              orderType=order["orderType"],
                                              qty=order["qty"],
                                              price=entry,
                                              stopLoss=order["stopLoss"],
                                              takeProfit=order["takeProfit"])
        except Exception as e:
            util.error(f'Error place order: {e}')
        if result["retCode"] != 0:
            util.error(f'Warning place order: {result["retMsg"]}', finish=False)
        order["result"] = result["retMsg"]
        order["orderId"] = result["result"]["orderId"]
        order["current_price"] = self.current_price
        return order

    def make_trade(self) -> None:
        """Make a trade"""
        # calculate sl per entry
        sl_percent = self.risk_percent / len(self.trade["entry"])
        for entry in self.trade["entry"]:
            if str(entry) == "cmp":
                order = self.place_market_order(sl_percent)
                self.orders.append(order)
            else:
                order = self.place_limit_order(entry, sl_percent)
                self.orders.append(order)
