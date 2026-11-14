"""Build the Stafbyte site from games.json.   usage: python build.py
Writes index.html, <slug>/index.html for every game with local_page=true, the Pixel Sudoku legal pages (from the game's
docs/legal/*.md), 404.html and favicon. To add a game: add an entry to games.json (copy an existing one), add its images to img/, run this."""
import os, re, json, html
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SUDOKU = os.path.join(os.path.dirname(HERE), "Sudoku")
EMAIL = "support@stafbyte.com"  # public studio contact (already published on the Street Kings site)
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
    ext = '' if g.get("local_page") else ' target="_blank" rel="noopener"'
    return f"""<article class="game">
  <div class="art"><img src="{g['hero']}" alt="{esc(g['name'])}"></div>
  <div class="body">
    <div class="title"><img src="{g['icon']}" alt=""><div><h3>{esc(g['name'])}</h3><p class="tag">{esc(g['tagline'])}</p></div></div>
    <p>{esc(g['blurb'])}</p>
    <div class="foot">
      <div class="meta"><span class="pill">{esc(g['genre'])}</span><span class="pill soon">{esc(g['status'])}</span></div>
      <div class="go"><a class="btn" href="{href}"{ext}>View game</a></div>
    </div>
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
    links = [(n, t) for n, t in [("privacy", "Privacy Policy"), ("terms", "Terms of Use"), ("ads", "About ads")] if n in g.get("legal", [])] + [tuple(x) for x in g.get("extra_pages", [])]
    if g.get("support") and not any(n == "support" for n, _ in links):
        links.append(("support", "Support"))
    legal = " &middot; ".join(f'<a href="{n}.html">{t}</a>' for n, t in links)
    imgs = "".join(f'<img src="../{p}" alt="">' for p in g.get("banners", []))
    banners = f'<section><div class="shots banners">{imgs}</div></section>' if imgs else ""
    discord = f'<section><h2>Join the community</h2><p>Chat with other players and hear about releases on <a href="{g["discord"]}" rel="noopener">our Discord</a>.</p></section>' if g.get("discord") else ""
    tester = '<a class="btn alt" href="testers.html">Become a tester</a>' if any(n == "testers" for n, _ in links) else ""
    store = f'<a class="btn" href="{g["play_url"]}" rel="noopener">Get it on Google Play</a>' if g.get("play_url") else f'<a class="btn" aria-disabled="true" href="#">{esc(g["status"])}</a>'
    body = f"""<main><div class="wrap">
<div class="crumbs"><a href="../index.html">Stafbyte</a> / {esc(g['name'])}</div>
<div class="page-hero"><img class="icon" src="../{g['icon']}" alt=""><div><h1>{esc(g['name'])}</h1><p>{esc(g['tagline'])}</p></div></div>
<section class="two"><div><p>{esc(g['description'])}</p><p>{esc(g.get('note', ''))}</p>{store} {tester}</div><div><img class="heroimg" src="../{g['hero']}" alt=""></div></section>
<section><h2>What you get</h2><div class="feat">{feats}</div></section>
<section><div class="shots">{shots}</div></section>
{banners}
{discord}
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


def import_pages(g):
    """Pages kept as plain HTML in _src/<slug>/ (Street Kings): keep their text, wrap it in the Stafbyte template."""
    src = os.path.join(HERE, g["import_from"])
    for n, t in g.get("extra_pages", []):
        raw = open(os.path.join(src, n + ".html"), encoding="utf8").read()
        inner = re.search(r"<main>(.*)</main>", raw, re.S).group(1)
        crumbs = f'<div class="crumbs"><a href="../index.html">Stafbyte</a> / <a href="index.html">{esc(g["name"])}</a> / {t}</div>'
        inner = inner.replace('<div class="wrap doc">', '<div class="wrap doc">' + crumbs, 1).replace('href="./"', 'href="index.html"')
        open(os.path.join(HERE, g["slug"], n + ".html"), "w", encoding="utf8").write(page(f"{g['name']} {t} | Stafbyte", t, f"<main>{inner}</main>", depth=1))


def support_page(g, email):
    faq = [("Where is my progress saved?", "On your device only. There are no accounts. If you uninstall the game or clear its data, the progress is gone and we cannot restore it."),
           ("Do I have to watch ads?", "The game is free and supported by ads. A short ad can appear between games, and you can watch optional video ads for extras. You can remove all ads with a one-time purchase."),
           ("I bought Remove Ads on another phone", "Open the Me tab and tap Restore purchase, signed in to the same Google account."),
           ("How do refunds work?", "Refunds are handled by Google Play under its refund policy. You can request one from your Play purchase history."),
           ("How do I delete my data?", "Everything is stored on your device. Clear the game's storage in Android settings or uninstall it. See the Privacy Policy for what Google collects for ads."),
           ("Where can I report a bug?", "Email us. Screenshots and your device model help a lot.")]
    det = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in faq)
    body = f'<main><div class="wrap doc"><div class="crumbs"><a href="../index.html">Stafbyte</a> / <a href="index.html">{esc(g["name"])}</a> / Support</div><h1>Support</h1><p>Need help? Email <a href="mailto:{email}">{email}</a>. Tell us your device, Android version and what happened.</p><h2>Common questions</h2>{det}</div></main>'
    open(os.path.join(HERE, g["slug"], "support.html"), "w", encoding="utf8").write(page(f"{g['name']} Support | Stafbyte", "Support", body, depth=1))


def legal_pages(g):
    src = os.path.join(SUDOKU, "docs", "legal")
    cp = os.path.join(src, "contact.txt")
    email = open(cp, encoding="utf8").read().strip() if os.path.exists(cp) else EMAIL
    for n, t in [("privacy", "Privacy Policy"), ("terms", "Terms of Use"), ("ads", "About ads")]:
        text = open(os.path.join(src, n + ".md"), encoding="utf8").read()
        text = text.replace("Email: CONTACT_EMAIL", f"Email: {email}")
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
            if g.get("import_from"): import_pages(g)
            if g.get("support"): support_page(g, EMAIL)
    body = '<main><div class="wrap hero"><h1>Page not found</h1><p>That page does not exist.</p><a class="btn" href="/">Back to Stafbyte</a></div></main>'
    open(os.path.join(HERE, "404.html"), "w", encoding="utf8").write(page("Not found | Stafbyte", "Page not found", body))
    print("site built")


if __name__ == "__main__":
    main()
