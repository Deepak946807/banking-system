"""
Unit tests for the Banking System.
Run with: python -m unittest discover tests
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bank import (
    SavingsAccount, CurrentAccount,
    InsufficientFundsError, InvalidAmountError, OverdraftLimitExceededError,
    AuthenticationError, WeakPinError,
)


class TestSavingsAccount(unittest.TestCase):
    def setUp(self):
        self.acc = SavingsAccount("MTBK-1001", "Rahul Sharma", balance=1000, pin="1234")

    def test_deposit(self):
        self.acc.deposit(500)
        self.assertEqual(self.acc.balance, 1500)

    def test_withdraw_success(self):
        self.acc.withdraw(400)
        self.assertEqual(self.acc.balance, 600)

    def test_withdraw_insufficient_funds(self):
        with self.assertRaises(InsufficientFundsError):
            self.acc.withdraw(5000)

    def test_negative_deposit_raises(self):
        with self.assertRaises(InvalidAmountError):
            self.acc.deposit(-100)

    def test_interest_applied(self):
        interest = self.acc.apply_interest()
        self.assertAlmostEqual(self.acc.balance, 1000 + interest)

    def test_correct_pin_verifies(self):
        self.assertTrue(self.acc.verify_pin("1234"))

    def test_wrong_pin_fails(self):
        self.assertFalse(self.acc.verify_pin("9999"))

    def test_require_pin_raises_on_wrong_pin(self):
        with self.assertRaises(AuthenticationError):
            self.acc.require_pin("0000")

    def test_weak_pin_rejected(self):
        with self.assertRaises(WeakPinError):
            self.acc.set_pin("12")  # not 4 digits


class TestCurrentAccount(unittest.TestCase):
    def setUp(self):
        self.acc = CurrentAccount("MTBK-2001", "Priya Verma", balance=1000, overdraft_limit=2000, pin="4321")

    def test_withdraw_within_overdraft(self):
        self.acc.withdraw(2500)  # 1000 balance + up to 2000 overdraft allowed
        self.assertEqual(self.acc.balance, -1500)

    def test_withdraw_exceeds_overdraft(self):
        with self.assertRaises(OverdraftLimitExceededError):
            self.acc.withdraw(3500)


if __name__ == "__main__":
    unittest.main()
