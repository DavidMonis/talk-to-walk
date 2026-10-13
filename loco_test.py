#!/usr/bin/env python3
# Pomalý test chôdze G1: postupne spustí niekoľko pohybov a po každom zastaví.
# Spúšťa sa na Jetsone robota (cez SSH). Robot musí byť v režime chôdze.
#
# Použitie (bez argumentov, rozhranie je nastavené v INTERFACE):
#   python3 loco_test.py
#
# Príklad behu: pred každým pohybom stlač Enter, Ctrl+C robota kedykoľvek zastaví.
#   $ python3 loco_test.py
#   Interface: eth0
#   Initializing DDS...
#   WARNING: Uisti sa, že okolo robota nie sú prekážky.
#   [Enter] dopredu pomaly: vx=0.2, vy=0.0, vyaw=0.0, 3.0 s
#     Hotovo. Zmeraj prejdenú vzdialenosť alebo uhol.
#   [Enter] otočenie (+vyaw): vx=0.0, vy=0.0, vyaw=0.3, 3.0 s
#   ...

import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient


INTERFACE = "eth0"

TESTS = [  # (popis, vx [m/s], vy [m/s], vyaw [rad/s], trvanie [s])
    ("dopredu pomaly", 0.2, 0.0, 0.0, 3.0),
    ("otočenie (+vyaw)", 0.0, 0.0, 0.3, 3.0),
    ("otočenie (-vyaw)", 0.0, 0.0, -0.3, 3.0),
    ("dopredu rýchlejšie", 0.4, 0.0, 0.0, 3.0),
]


def hold(client, vx, vy, vyaw, duration, rate=10):
    end = time.time() + duration
    while time.time() < end:
        client.Move(vx, vy, vyaw)
        time.sleep(1 / rate)


print(f"Interface: {INTERFACE}")
print("Initializing DDS...")

ChannelFactoryInitialize(0, INTERFACE)

client = LocoClient()
client.SetTimeout(10.0)
client.Init()

print("WARNING: Uisti sa, že okolo robota nie sú prekážky.")

try:
    for name, vx, vy, vyaw, duration in TESTS:
        input(f"[Enter] {name}: vx={vx}, vy={vy}, vyaw={vyaw}, {duration} s")
        hold(client, vx, vy, vyaw, duration)
        client.Move(0, 0, 0)
        print("  Hotovo. Zmeraj prejdenú vzdialenosť alebo uhol.")
finally:
    client.Move(0, 0, 0)  # zastaví chôdzu; nevolaj Damp(), stojaci robot by spadol
