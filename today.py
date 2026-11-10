"""Generate the boot-sequence terminal SVG header (dark + light) for the profile README."""

from datetime import datetime, timezone


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generate_svg(theme="dark"):
    # ── Colour palette ──────────────────────────────────────────────────
    if theme == "dark":
        bg      = "#0d1117"
        border  = "#30363d"
        user    = "#58a6ff"   # ghost@shellghostt
        dir_c   = "#79c0ff"   # ~
        prompt  = "#3fb950"   # $, progress fill, focus values
        text    = "#c9d1d9"
        muted   = "#8b949e"
    else:
        bg      = "#f6f8fa"
        border  = "#d0d7de"
        user    = "#0550ae"
        dir_c   = "#0969da"
        prompt  = "#1a7f37"
        text    = "#24292f"
        muted   = "#57606a"

    head = [
        ("ghost@shellghostt", "user"),
        (":",                  "muted"),
        ("~",                  "dir"),
        ("$ ",                 "prompt"),
    ]

    # ── Projects listing (name column padded for alignment) ─────────────
    projects = [
        ("agent-scan/",     "security scanner for AI agents & MCP"),
        ("de-caff/",        "js reverse-engineering & audit pipeline"),
        ("webvac/",         "async scraper for js-heavy sites"),
    ]

    # ── Boot sequence lines ─────────────────────────────────────────────
    # Each line is a list of (text, style) segments; [] is a blank line.
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
        [("[", "muted"), ("■■■■■■■■", "prompt"), ("□□", "muted"), ("] ", "muted"),
         ("loading next challenge...", "muted")],
        [],
        [(f"last login: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", "muted")],
    ]

    colour_map = {
        "user":   user,
        "dir":    dir_c,
        "prompt": prompt,
        "cmd":    text,
        "text":   text,
        "muted":  muted,
    }

    # ── Layout maths ────────────────────────────────────────────────────
    lh      = 20          # line height px
    fs      = 13          # font size px
    pad     = 20          # outer padding
    width   = 560         # fixed card width
    total_h = len(lines) * lh + pad * 2

    svg = [
        f'<svg width="{width}" height="{total_h}" viewBox="0 0 {width} {total_h}" '
        f'xmlns="http://www.w3.org/2000/svg">'
    ]
    svg.append(
        f'  <rect width="{width}" height="{total_h}" rx="10" '
        f'fill="{bg}" stroke="{border}" stroke-width="1"/>'
    )
    svg.append(
        f'  <style>text{{font-family:"SFMono-Regular","Consolas","Liberation Mono",'
        f'"Courier New",monospace;font-size:{fs}px;white-space:pre;}}</style>'
    )

    y0 = pad + lh
    for i, line in enumerate(lines):
        y = y0 + i * lh
        x = pad
        for content, style in line:
            svg.append(
                f'  <text x="{x}" y="{y}" fill="{colour_map[style]}">{esc(content)}</text>'
            )
            # 0.62 is a good monospace advance-width factor for 13px
            x += round(len(content) * fs * 0.62)

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    for theme in ("dark", "light"):
        path = f"{theme}_mode.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(generate_svg(theme))
        print(f"  wrote {path}")


if __name__ == "__main__":
    main()
