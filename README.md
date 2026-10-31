# Mona's Octoverse Arcade: Fort Mason Octodex

**A GitHub-themed monster-collector adventure set in San Francisco's Fort Mason, built as a Copilot App canvas extension.**

Explore Fort Mason, find the twelve Octocats hidden around the piers, the Great Meadow and the hill, and win turn-based battles with Git, Code, Ops and Security moves (Commit Strike, Pull Request Punch, Force Push, Secret Scan…) to fill your Octodex.

▶ **Play in the browser:** https://akiyo974.github.io/Mona-Game/
(published by GitHub Pages from `main`; see [Publish on GitHub Pages](#publish-on-github-pages))

![Title screen](docs/screenshots/after-title.png)

## Team

Built during the GitHub Day of Learning workshop by:

- Christen Dijoux ([@Akiyo974](https://github.com/Akiyo974))
- Chanrattnak Mong
- Brett Post
- Don Ebben
- Luke Vandekieft

## Highlights

**San Francisco & Fort Mason**
- A stylised map of Fort Mason: Piers 1-3, the Bay Promenade, Fort Mason Center, Herbst Pavilion, the Great Meadow, Fort Mason Hill, Gashouse Cove and Laguna Street.
- Alcatraz in the bay with a rotating lighthouse beam, a Laguna Street cable car, sailboats, seagulls and Karl the Fog rolling over the water.
- Battles take place in front of the Golden Gate Bridge, Alcatraz and the SF skyline (Transamerica Pyramid, Coit Tower).

**GitHub**
- Twelve hand-drawn Octodex-style Octocats: Octocat, Mona, Dinotocat, Daftpunkcat, Jetpacktocat, Spidertocat, Scottocat, Heisencat, Privateer, Nyantocat, Chellocat and Defunktocat.
- "GitHub Universe" signage on Fort Mason Center, where GitHub Universe is held.
- Contribution-graph flower beds on the Great Meadow, GitHub colours throughout and Git-themed battle moves.

**Gameplay & polish**
- Title screen, location banners, minimap and "!" alerts when a wild Octocat is near.
- Your first Octocat is free; after that, pick one of yours and battle to catch the next.
- Battle intro transition, animated HP bars, screen shake, particles, damage numbers and typewriter dialogue.

**Battle system**
- Four GitHub types with a rock-paper-scissors chart: **Code** beats **Ops**, **Ops** beats **Security**, **Security** beats **Code**; **Git** is neutral.
- Every Octocat has its own type, base stats (HP, Attack, Defense, Speed) and four signature moves.
- 14 moves with power, accuracy, same-type bonus, critical hits and effects: Rebase Rush always strikes first, Refactor heals, Copilot Assist raises Attack, Code Review lowers Defense, Fork Bomb hits hard but often fails.
- Speed decides who moves first, the wild Octocat picks its moves to exploit your weaknesses, and move buttons flag super-effective (▲) and weak (▼) choices.
- Switch Octocats mid-battle (the foe gets a free hit), keep fighting when one faints, and if your whole team faints you rest back at the Bay Promenade.
- Win and an Octodex orb wobbles three times… Gotcha! Each catch levels up your whole team.
- An Octodex with numbered entries and silhouettes for Octocats you have not found yet.
- An 8-bit chiptune soundtrack (overworld + battle) and sound effects, all synthesised with Web Audio.
- Keyboard, gamepad, and the Badger badge over USB serial.

![The twelve Octocats](docs/screenshots/octocats.png)

## Before and after

| | Before | After |
| --- | --- | --- |
| **Start** | ![Workshop starter](docs/screenshots/before-starter.png) | ![Title screen](docs/screenshots/after-title.png) |
| **World** | ![Original map](docs/screenshots/before-world.png) | ![New map](docs/screenshots/after-world.png) |
| **Battle** | ![Original battle](docs/screenshots/before-battle.png) | ![New battle](docs/screenshots/after-battle.png) |
| **Octodex** | ![Original Octodex](docs/screenshots/before-octodex.png) | ![New Octodex](docs/screenshots/after-octodex.png) |

### More of San Francisco

| Alcatraz & the bay | GitHub Universe at Fort Mason Center |
| --- | --- |
| ![Alcatraz](docs/screenshots/after-alcatraz.png) | ![GitHub Universe signage](docs/screenshots/after-universe.png) |
| **Contribution-graph flower beds** | **Battle: damage, types and effects** |
| ![Great Meadow](docs/screenshots/after-meadow.png) | ![Battle attack](docs/screenshots/after-attack.png) |

## Controls

| Action | Keyboard | Gamepad | Badger badge |
| --- | --- | --- | --- |
| Start | <kbd>Enter</kbd> / <kbd>Space</kbd> | A / Start | select |
| Move | <kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> or arrows | D-pad / left stick | arrows |
| Pick a move in battle | <kbd>1</kbd>–<kbd>4</kbd> (or <kbd>F</kbd> for the first) | D-pad + A | arrows + select |
| Switch Octocat | <kbd>S</kbd> | D-pad + A | arrows + select |
| Run from battle | <kbd>Esc</kbd> | B | back |
| Octodex | <kbd>I</kbd> | Y / A | back closes |
| Music on/off | <kbd>M</kbd> | | |

Music starts on your first key press or click. The badge connects with the **Connect badge** button (Web Serial, Chrome or Edge only).

## Bonus: Badger mode

The GitHub Universe '26 badge (GitHub Badger 2350) becomes a controller **and a second screen** for the game, over USB serial with MicroPython.

| World: live mini-map | Battle |
| --- | --- |
| ![Badge showing the mini-map](media/badge-photo-map.jpg) | ![Badge showing a battle](media/badge-photo-battle.jpg) |

- **Controller:** every press and release of the badge's arrows, Select and Back drives the game, like a gamepad.
- **Second screen:** the badge shows the title screen, a live mini-map (your position and the Octocats left, area, team level, Octodex progress), the Octodex, the pick menus and the battles (both HP bars, your four moves with type, power, accuracy and SUPER / weak, or the turn message).
- **Play from the badge:** in battle, Up / Down choose a move, Select uses it, Left switches Octocat and Right runs; in a pick menu, Up / Down and Select pick an Octocat.

To set it up, install the Controller app from [`badge/`](badge/README.md) on the badge, open **Controller**, then click **Connect badge** in the game (Chrome or Edge). The button reads **Badge: controller + screen**. A badge app without a screen keeps working as a plain controller. The messages between the game and the badge are described in the [badge protocol](docs/BADGE_PROTOCOL.md).

## Trailer

[![Fort Mason Octodex trailer](media/trailer-thumbnail-1280.jpg)](media/fort-mason-octodex-trailer.mp4)

A 54-second trailer recorded from the game, with its own music, ending on Badger mode: [watch it](media/fort-mason-octodex-trailer.mp4).

## Run it

**In the Copilot App (canvas extension).** Open this repository as a Project in the GitHub Copilot app and ask:

> Open the Mona's Octoverse Arcade starter canvas.

The extension lives in `.github/extensions/monas-octoverse-arcade-starter/`: `extension.mjs` registers the canvas and serves `game.html`, which contains the whole game (HTML, CSS and vanilla JavaScript, no build step, no external assets).

**Locally.** Open `.github/extensions/monas-octoverse-arcade-starter/game.html` directly in a browser.

## Publish on GitHub Pages

The workflow `.github/workflows/pages.yml` publishes `game.html` as the site's `index.html` on every push to `main` that touches the game, and can also be run manually from the **Actions** tab.

One-time setup:
1. Go to **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Push to `main` or run the **Deploy game to GitHub Pages** workflow. The game will be at https://akiyo974.github.io/Mona-Game/.

On a free plan, GitHub Pages requires the repository to be public.

---

# Workshop challenge guide

The rest of this README is the original Day of Learning Challenge guide that this project was built for.

**GitHub Day of Learning | 2-hour workshop game challenge | Canvas Extension Edition**

Build **Mona's Octoverse Arcade**: a browser game starring Mona the Octocat as
the hero and Copilot as the sidekick. Ship it as a **Copilot App canvas
extension** that installs and opens inside the Copilot App. Every team starts
from the same prompt, then makes the game its own.

This repository is the shared starter and challenge guide. Your GitHub
Hands-on Labs environment already provides your team's repository based on
this template; use that repository rather than creating another one.
It includes a minimal, working Copilot App canvas extension starter, not a
finished game. Start from it, confirm the canvas opens, then build your game
in the starter's `game.html`.

**Workshop links:** [Attendee instructions](https://gh.io/dol-instructions) |
[Discussion and submissions](https://gh.io/dol-discussion).
This README is the source of truth for the shared prompt and challenge rules;
the attendee website and Discussion follow the same guidance.

## Prerequisites, login, and add project to the Copilot app

1. **Install the GitHub Copilot app.** Download and install it from
   [github.com/features/copilot](https://github.com/features/copilot).
2. **Log in with your provided lab account.** Open the GitHub Copilot app
   and sign in using the **GitHub Hands-on Labs** account provided to you.
   Use that account, rather than your personal GitHub account, throughout
   the workshop. As part of the GitHub Hands-on Labs environment, a
   repository is already set up for your team, ready to add as a Project.

> [!NOTE]
> All team members should be able to log in with the one account
> provided to work on the repository, or you can have one teammate make
> the changes.

3. **Add your team's repository as a Project in the GitHub Copilot app.**
   In the app's sidebar, open **Projects** and create a new **Project**
   named for your team. In the repository picker, select the repository
   already set up in your GitHub Hands-on Labs environment, not the original
   `ghlearn/day-of-learning-challenge` template. Let the Project prepare the
   repository and wait for its reply that it is ready.

   In the **Project** chat, ask Copilot to start a coding session in your
   team's repository and open the **Mona's Octoverse Arcade starter** canvas.
   Confirm its welcome screen appears and its button responds before building.
   The project-scoped extension is already in the repository; you do not need
   a separate starter download.

Commit and push your team's extension changes so the submitted repository
contains the version shown in your demo.

**Challenge topics:** [Prompt](#prompt) | [Teams](#teams) |
[Canvas extension](#canvas-extension) | [Agenda](#agenda) |
[Submit](#submit) | [Judging](#judging) | [Awards](#awards) |
[Principles](#principles)

## Prompt

Every team starts with this prompt in the Copilot App. It sets the baseline,
not the limit.

```text
In the Mona's Octoverse Arcade starter canvas already included
in your team's challenge repository, build the game described here.

Keep the existing extension registration in extension.mjs;
implement the game in game.html with HTML, CSS, and vanilla
JavaScript, with no external build step.

Make a game where Mona the Octocat collects green commit-squares
while dodging red bugs. Track the score, increase speed over
time, and show a game-over screen with a restart button.

Copilot appears as a sidekick that gives an encouraging tip
every 10 points. Make sure the canvas still opens and the game
is playable.
```

**The baseline**

- Mona collects green commit squares and dodges red bugs.
- The score is tracked, and the speed increases over time.
- A game-over screen has a restart button.
- Copilot cheers you on with a tip every 10 points.

**Make it yours**

- **Rethink the world:** levels, settings, and a story that make Mona's arcade
  feel like yours.
- **Invent power-ups:** shields, magnets, merge combos, or boss bugs.
- **Give Copilot personality:** make the sidekick funny, helpful, or full of
  surprises.
- **Find your style:** art direction, animation, and sound that make people
  want to keep playing.

## Teams

Up to 150 people may take part. Plan attendance in multiples of 6 so everyone
can join a complete team.

- **Exactly 6 people per team:** no smaller or larger teams.
- **Choose a team name** during kickoff. Use it on your submission.
- **One shared repository:** keep your team's extension in one repository
  that judges can open.

With 150 participants, form 25 teams of 6, for 25 team submissions. If your
group has fewer than 6 people, join another group. If it has more than 6,
split into teams of exactly 6.

## Canvas extension

Your game cannot be a loose HTML file. It must be a **Copilot App canvas
extension** that:

1. **Lives in its own folder**, with an `extension.mjs` that registers a
   canvas (the game UI).
2. **Can be installed** into the Copilot App via `install_extension` from a
   GitHub gist or repository folder, or by placing the folder in the
   extensions directory.
3. **Runs as a canvas** when the agent opens it with `open_canvas`. The game
   renders in the side panel and is playable.

Start from the **included, known-good canvas starter** in
`.github/extensions/monas-octoverse-arcade-starter/`. Its `extension.mjs`
registers and serves the canvas; `game.html` is the welcome screen and the
place to build your game. Keep these files together. The starter is deliberately
not a playable game: the score, collectibles, bugs, difficulty, and Copilot
tips are yours to implement.

In the Copilot App session opened on your team's repository, ask:

> Open the Mona's Octoverse Arcade starter canvas.

The starter's button confirms that the canvas is interactive. Then paste the
challenge prompt above and build the game in `game.html`. Use HTML, CSS, and
vanilla JavaScript inside the canvas, with **no external build step**. Keep
the game self-contained: do not add a package manifest, dependencies, or
external assets. The starter handles canvas registration and serving so your
team can focus on the game and still learn how the extension fits together.

**Loading is the setup step:** opening your team's repository as a Project
loads the included project-scoped extension. You do not need a separate
starter download or to reinstall it for the demo. The installation options
above are for trying the extension in another environment.

## Agenda

The workshop lasts **2 hours**. All times below are elapsed from the start
of the workshop, not times of day. Install the app and log in before kickoff.

| Time | Phase | What to do |
| --- | --- | --- |
| 0:00-0:15 | Kickoff & teams | See the target canvas extension, get the starter prompt and rubric, form teams of exactly 6, and choose a team name. |
| 0:15-0:25 | Open the starter | Add the pre-provisioned lab repository as a Copilot App Project, open the included starter canvas, and confirm its button responds. |
| 0:25-1:15 | Build your game | Start from the prompt, then build your team's version inside the canvas with the Copilot App. |
| 1:15-1:35 | Power-up | Pick a stretch goal: leaderboard, sound, animation, theming, or your own idea. |
| 1:35-2:00 | Record & submit | Record a demo video of up to 90 seconds and post your submission in the challenge Discussion before the workshop ends. |

## Submit

Before the end of the **two-hour workshop**, one teammate posts your team's
submission as a **single comment in the
[challenge Discussion](https://gh.io/dol-discussion)**. Do not submit in a
separate Discussion in your team's repository.

Include all four items:

1. **Team name:** the name your team chose at kickoff.
2. **Description:** a few sentences about your game, your creative spin, and
   your power-up.
3. **Demo video:** up to **90 seconds**. Show your team's repository open as
   a Project with the included extension loaded, open the canvas, and play
   the game. No separate reinstallation is required. Attach the video to
   your comment or add a link that judges can access.
4. **Repository link:** your team's repository containing the extension
   folder. Make sure judges can access it and that your changes are pushed.

The repository must contain the version shown in your demo. Keep any lab
credentials out of your video and submission.

You can copy this into your submission comment and replace the placeholders:

```markdown
**Team name:** <your team name>

**Description:** <your game, creative spin, and power-up>

**Demo video:** <attach a video or paste an accessible link; up to 90 seconds>

**Repository:** <URL of your team's repository containing the extension folder>
```

## Judging

After the workshop, judges review every submission's demo video and
repository against this **25-point rubric**. They choose all three award
winners and announce them in the challenge Discussion. **There is no
audience vote.**

| Criteria | Points | What judges look for |
| --- | ---: | --- |
| **It works:** installs & runs as a canvas | 8 | Extension installs, canvas opens, game is actually playable. |
| **Fun factor** | 6 | Is it enjoyable? Would you play again? |
| **GitHub theme** | 5 | Creative use of Mona & Copilot as characters. |
| **Polish** | 3 | Visuals, animations, sound, game-over/restart flow. |
| **Wow / stretch** | 3 | A power-up feature that surprised the judges. |
| **Total** | **25** | |

## Awards

The **judges decide** all three categories. Each category winner takes home
**swag**.

| Award | Recognizes |
| --- | --- |
| **Overall Winner** | Best total rubric score across all criteria. |
| **Best Design** | The best-looking, most visually striking game (Polish). |
| **Most Fun** | The game the judges most wanted to keep playing (Fun factor). |

**Award rollover rule:** a team can win more than one category. However, if
the Overall Winner also tops another category, that second award rolls to
the runner-up to spread the recognition.

## Principles

- **Rubric up front:** teams know what is judged before building.
- **Known-good starter:** a working canvas starter makes "install & run"
  achievable for everyone without giving teams a finished game.
- **Reward working software:** "it works" has the highest weight, with 8 of
  25 points for installing and running as a canvas.
- **Shared theme, personal spin:** every team starts from the same prompt
  and builds Mona's Arcade, then makes it its own.

---

> **Note:** This is an independent workshop resource. It is not an official
> GitHub Universe or GitHub event website and is not endorsed by GitHub.
> GitHub, GitHub Copilot, and the Octocat are trademarks of GitHub, Inc.
> Public-facing mascot use requires approval from GitHub's Brand & Marketing
> Design team under the
> [mascot guidelines](https://brand.github.com/graphic-elements/mascots).
