import json
import base64
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.future.transaction import PaymentTxn
import algosdk.encoding as e 
def generate_algorand_keypair():
    private_key, address = account.generate_account()
    print("My address: {}".format(address))
    print("My private key: {}".format(private_key))
    print("My passphrase: {}".format(mnemonic.from_private_key(private_key)))
    return address, private_key

my_address, private_key = generate_algorand_keypair()

