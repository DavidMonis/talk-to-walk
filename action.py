#!/usr/bin/env python3

import sys

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient


INTERFACE = "eth0"

ACTIONS = {
    99: "release_arm",
    1: "turn_back_wave",
    11: "blow_kiss_with_both_hands",
    12: "blow_kiss_with_left_hand",
    13: "blow_kiss_with_right_hand",
    15: "both_hands_up",
    17: "clamp",
    18: "high_five",
    19: "hug",
    20: "make_heart_with_both_hands",
    21: "make_heart_with_right_hand",
    22: "refuse",
    23: "right_hand_up",
    24: "ultraman_ray",
    25: "wave_under_head",
    26: "wave_above_head",
    27: "shake_hand",
    28: "box_left_hand_win",
    29: "box_right_hand_win",
    30: "box_both_hand_win",
    33: "right_hand_on_heart",
    34: "both_hands_up_deviate_right",
    36: "forward_push",
}


def print_usage():
    print("Usage:")
    print("  python3 action.py <action_id>")
    print()
    print("Available actions:")
    for action_id, name in ACTIONS.items():
        print(f"  {action_id:2}  {name}")


if len(sys.argv) != 2:
    print_usage()
    sys.exit(1)

try:
    action_id = int(sys.argv[1])
except ValueError:
    print("Error: action ID must be an integer.")
    print_usage()
    sys.exit(1)

if action_id not in ACTIONS:
    print(f"Error: unknown action ID: {action_id}")
    print_usage()
    sys.exit(1)

action_name = ACTIONS[action_id]

print(f"Action: {action_name} (ID {action_id})")
print(f"Interface: {INTERFACE}")
print("Initializing DDS...")

ChannelFactoryInitialize(0, INTERFACE)

client = G1ArmActionClient()
client.SetTimeout(10.0)
client.Init()

print(f"Executing '{action_name}'...")

result = client.ExecuteAction(action_id)

print("Return code:", result)
