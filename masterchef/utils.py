from algosdk.v2client import algod
from algosdk import account as algo_acc
import yaml
import os
from pathlib import Path
from algosdk import mnemonic
from algosdk.v2client import indexer


def get_client():

    address = "http://localhost:4001"
    token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

    purestake_token = {'X-Api-key': token}

    algod_client = algod.AlgodClient(token, address, headers=purestake_token)
    return algod_client


def call_app(client, private_key, index, app_args) : 
    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    
    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id, 5)

    print("Application called", tx_id)

# create new application
def create_app(client, private_key, approval_program, clear_program, global_schema, local_schema):
    # define sender as creator
    sender = account.address_from_private_key(private_key)
    # sender = "ZnmOaVW+VaMJNGO4T9xQzgTlBmt/j2WESEM7v5btxzJT/pTm1zw4ETeu3FP6v2BHAXbAKoxCvBK0GMbWt9iHcQ=="

    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = transaction.ApplicationCreateTxn(sender, params, on_complete, \
                                            approval_program, clear_program, \
                                            global_schema, local_schema)

    # sign transaction
    signed_txn = txn.sign(private_key)
    
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id, 5)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['application-index']
    print("Created new app-id:", app_id)

    return app_id