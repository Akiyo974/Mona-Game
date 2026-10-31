# Badge: controller + second screen

The **Controller** app for the GitHub Universe '26 badge (**GitHub Badger 2350**: RP2350, 320×240 colour screen, MonaOS, MicroPython). It drives Fort Mason Octodex over USB serial and, once the game says hello, shows the game on the badge screen. The protocol is in [docs/BADGE_PROTOCOL.md](../docs/BADGE_PROTOCOL.md).

- `controller/__init__.py`: the app, replacing `/system/apps/controller/__init__.py` on the badge (its README and icon are unchanged).
- `original/`: the Controller app as it was on the badge before this change.

## What it does

- Every press and release of Up, Down, Left, Right, Select and Back is still printed as `+up` / `-up` (and so on), exactly like the original app.
- At startup, and whenever it reads the line `?`, it prints `hello display 1`.
- It reads the game's JSON lines without blocking the button loop, keeps only the latest message, and keeps the `map` apart.
- Screens: title (dancing Mona on a starry sky), world (textured mini-map with shores, roofs, trees and paths; the player as a pulsing red cross, the remaining Octocats as twinkling yellow dots; area, team level and an Octodex progress bar), Octodex (found and missing Octocats as a grid), pick menu (numbered cards) and battle (cards with type badges, HP bars that drain smoothly, the 4 moves with type, power / accuracy and SUPER / weak badges, or the turn message in a dialog box with Mona).
- Mona's animations come from the Merge Conflict app on the badge (`/system/apps/merge_conflict/mona-*.png`); without it the screens still work, just without Mona.
- Until the game sends something to draw, the original Controller screen is shown.

## Buttons

| Screen | Button | Sends |
| --- | --- | --- |
| everywhere | any button | `+x` / `-x` as before |
| battle, choosing a move | Up / Down | moves the highlight over the 4 moves |
| battle, choosing a move | Select | `move N` |
| battle, choosing a move | Left | `switch` (when switching is possible) |
| battle, choosing a move | Right | `run` |
| pick menu | Up / Down | moves the highlight |
| pick menu | Select | `pick N` |
| anywhere | Home | leaves the app |

`move N` / `pick N` is printed before `+select`, so the game acts on the badge's choice.

## Install

`/system` on the badge is read-only over the serial console. Copy the app over the badge's USB drive instead:

```bash
pip install mpremote
```

```bash
mpremote exec "import powman; powman.reset_into_msc()"
```

A `BADGER` drive appears: its root is the badge's `/system`. Copy `badge/controller/__init__.py` to `<drive>:\apps\controller\__init__.py`, eject the drive, then reboot the badge:

```bash
mpremote reset
```

## Use

1. Close Thonny and anything else holding the badge's serial port.
2. Open **Controller** on the badge.
3. Open the game in Chrome or Edge and click **Connect badge**. The button reads **Badge: controller + screen**.
