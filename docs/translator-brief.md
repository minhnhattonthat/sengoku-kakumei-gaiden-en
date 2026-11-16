# Translator brief - Sengoku Kakumei Gaiden (GBA, Konami 2002)

You translate part of the Japanese script of Sengoku Kakumei Gaiden into English for a fan patch. It is a light
action RPG set in a demon-haunted Sengoku Japan: the hero %n (male or female, named by the player) serves
Yoshihiro Shimazu and travels from Kyushu to Ezo meeting the famous warlords, gathering the seven magatama and
fighting the demons Mitsuhide Akechi let loose. Tone: earnest period adventure with comic townsfolk.
Work only on the batches named in your dispatch, one at a time in the order given, each to a passing check before
the next. Do all translation yourself; do not dispatch subagents.

## Read first
1. `docs/style-reference.md` - character voices and approved example pairs. Match this voice.
2. `build/terms_<batch>.txt` - binding glossary rows for this batch (full table in `glossary.md` if you need more).
3. `docs/synopsis.md` - plot, who is who and the late reveals (the three Oichis, possessions). Don't give a reveal
   away early; keep early lines consistent with what comes later.
4. For story context in the order the player sees it: `python -X utf8 tools/story.py groups --en`.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese` - form is dlg | choice | menu | name | narration; `|n` in the
Japanese is a column break of the original and carries no meaning; limit is the budget (3 lines x 24 letters = one
page, `%n` counts as 8 letters).
**Page order:** the batch lists entries in ROM order, and inside one dialogue the ROM holds the pages **last page
first**. The player sees them in the reverse of the batch order (proved in-game; `tools/story.py` prints display
order). A sentence split over two pages: its first half is the entry *later* in the batch.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII: straight quotes, `...`; no tabs, no Japanese
or fullwidth characters, no `\uXXXX`. Don't write `|n`: `tools/batches.py fix` wraps the English into 24-letter lines.

## Validate
Run `python -X utf8 tools/batches.py check <batch>` from the repo root and fix every reported id until it prints OK.
It checks ids, control codes (`%n`, `%d`), ASCII, the glossary (and its Avoid column), the 3 x 24 page budget, and
honorifics: 様/さま after a name needs `-sama`, 殿/どの after a name needs `-dono`.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese doesn't
  state; don't summarise or skip. Names in biographies stay (a review caught "his mother" for 母義姫 and "the Uesugi"
  for 上杉景勝): if a page can't hold them, report `LONG:`.
- Keep the speaker audible (voices in `docs/style-reference.md`). A line any speaker could have said is a mistake.
- Names and terms exactly as in the glossary, full forms, no abbreviations (D4).
- Honorifics kept, hyphenated (Hideyoshi-dono, %n-sama); Western name order (D1). The hero's gender is the player's
  choice: never "he"/"she" for %n or for the hero ("they", or rephrase).
- Punctuation: 「」 -> "...", 『』 -> '...', ・・・/… -> `...`, ！？ -> `!?`, ＊...＊ -> `*...*`.
- Placeholders: copy every one exactly; no suffix glued to `%d` ("No. %d", not "%dth"); no a/an right before `%n`.

## Notes from earlier batches (review findings)
- Page joins: "He became head..." after a page ending "and" (055800); a page starting "but" that is shown *before*
  the clause it continues (0511c4). Read the pages in display order before writing.
- "No, you are the finest warrior" for おぬしこそ！日本一のもののふよ - こそ is emphasis ("It is you who..."), not a
  correction.
- 豊臣殿の方 dropped to "the Toyotomi matter": the honorific stays (Toyotomi-dono).

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`,
`CUT: id - what was dropped`.
