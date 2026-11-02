#!/usr/bin/env python3
"""Bilingual structure check with a stub translator (no Argos needed):
each output cue must contain the translation lines first, then the
original lines, with timestamps untouched."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from translate_srt import parse_srt, translate_cues


class StubTranslation:
    def translate(self, text):
        return "[T] " + text.replace("\n", " ")


sample = Path(__file__).with_name("sample.en.srt").read_text(encoding="utf-8")
cues = parse_srt(sample)
out = translate_cues(cues, StubTranslation(), bilingual=True)

assert len(out) == len(cues) == 6
for orig, new in zip(cues, out):
    assert new.timing == orig.timing, "timestamp changed"
    assert new.lines[0].startswith("[T] "), "translation not on top: %s" % new.lines
    assert new.lines[1:] == orig.lines, "original lines not preserved: %s" % new.lines

print("bilingual structure OK: translation on top, original below, timestamps intact")
