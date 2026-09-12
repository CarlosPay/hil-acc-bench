import can

with can.Bus(interface="virtual", channel="bench") as tx, \
     can.Bus(interface="virtual", channel="bench") as rx:
    tx.send(can.Message(arbitration_id=0x100, data=[1, 2, 3, 4], is_extended_id=False))
    print(rx.recv(timeout=1))
