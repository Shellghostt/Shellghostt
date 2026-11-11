"""Generate the boot-sequence terminal SVG header (dark + light) for the profile README.

The terminal is sliced into stacked strips so each clickable region (the projects
header and every project line) can be wrapped in its own <a href> in the README —
links inside a single SVG are dead once GitHub serves it as an <img>.
"""

import os
from datetime import datetime, timezone

LH  = 20   # line height px
FS  = 13   # font size px
PAD = 20   # outer padding px
W   = 560  # card width px
RX  = 10   # corner radius px
ADV = 8    # monospace char advance (FS * 0.62, rounded)

BAR_W = 160  # loading-bar width px


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def prompt_head():
    return [
        ("ghost@shellghostt", "user"),
        (":",                 "muted"),
        ("~",                 "dir"),
        ("$ ",                "prompt"),
    ]


def build_lines():
    """Full terminal content as (segments, theme) rows; BAR and CURSOR are
    special markers rendered with SMIL animation."""
    head = prompt_head()
    projects = [
        ("agent-scan/", "security scanner for AI agents & MCP"),
        ("de-caff/",    "js reverse-engineering & audit pipeline"),
        ("webvac/",     "async scraper for js-heavy sites"),
    ]

    lines = [
        head + [("whoami", "cmd")],
        [("security student · ctf player · builder", "text")],
        [],
        head + [("cat focus.txt", "cmd")],
        [("web exploitation", "prompt"), ("  ·  ", "muted"), ("network recon", "prompt")],
        [],
        head + [("ls ~/projects", "cmd")],
    ]
    for name, desc in projects:
        lines.append([(f"{name:<18}", "dir"), (desc, "muted")])
    lines += [
        [],
        head + [("./boot --next", "cmd")],
        [("[", "muted"), ("BAR", "bar"), ("] loading next challenge...", "muted")],
        [],
        [(f"last login: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", "muted")],
        head + [("CURSOR", "cursor")],
    ]
    return lines


# (name, line slice, link target) — link goes into the README's <a href> wrapper
STRIPS = [
    ("top", slice(0, 5),  None),
    ("ph",  slice(5, 7),  "https://github.com/Shellghostt?tab=repositories"),
    ("p1",  slice(7, 8),  "https://github.com/Shellghostt/agent-scan"),
    ("p2",  slice(8, 9),  "https://github.com/Shellghostt/De-Caffeinator"),
    ("p3",  slice(9, 10), "https://github.com/Shellghostt/WebVac"),
    ("bot", slice(10, 16), None),
]


def strip_svg(chunk, role, theme):
    if theme == "dark":
        bg, border = "#0d1117", "#30363d"
        user, dir_c, prompt, text, muted = "#58a6ff", "#79c0ff", "#3fb950", "#c9d1d9", "#8b949e"
    else:
        bg, border = "#f6f8fa", "#d0d7de"
        user, dir_c, prompt, text, muted = "#0550ae", "#0969da", "#1a7f37", "#24292f", "#57606a"

    colour_map = {"user": user, "dir": dir_c, "prompt": prompt,
                  "cmd": text, "text": text, "muted": muted}

    pad_top = PAD if role == "top" else 0
    pad_bot = PAD if role == "bot" else 0
    h = len(chunk) * LH + pad_top + pad_bot
    y0 = PAD + LH if role == "top" else LH

    svg = [
        f'<svg width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
        f'xmlns="http://www.w3.org/2000/svg">',
        f'  <style>text{{font-family:"SFMono-Regular","Consolas","Liberation Mono",'
        f'"Courier New",monospace;font-size:{FS}px;white-space:pre;}}</style>',
    ]

    # ── Background + borders (stitched so stacked strips read as one card) ──
    if role == "top":
        fill_d = f"M0,{h} L0,{RX} Q0,0 {RX},0 L{W - RX},0 Q{W},0 {W},{RX} L{W},{h} Z"
        line_d = f"M0,{h} L0,{RX} Q0,0 {RX},0 L{W - RX},0 Q{W},0 {W},{RX} L{W},{h}"
        svg.append(f'  <path d="{fill_d}" fill="{bg}"/>')
        svg.append(f'  <path d="{line_d}" fill="none" stroke="{border}" stroke-width="1"/>')
    elif role == "bot":
        fill_d = f"M0,0 L0,{h - RX} Q0,{h} {RX},{h} L{W - RX},{h} Q{W},{h} {W},{h - RX} L{W},0 Z"
        line_d = f"M0,0 L0,{h - RX} Q0,{h} {RX},{h} L{W - RX},{h} Q{W},{h} {W},{h - RX} L{W},0"
        svg.append(f'  <path d="{fill_d}" fill="{bg}"/>')
        svg.append(f'  <path d="{line_d}" fill="none" stroke="{border}" stroke-width="1"/>')
    else:
        svg.append(f'  <rect width="{W}" height="{h}" fill="{bg}"/>')
        svg.append(f'  <rect x="0" width="1" height="{h}" fill="{border}"/>')
        svg.append(f'  <rect x="{W - 1}" width="1" height="{h}" fill="{border}"/>')

    # ── Content ─────────────────────────────────────────────────────────
    for i, line in enumerate(chunk):
        y = y0 + i * LH
        x = PAD
        for content, style in line:
            if style == "bar":
                # animated loading bar: dim track + green fill sweeping across
                by = y - 11
                svg.append(f'  <rect x="{x}" y="{by}" width="{BAR_W}" height="10" rx="3" '
                           f'fill="{muted}" opacity="0.3"/>')
                svg.append(f'  <rect x="{x}" y="{by}" height="10" rx="3" fill="{prompt}">'
                           f'<animate attributeName="width" values="0;{BAR_W}" dur="4s" '
                           f'repeatCount="indefinite"/></rect>')
                x += BAR_W
            elif style == "cursor":
                svg.append(f'  <text x="{x}" y="{y}" fill="{prompt}">█'
                           f'<animate attributeName="opacity" values="1;1;0;0" '
                           f'keyTimes="0;0.5;0.501;1" dur="1.4s" repeatCount="indefinite"/>'
                           f'</text>')
            else:
                svg.append(f'  <text x="{x}" y="{y}" fill="{colour_map[style]}">{esc(content)}</text>')
                x += len(content) * ADV

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    os.makedirs("assets", exist_ok=True)
    lines = build_lines()
    for theme in ("dark", "light"):
        for name, chunk, _ in STRIPS:
            path = f"assets/{name}_{theme}.svg"
            with open(path, "w", encoding="utf-8") as f:
                f.write(strip_svg(lines[chunk], name, theme))
            print(f"  wrote {path}")


if __name__ == "__main__":
    main()
