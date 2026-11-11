"""Generate the xCaptaiN09-style terminal assets (dark) for the profile README.

Layout pieces, all written to assets/:
  terminal-top.svg      window titlebar + whoami / focus
  link_<name>.svg       clickable terminal chips, inlined side-by-side in the README
  terminal-fetch.svg    fastfetch-style card: ASCII ghost + system info
  terminal-status.svg   thin status divider
  toolbox-footer.svg    pulsing tech chips footer
"""

import os
from datetime import datetime, timezone

LH  = 20   # line height px
FS  = 13   # font size px
PAD = 20   # outer padding px
ADV = 8    # monospace char advance (FS * 0.62, rounded)

C = {
    "bg":     "#0d1117",
    "panel":  "#161b22",
    "border": "#30363d",
    "user":   "#58a6ff",
    "dir":    "#79c0ff",
    "prompt": "#3fb950",
    "cmd":    "#c9d1d9",
    "text":   "#c9d1d9",
    "muted":  "#8b949e",
    "key":    "#d29922",
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def head():
    """Common svg-open tail (closes the <svg ... tag) + mono font style."""
    return [
        'xmlns="http://www.w3.org/2000/svg">',
        f'  <style>text{{font-family:"SFMono-Regular","Consolas","Liberation Mono",'
        f'"Courier New",monospace;font-size:{FS}px;white-space:pre;}}</style>',
    ]


# ── terminal-top.svg ────────────────────────────────────────────────────────

def terminal_top():
    bar_h = 30
    lines = [
        [("ghost@shellghostt", "user"), (":", "muted"), ("~", "dir"), ("$ ", "prompt"), ("whoami", "cmd")],
        [("security student · ctf player · builder", "text")],
        [],
        [("ghost@shellghostt", "user"), (":", "muted"), ("~", "dir"), ("$ ", "prompt"), ("cat focus.txt", "cmd")],
        [("web exploitation", "prompt"), ("  ·  ", "muted"), ("network recon", "prompt")],
    ]
    h = bar_h + PAD + len(lines) * LH + PAD
    w = 800

    svg = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '] + head()
    svg.append(f'  <rect width="{w}" height="{h}" rx="10" fill="{C["bg"]}" stroke="{C["border"]}"/>')
    # titlebar
    svg.append(f'  <path d="M0,10 Q0,0 10,0 L{w-10},0 Q{w},0 {w},10 L{w},{bar_h} L0,{bar_h} Z" fill="{C["panel"]}"/>')
    svg.append(f'  <line x1="0" y1="{bar_h}" x2="{w}" y2="{bar_h}" stroke="{C["border"]}"/>')
    for i, col in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        svg.append(f'  <circle cx="{20 + i * 20}" cy="15" r="5" fill="{col}"/>')
    svg.append(f'  <text x="{w/2}" y="19" fill="{C["muted"]}" text-anchor="middle">aditya@shellghostt — zsh</text>')
    # content
    y0 = bar_h + PAD + LH
    for i, line in enumerate(lines):
        y = y0 + i * LH
        x = PAD
        for content, style in line:
            if not content:
                continue
            svg.append(f'  <text x="{x}" y="{y}" fill="{C[style]}">{esc(content)}</text>')
            x += len(content) * ADV
    svg.append("</svg>")
    return "\n".join(svg)


# ── link_<name>.svg (clickable chips) ───────────────────────────────────────

LINKS = [
    ("linkedin",  "https://www.linkedin.com/in/shellghostt/"),
    ("github",    "https://github.com/Shellghostt"),
    ("webvac",    "https://github.com/Shellghostt/WebVac"),
    ("de-caff",   "https://github.com/Shellghostt/De-Caffeinator"),
    ("agent-scan", "https://github.com/Shellghostt/agent-scan"),
]


def link_chip(name):
    w = (len(name) + 4) * ADV + 20
    h = 30
    return "\n".join([
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '] + head() + [
        f'  <rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="6" fill="{C["bg"]}" stroke="{C["border"]}"/>',
        f'  <text x="{w/2}" y="19" fill="{C["muted"]}" text-anchor="middle">[ {name} ]</text>',
        "</svg>",
    ])


# ── terminal-fetch.svg (fastfetch-style) ────────────────────────────────────

GHOST = [
    r"        .::::.",
    r"      .::::::::.",
    r"     :::::::::::::",
    r"    :::  (o)(o)  :::",
    r"    :::    __    :::",
    r"    :::  \____/  :::",
    r"     '::::::::::::",
    r"       :::::::::::.",
    r"      /::::::::::::\\",
    r"     /:::: | | :::::\\",
    r"    '   '  |_|  '   '",
]

FETCH_INFO = [
    ("row",  "aditya@shellghostt", "user"),
    ("row",  "─" * 30,             "muted"),
    ("pair", "OS",                 "Linux · Windows"),
    ("pair", "Shell",              "zsh · PowerShell"),
    ("pair", "Editor",             "VSCode · Zed"),
    ("pair", "Langs",              "Python · TypeScript · JS"),
    ("pair", "Focus",              "web exploitation · recon"),
    ("gap",  "",                   ""),
    ("row",  "student by day. builder by night.", "text"),
]


def terminal_fetch():
    w = 800
    ghost_x, info_x = PAD, 240
    n = max(len(GHOST), len(FETCH_INFO))
    h = n * LH + PAD * 2

    svg = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '] + head()
    svg.append(f'  <rect width="{w}" height="{h}" rx="10" fill="{C["bg"]}" stroke="{C["border"]}"/>')
    y0 = PAD + LH
    for i, row in enumerate(GHOST):
        svg.append(f'  <text x="{ghost_x}" y="{y0 + i * LH}" fill="{C["dir"]}">{esc(row)}</text>')
    for i, (kind, a, b) in enumerate(FETCH_INFO):
        y = y0 + i * LH
        if kind == "row":
            svg.append(f'  <text x="{info_x}" y="{y}" fill="{C[b]}">{esc(a)}</text>')
        elif kind == "pair":
            svg.append(f'  <text x="{info_x}" y="{y}" fill="{C["key"]}">{esc(f"{a:<8}")}</text>')
            svg.append(f'  <text x="{info_x + 8 * ADV}" y="{y}" fill="{C["text"]}">{esc(b)}</text>')
    svg.append("</svg>")
    return "\n".join(svg)


# ── terminal-status.svg (thin divider) ──────────────────────────────────────

def terminal_status():
    w, h = 800, 24
    return "\n".join([
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '] + head() + [
        f'  <text x="{PAD}" y="17" fill="{C["key"]}">status</text>',
        f'  <text x="{PAD + 6 * ADV}" y="17" fill="{C["muted"]}">{"─" * 86}</text>',
        "</svg>",
    ])


# ── toolbox-footer.svg (pulsing tech chips) ─────────────────────────────────

TOOLS = ["python", "typescript", "javascript", "bash", "linux", "git", "github"]


def toolbox_footer():
    gap = 10
    chips = [(t, (len(t) + 4) * ADV + 20) for t in TOOLS]
    w = sum(cw for _, cw in chips) + gap * (len(chips) - 1) + PAD * 2
    h = 40

    svg = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '] + head()
    x = PAD
    for i, (name, cw) in enumerate(chips):
        pulse = (f'<animate attributeName="opacity" values="0.4;1;0.4" dur="3s" '
                 f'begin="{i * 0.4}s" repeatCount="indefinite"/>')
        svg.append(f'  <rect x="{x}" y="5" width="{cw}" height="{h - 10}" rx="6" '
                   f'fill="{C["bg"]}" stroke="{C["border"]}">{pulse}</rect>')
        svg.append(f'  <text x="{x + cw / 2}" y="24" fill="{C["muted"]}" '
                   f'text-anchor="middle">{name}</text>')
        x += cw + gap
    svg.append("</svg>")
    return "\n".join(svg)


def main():
    os.makedirs("assets", exist_ok=True)
    outputs = {
        "terminal-top.svg":    terminal_top(),
        "terminal-fetch.svg":  terminal_fetch(),
        "terminal-status.svg": terminal_status(),
        "toolbox-footer.svg":  toolbox_footer(),
    }
    for name, _ in LINKS:
        outputs[f"link_{name}.svg"] = link_chip(name)
    for name, body in outputs.items():
        with open(f"assets/{name}", "w", encoding="utf-8") as f:
            f.write(body)
        print(f"  wrote assets/{name}")


if __name__ == "__main__":
    main()
