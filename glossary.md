# Glossary - Sengoku Kakumei Gaiden

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces the tables: when a JP form is in a line, one of the EN forms (separated by ` / `)
must be in its English, and no Avoid form may be.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Nobunaga-sama). Name order: Western (given name first).
- Romanisation source: official English names where they exist, else an earlier fan patch, else Hepburn without macrons.
- Credits: English.
- Register / flavour (D9): plain modern English with a period feel. Lords and retainers speak formally, without
  contractions; Sasuke, townsfolk and the shrine maiden use contractions and casual speech. Sound effects and
  laughs are romanised as read (Heh heh heh, Guoooh, Kyaaah). Furigana readings in parentheses are dropped.
- Abbreviations: full names and terms everywhere, prefer engine changes over shortening.

## Style rules
- Punctuation map: 「」 -> "...", 『』 -> '...', ・・・/… -> ..., ！？ -> !?, ＊...＊ (system notices) -> *...*.
- Page = one entry = 3 lines x 24 letters (data/windows.tsv). English with no `|n` is word-wrapped by
  `tools/batches.py`; a sentence split over several pages keeps its fragments in display order (lower-case
  continuation, no repeated subject).
- Voices:
  - Nobutsuna Kamiizumi, the Sword Saint (じゃ/のう): old master, "eh?", "you see", chuckling asides. Never "my boy":
    the hero may be female (おぬし is neutral).
  - Yoshihiro Shimazu, Ieyasu Tokugawa, Yukimura Sanada, Nobunaga Oda, Masamune Date: lordly, formal, no contractions.
  - Hideyoshi Toyotomi (じゃ): pompous, impatient ("I am the Regent, after all!").
  - Motonari Mori (じゃ): elderly lord. Terumoto Mori (ですな): polite, "so to speak" for といったところですな.
  - Mitsunari Ishida (である): stiff gatekeeper.
  - Sasuke Sarutobi (おいら, 〜ぜ): casual, "gotta", contractions.
  - Lady Oichi, the impostor (a demon): refined ですわ/お兄様 while disguised (730a88-730ab0, the slip のぶ…いえ、お兄様),
    archaic and haughty わらわ/じゃ/ほほほ once exposed (730ac0); the real Oichi (私, です, 730b58) gentle and grieving;
    Oichi the shrine maiden (730b98..) shy, hesitant, contractions allowed. docs/synopsis.md has who is who.
  - Zanshu and the Demon King: menacing, "Heh heh heh", "Wah ha ha".

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 島津義弘 | Yoshihiro Shimazu | | daimyo of Kyushu, the hero's first patron | |
| 上泉信綱 | Nobutsuna Kamiizumi | | | |
| 剣聖 | Sword Saint | | Nobutsuna's epithet | Sword Sage |
| 毛利元就 | Motonari Mori / Motonari | | given name alone is fine once he is named | |
| 毛利輝元 | Terumoto Mori | | Motonari's grandson | |
| 織田信長 | Nobunaga Oda | | | |
| お市 | Oichi | | Nobunaga's sister; also the shrine maiden | |
| お市の方 | Lady Oichi | | name label | |
| 明智光秀 | Mitsuhide Akechi / Mitsuhide | | | |
| 真田幸村 | Yukimura Sanada | | | |
| 猿飛佐助 | Sasuke Sarutobi | | | |
| 豊臣秀吉 | Hideyoshi Toyotomi / Hideyoshi | | | |
| 石田三成 | Mitsunari Ishida | | | |
| 徳川家康 | Ieyasu Tokugawa / Ieyasu | | | |
| 伊達政宗 | Masamune Date | | | |
| 斬手 | Zanshu | | demon ninja leader; 影斬手 = Shadow Zanshu | |
| 安倍晴明 | Abe no Seimei | | conventional form kept | Seimei Abe |
| 服部半蔵 | Hanzo Hattori | | | |
| 柴田勝家 | Katsuie Shibata | | | |
| 妖魔王 / 妖魔の王 | Demon King / King of the Demons | | | |
| ぬえ | Nue | | weather demon of Edo | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 九州 | Kyushu | | | |
| 中国 | Chugoku | | the region, never China | China |
| 四国 | Shikoku | | | |
| 琉球 | Ryukyu | | | |
| 蝦夷 | Ezo | | | |
| 奥州 | Oshu | | | |
| 本能寺 | Honnoji | | | |
| 小田原 | Odawara | | | |
| 冥府魔道 | Netherworld | | | |
| 薩摩 / 肥後 | Satsuma / Higo | | provinces: "<name> Province" (script/provinces.json) | |
| 毛利領 / 織田領 / 真田領 / 豊臣領 / 徳川領 / 伊達領 | lands | | "the Mori lands" etc. | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 妖魔 | demon | | 妖怪や魔物 = "monsters and fiends"; 妖魔忍軍 = demon ninja (corps) | |
| 妖魔六将軍 | Six Demon Generals | | | |
| 勾玉 | magatama | | 七つの勾玉 = seven magatama; かけら = shards | |
| 結界 | barrier | | | |
| 連撃 | combo / hits | | %d連撃 = "%d hits" | |
| 溜め攻撃 / ため攻撃 | charge attack / Charge | | item lines: "Allows Charge Attack N" | |
| 関白 | Regent | | Imperial Regent | Kampaku |
| 天下大乱編 | Realm in Chaos | | the story mode's name | |
| 両 | ryo | | money | |
| 走る | Dash | | 「走る」 the move | |
| ちょうやく | Leap | | | |
| 気力 | spirit | | arts cost it | |
| 術 | art | | 〜のじゅつ = "<Name> Art" (tools/items_en.py) | |
| 記録 | save | | menu: "Choose a save to delete." | |

- The seven magatama (single kanji, so not machine-checked): 信 Faith, 智 Wisdom, 天 Heaven, 仁 Mercy, 忠 Loyalty,
  考 (孝) Piety, 勇 Courage. "the Faith magatama".

## Decisions from earlier batches
- b001 「Ａ」ボタン -> the A Button; 十字ボタン -> Control Pad; セレクト -> SELECT; Ａ決定　Ｂ戻る -> A: Select  B: Back.
- b002 results title words: adjective set 11 cells, noun set 10 cells; kana and kanji twins get the same English.
- b007/b008 item descriptions are generated from tools/items_en.py (name, colour, phrase tables) so they stay uniform.
