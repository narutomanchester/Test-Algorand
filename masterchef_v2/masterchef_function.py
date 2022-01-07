from algosdk.future import transaction
from pyteal import *
import algosdk
import utils
from algosdk import account, mnemonic
from masterchef_contracts import MasterChef
import os.path
import utils
import pandas as pd
import json

class MasterChefFunction(object):

    def __init__(self):
        self.DII_assest_id = 54033772
        self.app_id = 1
        self.creator_public_address = "VPAU3O5MFL7VWX4O5W4AL43ZMLO6Z6IRW3433P35BEKHVPEAVU5344R6EA"
        self.private_creator_private_key = "ZNuaZpHC1YaVp5j88ZPzSfsd8W+wB6CC61O8cDknPEKrwU27rCr/W1+O7bgF83li3ez5Ebb5vb99CRR6vICtOw=="
        self.algod_client = utils.get_client()
        self.escrow_fund_address = ""
    
    def add(self, lp_assest_id, _alloc_point):
        

        # 1. create new account 
        private_key, public_address = account.generate_account()
        mnemonic_ = mnemonic.from_private_key(private_key)

        # 1.1 write to local
        utils.write_file(public_address, lp_assest_id)

        #3.1 send to this acc 1 Algos
        utils.send_algos(self.private_creator_private_key, public_address, public_address, 10000)

        #3.2 add Pair assest ID to this account
        utils.opt_in(public_address, private_key, self.DII_assest_id)
        utils.opt_in(public_address, private_key, lp_assest_id)

        #3.3 rekey to creator account
        utils.send_rekey_transaction(public_address, private_key, self.creator_public_address)

        #4. call contracts - add_pool function
        app_args = ["add_pool", lp_assest_id, _alloc_point, public_address]

        signed_txn = utils.call_app(self.algod_client, self.creator_public_address, self.private_creator_private_key, self.app_id, app_args)

        tx_id = signed_txn.transaction.get_txid()
    
        #### send transaction
        self.algod_client.send_transactions([signed_txn])

        #### await confirmation
        utils.wait_for_confirmation(self.algod_client, tx_id, 5)

        print("Application ADD Function called", tx_id)

    
    def deposit(self, lp_assest_id, deposit_amount, user_address, user_private_key):

        sp = utils.get_default_suggested_params(self.algod_client)
        atomic_group = []

        # 1. load account address that hold lp_assest_id
        df = pd.read_csv('accounts.csv')
        pooler_address = df[df['pool_assest_id']==lp_assest_id].reset_index(drop=True).loc[0]['public_address']

        #1.1 load user local data
        local_storage = utils.get_local_storage(self.algod_client, user_address, self.app_id)
        for data in local_storage:
            if data['key'] == Bytes(lp_assest_id):
                user_data = json.loads(Btoi(data['value']['bytes']))
                break
        user_amount, user_reward_debt = user_data['amount'], user_data['debt']

        #1.2 load pool local data
        pool_storage = utils.get_local_storage(self.algod_client, user_address, self.app_id)
        for data in pool_storage:
            if data['key'] == Bytes("acc_DII_per_share"):
                acc_DII_per_share = Btoi(data['value']['uint'])
                break

        #2. call contracts - deposit function 

        #2.1 cal pending rewards
        if user_amount > 0:
            pending = (user_amount * acc_DII_per_share)/(1e3) - user_reward_debt

        #2.2 cal contracts

        app_args = ["deposit", lp_assest_id, pooler_address, user_address, user_amount]
        call_app_txn = utils.call_app(self.app_id, app_args)
        atomic_group.append(call_app_txn)

        #3x. send transfer deposit_amount from user -> escrow address
        transfer_deposit_txn = transaction.AssetTransferTxn(sender=user_address,
                                                sp=sp,
                                                receiver=self.escrow_fund_address,
                                                amt=deposit_amount,
                                                index=lp_assest_id)

        atomic_group.append(transfer_deposit_txn)

        #4. send transfer pending amount from  escrow address -> user
        if user_amount > 0:
            transfer_rewards_txn = transaction.AssetTransferTxn(sender=self.escrow_fund_address,
                                                sp=sp,
                                                receiver=user_address,
                                                amt=pending,
                                                index=lp_assest_id)
            atomic_group.append(transfer_rewards_txn)    


        #5. Atomic transfer
        gid = transaction.calculate_group_id(atomic_group)

        #5.1 assign group id
        for txn in atomic_group:
            txn.group = gid
        
        #5.2 sign
        
        call_app_txn_signed = call_app_txn.sign(self.private_creator_private_key)
        
        transfer_deposit_txn_signed = call_app_txn.sign(user_private_key)

        signed_group = [call_app_txn_signed, transfer_deposit_txn_signed]

        if user_amount > 0:
            transfer_rewards_txn_logic_signature = transaction.LogicSig(escrow_fund_program_bytes)
            transfer_rewards_txn_signed = transaction.LogicSigTransaction(transfer_rewards_txn, transfer_rewards_txn_logic_signature)
            
            signed_group.append(transfer_rewards_txn_signed)


        txid = self.algod_client.send_transactions(signed_group)
        print(f'deposit transaction completed in: {txid}')





