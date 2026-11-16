# Review records

- `phase6-flow.txt`: read-only `codex exec` pass over every story group in display order (`tools/story.py groups
  --en`), after the page order was proved in-game (pointer order = display order; `docs/re/text.md`).
  Verdicts: 0511c4/05119c, 054c1c, 07e908/07e8d8, 054b70 (Important) fixed; 0507d8, 055800, 055208/0551c8,
  055668, 0529e8, 053c58, 0517b8 (Minor) fixed too. 050654/05062c (Important) **waived**: in display order
  "What is more, the enemy is not human!" follows the retainer's own "Higo Castle has fallen" report two groups
  earlier, so the connective reads naturally; 050f14 is already in `docs/polish.md`.
- `phase6-rereview.txt`: fresh pass with `docs/synopsis.md` and `docs/style-reference.md` in hand. Its 4 Important
  findings (the hero gendered: 0548e8 "he", and three Sword Saint "my boy") are fixed; "my boy" left the voice
  rule and `tools/batches.py` now fails on gendered address. No other Critical or Important finding.
- The harness review `.harness/reviews/sengoku-kakumei-gaiden-en-phase6.md`: Important 1 (synopsis, style
  reference, brief, context review) and 2 (honorific check) fixed; Minor 3 fixed (`docs/polish.md`).
