from pyteal import *

class Variables:
    #global
    reward_rate = Bytes("reward_rate")
    last_update_time = Bytes("last_update_time")
    reward_per_token_stored = Bytes("reward_per_token_stored")
    total_supply = Bytes("total_supply")
    rewards_token = Bytes("rewards_token")
    token_1 = Bytes("token1")
    app_admin = Bytes("app_admin")

    #local user
    user_reward_per_token_paid = Bytes("user_reward_per_token_paid")
    rewards = Bytes("rewards")
    balances = Bytes("balances")

class AppMethods:
    initialize_escrow = "initializeEscrow"
    stake = "stake"
    withdraw = "withdraw"
    add = "add"