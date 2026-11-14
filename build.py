"""Build the Stafbyte site from games.json.   usage: python build.py
Writes index.html, <slug>/index.html for every game with local_page=true, the Pixel Sudoku legal pages (from the game's
docs/legal/*.md), 404.html and favicon. To add a game: add an entry to games.json (copy an existing one), add its images to img/, run this."""
import os, re, json, html
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SUDOKU = os.path.join(os.path.dirname(HERE), "Sudoku")
data = json.load(open(os.path.join(HERE, "games.json"), encoding="utf8"))
S, GAMES = data["studio"], data["games"]
esc = html.escape


def page(title, desc, body, depth=0, active=""):
    up = "../" * depth
    nav = "".join(f'<a href="{up}{href}">{label}</a>' for label, href in [("Games", "index.html#games"), ("About", "index.html#about")])
    return f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{up}img/logo.png">
<meta name="theme-color" content="#1b1938">
<link rel="icon" href="{up}img/favicon.png">
<link rel="stylesheet" href="{up}style.css">
</head>
<body>
<header class="site"><div class="wrap">
  <a class="brand" href="{up}index.html"><img src="{up}img/logo.png" alt="Stafbyte"></a>
  <nav>{nav}<a href="{esc(S['play_url'])}" rel="noopener">Google Play</a></nav>
</div></header>
{body}
<footer class="site"><div class="wrap">
  <img src="{up}img/logo.png" alt="Stafbyte">
  <div>&copy; 2026 Stafbyte. All rights reserved.</div>
  <div><a href="{esc(S['play_url'])}" rel="noopener">Our games on Google Play</a></div>
</div></footer>
</body>
</html>
"""


def card(g):
    href = g["slug"] + "/index.html" if g.get("local_page") else g.get("web_url") or "#"
    ext = ' target="_blank" rel="noopener"' if not g.get("local_page") else ""
    return f"""<article class="game">
  <div class="art"><img src="{g['hero']}" alt="{esc(g['name'])}"></div>
  <div class="body">
    <div class="title"><img src="{g['icon']}" alt=""><div><h3>{esc(g['name'])}</h3><p class="tag">{esc(g['tagline'])}</p></div></div>
    <p>{esc(g['blurb'])}</p>
    <div class="meta"><span class="pill">{esc(g['genre'])}</span><span class="pill soon">{esc(g['status'])}</span></div>
    <div class="go"><a class="btn" href="{href}"{ext}>{'Game page' if g.get('local_page') else 'Visit game site'}</a></div>
  </div>
</article>"""


def index():
    cards = "\n".join(card(g) for g in GAMES)
    body = f"""<main>
<div class="hero"><div class="wrap">
  <img class="logo" src="img/logo.png" alt="Stafbyte">
  <h1>{esc(S['tagline'])}</h1>
  <p>{esc(S['about'])}</p>
  <a class="btn" href="#games">See our games</a>
</div></div>
<section id="games"><div class="wrap">
  <h2>Our games</h2>
  <div class="grid">
{cards}
    <div class="soonbox"><h3>More on the way</h3><p>New games are in the works. Follow us on Google Play to see them first.</p></div>
  </div>
</div></section>
<section id="about"><div class="wrap two">
  <div><h2>About Stafbyte</h2><p>{esc(S['about'])}</p><p>Every game is made from scratch with its own art and music. Free to play, fair to play, and no account needed.</p>
  <a class="btn alt" href="{esc(S['play_url'])}" rel="noopener">Find us on Google Play</a></div>
  <div style="text-align:center"><img src="img/mascot.png" alt="" style="width:min(260px,70%)"></div>
</div></section>
</main>"""
    open(os.path.join(HERE, "index.html"), "w", encoding="utf8").write(page("Stafbyte | Mobile games", S["about"], body))


def game_page(g):
    feats = "".join(f"<div><h3>{esc(a)}</h3><p>{esc(b)}</p></div>" for a, b in g.get("features", []))
    shots = "".join(f'<img src="../{p}" alt="">' for p in g.get("images", []))
    legal = " &middot; ".join(f'<a href="{n}.html">{t}</a>' for n, t in [("privacy", "Privacy Policy"), ("terms", "Terms of Use"), ("ads", "About ads")] if n in g.get("legal", []))
    store = f'<a class="btn" href="{g["play_url"]}" rel="noopener">Get it on Google Play</a>' if g.get("play_url") else f'<a class="btn" aria-disabled="true" href="#">{esc(g["status"])}</a>'
    body = f"""<main><div class="wrap">
<div class="crumbs"><a href="../index.html">Stafbyte</a> / {esc(g['name'])}</div>
<div class="page-hero"><img class="icon" src="../{g['icon']}" alt=""><div><h1>{esc(g['name'])}</h1><p>{esc(g['tagline'])}</p></div></div>
<section class="two"><div><p>{esc(g['description'])}</p><p>{esc(g.get('note', ''))}</p>{store}</div><div><img class="heroimg" src="../{g['hero']}" alt=""></div></section>
<section><h2>What you get</h2><div class="feat">{feats}</div></section>
<section><div class="shots">{shots}</div></section>
<section><p class="tag">{legal}</p></section>
</div></main>"""
    os.makedirs(os.path.join(HERE, g["slug"]), exist_ok=True)
    open(os.path.join(HERE, g["slug"], "index.html"), "w", encoding="utf8").write(page(f"{g['name']} | Stafbyte", g["description"], body, depth=1))


def md_to_html(text):
    out, para, inlist = [], [], False
    def flush():
        if para: out.append("<p>" + link(" ".join(para)) + "</p>"); para.clear()
    def link(t): return re.sub(r"(https?://[^\s)]+)", r'<a href="\1" rel="noopener">\1</a>', esc(t))
    for line in text.splitlines():
        if line.startswith(("# ", "## ", "- ")) or not line.strip():
            flush()
            if inlist and not line.startswith("- "): out.append("</ul>"); inlist = False
        if line.startswith("# "): out.append(f"<h1>{esc(line[2:])}</h1>")
        elif line.startswith("## "): out.append(f"<h2>{esc(line[3:])}</h2>")
        elif line.startswith("- "):
            if not inlist: out.append("<ul>"); inlist = True
            out.append(f"<li>{link(line[2:])}</li>")
        elif line.strip(): para.append(line.strip())
    flush()
    if inlist: out.append("</ul>")
    return "\n".join(out)


def legal_pages(g):
    src = os.path.join(SUDOKU, "docs", "legal")
    contact = "the contact details on our Google Play developer page"
    cp = os.path.join(src, "contact.txt")
    email = open(cp, encoding="utf8").read().strip() if os.path.exists(cp) else ""
    for n, t in [("privacy", "Privacy Policy"), ("terms", "Terms of Use"), ("ads", "About ads")]:
        text = open(os.path.join(src, n + ".md"), encoding="utf8").read()
        text = text.replace("Email: CONTACT_EMAIL", f"Email: {email}" if email else "Contact: use the developer page below")
        body = f'<main><div class="wrap doc"><div class="crumbs"><a href="../index.html">Stafbyte</a> / <a href="index.html">{esc(g["name"])}</a> / {t}</div>{md_to_html(text)}</div></main>'
        open(os.path.join(HERE, g["slug"], n + ".html"), "w", encoding="utf8").write(page(f"{g['name']} {t} | Stafbyte", t, body, depth=1))


def main():
    Image.open(os.path.join(HERE, "img", "logo.png")).convert("RGBA").resize((64, 17), Image.NEAREST)  # sanity: logo readable
    # favicon: the logo's S on a dark tile
    lg = Image.open(os.path.join(HERE, "img", "logo.png")).convert("RGBA")
    side = max(lg.size)
    tile = Image.new("RGBA", (side, side), (27, 25, 56, 255))
    tile.alpha_composite(lg, ((side - lg.width) // 2, (side - lg.height) // 2))
    tile.resize((64, 64), Image.LANCZOS).save(os.path.join(HERE, "img", "favicon.png"))
    index()
    for g in GAMES:
        if g.get("local_page"):
            game_page(g)
            if g.get("legal"): legal_pages(g)
    body = '<main><div class="wrap hero"><h1>Page not found</h1><p>That page does not exist.</p><a class="btn" href="/">Back to Stafbyte</a></div></main>'
    open(os.path.join(HERE, "404.html"), "w", encoding="utf8").write(page("Not found | Stafbyte", "Page not found", body))
    print("site built")


if __name__ == "__main__":
    main()
