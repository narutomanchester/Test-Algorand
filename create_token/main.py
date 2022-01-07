from algosdk.v2client import algod
from algosdk.future.transaction import AssetConfigTxn
from algosdk.future.transaction import write_to_file
from util import sign_and_send, balance_formatter
creator_address = "KP7JJZWXHQ4BCN5O3RJ7VP3AI4AXNQBKRRBLYEVUDDDNNN6YQ5YWWCQVJE"
creator_passphrase = "coast delay regular torch problem hand park glimpse warfare illness chronic erupt skate script win month million capital payment victory coin window normal ability pear"

receiver_address = "VPAU3O5MFL7VWX4O5W4AL43ZMLO6Z6IRW3433P35BEKHVPEAVU5344R6EA"
receiver_passphrase = "hold hidden rebuild cinnamon process giant device obvious display exist what region desk wisdom lock amateur favorite puppy clarify armed indicate antenna ball able salon"

# Credentials to connect through an algod client
algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

# Details of the asset creation transaction
asset_details = {
	"asset_name": "DIGIME",
	"unit_name": "DIM",
	"total": 1e17,
	"decimals": 8,
	"default_frozen": False,
	"manager": creator_address,
	"reserve": creator_address,
	"freeze": creator_address,
	"clawback": creator_address,
	"url": "ava.jpg",
	"metadata_hash": b'cKR\xf1\xed\xbf\x02\x8c~\x8c\xa2\x1b\xa6\x8e\xde\xceB%\x8c\x1c\xa4\xe8\xe5\xb3\xf5\xe2\xe7a\x95\x1c1c'
}

metadata_file = "ava.jpg"
metadatahash_b64 = "Y0tS8e2/Aox+jKIbpo7ezkIljByk6OWz9eLnYZUcMWM="

# The asset ID is available after the asset is created.
asset_id = 0 # change this


# create coin
client = algod.AlgodClient(algod_token, algod_address)

def create(passphrase=None):
	"""
	Returns an unsigned txn object and writes the unsigned transaction
	object to a file for offline signing. Uses current network params.
	"""

	params = client.suggested_params()
	txn = AssetConfigTxn(creator_address, params, **asset_details)

	if passphrase:
		txinfo = sign_and_send(txn, passphrase, client)
		asset_id = txinfo.get('asset-index')
		print("Asset ID: {}".format(asset_id))
	else:
		write_to_file([txn], "create_coin.txn")

def optin(passphrase=None):
	"""
	Creates an unsigned opt-in transaction for the specified asset id and 
	address. Uses current network params.
	"""
	params = client.suggested_params()
	txn = AssetTransferTxn(sender=receiver_address, sp=params, receiver=receiver_address, amt=0, index=asset_id)
	if passphrase:
		txinfo = sign_and_send(txn, passphrase, client)
		print("Opted in to asset ID: {}".format(asset_id))
	else:
		write_to_file([txns], "optin.txn")

def transfer(passphrase=None):
	"""
	Creates an unsigned transfer transaction for the specified asset id, to the 
	specified address, for the specified amount.
	"""
	amount = 6000
	params = client.suggested_params()
	txn = AssetTransferTxn(sender=creator_address, sp=params, receiver=receiver_address, amt=amount, index=asset_id)
	if passphrase:
		txinfo = sign_and_send(txn, passphrase, client)
		formatted_amount = balance_formatter(amount, asset_id, client)
		print("Transferred {} from {} to {}".format(formatted_amount, 
			creator_address, receiver_address))
		print("Transaction ID Confirmation: {}".format(txinfo.get("tx")))
	else:
		write_to_file([txns], "transfer.txn")

def check_holdings(asset_id, address):
	"""
	Checks the asset balance for the specific address and asset id.
	"""
	account_info = client.account_info(address)
	assets = account_info.get("assets")
	for asset in assets:
		if asset['asset-id'] == asset_id:
			amount = asset.get("amount")
			print("Account {} has {}.".format(address, balance_formatter(amount, asset_id, client)))
			return
	print("Account {} must opt-in to Asset ID {}.".format(address, asset_id))


create(creator_passphrase)