#!/usr/bin/env python3
# Krátky test otáčania G1 na mieste: doľava, potom doprava, po každom stop.
# Spúšťa sa na Jetsone robota (cez SSH). Robot musí byť v režime chôdze.
# Ctrl+C robota kedykoľvek zastaví.
#
# Použitie:
#   python3 turn_test.py

import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient


INTERFACE = "eth0"
VYAW = 0.6      # rad/s (~17 °/s)
DURATION = 3.0  # s -> ~0.9 rad (~52 °), ak robot dosiahne zadanú rýchlosť


def hold(client, vyaw, duration, rate=10):
    end = time.time() + duration
    while time.time() < end:
        client.Move(0.0, 0.0, vyaw)
        time.sleep(1 / rate)


ChannelFactoryInitialize(0, INTERFACE)
client = LocoClient()
client.SetTimeout(10.0)
client.Init()

print("WARNING: Uisti sa, že okolo robota nie sú prekážky.")

try:
    for name, vyaw in [("doľava (+vyaw)", VYAW), ("doprava (-vyaw)", -VYAW)]:
        input(f"[Enter] otočenie {name}: vyaw={vyaw}, {DURATION} s")
        hold(client, vyaw, DURATION)
        client.Move(0, 0, 0)
        print("  Hotovo. Zmeraj uhol.")
finally:
    client.Move(0, 0, 0)  # stop; nevolaj Damp(), stojaci robot by spadol
