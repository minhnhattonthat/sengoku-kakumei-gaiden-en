# Story reviewer brief - Sengoku Kakumei Gaiden

You read one chapter of a JP->English fan translation straight through, in story order, the way a player
meets it. Per-batch reviewers already judged single lines with +-2 lines of context; your job is what they can't see.
Read-only: no edits, no git, no subagents. Return the report as your final message; the controller saves it.

## Inputs
- Chapter file (`work/qa/story/chapters/<name>.txt`): every page of the chapter's dialogue groups in display order,
  `>> id | group | JP` then the English on the next line. A `## group` is one conversation (one visit); groups in a
  file are the tables' order, which collects a speaker's later return talk together, so consecutive groups can be
  far apart in play. Read ALL of it before judging.
- `docs/synopsis.md` (plot, who is who, late reveals; its chapter list says which groups belong where),
  `docs/style-reference.md` (voice per character), `glossary.md` (rulings at the top).

## Game facts that are not bugs
- Every page is at most 3 lines of 24 letters (English drawn rotated in the game's vertical columns), so lines are
  short and terse by design. Do not ask for longer lines.
- `%n` is the player's name (up to 8 letters); the hero's gender is chosen by the player: no gendered words for the
  hero (`glossary.md`).
- Names in Western order ("Yoshihiro Shimazu"); honorifics kept, hyphenated (Nobunaga-sama) (`docs/decisions.md` D1).
- Readings in brackets in the JP （しまづよしひろ） are furigana for the reader; the English drops them.

## Judge, across the whole chapter
- Continuity: each page follows from the one before inside a group; setups, callbacks and references back are
  kept; who knows what stays coherent; nothing gives a later reveal away early.
- Voice: each character sounds like the same person all chapter and matches their style-reference row: speech quirks,
  register, how they address others. Name the line where a voice drifts or goes neutral.
- Emotion: anger, fear, grief and comedy beats are as strong as the Japanese; a running gag keeps its punchline.
- Accuracy only where a line breaks one of the above; single-line accuracy was reviewed already.

## Report
### Issues
#### Critical (continuity break, reveal given away, wrong speaker)
#### Important (voice drift or flattened, emotional beat lost, setup or callback dropped, joke dead)
#### Minor (deferred to the polish pass)
Each: `id - JP gist - problem - suggested EN` (suggested EN must fit 3 lines x 24 letters).
### Assessment
`ok` (no Critical/Important) | `issue` - one sentence why. The controller writes this word into the chapter's verdict.
