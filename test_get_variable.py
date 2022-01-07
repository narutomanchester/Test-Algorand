import base64
from algosdk.v2client import algod
from pyteal import *

def get_client():

    address = "http://localhost:4001"
    token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

    purestake_token = {'X-Api-key': token}

    algod_client = algod.AlgodClient(token, address, headers=purestake_token)
    return algod_client

# helper function that formats global state for printing
def format_state(state):
    formatted = {}
    for item in state:
        key = item['key']
        value = item['value']
        formatted_key = base64.b64decode(key).decode('utf-8')
        if value['type'] == 1:
            # byte string
            if formatted_key == 'voted':
                formatted_value = base64.b64decode(value['bytes']).decode('utf-8')
            else:
                formatted_value = value['bytes']
            formatted[formatted_key] = formatted_value
        else:
            # integer
            formatted[formatted_key] = value['uint']
    return formatted

# helper function to read app global state
def read_local_state(addr, app_id):
    client = get_client()
    account = client.account(addr)
    # apps_created = results['created-apps']
    # for app in apps_created:
    #     if app['id'] == app_id:
    #         return format_state(app['params']['local-state'])
    print(App.localGetEx(account, Int(app_id), base64.b64decode('c1').decode('utf-8')))
    # return {}

# read_local_state("FMUGCX2ZWVL3TLMNOUBZV7UFLU5MMLMWIMAPMR5MSA3LUSRXVV6FLXMQ6E", 21580889)

# for x in get_client().account_info("FMUGCX2ZWVL3TLMNOUBZV7UFLU5MMLMWIMAPMR5MSA3LUSRXVV6FLXMQ6E")['apps-local-state']:
#     if x['id'] == 21580889:
#         print(x)

# x = get_client()

# print(x.block_info(x.status()['last-round'])['block']['ts'])
