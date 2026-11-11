"""Generate cyber "case-file" cover-art thumbnails (16:9 SVG) for README_V2.

Each card is a HUD-style dossier cover: scanlines, corner brackets, status
strip, language chip, and a glyph mark. Written to thumbs/.
"""

import os

W, H = 560, 315

CARDS = [
    {
        "name": "WebVac",
        "tag": "SCRAPER // CRAWLER",
        "desc": "asyncio crawling for JS-heavy targets",
        "lang": "Python",
        "pct": "82%",
        "glyph": ["  /\\  ", " /||\\ ", "  ||  ", " /||\\ ", "/____\\"],
        "accent": "#00ff9c",
        "accent2": "#00d1ff",
    },
    {
        "name": "De-Caffeinator",
        "tag": "REVERSE ENGINEERING",
        "desc": "deobfuscates bundles, finds hidden endpoints",
        "lang": "TypeScript",
        "pct": "91%",
        "glyph": [" .--. ", "( ## )", " \\--/ ", "  \\/  ", "  \\/  "],
        "accent": "#ffb454",
        "accent2": "#ff2e88",
    },
    {
        "name": "agent-scan",
        "tag": "SECURITY SCANNER",
        "desc": "audits AI agents, MCP servers & skills",
        "lang": "Python",
        "pct": "76%",
        "glyph": [" .--. ", "(o o) ", " | - | ", " '--' ", " /|\\ "],
        "accent": "#c792ea",
        "accent2": "#00d1ff",
    },
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(card):
    a, a2 = card["accent"], card["accent2"]
    glyph = "\n".join(card["glyph"])
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">',
        f'  <defs>',
        f'    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{a}" stop-opacity=".14"/>'
        f'<stop offset="1" stop-color="{a2}" stop-opacity=".05"/></linearGradient>',
        f'    <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{a2}"/></linearGradient>',
        f'    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
        f'<rect width="4" height="2" fill="#ffffff" opacity=".03"/></pattern>',
        f'  </defs>',
        f'  <rect width="{W}" height="{H}" rx="12" fill="#0a0e14"/>',
        f'  <rect width="{W}" height="{H}" rx="12" fill="url(#g)"/>',
        f'  <rect width="{W}" height="{H}" rx="12" fill="url(#scan)"/>',
        # grid
        "  " + "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="#ffffff" stroke-opacity=".04"/>'
                       for x in range(40, W, 40)),
        "  " + "".join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#ffffff" stroke-opacity=".04"/>'
                       for y in range(40, H, 40)),
        # HUD corner brackets
        f'  <path d="M14 34 V14 H44" fill="none" stroke="{a}" stroke-width="2"/>',
        f'  <path d="M{W-14} 34 V14 H{W-44}" fill="none" stroke="{a}" stroke-width="2"/>',
        f'  <path d="M14 {H-34} V{H-14} H44" fill="none" stroke="{a}" stroke-width="2"/>',
        f'  <path d="M{W-14} {H-34} V{H-14} H{W-44}" fill="none" stroke="{a}" stroke-width="2"/>',
        # header strip
        f'  <rect x="24" y="24" width="8" height="8" fill="{a}"/>',
        f'  <text x="40" y="32" font-family="Consolas,monospace" font-size="11" letter-spacing="2" '
        f'fill="{a}">{esc(card["tag"])}</text>',
        f'  <text x="{W-24}" y="32" text-anchor="end" font-family="Consolas,monospace" font-size="11" '
        f'fill="#5a6472">FILE-{W}-{card["lang"].upper()}</text>',
        # glyph art
        f'  <text x="28" y="86" font-family="Consolas,monospace" font-size="22" fill="{a}" '
        f'xml:space="preserve">{glyph}</text>',
        # title + desc
        f'  <text x="28" y="176" font-family="Consolas,monospace" font-weight="700" font-size="34" '
        f'fill="#e6edf3">{esc(card["name"])}</text>',
        f'  <text x="28" y="204" font-family="Consolas,monospace" font-size="14" '
        f'fill="#8b949e">{esc(card["desc"])}</text>',
        # language bar
        f'  <rect x="28" y="236" width="{W-56}" height="6" rx="3" fill="#1c2530"/>',
        f'  <rect x="28" y="236" width="{int((W-56) * int(card["pct"][:-1]) / 100)}" height="6" rx="3" fill="url(#bar)"/>',
        f'  <text x="28" y="266" font-family="Consolas,monospace" font-size="12" fill="{a}">{card["lang"]}</text>',
        f'  <text x="{W-28}" y="266" text-anchor="end" font-family="Consolas,monospace" font-size="12" '
        f'fill="#8b949e">operational</text>',
        # blinking cursor strip
        f'  <text x="28" y="{H-22}" font-family="Consolas,monospace" font-size="12" fill="#5a6472">'
        f'&gt;_ open case file</text>',
        f'  <text x="132" y="{H-22}" font-family="Consolas,monospace" font-size="12" fill="{a}">█'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.501;1" dur="1.4s" '
        f'repeatCount="indefinite"/></text>',
        "</svg>",
    ]
    return "\n".join(parts)


def main():
    os.makedirs("thumbs", exist_ok=True)
    for card in CARDS:
        path = f"thumbs/{card['name'].lower()}.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(build(card))
        print(f"  wrote {path}")


if __name__ == "__main__":
    main()
