import unittest
from unittest.mock import Mock
from datetime import datetime
from accounts.accounts import AccountCreation, Transaction
from accounts import business_logic as bl


class BusinessLogicTestCase(unittest.TestCase):
    def setUp(self):
        self.account = Mock(
                active_card=True,
                available_limit=100,
                transactions=[],
        )
        self.account_creation = Mock(
                active_card=True,
                available_limit=100,
                account=None,
        )
        self.transaction = Mock(
                amount=40,
                account=self.account,
        )

    def test_account_already_initialized(self):
        # test for OK
        self.assertIsNone(bl.account_already_initialized(self.account_creation))
        # test for violation
        self.account_creation.account = self.account
        self.assertEqual(bl.account_already_initialized(self.account_creation), 'account-already-initialized')
        # check the rule has been added
        self.assertIn(bl.account_already_initialized, AccountCreation.rules)

    def test_account_not_initialized(self):
        # test for OK
        self.assertIsNone(bl.account_not_initialized(self.transaction))
        # test for violations
        self.transaction.account = None
        self.assertEqual(bl.account_not_initialized(self.transaction), 'account-does-not-exists')
        # check the rule has been added
        self.assertIn(bl.account_not_initialized, Transaction.rules)

    def test_insufficient_limit(self):
        # test for OK
        self.assertIsNone(bl.insufficient_limit(self.transaction))
        # test for violation
        self.account.available_limit = 20
        self.assertEqual(bl.insufficient_limit(self.transaction), 'insufficient-limit')
        # check the rule has been added
        self.assertIn(bl.insufficient_limit, Transaction.rules)

    def test_card_not_active(self):
        # test for OK
        self.assertIsNone(bl.card_not_active(self.transaction))
        # test for violation
        self.account.active_card = False
        self.assertEqual(bl.card_not_active(self.transaction), 'card-not-active')
        # check the rule has been added
        self.assertIn(bl.card_not_active, Transaction.rules)

    def test_high_frequency_small_interval(self):
        transaction = Mock(
            time=datetime(2020, 1, 1, 10, 30, 0), # 2020-01-01 T10:30:00
            account=self.account,
        )
        # test for OK
        # ... with no previous transactions
        self.assertIsNone(bl.high_frequency_small_interval(transaction))
        # ... with only one
        self.account.transactions.append(Mock(time=datetime(2020, 1, 1, 10, 0, 0)))
        self.assertIsNone(bl.high_frequency_small_interval(transaction))
        # ... with two old
        self.account.transactions.append(Mock(time=datetime(2020, 1, 1, 10, 20, 0)))
        self.assertIsNone(bl.high_frequency_small_interval(transaction))
        # ... with only one in the last minute
        self.account.transactions.append(Mock(time=datetime(2020, 1, 1, 10, 29, 0)))
        self.assertIsNone(bl.high_frequency_small_interval(transaction))
        # test for violation
        self.account.transactions.append(Mock(time=datetime(2020, 1, 1, 10, 29, 30)))
        self.assertEqual(bl.high_frequency_small_interval(transaction), 'high-frequency-small-interval')
        # check the rule has been added
        self.assertIn(bl.high_frequency_small_interval, Transaction.rules)

    def test_doubled_transaction(self):
        LOREM = 'Lorem Ipsum'
        DOLOR = 'dolor sit amet'
        transaction = Mock(
            merchant=LOREM,
            amount=40,
            time=datetime(2020, 1, 1, 10, 30, 0), # 2020-01-01 T10:30:00
            account=self.account,
        )
        # test for OK
        # ... with no previous transactions
        self.assertIsNone(bl.doubled_transaction(transaction))
        # ... with only one, but different
        self.account.transactions.append(Mock(merchant=DOLOR, amount=70, time=datetime(2020, 1, 1, 10, 20)))
        self.assertIsNone(bl.doubled_transaction(transaction))
        # ... with only same merchant
        self.account.transactions.append(Mock(merchant=LOREM, amount=70, time=datetime(2020, 1, 1, 10, 21)))
        self.assertIsNone(bl.doubled_transaction(transaction))
        # ... with only same amount
        self.account.transactions.append(Mock(merchant=DOLOR, amount=40, time=datetime(2020, 1, 1, 10, 22)))
        self.assertIsNone(bl.doubled_transaction(transaction))
        # ... same but old
        self.account.transactions.append(Mock(merchant=LOREM, amount=40, time=datetime(2020, 1, 1, 10, 23)))
        self.assertIsNone(bl.doubled_transaction(transaction))
        # test for violation
        self.account.transactions.append(Mock(merchant=LOREM, amount=40, time=datetime(2020, 1, 1, 10, 29)))
        self.assertEqual(bl.doubled_transaction(transaction), 'doubled-transaction')
        # check the rule has been added
        self.assertIn(bl.doubled_transaction, Transaction.rules)

    def test_decorator_with_account(self):
        # for 'with_account' decorator, check nothing happens when there is no account
        self.transaction.account = None
        self.assertIsNone(bl.insufficient_limit(self.transaction))
        self.assertIsNone(bl.card_not_active(self.transaction))
        self.assertIsNone(bl.high_frequency_small_interval(self.transaction))
        self.assertIsNone(bl.doubled_transaction(self.transaction))

