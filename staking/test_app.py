from app import Deploy, ClientApp
import utils
from staking_function import ContractsFunction

token_1_id, rewards_token_id, app_id, escrow_logicsig, escrow_address = Deploy.deploy()

print("token_1_id, rewards_token_id, app_id, escrow_logicsig, escrow_address: ", token_1_id, rewards_token_id, app_id, escrow_logicsig, escrow_address)
# token_1_id, rewards_token_id, app_id, escrow_logicsig, escrow_address = 56502716, 56502715, 56502815, "AiAHAQIGn9T4GgS80/gau9P4GjIEIhJAAC0yBCMSQAABADMAECQSMwAYJRIQMRYjEhAxECEEEhAxCTIDEhAxFTIDEhBCACExGSISMRglEhAxECEEEjEAMRQSEDERIQUSMREhBhIREBFD", "BGLRXFBHYHUATPUFH6TQPYUI3VWSODKDBXZD6NLPXTGNEPX7EGFVMVNM74"


######## Test Call App ########
user_address = "IDPZURIZGAG7XOCU2MRN4ZKCZTDPRORJBSLNYVB4BHJ335QYC33G2CWBCQ"
user_private_key = "ofc9QWMTIz+qK7JMldDHkHOC+BI2Z/7hQaJBfDMDjqxA35pFGTAN+7hU0yLeZULMxvi6KQyW3FQ8CdO99hgW9g=="

# init
client = utils.get_client()
contractsFunction = ContractsFunction(client)

# contractsFunction.opt_user_into_contract(app_id, client, user_address, user_private_key)

contractsFunction.opt_user_into_token(token_1_id, client, user_address, user_private_key)
contractsFunction.opt_user_into_token(rewards_token_id, client, user_address, user_private_key)

contractsFunction.transfer_token_1_to_user(client, token_1_id, user_address)

client_app = ClientApp(user_address, user_private_key, 56447868, "CFS4OCUQODIJ77XWTILHNBWLWDPRH55TSY7SLALANWZTZ3SAGND6VBSFFA", token_1_id)

client_app.stake()