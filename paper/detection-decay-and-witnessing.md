# Detection Decay and Content-Addressed Witnessing: a Position from the Complete Image Space

**Javen Burchell (Javenexe)** · July 2026 · draft v0.1
Reference implementation: https://javenexe.github.io/pixel-theory/ · https://github.com/Javenexe/pixel-theory

## Abstract

We consider the finite set of all possible images at a fixed resolution — for
1080×1080 24-bit RGB, an integer with 8,426,914 digits ("the Javen Number") —
and draw out its consequences for synthetic-media defense. (1) Because
captured and generated images are members of the same set, with origin a
property of *selection events* rather than pixels, zero-error detection is
impossible in principle. (2) Practical detection exploits the statistical
distance between capture and generator distributions; since minimizing this
distance is the explicit training objective of generative modeling, and since
published detectors supply gradients to adversarial training, detection power
is a structurally wasting asset. (3) Trust must therefore attach to
provenance: fingerprint (content hash), signature (witness testimony over
hash, dimensions, and time), and ledger (externally time-anchored claim
history). We describe a minimal dependency-free reference implementation —
browser-side ECDSA witnessing, content-addressed claims that survive metadata
stripping, an independent verifier, and a public archive whose root hash is
anchored into Bitcoin via OpenTimestamps — and situate it as complementary to
capture-time manifest standards such as C2PA. We state honestly what
witnessing does not provide, and argue corroboration converts residual
forgery from a technical problem into a conspiracy problem.

## 1. The complete image space

Fix width w, height h, and 24-bit RGB. The set of possible images has
N = 16,777,216^(w·h) members. For w = h = 1080, N ≈ 1.93472 × 10^8,426,913.
The set is finite, fully specified, and complete: it contains every
photograph, every film frame, and every forgery that will ever exist at this
resolution. Writing a frame's index in base 256 across the raster shows the
address and the image are the same bytes read two ways; the set requires no
storage, and rendering and addressing are exact inverses.

Two counting facts follow immediately.

**Fact 1 (no short names).** No injective naming scheme can give all members
names shorter than the members; transmitting an arbitrary frame's position
costs exactly the raw image (pigeonhole).

**Fact 2 (measure of the compressible).** At most 256^K members possess any
description of K bytes or fewer. A frame that deflate-compresses to K bytes
lives on an "island" of at most 256^K comparably-describable frames — for a
200 KB photograph at 1080×1080, at most ~10^481,000 frames, a 10^−7,945,000
fraction of the space. Everything recognizable as an image has, provably,
measure ~0.

## 2. Why detection decays

**In principle.** A deepfake detector partitions the set into "captured" and
"synthesized." But every member is both a possible capture and a possible
synthesis; the classes coincide as sets. Origin is a fact about the event
that selected a frame, not about the frame. Zero-error detection from pixels
alone is therefore impossible — not hard, impossible.

**In practice.** The serious objection is distributional: cameras and
generators induce different distributions on the set, and classifiers
separate distributions. This is correct, and it concedes the decisive point.
Detector advantage is bounded by the statistical distance between the capture
distribution P_cap and the generator distribution P_gen; the training
objective of generative modeling *is* the minimization of this distance.
Three dynamics make the decay structural:

1. **Convergence.** Successive model families monotonically reduce the
   divergences detectors exploit.
2. **The adversarial loop.** A published detector is a differentiable
   description of the remaining gap; GAN training makes the defense a
   component of the attack. Better defenses train better forgers.
3. **Asymmetry and base rates.** Defense must be right about every image;
   the attacker needs one image to pass once. At realistic base rates, even
   accurate detectors drown true positives in false alarms.

Hence the refined claim: detection is not useless today; it is a wasting
asset whose designed fate is extinction. Infrastructure should not be built
on a signal whose decay is the attacker's objective function.

## 3. Witnessing

Truth was never a property of pixels: a photograph is true because a capture
event selected it, and the set contains every image but no events. The
answerable question is not "is this image real?" but "who vouches that a
capture event selected this frame, and when?" — a fact outside the set, and
therefore beyond any generator's reach.

The minimal architecture:

- **Fingerprint.** SHA-256 over the frame's exact bytes, naming content
  independent of container or metadata.
- **Signature.** ECDSA P-256 over the canonical string
  `javen-claim-v1|sha256|WxH|timestamp` — testimony that a key vouched for
  this frame at this moment.
- **Ledger.** Claims accumulate in a public archive (here: a git repository)
  whose deterministic root hash is anchored via OpenTimestamps into the
  Bitcoin blockchain on every change, so no party — including the
  maintainer — can backdate testimony.

The reference implementation is ~300 lines of auditable browser code: keys
generated locally and never transmitted; claims verifiable by anyone, forever,
offline, via an independent verifier that recomputes fingerprint and
signature from scratch. Because claims are keyed by content hash and live
outside the file, they survive metadata stripping, re-encoding of containers,
and platform laundering — complementing capture-time embedded-manifest
standards (C2PA, with hardware-rooted signing available in commercial cameras
as of 2026), which establish provenance at the sensor but travel with the
file.

## 4. Limits and corroboration

A signature proves a key vouched at a time — not that the content is true. A
liar can sign a fake; keys can be stolen; a signing camera can be pointed at
a screen; a timestamp proves *no later than*, not *at*. These limits are all
questions about people and process — the domain where testimony has always
been adjudicated. The structural remedy is corroboration: a real event
produces many independent selection events that agree. Forging one signed
image requires one bad actor; forging corroboration requires N key-holders
coordinating in real time and permanently staking accumulated reputation on
an attributable, time-anchored lie. Corroboration converts forgery from a
technical problem (solved, improving) into a conspiracy problem (expensive,
leaky, on the record). Roadmap consequences for claim formats: co-signatures
over one fingerprint; scene claims binding multiple frames to one asserted
event; key reputation as a public function of corroborated history.

## 5. Conclusion

The complete image space settles the strategy question. Every fake has
existed since before the first camera; appearances alone were never what
truth was made of. Detection asks pixels a question they cannot answer.
Witnessing asks people a question civilization has three millennia of
practice answering — and unlike detection, witnessing strengthens with time:
every anchored claim adds history that no future generator, however perfect,
can reach back and forge.

## References

- J. L. Borges, *The Library of Babel*, 1941.
- J. Basile, *libraryofbabel.info* and the Babel Image Archives, 2015.
- A. N. Kolmogorov, "Three approaches to the quantitative definition of
  information," 1965.
- C2PA, *Content Credentials: Technical Specification*, v2.2, 2025.
- P. Todd et al., *OpenTimestamps: scalable, trust-minimized timestamping*,
  2016.
- Burchell, J., *Pixel Theory* (interactive reference implementation), 2026.
  https://github.com/Javenexe/pixel-theory
