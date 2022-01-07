from staking_function import StakingFunction, ContractsFunction
import utils

class Deploy:
    def deploy():

        # 1. init
        algod_client = utils.get_client()

        contractsFunction = ContractsFunction(algod_client)

        ### 2.DEPLOY
        # 2.1 deploy token rewards / token stake
        token_1_id, rewards_token_id = contractsFunction.deploy_token() 

        # 2.2 deploy app
        app_id = contractsFunction.deploy_statefull_contracts(token_1_id, rewards_token_id)

        # 2.3 deploy escrow
        escrow_logicsig, escrow_address = contractsFunction.compile_exchange_escrow(app_id, token_1_id, rewards_token_id) 

        #2.4 send algo -> escrow
        utils.send_algos(client=algod_client,
                        private_key="3QPWr4i4ymrgWS9/KaZRqhB8TuueTX+/gY21qWL1tZjyKLnXjYf8MB9GfMMjenLQ7PZ4o0gT+YQlN8OH/r0dfw==",
                        my_address="6IULTV4NQ76DAH2GPTBSG6TS2DWPM6FDJAJ7TBBFG7BYP7V5DV7R5LAQ3E",
                        receiver_address=escrow_address,
                        amount=300000)

        ### 3. Opt-in
        #3.1 opt-int escrow -> token
        contractsFunction.opt_escrow_into_token(algod_client, escrow_logicsig, token_1_id)
        utils.send_algos(client=algod_client,
                        private_key="3QPWr4i4ymrgWS9/KaZRqhB8TuueTX+/gY21qWL1tZjyKLnXjYf8MB9GfMMjenLQ7PZ4o0gT+YQlN8OH/r0dfw==",
                        my_address="6IULTV4NQ76DAH2GPTBSG6TS2DWPM6FDJAJ7TBBFG7BYP7V5DV7R5LAQ3E",
                        receiver_address=escrow_address,
                        amount=300000)
        contractsFunction.opt_escrow_into_token(algod_client, escrow_logicsig, rewards_token_id)


        return token_1_id, rewards_token_id, app_id, escrow_logicsig, escrow_address


class ClientApp(object):
    def __init__(self, user_address, user_private_key, app_id, escrow_fund_address, stake_token_id):
        self.user_address = user_address
        self.user_private_key = user_private_key
        
        self.staking_function = StakingFunction(utils.get_client(), app_id, escrow_fund_address, self.user_address, stake_token_id)
  
    def stake(self, amount=1000):
        self.staking_function.stake(amount, self.user_address, self.user_private_key)

    def withdraw(self, amount=1000):
        self.staking_function.withdraw(amount, self.user_address, self.user_private_key)

    




