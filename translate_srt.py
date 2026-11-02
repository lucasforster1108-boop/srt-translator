#!/usr/bin/env python3
"""srt-translator: translate an existing SRT subtitle file, fully offline.

You already have subtitles, just in the wrong language. This reads the .srt,
keeps every timestamp exactly as-is, translates the text cue by cue with
Argos Translate (local models, nothing leaves your machine), and writes a
new .srt -- optionally bilingual, translation on top, original below.
"""

import argparse
import re
import sys

# Argos uses plain ISO codes; accept the common aliases people actually type.
LANG_ALIASES = {
    "jp": "ja",
    "cn": "zh",
    "zh-cn": "zh",
    "zh_cn": "zh",
    "kr": "ko",
    "english": "en",
    "japanese": "ja",
    "chinese": "zh",
    "korean": "ko",
    "spanish": "es",
    "french": "fr",
    "german": "de",
}

TIME_RE = re.compile(
    r"^\d{1,2}:\d{2}:\d{2}[,.]\d{1,3}\s*-->\s*\d{1,2}:\d{2}:\d{2}[,.]\d{1,3}"
)


def norm_lang(code):
    return LANG_ALIASES.get(code.lower(), code.lower())


class Cue:
    __slots__ = ("timing", "lines")

    def __init__(self, timing, lines):
        self.timing = timing  # the full "-->" line, kept verbatim
        self.lines = lines    # subtitle text lines (one cue can span several)

    @property
    def text(self):
        return "\n".join(self.lines)


def parse_srt(content):
    """Parse SRT text into a list of Cue. Tolerant of missing index numbers,
    CRLF line endings and extra blank lines."""
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n\s*\n", content.strip())
    cues = []
    for block in blocks:
        lines = [ln for ln in block.split("\n")]
        # find the timing line; anything before it is the index (dropped,
        # we renumber on write anyway)
        tpos = None
        for i, ln in enumerate(lines):
            if TIME_RE.match(ln.strip()):
                tpos = i
                break
        if tpos is None:
            continue
        timing = lines[tpos].strip()
        text_lines = [ln for ln in lines[tpos + 1:] if ln.strip() != ""]
        cues.append(Cue(timing, text_lines))
    return cues


def dump_srt(cues):
    """Serialize cues back to SRT text, renumbered from 1, timings verbatim."""
    out = []
    for i, cue in enumerate(cues, 1):
        out.append(str(i))
        out.append(cue.timing)
        out.extend(cue.lines)
        out.append("")
    return "\n".join(out)


def get_translation(from_code, to_code):
    """Return an argostranslate Translation object, or exit with the exact
    install command if the language package isn't there."""
    try:
        import argostranslate.translate as argos_translate
    except ImportError:
        sys.exit(
            "argostranslate is not installed. Install it first:\n"
            "  pip install argostranslate"
        )
    installed = argos_translate.get_installed_languages()
    src = next((l for l in installed if l.code == from_code), None)
    dst = next((l for l in installed if l.code == to_code), None)
    if src is None or dst is None:
        sys.exit(
            f"Argos language package {from_code} -> {to_code} is not installed.\n"
            "Install it with:\n"
            f"  argospm update && argospm install translate-{from_code}_{to_code}"
        )
    translation = src.get_translation(dst)
    if translation is None:
        sys.exit(
            f"No Argos translation path {from_code} -> {to_code}.\n"
            "Install it with:\n"
            f"  argospm update && argospm install translate-{from_code}_{to_code}"
        )
    return translation


def translate_cues(cues, translation, bilingual):
    result = []
    total = len(cues)
    for n, cue in enumerate(cues, 1):
        if cue.text.strip():
            translated = translation.translate(cue.text)
            translated_lines = translated.split("\n") if translated else []
        else:
            translated_lines = []
        if bilingual:
            lines = translated_lines + cue.lines
        else:
            lines = translated_lines
        result.append(Cue(cue.timing, lines))
        if n % 20 == 0 or n == total:
            print(f"\rtranslated {n}/{total} cues", end="", file=sys.stderr)
    print("", file=sys.stderr)
    return result


def main():
    ap = argparse.ArgumentParser(
        description="Translate an SRT subtitle file offline with Argos Translate."
    )
    ap.add_argument("input", help="input .srt file")
    ap.add_argument("--from", dest="from_lang", default="ja",
                    help="source language code (default: ja)")
    ap.add_argument("--to", dest="to_lang", default="zh",
                    help="target language code (default: zh)")
    ap.add_argument("--bilingual", action="store_true",
                    help="keep the original text under the translation in each cue")
    ap.add_argument("-o", "--output", help="output .srt path "
                    "(default: <input>.<to>.srt, or <input>.<to>.bilingual.srt)")
    args = ap.parse_args()

    from_code = norm_lang(args.from_lang)
    to_code = norm_lang(args.to_lang)

    with open(args.input, encoding="utf-8-sig") as f:
        cues = parse_srt(f.read())
    if not cues:
        sys.exit(f"no cues parsed from {args.input} -- is it really an SRT file?")

    translation = get_translation(from_code, to_code)
    out_cues = translate_cues(cues, translation, args.bilingual)

    if args.output:
        out_path = args.output
    elif args.bilingual:
        out_path = re.sub(r"\.srt$", "", args.input) + f".{to_code}.bilingual.srt"
    else:
        out_path = re.sub(r"\.srt$", "", args.input) + f".{to_code}.srt"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(dump_srt(out_cues))
    print(f"wrote {out_path} ({len(out_cues)} cues, {from_code} -> {to_code})")


if __name__ == "__main__":
    main()
