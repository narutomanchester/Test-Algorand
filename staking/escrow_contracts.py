from pyteal import *


def logicsig(app_id, token1_asset_id, token2_asset_id, ):
  
    program = Cond(
        [
            # If there is a single transaction within the group
            Global.group_size() == Int(1),
            # Then either this is an opt-in to a contract, or to an asset
            Or(
                And(
                    # This is a contract opt-in transaction
                    Txn.on_completion() == OnComplete.OptIn,

                    # Is an opt in to the manager contract
                    Txn.application_id() == Int(app_id)
                    
                ),
                And(
                    # This is an asset opt-in
                    Txn.type_enum() == TxnType.AssetTransfer,
                    # Sender and asset receiver are both Escrow
                    Txn.sender() == Txn.asset_receiver(),
               
                    # Is an opt-in to one of the expected assets
                    Or(
                        # Is an opt in to Token 1 Asset
                        Txn.xfer_asset() == Int(token1_asset_id),
                        # Is an opt in to Token 2 Asset
                        Txn.xfer_asset() == Int(token2_asset_id),

                    )
                )
            )
        ],
        [
            # If there are 2 transactions within the group
            Global.group_size() == Int(2),
            # Then this is a stake/withdraw transaction
            And(
                # first one is an ApplicationCall
                Gtxn[0].type_enum() == TxnType.ApplicationCall,
                # the ApplicationCall must be approved by the validator application
                Gtxn[0].application_id() == Int(app_id),

                # this transaction is the 2nd one
                Txn.group_index() == Int(2),
                # this transaction is an AssetTransfer
                Txn.type_enum() == TxnType.AssetTransfer,
                # this transaction is not a close transaction
                Txn.close_remainder_to() == Global.zero_address(),
                # this transaction is not an asset close transaction
                Txn.asset_close_to() == Global.zero_address()
            )
        ]
       
    )
    return program


if __name__ == "__main__":
    print(compileTeal(logicsig, Mode.Signature))
