import requests
import os
from datetime import datetime

USERNAME = "Shellghostt"
TOKEN = os.environ.get("GH_TOKEN", "")

HEADERS = {"Authorization": f"token {TOKEN}"} if TOKEN else {}


def get_user_data():
    r = requests.get(f"https://api.github.com/users/{USERNAME}", headers=HEADERS)
    r.raise_for_status()
    return r.json()


def get_total_stars(repos_count):
    stars = 0
    page = 1
    while True:
        r = requests.get(
            f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}",
            headers=HEADERS,
        )
        repos = r.json()
        if not repos:
            break
        stars += sum(repo.get("stargazers_count", 0) for repo in repos)
        page += 1
    return stars


def get_commit_count():
    """Estimate total commits via the search API."""
    r = requests.get(
        f"https://api.github.com/search/commits?q=author:{USERNAME}",
        headers={**HEADERS, "Accept": "application/vnd.github.cloak-preview"},
    )
    if r.status_code == 200:
        return r.json().get("total_count", 0)
    return 0


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def dot(label, value, total_width=38):
    """Format a label....value line like neofetch."""
    label = label + " "
    dots = "." * (total_width - len(label) - len(str(value)))
    return f"{label}{dots} {value}"


def generate_svg(user, stars, commits, theme="dark"):
    repos = user.get("public_repos", 0)
    followers = user.get("followers", 0)
    following = user.get("following", 0)
    updated = datetime.utcnow().strftime("%Y-%m-%d")

    # ── Colour palettes ──────────────────────────────────────────────────
    if theme == "dark":
        bg      = "#0d1117"
        border  = "#30363d"
        title   = "#58a6ff"
        accent  = "#79c0ff"
        muted   = "#8b949e"
        normal  = "#c9d1d9"
        green   = "#3fb950"
        red     = "#f85149"
        yellow  = "#d29922"
    else:
        bg      = "#f6f8fa"
        border  = "#d0d7de"
        title   = "#0550ae"
        accent  = "#0969da"
        muted   = "#57606a"
        normal  = "#24292f"
        green   = "#1a7f37"
        red     = "#cf222e"
        yellow  = "#9a6700"

    # ── Ghost ASCII art (left panel) ─────────────────────────────────────
    ghost = [
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

    # ── Info panel lines (right panel) ───────────────────────────────────
    sep = "─" * 36
    half = "─" * 15

    info = [
        ("Shellghostt@github",  "title"),
        (sep,                   "muted"),
        (dot("Name",   "Adityaaa"),                     "normal"),
        (dot("Shell",  "bash / zsh"),                   "normal"),
        (dot("OS",     "Linux / Windows"),               "normal"),
        ("",                    ""),
        (f"{half} Languages {half}", "muted"),
        (dot("Primary", "Python, TypeScript, Kotlin"),  "accent"),
        (dot("Web",     "JavaScript, HTML, CSS"),       "accent"),
        ("",                    ""),
        (f"{half} Projects {half}",  "muted"),
        (dot("NYRA",        "Yoga AI Recognition (Py)"), "green"),
        (dot("De-Caff",     "JS Security Auditing (TS)"), "green"),
        (dot("ChatApp",     "Mobile chat app (Kotlin)"), "green"),
        ("",                    ""),
        (f"{half} Stats {half}",     "muted"),
        (dot("Repos",     repos),                       "normal"),
        (dot("Stars",     stars),                       "yellow"),
        (dot("Commits",   commits),                     "normal"),
        (dot("Followers", f"{followers}  |  Following: {following}"), "normal"),
        ("",                    ""),
        (dot("Updated", updated),                       "muted"),
    ]

    # ── Layout maths ─────────────────────────────────────────────────────
    lh      = 19          # line height px
    fs      = 12          # font size px
    pad     = 18          # outer padding
    lgap    = 24          # gap between columns
    lw      = 196         # left column width
    rw      = 450         # right column width
    total_w = pad + lw + lgap + rw + pad
    total_h = max(len(ghost), len(info)) * lh + pad * 2 + 10

    colour_map = {
        "title":  title,
        "accent": accent,
        "muted":  muted,
        "normal": normal,
        "green":  green,
        "red":    red,
        "yellow": yellow,
        "":       "transparent",
    }

    lines = []
    lines.append(
        f'<svg width="{total_w}" height="{total_h}" viewBox="0 0 {total_w} {total_h}" '
        f'xmlns="http://www.w3.org/2000/svg">'
    )
    # Background + border
    lines.append(
        f'  <rect width="{total_w}" height="{total_h}" rx="8" '
        f'fill="{bg}" stroke="{border}" stroke-width="1"/>'
    )
    # Font style
    lines.append(
        f'  <style>text{{font-family:"SFMono-Regular","Consolas","Liberation Mono","Courier New",monospace;'
        f'font-size:{fs}px;white-space:pre;}}</style>'
    )

    y0 = pad + lh  # first baseline

    # Left: ghost
    for i, row in enumerate(ghost):
        y = y0 + i * lh
        lines.append(
            f'  <text x="{pad}" y="{y}" fill="{accent}">{esc(row)}</text>'
        )

    # Right: info
    rx = pad + lw + lgap
    for i, (content, style) in enumerate(info):
        if not content:
            continue
        y = y0 + i * lh
        c = colour_map.get(style, normal)
        lines.append(
            f'  <text x="{rx}" y="{y}" fill="{c}">{esc(content)}</text>'
        )

    lines.append("</svg>")
    return "\n".join(lines)


def main():
    print("Fetching GitHub data…")
    user    = get_user_data()
    stars   = get_total_stars(user.get("public_repos", 0))
    commits = get_commit_count()

    print(f"  Repos: {user['public_repos']}  Stars: {stars}  Commits: {commits}")

    for theme in ("dark", "light"):
        svg  = generate_svg(user, stars, commits, theme)
        path = f"{theme}_mode.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"  Written {path}")

    print("Done!")


if __name__ == "__main__":
    main()
