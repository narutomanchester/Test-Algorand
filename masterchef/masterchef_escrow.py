from pyteal import *


def deposit_escrow(app_id: int, pid: int, ammount: int):
    return Seq([
        Assert(Global.group_size() == Int(3)),
        Assert(Gtxn[0].application_id() == Int(app_id)),
        Assert(Gtxn[1].pid() == Int(app_id)),

        Assert(Gtxn[2].fee() <= Int(1000)),
 

        Return(Int(1))
    ])
