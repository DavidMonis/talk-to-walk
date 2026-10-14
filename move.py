#!/usr/bin/env python3
# Pohyb G1 cez LocoClient.Move(vx, vy, vyaw): typ pohybu + hodnoty ako argumenty.
# Spúšťa sa na Jetsone robota (cez SSH). Robot musí byť v režime chôdze.
# Ctrl+C robota kedykoľvek zastaví (Move(0, 0, 0), nikdy Damp()).
#
# Použitie:
#   python3 move.py stop
#   python3 move.py forward 0.2 -t 2       # dopredu 0.2 m/s počas 2 s (záporné = dozadu)
#   python3 move.py strafe 0.15 -t 2       # do strany, + = doľava
#   python3 move.py turn 0.3 -t 2          # otočenie, + = doľava (proti smeru hodín)
#   python3 move.py vel 0.2 0 0.2 -t 3     # ľubovoľný vektor (vx, vy, vyaw)
#   python3 move.py teleop                 # klávesnica, robot ide len kým držíš kláves
#   python3 move.py forward 0.2 --dry-run  # bez robota, len vypíše príkazy
#   python3 move.py teleop --log run1.csv  # zapíše čas a príkazy do CSV (podklad pre dataset)

import argparse
import csv
import select
import sys
import termios
import time
import tty

# Bezpečnostné limity (absolútne hodnoty). Zvyšuj až po kalibrácii s loco_test.py.
MAX_VX = 0.4     # m/s
MAX_VY = 0.3     # m/s
MAX_VYAW = 0.6   # rad/s
MAX_DURATION = 10.0  # s

# Teleop: kláves -> (vx, vy, vyaw)
TELEOP_KEYS = {
    "w": (0.2, 0.0, 0.0),
    "s": (-0.15, 0.0, 0.0),
    "a": (0.0, 0.15, 0.0),
    "d": (0.0, -0.15, 0.0),
    "q": (0.0, 0.0, 0.4),
    "e": (0.0, 0.0, -0.4),
}
DEADMAN_TIMEOUT = 0.6  # s bez stlačeného klávesu -> stop


def clamp(value, limit):
    return max(-limit, min(limit, value))


class Robot:
    """Obal okolo LocoClient. V --dry-run režime iba vypisuje príkazy."""

    def __init__(self, iface, dry_run, log_path=None):
        self.dry_run = dry_run
        self.client = None
        self.log_file = None
        self.log = None
        self.t0 = time.time()
        self.last = None

        if log_path:
            self.log_file = open(log_path, "w", newline="")
            self.log = csv.writer(self.log_file)
            self.log.writerow(["t", "vx", "vy", "vyaw"])

        if dry_run:
            print("[dry-run] robot sa nehýbe")
            return

        from unitree_sdk2py.core.channel import ChannelFactoryInitialize
        from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient

        print(f"Interface: {iface}")
        print("Initializing DDS...")
        ChannelFactoryInitialize(0, iface)
        self.client = LocoClient()
        self.client.SetTimeout(10.0)
        self.client.Init()

    def move(self, vx, vy, vyaw):
        vx, vy, vyaw = clamp(vx, MAX_VX), clamp(vy, MAX_VY), clamp(vyaw, MAX_VYAW)
        cmd = (round(vx, 3), round(vy, 3), round(vyaw, 3))
        if self.log:
            self.log.writerow([round(time.time() - self.t0, 3), *cmd])
        if cmd != self.last:  # vypisuj len zmeny, nie každý tick
            print(f"  Move(vx={cmd[0]}, vy={cmd[1]}, vyaw={cmd[2]})")
            self.last = cmd
        if self.client:
            self.client.Move(*cmd)

    def stop(self):
        self.move(0.0, 0.0, 0.0)

    def close(self):
        self.stop()
        if self.log_file:
            self.log_file.close()


def hold(robot, vx, vy, vyaw, duration, rate):
    end = time.time() + duration
    while time.time() < end:
        robot.move(vx, vy, vyaw)
        time.sleep(1 / rate)
    robot.stop()


def teleop(robot, rate):
    print("Teleop: drž w/s dopredu/dozadu, a/d do strán, q/e otočenie, medzera stop, x koniec")
    old = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    target = (0.0, 0.0, 0.0)
    last_key = 0.0
    try:
        while True:
            ready, _, _ = select.select([sys.stdin], [], [], 1 / rate)
            if ready:
                key = sys.stdin.read(1).lower()
                if key == "x":
                    break
                if key == " ":
                    target = (0.0, 0.0, 0.0)
                elif key in TELEOP_KEYS:
                    target = TELEOP_KEYS[key]
                last_key = time.time()
            if time.time() - last_key > DEADMAN_TIMEOUT:
                target = (0.0, 0.0, 0.0)
            robot.move(*target)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)


def main():
    p = argparse.ArgumentParser(description="Pohyb Unitree G1 cez LocoClient.Move")
    p.add_argument("mode", choices=["stop", "forward", "strafe", "turn", "vel", "teleop"])
    p.add_argument("values", nargs="*", type=float,
                   help="forward/strafe/turn: 1 hodnota, vel: vx vy vyaw")
    p.add_argument("-t", "--duration", type=float, default=2.0, help="trvanie v s (default 2)")
    p.add_argument("--iface", default="eth0", help="sieťové rozhranie (over cez `ip a`)")
    p.add_argument("--rate", type=float, default=10.0, help="frekvencia posielania Move v Hz")
    p.add_argument("--dry-run", action="store_true", help="bez robota, len vypíše príkazy")
    p.add_argument("--log", help="CSV súbor na záznam príkazov")
    args = p.parse_args()

    expected = {"stop": 0, "teleop": 0, "forward": 1, "strafe": 1, "turn": 1, "vel": 3}
    if len(args.values) != expected[args.mode]:
        p.error(f"'{args.mode}' čaká {expected[args.mode]} hodnot(y), dostal {len(args.values)}")
    if not 0 < args.duration <= MAX_DURATION:
        p.error(f"--duration musí byť v (0, {MAX_DURATION}] s")

    v = args.values
    vector = {
        "forward": lambda: (v[0], 0.0, 0.0),
        "strafe": lambda: (0.0, v[0], 0.0),
        "turn": lambda: (0.0, 0.0, v[0]),
        "vel": lambda: (v[0], v[1], v[2]),
    }

    robot = Robot(args.iface, args.dry_run, args.log)
    try:
        if args.mode == "stop":
            robot.stop()
        elif args.mode == "teleop":
            print("WARNING: Uisti sa, že okolo robota nie sú prekážky.")
            teleop(robot, args.rate)
        else:
            vx, vy, vyaw = vector[args.mode]()
            print(f"{args.mode}: vx={vx}, vy={vy}, vyaw={vyaw}, {args.duration} s "
                  f"(limity {MAX_VX}/{MAX_VY}/{MAX_VYAW})")
            hold(robot, vx, vy, vyaw, args.duration, args.rate)
        print("Hotovo.")
    except KeyboardInterrupt:
        print("\nCtrl+C -> stop")
    finally:
        robot.close()  # Move(0, 0, 0); nevolaj Damp(), stojaci robot by spadol


if __name__ == "__main__":
    main()
