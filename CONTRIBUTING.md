# Submitting a specimen

The Specimen Archive is the public ledger of witnessed frames. There is no
backend and no database: **the repository is the ledger, and the git history
is the provenance chain.** Anyone can verify any specimen from its coordinate
and signature alone.

## How to submit

1. **Discover a frame** in [the explorer](https://javenexe.github.io/pixel-theory/) —
   render it, address a photograph, write a sentence, or find it in the static.
2. **Claim it** in section 11 (The Witness Registry). This signs the claim with
   the ECDSA key generated in your browser.
3. **Export two files**:
   - the coordinate: `⧉ export viewer frame as coordinate (.javen)` in section 07
   - the claim: the `↓ claim` button on your registry entry
4. **Fork this repository** and add:
   - `specimens/specimen-NNN.javen` (next available number)
   - your claim's fields as a new entry in `specimens/manifest.json`:

```json
{
  "id": NNN,
  "title": "a short name for the frame",
  "witness": "your name",
  "space": "WxH",
  "sha256": "…",
  "ts": 1234567890123,
  "sig": "…",
  "pub": "…",
  "date": "YYYY-MM-DD",
  "file": "specimen-NNN.javen",
  "note": "one or two sentences: what this frame is and why you witnessed it"
}
```

5. **Open a pull request.** Keep the coordinate under ~2 MB (meaningful frames
   compress; if yours doesn't fit, it may be telling you something about its
   entropy).

## What gets verified

- the `.javen` decompresses to exactly `space` worth of bytes
- its SHA-256 matches the manifest entry
- if `sig`/`pub`/`ts` are present, the ECDSA P-256 signature verifies over
  `javen-claim-v1|<sha256>|<space>|<ts>`

A frame proves nothing about itself — every possible fake already exists in
the set. What cannot be faked is a signature on a witnessing: proof that
someone vouched for this frame at this moment. That is what the archive
records.
