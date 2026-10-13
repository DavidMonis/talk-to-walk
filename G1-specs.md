# Unitree G1: špecifikácia a nastavenie

Robot, na ktorom beží projekt TalkToWalk.

## Robot

- **Model:** Unitree G1 EDU s robotickými rukami Inspire (výrobca Inspire Robots).
- **Pripojenie:** cez SSH na palubný počítač robota. IP adresa a heslo sa do repozitára **nezapisujú** (repozitár je verejný).

## Palubné počítače

- **Jetson Orin NX 16 GB** (podľa špecifikácie EDU verzie; overiť `cat /etc/nv_tegra_release; free -h`). Používateľ `unitree`, pracovný adresár `/home/unitree/monis4`.
- **Riadenie chôdze:** druhý počítač drží rovnováhu a chôdzu, je uzavretý.

## Senzory

- **Intel RealSense D435i** v hlave. Na Jetsone je RGB stream `/dev/video6`, `/dev/video2` je IR stream (s bodkami z projektora, na model nepoužívať).
- **Livox MID-360** LiDAR v hlave.

## Ovládanie z Pythonu (`unitree_sdk2py`)

- **Inicializácia:** `ChannelFactoryInitialize(0, "<sieťové rozhranie>")`.
- **Chôdza:** `unitree_sdk2py.g1.loco.g1_loco_client.LocoClient`, `Move(vx, vy, vyaw)`. Zastavenie cez `Move(0, 0, 0)`, nie `Damp()` (stojaci robot by spadol).
- **Gestá rúk:** `G1ArmActionClient.ExecuteAction(id)`, pozri `action.py` a `G1_available_actions_formatted.txt`.

## Skripty pre robota

- `action.py`: spustenie gesta rúk podľa ID.
- `snapshot.py`: na Jetsone prejde `/dev/video0` až `/dev/video7` a uloží snímku z každej kamery.
- `stream.py`: MJPEG stream kamery `/dev/video6` cez HTTP na porte 8080.
- `snapshot_video2.jpg`, `snapshot_video6.jpg`: ukážkové snímky (IR a RGB).

## Ďalší hardvér

- **Školské PC s GPU 24 GB VRAM:** Isaac Sim/Isaac Lab (verzie zladiť s `unitree_rl_lab`, aktuálne Isaac Sim 5.1 + Isaac Lab 2.3). GR00T mať v samostatnom conda prostredí.
