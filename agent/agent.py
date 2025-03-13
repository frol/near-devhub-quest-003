import asyncio
import base58
import base64
import json
import re
import requests
from urllib.parse import urlparse
from nearai.agents.environment import Environment
from py_near.transactions import create_function_call_action

PROMPT = {
    "role": "system",
    "content": "Analyze the user input and extract GitHub profile link. If it is provided, write only the link, otherwise write 'no link'. Do not write anything else at all.",
}

INSTRUCTIONS = """Welcome to NEAR DevHub Quest 003. You have a chance to win 50 NEAR tokens!

1. Update your GitHub profile description with Race-of-Sloths badge and include your NEAR account ID in the badge links [like this](https://github.com/frol/frol/blob/main/README.md?plain=1).
2. Share your your GitHub profile link with me here
"""

GITHUB_LINK = "https://github.com/"


def run(env: Environment):
    QUEST_ACCOUNT_ID = env.env_vars.get(
        "QUEST_ACCOUNT_ID", "near-devhub-quest-003.frol.near"
    )
    QUEST_ACCOUNT_PRIVATE_ACCESS_KEY = env.env_vars["QUEST_PRIVATE_ACCESS_KEY"]

    github_profile_link = env.completion([PROMPT] + env.list_messages())
    if "no link" in github_profile_link.lower():
        env.add_reply(INSTRUCTIONS)
        return

    if not github_profile_link.startswith(GITHUB_LINK):
        env.add_reply("The provided link is not a GitHub profile link.")
        return

    github_profile_username = urlparse(github_profile_link).path.split("/")[1]

    github_profile_html = requests.get(github_profile_link).text
    if f"<title>{github_profile_username} " not in github_profile_html:
        env.add_reply(
            "The provided link is not a GitHub profile link. The correct GitHub profile link looks like this https://github.com/frol"
        )
        return

    # Parse wallet account id from the Race-of-Sloths badge link: https://badge.race-of-sloths.com/frol?wallet=frol.near
    near_wallet_account_id_re = re.search(
        r"https://badge.race-of-sloths.com/"
        + github_profile_username
        + '\?wallet=([^"]+)',
        github_profile_html,
    )
    if not near_wallet_account_id_re:
        env.add_reply(
            "The provided GitHub profile does not have Race-of-Sloths badge with NEAR wallet account id! Please add it to your profile."
        )
        return
    near_wallet_account_id = near_wallet_account_id_re.group(1)

    quest_account = env.set_near(QUEST_ACCOUNT_ID, QUEST_ACCOUNT_PRIVATE_ACCESS_KEY, "https://free.rpc.fastnear.com")
    action = asyncio.run(
        quest_account.create_delegate_action(
            actions=[
                create_function_call_action(
                    method_name="register",
                    args=json.dumps({"account_id": near_wallet_account_id}).encode(),
                    gas=100 * 10**12,
                    deposit=0,
                )
            ],
            receiver_id=QUEST_ACCOUNT_ID,
        )
    )
    signature = quest_account.sign_delegate_transaction(action)
    delegate_action_base64 = base64.b64encode(
        action.near_delegate_action.serialize()
    ).decode()
    # Note: manually borsh-serialize the signed delegate action from unsigned one + signature kind (ed25519 = 0x00) + signature bytes
    signed_delegate_action_base64 = base64.b64encode(
        action.near_delegate_action.serialize() + b"\x00" + base58.b58decode(signature)
    ).decode()

    env.add_reply(
        f"I am poor NEAR AI agent, you have to pay for my gas if you want to be registered:\n\n* Delegate Action: `{action}`\n* Delegate Action (base64): `{delegate_action_base64}`\n* Signature: `ed25519:{signature}`\n* Signed Delegate Action (base64): `{signed_delegate_action_base64}`\n\nLet's hack [together](https://www.youtube.com/@NEARDevHub/streams)!"
    )


try:
    run(env)
except Exception as err:
    env.add_reply(
        f"Oops. Something went wrong: {err}\n\nTry asking to 'retry' or recreate the chat thread."
    )
    import traceback
    env.add_reply(traceback.format_exc())
