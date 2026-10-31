# Prompt for a local Claude Code session (badge side)

Paste the text below into a Claude Code session running **on the computer the badge is plugged into**, opened in your local clone of this repository (after `git pull`).

---

My Badger badge is plugged into this computer over USB. It runs a MicroPython "Controller" app that drives my browser game (`.github/extensions/monas-octoverse-arcade-starter/game.html`, also live at https://akiyo974.github.io/Mona-Game/) over USB serial: it prints `+up` / `-up` style lines (up, down, left, right, select, back) for button presses and releases.

The game now supports using the badge as a **second screen**. The full protocol is in `docs/BADGE_PROTOCOL.md`; read it first, together with the badge section of `game.html` (search for `Badger badge over USB serial`). Your job is the badge side.

1. **Inspect the badge, without changing anything yet.** Make sure nothing else holds the serial port (close Thonny and any browser tab connected to the badge). Use `mpremote` (`pip install mpremote` if needed): `mpremote ls -r`, then `mpremote cat` the Controller app and anything it imports. Identify the badge model and its display API and resolution (e.g. Pimoroni Badger 2040 / 2040 W: `badger2040`, 296×128 1-bit e-ink, buttons A, B, C, UP, DOWN; or a GitHub Universe badge: check its own libraries). Tell me what you found before editing.
2. **Back up first.** Copy every file you will change into `badge/original/` in this repo.
3. **Extend the Controller app**, keeping every existing behaviour and line exactly as it is today:
   - At startup, and every time it receives the line `?` on USB serial (stdin), print `hello display 1`.
   - Read incoming lines **without blocking** the button loop (e.g. `select.poll` on `sys.stdin` with a 0 timeout, or a non-blocking read), parse them as JSON, and keep only the latest message (`map` is stored separately and kept).
   - Draw the latest message, adapting the layout to the real resolution:
     - `title`: "FORT MASON OCTODEX" and "press a button".
     - `world`: a mini-map from the stored `map` (water dark, land light, buildings solid, paths dotted, ~2–3 px per tile), the player as a blinking/crossed marker, remaining Octocats as small dots, plus the area name, `dex`/`total` and team `lv`.
     - `dex`: found names and the count.
     - `pick`: the title and options as a list with `sel` highlighted.
     - `battle`: both names, `Lv`, type and HP bars (with numbers for `me`); if `busy` is false, the 4 moves (name, type, pow/acc or heal/buff, "SUPER" when `eff` is 2, "weak" when `eff` is 0.5) with the selected one highlighted; if `busy` is true, just `msg` in large text.
   - E-ink is slow: redraw only when the latest message differs from what is on screen, use the fastest update speed / partial updates the library offers for battle screens, and never redraw more than about twice per second.
   - **Buttons on the second screen** (keep sending the existing `+x`/`-x` lines too): in a battle with `busy: false`, let UP/DOWN move a local highlight over the 4 moves and A/select send `move N`; add a way to send `switch` and `run` (e.g. B = `switch`, C = `run`, or long presses, whichever fits the badge's buttons); in `pick`, UP/DOWN + A send `pick N`.
4. **Test on the device**: copy the files with `mpremote cp`, reset, open the game in Chrome or Edge, click **Connect badge**. The button must read "Badge: controller + screen". Walk around (mini-map updates when the area changes), then start a battle and choose moves from the badge.
5. **Save it in the repo**: put the final badge files in `badge/` with a short `badge/README.md` (model, how to install with `mpremote`, button mapping), and commit. Don't add my name or any AI attribution to commits.

Constraints: MicroPython only, no new libraries beyond what is on the badge, don't break the existing controller behaviour, and keep the protocol exactly as in `docs/BADGE_PROTOCOL.md` (if you need a change, ask me first, because the game side must match).
