#!/usr/bin/env python3
"""
Pixel Theory — an enumeration engine for the total image space of a fixed
resolution (the "Javen Number" for 1080x1080 RGB).

Core idea
---------
Every possible image at a given resolution is one element of a finite set. If
each RGB pixel has 256*256*256 = 16,777,216 = 2**24 possible values, then an
image of W*H pixels has

    (2**24) ** (W*H)  =  2 ** (24*W*H)

possible states. For 1080x1080 that is 2**27,993,600 — a number with roughly
8.4 million decimal digits.

You cannot store that dataset (it dwarfs the number of atoms in the universe by
an incomprehensible margin). But you never need to. There is a perfect
bijection between an *index* in [0, total) and the raw pixel bytes of a
specific image:

    index  ->  fixed-length base-256 byte string  ->  image      (render)
    image  ->  raw RGB bytes  ->  base-256 integer  ->  index     (address)

So the "unique identifier" of any frame is simply its index. Enumerate distinct
indices and duplicates are impossible by construction. This module implements
both directions plus tooling to describe the size of the space.
"""

from __future__ import annotations

import argparse
import hashlib
import secrets
import sys
from dataclasses import dataclass
from decimal import Decimal, getcontext

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None


# ---------------------------------------------------------------------------
# The space
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Space:
    """A fixed image space: width x height, `channels` bytes per pixel."""

    width: int
    height: int
    channels: int = 3          # RGB
    depth: int = 256           # values per channel (0..255)

    def __post_init__(self):
        if self.depth != 256:
            # The byte-based bijection below assumes one byte per channel.
            raise ValueError("this engine assumes 8-bit channels (depth=256)")
        if self.width < 1 or self.height < 1:
            raise ValueError("resolution must be positive")

    @property
    def pixels(self) -> int:
        return self.width * self.height

    @property
    def bytes_per_frame(self) -> int:
        """Length of the raw pixel buffer / the fixed base-256 encoding."""
        return self.pixels * self.channels

    @property
    def bits_per_frame(self) -> int:
        return self.bytes_per_frame * 8

    @property
    def combos_per_pixel(self) -> int:
        return self.depth ** self.channels          # 16,777,216 for RGB

    @property
    def total(self) -> int:
        """Total number of distinct frames = 2 ** bits_per_frame.

        Returned as an exact Python int. For anything past ~4x4 this is a huge
        integer; we generally reason about it via `total_power_of_two()` and
        `scientific()` rather than materialising the decimal string.
        """
        return 1 << self.bits_per_frame

    def total_power_of_two(self) -> int:
        """The exponent k such that total == 2 ** k. Cheap and exact."""
        return self.bits_per_frame

    # -- the bijection --------------------------------------------------------

    def index_to_bytes(self, index: int) -> bytes:
        if index < 0 or index >= (1 << self.bits_per_frame):
            raise ValueError("index out of range for this space")
        return index.to_bytes(self.bytes_per_frame, "big")

    def bytes_to_index(self, buf: bytes) -> int:
        if len(buf) != self.bytes_per_frame:
            raise ValueError(
                f"buffer is {len(buf)} bytes, expected {self.bytes_per_frame}"
            )
        return int.from_bytes(buf, "big")

    def random_index(self) -> int:
        """A uniformly random frame index (cryptographically random)."""
        return secrets.randbits(self.bits_per_frame)


# ---------------------------------------------------------------------------
# Rendering (requires Pillow)
# ---------------------------------------------------------------------------

def render(space: Space, index: int, out_path: str) -> str:
    """Render the frame at `index` to a lossless PNG. Returns its SHA-256 hex."""
    if Image is None:
        raise RuntimeError("Pillow is required to render frames (pip install pillow)")
    buf = space.index_to_bytes(index)
    img = Image.frombytes("RGB", (space.width, space.height), buf)
    img.save(out_path, format="PNG")
    return hashlib.sha256(buf).hexdigest()


def address(space: Space, image_path: str) -> tuple[int, str]:
    """Reverse a PNG back to its canonical (index, sha256) in this space."""
    if Image is None:
        raise RuntimeError("Pillow is required to read frames (pip install pillow)")
    img = Image.open(image_path).convert("RGB")
    if img.size != (space.width, space.height):
        raise ValueError(
            f"image is {img.size[0]}x{img.size[1]}, "
            f"space is {space.width}x{space.height}"
        )
    buf = img.tobytes()
    return space.bytes_to_index(buf), hashlib.sha256(buf).hexdigest()


# ---------------------------------------------------------------------------
# Describing the size of the space
# ---------------------------------------------------------------------------

def scientific(power_of_two: int, sig: int = 12) -> tuple[str, int]:
    """Given k, return (mantissa, exp10) approximating 2**k as mantissa*10**exp10.

    Works for arbitrarily large k without building 2**k as a decimal string.
    """
    getcontext().prec = max(sig + 15, 40)
    log10_2 = Decimal(2).ln() / Decimal(10).ln()
    log_total = Decimal(power_of_two) * log10_2
    exp10 = int(log_total)                       # floor for positive values
    frac = log_total - exp10
    mantissa = Decimal(10) ** frac
    return (f"{mantissa:.{sig}g}", exp10)


def digit_count(power_of_two: int) -> int:
    """Number of decimal digits of 2**k, computed exactly from the log."""
    getcontext().prec = 60
    log10_2 = Decimal(2).ln() / Decimal(10).ln()
    return int(Decimal(power_of_two) * log10_2) + 1


def human_bytes(n_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    size = float(n_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:,.2f} {unit}"
        size /= 1024
    return f"{size:.2f} YB"


def describe(space: Space) -> str:
    k = space.total_power_of_two()
    mantissa, exp10 = scientific(k)
    digits = digit_count(k)
    lines = []
    lines.append("=" * 66)
    label = ""
    if space.width == space.height == 1080 and space.channels == 3:
        label = "   ← the \"Javen Number\""
    lines.append(f"  RESOLUTION  {space.width} x {space.height}  (RGB, 8-bit){label}")
    lines.append("=" * 66)
    lines.append(f"  Pixels per frame ........ {space.pixels:,}")
    lines.append(f"  Combinations per pixel .. {space.combos_per_pixel:,}  (256^3 = 2^24)")
    lines.append(f"  Bytes per frame ......... {space.bytes_per_frame:,}  "
                 f"({human_bytes(space.bytes_per_frame)})")
    lines.append(f"  Bits per frame .......... {space.bits_per_frame:,}")
    lines.append("")
    lines.append(f"  TOTAL DISTINCT FRAMES")
    lines.append(f"    exact form ..... 16,777,216 ^ {space.pixels:,}")
    lines.append(f"    power of two ... 2 ^ {k:,}")
    lines.append(f"    scientific ..... {mantissa} x 10^{exp10:,}")
    lines.append(f"    decimal digits . {digits:,}")
    lines.append("")
    # storage to hold the ENTIRE dataset, for perspective:
    # total storage = total_frames * bytes_per_frame, added in log-space.
    getcontext().prec = 40
    log10_2 = Decimal(2).ln() / Decimal(10).ln()
    store_log = Decimal(k) * log10_2 + Decimal(space.bytes_per_frame).log10()
    store_exp = int(store_log)
    store_mant = Decimal(10) ** (store_log - store_exp)
    lines.append(f"  To store EVERY frame once (~{human_bytes(space.bytes_per_frame)} each):")
    lines.append(f"    ~ {store_mant:.4g} x 10^{store_exp:,} bytes")
    lines.append("")
    lines.append("  For perspective:")
    lines.append(f"    atoms in observable universe .. ~10^80")
    lines.append(f"    this frame count .............. ~10^{exp10:,}")
    if exp10 > 80:
        lines.append(f"    → larger by a factor of ~10^{exp10 - 80:,}")
    lines.append("=" * 66)
    lines.append("  Every frame's identifier is its index in [0, total).")
    lines.append("  Enumerate distinct indices and duplicates are impossible.")
    lines.append("=" * 66)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_resolution(text: str) -> tuple[int, int]:
    text = text.lower().replace(" ", "")
    if "x" in text:
        w, h = text.split("x", 1)
        return int(w), int(h)
    n = int(text)
    return n, n


def parse_index(text: str, space: Space) -> int:
    text = text.strip()
    if text == "random":
        return space.random_index()
    if text.startswith("0x"):
        return int(text, 16)
    if text.startswith("@"):
        # read the index from a file (for huge indices)
        with open(text[1:], "r") as fh:
            return int(fh.read().strip())
    return int(text)


def cmd_info(args):
    w, h = parse_resolution(args.resolution)
    print(describe(Space(w, h)))


def cmd_render(args):
    w, h = parse_resolution(args.res)
    space = Space(w, h)
    index = parse_index(args.index, space)
    sha = render(space, index, args.out)
    print(f"rendered {space.width}x{space.height} frame -> {args.out}")
    print(f"  sha256: {sha}")
    if args.save_index:
        with open(args.save_index, "w") as fh:
            fh.write(str(index))
        print(f"  index saved: {args.save_index} ({digit_count_of_int(index)} digits)")
    else:
        d = digit_count_of_int(index)
        if d <= 40:
            print(f"  index:  {index}")
        else:
            print(f"  index:  {d}-digit integer (use --save-index to write it out)")


def cmd_address(args):
    w, h = parse_resolution(args.res)
    space = Space(w, h)
    index, sha = address(space, args.image)
    print(f"sha256: {sha}")
    d = digit_count_of_int(index)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(str(index))
        print(f"index: {d}-digit integer written to {args.out}")
    elif d <= 60:
        print(f"index: {index}")
    else:
        print(f"index: {d}-digit integer (pass --out to write it)")


def cmd_random(args):
    w, h = parse_resolution(args.res)
    space = Space(w, h)
    index = space.random_index()
    sha = render(space, index, args.out)
    print(f"random {space.width}x{space.height} frame -> {args.out}")
    print(f"  sha256: {sha}")
    if args.manifest:
        seen = _load_manifest(args.manifest)
        if sha in seen:
            print("  NOTE: this fingerprint is already in the manifest (astronomically rare)")
        else:
            with open(args.manifest, "a") as fh:
                fh.write(sha + "\n")


def cmd_verify(args):
    """Round-trip proof: render(i) then address == i, for small spaces."""
    import os, tempfile
    for res in [(2, 2), (3, 3), (4, 4), (16, 16)]:
        space = Space(*res)
        idx = space.random_index()
        fd, path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        render(space, idx, path)
        back, _ = address(space, path)
        os.unlink(path)
        ok = "OK " if back == idx else "FAIL"
        print(f"  [{ok}] {res[0]}x{res[1]} round-trip {'matches' if back == idx else 'MISMATCH'}")
    print("bijection verified: render and address are exact inverses.")


def digit_count_of_int(n: int) -> int:
    return len(str(n)) if n else 1


def _load_manifest(path: str) -> set[str]:
    try:
        with open(path) as fh:
            return {line.strip() for line in fh if line.strip()}
    except FileNotFoundError:
        return set()


def build_parser():
    p = argparse.ArgumentParser(
        prog="pixeltheory",
        description="Enumerate the total image space of a fixed resolution.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    pi = sub.add_parser("info", help="describe the size of a resolution's space")
    pi.add_argument("resolution", help="e.g. 2, 2x2, 1080, 1920x1080")
    pi.set_defaults(func=cmd_info)

    pr = sub.add_parser("render", help="render the frame at a given index")
    pr.add_argument("index", help="decimal, 0xHEX, @file, or 'random'")
    pr.add_argument("--res", required=True, help="resolution, e.g. 16 or 1080")
    pr.add_argument("--out", required=True, help="output PNG path")
    pr.add_argument("--save-index", help="write the exact index to this file")
    pr.set_defaults(func=cmd_render)

    pa = sub.add_parser("address", help="reverse a PNG back to its index")
    pa.add_argument("image", help="input PNG path")
    pa.add_argument("--res", required=True, help="resolution of the space")
    pa.add_argument("--out", help="write the exact index to this file")
    pa.set_defaults(func=cmd_address)

    pn = sub.add_parser("random", help="render a uniformly random frame")
    pn.add_argument("--res", required=True, help="resolution, e.g. 16 or 1080")
    pn.add_argument("--out", required=True, help="output PNG path")
    pn.add_argument("--manifest", help="append/dedup SHA-256 fingerprints here")
    pn.set_defaults(func=cmd_random)

    pv = sub.add_parser("verify", help="prove render/address are exact inverses")
    pv.set_defaults(func=cmd_verify)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
