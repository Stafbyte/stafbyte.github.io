# stafbyte.github.io (Stafbyte studio site)

Static site, no build tools needed to host it. `python build.py` regenerates the pages from `games.json`.

## Put it online
1. GitHub: create the organization `stafbyte`, then a PUBLIC repo named exactly `stafbyte.github.io`.
2. In this folder:
   ```
   git init -b main
   git add .
   git commit -m "Stafbyte site"
   git remote add origin https://github.com/stafbyte/stafbyte.github.io.git
   git push -u origin main
   ```
3. Repo Settings > Pages > Deploy from branch `main` / root. Live at https://stafbyte.github.io within minutes.

## Add a new game
1. Copy an entry in `games.json` (set `local_page: true` for a page here, or `web_url` to link to the game's own site like Street Kings).
2. Put its images in `img/`, run `python build.py`, commit and push.

## Notes
- Pixel Sudoku legal pages are built from `../Sudoku/docs/legal/*.md` (run `python build.py` again after editing them). Privacy URL for Play Console: https://stafbyte.github.io/pixel-sudoku/privacy.html
- Contact email: put it in `../Sudoku/docs/legal/contact.txt` and rebuild; until then the policy points to the Google Play developer page.
- Street Kings links to the existing https://streetkingsidle.github.io/ ; set `play_url` once the games are live on Google Play.
- Preview locally: `python -m http.server 5191` then open http://127.0.0.1:5191
