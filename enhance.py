"""
enhance.py — Adaptive real-estate photo enhancement for 2714 Harvard St.

Applies per-category adjustments:
  - Baseline: auto-contrast, warmth, saturation, sharpness
  - Overexposed interiors (baths/bedrooms): stronger brightness pull-back + contrast
  - Exteriors: higher saturation, deeper contrast, cooler sky preservation
  - Outdoor decks/terraces: vivid sky and greenery boost
  - Kitchen: preserve navy accuracy while warming wood floors

Usage:
    python3 enhance.py
    # Enhanced images written to static/img/ (originals backed up to static/img/originals/)
"""

from PIL import Image, ImageEnhance, ImageOps
import os, shutil, pathlib

# ── Photo category map ───────────────────────────────────────────────────────
# (img number: category)
CATEGORIES = {
    # Exterior
    1:  "exterior", 2:  "exterior", 3:  "exterior", 32: "exterior",
    # Entry / staircase
    4:  "interior", 5:  "interior",
    # Living / dining (bright, high-ceiling — needs warmth + contrast, not brightness cut)
    6:  "living",   7:  "living",   8:  "living",
    9:  "living",   10: "living",   11: "living",   12: "living",
    # Kitchen (preserve navy; warm floors)
    13: "kitchen",  14: "kitchen",  15: "kitchen",  16: "kitchen",
    # Half bath (small, tends toward cool + flat)
    17: "bath_small",
    # Primary bedroom
    18: "bedroom",
    # Primary bath (most overexposed shot in the set)
    19: "bath_primary", 20: "bath_primary",
    # Game room / flex
    21: "living",   22: "living",
    # Secondary bedrooms
    23: "bedroom",  24: "bedroom",  25: "bedroom",
    # Secondary baths
    26: "bath_small", 27: "bath_small", 28: "bath_small",
    # Outdoor
    29: "outdoor",  30: "outdoor",  31: "outdoor",
}

# ── Enhancement profiles ─────────────────────────────────────────────────────
# (brightness, contrast, saturation, sharpness, warmth_r, warmth_b)
# warmth_r = red channel multiplier (>1 = warmer)
# warmth_b = blue channel multiplier (<1 = warmer)
PROFILES = {
    "exterior":    dict(brightness=0.97, contrast=1.20, sat=1.25, sharp=1.20, wr=1.04, wb=0.96),
    "living":      dict(brightness=0.94, contrast=1.18, sat=1.15, sharp=1.15, wr=1.05, wb=0.96),
    "kitchen":     dict(brightness=0.93, contrast=1.15, sat=1.18, sharp=1.18, wr=1.03, wb=0.97),
    "bedroom":     dict(brightness=0.95, contrast=1.12, sat=1.12, sharp=1.12, wr=1.04, wb=0.97),
    "bath_primary":dict(brightness=0.88, contrast=1.22, sat=1.10, sharp=1.20, wr=1.03, wb=0.97),
    "bath_small":  dict(brightness=0.92, contrast=1.18, sat=1.12, sharp=1.15, wr=1.04, wb=0.97),
    "interior":    dict(brightness=0.95, contrast=1.15, sat=1.12, sharp=1.12, wr=1.04, wb=0.97),
    "outdoor":     dict(brightness=0.96, contrast=1.18, sat=1.28, sharp=1.15, wr=1.03, wb=0.97),
}

def apply_warmth(img, wr, wb):
    """Shift white balance toward warm by boosting R, pulling B."""
    r, g, b = img.split()
    r = r.point(lambda x: min(255, int(x * wr)))
    b = b.point(lambda x: max(0,   int(x * wb)))
    return Image.merge("RGB", (r, g, b))

def enhance(img_path, out_path, category):
    p = PROFILES[category]
    img = Image.open(img_path).convert("RGB")

    # 1. Auto-contrast (clips 0.4% at each end — recovers flat shots without blowing)
    img = ImageOps.autocontrast(img, cutoff=0.4)

    # 2. Brightness
    img = ImageEnhance.Brightness(img).enhance(p["brightness"])

    # 3. Contrast
    img = ImageEnhance.Contrast(img).enhance(p["contrast"])

    # 4. Warmth (before saturation so hue shift saturates correctly)
    img = apply_warmth(img, p["wr"], p["wb"])

    # 5. Saturation
    img = ImageEnhance.Color(img).enhance(p["sat"])

    # 6. Sharpness
    img = ImageEnhance.Sharpness(img).enhance(p["sharp"])

    img.save(out_path, "JPEG", quality=93, optimize=True)

def main():
    img_dir  = pathlib.Path("static/img")
    orig_dir = img_dir / "originals"
    orig_dir.mkdir(exist_ok=True)

    processed = 0
    for num in range(1, 33):
        fname    = f"img_{num:02d}.jpg"
        src      = img_dir / fname
        orig_bak = orig_dir / fname

        if not src.exists():
            print(f"  skip  {fname} (not found)")
            continue

        # Backup original if not already backed up
        if not orig_bak.exists():
            shutil.copy2(src, orig_bak)

        cat = CATEGORIES.get(num, "interior")
        enhance(str(orig_bak), str(src), cat)  # read from backup, write to live
        print(f"  ✓  {fname}  [{cat}]")
        processed += 1

    print(f"\nDone — {processed} images enhanced.")
    print("Originals preserved in static/img/originals/")
    print("To revert any image: cp static/img/originals/img_XX.jpg static/img/")

if __name__ == "__main__":
    main()
