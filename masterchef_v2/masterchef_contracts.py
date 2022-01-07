from pyteal import *
import algosdk
import utils
from algosdk import account, mnemonic
from masterchef_interface import MasterchefInterface
import json

class MasterChef(MasterchefInterface):
    class Variables:
        DII_assest_id = 54033772
        bonus_multiplier_cons = 10

        escrow_address = Bytes("ESCROW_ADDRESS")
        amount = Bytes("AMOUNT")
        pid = Bytes("PID")
        app_state = Bytes("APP_STATE")
        app_admin = Bytes("APP_ADMIN")
        start_round = Bytes("start_round")
        assest_id = Bytes("assest_id")
        alloc_point = Bytes("alloc_point")
        last_reward_round = Bytes("last_reward_round")
        DII_per_round = Bytes("DII_per_round")
        acc_DII_per_share = Bytes("acc_DII_per_share")
        can_claim = Bytes("can_claim")
        # total_alloc_point = Bytes("total_alloc_point")
        # dev_addr = Bytes("dev_addr")

        bonus_end_round = Bytes("bonus_end_round")
        token_per_round = Bytes("token_per_round")
        bonus_multiplier = Bytes("BONUS_MULTIPLIER")

        lp_assest_id = Bytes("lp_assest_id")

    class AppMethods:
        initialize_escrow = "initializeEscrow"
        deposit = "deposit"
        withdraw = "withdraw"
        add = "add"

    # class AppState:
    #     not_initialized = Int(0)
    #     active = Int(1)

    @property
    def global_schema(self):
        return algosdk.future.transaction.StateSchema(num_uints=2,
                                                      num_byte_slices=2)

    @property
    def local_schema(self):
        return algosdk.future.transaction.StateSchema(num_uints=0,
                                                      num_byte_slices=0)

    def application_start(self):
        actions = Cond(
            [Txn.application_id() == Int(0), self.app_initialization()],

            [Txn.application_args[0] == Bytes(self.AppMethods.initialize_escrow),
             self.initialize_escrow(escrow_address=Txn.application_args[1])],

            [Txn.application_args[0] == Bytes(self.AppMethods.deposit),
             self.deposit()],

            [Txn.application_args[0] == Bytes(self.AppMethods.add),
             self.add()],

        )

        return actions

    def app_initialization(self):
        return Seq([
            # Assert(Txn.application_args.length() == Int(2)),
            App.globalPut(self.Variables.app_state, self.AppState.not_initialized),
            # App.globalPut(self.Variables.asa_owner, Txn.application_args[0]),
            # App.globalPut(self.Variables.app_admin, Txn.application_args[1]),
            App.globalPut(self.Variables.total_alloc_point, Int(0)),
            App.globalPut(self.Variables.bonus_multiplier, Int(10)),
            App.globalPut(self.Variables.bonus_end_round, Int(18662548000)),
            App.globalPut(self.Variables.DII_per_round, Int(10)),
            
            Return(Int(1))
        ])

    
    def initialize_escrow(self, escrow_address):
        curr_escrow_address = App.globalGetEx(Int(0), self.Variables.escrow_address)

        return Seq([
            curr_escrow_address,
            Assert(curr_escrow_address.hasValue() == Int(0)), 

            Assert(App.globalGet(self.Variables.app_admin) == Txn.sender()),
            Assert(Global.group_size() == Int(1)),
            App.globalPut(self.Variables.escrow_address, escrow_address),
            App.globalPut(self.Variables.app_state, self.AppState.active),
            
            Return(Int(1))
        ])

    def get_multiplier(self, _from, _to, bonus_end_round):
        if _to < _from:
            return (_to - _from) * self.Variables.bonus_multiplier_cons
        elif _from > bonus_end_round:
            return _to - _from
        else:
            return (bonus_end_round - _from) * self.Variables.bonus_multiplier_cons + bonus_end_round

    # def withdraw(self):

    def deposit(self):
        # get pool info 
        pool_account_public_address = Btoi(Txn.application_args[2])
        lp_assest_id = Btoi(Txn.application_args[1])
        deposit_amount = Btoi(Txn.application_args[6])
        

        # get user info
        user_public_address = Btoi(Txn.application_args[3])
        user_info = json.loads(Btoi(App.localGet(Int(0), Bytes(lp_assest_id))))
        user_amount = user_info['amount']
        user_reward_debt = user_info['reward_debt']


        # get Global Var
        acc_DII_per_share = Btoi(App.globalGet(self.Variables.acc_DII_per_share))
        

        # 2. Do logical - cal 
        #2.1 Update Pool
        seq_pool = self.update_pool(pool_account_public_address, lp_assest_id)

        #2.2 cal rewards
        if user_amount > 0:
            pending = (user_amount * acc_DII_per_share)/(1e3) - user_reward_debt

        user_new_amount = user_amount + deposit_amount
        user_new_reward_debt = (user_amount * acc_DII_per_share)/(1e3)


        #3. Verify rewards transaction escrow -> user
        valid_rewards_tranfer_from_escrow_user = And(
            Gtxn[1].type_enum() == TxnType.AssetTransfer,
            Gtxn[1].sender() == App.globalGet(self.Variables.escrow_address),
            Gtxn[1].xfer_asset() == lp_assest_id,
            Gtxn[1].asset_amount() == Int(pending)
        )

        #4. Verify transaction deposit user -> escrow
        valid_deposit_from_user_escrow = And(
            Gtxn[2].type_enum() == TxnType.AssetTransfer,
            Gtxn[2].sender() == user_public_address,
            Gtxn[2].xfer_asset() == lp_assest_id,
            Gtxn[2].asset_amount() == Int(deposit_amount)
        )

        all_valid  = And (
            valid_rewards_tranfer_from_escrow_user,
            valid_deposit_from_user_escrow
        )

        #5. get current state of contracts function
        update_state = Seq(seq_pool + [
            App.localPut(user_public_address, Bytes(lp_assest_id), {'amount': user_new_amount, 'reward_debt':user_new_reward_debt}),
            
            Return(Int(1))
        ])

        return If(all_valid).Then(update_state).Else(Return(Int(0)))

        
    def update_pool(self, pool_account_public_address, lp_assest_id):
        # 1. get info 
        curr_round = utils.get_client().status()["last-round"]
        last_reward_round = Btoi(App.localGet(pool_account_public_address, self.Variables.last_reward_round))
        bonus_end_round = Btoi(App.globalGet(self.Variables.bonus_end_round))
        DII_per_round = Btoi(App.globalGet(self.Variables.DII_per_round))
        total_alloc_point = Btoi(App.globalGet(self.Variables.total_alloc_point))
        acc_DII_per_share = Btoi(App.globalGet(self.Variables.acc_DII_per_share))

        if curr_round <= last_reward_round:
            return
        
        escrow_address = ""
        lp_supply = utils.get_balance(lp_assest_id, escrow_address)

        if lp_supply == 0:
            return [App.localPut(pool_account_public_address, self.Variables.last_reward_round, Int(curr_round))]

        multiplier = self.get_multiplier()

        multiplier = self.getMultiplier(last_reward_round, curr_round, bonus_end_round)
        DII_reward = (multiplier * DII_per_round) / total_alloc_point

        acc_DII_per_share = (acc_DII_per_share + DII_reward) * (1e3) / lp_supply
        last_reward_round = curr_round


        return [
            App.localPut(pool_account_public_address, self.Variables.acc_DII_per_share, Int(acc_DII_per_share)),
            App.localPut(pool_account_public_address, self.Variables.last_reward_round, Int(last_reward_round))
        ]

    
    def add_pool(self):

        address = Btoi(Txn.application_args[3])
        _alloc_point = Btoi(Txn.application_args[2])
        # Get Last Reward Round
        start_round = Btoi(App.globalGet(self.Variables.start_round))
        curr_round = utils.get_client().status()["last-round"]
        last_reward_round = curr_round if curr_round > start_round else start_round
        
        scratchTotalPoint = ScratchVar(TealType.uint64)

        # Put Var
        return Seq([
                App.localPut(address, self.Variables.last_reward_round, Int(last_reward_round)),
                App.localPut(address, self.Variables.lp_assest_id, Int(Btoi(Txn.application_args[1]))),
                App.localPut(address, self.Variables.acc_DII_per_share, Int(0)),
                App.localPut(address, self.Variables.alloc_point, Int(_alloc_point)),
                scratchTotalPoint.store(App.globalGet(self.Variables.total_alloc_point)),
                App.globalPut(self.Variables.total_alloc_point, scratchTotalPoint.load() + Int(_alloc_point)),
                Return(Int(1))
        ])


    def approval_program(self):
        return self.application_start()

    def clear_program(self):
        return Return(Int(1))
