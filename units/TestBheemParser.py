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
        self.assertEqual(self.parser.trade["pair"],"eth")
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

    def test_parse_alert_message_data(self):
        new_message = "ICP SL BE (11.683) <@&1202381848127479828>"
        self.parser.parse_alert_message_data(new_message)
        self.assertEqual(self.parser.alert["pair"], 'icp')
        self.assertEqual(self.parser.alert["action"], 'move_sl')
        self.assertEqual(self.parser.alert["value"], 'be')


if __name__ == '__main__':
    unittest.main()
