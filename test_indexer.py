# # /indexer/python/account_info_block.py
# import json
# # requires Python SDK version 1.3 or higher
# from algosdk.v2client import indexer

# # instantiate indexer client
# myindexer = indexer.IndexerClient(indexer_token="", indexer_address="http://localhost:8980")
# # myindexer = indexer.IndexerClient(indexer_token="", indexer_address='https://testnet-algorand.api.purestake.io/idx2')

# response = myindexer.account_info(
#     address="7WENHRCKEAZHD37QMB5T7I2KWU7IZGMCC3EVAO7TQADV7V5APXOKUBILCI", block=50)
# print("Account Info: " + json.dumps(response, indent=2, sort_keys=True))

import json
from algosdk.v2client import indexer
import base64
indexer_address = "https://mainnet-algorand.api.purestake.io/idx2"
indexer_token = ""
headers = {
    "X-API-Key": "aGqhPDww0Z6mlwbaWr4Fg9OfOOxphBxyzmVJ3iba",
}

indexer_client = indexer.IndexerClient(indexer_token, indexer_address, headers)

# response = indexer_client.search_transactions(
#     address="JA2V6HFOBR2642M523742GOA4BKN7FKEA5LTJFONOF45THKBX2GP3H7WJE", application_id=21580889)

response = indexer_client.search_transactions(application_id=350338509, txn_type="appl")
# , address="GZ6RELRNWAHFUY7QEDIEMBROCH4YF53JECWJYLKXHXDZNAAXIVSQMAI2DY")

# print(json.loads(base64.b64decode(json.loads(json.dumps(response))["transactions"][0]['note']).decode())
transactions = json.loads(json.dumps(response))['transactions']
# print(transactions)
transac_list = {}
for transac in transactions:
    # print(transac, type(transac))
    if 'bWludA==' in transac['application-transaction']['application-args'] and len(transac['local-state-delta'])==2:
        x = transac['application-transaction']['accounts'][0]
        if x not in transac_list:
            transac_list[x] = []
        transac_list[x].append(transac)
        # print(transac)
        # break
        if len(transac['local-state-delta'][1]['delta']) > 2:
    # print(transac)?
        # transac_list.append(transac)
            print(transac)


for x,y in transac_list.items():
    if len(y)>5:
        print(x,y)
        break
# print(transac_list[-10:])
print(base64.b64decode("dA==").decode())

