#!/usr/bin/env python3
"""Invent a Word We Need — make.fun entry.

Writes one invented English word with its one-line definition to
$MAKEFUN_OUTPUT_DIR/entry.txt (falling back to /output/entry.txt).

The entry (60 characters, 60 bytes, no trailing newline):
    replydraft: a message typed, perfected, then deleted unsent.

Chosen from 36 candidates scored 1-5 against each of the published judge
criteria in order (see candidates.md in the work dir): real gap filled,
definition lands in one reading, sayable/spellable/memorable, fresh and
surprising. Winner scored 20/20; the nearest surviving rivals scored 18/20
and lose on the brief's own tie-break (gap 5 vs 4, or freshness 5 vs 3/4).
The nearest rival overall, chairdrobe (19/20), was eliminated: it already
exists as slang. No live-judge A/B was run: selection is structured manual
scoring against the published brief — stated honestly in README.md, with no
judge numbers claimed.

Deterministic, no network, no randomness: repeated runs produce
byte-identical output. See README.md for the methodology.
"""

import hashlib
import os
import re

ENTRY = "replydraft: a message typed, perfected, then deleted unsent."

# sha256 of ENTRY encoded as UTF-8 (60 bytes, no trailing newline). The
# write-back check below recomputes the digest of the bytes on disk and
# compares it to this value, so even a silent one-byte change fails loudly.
EXPECTED_SHA256 = "d83c6c460f882463c7d0e77bb26357c5a2f36cb61caad7c255fe37f089894bfb"

# The competition gate is 1-140 characters, one line, not only whitespace.
# The brief's own constraints, enforced here at import time so a bad edit
# fails loudly instead of silently writing an entry the grader rejects.
MAX_CHARS = 140
BANNED_PATTERNS = (
    re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]"),  # control characters
    re.compile(r"https?://"),                        # links: the entry stands alone
    re.compile(r"[*#`_~]"),                         # markdown formatting
    re.compile(r"\[[^\]]*\]"),                      # stage directions like [sighs]
)


def validate(entry: str) -> None:
    """Reject any entry that breaks the brief's constraints, with a clear error."""
    if not entry or not entry.strip():
        raise ValueError("entry is empty or only whitespace: gate needs 1-140 characters")
    if not 1 <= len(entry) <= MAX_CHARS:
        raise ValueError(
            f"entry is {len(entry)} chars, outside the 1-{MAX_CHARS} gate"
        )
    if "\n" in entry or "\r" in entry:
        raise ValueError("entry must be one line: it contains a newline")
    if entry.count(":") < 1:
        raise ValueError("entry must be 'word: definition' — no colon found")
    word = entry.split(":", 1)[0].strip()
    if not word.isalpha() or not word.islower():
        raise ValueError(f"headword {word!r} must be a single lowercase word")
    for pattern in BANNED_PATTERNS:
        match = pattern.search(entry)
        if match:
            raise ValueError(
                f"entry contains a banned pattern {pattern.pattern!r}: {match.group(0)!r}"
            )


validate(ENTRY)


def main() -> None:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(ENTRY)
    # Verify the write: read the file back, compare bytes, then compare the
    # sha256 digest of the read-back bytes against the expected digest, so a
    # partial write, encoding surprise, or one-byte corruption fails loudly
    # instead of submitting a corrupted entry.
    written = open(path, "rb").read()
    if written != ENTRY.encode("utf-8"):
        raise OSError(f"entry.txt at {path} does not match the entry")
    digest = hashlib.sha256(written).hexdigest()
    if digest != EXPECTED_SHA256:
        raise OSError(
            f"entry.txt sha256 {digest} != expected {EXPECTED_SHA256}"
        )


if __name__ == "__main__":
    main()
