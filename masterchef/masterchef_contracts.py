from pyteal import *
import algosdk
import utils

from masterchef_interface import MasterchefInterface


class MasterChef(MasterchefInterface):
    class Variables:
        escrow_address = Bytes("ESCROW_ADDRESS")
        amount = Bytes("AMOUNT")
        pid = Bytes("PID")
        app_state = Bytes("APP_STATE")
        app_admin = Bytes("APP_ADMIN")
        start_block = Bytes("start_block")
        assest_id = Bytes("assest_id")
        alloc_point = Bytes("alloc_point")
        last_reward_block = Bytes("last_reward_block")
        acc_DIM_per_share = Bytes("acc_DIM_per_share")
        # total_alloc_point = Bytes("total_alloc_point")
        dev_addr = Bytes("dev_addr")

        bonus_end_block = Bytes("bonus_end_block")
        token_per_block = Bytes("token_per_block")
        bonus_multiplier = Bytes("BONUS_MULTIPLIER")

    class AppMethods:
        initialize_escrow = "initializeEscrow"
        deposit = "deposit"
        withdraw = "withdraw"
        add = "add"

    class AppState:
        not_initialized = Int(0)
        active = Int(1)

    @property
    def global_schema(self):
        return algosdk.future.transaction.StateSchema(num_uints=2,
                                                      num_byte_slices=2)

    @property
    def local_schema(self):
        return algosdk.future.transaction.StateSchema(num_uints=0,
                                                      num_byte_slices=0)

    def app_initialization(self):
        return Seq([
            Assert(Txn.application_args.length() == Int(2)),
            App.globalPut(self.Variables.app_state, self.AppState.not_initialized),
            App.globalPut(self.Variables.asa_owner, Txn.application_args[0]),
            App.globalPut(self.Variables.app_admin, Txn.application_args[1]),
            App.globalPut(self.Variables.pool_info, Array()),
            App.globalPut(self.Variables.total_alloc_point, Int(0)),
            App.globalPut(self.Variables.bonus_multiplier, Int(10)),
            Return(Int(1))
        ])

    
     def initialize_escrow(self, escrow_address):
        curr_escrow_address = App.globalGetEx(Int(0), self.Variables.escrow_address) 

        # asset_escrow = AssetParam.clawback(Txn.assets[0])
        # manager_address = AssetParam.manager(Txn.assets[0])
        # freeze_address = AssetParam.freeze(Txn.assets[0])
        # reserve_address = AssetParam.reserve(Txn.assets[0])
        # default_frozen = AssetParam.defaultFrozen(Txn.assets[0])

        return Seq([
            curr_escrow_address,
            Assert(curr_escrow_address.hasValue() == Int(0)), 

            Assert(App.globalGet(self.Variables.app_admin) == Txn.sender()),
            Assert(Global.group_size() == Int(1)),

            # asset_escrow,
            # manager_address,
            # freeze_address,
            # reserve_address,
            # default_frozen,
            # Assert(Txn.assets[0] == App.globalGet(self.Variables.asa_id)),
            # Assert(asset_escrow.value() == Txn.application_args[1]),
            # Assert(default_frozen.value()),
            # Assert(manager_address.value() == Global.zero_address()),
            # Assert(freeze_address.value() == Global.zero_address()),
            # Assert(reserve_address.value() == Global.zero_address()),

            App.globalPut(self.Variables.escrow_address, escrow_address),
            App.globalPut(self.Variables.app_state, self.AppState.active),
            
            Return(Int(1))
        ])

    def add(self, _alloc_point):
        # if curr Block > startBlock -> curr Block else startBlock 

        curr_block = cleint.get_client().status()["last-round"]
        scratch_total_alloc_point = ScratchVar(TealType.uint64)
        scratch_start_block = ScratchVar(TealType.uint64)

        add_seq = Seq([ 
            scratch_total_alloc_point.store(App.globalGet(self.Variables.total_alloc_point)),
            scratch_start_block.store(App.globalGet(self.Variables.start_block)),
            App.globalPut(self.Variables.total_alloc_point, scratch_total_alloc_point.load() + Int(_alloc_point)),
            If(scratch_start_block.load() > Int(curr_block)).Then( App.globalPut(self.Variables.start_block, Int(curr_block) ).Else( App.globalPut(self.Variables.start_block, scratch_start_block.load() ) ),
            Return(Int(1))
        ])

        return add_seq

