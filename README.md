[English](README.md) | [简体中文](README_zh.md) | [日本語](README_ja.md) | [한국어](README_ko.md)

# srt-translator

I kept running into the same wall: the video has subtitles, just not in a language I can read. Japanese subs on a Japanese video, English subs on everything else. Hiring a human translator for a subtitle file is silly, and pasting 800 cues into a web translator one by one is worse.

So this is a small offline tool that translates an existing `.srt` file for you. It reads the cues, translates the text with [Argos Translate](https://github.com/argosopentech/argos-translate) — models that live on your own machine — and writes a new `.srt` with every timestamp untouched. There's a bilingual mode too: translation on top, original underneath, same cue.

No network is involved in the translation itself. The file never leaves your computer, which, for some subtitle collections, is exactly the point.

## In plain words

A lot of adult videos — Japanese ones especially — come with subtitles, but only in Japanese or English. If you can't read them, the dialogue is guesswork and half the scene is lost on you.

A subtitle file (`.srt`) is nothing fancy: it's a plain text file that says "at this second, this line is spoken", like a script with a clock attached. This tool takes that file and swaps the words into Chinese, without moving a single timestamp. The translation is done by a small translation program installed on your own computer (that's the "model" — no account, no website), so nothing is uploaded anywhere and nobody ever sees what you're watching.

There's also a bilingual mode: Chinese on the top line, the original language right underneath, so you can follow the Chinese and glance at the original when a line feels off.

Drop the translated file next to the video with the same name, and most players pick it up automatically. That's the whole trick.

## How this differs from speech-to-subtitle tools

Different job. Tools like my [av-subtitles](https://github.com/lucasforster1108-boop/av-subtitles) *create* subtitles by listening to the audio when none exist. This one assumes you already have a subtitle file and just can't read it. Transcription first if you have nothing; translation here once you have something.

## Install

You need Python 3.9+.

```bash
pip install argostranslate
```

Then install the language package for your pair. Argos models are downloaded once and kept locally:

```bash
argospm update
argospm install translate-ja_zh   # Japanese -> Chinese
argospm install translate-en_zh   # English -> Chinese
```

One package is roughly 100–300 MB depending on the pair. If you run the tool without the package, it stops and prints the exact install command instead of pretending to translate — I hate tools that fail silently, so this one fails loudly.

## Usage

```bash
# Japanese subs -> Chinese subs, writes movie.zh.srt next to the input
python translate_srt.py movie.ja.srt --from ja --to zh

# bilingual: Chinese on top, Japanese below, in the same cue
python translate_srt.py movie.ja.srt --from ja --to zh --bilingual

# pick the output path yourself
python translate_srt.py movie.en.srt --from en --to zh -o movie.chinese.srt
```

Timestamps, cue order and line breaks inside a cue are preserved; cues are renumbered cleanly from 1. Translation is cue by cue — cues are never merged, so timing can't drift.

## Honest limitations

- It's offline machine translation. Quality is "now I understand the scene", not "publish this". Proper nouns, slang, and double meanings will trip it up regularly.
- Long lines sometimes come back shortened or with a clause dropped. Short, clean source subs translate noticeably better.
- Argos language coverage is uneven. Major pairs (en, ja, ko, es, fr, de <-> zh, etc.) exist; exotic pairs may not, and some pairs route through English as a pivot, which costs quality.
- Speed depends on your CPU. A full movie file is a few minutes, not seconds.

## Tests

`tests/` has a small English sample subtitle (public, neutral content), a round-trip check (parse → serialize loses nothing), and a bilingual structure check with a stub translator.

## License

MIT. See [LICENSE](LICENSE).
