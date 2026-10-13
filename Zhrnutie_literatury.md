## Zhrnutie literatúry

### [1] GR00T N1: An Open Foundation Model for Generalist Humanoid Robots (Björck et al., NVIDIA, 2025)
https://arxiv.org/abs/2503.14734

- Otvorený základný (foundation) **VLA model pre humanoidné roboty** od NVIDIE.
- Má **dvojsystémovú architektúru** inšpirovanú ľudským myslením:
  - **System 2 (pomalý, „premýšľajúci“):** vision-language model, ktorý z obrazu a textovej inštrukcie pochopí situáciu a úlohu.
  - **System 1 (rýchly, „reflexný“):** diffusion transformer, ktorý v reálnom čase generuje plynulé motorické akcie.
  - Oba systémy sú prepojené a trénované spoločne (end-to-end).
- Trénovaný na zmesi **záznamov z reálnych robotov, videí ľudí a syntetických (simulovaných) dát**.
- Prekonal vtedajšie metódy učenia imitáciou v simuláciách na viacerých typoch robotov. Na humanoidovi Fourier GR-1 zvládol manipuláciu oboma rukami podľa jazykových inštrukcií a potreboval na to málo dát.
- **Význam pre moju prácu:** Je to hlavný kandidát na model, ktorý budem dolaďovať. Pôvodne je zameraný skôr na manipuláciu rukami, preto je úlohou mojej práce prispôsobiť ho na **navigáciu (chôdzu) podľa textu** na robotovi G1.

### [2] FocusNav: Spatial Selective Attention with Waypoint Guidance for Humanoid Local Navigation (Zhang et al., 2026)
https://arxiv.org/abs/2601.12790

- Rieši **lokálnu navigáciu humanoidov** v neštruktúrovanom a meniacom sa prostredí. Robot musí zároveň smerovať k cieľu a nespadnúť.
- Využíva **selektívnu priestorovú pozornosť (attention)**, teda robot „sa pozerá“ hlavne na to, čo je pre neho práve dôležité. Má dve časti:
  - **Waypoint-Guided Spatial Cross-Attention (WGSCA):** Model predpovedá sériu bezkolíznych prechodových bodov (waypointov) a sústreďuje vnímanie prostredia pozdĺž tejto plánovanej trasy.
  - **Stability-Aware Selective Gating (SASG):** Keď robot zistí, že je nestabilný, potlačí informácie zo vzdialeného okolia a sústredí sa na bezpečné miesta na došľap tesne pred sebou.
- Testované na **robotovi Unitree G1**, teda na rovnakom robotovi, aký používam ja. Oproti porovnávaným metódam dosiahlo vyššiu úspešnosť navigácie, lepšie vyhýbanie sa prekážkam a stabilnejší pohyb.
- **Význam pre moju prácu:** Ukazuje, ako robiť nekolíznu navigáciu priamo na G1. Myšlienka waypointov sa hodí na prepojenie textového popisu trasy s konkrétnymi bodmi, kam má robot ísť.

### [3] ViNT: A Foundation Model for Visual Navigation (Shah et al., CoRL 2023)
https://proceedings.mlr.press/v229/shah23a.html

- **Visual Navigation Transformer**, teda základný model špeciálne pre **vizuálnu navigáciu robotov** podľa kamery.
- Trénovaný na **stovkách hodín navigačných dát z rôznych robotov** so všeobecným cieľom „dostať sa k zadanému cieľu“ (goal-reaching). Preto funguje lepšie než modely trénované len na jednu konkrétnu úlohu.
- Ciele sú reprezentované ako **tokeny**. Vymenením goal encodera, čo je technika podobná prompt-tuningu, sa model dá rýchlo prispôsobiť na **iné typy zadaní**, napríklad GPS body alebo **slovné pokyny typu „odboč doľava“**.
- S návrhmi cieľov generovanými difúznym modelom vie skúmať nové prostredia a v kombinácii s heuristikami zvládne aj navigáciu na vzdialenosť kilometrov.
- **Význam pre moju prácu:** Dokazuje, že veľký predtrénovaný navigačný model sa dá s malým množstvom dát prispôsobiť na nové prostredie aj na nový typ zadania, napríklad text. To je presne princíp, na ktorom stojí moja práca.

### Ako literatúra do seba zapadá

- **GR00T N1** je *model*: všeobecný VLA model pre humanoidy, ktorý sa bude dolaďovať.
- **ViNT** je *princíp*: predtrénovaný navigačný model sa dá lacno prispôsobiť na nové prostredie a nový typ cieľa.
- **FocusNav** je *bezpečnosť na G1*: ukazuje, ako na rovnakom robotovi dosiahnuť nekolízny a stabilný pohyb.