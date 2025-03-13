# NEAR DevHub Quest 002

It is the second quest in the [NEAR DevHub](https://dev.near.org) Quests. Learn more in the [most recent DevHub Live episode](https://www.youtube.com/live/BzoBrTYCNBk?feature=shared&t=2857).

This quest started on March 13th, 2025, and was deployed to [neardev-quest-003.frol.near](https://explorer.near.org/accounts/near-devhub-quest-003.frol.near) and [helper NEAR AI agent](https://app.near.ai/agents/frol.near/DevHub-Quest-003/latest).

## Quest

The quest is simple: withdraw 50 NEAR from the contract.

## Rewards

The rewards are 50 NEAR.

## Development

This quest uses an early version of [near-sdk-py](https://github.com/r-near/near-sdk-py).

### Prerequisites

- Python 3.9 or higher
- [uv](https://pypi.org/project/uv/)
- [NEAR CLI](https://near.cli.rs)

### Setup

1. Install dependencies:

```sh
uv venv
uv sync
```

2. Build the contract:

```sh
uvx nearc
```

3. Deploy the contract:

```sh
near contract deploy use-file main.wasm
```
