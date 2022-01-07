from algosdk import kmd
from algosdk.wallet import Wallet

kmd_token = <kmd-token>
kmd_address = <kmd-address>
# create a kmd client
kcl = kmd.KMDClient(kmd_token, kmd_address)

# create a wallet object
wallet = Wallet("MyTestWallet1", "testpassword", kcl)

# get wallet information
info = wallet.info()
print("Wallet name:", info["wallet"]["name"])

# create an account
address = wallet.generate_key()
print("New account:", address)