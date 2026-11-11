#!/usr/bin/env python3
"""Generate the terminal-window SVG assets used by README.md.

Standard library only. Writes to Assets/terminal/:
  terminal-top[-compact].svg      macOS title bar, whoami + name art, cat about.txt, ls links/
  terminal-link-<name>[-compact]  one clickable `ls` entry per destination
  terminal-fetch[-compact].svg    fastfetch output and the final blinking prompt
  terminal-status.svg             tmux-style status segment placed before the live badges

Everything is shown by default. Typing and reveal animations are CSS only and are
disabled by prefers-reduced-motion.
"""
from __future__ import annotations

import json
import math
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Assets" / "terminal"
LOGOS = ROOT / "Assets" / "profile" / "toolbox-logos.json"
SVG_NS = "http://www.w3.org/2000/svg"

NAME = "SHELLGHOSTT"
SUBTITLE = "Aditya"
PROMPT = "ghost@arch ~ $ "
LINKS = ("linkedin", "github", "webvac", "de-caff", "agent-scan", "openmed", "nyra")
ABOUT = (
    "Security Student & CTF Player",
    "Python | TypeScript | JavaScript",
    "Web Exploitation | Network Recon",
    "Open Source | Scraping | Security Tooling",
    "Breaking things so I can fix them.",
)
FIELDS = (
    ("OS", "Linux / Windows"),
    ("Shell", "zsh / PowerShell"),
    ("Editor", "VSCode / Zed"),
    ("Terminal", "Windows Terminal"),
    ("Languages", "Python / TypeScript / JS"),
    ("Focus", "Web Exploit / Recon"),
    ("Status", "Learning & Building"),
)
LETTER_COLORS = ("green", "green", "teal", "blue", "blue", "mauve", "mauve", "teal", "green", "blue", "blue")

# (dark, light) per colour name. Dark is Catppuccin Mocha, light is Catppuccin Latte.
PALETTE = {
    "fg": ("#cdd6f4", "#4c4f69"),
    "dim": ("#7f849c", "#7c7f93"),
    "green": ("#a6e3a1", "#40a02b"),
    "blue": ("#89b4fa", "#1e66f5"),
    "mauve": ("#cba6f7", "#8839ef"),
    "teal": ("#94e2d5", "#179299"),
    "yellow": ("#f9e2af", "#df8e1d"),
    "red": ("#f38ba8", "#d20f39"),
    "arch": ("#1793d1", "#1793d1"),
}
SWATCHES = ("red", "green", "yellow", "blue", "mauve", "teal", "fg", "dim")
# macOS order: close, minimise, zoom. (fill, stroke)
TRAFFIC_LIGHTS = (("#ff5f57", "#e0443e"), ("#febc2e", "#d8a123"), ("#28c840", "#1aab29"))

# 5x7 dot-matrix glyphs for the name art.
FONT = {
    "A": "01110/10001/10001/11111/10001/10001/10001",
    "C": "01111/10000/10000/10000/10000/10000/01111",
    "I": "11111/00100/00100/00100/00100/00100/11111",
    "N": "10001/11001/11001/10101/10011/10011/10001",
    "P": "11110/10001/10001/11110/10000/10000/10000",
    "T": "11111/00100/00100/00100/00100/00100/00100",
    "X": "10001/10001/01010/00100/01010/10001/10001",
    "0": "01110/10001/10011/10101/11001/10001/01110",
    "9": "01110/10001/10001/01111/00001/00001/01110",
    "S": "01111/10000/10000/01110/00001/00001/11110",
    "H": "10001/10001/10001/11111/10001/10001/10001",
    "E": "11111/10000/10000/11110/10000/10000/11111",
    "L": "10000/10000/10000/10000/10000/10000/11111",
    "G": "01110/10001/10000/10111/10001/10001/01110",
    "O": "01110/10001/10001/10001/10001/10001/01110",
}


@dataclass(frozen=True)
class Layout:
    """Sizes for one responsive variant."""

    suffix: str
    width: int
    font: float
    pitch: float
    logo: int
    gap: int
    bar: int
    title: str

    @property
    def compact(self) -> bool:
        return bool(self.suffix)

    @property
    def adv(self) -> float:
        """Monospace advance width; text uses textLength so this holds on any font."""
        return self.font * 0.6

    @property
    def line(self) -> int:
        return round(self.font * 1.7)


DESKTOP = Layout("", 800, 13, 5, 140, 28, 34, "ghost@arch — zsh — 100×30")
COMPACT = Layout("-compact", 340, 11, 3.4, 64, 14, 30, "ghost@arch — zsh")


def base_css(font: float) -> str:
    dark = "".join(f".f-{n}{{fill:{d}}}.k-{n}{{stroke:{d}}}" for n, (d, _) in PALETTE.items())
    light = "".join(f".f-{n}{{fill:{l}}}.k-{n}{{stroke:{l}}}" for n, (_, l) in PALETTE.items())
    return (
        "text{font-family:ui-monospace,SFMono-Regular,'JetBrains Mono','DejaVu Sans Mono',"
        f"Menlo,Consolas,monospace;font-size:{font:g}px}}"
        ".b{font-weight:700}.i{font-style:italic}"
        f"{dark}"
        ".bar{fill:#fff;fill-opacity:.07}.cur{opacity:0;fill-opacity:.85}.cur-end{fill-opacity:.85}"
        f"@media(prefers-color-scheme:light){{{light}.bar{{fill:#000;fill-opacity:.06}}}}"
        "@keyframes hide{from,to{opacity:0;fill-opacity:0}}"
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
        "@media(prefers-reduced-motion:reduce){*{animation:none!important}}"
    )


def svg_doc(width: float, height: float, font: float, title: str, body: str, extra_css: str = "") -> str:
    w, h = math.ceil(width), math.ceil(height)
    return (
        f'<svg xmlns="{SVG_NS}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t">'
        f'<title id="t">{escape(title)}</title><style>{base_css(font)}{extra_css}</style>{body}</svg>\n'
    )


def hold(t: float) -> str:
    """Style attribute that keeps an element hidden for t seconds, then leaves it visible."""
    return f' style="animation:hide {t:.2f}s steps(1,end)"' if t > 0 else ""


def prompt_text(layout: Layout, y: float, t: float) -> str:
    return (
        f'<text x="0" y="{y:g}" textLength="{len(PROMPT) * layout.adv:g}" xml:space="preserve"{hold(t)}>'
        '<tspan class="f-green b">ghost@arch</tspan><tspan class="f-blue"> ~ </tspan>'
        '<tspan class="f-fg">$ </tspan></text>'
    )


class Scene:
    """Accumulates SVG parts for one terminal session and tracks the animation clock."""

    def __init__(self, layout: Layout, y: float, t: float) -> None:
        self.layout = layout
        self.y = y
        self.t = t
        self.parts: list[str] = []
        self.css: list[str] = []
        self.last_baseline = y
        self._cursor_id = 0

    def command(self, cmd: str, per_char: float = 0.05, pause: float = 0.3, tail: float = 0.3) -> None:
        """Draw a prompt, type cmd character by character with a moving block cursor."""
        if not cmd or not cmd.isprintable():
            raise ValueError(f"command must be non-empty printable text, got {cmd!r}")
        layout, n = self.layout, len(cmd)
        x0 = len(PROMPT) * layout.adv
        width = n * layout.adv
        self.parts.append(prompt_text(layout, self.y, self.t))
        chars = "".join(
            f'<tspan style="animation:hide {self.t + pause + (i + 1) * per_char:.2f}s steps(1,end)">{escape(c)}</tspan>'
            for i, c in enumerate(cmd)
        )
        self.parts.append(
            f'<text class="f-fg" x="{x0:g}" y="{self.y:g}" textLength="{width:g}" xml:space="preserve">{chars}</text>'
        )
        total = pause + n * per_char + tail
        p1, p2 = pause / total * 100, (pause + n * per_char) / total * 100
        cid = self._cursor_id
        self._cursor_id += 1
        self.css.append(
            f"@keyframes m{cid}{{0%{{opacity:1;transform:translateX(0)}}"
            f"{p1:.2f}%{{transform:translateX(0);animation-timing-function:steps({n},end)}}"
            f"{p2:.2f}%{{opacity:1;transform:translateX({width:g}px);animation-timing-function:steps(1,end)}}"
            f"100%{{opacity:0;transform:translateX({width:g}px)}}}}"
            f".m{cid}{{animation:m{cid} {total:.2f}s linear {self.t:.2f}s forwards}}"
        )
        self.parts.append(
            f'<rect class="cur f-fg m{cid}" x="{x0:g}" y="{self.y - layout.font + 1:g}" '
            f'width="{layout.adv:g}" height="{layout.font + 2:g}"/>'
        )
        self.last_baseline = self.y
        self.t += total
        self.y += layout.line

    def reveal(self, markup: str, step: float = 0.0) -> None:
        self.parts.append(f"<g{hold(self.t)}>{markup}</g>")
        self.t += step

    def final_prompt(self) -> None:
        """Idle prompt with a blinking block cursor; the last thing on screen."""
        layout = self.layout
        self.parts.append(prompt_text(layout, self.y, self.t))
        anim = f"animation:hide {self.t:.2f}s steps(1,end),blink 1.1s steps(1,end) {self.t:.2f}s infinite"
        self.parts.append(
            f'<rect class="cur-end f-fg" x="{len(PROMPT) * layout.adv:g}" y="{self.y - layout.font + 1:g}" '
            f'width="{layout.adv:g}" height="{layout.font + 2:g}" style="{anim}"/>'
        )
        self.last_baseline = self.y

    def render(self, title: str, width: float) -> str:
        return svg_doc(width, self.last_baseline + 10, self.layout.font, title, "".join(self.parts), "".join(self.css))


def pixel_text(word: str, x: float, y: float, pitch: float) -> str:
    """Block-pixel lettering in the 5x7 font, one colour class per letter."""
    if len(word) != len(LETTER_COLORS):
        raise ValueError(f"word {word!r} has {len(word)} letters but LETTER_COLORS has {len(LETTER_COLORS)}")
    size = round(pitch * 0.84, 2)
    groups = []
    for i, ch in enumerate(word):
        try:
            glyph = FONT[ch]
        except KeyError as exc:
            raise ValueError(f"no glyph for {ch!r} in word {word!r}") from exc
        rects = [
            f'<rect x="{x + (i * 6 + col) * pitch:g}" y="{y + row * pitch:g}" width="{size:g}" height="{size:g}" rx=".8"/>'
            for row, line in enumerate(glyph.split("/"))
            for col, bit in enumerate(line)
            if bit == "1"
        ]
        groups.append(f'<g class="f-{LETTER_COLORS[i]}">{"".join(rects)}</g>')
    return "".join(groups)


def about_line(y: float, value: str, *, bold: bool = False, muted: bool = False) -> str:
    cls = "f-dim i" if muted else ("f-fg b" if bold else "f-fg")
    sep = '<tspan class="f-dim"> | </tspan>'
    body = sep.join(f'<tspan class="{cls}">{escape(part)}</tspan>' for part in value.split(" | "))
    return f'<text x="0" y="{y:g}" xml:space="preserve">{body}</text>'


def build_top(layout: Layout, t0: float = 0.4) -> tuple[str, float]:
    w, bar = layout.width, layout.bar
    head = [f'<rect class="bar" x="0" y="0" width="{w}" height="{bar}" rx="8"/>']
    for i, (fill, stroke) in enumerate(TRAFFIC_LIGHTS):
        head.append(f'<circle cx="{18 + i * 20}" cy="{bar / 2:g}" r="6" fill="{fill}" stroke="{stroke}" stroke-width=".6"/>')
    head.append(
        f'<text class="f-dim" x="{w / 2:g}" y="{bar / 2 + layout.font * 0.35:g}" text-anchor="middle">{escape(layout.title)}</text>'
    )

    scene = Scene(layout, bar + layout.line + 6, t0)
    scene.parts.extend(head)

    scene.command("whoami")
    art_top = scene.y - layout.font + 3
    art_h = 7 * layout.pitch
    art = pixel_text(NAME, 0, art_top, layout.pitch)
    if layout.compact:
        sub_y = art_top + art_h + layout.line
        sub = f'<text class="f-dim" x="0" y="{sub_y:g}">{escape(SUBTITLE)}</text>'
        scene.y = sub_y + layout.line * 1.4
    else:
        art_w = 59 * layout.pitch + layout.pitch * 0.84
        sub = f'<text class="f-dim" x="{art_w + 28:g}" y="{art_top + art_h / 2 + layout.font * 0.35:g}">{escape(SUBTITLE)}</text>'
        scene.y = art_top + art_h + layout.line * 1.1
    scene.reveal(art + sub, 0.55)

    scene.command("cat about.txt")
    for i, value in enumerate(ABOUT):
        last = i == len(ABOUT) - 1
        scene.reveal(about_line(scene.y, value, bold=i == 0, muted=last), 0.14)
        scene.y += layout.line
    scene.t += 0.4
    scene.y += 6

    scene.command("ls links/")
    return scene.render(f"Terminal window for Shellghostt: {SUBTITLE}. Security student, CTF player, builder. Web exploitation and network recon.", w), scene.t


def build_link(layout: Layout, name: str, delay: float) -> str:
    label = f"{name}/"
    text_w = len(label) * layout.adv
    height = layout.line + 6
    base = layout.font + 3
    body = (
        f'<g{hold(delay)}><text class="f-blue b" x="0" y="{base:g}" textLength="{text_w:g}" xml:space="preserve">{escape(label)}</text>'
        f'<path class="k-blue" d="M0 {base + 3:g}H{text_w:g}" stroke-width="1" stroke-opacity=".45"/></g>'
    )
    return svg_doc(math.ceil(text_w) + (14 if not layout.compact else 12), height, layout.font, f"Open {name}", body)


def load_arch_path() -> str:
    """Return the Arch Linux logo path (without the trademark glyph) from the bundled sources."""
    try:
        icons = json.loads(LOGOS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot read logo sources at {LOGOS}") from exc
    for icon in icons:
        if icon.get("id") == "archlinux":
            root = ET.fromstring(icon["svg"])
            for node in root.iter(f"{{{SVG_NS}}}path"):
                if node.get("d"):
                    return node.get("d")
            raise ValueError(f"archlinux entry in {LOGOS} contains no path data")
    raise ValueError(f"no 'archlinux' entry in {LOGOS}")


def build_fetch(layout: Layout, t0: float, arch_path: str) -> str:
    adv, line, w = layout.adv, layout.line, layout.width
    scene = Scene(layout, layout.font + 6, t0)
    scene.command("fastfetch")
    y1 = scene.y
    tx = layout.logo + layout.gap
    key_w = (max(len(k) for k, _ in FIELDS) + 2) * adv

    scale = layout.logo / 128
    scene.reveal(
        f'<g transform="translate(0 {y1 - layout.font + 2:g}) scale({scale:.4f})">'
        f'<path class="f-arch" fill-rule="evenodd" d="{arch_path}"/></g>',
        0.1,
    )
    title = (
        f'<text x="{tx}" y="{y1:g}" xml:space="preserve"><tspan class="f-blue b">ghost</tspan>'
        '<tspan class="f-fg">@</tspan><tspan class="f-blue b">arch</tspan></text>'
        f'<path class="k-dim" d="M{tx} {y1 + 8:g}h{8 * adv:g}" stroke-width="1" stroke-opacity=".6"/>'
    )
    scene.reveal(title, 0.08)
    for i, (key, value) in enumerate(FIELDS):
        y = y1 + line * (i + 1)
        row = (
            f'<text x="{tx}" y="{y:g}" class="f-blue b" textLength="{len(key) * adv:g}" xml:space="preserve">{escape(key)}</text>'
            f'<text x="{tx + len(key) * adv:g}" y="{y:g}" class="f-dim">:</text>'
            f'<text x="{tx + key_w:g}" y="{y:g}" class="f-fg">{escape(value)}</text>'
        )
        scene.reveal(row, 0.08)
    sw = 16 if layout.compact else 20
    sw_y = y1 + line * len(FIELDS) + 14
    swatches = "".join(
        f'<rect class="f-{name}" x="{tx + i * (sw + 4)}" y="{sw_y:g}" width="{sw}" height="{sw * 0.55:g}" rx="1.5"/>'
        for i, name in enumerate(SWATCHES)
    )
    scene.reveal(swatches, 0.3)
    scene.y = sw_y + sw * 0.55 + line + 4
    scene.final_prompt()
    return scene.render("fastfetch: Linux, Windows. zsh, PowerShell. Student by day. Builder by night.", w)


def build_status() -> str:
    width, height = 112, 20
    body = (
        f'<rect width="{width}" height="{height}" fill="#a6e3a1"/>'
        f'<text x="{width / 2:g}" y="14" text-anchor="middle" font-size="11" font-weight="700" fill="#1e1e2e" '
        f'textLength="{width - 16}" xml:space="preserve">[main] 0:zsh*</text>'
    )
    return svg_doc(width, height, 11, "tmux status segment", body)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    arch_path = load_arch_path()
    count = 0
    for layout in (DESKTOP, COMPACT):
        suffix = layout.suffix
        top_svg, top_end = build_top(layout)
        (OUT / f"terminal-top{suffix}.svg").write_text(top_svg, encoding="utf-8")
        link_start = top_end + 0.15
        for i, name in enumerate(LINKS):
            (OUT / f"terminal-link-{name}{suffix}.svg").write_text(build_link(layout, name, link_start + i * 0.08), encoding="utf-8")
        fetch_start = link_start + len(LINKS) * 0.08 + 0.35
        (OUT / f"terminal-fetch{suffix}.svg").write_text(build_fetch(layout, fetch_start, arch_path), encoding="utf-8")
        count += 2 + len(LINKS)
    (OUT / "terminal-status.svg").write_text(build_status(), encoding="utf-8")
    print(f"Generated {count + 1} SVG assets in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
