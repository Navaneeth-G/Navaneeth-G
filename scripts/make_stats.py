import os, json, html, urllib.request
from datetime import datetime, timezone

USER = os.environ.get("GH_USER", "Navaneeth-G")
TOKEN = os.environ.get("GH_TOKEN", "")

def api(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "dashboard-script"}
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    req = urllib.request.Request("https://api.github.com" + path, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

user = api(f"/users/{USER}")
repos = api(f"/users/{USER}/repos?per_page=100&type=owner&sort=pushed")
own = [r for r in repos if not r["fork"]]
stars = sum(r["stargazers_count"] for r in own)

langs = {}
for r in own:
    try:
        for k, v in api(f"/repos/{USER}/{r['name']}/languages").items():
            langs[k] = langs.get(k, 0) + v
    except Exception:
        pass
total = sum(langs.values()) or 1
top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]

COLORS = {"Python": "#3572A5", "JavaScript": "#f1e05a", "HTML": "#e34c26", "CSS": "#563d7c",
          "Java": "#b07219", "C": "#9aa0a6", "Jupyter Notebook": "#DA5B0B", "Shell": "#89e051",
          "TypeScript": "#3178c6", "C++": "#f34b7d", "SQL": "#4479A1"}

def fmt(d):
    return datetime.strptime(d, "%Y-%m-%dT%H:%M:%SZ").strftime("%d %b %Y")

recent = sorted(own, key=lambda r: r["pushed_at"], reverse=True)[:4]
last_push = fmt(recent[0]["pushed_at"]) if recent else "n/a"

W, M = 760, 24
tiles = [("Public repos", str(user["public_repos"])), ("Stars earned", str(stars)),
         ("Followers", str(user["followers"])), ("Last push", last_push)]
out = []
a = out.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="380" viewBox="0 0 {W} 380" role="img" aria-label="GitHub dashboard for {html.escape(USER)}">')
a('<rect x="0.5" y="0.5" width="759" height="379" rx="14" fill="#0D1117" stroke="#1E3A5F"/>')
a(f'<text x="{M}" y="38" fill="#f0f0ff" font-family="Segoe UI,Arial,sans-serif" font-size="18" font-weight="700">GitHub Dashboard</text>')
a(f'<text x="{W-M}" y="38" fill="#5a5a7a" font-family="Segoe UI,Arial,sans-serif" font-size="12" text-anchor="end">@{html.escape(USER)}</text>')
tw, gap = 164, 18.67
for i, (label, val) in enumerate(tiles):
    x = M + i * (tw + gap)
    a(f'<rect x="{x:.1f}" y="56" width="{tw}" height="64" rx="10" fill="#0f0f20" stroke="#1E3A5F"/>')
    size = 22 if len(val) < 8 else 16
    a(f'<text x="{x+14:.1f}" y="88" fill="#00d4ff" font-family="Segoe UI,Arial,sans-serif" font-size="{size}" font-weight="700">{html.escape(val)}</text>')
    a(f'<text x="{x+14:.1f}" y="108" fill="#9090b0" font-family="Segoe UI,Arial,sans-serif" font-size="11">{label}</text>')
a(f'<text x="{M}" y="150" fill="#9090b0" font-family="Segoe UI,Arial,sans-serif" font-size="11" letter-spacing="1.5">LANGUAGES (BY CODE VOLUME)</text>')
x = M
bar_w = W - 2 * M
a(f'<clipPath id="bar"><rect x="{M}" y="160" width="{bar_w}" height="10" rx="5"/></clipPath><g clip-path="url(#bar)">')
for name, v in top:
    w = bar_w * v / total
    a(f'<rect x="{x:.1f}" y="160" width="{w:.1f}" height="10" fill="{COLORS.get(name, "#7c8fff")}"/>')
    x += w
a('</g>')
lx = M
for name, v in top:
    a(f'<circle cx="{lx+5}" cy="192" r="5" fill="{COLORS.get(name, "#7c8fff")}"/>')
    label = f'{html.escape(name)} {100*v/total:.1f}%'
    a(f'<text x="{lx+16}" y="196" fill="#9090b0" font-family="Segoe UI,Arial,sans-serif" font-size="12">{label}</text>')
    lx += 16 + 7.2 * len(label) + 16
a(f'<text x="{M}" y="236" fill="#9090b0" font-family="Segoe UI,Arial,sans-serif" font-size="11" letter-spacing="1.5">RECENTLY UPDATED</text>')
y = 262
for r in recent:
    a(f'<text x="{M}" y="{y}" fill="#f0f0ff" font-family="Segoe UI,Arial,sans-serif" font-size="13" font-weight="600">{html.escape(r["name"])}</text>')
    lang = r["language"] or "n/a"
    a(f'<circle cx="300" cy="{y-4}" r="4" fill="{COLORS.get(lang, "#7c8fff")}"/>')
    a(f'<text x="311" y="{y}" fill="#9090b0" font-family="Segoe UI,Arial,sans-serif" font-size="12">{html.escape(lang)}</text>')
    a(f'<text x="440" y="{y}" fill="#9090b0" font-family="Segoe UI,Arial,sans-serif" font-size="12">★ {r["stargazers_count"]}</text>')
    a(f'<text x="{W-M}" y="{y}" fill="#5a5a7a" font-family="Segoe UI,Arial,sans-serif" font-size="12" text-anchor="end">pushed {fmt(r["pushed_at"])}</text>')
    y += 26
today = datetime.now(timezone.utc).strftime("%d %b %Y")
a(f'<text x="{W-M}" y="368" fill="#5a5a7a" font-family="Segoe UI,Arial,sans-serif" font-size="10" text-anchor="end">Generated from the GitHub API on {today} (public repos only)</text>')
a('</svg>')
open("dashboard.svg", "w", encoding="utf-8").write("\n".join(out))
