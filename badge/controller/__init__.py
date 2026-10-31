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
import math
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

# Second screen colours (GitHub dark)
panel = color.rgb(22, 27, 34)
raised = color.rgb(40, 46, 54)
edge = color.rgb(48, 54, 61)
faint = color.rgb(72, 79, 88)
yellow = color.rgb(227, 179, 65)
red = color.rgb(248, 81, 73)
shade = color.rgb(0, 0, 0, 110)
glow = color.rgb(255, 255, 255, 70)
TYPE_COLOURS = {
    "Code": color.rgb(88, 166, 255),
    "Ops": color.rgb(240, 136, 62),
    "Security": color.rgb(248, 81, 73),
    "Git": color.rgb(188, 140, 255),
}

# Map tiles: water dark, land light, buildings solid, paths dotted
WATER, WAVE = color.rgb(16, 52, 98), color.rgb(46, 98, 156)
GRASS, GRASS_ALT = color.rgb(118, 180, 92), color.rgb(110, 171, 86)
SAND, SAND_DOT = color.rgb(224, 202, 152), color.rgb(176, 146, 100)
SHORE = color.rgb(236, 220, 178)
PIER, PIER_SEAM = color.rgb(156, 112, 70), color.rgb(112, 78, 48)
ROOF, ROOF_TOP, WALL, WINDOW = color.rgb(76, 84, 98), color.rgb(110, 120, 136), color.rgb(42, 46, 56), color.rgb(242, 204, 96)
STREET, STREET_LINE = color.rgb(72, 78, 88), color.rgb(200, 204, 210)
CANOPY, CANOPY_LIGHT = color.rgb(46, 112, 60), color.rgb(84, 150, 76)
MAP_TOP, MAP_BOTTOM = 32, 200

# Serial input from the game: only the latest message is kept, the map is kept apart
stdin = select.poll()
stdin.register(sys.stdin, select.POLLIN)
incoming = []
latest = None
world_map = None  # (image, left, top, tile size)
choice = 0  # local highlight in battle moves / pick options
shown_hp = {}  # side -> (name, hp drawn), so HP bars slide instead of jumping
last_frame = None


def load_mona(name, frames):
    """Mona's animation from the Merge Conflict app, or None when it is not on the badge."""
    try:
        sheet = image.load("/system/apps/merge_conflict/mona-%s.png" % name)
    except OSError:
        return None
    return sheet, sheet.width // frames, sheet.height, frames


MONA = {"default": load_mona("default", 11), "dance": load_mona("dance", 6)}


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
    """Draws the map once into an image: textured tiles, shores, roofs with lit windows, trees."""
    rows, w, h = message["rows"], message["w"], message["h"]
    size = max(1, min(WIDTH // w, (MAP_BOTTOM - MAP_TOP) // h))
    canvas = image(w * size, h * size)
    canvas.antialias = image.OFF

    def at(x, y):
        if 0 <= y < len(rows) and 0 <= x < len(rows[y]):
            return rows[y][x]
        return "~"

    mid, dot = size // 2, max(1, size // 3)
    for y, row in enumerate(rows):
        for x, tile in enumerate(row):
            px, py = x * size, y * size
            if tile == "~":
                canvas.pen = WATER
                canvas.rectangle(px, py, size, size)
                if (x * 3 + y * 5) % 7 == 0:
                    canvas.pen = WAVE
                    canvas.rectangle(px + 1, py + mid, size - 2, 1)
                continue
            if tile == "P":
                canvas.pen = PIER
                canvas.rectangle(px, py, size, size)
                canvas.pen = PIER_SEAM
                canvas.rectangle(px, py + size - 1, size, 1)
                continue
            if tile == "B":
                canvas.pen = ROOF
                canvas.rectangle(px, py, size, size)
                if at(x, y - 1) != "B":
                    canvas.pen = ROOF_TOP
                    canvas.rectangle(px, py, size, 1)
                if at(x, y + 1) != "B":
                    canvas.pen = WALL
                    canvas.rectangle(px, py + size - 2, size, 2)
                elif x % 2 == 0 and y % 2 == 1:
                    canvas.pen = WINDOW
                    canvas.rectangle(px + mid - 1, py + mid - 1, 2, 2)
                continue
            if tile == "#":
                canvas.pen = STREET
                canvas.rectangle(px, py, size, size)
                if y % 2 == 0 and at(x + 1, y) == "#":
                    canvas.pen = STREET_LINE
                    canvas.rectangle(px + size - 1, py + 1, 2, size - 2)
                continue
            if tile == "=":
                canvas.pen = SAND
                canvas.rectangle(px, py, size, size)
                if (x + y) % 2 == 0:
                    canvas.pen = SAND_DOT
                    canvas.rectangle(px + (size - dot) // 2, py + (size - dot) // 2, dot, dot)
            else:
                canvas.pen = GRASS if (x + y) % 2 else GRASS_ALT
                canvas.rectangle(px, py, size, size)
            # Sandy shore where land meets the bay
            canvas.pen = SHORE
            if at(x, y - 1) == "~":
                canvas.rectangle(px, py, size, 1)
            if at(x, y + 1) == "~":
                canvas.rectangle(px, py + size - 1, size, 1)
            if at(x - 1, y) == "~":
                canvas.rectangle(px, py, 1, size)
            if at(x + 1, y) == "~":
                canvas.rectangle(px + size - 1, py, 1, size)
            if tile == "T":
                canvas.pen = CANOPY
                canvas.circle(vec2(px + size / 2, py + size / 2), size * 0.6)
                canvas.pen = CANOPY_LIGHT
                canvas.circle(vec2(px + size / 2 - 1, py + size / 2 - 1), size * 0.25)
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


def box(x, y, w, h, fill, border=None, radius=6):
    """Rounded panel, with a 1 px border when given."""
    if border is not None:
        screen.pen = border
        screen.shape(shape.rounded_rectangle(x, y, w, h, radius))
        x, y, w, h, radius = x + 1, y + 1, w - 2, h - 2, max(1, radius - 1)
    screen.pen = fill
    screen.shape(shape.rounded_rectangle(x, y, w, h, radius))


def pill(text, right, y, size, fill, ink):
    """A rounded label ending at x = right; returns its left edge."""
    width, _ = screen.measure_text(text, font_size=size)
    left = right - width - 10
    box(left, y, width + 10, size + 5, fill, radius=(size + 5) // 2)
    write(text, left + 5, y + 2, size, ink)
    return left


def bar(x, y, w, h, share, fill):
    box(x, y, w, h, idle, radius=h // 2)
    if share > 0:
        box(x, y, max(h, int(w * min(1, share))), h, fill, radius=h // 2)
        screen.pen = glow
        screen.rectangle(x + h // 2, y + 1, max(0, int(w * min(1, share)) - h), 1)


def draw_mona(name, x, y, scale):
    mona = MONA.get(name) or MONA.get("default")
    if mona is None:
        return
    sheet, w, h, frames = mona
    frame = (badge.ticks // 110) % frames
    screen.blit(sheet, rect(frame * w, 0, w, h), rect(x, y, w * scale, h * scale))


def stars(count, top, bottom):
    """A slow twinkle of fixed stars."""
    for i in range(count):
        x, y = (i * 97 + 13) % WIDTH, top + (i * 57 + 29) % (bottom - top)
        level = 0.5 + 0.5 * math.sin(badge.ticks / 600 + i * 1.7)
        screen.pen = color.rgb(200, 220, 255, int(60 + 150 * level))
        screen.circle(vec2(x, y), 0.6 + level)


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
    stars(36, 0, HEIGHT)
    bob = int(3 * math.sin(badge.ticks / 300))
    draw_mona("dance", (WIDTH - 112) // 2, 14 + bob, 4)
    centered("FORT MASON", 118, 22, white)
    centered("OCTODEX", 142, 36, lit)
    if (badge.ticks // 600) % 2 == 0:
        centered("press a button", 204, 14, dim)


def draw_world(message):
    # Header: map pin, area name, team level
    box(0, -6, WIDTH, 32, panel, edge)
    screen.pen = red
    screen.circle(vec2(14, 10), 5)
    screen.triangle(vec2(9.5, 12), vec2(18.5, 12), vec2(14, 20))
    screen.pen = panel
    screen.circle(vec2(14, 10), 2)
    left = pill("Lv %s" % message.get("lv", 1), WIDTH - 8, 4, 13, lit, background)
    write(fit(message.get("area", ""), 17, left - 34), 26, 3, 17, white)

    if world_map is None:
        centered("waiting for the map...", 110, 14, dim)
    else:
        canvas, mx, my, size = world_map
        box(mx - 3, my - 3, canvas.width + 6, canvas.height + 6, edge, radius=5)
        screen.blit(canvas, rect(mx, my, canvas.width, canvas.height))
        half = size / 2
        for i, (x, y) in enumerate(message.get("left", ())):
            cx, cy = mx + x * size + half, my + y * size + half
            twinkle = 0.5 + 0.5 * math.sin(badge.ticks / 250 + i * 1.3)
            screen.pen = shade
            screen.circle(vec2(cx + 1, cy + 1), 3.2)
            screen.pen = background
            screen.circle(vec2(cx, cy), 3.4 + twinkle * 0.6)
            screen.pen = yellow
            screen.circle(vec2(cx, cy), 2.4 + twinkle * 0.6)
            screen.pen = white
            screen.circle(vec2(cx - 0.8, cy - 0.8), 0.8)
        me = message.get("me")
        if me:
            cx, cy = mx + me[0] * size + half, my + me[1] * size + half
            pulse = (badge.ticks % 1200) / 1200
            screen.pen = color.rgb(255, 255, 255, int(180 * (1 - pulse)))
            screen.shape(shape.arc(cx, cy, 4 + pulse * 9, 5.5 + pulse * 9, 0, 360))
            arm = max(3, size)
            for colour, offset in ((white, 1), (red, 0)):
                screen.pen = colour
                for dx in range(-offset, offset + 1):
                    screen.line(vec2(cx - arm + dx, cy - arm), vec2(cx + arm + dx, cy + arm))
                    screen.line(vec2(cx - arm + dx, cy + arm), vec2(cx + arm + dx, cy - arm))

    # Footer: Octodex progress
    dex, total = message.get("dex", 0), max(1, message.get("total", 1))
    write("Octodex", 10, 209, 12, dim)
    write_right("%s/%s" % (dex, total), WIDTH - 10, 210, 16, white)
    bar(10, 226, WIDTH - 72, 8, dex / total, yellow)


def draw_dex(message):
    found, total = message.get("found", ()), max(1, message.get("total", 1))
    write("Octodex", 10, 6, 22, white)
    write_right("%d/%d" % (len(found), total), WIDTH - 10, 9, 18, lit)
    bar(10, 36, WIDTH - 20, 6, len(found) / total, lit)
    rows = (min(total, 12) + 1) // 2
    height = min(29, (HEIGHT - 50) // max(1, rows))
    for i in range(min(total, 2 * rows)):
        column, row = divmod(i, rows)
        x, y = 8 + column * 156, 50 + row * height
        known = i < len(found)
        box(x, y, 148, height - 4, raised if known else panel, edge if known else None, radius=5)
        cy = y + (height - 4) / 2
        screen.pen = lit if known else idle
        screen.circle(vec2(x + 13, cy), 7)
        if known:
            screen.pen = background
            screen.line(vec2(x + 9, cy), vec2(x + 12, cy + 3))
            screen.line(vec2(x + 12, cy + 3), vec2(x + 17, cy - 3))
            write(fit(found[i], 13, 118), x + 26, cy - 8, 13, white)
        else:
            write("?", x + 10.5, cy - 7, 12, faint)
            write("???", x + 26, cy - 8, 13, faint)


def draw_pick(message):
    lines = wrap(message.get("title", ""), 15, WIDTH - 24)[:2]
    box(0, -6, WIDTH, 14 + 19 * len(lines), panel, edge)
    for i, line in enumerate(lines):
        write(line, 12, 4 + i * 19, 15, white)
    options = message.get("options", ())[:9]
    top, height = 18 + 19 * len(lines), 30
    visible = (HEIGHT - 20 - top) // height
    first = min(max(0, choice - visible + 1), max(0, len(options) - visible))
    for i in range(first, min(len(options), first + visible)):
        y = top + (i - first) * height
        selected = i == choice
        box(8, y, WIDTH - 16, height - 4, raised if selected else panel, lit if selected else edge, radius=6)
        cy = y + (height - 4) / 2
        screen.pen = lit if selected else idle
        screen.circle(vec2(24, cy), 8)
        number = str(i + 1)
        width, _ = screen.measure_text(number, font_size=12)
        write(number, 24 - width / 2, cy - 7, 12, background if selected else dim)
        write(fit(options[i], 14, WIDTH - 60), 40, cy - 8, 14, white)
    centered("Up/Down choose · Select pick · Back run", 224, 11, dim)


def slide_hp(key, side, dt):
    """The HP drawn moves towards the real HP, so damage drains the bar."""
    name, hp = side.get("name", ""), max(0, side.get("hp", 0))
    old = shown_hp.get(key)
    if old is None or old[0] != name:
        shown = hp
    else:
        shown = old[1] + (hp - old[1]) * min(1, dt / 250)
        if abs(shown - hp) < 0.2:
            shown = hp
    shown_hp[key] = (name, shown)
    return shown


def side_card(side, y, h, key, numbers, dt):
    box(6, y, WIDTH - 12, h, panel, edge, radius=7)
    kind = side.get("type", "")
    left = pill(kind, WIDTH - 14, y + 5, 11, TYPE_COLOURS.get(kind, dim), background)
    stages = "".join(" %s%+d" % (name.upper(), side.get(name, 0)) for name in ("atk", "def") if side.get(name))
    level = "Lv %s%s" % (side.get("lv", "?"), stages)
    width, _ = screen.measure_text(level, font_size=12)
    write(level, left - width - 6, y + 6, 12, dim)
    write(fit(side.get("name", ""), 16, left - width - 30), 14, y + 3, 16, white)
    hp, top = slide_hp(key, side, dt), max(1, side.get("max", 1))
    share = hp / top
    colour = lit if share > 0.5 else yellow if share > 0.2 else red
    write("HP", 14, y + h - 14, 10, dim)
    bar(32, y + h - 12, (WIDTH - 104) if numbers else (WIDTH - 52), 7, share, colour)
    if numbers:
        write_right("%d/%d" % (round(hp), top), WIDTH - 14, y + h - 17, 13, white)


def draw_battle(message):
    global last_frame
    now = badge.ticks
    dt = 0 if last_frame is None else min(200, now - last_frame)
    last_frame = now
    side_card(message.get("foe", {}), 4, 40, "foe", False, dt)
    side_card(message.get("me", {}), 48, 42, "me", True, dt)
    if message.get("busy"):
        box(6, 98, WIDTH - 12, 136, panel, edge, radius=8)
        text = message.get("msg", "")
        draw_mona("dance" if "super" in text.lower() else "default", 16, 140, 2)
        lines = wrap(text, 18, WIDTH - 104)[:5]
        top = 98 + (136 - len(lines) * 24) // 2
        for i, line in enumerate(lines):
            write(line, 82, top + i * 24, 18, white)
        if (now // 400) % 2 == 0:
            screen.pen = dim
            screen.triangle(vec2(WIDTH - 26, 220), vec2(WIDTH - 16, 220), vec2(WIDTH - 21, 226))
        return
    for i, move in enumerate(message.get("moves", ())[:4]):
        y = 96 + i * 32
        selected = i == choice
        kind = move.get("type", "")
        tint = TYPE_COLOURS.get(kind, dim)
        box(6, y, WIDTH - 12, 29, raised if selected else panel, lit if selected else edge, radius=6)
        screen.pen = tint
        screen.shape(shape.rounded_rectangle(8, y + 4, 4, 21, 2))
        write(fit(move.get("n", ""), 14, 196), 20, y + 1, 14, white)
        if move.get("kind", "atk") == "atk":
            stats = "pow %s · acc %s" % (move.get("pow", 0), move.get("acc", 100))
        else:
            stats = "%s · acc %s" % (move.get("kind"), move.get("acc", 100))
        write(kind, 20, y + 16, 10, tint)
        width, _ = screen.measure_text(kind + "  ", font_size=10)
        write(stats, 20 + width, y + 16, 10, dim)
        eff = move.get("eff", 1)
        if eff == 2:
            pill("SUPER", WIDTH - 14, y + 7, 11, lit, background)
        elif eff == 0.5:
            pill("weak", WIDTH - 14, y + 7, 11, idle, red)
    switch = "Left switch · " if message.get("canSwitch") else ""
    centered(switch + "Right run · Select use", 226, 11, dim)


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
