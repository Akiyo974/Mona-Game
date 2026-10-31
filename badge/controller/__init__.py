"""
Controller: the badge as a game pad for a computer, over the USB cable.

Each press and release of ↑ ↓ ← → Select and Back is printed on the serial
port as one line, "+up" when pressed and "-up" when let go. On the computer,
tools/badge_controller.py turns those lines into key presses for any game or
program; your own code can read them too (docs/guides/controller.md).

Presses from the Badger Remote watch arrive here like real ones, so the watch
can drive the computer through the badge. Home leaves the app.

Second screen for Fort Mason Octodex (Mona-Game docs/BADGE_PROTOCOL.md): the
app prints "hello display 1" at startup and whenever it reads the line "?",
then draws the latest JSON message the game sends. In a battle ↑ ↓ choose a
move, Select sends "move N", ← sends "switch" and → sends "run"; in a pick
menu ↑ ↓ choose and Select sends "pick N". The +x / -x lines are always sent.
"""
import json
import select
import sys

import missing_details

badge.mode(HIRES | VSYNC)
screen.antialias = image.X2

WIDTH, HEIGHT = 320, 240
# The name sent for each button: also the keys of tools/badge_controller.py
BUTTONS = (
    (BUTTON_UP, "up"),
    (BUTTON_DOWN, "down"),
    (BUTTON_LEFT, "left"),
    (BUTTON_RIGHT, "right"),
    (BUTTON_SELECT, "select"),
    (BUTTON_BACK, "back"),
)

background = color.rgb(13, 17, 23)
white = color.rgb(230, 237, 243)
dim = color.rgb(139, 148, 158)
idle = color.rgb(33, 38, 45)
lit = color.rgb(57, 211, 83)

font = missing_details.mona_sans()
held = set()
presses = 0

# Where each button is drawn: (x, y, width, height)
PAD = {
    "up": (70, 78, 40, 40),
    "down": (70, 158, 40, 40),
    "left": (30, 118, 40, 40),
    "right": (110, 118, 40, 40),
    "select": (196, 98, 92, 40),
    "back": (196, 150, 92, 40),
}
LABELS = {"select": "Select", "back": "Back"}

# Second screen colours
panel = color.rgb(22, 27, 34)
yellow = color.rgb(227, 179, 65)
red = color.rgb(248, 81, 73)
TYPE_COLOURS = {
    "Code": color.rgb(88, 166, 255),
    "Ops": color.rgb(240, 136, 62),
    "Security": color.rgb(248, 81, 73),
    "Git": color.rgb(188, 140, 255),
}
# Map tiles: (fill, dot or None); water dark, land light, buildings solid, paths dotted
TILES = {
    "~": (color.rgb(13, 45, 90), None),
    "P": (color.rgb(150, 112, 74), None),
    "B": (color.rgb(48, 54, 61), None),
    "=": (color.rgb(176, 214, 140), color.rgb(120, 92, 60)),
    "#": (color.rgb(176, 214, 140), color.rgb(72, 78, 86)),
    "T": (color.rgb(74, 140, 82), None),
    ".": (color.rgb(176, 214, 140), None),
}
MAP_TOP, MAP_BOTTOM = 26, 204

# Serial input from the game: only the latest message is kept, the map is kept apart
stdin = select.poll()
stdin.register(sys.stdin, select.POLLIN)
incoming = []
latest = None
world_map = None  # (image, left, top, tile size)
choice = 0  # local highlight in battle moves / pick options


def centered(text, top, size, pen):
    width, _ = screen.measure_text(text, font_size=size)
    screen.pen = pen
    screen.text(text, (WIDTH - width) / 2, top, size)


def send():
    """Prints one line per change since the last frame: +name pressed, -name let go."""
    global presses
    for button, name in BUTTONS:
        down = badge.held(button)
        if down and name not in held:
            held.add(name)
            presses += 1
            print("+" + name)
        elif not down and name in held:
            held.discard(name)
            print("-" + name)


def hello():
    print("hello display 1")


def build_map(message):
    """Draws the map once into an image, one rectangle per run of identical tiles."""
    rows, w, h = message["rows"], message["w"], message["h"]
    size = max(1, min(WIDTH // w, (MAP_BOTTOM - MAP_TOP) // h))
    canvas = image(w * size, h * size)
    canvas.antialias = image.OFF
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            end = x
            while end < len(row) and row[end] == row[x]:
                end += 1
            fill, dot = TILES.get(row[x], TILES["."])
            canvas.pen = fill
            canvas.rectangle(x * size, y * size, (end - x) * size, size)
            if dot is not None:
                canvas.pen = dot
                d = max(1, size // 3)
                for tx in range(x, end):
                    canvas.rectangle(tx * size + (size - d) // 2, y * size + (size - d) // 2, d, d)
            x = end
    return canvas, (WIDTH - w * size) // 2, MAP_TOP + (MAP_BOTTOM - MAP_TOP - h * size) // 2, size


def choosing(message):
    return message is not None and (message.get("t") == "pick" or (message.get("t") == "battle" and not message.get("busy")))


def accept(line):
    """Handles one line from the game: "?" or one JSON message."""
    global latest, world_map, choice
    if line == "?":
        hello()
        return
    if not line.startswith("{"):
        return
    try:
        message = json.loads(line)
    except ValueError:
        return
    kind = message.get("t")
    if kind == "map":
        try:
            world_map = build_map(message)
        except (KeyError, TypeError, ValueError, MemoryError) as error:
            print("map ignored:", error)
        return
    # A new menu starts from the game's highlight; while it stays open the badge keeps its own
    if choosing(message):
        same = choosing(latest) and latest.get("t") == kind and (kind == "battle" or latest.get("options") == message.get("options"))
        if not same:
            choice = message.get("sel", 0) or 0
    latest = message


def receive():
    """Reads whatever the game sent without waiting, line by line."""
    count = 0
    while count < 8192 and stdin.poll(0):
        char = sys.stdin.read(1)
        count += 1
        if not char:
            break
        if char == "\n":
            accept("".join(incoming).strip())
            incoming.clear()
        elif char != "\r":
            incoming.append(char)


def commands():
    """Second screen buttons: sent before the +x lines so the game acts on the badge's choice."""
    global choice
    message = latest
    if not choosing(message):
        return
    entries = message.get("moves") if message.get("t") == "battle" else message.get("options")
    count = min(len(entries or ()), 4 if message.get("t") == "battle" else 9)
    if count:
        if badge.pressed(BUTTON_UP):
            choice = (choice - 1) % count
        if badge.pressed(BUTTON_DOWN):
            choice = (choice + 1) % count
        choice = min(max(choice, 0), count - 1)
        if badge.pressed(BUTTON_SELECT):
            print(("move %d" if message.get("t") == "battle" else "pick %d") % (choice + 1))
    if message.get("t") == "battle":
        if badge.pressed(BUTTON_LEFT) and message.get("canSwitch"):
            print("switch")
        if badge.pressed(BUTTON_RIGHT):
            print("run")


def fit(text, size, width):
    """Shortens text with ".." until it fits in width."""
    text = str(text)
    if screen.measure_text(text, font_size=size)[0] <= width:
        return text
    while text and screen.measure_text(text + "..", font_size=size)[0] > width:
        text = text[:-1]
    return text + ".."


def wrap(text, size, width):
    lines, line = [], ""
    for word in str(text).split():
        attempt = word if not line else line + " " + word
        if line and screen.measure_text(attempt, font_size=size)[0] > width:
            lines.append(line)
            line = word
        else:
            line = attempt
    if line:
        lines.append(line)
    return lines


def write(text, x, y, size, pen):
    screen.pen = pen
    screen.text(text, x, y, size)


def write_right(text, right, y, size, pen):
    width, _ = screen.measure_text(text, font_size=size)
    write(text, right - width, y, size, pen)


def draw_controller():
    screen.pen = background
    screen.clear()
    screen.font = font
    centered("Controller", 12, 24, white)
    centered("plug in USB, run tools/badge_controller.py", 42, 12, dim)
    for name, (x, y, w, h) in PAD.items():
        screen.pen = lit if name in held else idle
        screen.shape(shape.rounded_rectangle(x, y, w, h, 6))
        label = LABELS.get(name)
        if label:
            screen.pen = background if name in held else white
            width, _ = screen.measure_text(label, font_size=14)
            screen.text(label, x + (w - width) / 2, y + 11, 14)
    centered(f"{presses} presses · Home to leave", 214, 12, dim)


def draw_title(message):
    centered("FORT MASON", 70, 28, white)
    centered("OCTODEX", 104, 28, lit)
    centered("press a button", 160, 14, dim)


def draw_world(message):
    write(fit(message.get("area", ""), 18, WIDTH - 16), 8, 3, 18, white)
    if world_map is None:
        centered("waiting for the map...", 110, 14, dim)
    else:
        canvas, left, top, size = world_map
        screen.blit(canvas, rect(left, top, canvas.width, canvas.height))
        half = size / 2
        for x, y in message.get("left", ()):
            cx, cy = left + x * size + half, top + y * size + half
            screen.pen = background
            screen.circle(vec2(cx, cy), max(2, size * 0.5) + 1)
            screen.pen = yellow
            screen.circle(vec2(cx, cy), max(2, size * 0.5))
        me = message.get("me")
        if me:
            cx, cy = left + me[0] * size + half, top + me[1] * size + half
            arm = max(3, size)
            for colour, offset in ((white, 1), (red, 0)):
                screen.pen = colour
                for dx in range(-offset, offset + 1):
                    screen.line(vec2(cx - arm + dx, cy - arm), vec2(cx + arm + dx, cy + arm))
                    screen.line(vec2(cx - arm + dx, cy + arm), vec2(cx + arm + dx, cy - arm))
    write("Octodex %s/%s" % (message.get("dex", 0), message.get("total", 0)), 8, 214, 16, white)
    write_right("Team Lv %s" % message.get("lv", 1), WIDTH - 8, 214, 16, lit)


def draw_dex(message):
    found = message.get("found", ())
    write("Octodex", 10, 6, 22, white)
    write_right("%d/%s" % (len(found), message.get("total", 0)), WIDTH - 10, 8, 20, lit)
    for i, name in enumerate(found[:20]):
        column, row = divmod(i, 10)
        write(fit(name, 14, 146), 12 + column * 156, 42 + row * 19, 14, white)
    if not found:
        centered("no Octocats yet", 110, 14, dim)


def draw_pick(message):
    lines = wrap(message.get("title", ""), 16, WIDTH - 20)[:2]
    for i, line in enumerate(lines):
        write(line, 10, 6 + i * 20, 16, white)
    options = message.get("options", ())[:9]
    top, height = 52, 22
    visible = (HEIGHT - 24 - top) // height
    first = min(max(0, choice - visible + 1), max(0, len(options) - visible))
    for i in range(first, min(len(options), first + visible)):
        y = top + (i - first) * height
        if i == choice:
            screen.pen = lit
            screen.shape(shape.rounded_rectangle(6, y, WIDTH - 12, height - 2, 4))
        write(fit("%d  %s" % (i + 1, options[i]), 14, WIDTH - 28), 14, y + 3, 14, background if i == choice else white)
    centered("Up/Down choose · Select pick · Back run", 222, 12, dim)


def hp_bar(side, y, numbers):
    hp, top = max(0, side.get("hp", 0)), max(1, side.get("max", 1))
    width = 228 if numbers else 300
    screen.pen = idle
    screen.rectangle(10, y, width, 8)
    share = min(1, hp / top)
    screen.pen = lit if share > 0.5 else yellow if share > 0.2 else red
    screen.rectangle(10, y, int(width * share), 8)
    if numbers:
        write_right("%d/%d" % (hp, top), WIDTH - 10, y - 4, 14, white)


def side_header(side, y):
    stages = "".join(" %s%+d" % (name.upper(), side.get(name, 0)) for name in ("atk", "def") if side.get(name))
    right = "Lv %s · %s%s" % (side.get("lv", "?"), side.get("type", ""), stages)
    write_right(right, WIDTH - 10, y + 3, 13, TYPE_COLOURS.get(side.get("type"), dim))
    width, _ = screen.measure_text(right, font_size=13)
    write(fit(side.get("name", ""), 17, WIDTH - 30 - width), 10, y, 17, white)


def draw_battle(message):
    foe, me = message.get("foe", {}), message.get("me", {})
    side_header(foe, 4)
    hp_bar(foe, 26, False)
    side_header(me, 42)
    hp_bar(me, 64, True)
    if message.get("busy"):
        lines = wrap(message.get("msg", ""), 22, WIDTH - 24)[:4]
        top = 82 + (HEIGHT - 82 - len(lines) * 28) // 2
        for i, line in enumerate(lines):
            centered(line, top + i * 28, 22, white)
        return
    for i, move in enumerate(message.get("moves", ())[:4]):
        y = 82 + i * 35
        selected = i == choice
        screen.pen = lit if selected else panel
        screen.shape(shape.rounded_rectangle(6, y, WIDTH - 12, 32, 5))
        ink, faint = (background, background) if selected else (white, dim)
        kind = move.get("kind", "atk")
        if kind == "atk":
            stats = "pow %s · acc %s" % (move.get("pow", 0), move.get("acc", 100))
        else:
            stats = "%s · acc %s" % (kind, move.get("acc", 100))
        eff = move.get("eff", 1)
        tag = "SUPER" if eff == 2 else "weak" if eff == 0.5 else ""
        write(fit(move.get("n", ""), 15, 190), 14, y + 2, 15, ink)
        if tag:
            write_right(tag, WIDTH - 14, y + 3, 14, ink if selected else lit if eff == 2 else red)
        screen.pen = ink if selected else TYPE_COLOURS.get(move.get("type"), dim)
        screen.text(move.get("type", ""), 14, y + 18, 11)
        type_width, _ = screen.measure_text(move.get("type", "") + "  ", font_size=11)
        write(stats, 14 + type_width, y + 18, 11, faint)
    switch = "Left switch · " if message.get("canSwitch") else ""
    centered(switch + "Right run · Select use", 224, 12, dim)


SCREENS = {"title": draw_title, "world": draw_world, "dex": draw_dex, "pick": draw_pick, "battle": draw_battle}


def update():
    receive()
    commands()
    send()
    draw = SCREENS.get(latest.get("t")) if latest else None
    if draw is None:
        draw_controller()
        return
    screen.pen = background
    screen.clear()
    screen.font = font
    try:
        draw(latest)
    except (KeyError, TypeError, ValueError, IndexError) as error:
        print("draw failed:", error)
        latest.clear()


hello()
run(update)
