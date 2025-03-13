import near
from near_sdk_py import view, call, init, Context, Log, Storage, AccountId, Balance
from near_sdk_py.constants import ONE_NEAR

DEADLINE_STORAGE_KEY = "deadline"
REGISTERED_ACCOUNTS_STORAGE_KEY = "registered_accounts"

QUEST_AMOUNT = Balance(50 * ONE_NEAR)


class QuestContract:
    @init
    def new(self):
        if Storage.has(DEADLINE_STORAGE_KEY):
            near.panic_utf8("Already initialized")
        Storage.set_json(DEADLINE_STORAGE_KEY, Context.block_height() + 216000)

    @call
    def register_account(self, account_id: AccountId):
        if Context.predecessor_account_id() != Context.current_account_id():
            near.panic_utf8("Unauthorized")
        if Context.block_height() > Storage.get_json(DEADLINE_STORAGE_KEY):
            near.panic_utf8("Registration deadline passed")

        registered_accounts = Storage.get_json(REGISTERED_ACCOUNTS_STORAGE_KEY) or []
        if account_id in registered_accounts:
            near.panic_utf8("Already registered")

        # You can be extra lucky
        if len(registered_accounts) < 3:
            registered_accounts.append(account_id)
        registered_accounts.append(account_id)

        Storage.set_json(REGISTERED_ACCOUNTS_STORAGE_KEY, registered_accounts)

    @view
    def get_registered_accounts(self) -> list[AccountId]:
        return Storage.get_json(REGISTERED_ACCOUNTS_STORAGE_KEY) or []

    @call
    def three_two_one_go(self):
        import random

        if Context.block_height() <= Storage.get_json(DEADLINE_STORAGE_KEY):
            near.panic_utf8("Registration deadline not passed yet")
        registered_accounts = Storage.get_json(REGISTERED_ACCOUNTS_STORAGE_KEY) or []

        # You can be extra lucky
        if Context.predecessor_account_id() in registered_accounts:
            registered_accounts += [Context.predecessor_account_id()] * 3

        lucky_account_id = random.choice(registered_accounts)
        Log.info(f"NEAR DevHub Quest 003 winner: {lucky_account_id}")

        promise = near.promise_batch_create(lucky_account_id)
        near.promise_batch_action_transfer(promise, QUEST_AMOUNT)


# Export the contract methods
contract = QuestContract()

# These exports make functions available to the NEAR runtime
new = contract.new
register_account = contract.register_account
get_registered_accounts = contract.get_registered_accounts
three_two_one_go = contract.three_two_one_go
