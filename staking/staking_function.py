from algosdk.future import transaction
from pyteal import *
import algosdk
import utils
from algosdk import account, mnemonic
from staking_contracts import StakingContract
import utils
from algosdk.encoding import decode_address
from variables import Variables, AppMethods
import escrow_contracts
import base64

class ContractsFunction(object):
    def __init__(self, algod_client):
        self.algod_client = algod_client
        self.creator_public_address = "6IULTV4NQ76DAH2GPTBSG6TS2DWPM6FDJAJ7TBBFG7BYP7V5DV7R5LAQ3E"
        self.creator_private_key = "3QPWr4i4ymrgWS9/KaZRqhB8TuueTX+/gY21qWL1tZjyKLnXjYf8MB9GfMMjenLQ7PZ4o0gT+YQlN8OH/r0dfw=="

    def deploy_token(self):
        token1_asset_id, token2_asset_id = utils.deploy_token1_token2(self.algod_client, self.creator_public_address, self.creator_private_key)
        return token1_asset_id, token2_asset_id

    def deploy_statefull_contracts(self,token_1_id, rewards_token_id):
        contracts = StakingContract()
  
        approval_program_compiled = compileTeal(contracts.approval_program(),
                                        mode=Mode.Application,
                                        version=4)

        clear_program_compiled = compileTeal(contracts.clear_program(),
                                            mode=Mode.Application,
                                            version=4)

        approval_program_bytes = utils.compile_program(client=self.algod_client,
                                                                    source_code=approval_program_compiled)

        clear_program_bytes = utils.compile_program(client=self.algod_client,
                                                                source_code=clear_program_compiled)

        app_args = [
            decode_address(self.creator_public_address)
        ]

        
        txn = transaction.ApplicationCreateTxn(sender=self.creator_public_address,
                                            sp=utils.get_default_suggested_params(self.algod_client),
                                            on_complete=transaction.OnComplete.NoOpOC.real,
                                            approval_program=approval_program_bytes,
                                            clear_program=clear_program_bytes,
                                            global_schema=transaction.StateSchema(num_uints=5,num_byte_slices=0),
                                            local_schema=transaction.StateSchema(num_uints=3,num_byte_slices=0),
                                            app_args=app_args,
                                            foreign_assets=[token_1_id, rewards_token_id])

        
        app_transaction = txn.sign(private_key=self.creator_private_key)

        tx_id = utils.submit_transaction(self.algod_client, transaction=app_transaction)

        transaction_response = self.algod_client.pending_transaction_info(tx_id)

        app_id = transaction_response['application-index']
        print(f'Deployed app with app_id: {app_id}')
        return app_id

    def compile_exchange_escrow(self, app_id, token_1_id, rewards_token_id):
        
        print("Compiling exchange escrow logicsig...")
        escrow_logicsig_teal_code = compileTeal(
            escrow_contracts.logicsig(app_id, token_1_id, rewards_token_id), Mode.Application)
        compile_response = self.algod_client.compile(escrow_logicsig_teal_code)
        escrow_logicsig = compile_response['result']
        escrow_logicsig_bytes = base64.b64decode(escrow_logicsig)
        ESCROW_BYTECODE_LEN = len(escrow_logicsig_bytes)
        ESCROW_ADDRESS = compile_response['hash']
        print(
            f"Exchange Escrow | {ESCROW_BYTECODE_LEN}/1000 bytes ({ESCROW_ADDRESS})")

        with open('build/escrow.teal', 'w') as f:
            f.write(escrow_logicsig_teal_code)

        with open("build/escrow_logicsig", "w") as f:
            f.write(escrow_logicsig)

        print(f"Escrow logicsig compiled with address {ESCROW_ADDRESS}")

        print()

        return escrow_logicsig, ESCROW_ADDRESS
        
    def opt_user_into_contract(self, app_id, client, user_public_address, user_private_key):
        print(
            f"Opting user into contract with App ID: {app_id}..."
        )

        txn = transaction.ApplicationOptInTxn(
            sender=user_public_address,
            sp=client.suggested_params(),
            index=app_id
        ).sign(user_private_key)

        tx_id = client.send_transaction(txn)

        utils.wait_for_confirmation(client, tx_id, 5)

        print(
            f"Opted user into contract with App ID: {app_id} successfully! Tx ID: https://testnet.algoexplorer.io/tx/{tx_id}"
        )

        print()

    def opt_user_into_token(self, asset_id, client, user_public_address, user_private_key):
        print(
            f"Opting user into token with Asset ID: {asset_id}..."
        )

        txn = transaction.AssetTransferTxn(
            sender=user_public_address,
            sp=client.suggested_params(),
            receiver=user_public_address,
            amt=0,
            index=asset_id
        ).sign(user_private_key)

        tx_id = client.send_transaction(txn)

        utils.wait_for_confirmation(client, tx_id, 5)

        print(
            f"Opted user into token with Asset ID: {asset_id} successfully! Tx ID: https://testnet.algoexplorer.io/tx/{tx_id}"
        )

        print()
    
    def opt_escrow_into_token(self, client, escrow_logicsig, token_idx):
        print(
            f"Opting Escrow into Token with Asset ID: {token_idx}..."
        )
        program = base64.b64decode(escrow_logicsig)

        lsig = transaction.LogicSig(program)

        txn = transaction.AssetTransferTxn(
            sender=lsig.address(),
            sp=client.suggested_params(),
            receiver=lsig.address(),
            amt=0,
            index=token_idx,
        )

        lsig_txn = transaction.LogicSigTransaction(txn, lsig)

        tx_id = client.send_transaction(lsig_txn)

        utils.wait_for_confirmation(client,tx_id,5)

        print(
            f"Opted Escrow into Token with Asset ID: {token_idx} successfully! Tx ID: https://testnet.algoexplorer.io/tx/{tx_id}"
        )

        print()

    def transfer_token_1_to_user(self, client, stake_token, user_address, TOKEN_AMOUNT = 1000):
        
        print(
            f"Transferring {TOKEN_AMOUNT} to User..."
        )

        txn = transaction.AssetTransferTxn(
            sender=self.creator_public_address,
            sp=client.suggested_params(),
            receiver=user_address,
            amt=TOKEN_AMOUNT,
            index=stake_token
        ).sign(self.creator_private_key)


        tx_id = client.send_transaction(txn)
        

        utils.wait_for_confirmation(client, tx_id, 5)
        

        print(
            "Transferred ", tx_id
        )

        print()


class StakingFunction(object):

    def __init__(self, algod_client, app_id, escrow_fund_address, sender_public_address, stake_token_id):

        self.app_id = app_id
        self.algod_client = algod_client
        self.escrow_fund_address = escrow_fund_address
        self.sender_public_address = sender_public_address
        self.stake_token_id = stake_token_id
       

    def stake(self, stake_amount, user_address, user_private_key):
        sp = utils.get_default_suggested_params(self.algod_client)
        atomic_group = []

        #2. call contracts - stake function

        app_args = ["stake", stake_amount]
        call_app_txn = utils.call_app(self.algod_client, user_address, self.app_id, app_args )
        atomic_group.append(call_app_txn)

        #3. send transfer deposit_amount from user -> escrow address
        transfer_stake_txn = transaction.AssetTransferTxn(sender=user_address,
                                                sp=sp,
                                                receiver=self.escrow_fund_address,
                                                amt=stake_amount,
                                                index=self.stake_token_id)

        atomic_group.append(transfer_stake_txn)  


        #4. Atomic transfer
        gid = transaction.calculate_group_id(atomic_group)

        #4.1 assign group id
        for txn in atomic_group:
            txn.group = gid
        
        #4.2 sign
        
        call_app_txn_signed = call_app_txn.sign(user_private_key)
        
        transfer_stake_txn_signed = transfer_stake_txn.sign(user_private_key)

        signed_group = [call_app_txn_signed, transfer_stake_txn_signed]


        txid = self.algod_client.send_transactions(signed_group)
        print(f'deposit transaction completed in: {txid}')


    def withdraw(self, withdraw_amount, user_address, user_private_key):
        sp = utils.get_default_suggested_params(self.algod_client)
        atomic_group = []

        #2. call contracts - withdraw function

        app_args = ["withdraw", withdraw_amount]
        call_app_txn = utils.call_app(self.algod_client, self.escrow_fund_address, self.app_id, app_args, account=[user_address])

        atomic_group.append(call_app_txn)

        #3. send transfer withdraw_amount from escrow address -> user
        transfer_stake_txn = transaction.AssetTransferTxn(sender=self.escrow_fund_address,
                                                sp=sp,
                                                receiver=user_address,
                                                amt=withdraw_amount,
                                                index=self.token1_asset_id)

        atomic_group.append(transfer_stake_txn)  


        #4. Atomic transfer
        gid = transaction.calculate_group_id(atomic_group)

        #4.1 assign group id
        for txn in atomic_group:
            txn.group = gid
        
        #4.2 sign
        
        call_app_txn_signed = call_app_txn.sign(self.creator_private_key)
        
        transfer_stake_txn_signed = transfer_stake_txn.sign(user_private_key)

        signed_group = [call_app_txn_signed, transfer_stake_txn_signed]


        txid = self.algod_client.send_transactions(signed_group)
        print(f'deposit transaction completed in: {txid}')

