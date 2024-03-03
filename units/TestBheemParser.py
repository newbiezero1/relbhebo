import unittest
from bheem import BheemParser


class TestBheemParser(unittest.TestCase):
    def setUp(self):
        self.parser = BheemParser()

    def test_find_pair(self):
        self.parser.find_pair("**ETH/SPOT - LONG**")
        self.assertEqual(self.parser.trade["pair"], "eth")

    def test_find_side(self):
        self.parser.find_side("**ETH/SPOT - LONG**")
        self.assertEqual(self.parser.trade["side"], "long")

    def test_find_entry_with_slash(self):
        self.parser.find_entry("Entry: 2052.32/1985.78")
        self.assertEqual(self.parser.trade["entry"], ["2052.32", "1985.78"])

    def test_find_entry_with_cmp(self):
        self.parser.find_entry("Entry: CMP")
        self.assertEqual(self.parser.trade["entry"], ["cmp"])

    def test_find_sl(self):
        self.parser.find_sl("SL: 1903.99")
        self.assertEqual(self.parser.trade["sl"], "1903.99")

    def test_find_tp(self):
        self.parser.find_tp("TP: 2415.2")
        self.assertEqual(self.parser.trade["tp"], "2415.2")

    def test_find_in_many_line(self):
        message = "**ETH/SPOT - LONG**\nEntry: 2052.32/1985.78\nSL: 1903.9\nTP: 2415.2\n"
        self.parser.find_in_many_line(message.split("\n"))
        self.assertEqual(self.parser.trade["pair"], "eth")
        self.assertEqual(self.parser.trade["side"], "long")
        self.assertEqual(self.parser.trade["entry"], ["2052.32", "1985.78"])
        self.assertEqual(self.parser.trade["sl"], "1903.9")
        self.assertEqual(self.parser.trade["tp"], "2415.2")

    def test_find_in_one_line(self):
        message = "SUI long CMP/1.45 SL: 1.4275 <@&1202381806989754378>"
        self.parser.find_in_one_line(message)
        self.assertEqual(self.parser.trade["pair"], "sui")
        self.assertEqual(self.parser.trade["side"], "long")
        self.assertEqual(self.parser.trade["entry"], ["cmp", "1.45"])
        self.assertEqual(self.parser.trade["sl"], "1.4275")
        self.assertEqual(self.parser.trade["tp"], "")

    def test_parse_message_many_lines_standart(self):
        new_messages = '''ETH/SPOT - LONG
        Entry: 2052.32/1985.78
        SL: 1903.99
        TP: 2415.2'''
        self.parser.parse_trade_message_data(new_messages)
        self.assertEqual(self.parser.trade["pair"], 'eth')
        self.assertEqual(self.parser.trade["side"], 'long')
        self.assertEqual(self.parser.trade["entry"], ['2052.32', '1985.78'])
        self.assertEqual(self.parser.trade["sl"], '1903.99')
        self.assertEqual(self.parser.trade["tp"], '2415.2')

    def test_parse_message_many_lines_with_entry_cpm(self):
        new_messages = '''ETH/SPOT - LONG
                Entry: CMP
                SL: 1903.99
                TP: 2415.2'''
        self.parser.parse_trade_message_data(new_messages)
        self.assertEqual(self.parser.trade["pair"], 'eth')
        self.assertEqual(self.parser.trade["side"], 'long')
        self.assertEqual(self.parser.trade["entry"], ['cmp'])
        self.assertEqual(self.parser.trade["sl"], '1903.99')
        self.assertEqual(self.parser.trade["tp"], '2415.2')

    def test_parse_message_one_line(self):
        new_messages = '''SUI long CMP/1.45 SL: 1.4275 <@&1202381806989754378>'''
        self.parser.parse_trade_message_data(new_messages)
        self.assertEqual(self.parser.trade["pair"], 'sui')
        self.assertEqual(self.parser.trade["side"], 'long')
        self.assertEqual(self.parser.trade["entry"], ['cmp', '1.45'])
        self.assertEqual(self.parser.trade["sl"], '1.4275')

    def test_parse_message_one_line_with_ssl(self):
        new_messages = '''LINK limit 17.382/17.011 SSL: H4 close below 16.696 <@&1202381806989754378>'''
        self.parser.parse_trade_message_data(new_messages)
        self.assertEqual(self.parser.trade["pair"], 'link')
        self.assertEqual(self.parser.trade["side"], 'long')
        self.assertEqual(self.parser.trade["entry"], ['17.382', '17.011'])
        self.assertEqual(self.parser.trade["sl"], '16.696')

    def test_parse_message_many_lines_with_ssl(self):
        new_messages = '''SUI/SPOT - LONG
            Entry: 1.422/1.410
            SSL: H1 1.393
            TP: TBD
            <@&1202381806989754378>'''
        self.parser.parse_trade_message_data(new_messages)
        self.assertEqual(self.parser.trade["pair"], 'sui')
        self.assertEqual(self.parser.trade["side"], 'long')
        self.assertEqual(self.parser.trade["entry"], ['1.422', '1.410'])
        self.assertEqual(self.parser.trade["sl"], '1.393')
        self.assertEqual(self.parser.trade["tp"], 'tbd')

    def test_parse_message_many_lines_with_ssl_m15(self):
        new_messages = '''**BTC/SPOT - LONG**
            
            Entry: 47751/47557
            SSL: m15 47454
            TP: 51936'''
        self.parser.parse_trade_message_data(new_messages)
        self.assertEqual(self.parser.trade["pair"], 'btc')
        self.assertEqual(self.parser.trade["side"], 'long')
        self.assertEqual(self.parser.trade["entry"], ['47751', '47557'])
        self.assertEqual(self.parser.trade["sl"], '47454')
        self.assertEqual(self.parser.trade["tp"], '51936')

    def test_parse_alert_message_data(self):
        new_message = "ICP SL BE (11.683) <@&1202381848127479828>"
        self.parser.parse_alert_message_data(new_message)
        self.assertEqual(self.parser.alert["pair"], 'icp')
        self.assertEqual(self.parser.alert["action"], 'move_sl')
        self.assertEqual(self.parser.alert["value"], 'be')

    def test_parse_alert_message_when_pair_second(self):
        new_message = "Cancel RNDR Long @RAMI ALERT"
        self.parser.parse_alert_message_data(new_message)
        self.assertEqual(self.parser.alert["pair"], 'rndr')
        self.assertEqual(self.parser.alert["action"], 'cancel')

    def test_parse_alert_message_cancel(self):
        new_message = "WIF cancelled @BHEEM ALERT"
        self.parser.parse_alert_message_data(new_message)
        self.assertEqual(self.parser.alert["pair"], 'wif')
        self.assertEqual(self.parser.alert["action"], 'cancel')

    def test_parse_alert_message_cancel_with_other_world(self):
        new_message = "SUI spot cancelled @BHEEM ALERTT"
        self.parser.parse_alert_message_data(new_message)
        self.assertEqual(self.parser.alert["pair"], 'sui')
        self.assertEqual(self.parser.alert["action"], 'cancel')

    def test_parse_alert_message_close(self):
        new_message = "SUI closed BE @BHEEM ALERTT"
        self.parser.parse_alert_message_data(new_message)
        self.assertEqual(self.parser.alert["pair"], 'sui')
        self.assertEqual(self.parser.alert["action"], 'close')

    def test_parse_alert_message_filled_with_close(self):
        new_message = "BTC filled 42440, closed at 42420"
        self.parser.parse_alert_message_data(new_message)
        self.assertEqual(self.parser.alert["pair"], 'btc')
        self.assertEqual(self.parser.alert["action"], 'close')

    def test_parse_alert_message_move_sl(self):
        new_message = "SUI: Filled ByBit, SL BE for those <@&1202381848127479828>"
        self.parser.parse_alert_message_data(new_message)
        self.assertEqual(self.parser.alert["pair"], 'sui')
        self.assertEqual(self.parser.alert["action"], 'move_sl')
        self.assertEqual(self.parser.alert["value"], 'be')

    def test_parse_alert_message_update_with_sl(self):
        new_message = "SEI: SL updated to H4 SSL @BHEEM ALERT"
        self.parser.parse_alert_message_data(new_message)
        self.assertEqual(self.parser.alert["pair"], 'sei')
        self.assertEqual(self.parser.alert["action"], 'update')

    def test_parse_alert_message_update_without_sl(self):
        new_message = "BLUR updated to H1 SSL <@&1202381848127479828>"
        self.parser.parse_alert_message_data(new_message)
        self.assertEqual(self.parser.alert["pair"], 'blur')
        self.assertEqual(self.parser.alert["action"], 'update')

    def test_parse_alert_message_update_back_without_sl(self):
        new_message = "ORDI updated back to HSL @BHEEM ALERT"
        self.parser.parse_alert_message_data(new_message)
        self.assertEqual(self.parser.alert["pair"], 'ordi')
        self.assertEqual(self.parser.alert["action"], 'update')

    def test_parse_alert_message_closed_with_booked(self):
        new_message = "Booked at 0.3274 for BIGTIME @RAMI ALERT"
        self.parser.parse_alert_message_data(new_message)
        self.assertEqual(self.parser.alert["pair"], 'BIGTIME')
        self.assertEqual(self.parser.alert["action"], 'close')

    def test_parse_alert_message_find_pair_in_for(self):
        new_message = "Booked at 0.3274 for BIGTIME @RAMI ALERT"
        self.parser.parse_alert_message_data(new_message)
        self.assertEqual(self.parser.alert["pair"], 'BIGTIME')

    def test_parse_alert_message_move_sl_with_coma_and_space(self):
        new_message = " JUP filled, SL BE <@&1202381848127479828>"
        self.parser.parse_alert_message_data(new_message)
        self.assertEqual(self.parser.alert["pair"], 'jup')
        self.assertEqual(self.parser.alert["action"], 'move_sl')

    def test_parse_message_ssl_without_point(self):
        new_message = "SEI limit 6561/6502 SSL: H4"
        self.parser.parse_trade_message_data(new_message)
        self.assertEqual(self.parser.trade["pair"], 'sei')
        self.assertEqual(self.parser.trade["sl"], '')

    def test_parse_message_find_r(self):
        new_messages = ''' RNDR - Long (0.25R)
        Entry: 3.9650
        SL: 3.740
        TP: 4.3873'''
        self.parser.parse_trade_message_data(new_messages)
        self.assertEqual(self.parser.trade["pair"], 'rndr')
        self.assertEqual(self.parser.trade["side"], 'long')
        self.assertEqual(self.parser.trade["entry"], ['3.9650'])
        self.assertEqual(self.parser.trade["sl"], '3.740')
        self.assertEqual(self.parser.trade["tp"], '4.3873')
        self.assertEqual(self.parser.trade['risk'], 0.25)

    def test_parse_message_find_r_oneline(self):
        new_messages = '''LINK long CMP/19.751 @TRADES (0.5R)'''
        self.parser.parse_trade_message_data(new_messages)
        self.assertEqual(self.parser.trade["pair"], 'link')
        self.assertEqual(self.parser.trade["side"], 'long')
        self.assertEqual(self.parser.trade["entry"], ['cmp', '19.751'])
        self.assertEqual(self.parser.trade['risk'], 0.5)

    def test_parse_message_find_sl_without_dot_online(self):
        new_messages = '''ORDI limit 82/78.47 SL 76 TP 106 @TRADES'''
        self.parser.parse_trade_message_data(new_messages)
        self.assertEqual(self.parser.trade["pair"], 'ordi')
        self.assertEqual(self.parser.trade["side"], 'long')
        self.assertEqual(self.parser.trade["entry"], ['82', '78.47'])
        self.assertEqual(self.parser.trade['sl'], '76')

if __name__ == '__main__':
    unittest.main()
