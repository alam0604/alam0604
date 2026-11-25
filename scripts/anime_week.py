#!/usr/bin/env python3
"""Draw the lilac "anime of the week" card from AniList.

Picks the 3 best-rated anime that are airing right now, ranked by AniList's
average user score, and only counting shows with enough ratings and reviews
to be trustworthy. Runs daily from the workflow but only changes the picks
once per week (the week is stored in assets/anime-week.json).
If AniList can't be reached, the existing card is left untouched.
"""
import datetime as dt
import html
import json
import os
import sys
import urllib.request

CARD = "assets/anime-week.svg"
STATE = "assets/anime-week.json"
PICKS = 3
MIN_POPULARITY = 15000  # people who added it to a list: filters out obscure shows with inflated scores

QUERY = """query {
  Page(perPage: 50) {
    media(type: ANIME, status: RELEASING, isAdult: false, sort: SCORE_DESC,
          format_in: [TV, TV_SHORT, ONA]) {
      title { english romaji }
      averageScore popularity genres episodes nextAiringEpisode { episode }
      siteUrl season seasonYear
      reviews(perPage: 1) { pageInfo { total } }
    }
  }
}"""

F = "font-family=\"'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif\""
BG, STROKE, HEAD, TX, MUTED = "#fbf7ff", "#dcc5f2", "#9b82c9", "#55406f", "#8e8aa3"
L1, L2, L3, DARK = "#efe4fb", "#d4baf2", "#b79ced", "#74529b"


def fetch():
    req = urllib.request.Request(
        "https://graphql.anilist.co",
        data=json.dumps({"query": QUERY}).encode(),
        headers={"Content-Type": "application/json", "Accept": "application/json",
                 "User-Agent": "alam0604-profile-card"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]["Page"]["media"]


def choose(media):
    good = [m for m in media if m.get("averageScore") and (m.get("popularity") or 0) >= MIN_POPULARITY]
    # rating first; reviews break ties so the more-discussed show wins
    good.sort(key=lambda m: (m["averageScore"], m["reviews"]["pageInfo"]["total"]), reverse=True)
    return good[:PICKS]


def t(x, y, s, size, fill, weight=400, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{html.escape(str(s))}</text>')


def clip(s, n):
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def draw(picks, week_label):
    W, H = 800, 268
    medals = ["🥇", "🥈", "🥉"]
    fills = [L2, L1, L1]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" {F} '
           f'role="img" aria-label="Anime of the week: ' +
           html.escape(", ".join(p["name"] for p in picks)) + '">',
           f'<rect x="1" y="1" width="798" height="{H-2}" rx="14" fill="{BG}" stroke="{STROKE}" stroke-width="1.5"/>',
           t(28, 36, "✧ anime of the week", 15, HEAD, 600),
           t(772, 36, week_label, 12.5, MUTED, 600, "end")]
    cw, gap = 236, 18
    for i, p in enumerate(picks):
        x, y = 28 + i * (cw + gap), 56
        d = 0.5 + i * 0.15  # staggered fade-in; cards stay visible where SVG animation isn't supported
        out.append(f'<g><animate attributeName="opacity" values="0;0;1" keyTimes="0;{i*0.15/d:.2f};1" '
                   f'dur="{d:.2f}s" fill="freeze"/>')
        out.append(f'<rect x="{x}" y="{y}" width="{cw}" height="164" rx="12" fill="{fills[i]}" stroke="{STROKE}"/>')
        out.append(t(x + 16, y + 30, medals[i], 20, TX))
        out.append(t(x + cw - 16, y + 30, f"★ {p['score'] / 10:.1f}", 18, DARK, 700, "end"))
        out.append(t(x + 16, y + 62, clip(p["name"], 24), 15.5, TX, 700))
        out.append(t(x + 16, y + 84, clip(" · ".join(p["genres"][:3]).lower(), 34), 12, DARK))
        # score bar
        out.append(f'<rect x="{x+16}" y="{y+100}" width="{cw-32}" height="7" rx="3.5" fill="#f7f0fd"/>')
        out.append(f'<rect x="{x+16}" y="{y+100}" width="{(cw-32)*p["score"]/100:.0f}" height="7" rx="3.5" fill="{L3}"/>')
        out.append(t(x + 16, y + 130, f"{p['fans']:,} fans · {p['reviews']} reviews", 12, MUTED))
        out.append(t(x + 16, y + 150, p["ep"], 12, MUTED))
        out.append("</g>")
    out.append(t(28, H - 24, "✧ top-rated anime airing right now, by AniList user scores · refreshed every Monday", 12, MUTED))
    out.append("</svg>")
    return "".join(out)


def main():
    today = dt.date.today()
    year, week, _ = today.isocalendar()
    key = f"{year}-W{week:02d}"
    if os.path.exists(STATE) and os.path.exists(CARD) and "--force" not in sys.argv:
        if json.load(open(STATE, encoding="utf-8")).get("week") == key:
            print("anime of the week already picked for", key)
            return
    try:
        media = fetch()
    except Exception as e:  # keep the old card rather than failing the whole workflow
        body = e.read().decode(errors="replace")[:500] if hasattr(e, "read") else ""
        print("AniList unreachable, keeping the old card:", e, body)
        return
    picks = []
    for m in choose(media):
        nxt = (m.get("nextAiringEpisode") or {}).get("episode")
        total = m.get("episodes")
        ep = f"episode {nxt - 1} out" if nxt else "airing now"
        if nxt and total:
            ep += f" of {total}"
        picks.append({"name": m["title"]["english"] or m["title"]["romaji"], "score": m["averageScore"],
                      "fans": m["popularity"], "reviews": m["reviews"]["pageInfo"]["total"],
                      "genres": m.get("genres") or [], "ep": ep, "url": m["siteUrl"]})
    if not picks:
        print("no picks found, keeping the old card")
        return
    monday = today - dt.timedelta(days=today.weekday())
    with open(CARD, "w", encoding="utf-8") as f:
        f.write(draw(picks, f"week of {monday.day} {monday:%b}"))
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump({"week": key, "picks": picks}, f, ensure_ascii=False, indent=2)
    print("anime of the week:", ", ".join(p["name"] for p in picks))


if __name__ == "__main__":
    main()
