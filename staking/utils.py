from algosdk.v2client import algod
from algosdk import account as algo_acc
import os
from pathlib import Path
from algosdk import mnemonic
from algosdk.v2client import indexer
from pathlib import Path
import algosdk.encoding as e
import json
import base64
from algosdk.future import transaction
from algosdk.encoding import decode_address


def get_token_id(client, txid):
    txinfo = client.pending_transaction_info(txid)
    asset_id = txinfo.get('asset-index')
    return asset_id


def deploy_token1_token2(client, creator_public_address, creator_private_key):

    txn_1 = transaction.AssetConfigTxn(
        sender=creator_public_address,
        sp=get_default_suggested_params(client),
        total=100000000000,
        default_frozen=False,
        unit_name="DIMMM",
        asset_name="DIMMM",
        manager=creator_public_address,
        reserve=creator_public_address,
        freeze=creator_public_address,
        clawback=creator_public_address,
        decimals=8
    ).sign(creator_private_key)

    txn_2 = transaction.AssetConfigTxn(
        sender=creator_public_address,
        sp=get_default_suggested_params(client),
        total=100000000000,
        default_frozen=False,
        unit_name="MIIIII",
        asset_name="MIIIII",
        manager=creator_public_address,
        reserve=creator_public_address,
        freeze=creator_public_address,
        clawback=creator_public_address,
        decimals=8
    ).sign(creator_private_key)

    tx_id_1 = client.send_transaction(txn_1)
    tx_id_2 = client.send_transaction(txn_2)

    wait_for_confirmation(client, tx_id_1, 5)
    wait_for_confirmation(client, tx_id_2, 5)

    token_1_asset_id = get_token_id(client, tx_id_1)
    token_2_asset_id = get_token_id(client, tx_id_2)

    
    print("already deployed 2 tokens: ", token_1_asset_id, token_2_asset_id)


    return token_1_asset_id, token_2_asset_id

def get_curr_round_ts(client):
    return client.block_info(client.status()['last-round'])['block']['ts']

def get_local_storage(client, public_address, app_id):
    for app_data in client.account_info(public_address)['apps-local-state']:
        if app_data['id'] == app_id:
            return app_data['key-value']

def get_default_suggested_params(client):
  
    suggested_params = client.suggested_params()

    suggested_params.flat_fee = True
    suggested_params.fee = 1000

    return suggested_params

def get_client():

    address = "http://localhost:4001"
    token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

    purestake_token = {'X-Api-key': token}

    algod_client = algod.AlgodClient(token, address, headers=purestake_token)
    return algod_client

def get_last_note_in_app(address, lp_asset_id, application_id):
    indexer_address = "https://testnet-algorand.api.purestake.io/idx2"
    indexer_token = ""
    headers = {
        "X-API-Key": "aGqhPDww0Z6mlwbaWr4Fg9OfOOxphBxyzmVJ3iba",
    }

    indexer_client = indexer.IndexerClient(indexer_token, indexer_address, headers)

    response = indexer_client.search_transactions(
        address=address, asset_id=lp_asset_id, application_id=application_id)

    return json.loads(base64.b64decode(json.loads(json.dumps(response))["transactions"][0]['note']).decode())

def get_escrow_address(app_id):
    return e.encode_address(e.checksum(b'appID'+(53742206).to_bytes(8, 'big')))

# def get_balance(lp_assest_id, account_address):
#     return AssetHolding.balance(account_address, lp_assest_id).value()

def wait_for_confirmation(client, transaction_id, timeout):
    """
    Wait until the transaction is confirmed or rejected, or until 'timeout'
    number of rounds have passed.
    Args:
        transaction_id (str): the transaction to wait for
        timeout (int): maximum number of rounds to wait    
    Returns:
        dict: pending transaction information, or throws an error if the transaction
            is not confirmed or rejected in the next timeout rounds
    """
    start_round = client.status()["last-round"] + 1
    current_round = start_round

    while current_round < start_round + timeout:
        try:
            pending_txn = client.pending_transaction_info(transaction_id)
        except Exception:
            return 
        if pending_txn.get("confirmed-round", 0) > 0:
            return pending_txn
        elif pending_txn["pool-error"]:  
            raise Exception(
                'pool error: {}'.format(pending_txn["pool-error"]))
        client.status_after_block(current_round)                   
        current_round += 1
    raise Exception(
        'pending tx not found in timeout rounds, timeout value = : {}'.format(timeout))

def call_app(client, sender_public_address, app_id, app_args, account=None) : 

    # get node suggested parameters
    params = get_default_suggested_params(client)

    # create unsigned transaction
    txn = transaction.ApplicationNoOpTxn(sender_public_address, params, app_id, app_args, accounts=account)

    # sign transaction
    # signed_txn = txn.sign(sender_private_key)
    return txn
    

# create new application
def create_app(client, public_address, private_key, approval_program, clear_program, global_schema, local_schema):

    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = get_default_suggested_params(client)

    # create unsigned transaction
    txn = transaction.ApplicationCreateTxn(public_address, params, on_complete, \
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


def send_algos(client, private_key, my_address, receiver_address, amount):
    
    algod_client = get_client()

    print("My address: {}".format(my_address))
    account_info = algod_client.account_info(my_address)
    print("Account balance: {} microAlgos".format(account_info.get('amount')))

    # build transaction
    params = get_default_suggested_params(client)
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    unsigned_txn = transaction.PaymentTxn(my_address, params, receiver_address, amount, None, None)

    # sign transaction
    signed_txn = unsigned_txn.sign(private_key)

    # submit transaction
    txid = algod_client.send_transaction(signed_txn)
    print("Signed transaction with txID: {}".format(txid))

    # wait for confirmation 
    try:
        confirmed_txn = wait_for_confirmation(algod_client, txid, 4)  
    except Exception as err:
        print(err)
        return

    print("Transaction send_algos information: {}".format(
        json.dumps(confirmed_txn, indent=4)))
    

def send_rekey_transaction(pool_public_address, pool_private_key, main_public_address):
    algod_client = get_client()
    params = get_default_suggested_params(client)
    txn_rekey = transaction.PaymentTxn(pool_public_address, params['minFee'], params['lastRound'], params['lastRound']+1000, params['genesishashb64'], pool_public_address, 0, rekey_to=main_public_address)
    stxn_rekey = txn_rekey.sign(pool_private_key)
    txid = algod_client.send_transaction(stxn_rekey)

    # wait for confirmation 
    try:
        confirmed_txn = wait_for_confirmation(algod_client, txid, 4)  
    except Exception as err:
        print(err)
        return

    print("Transaction send_rekey_transaction information: {}".format(
        json.dumps(confirmed_txn, indent=4)))


def write_file(public_address, pool_assest_id):
    _file_ = Path("accounts.csv")
    output = open(_file_, 'w')
    if not _file_.is_file():
        output.write("public_address;pool_assest_id\n")
    output.write(f"{public_address};{pool_assest_id}\n")


def compile_program(client, source_code):

    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response['result'])

def submit_transaction(client, transaction):
    txid = client.send_transaction(transaction)

    wait_for_confirmation(client, txid, 5)

    return txid


