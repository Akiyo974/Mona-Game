# Badge protocol: Fort Mason Octodex ⇄ Badger badge

The game talks to the badge over USB serial (Web Serial, 115200 baud, UTF-8, one message per line ending in `\n`).
The badge is both a **controller** and, optionally, a **second screen**.

## Badge → game

| Line | Meaning |
| --- | --- |
| `+up` / `-up` (also `down`, `left`, `right`, `select`, `back`) | Button pressed / released. `select` acts as A, `back` as B. Already supported by the original Controller app. |
| `hello display 1` | The badge app can draw. Send it at startup **and** every time the badge receives the line `?`. |
| `move 1` … `move 4` | In battle: use that move. On the title screen: start the game. |
| `switch` | In battle: open the switch menu. |
| `run` | In battle: run away, or go back from the switch menu. |
| `pick 1` … `pick 9` | In a "choose an Octocat" menu: pick that entry. |

Unknown lines are ignored.

## Game → badge

1. Right after connecting, the game sends one line: `?`
2. **Nothing else is sent until the badge answers `hello display 1`.** A badge app that never answers keeps working as a plain controller.
3. After the hello, the game sends `{"t":"map",…}` once, then one JSON object per line whenever what should be on screen changes. Identical states are not resent. In the world, updates are sent when the area or the Octodex count changes, and at most every 3 s while walking.

The badge should always draw the **latest** message only. It can skip messages that arrive while it is refreshing.

### `map`: sent once

```json
{"t":"map","w":48,"h":34,"rows":["~~~~…", "…"]}
```

`rows` has `h` strings of `w` characters, `rows[y][x]` is the tile at column x, row y:

| Char | Tile |
| --- | --- |
| `~` | water (San Francisco Bay, Gashouse Cove) |
| `P` | pier / dock |
| `B` | building |
| `=` | path / promenade |
| `#` | street (Laguna St) |
| `T` | tree |
| `.` | grass |

### `title`

```json
{"t":"title"}
```

### `world`

```json
{"t":"world","area":"Bay Promenade","dex":3,"total":12,"lv":15,"me":[23,9],"left":[[7,2],[31,7]]}
```

`me` is the player tile `[x, y]`; `left` are the tiles of the Octocats not caught yet; `lv` is the team level.

### `dex`: Octodex open

```json
{"t":"dex","found":["Octocat","Mona"],"total":12}
```

### `pick`: choose an Octocat (before a battle, or to switch)

```json
{"t":"pick","title":"Choose an Octocat to battle Heisencat","options":["Mona Git Commit Strike","Octocat Git Commit Strike"],"sel":0}
```

`sel` is the highlighted entry (0-based). The badge answers with `pick N` (1-based).

### `battle`

```json
{"t":"battle","busy":false,"msg":"What will Mona do?",
 "me":{"name":"Mona","type":"Git","lv":9,"hp":29,"max":29,"atk":0,"def":0},
 "foe":{"name":"Heisencat","type":"Security","lv":7,"hp":25,"max":25,"atk":0,"def":0},
 "moves":[{"n":"Commit Strike","type":"Git","pow":40,"acc":100,"kind":"atk","eff":1},
          {"n":"Pull Request Punch","type":"Code","pow":60,"acc":95,"kind":"atk","eff":0.5},
          {"n":"Code Review","type":"Security","pow":45,"acc":100,"kind":"atk","eff":1},
          {"n":"Copilot Assist","type":"Git","pow":0,"acc":100,"kind":"buff","eff":1}],
 "sel":0,"canSwitch":true}
```

- `busy: true` means the game is playing a turn and only `msg` matters (e.g. `"Mona used Merge Slam!"`, `"It's super effective!"`).
- `busy: false` means the player must choose: show the 4 moves. The badge answers `move N`.
- `kind` is `atk`, `heal` or `buff`. `eff` is the type multiplier against the foe: `2` super effective, `0.5` not very effective.
- `atk` / `def` are stat stages (-3…+3).
- Types: **Code** beats **Ops**, **Ops** beats **Security**, **Security** beats **Code**, **Git** is neutral.
