import datetime
from accounts import Account, AccountCreation, Transaction, with_account


@AccountCreation.rule
def account_already_initialized(operation):
    "Once created, the account should not be updated or recreated"
    print(333, Account.account)
    if Account.account:
        return 'account-already-initialized'

@Transaction.rule
def account_not_initialized(operation):
    "The transaction needs an account"
    if not operation.account:
        return 'account-does-not-exists'

@Transaction.rule
@with_account
def insufficient_limit(operation):
    'The transaction amount should not exceed available limit'
    if operation.amount > operation.account.available_limit:
        return 'insufficient-limit'

@Transaction.rule
@with_account
def card_not_active(operation):
    'No transaction should be accepted when the card is not active'
    if not operation.account.active_card:
        return 'card-not-active'

@Transaction.rule
@with_account
def high_frequency_small_interval(operation):
    'There should not be more than 3 transactions on a 2 minute interval'
    delta = datetime.timedelta(minutes=2)
    if len([x for x in operation.account.transactions[-2:] if x.time >= operation.time - delta]) >= 2:
        return 'high-frequency-small-interval'

@Transaction.rule
@with_account
def doubled_transaction(operation):
    'There should not be more than 2 similar transactions (same amount and merchant) in a 2 minutes interval'
    delta = datetime.timedelta(minutes=2)
    if any(x for x in operation.account.transactions[-1:]
            if x.time >= operation.time - delta
            and operation.amount == x.amount
            and operation.merchant == x.merchant):
        return 'doubled-transaction'

