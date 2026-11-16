# Style reference - Sengoku Kakumei Gaiden

The voice every translator and reviewer matches. Built from the shipped phase 6 lines that passed review (pilot:
the opening, ev000, checked in-game in `work/qa/tl_warp` and `work/qa/order`). Rulings: `glossary.md` (D1, D9, D10).
Pairs are in **display order** (`tools/story.py groups --en`). `|n` breaks are left out here.

## Voices
| Speaker | JP markers | English devices | Example (JP -> EN) |
|---|---|---|---|
| Yoshihiro Shimazu, lords (Ieyasu, Yukimura, Masamune, Nobunaga) | わし, 〜のだ, 〜ぞ, おぬし/そなた, じゃ (Shimazu) | formal, no contractions, "I am counting on you", imperatives | では、頼んだぞ！%n！ -> I am counting on you, %n! |
| Retainers, messengers | 〜にござります/ござる, 〜ませぬ, 殿！ | stiff and urgent, "My lord!", no contractions | 殿！一大事にござります！ -> My lord! Grave news! |
| Nobutsuna Kamiizumi, the Sword Saint | じゃ, のう, わい, 〜のお | old master: "eh", "you see", chuckling asides; never "my boy" (the hero may be female) | 面白いのお！ -> Funny, eh! |
| Hideyoshi Toyotomi | じゃ, ほほほ, わしは関白 | pompous, impatient, "I am the Regent, after all!" | |
| Motonari Mori | じゃのう, わし | elderly lord, weary, "it seems..." | どうやら…妖魔に操られておったようじゃのう… -> It seems... I was being controlled by demons... |
| Terumoto Mori | です/ですな, …といったところですな | polite, measured, tag "...so to speak." | 名実ともに、天下人。…といったところですな。 -> Ruler of the realm in name and in fact... so to speak. |
| Mitsunari Ishida | である | stiff gatekeeper, "I am Mitsunari Ishida." | わたしは石田三成である。 -> I am Mitsunari Ishida. |
| Sasuke Sarutobi | おいら, 〜ぜ, 〜ってんだ, 〜さ | casual: contractions, "gotta", "that's me", "Let's do this" | おいらも力になるからさ！一緒にがんばろうぜ！ -> I'll help you out too! Let's do this together! |
| Lady Oichi, the impostor, disguised (730a88-730ab0) | ですわ, まいりましたわ, お兄様 | refined, sweet, "dear brother"; keep her slip visible | いえ、何でもないですわ。それよりのぶ…いえ、お兄様。 -> Oh, it is nothing. More to the point, Nobu... I mean, dear brother. |
| Lady Oichi, the impostor, exposed (730ac0..) | わらわ, じゃ, のう, ほほほ | archaic, haughty, gloating, "Ho ho ho" | わらわか？わらわは信長の妹、お市じゃ。 -> Me? Why, I am Oichi, sister of Nobunaga. |
| Oichi, the real one (730b58) | 私, です, 下さい, trailing … | gentle, grieving, polite, no contractions | 安心して下さい。偽者ではありませんから… -> Do not worry. I am no fake... |
| Oichi, the shrine maiden | あの…, 私…, 〜下さい | shy, hesitant: "Um...", broken-off sentences, "%n-sama" | あの…%n様ではありませんか？ -> Um... Aren't you %n-sama? |
| Zanshu, Demon King, demons | ふふふ, 貴様, 〜ぞ | menacing: "Heh heh heh...", "you" (貴様 is not an honorific) | 貴様ら人間の心の闇こそ我らの糧。 -> The darkness in your human hearts is what we feed on. |
| Biographies (narration) | 〜である, 〜という | plain encyclopedic past tense, subjectless pages continue the last one | 尾張の小大名にすぎなかった信長は、桶狭間の戦いで、 / 十倍もの今川軍を破り… -> Once a minor lord of Owari, Nobunaga, at the Battle of Okehazama, / routed an Imagawa army ten times his size and made his name. |
| System notices | ＊…＊ | `*...*`, short | ＊五百両を手に入れた＊ -> *Received 500 ryo* |

## Approved pairs
1. 中国の毛利軍により肥後の城が攻め落とされました！ -> Higo Castle has fallen to the Mori army of Chugoku!
   (中国 is the region, never China.)
2. むむむ！毛利殿は妖魔と手を組んだのか？ -> Hmm! Has Mori-dono joined hands with demons?
   (honorific kept, hyphenated.)
3. 魔をも斬るといわれたそなたの武勇に頼るしかない！ -> They say your valor can cut down even demons. You are our only hope!
4. 死ぬでないぞ！%n！必ず生きて帰ってくるのだ -> Do not die, %n! Come back alive, no matter what!
5. ふむ、結界か…どこかにその結界を壊す手がかりがあるはずだ。 -> Hmm, a barrier... Somewhere there must be a clue to
   breaking it. (結界 = barrier, not kekkai: D10.)

## Corrected examples (what review caught)
- Page join read backwards. Display order:
  われらも急ぎ兵をあげ、妖魔の軍勢にそなえよう！ / 直接おぬしの手助けはしてやれぬが… / 死ぬでないぞ！
  - Shipped first: "but we will raise troops at once..." / "I cannot lend you a hand directly..." (the "but" is on
    the page shown first, continuing a page the player has not seen yet).
  - Fixed: "We too will raise troops at once and stand ready for the demon army!" / "I cannot lend you a hand
    directly, but..." / "Do not die, %n!..."
- Honorific dropped: 豊臣殿の方は我らで調べておこう。 "We will look into the Toyotomi matter." -> "We shall look into
  Toyotomi-dono ourselves. No need to worry!"
- こそ read as a correction: おぬしこそ！日本一のもののふよ！ "No, you are the finest warrior in Japan!" -> "It is you
  who are the finest warrior in Japan!"
- Hero's gender assumed: その後の行方？ "Where did he go after?" -> "Where did they go after?" (%n may be female).
  Same for the Sword Saint's おぬし: "Have you ever seen it, my boy?" -> "Have you ever seen it, eh?"
