from pyteal import *
from pyteal.ast import app
from algosdk import logic as algo_logic
from algosdk.future import transaction as algo_txn
from pyteal import compileTeal, Mode
from algosdk.encoding import decode_address
import utils

class StatelessContracts:
    def __init__(self, app_id, asa_id, algod_client, user_rewards, deposit_amount):
        self.app_id = app_id
        self.asa_id = asa_id
        self.client = algod_client
        self.user_rewards = user_rewards
        self.deposit_amount = deposit_amount


    def escrow_bytes(self):

        escrow_fund_program_compiled = compileTeal(
            self.masterchef_escrow(),
            mode=Mode.Signature,
            version=4,
        )

        return utils.compile_program(
            client=self.client, source_code=escrow_fund_program_compiled
        )

    
    def escrow_address(self):
        return algo_logic.address(self.escrow_bytes)


    def masterchef_escrow(self):
        return Seq([
            Assert(Gtxn[0].application_id() == Int(self.app_id)),
            
            Assert(Gtxn[1].type_enum() == TxnType.AssetTransfer),
            Assert(Gtxn[1].asset_amount() == Int(self.user_rewards)),
            Assert(Gtxn[1].xfer_asset() == Int(self.asa_id)),
            Assert(Gtxn[1].fee() <= Int(1000)),

            Assert(Gtxn[2].type_enum() == TxnType.AssetTransfer),
            Assert(Gtxn[2].asset_amount() == Int(self.deposit_amount)),
            Assert(Gtxn[2].xfer_asset() == Int(self.asa_id)),
            Assert(Gtxn[2].fee() <= Int(1000)),
            
            Return(Int(1))
        ])
