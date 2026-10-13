# TalkToWalk: kontext projektu

Bakalárska práca Dávida Moniša (FMFI UK, vedúci RNDr. Andrej Lúčny, PhD.): doladiť VLA model tak, aby humanoid Unitree G1 prešiel trasu opísanú textom („choď rovno, na ďalšej križovatke doprava") len podľa kamery a bez kolízií. Oficiálne zadanie je v `zadanie-zp_216141.pdf`. Text na webe (vetva `web`) je pracovný návrh, nie záväzné zadanie.

Komunikácia s autorom prebieha po slovensky.

## Robot

- **Model:** Unitree G1 EDU s robotickou rukou (presný typ ruky, napr. Dex3-1 alebo Inspire, ešte doplniť).
- **Pripojenie:** cez SSH na palubný počítač robota. IP adresa a heslo sa do repozitára **nezapisujú** (repozitár je verejný).
- **Palubné počítače:**
  - Jetson Orin NX 16 GB (podľa špecifikácie EDU verzie; overiť `cat /etc/nv_tegra_release; free -h`). Používateľ `unitree`, pracovný adresár `/home/unitree/monis4`.
  - Druhý počítač riadi chôdzu a rovnováhu, je uzavretý.
- **Senzory:**
  - Intel RealSense D435i v hlave. Na Jetsone je RGB stream `/dev/video6`, `/dev/video2` je IR stream (s bodkami z projektora, na model nepoužívať).
  - Livox MID-360 LiDAR v hlave.
- **Ovládanie z Pythonu (`unitree_sdk2py`):**
  - Chôdza: `unitree_sdk2py.g1.loco.g1_loco_client.LocoClient`, `Move(vx, vy, vyaw)`. Zastavenie cez `Move(0, 0, 0)`, nie `Damp()` (stojaci robot by spadol).
  - Gestá rúk: `G1ArmActionClient.ExecuteAction(id)` (pozri `action.py` a `G1_available_actions_formatted.txt`).
  - Inicializácia: `ChannelFactoryInitialize(0, "<sieťové rozhranie>")`.

## Ďalší hardvér

- Školské PC s GPU 24 GB VRAM: Isaac Sim/Isaac Lab (verzie zladiť s `unitree_rl_lab`, aktuálne Isaac Sim 5.1 + Isaac Lab 2.3). GR00T mať v samostatnom conda prostredí.

## Súbory v repozitári

- `action.py`: spustenie gesta rúk podľa ID.
- `snapshot.py`: na Jetsone prejde `/dev/video0` až `/dev/video7` a uloží snímku z každej kamery.
- `stream.py`: MJPEG stream kamery `/dev/video6` cez HTTP na porte 8080.
- `snapshot_video2.jpg`, `snapshot_video6.jpg`: ukážkové snímky (IR a RGB).
- `Zhrnutie_literatury.md`: zhrnutie troch kľúčových článkov (GR00T N1, FocusNav, ViNT).

## Aktuálny smer (október 2026, nie je definitívny)

- Základný model: GR00T N1.7 (najnovšia verzia v NVIDIA/Isaac-GR00T).
- Hotový model dostáva len kameru (RGB, prípadne hĺbku z D435i) a text aktuálneho príkazu. LiDAR slúži ako učiteľ (odmeny, automatické štítky križovatiek) a ako nezávislá bezpečnostná brzda, nie ako vstup modelu.
- Fáza 1: RL učiteľ v Isaac Lab (LiDAR + príkaz → rýchlosti), destilácia do GR00T N1.7 (kamera + text) cez SFT a DAgger. Ďalšia výstupná hlava rozpoznáva križovatku.
- Fáza 2: postupnosti príkazov (ukazovateľ na aktuálny príkaz sa posúva pri výstupe z križovatky), reálne dáta a opravy od človeka.
- Inferencia: vývoj cez server–klient s externou GPU; beh priamo na Jetsone ako samostatný experiment.
