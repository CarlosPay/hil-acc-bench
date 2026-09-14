import argparse

import can

from bench.timing import STEP_S, FixedStepPacer
from sut.acc_stub import AccStub


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", default="vcan0")
    args = parser.parse_args()

    bus = can.Bus(interface="socketcan", channel=args.channel)
    stub = AccStub(bus)
    pacer = FixedStepPacer(STEP_S)
    try:
        while True:
            stub.step()
            pacer.wait_for_next_step()
    finally:
        bus.shutdown()


if __name__ == "__main__":
    main()
