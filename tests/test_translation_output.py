#!/usr/bin/env python3
"""Verify the real en->zh outputs produced by the CLI test run:
cue count and timestamps unchanged, translated text non-empty Chinese."""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from translate_srt import parse_srt

here = Path(__file__).parent
src = parse_srt((here / "sample.en.srt").read_text(encoding="utf-8"))
zh = parse_srt((here / "sample.zh.srt").read_text(encoding="utf-8"))
bi = parse_srt((here / "sample.bilingual.srt").read_text(encoding="utf-8"))

assert len(zh) == len(src) == 6, "cue count changed"
assert [c.timing for c in zh] == [c.timing for c in src], "timestamps changed"
for c in zh:
    assert c.text.strip(), "empty translation"
    assert re.search(r"[\u4e00-\u9fff]", c.text), "no Chinese in: %r" % c.text

assert len(bi) == 6 and [c.timing for c in bi] == [c.timing for c in src]
for o, b in zip(src, bi):
    assert b.lines[-len(o.lines):] == o.lines, "bilingual: original not at bottom"
    assert re.search(r"[\u4e00-\u9fff]", b.lines[0]), "bilingual: translation not on top"

print("translation output OK: 6 cues, timestamps identical, Chinese on top in bilingual")
