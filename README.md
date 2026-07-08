# Pixel Theory

**[The explorer](https://javenexe.github.io/pixel-theory/)** ·
**[The essay](https://javenexe.github.io/pixel-theory/essay.html)** ·
**[Submit a specimen](CONTRIBUTING.md)**

The **Specimen Archive** is the public ledger of witnessed frames: coordinates
live in [`specimens/`](specimens/), the manifest is the index, and the git
history is the provenance chain. Claims are signed with browser-generated
ECDSA keys and are verifiable by anyone. See [CONTRIBUTING.md](CONTRIBUTING.md)
to submit yours by pull request.

An enumeration engine for the **total image space** of a fixed resolution — the
set of every image that can exist at that resolution. For 1080×1080 RGB that
count is the **"Javen Number"**: 2^27,993,600 ≈ 1.93 × 10^8,426,913 (an
8,426,914-digit integer).

## The idea

Every RGB pixel has 256 × 256 × 256 = 16,777,216 = 2^24 possible values. An
image of W×H pixels therefore has `(2^24)^(W·H) = 2^(24·W·H)` possible states.
The set is finite, and somewhere in it is every photograph that was ever taken,
every one that never was, and mostly an ocean of noise.

You can't store that set — it's larger than the universe by a factor beyond
naming. **But you never need to.** Each image *is* a number:

```
index  ──render──▶  fixed-length base-256 bytes  ──▶  image
image  ─address──▶  raw RGB bytes  ──▶  base-256 integer  ──▶  index
```

`render` and `address` are exact inverses (run `verify` to prove it). The
identifier of any frame is simply its index. Enumerate distinct indices and
**duplicates are impossible by construction** — no database, no dedup scan.

## The browser explorer

`index.html` is a self-contained web UI (no dependencies, runs entirely locally):

```bash
python3 -m http.server 8484   # then open http://localhost:8484
# or simply open index.html directly in a browser
```

Five instruments, all live against a selectable space (2×2 … 4096×4096):

1. **The Space** — stat tiles for the total frame count (scientific notation,
   digit count, bits/bytes), a magnitude ladder comparing it to atoms in the
   universe on a log scale, and the *futility meter*: the progress a
   universe-sized computer would have made since the Big Bang (zero).
2. **Frame Viewer** — render any frame by its index (decimal, hex, `random`,
   `max`), step ±1, or *walk* the enumeration live and watch the bottom-right
   channel flicker while the top-left pixel waits 10^8,426,890 years for its turn.
3. **The Static Channel** — autoplay uniform random frames. Nearly every frame
   shown has never been seen by anyone and never will be again.
4. **Address a Photograph** — drop in any image and get the coordinate it has
   always occupied in the set. The camera looks up addresses; it doesn't create.
5. **Islands of Meaning** — corrupt a growing fraction of a real image's pixels
   and watch meaning survive, then dissolve, with the neighborhood-vs-ocean math
   alongside.
6. **The Dissolve** — travel between two frames along three different paths, all
   entirely inside the set: a crossfade, random pixel defection, and the *true
   straight line in index space* — which spends nearly the whole journey inside
   noise, proving that enumeration order is blind to meaning.
7. **Coordinates** — export any frame as a `.javen` coordinate card (its exact
   index, deflate-compressed) and re-render it anywhere from the address alone.
   A photograph's coordinate compresses ~70×; a noise frame's compresses 1.000×.
   Meaning is compressibility — Kolmogorov complexity made tangible.
8. **A Finishable Universe** — fully enumerate the 1×1 space (16,777,216 frames),
   the only square RGB universe a human can witness in full, then render its
   complete atlas: every possible 1×1 image once, on a single 4096×4096 sheet —
   which is itself a single frame of the 4096×4096 space.

9. **Generators Are Navigators** — the AI section. Dissolve a photograph into
   noise, then attempt the return three ways: averaging (converges to mush),
   random search (abandoned after showing the expected wait), and consulting
   the map (instant — because the map already contained the address). A
   diffusion model is not an artist; its weights are a compressed atlas of the
   islands of meaning.
10. **A Film's Path** — drop in any video; it is sampled into a polyline through
    the space, with a filmstrip, motion and position charts, and the punchline:
    every frame of every film ever made covers ~10^-8,426,896 of the 1080×1080
    space. Cinema is a scribble of measure zero.
11. **The Witness Registry** — claim frames you are the first consciousness to
    see. Every claim is **cryptographically signed** with an ECDSA P-256 key
    generated in your browser (stored in IndexedDB, never transmitted). Since
    every possible fake already exists in the set, no frame can prove anything
    about itself — but a signature on a witnessing can. Verify any claim in one
    click; tampered claims fail. Recall stored frames by sha-256 fingerprint.
    Exportable as JSON; becomes a public ledger at publish.
12. **Your Words Already Had a Number** — type a sentence; rendered as pixels it
    becomes a frame with an address it has held since before language existed.
    One click copies a URL that *is* the sentence's address — a typical phrase
    at 256×256 compresses into ~8 KB of link.

Plus two ways to travel:

- **✦ Take the tour** — a 10-step guided narrative through all eight instruments,
  from "here is the number" to "a complete library whose card catalog is the
  library." Each step scrolls, demonstrates, and cleans up after itself
  (arrow keys navigate, Esc exits).
- **⧉ Share links** — the `⧉ link` button in the viewer encodes the current
  frame's exact address into the URL fragment (`#f1.WxH.d.…`), so the link
  itself is the coordinate. Anyone opening it re-renders the identical frame.
  Noise frames refuse to fit in a URL; meaningful frames compress in — the
  size limit itself demonstrates that meaning is compressibility.

## CLI usage

```bash
# Describe the size of a resolution's space
python3 pixeltheory.py info 1080
python3 pixeltheory.py info 1920x1080

# Render the frame at a specific index (decimal, 0xHEX, @file, or 'random')
python3 pixeltheory.py render 0 --res 1080 --out out/black.png
python3 pixeltheory.py render random --res 64 --out out/f.png --save-index out/f.idx

# Reverse any image back to its canonical index in the space
python3 pixeltheory.py address out/f.png --res 64 --out out/f.recovered.idx

# Render a uniformly random frame, optionally deduping by fingerprint
python3 pixeltheory.py random --res 128 --out out/r.png --manifest seen.txt

# Prove render() and address() are exact inverses
python3 pixeltheory.py verify
```

## On "avoiding duplicate frames"

Two levels:

1. **Enumeration** — if you walk indices `0, 1, 2, …` (or any set of distinct
   indices) you cannot produce a duplicate. The index *is* the dedup key, and
   it is exact.

2. **Fingerprinting arbitrary renders** — to ask "have I seen this frame
   before?" without holding a multi-megabyte index, use its SHA-256 (32 bytes).
   Store hashes in a manifest. Collisions exist in principle (there are vastly
   more frames than 2^256 hashes) but are negligible for any realistic number
   of frames you could ever render.

A fundamental limit worth internalizing: an identifier for an *arbitrary* image
cannot be meaningfully smaller than the image itself. That's not an
implementation gap — it's the pigeonhole principle. The 1080 index is ~8.4M
digits because the frame carries ~3.5 MB of information. The index isn't
overhead; it's the image, rewritten.

## Requirements

- Python 3.8+
- Pillow (`pip install pillow`)
