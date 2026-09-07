#!/usr/bin/env python3
"""Shrink gallery photos to a web-sensible size.

Straight-from-the-phone photos are ~4000px on the long edge. A browser decodes
an image to a raw bitmap before it can paint it, and that bitmap costs
width * height * 4 bytes of RAM *regardless of how small the image is displayed*
-- a 4032x3024 photo needs ~48MB whether it fills the screen or sits in a 150px
grid cell. Two dozen of those exhausts a phone's memory budget, and the browser
starts throwing decoded images away, leaving blank tiles.

Resizing to 1600px on the long edge drops that to ~7.7MB each and the files to
roughly a tenth of their size, with no visible difference at grid size.

The originals are never destroyed: on the first run each one is MOVED into
ORIGINALS_DIR, and the web-sized copy is written in its place. Re-running
regenerates the copies from those originals, so it is safe to run again after
adding new photos.

    python scripts/optimize-images.py                # process images/personal
    python scripts/optimize-images.py --dry-run      # report, change nothing
    python scripts/optimize-images.py path/to/dir --max-edge 2000 --quality 85
"""

import argparse
import os
import shutil
import sys

from PIL import Image, ImageOps

# Windows consoles default to a legacy code page, which raises
# UnicodeEncodeError as soon as a filename contains non-Latin characters.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

ORIGINALS_DIRNAME = "_originals"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".bmp", ".tif", ".tiff"}


def human(n):
    return f"{n / 1048576:.2f} MB"


def collect(folder):
    """Image files sitting directly in `folder` (not in sub-directories)."""
    out = []
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if os.path.isfile(path) and os.path.splitext(name)[1].lower() in IMAGE_EXTS:
            out.append(name)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", nargs="?", default="images/personal")
    ap.add_argument("--max-edge", type=int, default=1600,
                    help="longest edge in pixels (default: 1600)")
    ap.add_argument("--quality", type=int, default=82,
                    help="JPEG quality (default: 82)")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would happen without writing anything")
    args = ap.parse_args()

    folder = args.folder
    if not os.path.isdir(folder):
        sys.exit(f"No such folder: {folder}")

    originals = os.path.join(folder, ORIGINALS_DIRNAME)
    if not args.dry_run:
        os.makedirs(originals, exist_ok=True)

    # Anything already banked in _originals is the source of truth. A file of the
    # same stem still sitting in the folder is a previously generated copy.
    # Maps stem -> (source path to read from, original file name).
    banked = {}
    if os.path.isdir(originals):
        for name in collect(originals):
            banked[os.path.splitext(name)[0]] = (os.path.join(originals, name), name)

    moved = skipped = unreadable = 0
    for name in collect(folder):
        stem = os.path.splitext(name)[0]
        if stem in banked:
            skipped += 1
            continue
        here = os.path.join(folder, name)
        try:
            with Image.open(here):
                pass
        except Exception:
            with open(here, "rb") as fh:
                brand = fh.read(12)[4:12].decode("latin1", "replace")
            print(f"  ! {name}: not a readable image (container '{brand}') -- left untouched")
            unreadable += 1
            continue
        if args.dry_run:
            banked[stem] = (here, name)
        else:
            shutil.move(here, os.path.join(originals, name))
            banked[stem] = (os.path.join(originals, name), name)
        moved += 1

    if moved:
        print(f"Banked {moved} original(s) in {originals}/")
    if skipped:
        print(f"{skipped} file(s) already had an original banked; regenerating from it")
    if not banked:
        sys.exit("Nothing to do.")

    print(f"\nResizing to {args.max_edge}px long edge, quality {args.quality}\n")

    before = after = 0
    rows = []
    for stem in sorted(banked):
        src, src_name = banked[stem]
        src_size = os.path.getsize(src)
        before += src_size

        with Image.open(src) as im:
            # Phone photos carry rotation in EXIF rather than in the pixels;
            # baking it in now means the copy is upright everywhere.
            im = ImageOps.exif_transpose(im)
            # Read these off the transposed image: exif_transpose clears the
            # orientation tag it just applied, so re-saving these bytes will not
            # rotate the already-rotated pixels a second time. Carrying them over
            # keeps the capture date, camera and colour profile on the copy --
            # without this the resized file has no date left at all.
            exif_bytes = im.info.get("exif")
            icc_profile = im.info.get("icc_profile")
            keep_png = im.format == "PNG"
            w, h = im.size
            scale = min(1.0, args.max_edge / max(w, h))
            new_size = (round(w * scale), round(h * scale))
            if scale < 1.0:
                im = im.resize(new_size, Image.LANCZOS)

            ext = ".png" if keep_png else ".jpg"
            dest = os.path.join(folder, stem + ext)

            if keep_png:
                params = dict(format="PNG", optimize=True)
            else:
                if im.mode in ("RGBA", "LA", "P"):
                    # JPEG has no alpha channel; flatten onto white.
                    flat = Image.new("RGB", im.size, (255, 255, 255))
                    src_rgba = im.convert("RGBA")
                    flat.paste(src_rgba, mask=src_rgba.split()[-1])
                    im = flat
                elif im.mode != "RGB":
                    im = im.convert("RGB")
                params = dict(format="JPEG", quality=args.quality,
                              optimize=True, progressive=True)
                if exif_bytes:
                    params["exif"] = exif_bytes
            if icc_profile:
                params["icc_profile"] = icc_profile

            if not args.dry_run:
                im.save(dest, **params)

        # A source whose extension changed (.png holding JPEG data, say) would
        # otherwise leave the stale file behind next to the new one.
        stale = os.path.join(folder, src_name)
        if os.path.abspath(stale) != os.path.abspath(dest) and os.path.isfile(stale):
            if not args.dry_run:
                os.remove(stale)

        dest_size = os.path.getsize(dest) if (not args.dry_run and os.path.isfile(dest)) else 0
        if args.dry_run:
            dest_size = 0
        after += dest_size
        rows.append((os.path.basename(dest), f"{w}x{h}", f"{new_size[0]}x{new_size[1]}",
                     human(src_size), human(dest_size)))

    width = max(len(r[0]) for r in rows)
    print(f"{'file':<{width}}  {'from':>11} {'to':>11}  {'was':>9} {'now':>9}")
    for r in rows:
        print(f"{r[0]:<{width}}  {r[1]:>11} {r[2]:>11}  {r[3]:>9} {r[4]:>9}")

    print("-" * (width + 48))
    print(f"{len(rows)} images: {human(before)} -> {human(after)}"
          + (f"  ({100 * (1 - after / before):.0f}% smaller)" if before and after else ""))
    if args.dry_run:
        print("\n(dry run -- nothing was written)")


if __name__ == "__main__":
    main()
