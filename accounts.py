import datetime
import json


class OperationFactory():
    operations = []

    @classmethod
    def add(cls, op_class):
        cls.operations.append(op_class)
        return op_class

    @classmethod
    def get_instance(self, js):
        for op in self.operations:
            if op.KEY in js:
                return op(**js[op.KEY]).run()
        return None


class Operation():
    KEY = None
    _rules = []

    @classmethod
    def parse(self, text):
        if not text:
            return None
        js = json.loads(text)
        instance = OperationFactory.get_instance(js)
        return instance and instance.run() or ''

    @classmethod
    def rule(cls, function):
        cls._rules.append(function)
        return function

    def execute_rules(self):
        violations = []
        for rule in self._rules:
            error = rule(self)
            if error:
                violations.append(error)
        return violations

    def to_json(self):
        return {
            'account': self.account and self.account.to_json() or {},
            'violations': self.violations,
        }

    def __str__(self):
        return json.dumps(self.to_json())


@OperationFactory.add
class AccountCreation(Operation):
    KEY = 'account'
    _rules = []

    def __init__(self, activeCard, availableLimit):
        self.active_card = activeCard
        self.available_limit = availableLimit
        self.account = None
        self.violations = []

    def run(self):
        self.violations = self.execute_rules()
        if not Account.account:
            Account.account = Account(self.active_card, self.available_limit)
        self.account = Account.account
        return self


@OperationFactory.add
class Transaction(Operation):
    KEY = 'transaction'
    _rules = []
    DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

    def __init__(self, merchant, amount, time):
        self.merchant = merchant
        self.amount = amount
        self.time = datetime.datetime.strptime(time, self.DATE_FORMAT)
        self.account = Account.account
        self.violations = []

    def run(self):
        print(111)
        self.violations = self.execute_rules()
        if self.account:
            print(222)
            self.account.apply_transaction(self)
        return self


class Account():
    account = None

    def __init__(self, active_card, available_limit):
        self.active_card = active_card
        self.available_limit = available_limit
        self.transactions = []

    def to_json(self):
        return {
            "activeCard": self.active_card,
            "availableLimit": self.available_limit,
        }

    def apply_transaction(self, transaction):
        self.transactions.append(transaction)
        if not transaction.violations:
            self.available_limit -=  transaction.amount


def with_account(rule):
    "decorator: executes the function only if there is an account"
    def rule_with_account(operation):
        if operation.account:
            return rule(operation)
    return rule_with_account

