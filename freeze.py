"""
Build a fully-static copy of the listing site for GitHub Pages.

Usage:
    python3 freeze.py

Output: ./build/   ← drag-and-drop to Netlify, or push to gh-pages branch.
"""

from app import app
from flask_frozen import Freezer

app.config["FREEZER_DESTINATION"] = "build"
app.config["FREEZER_RELATIVE_URLS"] = True   # makes all hrefs relative — works in any subdir
app.config["FREEZER_REMOVE_EXTRA_FILES"] = True

freezer = Freezer(app)

def _fix_paths(build_dir="build"):
    """
    frozen-flask converts <src>/<href> attrs to relative, but not CSS
    url('/static/...') inside <style> blocks. Fix those too so the
    build works at any subdirectory path (e.g. username.github.io/repo/).
    """
    import pathlib, re
    for html in pathlib.Path(build_dir).rglob("*.html"):
        text = html.read_text()
        # url('/static/...')  →  url('static/...')
        fixed = re.sub(r"url\('/static/", "url('static/", text)
        # also catch double-quoted variants
        fixed = re.sub(r'url\("/static/', 'url("static/', fixed)
        if fixed != text:
            html.write_text(fixed)
            print(f"  patched: {html}")

if __name__ == "__main__":
    freezer.freeze()
    _fix_paths()
    print("\n✓ Static build written to ./build/")
    print("  Next steps:")
    print("  1. cd build && python3 -m http.server 8000  ← test locally")
    print("  2. Push to GitHub Pages (see README for full commands)")
