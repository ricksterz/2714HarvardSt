# 2714 Harvard Street — Marketing Landing Page

## Live URLs
| Host | URL | Auth required? |
|---|---|---|
| Databricks Apps | https://harvard-st-2714-1056885807317405.aws.databricksapps.com | ✅ Databricks login |
| GitHub Pages (custom domain) | https://2714harvardst.com | ❌ Public |
| GitHub Pages (default) | https://ricksterz.github.io/2714HarvardSt/ | ❌ Public |

> `freeze.py` writes `build/CNAME` with the custom domain on every rebuild
> (see `CUSTOM_DOMAIN` near the bottom of `freeze.py`), so the domain survives
> future `gh-pages` redeploys.

---

## Local dev

```bash
cd ~/harvard-st-listing
pip3 install -r requirements.txt
flask --app app run --debug
# Open http://localhost:5000
```

---

## Redeploy to Databricks

```bash
# 1. Push changed files to workspace (repeat for each changed file, or use import-dir for bulk)
databricks workspace import \
  /Workspace/Users/neilrickydsa@gmail.com/harvard-st-2714/templates/index.html \
  --file ~/harvard-st-listing/templates/index.html --overwrite --format RAW

# 2. Trigger new deployment
databricks apps deploy harvard-st-2714 \
  --source-code-path /Workspace/Users/neilrickydsa@gmail.com/harvard-st-2714
```

> **Note:** All images are stored at 2400 px wide (≤ 1.6 MB each) to stay under
> Databricks Apps' 10 MB per-file limit. Raw originals are in `~/Downloads/2714HarvardSt/`.

---

## Deploy to GitHub Pages (public, no login)

### First-time setup

**1. Create the GitHub repo**
Go to https://github.com/new and create a repo named **`2714HarvardSt`** (public).

**2. Add the remote and push source**
```bash
cd ~/harvard-st-listing
git remote add origin https://github.com/ricksterz/2714HarvardSt.git
git push -u origin main
```

**3. Build the static site**
```bash
python3 freeze.py
# Writes static files to ./build/
```

**4. Push the build to the gh-pages branch**
```bash
cd ~/harvard-st-listing

# Create an orphan gh-pages branch containing only the build output
git checkout --orphan gh-pages
git rm -rf . --quiet             # clear everything from index
cp -r build/. .                  # copy build contents to root
git add .
git commit -m "Deploy static site"
git push origin gh-pages --force
git checkout main                # back to your working branch
```

**5. Enable GitHub Pages**
- Go to your repo on GitHub → **Settings → Pages**
- Source: **Deploy from a branch**
- Branch: `gh-pages` / `/ (root)`
- Click **Save**

Your site will be live at:
**`https://ricksterz.github.io/2714HarvardSt/`** (usually within 60 seconds)

### Subsequent redeploys (after editing)

```bash
cd ~/harvard-st-listing

# 1. Commit source changes on main
git add -A && git commit -m "Update listing"
git push origin main

# 2. Rebuild and push gh-pages
python3 freeze.py
git checkout gh-pages
cp -r build/. .
git add -A && git commit -m "Redeploy"
git push origin gh-pages --force
git checkout main
```

---

## Update the price

Search `templates/index.html` for `$549,000` and `$195` and replace all occurrences
(title, meta/OG/Twitter tags, JSON-LD `offers.price`, nav, hero, stats strip, About
copy, Market Context bars — the $/sf figure also drives the `data-width` percentages
on the value bars).

## Update the listing status (e.g. Pending / Sold)

Search for `Pending` (status badges in nav/hero, footer text) and
`schema.org/Reserved` (JSON-LD `offers.availability`) and update together —
e.g. switch to `schema.org/InStock` and drop the badges once active again, or
`schema.org/SoldOut` once closed.

---

## Styling (Tailwind)

Tailwind is **compiled to a static file** (`static/css/tailwind.css`) instead of
loaded from the dev-only CDN — this removes a third-party script and improves
load time and supply-chain safety.

> **Important:** if you add or change any Tailwind utility classes in
> `templates/index.html`, you must recompile the CSS or the new classes won't be
> styled:
>
> ```bash
> npx tailwindcss@3.4.17 -c ./tailwind.config.js \
>   -i ./tailwind.input.css -o ./static/css/tailwind.css --minify
> ```
>
> Custom CSS (color tokens, dark mode, lightbox, etc.) lives in the `<style>`
> block of `index.html` and does not require a rebuild.

---

## Security

- **Content-Security-Policy** + `referrer` are set via `<meta>` tags in
  `index.html`, restricting scripts/styles/frames/images to the known external
  origins (Google Tag Manager, Google Fonts, Google Maps). Note: GitHub Pages
  serves static files only and cannot send custom HTTP headers, so header-only
  controls (HSTS, `X-Frame-Options`, CSP `frame-ancestors`) aren't available on
  the public host.
- **Pinned dependencies** in `requirements.txt` for reproducible builds.
- **CI** (`.github/workflows/ci.yml`) runs `pip-audit` (dependency CVEs),
  `gitleaks` (committed-secret scan), and verifies the `freeze.py` build.
- **Dependabot** (`.github/dependabot.yml`) opens weekly update PRs for pip and
  GitHub Actions dependencies.

---

## Project structure

```
harvard-st-listing/
├── app.py              Flask entrypoint — reads PORT env var
├── app.yaml            Databricks Apps config
├── freeze.py           Builds static site to ./build/ for GitHub Pages
├── requirements.txt    Pinned Python dependencies
├── tailwind.config.js  Tailwind build config
├── tailwind.input.css  Tailwind entry (@tailwind directives)
├── .github/
│   ├── dependabot.yml  Weekly dependency update PRs
│   └── workflows/
│       └── ci.yml      pip-audit + gitleaks + build verification
├── templates/
│   └── index.html      Single-page site (compiled Tailwind, vanilla JS)
├── static/
│   ├── css/
│   │   └── tailwind.css  Compiled Tailwind (do not edit — regenerate)
│   └── img/
│       ├── img_01.jpg … img_50.jpg   2400px listing photos
│       ├── favicon.png, favicon-32.png
│       ├── floorplan.png             Rendered floor plan (2400px)
│       └── floorplan.pdf             Original downloadable PDF
└── build/              Generated by freeze.py — do not edit manually
```
