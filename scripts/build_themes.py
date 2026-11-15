#!/usr/bin/env python3
"""Build the themed profile README from profile-source.md (the lilac default).

  * recolors the SVGs in assets/ into assets/themes/<theme>/
  * writes README.md with every theme as a fold-out section, lilac open

Edit profile-source.md (not README.md); the workflow re-runs this script.
Lines the themes don't recognise are copied over unchanged.
"""
import colorsys
import os
import re
import urllib.parse as up

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")
SOURCE = os.path.join(ROOT, "profile-source.md")
ORDER = ["midnight", "sakura", "enchanted", "lilac"]  # lilac last: it is the one open by default
REPO_BLOB = "https://github.com/alam0604/alam0604/blob/main/themes/"
PROFILE = "https://github.com/alam0604"

# SVGs that already have a dark background (recolored without flipping light/dark)
DARK_SVGS = {"terminal-style.svg", "lilac-terminal.svg"}

START, END = "<!-- theme-switcher:start -->", "<!-- theme-switcher:end -->"


# ---------------------------------------------------------------- colors
def hex2hls(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hh, l, s = colorsys.rgb_to_hls(r, g, b)
    return hh * 360, s, l


def hls2hex(h, s, l, upper):
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360, max(0, min(1, l)), max(0, min(1, s)))
    out = "".join(f"{round(c * 255):02x}" for c in (r, g, b))
    return out.upper() if upper else out


def themable(h, s, l):
    """Lilac/purple tones and neutrals change; greens, golds, reds etc. stay."""
    return s <= 0.25 or 200 <= h <= 330


def midnight(h, s, l, dark_src):
    if dark_src:
        if s <= 0.25 and l > 0.96:
            return h, s, l
        if l < 0.2:
            return 215, 0.35, l * 0.8
        return 187 + (l - 0.7) * 60, max(s, 0.6), l
    if s <= 0.25 and 0.3 < l < 0.85:
        return 210, 0.15, l
    if l >= 0.85:
        return 215, 0.3, 0.06 + (1 - l) * 0.5
    if l < 0.5:
        return 180, 0.9, 1.05 - l * 0.6
    return 187 + (l - 0.65) * 100, max(s, 0.75), 0.35 + (l - 0.5) * 0.9


def sakura(h, s, l, dark_src):
    if s <= 0.05:
        return h, s, l
    return 335, min(1, s * 1.1 + 0.05), l


def enchanted(h, s, l, dark_src):
    if dark_src:
        if s <= 0.25 and l > 0.96:
            return h, s, l
        if l < 0.2:
            return 252, 0.6, l
        if l >= 0.85:
            return 45, 1, 0.88
        return 272, max(s, 0.65), l
    if s <= 0.25 and 0.3 < l < 0.85:
        return 255, 0.2, l
    if l >= 0.85:
        return 250, 0.55, 0.08 + (1 - l) * 0.6
    if l < 0.5:
        return 45, 0.95, 0.75
    return 272, max(s, 0.65), min(l + 0.05, 0.72)


def recolor_hex(hexstr, fn, dark_src):
    h, s, l = hex2hls(hexstr)
    if not themable(h, s, l):
        return hexstr
    upper = hexstr.lstrip("#") == hexstr.lstrip("#").upper()
    return hls2hex(*fn(h, s, l, dark_src), upper)


def recolor_svg(text, fn, dark_src):
    return re.sub(r"#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b",
                  lambda m: "#" + recolor_hex(m.group(1), fn, dark_src), text)


# ---------------------------------------------------------------- themes
THEMES = {
    "lilac": dict(label="✧ lilac", swatch="C9A7EB", link=PROFILE),
    "midnight": dict(
        label="⚡ midnight", swatch="0D1117", link=REPO_BLOB + "midnight.md", fn=midnight,
        glyph="⚡",
        capsule=("0:000000,50:0D1117,100:0B3D4A", "0:0B3D4A,50:0D1117,100:000000", "shark"),
        badges=(["0D1117"], "00E5FF"),
        url_overrides={"fontColor=74529B": "fontColor=00E5FF", "color=9B7BC7": "color=00E5FF",
                       "color=B79CED": "color=7DF9FF"},
        text={
            "hello, fellow explorer!": "welcome to the dark side.",
            "a tiny universe built with code ✧": "power, precision, and pipelines ⚡",
            "turning messy data into tiny bits of magic 🪄": "engineering data at scale. no excuses.",
            "building pipelines that don't wake anyone at 3am ☁️": "pipelines that run while the world sleeps 🌑",
            "always curious, always learning 🌱": "optimize. ship. repeat.",
            "Every project starts with a little curiosity.": "Every project starts with a problem worth crushing.",
            "pssst... there's a little something for you": "classified. open at your own risk",
            "Here's a tiny cookie for your journey 🍪": "Now go build something unstoppable 🖤",
            "✨ a little magic, a little code, and a lot of curiosity.": "⚡ built in the dark, shipped with precision.",
        }),
    "sakura": dict(
        label="🌸 sakura", swatch="FFB3CF", link=REPO_BLOB + "sakura.md", fn=sakura,
        glyph="🌸",
        url_overrides={},
        text={
            "hello, fellow explorer!": "hi there, lovely human!",
            "a tiny universe built with code ✧": "soft code, sweet data 🌸",
            "turning messy data into tiny bits of magic 🪄": "making data bloom, one pipeline at a time 🌷",
            "building pipelines that don't wake anyone at 3am ☁️": "soft skills, strong pipelines 💗",
            "Every project starts with a little curiosity.": "Every project starts with a little seed of curiosity.",
            "pssst... there's a little something for you": "psst... a little petal fell here for you",
            "Here's a tiny cookie for your journey 🍪": "Here's a tiny flower for your journey 🌷",
            "✨ a little magic, a little code, and a lot of curiosity.": "🌸 a little bloom, a little code, and a lot of curiosity.",
        }),
    "enchanted": dict(
        label="🔮 enchanted", swatch="4B2A7B", link=REPO_BLOB + "enchanted.md", fn=enchanted,
        glyph="🔮",
        capsule=("0:0B0B2B,40:3B1E6E,75:7B3FA0,100:F5C26B", "0:F5C26B,25:7B3FA0,60:3B1E6E,100:0B0B2B", "egg"),
        badges=(["2E1A47", "4B2A7B"], "FFE29A"),
        url_overrides={"fontColor=74529B": "fontColor=FFE29A", "animation=fadeIn": "animation=twinkling",
                       "color=9B7BC7": "color=F5C26B", "color=B79CED": "color=C9A0FF"},
        text={
            "hello, fellow explorer!": "welcome, traveler of realms",
            "a tiny universe built with code ✧": "where data turns into spells 🔮",
            "turning messy data into tiny bits of magic 🪄": "casting spells on messy data ✨",
            "building pipelines that don't wake anyone at 3am ☁️": "conjuring pipelines under the moonlight 🌙",
            "always curious, always learning 🌱": "the curious find the magic 🪄",
            "Every project starts with a little curiosity.": "Every spell starts with a little curiosity.",
            "pssst... there's a little something for you": "a sealed scroll... dare to open it?",
            "Here's a tiny cookie for your journey 🍪": "Here's a little stardust for your journey ✨",
            "✨ a little magic, a little code, and a lot of curiosity.": "🌙 may your pipelines never fail and your stars always align.",
        }),
}


def badge(label, msg, color):
    q = lambda s: up.quote(s, safe="")
    return f"https://img.shields.io/badge/{q(label)}-{q(msg)}-{color}?style=for-the-badge&labelColor={color}"


def switcher(current):
    lines = [START, '<div align="center">', "<sub>✧ pick a vibe ✧</sub><br/>"]
    for key, t in THEMES.items():
        msg = "you're here" if key == current else ("default" if key == "lilac" else "switch")
        lines.append(f'<a href="{t["link"]}"><img src="{badge(t["label"], msg, t["swatch"])}" alt="{key} theme"/></a>')
    lines += ["</div>", END]
    return "\n".join(lines)


def set_switcher(md, current):
    block = switcher(current)
    if START in md and END in md:
        return re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, md, flags=re.S)
    return block + "\n\n" + md


# ---------------------------------------------------------------- markdown
URL_HEX = re.compile(r"(?<=[=:\-])([0-9A-Fa-f]{6})(?=[?&,;\"')\s]|$)")
URL_RE = re.compile(r"https://(?:img\.shields\.io|capsule-render\.vercel\.app|readme-typing-svg\.demolab\.com)[^\s\")]*")


def norm(s):
    return s.replace("\ufe0f", "").strip()


def retext(piece, t, plus):
    """Swap one URL-encoded text piece (header text or a typing line)."""
    dec = up.unquote_plus(piece) if plus else up.unquote(piece)
    table = {norm(k): v for k, v in t["text"].items()}
    new = table.get(norm(dec), dec.replace("✧", t["glyph"]))
    if new == dec:
        return piece
    e = up.quote(new, safe="!'")
    return e.replace("%20", "+") if plus else e


def theme_url(url, t, n=[0]):
    if "capsule-render" in url and t.get("capsule"):
        head, foot, shape = t["capsule"]  # solid shapes: "waving" is see-through
        url = re.sub(r"type=[a-z]+", "type=" + shape, url)
        url = re.sub(r"color=[0-9A-Fa-f:,]+", "color=" + (foot if "section=footer" in url else head), url)
    if "img.shields.io/badge/" in url and t.get("badges"):
        bgs, logo = t["badges"]
        bg = bgs[n[0] % len(bgs)]
        n[0] += 1
        url = re.sub(r"-[0-9A-Fa-f]{6}\?", f"-{bg}?", url, count=1)
        url = re.sub(r"logoColor=[0-9A-Za-z]+", f"logoColor={logo}", url)
        return url
    held = {}
    for i, (old, new) in enumerate(t["url_overrides"].items()):
        if old in url:
            token = f"@@{i}@@"
            url = url.replace(old, token)
            held[token] = new
    if not ("capsule-render" in url and t.get("capsule")):
        url = URL_HEX.sub(lambda m: recolor_hex(m.group(1), t["fn"], False), url)
    plus = "readme-typing-svg" in url
    url = re.sub(r"(?<=[?&])(text|desc|lines)=([^&\"]*)",
                 lambda m: m.group(1) + "=" + ";".join(retext(p, t, plus) for p in m.group(2).split(";")),
                 url)
    for token, new in held.items():
        url = url.replace(token, new)
    return url


def build_md(md, key, t):
    """Restyle the lilac source into one theme (image paths relative to the repo root)."""
    md = URL_RE.sub(lambda m: theme_url(m.group(0), t), md)
    for old, new in t["text"].items():
        md = md.replace(old, new).replace(norm(old), new)
    md = md.replace("✧ apparently my life is all about ✧", f"{t['glyph']} apparently my life is all about {t['glyph']}")
    md = re.sub(r'src="assets/([^"/]+\.svg)"', rf'src="assets/themes/{key}/\1"', md)
    return md.replace("My lilac ", "My ").replace("little lilac ", "little ")


def section(key, body):
    t = THEMES[key]
    is_default = key == "lilac"
    msg = "default" if is_default else "tap to switch"
    button = f'<img src="{badge(t["label"], msg, t["swatch"])}" alt="{key} theme"/>'
    return (f'<details name="vibe"{" open" if is_default else ""}>\n'
            f"<summary>{button}</summary>\n\n{body.strip()}\n\n</details>\n")


def main():
    if not os.path.exists(SOURCE):  # first run: the current README becomes the source
        with open(README, encoding="utf-8") as f:
            md = f.read()
        md = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\s*", "", md, flags=re.S)
        with open(SOURCE, "w", encoding="utf-8") as f:
            f.write(md)
    with open(SOURCE, encoding="utf-8") as f:
        src = f.read()

    assets = os.path.join(ROOT, "assets")
    svgs = [n for n in os.listdir(assets) if n.endswith(".svg")]
    for key, t in THEMES.items():
        if key == "lilac":
            continue
        out_dir = os.path.join(assets, "themes", key)
        os.makedirs(out_dir, exist_ok=True)
        for name in svgs:
            with open(os.path.join(assets, name), encoding="utf-8") as f:
                svg = f.read()
            with open(os.path.join(out_dir, name), "w", encoding="utf-8") as f:
                f.write(recolor_svg(svg, t["fn"], name in DARK_SVGS))

    parts = ["<!-- ✏️ generated by scripts/build_themes.py: edit profile-source.md instead -->",
             '<div align="center"><sub>✧ pick a vibe ✧ tap a theme to open it right here ✧</sub></div>\n']
    for key in ORDER:
        parts.append(section(key, src if key == "lilac" else build_md(src, key, THEMES[key])))
    with open(README, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))

    # the old one-page-per-theme files are no longer used
    old = os.path.join(ROOT, "themes")
    if os.path.isdir(old):
        for n in os.listdir(old):
            os.remove(os.path.join(old, n))
        os.rmdir(old)
    print("built README.md with", ", ".join(ORDER))


if __name__ == "__main__":
    main()
