#!/usr/bin/env python3
"""Round-trip check: parse the sample SRT, serialize it back, and assert
nothing was lost -- same cue count, same timestamps, same text."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from translate_srt import parse_srt, dump_srt

sample = Path(__file__).with_name("sample.en.srt").read_text(encoding="utf-8")

cues = parse_srt(sample)
assert len(cues) == 6, f"expected 6 cues, got {len(cues)}"

expected_timings = [
    "00:00:01,000 --> 00:00:03,500",
    "00:00:04,000 --> 00:00:06,200",
    "00:00:06,800 --> 00:00:10,000",
    "00:00:10,500 --> 00:00:13,000",
    "00:00:13,500 --> 00:00:16,000",
    "00:00:16,500 --> 00:00:19,000",
]
assert [c.timing for c in cues] == expected_timings, "timestamps changed"

# the multi-line cue must survive intact
assert cues[2].lines == [
    "The sea is very deep,",
    "and many strange animals live there.",
], f"multi-line cue mangled: {cues[2].lines}"

round_tripped = dump_srt(cues)
cues2 = parse_srt(round_tripped)
assert len(cues2) == 6
assert [c.timing for c in cues2] == expected_timings
assert [c.text for c in cues2] == [c.text for c in cues], "text changed after round-trip"

# serialized form should be byte-identical to the (canonical) input
assert round_tripped == sample.rstrip("\n") + "\n" or round_tripped.strip() == sample.strip(), \
    "serialized output differs from input"

print("round-trip OK: 6 cues, timestamps and text (incl. multi-line cue) intact")
