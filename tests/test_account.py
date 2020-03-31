from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock
from accounts.accounts import Account, OperationFactory, Operation


class FirstOperation(Operation):
    KEY = 'first'
    rules = []
    def __init__(self, a):
        super().__init__()
        self.a = a

class SecondOperation(Operation):
    KEY = 'second'
    rules = []
    def __init__(self, b):
        super().__init__()
        self.b = b


def first_rule(x):
    if x.a < 0:
        return 'flag1'

def second_rule(x):
    if x.b < 0:
        return 'flag2'

third_rule = Mock(return_value='flag3')


class OperationTestCase(TestCase):
    def setUp(self):
        self._original_operations = OperationFactory.operations
        OperationFactory.operations = [FirstOperation, SecondOperation]
        FirstOperation.rules = [first_rule]
        SecondOperation.rules = [second_rule]

    def tearDown(self):
        OperationFactory.operations = self._original_operations

    def test_get_instance(self):
        x = OperationFactory.get_instance({'first': {'a': 1}})
        self.assertIsInstance(x, FirstOperation)
        self.assertEqual(x.a, 1)
        x = OperationFactory.get_instance({'second': {'b': 2}})
        self.assertIsInstance(x, SecondOperation)
        self.assertEqual(x.b, 2)

        x = OperationFactory.get_instance({'something_else': {'c': 3}})
        self.assertIsNone(x)

    def test_add(self):
        @OperationFactory.add
        class ThirdOperation():
            KEY = 'third'

        class FourthOperation():
            KEY = 'fourth'

        self.assertIs(OperationFactory.operations[-1], ThirdOperation)
        x = OperationFactory.add(FourthOperation)
        self.assertIs(OperationFactory.operations[-1], FourthOperation)
        self.assertIs(x, FourthOperation)

    def test_parse(self):
        x = Operation.parse('')
        self.assertIsNone(x)
        x = Operation.parse('{"first": {"a": 1}}')
        self.assertIsInstance(x, FirstOperation)
        self.assertEqual(x.a, 1)
        self.assertEqual(x.violations, [])
        x = Operation.parse('{"second": {"b": -2}}')
        self.assertIsInstance(x, SecondOperation)
        self.assertEqual(x.violations, ['flag2'])
        x = Operation.parse('{"something_else": {"c": 3}}')
        self.assertIsNone(x)

    def test_rule(self):
        x = FirstOperation.rule(third_rule)
        self.assertIs(third_rule, FirstOperation.rules[-1])
        self.assertIs(third_rule, x)

    def test_execute_rules(self):
        x = FirstOperation.rule(third_rule)
        operation = FirstOperation(a=1)
        self.assertEqual(operation.execute_rules(), ['flag3'])
        operation = FirstOperation(a=-1)
        self.assertEqual(operation.execute_rules(), ['flag1', 'flag3'])
        self.assertIs(operation.run(), operation)
        self.assertEqual(operation.violations, ['flag1', 'flag3'])

    def test_to_json(self):
        operation = FirstOperation(a=-1)
        operation.run()
        js = operation.to_json()
        self.assertEqual(js, {'account': {}, 'violations': ['flag1']})
        operation.account = Account()
        js = operation.to_json()
        self.assertEqual(js, {'account': {'activeCard': False, 'availableLimit': 0}, 'violations': ['flag1']})

    def test_apply_transaction(self):
        # test for OK: 100-40=60
        transaction = Mock(amount=40, violations=[])
        account = Account(available_limit=100)
        account.apply_transaction(transaction)
        self.assertEqual(account.transactions, [transaction])
        self.assertEqual(account.available_limit, 60)
        # test for violation: 60-40=60
        transaction2 = Mock(amount=40, violations=['flag1'])
        account.apply_transaction(transaction2)
        self.assertEqual(account.transactions, [transaction, transaction2])
        self.assertEqual(account.available_limit, 60)

