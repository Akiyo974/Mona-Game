# Contributing to Fort Mason Octodex

Thanks for wanting to help! This game was built during the GitHub Day of Learning workshop, and contributions of any size are welcome: a new Octocat, a new move, a fix, or a better sentence in the README.

## Where things are

The whole game is one file: [`.github/extensions/monas-octoverse-arcade-starter/game.html`](.github/extensions/monas-octoverse-arcade-starter/game.html). It is plain HTML, CSS and JavaScript, with no build step and no external assets.

| What | Where in `game.html` |
| --- | --- |
| The twelve Octocats and where they hide | `const OCTOCATS = [...]` |
| Types and the type chart | `const TYPES` and `const STRONG` |
| Battle moves | `const MOVES = {...}` |
| Each Octocat's type, stats and four moves | `const KITS = {...}` |
| How each Octocat is drawn | `OCTOCAT_STYLES` and `drawOctocat()` |
| Items (Hotfix, Revert) | `useItem()` and `collect()` |
| The Merge Conflict boss | `const BOSS`, `drawConflict()` and the `battle.boss` checks |
| Trainers | `const TRAINERS` and `beatTrainer()` |
| Building interiors and the people inside | `const ROOMS` (one room per entry of `BUILDINGS`, same order), `drawItem()` for furniture, `tryTalk()` for dialogue |
| The bus and GitHub HQ | `BUS_STOP`, `rideBus()` and `renderBus()`; `HQ_STREET` and `HQ` are tile-grid rooms (`hqGrid()` builds the floor plan, `HQ_ART` draws the furniture) |
| Shiny Octocats | `SHINY_RATE` and `drawCat()` |
| Achievements | `const ACHIEVEMENTS` and `unlock()` |
| Settings and key bindings | `KEY_ACTIONS`, `applySettings()` and `refreshKeyLabels()` |
| Saving | `save()` and `loadSave()` (progress), `saveMeta()` (achievements, best time) |
| Installable app and offline play | [`pwa/`](pwa/) (manifest, icons, service worker), copied next to the page by the Pages workflow |
| Badger badge | [`badge/`](badge/README.md) and [`docs/BADGE_PROTOCOL.md`](docs/BADGE_PROTOCOL.md) |

## Run it locally

Open `game.html` in a browser. That's it. To test on a phone on the same network, serve the folder, for example:

```bash
python -m http.server 8000 --directory .github/extensions/monas-octoverse-arcade-starter
```

then open `http://<your computer's IP>:8000/game.html` on the phone.

## Making a change

1. Fork the repository and create a branch.
2. Make your change in `game.html` and play it: title screen, a catch, a battle and the Octodex should still work. If you touch controls, try the keyboard and, if you can, a phone.
3. Keep the code style of the file: small functions, short comments that say why, no new libraries.
4. Open a pull request that says what changed and, if it is visual, includes a screenshot.

## Rules for the Badger badge

The game and the badge app talk through the protocol in [`docs/BADGE_PROTOCOL.md`](docs/BADGE_PROTOCOL.md). Both sides must match, so please open an issue before changing it. The badge app is MicroPython and may only use what is already on the badge.

## Good first issues

Look for the [`good first issue`](https://github.com/Akiyo974/Mona-Game/labels/good%20first%20issue) label. Each one explains which part of `game.html` to edit.

## Be kind

Be welcoming and patient with each other. We are all here to learn.
