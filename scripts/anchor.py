#!/usr/bin/env python3
"""Anchor the Specimen Archive in time.

Computes a deterministic root hash over the archive (the manifest plus the
sha-256 of every specimen coordinate, sorted) and timestamps it with
OpenTimestamps, which aggregates it into the Bitcoin blockchain via public
calendar servers. The resulting ledger/ROOT and ledger/ROOT.ots are committed
to the repository.

What this buys: proof that every claim in the archive existed no later than
the anchored moment, attested by infrastructure no one involved controls.
A ledger whose history could otherwise be rewritten by its maintainer becomes
one whose past is pinned outside the maintainer's reach.

Run on every merge that changes specimens/:  python3 scripts/anchor.py
Verify anytime:                              ots verify ledger/ROOT.ots -f ledger/ROOT
(Proofs are upgradeable: `ots upgrade ledger/ROOT.ots` once Bitcoin confirms.)
"""
import hashlib
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SPECIMENS = REPO / "specimens"
LEDGER = REPO / "ledger"


def archive_root() -> str:
    parts = []
    manifest = json.loads((SPECIMENS / "manifest.json").read_text())
    for s in sorted(manifest.get("specimens", []), key=lambda s: s["id"]):
        body = (SPECIMENS / s["file"]).read_bytes()
        parts.append(f'{s["id"]}|{s["sha256"]}|{hashlib.sha256(body).hexdigest()}')
    joined = "javen-archive-root-v1\n" + "\n".join(parts) + "\n"
    return hashlib.sha256(joined.encode()).hexdigest()


def main() -> int:
    LEDGER.mkdir(exist_ok=True)
    root = archive_root()
    root_file = LEDGER / "ROOT"
    root_file.write_text(root + "\n")
    print(f"archive root: {root}")
    ots_path = root_file.with_suffix(".ots")
    if ots_path.exists():
        ots_path.unlink()
    from otsclient import ots as ots_main  # noqa: PLC0415 — imported here so root computation works without the client
    sys.argv = ["ots", "stamp", str(root_file)]
    try:
        ots_main.main()
    except SystemExit:
        pass
    if ots_path.exists():
        print(f"anchored: {ots_path.name} — verify with: ots verify ledger/ROOT.ots -f ledger/ROOT")
        return 0
    print("stamping failed — root written, anchor when network allows")
    return 1


if __name__ == "__main__":
    sys.exit(main())
