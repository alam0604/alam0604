#!/usr/bin/env python3
"""Redraw the lilac LeetCode stats card from live LeetCode numbers.

Reads the username from the LEETCODE_USERNAME environment variable
(a repository secret), so it never appears in the repo.
If LeetCode can't be reached, the existing card is left untouched.
"""
import json
import math
import os
import re
import sys
import urllib.request

CARD = "assets/leetcode-stats-lilac.svg"
README = "README.md"

QUERY = """query($u: String!) {
  matchedUser(username: $u) { submitStatsGlobal { acSubmissionNum { difficulty count } } }
}"""


def fetch(username):
    req = urllib.request.Request(
        "https://leetcode.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"u": username}}).encode(),
        headers={
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com/",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    rows = data["data"]["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]
    return {row["difficulty"]: row["count"] for row in rows}


def text(x, y, s, size, fill, weight=400, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}" {extra}>{s}</text>')


def render(so):
    BG, BORDER, INK, SUB, TRACK = "#fbf7ff", "#dcc5f2", "#55406f", "#8e8aa3", "#efe4fb"
    COL = {"Easy": "#d4baf2", "Medium": "#b79ced", "Hard": "#74529b"}
    W, H, cx, cy, r = 800, 230, 130, 122, 62
    C = 2 * math.pi * r
    total = max(so["All"], 1)
    widest = max(so["Easy"], so["Medium"], so["Hard"], 1)

    ring, off = "", 0.0
    for k in ("Easy", "Medium", "Hard"):
        L = C * so[k] / total
        if L > 0:
            ring += (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{COL[k]}" stroke-width="13" '
                     f'stroke-linecap="round" stroke-dasharray="{max(L - 6, 0.1):.1f} {C - L + 6:.1f}" '
                     f'stroke-dashoffset="{-off - 3:.1f}" transform="rotate(-90 {cx} {cy})"/>')
        off += L

    rows = ""
    for i, k in enumerate(("Easy", "Medium", "Hard")):
        y = 78 + i * 50
        bw = f"{452 * so[k] / widest:.1f}"
        rows += (f'<circle cx="292" cy="{y - 5}" r="6" fill="{COL[k]}"/>'
                 + text(306, y, k, 15, INK, 600)
                 + text(712, y, so[k], 17, INK, 700, "end")
                 + text(744, y, f"{round(100 * so[k] / total)}%", 12, SUB, 400, "end")
                 + f'<rect x="292" y="{y + 11}" width="452" height="9" rx="4.5" fill="{TRACK}"/>'
                 + f'<rect x="292" y="{y + 11}" width="{bw}" height="9" rx="4.5" fill="{COL[k]}">'
                 + f'<animate attributeName="width" from="0" to="{bw}" dur="1.2s" fill="freeze"/></rect>')

    label = (f"LeetCode: {so['All']} problems solved, {so['Easy']} easy, "
             f"{so['Medium']} medium, {so['Hard']} hard")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f"font-family=\"'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif\" role=\"img\" aria-label=\"{label}\">\n"
           f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>\n'
           + text(28, 36, "✧ leetcode, in numbers", 15, "#9b82c9", 600)
           + text(W - 28, 36, "✧", 15, "#c9a7eb", 400, "end") + "\n"
           + f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{TRACK}" stroke-width="13"/>{ring}\n'
           + text(cx, cy + 6, so["All"], 34, INK, 700, "middle")
           + text(cx, cy + 28, "problems solved", 11, SUB, 400, "middle") + "\n"
           + rows + "\n</svg>\n")
    return svg, label


def main():
    username = os.environ.get("LEETCODE_USERNAME", "").strip()
    if not username:
        print("LEETCODE_USERNAME secret is not set; leaving the card as it is.")
        return 0
    try:
        so = fetch(username)
        so = {k: int(so[k]) for k in ("All", "Easy", "Medium", "Hard")}
    except Exception as e:  # LeetCode down or blocking us: keep the old card
        print(f"Could not fetch LeetCode stats ({type(e).__name__}); leaving the card as it is.")
        return 0

    svg, label = render(so)
    with open(CARD, "w", encoding="utf-8") as f:
        f.write(svg)

    # keep the README alt text in sync with the numbers
    if os.path.exists(README):
        with open(README, encoding="utf-8") as f:
            md = f.read()
        md2 = re.sub(r'alt="LeetCode: [^"]*"', f'alt="{label}"', md)
        if md2 != md:
            with open(README, "w", encoding="utf-8") as f:
                f.write(md2)

    print(f"Card updated: {so['All']} solved ({so['Easy']} / {so['Medium']} / {so['Hard']}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
