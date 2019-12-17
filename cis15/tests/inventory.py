import unittest
import pexpect
import logging
import sys

from . import Project

class Inventory(Project):

    def __init__(self, *args):
        super().__init__('inventory.py', *args)

    def setUp(self):
        self.cmdline = f'python3.6 "{self.find_file()}"'
        with open('test_inventory.csv', 'w') as f:
            f.write(f"""A, 100.00, 100\n""")
            f.write(f"""B, 200.00, 200\n""")
            f.write(f"""C, 300.00, 300\n""")

    def test_11_load_inventory(self):

        self.banner("Testing the load and balance commands.")
        with open('inventory_test.out', 'w') as log:
            test = pexpect.spawnu(self.cmdline, logfile=log, echo=False, timeout=1)

            test.sendline('load test_inventory.csv')
            test.sendline('list')
            if 2 > test.expect([pexpect.EOF, pexpect.TIMEOUT, 'A.*100.*100']):
                self.fail("""I don't see your the loaded inventory.""")
            test.sendline('balance')
            if test.expect([pexpect.EOF, pexpect.TIMEOUT, '0']):
                self.fail("""Your balance didn't start at 0.""")

            test.close()


    def test_12_sell_inventory(self):

        self.banner("Testing the sell command.")
        with open('inventory_test.out', 'a') as log:
            test = pexpect.spawnu(self.cmdline, logfile=log, echo=False, timeout=1)

            test.sendline('load test_inventory.csv')
            test.sendline('sell A 50')
            test.sendline('list')
            test.expect('A.*100.*50')
            test.sendline('balance')
            test.expect('5000')

            test.sendline('quit')
            test.close()

    def test_13_sell_too_much(self):

        self.banner("Testing what happens when I sell too much.")
        with open('inventory_test.out', 'a') as log:
            test = pexpect.spawnu(self.cmdline, logfile=log, echo=False, timeout=1)

            test.sendline('load test_inventory.csv')
            test.sendline('sell A 500')
            test.sendline('list')
            test.expect('A.*100.*100')
            test.sendline('balance')
            test.expect('0')

            test.sendline('quit')
            test.close()

    def test_14_buy_inventory(self):

        self.banner("Testing the buy command.")
        with open('inventory_test.out', 'a') as log:
            test = pexpect.spawnu(self.cmdline, logfile=log, echo=False, timeout=1)

            test.sendline('load test_inventory.csv')
            test.sendline('sell A 50')
            test.sendline('buy B 10')
            test.sendline('list')
            test.expect('B.*200.*210')
            test.sendline('balance')
            test.expect('3000')

            test.sendline('quit')
            test.close()

    def test_15_buy_too_much(self):

        self.banner("Testing what happens when I buy too much.")
        with open('inventory_test.out', 'a') as log:
            test = pexpect.spawnu(self.cmdline, logfile=log, echo=False, timeout=1)

            test.sendline('load test_inventory.csv')
            test.sendline('sell A 50')
            test.sendline('buy B 100')
            test.sendline('list')
            test.expect('B.*200.*200')
            test.sendline('balance')
            test.expect('5000')

            test.sendline('quit')
            test.close()


if __name__ == '__main__':
    unittest.main(verbosity=0, exit=False)
