#!/usr/bin/env bash
# Create the virtual CAN interface used by the bench.
# Must be re-run after every WSL/host restart.
set -euo pipefail

sudo modprobe vcan
sudo ip link add dev vcan0 type vcan 2>/dev/null || true
sudo ip link set up vcan0
ip link show vcan0
