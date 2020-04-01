import datetime
import json


class Account():
    " Saves the state of an account "
    account = None  # almost like a singleton

    def __init__(self, active_card=False, available_limit=0):
        self.active_card = active_card
        self.available_limit = available_limit
        self.transactions = []

    def to_json(self):
        " returns a dict to export as a json "
        return {
            "activeCard": self.active_card,
            "availableLimit": self.available_limit,
        }

    def apply_transaction(self, transaction):
        " saves the transaction and discounts the amount "
        self.transactions.append(transaction)
        if not transaction.violations:
            self.available_limit -=  transaction.amount


class OperationFactory():
    " Returns an instance of Operation "
    operations = []

    @classmethod
    def add(cls, op_class):
        " adds a new subclass to manage the instances. Works as decorator "
        cls.operations.append(op_class)
        return op_class

    @classmethod
    def get_instance(self, js):
        " Creates an instance of Operation subclasses, taking a json as reference "
        for op in self.operations:
            if op.KEY in js:
                return op(**js[op.KEY])
        return None


class Operation():
    " Abstract class for the different operations "
    KEY = None  # identifies the subclass for the factory. Overwrite on subclasses
    rules = []  # list of business rules. Overwrite on subclasses

    def __init__(self, **args):
        self.violations = []
        self.account = None

    @classmethod
    def parse(self, text):
        " Takes a text and transforms into an instance. Then checks for violations "
        if not text:
            return None
        js = json.loads(text)
        instance = OperationFactory.get_instance(js)
        return instance and instance.run()

    @classmethod
    def rule(cls, function):
        " adds a function as a business rule. Works as decorator "
        cls.rules.append(function)
        return function

    def run(self):
        " check for violations. Overwrite on subclasses when needed "
        self.violations = self.execute_rules()
        return self

    def execute_rules(self):
        " returns the violations to business rules "
        violations = []
        for rule in self.rules:
            error = rule(self)
            if error:
                violations.append(error)
        return violations

    def to_json(self):
        " returns a dict to export as a json "
        return {
            'account': self.account and self.account.to_json() or {},
            'violations': self.violations,
        }

    def __str__(self):
        " str(x) --> x.__str__() "
        return json.dumps(self.to_json())


@OperationFactory.add
class AccountCreation(Operation):
    " Operation for creating an account "
    KEY = 'account'
    rules = []

    def __init__(self, activeCard=False, availableLimit=0):
        self.active_card = activeCard
        self.available_limit = availableLimit
        self.account = Account.account
        self.violations = []

    def run(self):
        " check for violations and assign the account to the Account class "
        self.violations = self.execute_rules()
        if not self.account:
            self.account = Account.account = Account(self.active_card, self.available_limit)
        return self


@OperationFactory.add
class Transaction(Operation):
    KEY = 'transaction'
    rules = []
    DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

    def __init__(self, merchant='', amount=0, time=''):
        self.merchant = merchant
        self.amount = amount
        self.time = datetime.datetime.strptime(time, self.DATE_FORMAT)
        self.account = Account.account
        self.violations = []

    def run(self):
        " check for violations and applies the transaction "
        self.violations = self.execute_rules()
        if self.account:
            self.account.apply_transaction(self)
        return self


def with_account(rule):
    "decorator: executes the function only if there is an account"
    def rule_with_account(operation):
        if operation.account:
            return rule(operation)
    rule_with_account.__name__ = rule.__name__
    return rule_with_account

