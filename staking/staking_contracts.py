from pyteal import *
import algosdk
import utils
from algosdk import account, mnemonic
import json
from variables import Variables, AppMethods

class StakingContract(object):
    # def __init__(self):
    
    def application_start(self):

        actions = Cond(
            [Txn.application_id() == Int(0), self.app_initialization()],

            # [Txn.application_args[0] == Bytes(AppMethods.initialize_escrow),
            #  self.initialize_escrow(escrow_address=Txn.application_args[1])],

            [Txn.application_args[0] == Bytes(AppMethods.stake),
             self.stake()],

            [Txn.application_args[0] == Bytes(AppMethods.withdraw),
             self.withdraw()],
            [Txn.on_completion() == OnComplete.CloseOut,
                Return(Int(1))],
            [Txn.on_completion() == OnComplete.OptIn,
                self.user_opt_in()],

        )

        return actions

    def user_opt_in(self):
        return Seq([
            Assert(Txn.application_args.length() == Int(0)),
            App.localPut(Txn.sender(), Variables.balances, Int(0)),
            App.localPut(Txn.sender(), Variables.rewards, Int(0)),
            App.localPut(Txn.sender(), Variables.user_reward_per_token_paid, Int(0)),
            Return(Int(1))
        ])

    def app_initialization(self):
        return Seq([
            Assert(Txn.application_args.length() == Int(1)),
            
            App.globalPut(Variables.reward_rate, Int(100)),
            App.globalPut(Variables.last_update_time, Int(0)),
            App.globalPut(Variables.reward_per_token_stored, Int(0)),
            App.globalPut(Variables.token_1, Txn.assets[0]),
            App.globalPut(Variables.rewards_token, Txn.assets[1]),
            Return(Int(1))
        ])

    # def initialize_escrow(self, escrow_address):
        
    #     # curr_escrow_address = App.globalGetEx(Int(0), Variables.escrow_address)

    #     # asset_escrow = AssetParam.clawback(Txn.assets[0])
    #     # manager_address = AssetParam.manager(Txn.assets[0])
    #     # freeze_address = AssetParam.freeze(Txn.assets[0])
    #     # reserve_address = AssetParam.reserve(Txn.assets[0])
    #     # default_frozen = AssetParam.defaultFrozen(Txn.assets[0])

    #     return Seq([
    #         # curr_escrow_address,
    #         # Assert(curr_escrow_address.hasValue() == Int(0)),

    #         Assert(App.globalGet(Variables.app_admin) == Txn.sender()),
    #         Assert(Global.group_size() == Int(1)),
    #         App.globalPut(Variables.escrow_address, Txn.application_args[0]),
    #         Return(Int(1))
    #     ])

    def reward_per_token(self, total_supply, reward_per_token_stored, last_update_time, reward_rate, curr_round_time_stamp):

        if total_supply == Int(0) :
            return Int(0)
        
        return  (reward_per_token_stored + (curr_round_time_stamp - last_update_time) * reward_rate * (Int(int(1e6))) )/total_supply
   
    def earned(self, balances, reward_per_token, user_reward_per_token_paid, user_rewards):

        return (balances * reward_per_token -  user_reward_per_token_paid ) / (Int(int(1e6))) + user_rewards
 
       
    def update_rewards(self, balances, account, total_supply):
        #1. get data
        reward_per_token_stored = Btoi(App.globalGet(Variables.reward_per_token_stored))
        last_update_time = Btoi(App.globalGet(Variables.last_update_time))
        reward_rate = Btoi(App.globalGet(Variables.reward_rate))

        user_reward_per_token_paid = Btoi(App.localGet(account, Variables.user_reward_per_token_paid))
        user_rewards = Btoi(App.localGet(account, Variables.rewards))

        #2. cal 
        updated_last_update_time = Global.latest_timestamp()
        updated_reward_per_token_stored = self.reward_per_token(total_supply, reward_per_token_stored, last_update_time, reward_rate, updated_last_update_time)
        

        updated_user_rewards = self.earned(balances, reward_per_token_stored, user_reward_per_token_paid, user_rewards)


        return [App.localPut(account, Variables.rewards, updated_user_rewards),
                App.localPut(account, Variables.user_reward_per_token_paid, updated_reward_per_token_stored)
                ]


    def stake(self):
        # stake_amount = Btoi(Txn.application_args[1])
        # total_supply = Btoi(App.globalGet(Variables.total_supply))
        # balances = Btoi(App.localGet(Txn.sender(), Variables.balances))

        # 1. check transfer stake token user -> escrow
        # valid_stake_from_user_escrow = And(
        #     Gtxn[1].amount() > Int(0),
        #     Gtxn[1].type_enum() == TxnType.AssetTransfer,
        #     Gtxn[1].sender() == Txn.sender(),
        #     Gtxn[1].xfer_asset() == App.globalGet(Variables.token_1),
        #     Gtxn[1].amount() == stake_amount
        # )

        # 2. update state

        # update_rewards_seq = self.update_rewards(balances, Txn.sender(), total_supply)
        # update_curr_state = Seq(update_rewards_seq + [
        #     Assert(stake_amount > Int(0)),
        #     App.globalPut(Variables.total_supply, total_supply + stake_amount),
        #     App.localPut(Txn.sender(), Variables.balances, balances+stake_amount),
        #     Return(Int(1))
        # ])

        # return If(valid_stake_from_user_escrow).Then(update_curr_state).Else(Return(Int(0)))
        # return update_curr_state

        return Seq([Return(Int(1))])


    def withdraw(self):
        withdraw_amount = Btoi(Txn.application_args[1])
        total_supply = Btoi(App.globalGet(Variables.total_supply))
        balances = Btoi(App.localGet(Txn.accounts[1], Variables.balances))
        stake_token = App.globalGet(Variables.token_1)

        # 1. check transfer stake token escrow -> user
        valid_withdraw_from_user_escrow = And(
            Gtxn[1].asset_amount() > Int(0),
            Gtxn[1].type_enum() == TxnType.AssetTransfer,
            Gtxn[1].sender() == Txn.accounts[1],
            Gtxn[1].xfer_asset() == stake_token,
            Gtxn[1].asset_amount() == withdraw_amount
        )

        # 2. update state
        update_rewards_seq = self.update_rewards(balances, Txn.accounts[1], total_supply)

        update_curr_state = Seq(update_rewards_seq +[
            Assert(withdraw_amount <= balances),
            Assert(withdraw_amount <= total_supply),
            Assert(withdraw_amount > Int(0)),
            App.globalPut(Variables.total_supply, total_supply - withdraw_amount),
            App.localPut(Txn.accounts[1], Variables.balances, balances - withdraw_amount),
            Return(Int(1))
        ])

        return If(valid_withdraw_from_user_escrow).Then(update_curr_state).Else(Return(Int(0)))


    def approval_program(self):
        return self.application_start()

    def clear_program(self):
        return Return(Int(1))
