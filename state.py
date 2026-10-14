#!/usr/bin/env python3
# Zistenie a zmena režimu (FSM) G1 cez LocoClient. Funguje aj so staršou verziou
# unitree_sdk2py, ktorá ešte nemá LocoClient.GetFsmId().
# Spúšťa sa na Jetsone robota (cez SSH).
#
# Použitie:
#   python state.py          # vypíše aktuálny režim
#   python state.py dump     # FSM 1:   damping (POZOR: stojaci robot spadne)
#   python state.py lock     # FSM 4:   locked standing
#   python state.py regular  # FSM 501: regular mode 
#   python state.py running  # FSM 801: running mode, v ňom funguje Move()
#   python state.py set 801  # ľubovoľné FSM ID
#
# FSM ID na našom G1 (namerané 2026-10-14):
#   0   zero torque     - po zapnutí robota, motory bez sily
#   1   damping         - tlmenie, robot je "mäkký"
#   4   locked standing - zamknutý stoj, robot stojí, ale nechodí
#   801 running mode    - chôdza

import json
import sys
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient


INTERFACE = "eth0"
API_GET_FSM_ID = 7001  # zistenie FSM ID, registrované v LocoClient.Init()

FSM_NAMES = {
    0: "zero torque",
    1: "damping",
    4: "locked standing",
    501: "regular mode",
    801: "running mode",
}

COMMANDS = {
    "dump": 1,
    "lock": 4,
    "regular": 501,
    "running": 801,
}
FALL_RISK = {0, 1}  # zero torque, damping: stojaci robot spadne


def get_fsm_id(client):
    code, data = client._Call(API_GET_FSM_ID, json.dumps({}))
    if code != 0:
        return code, None
    return code, json.loads(data).get("data")


def describe(fsm_id):
    return f"{fsm_id} ({FSM_NAMES.get(fsm_id, 'neznámy')})"


args = sys.argv[1:]
target = None
if len(args) == 1 and args[0] in COMMANDS:
    target = COMMANDS[args[0]]
elif len(args) == 2 and args[0] == "set" and args[1].isdigit():
    target = int(args[1])
elif args:
    print("Použitie: python3 state.py [dump|lock|running|set <id>]")
    sys.exit(1)

ChannelFactoryInitialize(0, INTERFACE)
client = LocoClient()
client.SetTimeout(10.0)
client.Init()

code, fsm_id = get_fsm_id(client)
print(f"Aktuálny režim: {describe(fsm_id)}, return code {code}")

if target is not None:
    if target in FALL_RISK:
        print(f"POZOR: v režime {describe(target)} stojaci robot spadne. "
              "Použi len keď visí na stojane alebo sedí.")
    input(f"[Enter] prepnúť na {describe(target)}, Ctrl+C zruší")
    code = client.SetFsmId(target)
    print(f"SetFsmId({target}) return code: {code}")
    time.sleep(2.0)
    code, fsm_id = get_fsm_id(client)
    print(f"Nový režim: {describe(fsm_id)}, return code {code}")
