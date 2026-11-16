# Story Synopsis — Sengoku Kakumei Gaiden

Built 2026-11-16 from the Japanese script in display order (`python -X utf8 tools/story.py groups --en`), drafted
by a read-only `codex exec` pass and checked against the text (the Oichi scenes 730a88-730b58 were re-read). Group
addresses are the event-table addresses `tools/story.py` prints. "Unsure" marks what the text does not settle.

## Premise

The player-named hero, `%n`, is a wandering warrior training across Japan; the player chooses a male or female hero.
In Satsuma, Yoshihiro Shimazu asks the hero to investigate an invasion of Kyushu by apparently demonic Mori troops.
Regional barriers force the hero to gather scattered magatama shards while following the demons east and north.
The demons exploit warfare and human hatred, turning political ambition into a means of bringing the Netherworld into Japan.
Mitsuhide Akechi released them, but their allegiance is to their own king, not to any human ruler.
Seven magatama offer a way to seal them again—and, in hostile hands, to break the final seal instead.
The hero and Sasuke ultimately confront the Demon King in Ezo, but defeating demons does not end human warfare.

## Who is who

Names follow the supplied glossary. Names absent from that glossary are identified below as unlisted; their English forms are provisional. Speech descriptions distinguish actual dialogue from profile-only mentions.

| JP / English | Role, voice, and relationship to the hero |
|---|---|
| 主人公・`%n` / player-named hero | Traveling warrior and player character. Male or female; do not infer gender from おぬし, あやつ, or もののふ. No directly quoted player speech here; `730af8` narrates an explanation to Nobunaga. Ultimately disappears from the lords’ view rather than entering their service. |
| 島津義弘 / Yoshihiro Shimazu | Daimyo of Kyushu and first patron. Uses わし, そなた, おぬし, じゃ, のう, and commanding requests. Formal, paternal, sometimes comically explosive at bad news. Funds the hero, later offers employment (`7309a0`), and prepares troops for the final crisis. |
| 上泉信綱・剣聖 / Nobutsuna Kamiizumi, the Sword Saint | Optional Ryukyu teacher. わし／おぬし, frequent じゃ／のう／ぞ／のじゃよ. An affectionate, eccentric old master whose instruction drifts into naps, scenery, and food. 上泉伊勢守 is another designation for him; 伊勢守 is a title, not another person (`7310c8`). |
| 毛利元就 / Motonari Mori | Elderly ruler of Chugoku. わし, じゃ, のう, わい; grateful and reflective after rescue. Demon control is confirmed in `7309e4`, not a willing alliance. He suspects Nobunaga, but this is a character’s theory. Reports poor health in `730a0c`; his death is announced in `730a18`. |
| 毛利輝元 / Terumoto Mori | Motonari’s grandson and successor. 私, polite です／ます, おじい様, and といったところですな. Gives political updates and thanks the hero indirectly through Motonari’s final words. Resolute about avenging his grandfather in `730a68`. |
| 織田信長 / Nobunaga Oda | Powerful lord wrongly suspected of directing the demons. わし／おぬし, じゃ, authoritative imperatives; formal, proud, then composed before death. Directs the hero to the Sanada and entrusts the struggle to them. Suicide at Honnoji explicitly narrated in `730b48`. |
| お市の方 / Lady Oichi, the impostor | Demon impersonating Nobunaga’s sister. While maintaining the disguise, uses polite feminine speech, including ですわ and お兄様 (`730a88`–`730ab0`); the slip のぶ…いえ、お兄様 hints at the deception. Once exposed, uses わらわ, じゃ, のう, and ほほほ. Explicitly says she is not the real Oichi in `730ac0`; explains the demons’ aims in `730ad4`. Exact species/name and whether the impersonation involves possession are **unsure**. |
| お市 / Oichi, Nobunaga’s real sister | Introduces herself and explicitly denies being a fake in `730b58`. 私, polite requests, hesitant pauses; gentle and grief-stricken. The glossary assigns her the gentle ですわ register, but the earlier disguised speaker also imitates that register. Blames her own lapse for her brother’s death. Later marries Katsuie Shibata and shares his fate (`730b70`–`730b7c`). |
| お市 / Oichi, the shrine maiden | Introduced separately in `730b98`–`730ba0`, after the real sister’s death has been reported. 私／あたし, あの, っていいます, polite but intimate and hesitant speech; contractions allowed. Dreams of a beautiful woman disappearing into a burning castle and feels she already knows the hero (`730bac`). A supernatural connection is suggested; reincarnation, identity, or possession is **unsure**, never confirmed. Promises to await the hero. |
| 明智光秀 / Mitsuhide Akechi | Nobunaga’s retainer and betrayer; no direct dialogue. The impostor reveals that he broke the demons’ seal to take the realm from Nobunaga (`730ad4`). The demons incited his rebellion and used him. His death at Hideyoshi’s forces’ hands is reported in `730c78` and `730a28`. He did **not** break the final seal (`730f10`). |
| 真田幸村 / Yukimura Sanada | Lord and intelligence provider. おれ／おぬし, 殿, emphatic commands and martial declarations; formal English without contractions. Initially hides to observe the hero’s ability (`730c60`), then becomes a dependable ally. His profile identifies 信繁 / Nobushige as his real name and 幸村 as a later invention (`73112c`); this is profile commentary, not a story identity twist. |
| 猿飛佐助 / Sasuke Sarutobi | Yukimura’s ninja and the hero’s companion. おいら, あんた, ってんだ, さ, ぜ, 〜ちまった, ねえ; friendly, energetic, casual English with contractions. Rescues the hero and joins in `730c0c`–`730c34`; Yukimura confirms his continuing assignment in `730cb0`. Summoned through the Ninja Art. |
| 豊臣秀吉 / Hideyoshi Toyotomi | Nobunaga’s former subordinate, Mitsuhide’s conqueror, and eventual Regent. わし, じゃ, impatient commands; pompous, defensive, and increasingly obsessed with world conquest. Hears Zanshu’s proposal in `730d34`–`730d74`, evades the hero’s questions in `730d98`, and privately savors the prospect of world rule in `730dc0`. Exact agreement is **unsure**. Ieyasu explicitly says he is not possessed (`730e7c`). 木下藤吉郎 / Tokichiro Kinoshita is his youthful name in the profile (`731158`; unlisted glossary alias). |
| 石田三成 / Mitsunari Ishida | Hideyoshi’s retainer and gatekeeper. わたし, である, おまえ, curt dismissal; stiff and hostile toward the hero. Refuses even to hear the Demon King warning (`730de4`). The concerned 殿下… in `73103c` is likely his response to Hideyoshi, but the supplied text has no speaker label. |
| 徳川家康 / Ieyasu Tokugawa | Lord rescued from Nue’s attack; political investigator and ally. わし, じゃ, のう, くだされ; formal, courteous, cautious. Investigates Hideyoshi while directing the hero north. Distinguishes possible demonic influence from literal possession. |
| 伊達政宗 / Masamune Date | Young lord, the One-Eyed Dragon of Oshu. おれ, forceful challenges, 貴様, 〜してくれるわ; proud, martial, formal English. Confronts Zanshu in `730ea0`–`730edc`, then appears to demand the magatama. That later behavior is Zanshu controlling his body, revealed in `730f10`–`730f44`. Freed in `730f50`–`730f58`; directs the hero to Ezo. |
| 斬手・影斬手 / Zanshu, Shadow Zanshu | Demon ninja leader, recurring antagonist, and deceiver. 我／俺, 貴様, threats, くっくっく; adopts ingratiating ございます／いたしたい toward Hideyoshi. Names himself after the Shinano encounter (`730c4c`). Sacrifices his own body to control Masamune through 影法師の舞, rendered “Shadow Puppet Dance” (`730f10`); the defeat notice names Shadow Zanshu (`730f50`). Returns for the final gauntlet. |
| 妖魔王・妖魔の王 / Demon King, King of the Demons | Master of the demons and final enemy. 我, なり, 得たり, 貴様ら, grand threats and わーはっはっは. Claims over six hundred years of imprisonment. Feeds on human darkness and seeks to transform the world. Recognizes the magatama’s sword as Seimei’s continuing opposition. |
| 妖魔六将軍 / Six Demon Generals | Reviving elite enemies guarding the Demon King; explicitly named as a collective in `730f90`. Zanshu’s speech includes himself among them. The supplied dialogue does not establish all six individual names or a complete regional roster: **unsure**. Do not equate seven magatama with seven generals. |
| ぬえ / Nue | Weather-controlling demon responsible for darkness and lightning over Edo. No direct speech. Its defeat frees the Tokugawa lands (`730cdc`, `730e14`, `730e38`). |
| 地獄百足 / Hell Centipede | Boss summoned by Zanshu in the Toyotomi lands (`730d7c`). No speech or independent motives supplied. English name is in the supplied translation, but unlisted in the glossary. |
| 安倍晴明 / Abe no Seimei | Heian-era diviner who sealed the demons with the magatama (`730c78`). Dead by the main story; no direct speech. His surviving protection enables the final sword transformation (`730ff8`). |
| 服部半蔵 / Hanzo Hattori | Ieyasu’s ninja ally, mentioned with the Iga ninja in `730e38`. No direct dialogue or meeting with the hero supplied. |
| 柴田勝家 / Katsuie Shibata | Real Oichi’s later husband, defeated by Hideyoshi; her death accompanies his (`730b70`–`730b7c`). No direct speech. |
| 島津家の使者・家臣 / Shimazu messenger or retainer | Repeated bearer of disastrous news. 殿, ござります, ござる, ませぬ: urgent, deferential military reporting. Exact identity and whether every report has the same speaker are **unsure**. |
| 町人 / townsman or local civilian | Terrified witness to Nue’s attack (`730e04`–`730e14`). ひいいい, じゃ, 〜ちまった, 〜とる, repeated たたり: panicked colloquial speech. Helps the hero and Sasuke understand the crisis. |
| 商人 / merchant | Recurring shop voice: まいど, polite sales questions and apologies (`73042c`). Service dialogue, not a story companion. |
| 妖魔忍軍 / demon ninja corps | Zanshu’s hostile forces; threaten the hero and seek the magatama. The threatening speaker in `730bf8` is not named in that group: **unsure** whether it is Zanshu personally. |
| 伊賀忍軍・真田十勇士 / Iga ninja; Ten Sanada Braves | Allied organizations, not additional individual speakers. The Iga support Ieyasu’s investigation; Sasuke belongs to the Braves, and Yukimura hopes to recruit the hero (`731060`). |

Additional named people and houses appear only in historical background or reports. They have no supplied speaking voice or direct relationship with the hero:

| JP / English | Context |
|---|---|
| 長宗我部家 / Chosokabe clan | Shikoku house destroyed by the invading Mori army (`730900`); unlisted. No individual Chosokabe lord is named. |
| 北条 / Hojo clan | Target of the Odawara campaign mentioned by Terumoto (`730a54`); unlisted. |
| 長野家・武田信玄 / Nagano clan; Shingen Takeda | Kamiizumi’s former lords and their conqueror (`7310c8`); Shingen also appears in Ieyasu’s profile (`731184`). Unlisted. |
| 柳生石舟斉・宝蔵院胤栄 / Sekishusai Yagyu; Inei Hozoin | Kamiizumi’s pupils in his profile (`7310c8`); unlisted. |
| 毛利隆元 / Takamoto Mori | Motonari’s eldest son and Terumoto’s father (`7310f8`); unlisted. JP gives 隆元 in context. |
| 豊臣秀頼 / Hideyori Toyotomi | Hideyoshi’s son, assisted by Terumoto (`7310f8`); unlisted. JP gives 秀頼 in context. |
| 浅井長政・浅井家 / Nagamasa Azai; Azai clan | Real Oichi’s earlier husband and his destroyed house (`73111c`); unlisted. Her slain son is unnamed. |
| 真田昌幸・上杉景勝 / Masayuki Sanada; Kagekatsu Uesugi | Yukimura’s father and the lord who held Yukimura as a hostage (`73112c`); unlisted. JP gives 昌幸 in context. |
| 今川家・今川軍 / Imagawa clan and army | Nobunaga’s defeated enemy and Ieyasu’s former captors (`731108`, `731184`); unlisted. No individual Imagawa lord is named. |
| 小次郎・義姫 / Kojiro; Yoshihime | Masamune’s younger brother and mother in the poisoning account in his profile (`73119c`); unlisted. |

Rank labels such as 不動明王 and 韋駄天 in `7469b0` are title vocabulary, not additional story characters.

## Story by chapter

The table groups many return conversations under their speaker. Consequently, adjacent group addresses can describe widely separated story stages. The sequence below follows the journey; later return dialogue is placed with the development it discusses. Regional magatama assignments are **unsure**: the notices list seven names but do not identify their regions.

### 1. Kyushu: Satsuma’s appeal and the barrier at Higo

Yoshihiro Shimazu welcomes the traveling hero, only for a messenger to announce that Mori forces have captured Higo Castle and that the attackers are monsters. Shimazu sends the hero to investigate and gives 500 ryo. A barrier prevents entry; exploration and shard collection provide the means to destroy it. The hero defeats a demon general inside Higo, but news that the Chosokabe of Shikoku have been destroyed turns a local rescue into an expedition against the demons in the Mori lands. The Higo general’s personal name is **unsure**.

**Groups:** `730830`–`73091c`.  
**Tone / optional talk:** Warm patronage gives way to urgent, sometimes exaggerated alarm. `730894` includes shopping and optional Ryukyu guidance. `7308b0`–`7308d8` are progress-dependent return hints, not separate advances in the plot.

### 2. Optional Ryukyu: the Sword Saint’s lessons

South of Satsuma, Nobutsuna Kamiizumi teaches the hero combat fundamentals and more advanced techniques. His instruction supplies a comic counterpoint to the war: the formidable Sword Saint can be sleepy, distracted by Mount Fuji, or thinking about cherry rice cakes. This is an optional training destination, not a required campaign chapter.

**Groups:** Referral dialogue in `730894`, `7308b0`, `7308c4`; teacher dialogue `7341dc`–`7343c4`.  
**Tone / optional talk:** Patient old-master instruction and affectionate comedy. Tutorials, control-scheme variants, repeat hints, and idle conversations should not be treated as chronological story events.

### 3. Mori lands: Chugoku and the aftermath in Shikoku

The hero enters the Mori campaign, gathers shards, and breaks another barrier. Rescued Motonari confirms that demons controlled him. He says they came from the Oda lands and suspects Nobunaga because of the Oda army’s strength; the story does not establish that suspicion as fact. Shimazu thanks the hero and contributes another 500 ryo for the journey east. Motonari subsequently reports ill health, and a later visit finds Terumoto mourning his grandfather. Shikoku’s fall is reported, but a separate Shikoku lord encounter or named boss is **unsure** from this dialogue.

**Groups:** `730930`–`73096c`; `7309e4`–`730a18`.  
**Tone / optional talk:** Relief and gratitude become frailty and bereavement. Shimazu’s barrier advice and Motonari’s health update are return conversations; Terumoto’s succession is a later state, not necessarily immediate after rescue.

### 4. Oda lands and Kyoto: false Oichi and Honnoji

An apparent Oichi directs Nobunaga to a meeting with Mitsuhide at Honnoji. Confronted by the hero, she drops her polite disguise, declares herself a fake, and boasts that the demons incited Mitsuhide. Mitsuhide originally released them to seize power, but they want war and hatred rather than any stable ruler. At Honnoji, Nobunaga hears the hero’s account, recognizes the deception, and sends them northeast to the Sanada for intelligence about the magatama. He stays behind, accepting death; narration dates his suicide to 1582. The real Oichi later appears, grieving and blaming herself.

**Groups:** `730a78`–`730b58`; Shimazu’s reaction `730974`.  
**Tone / optional talk:** Deceptive domestic politeness becomes haughty villainy, then Nobunaga’s restrained farewell and Oichi’s grief. Do not translate the fake’s claims as the real sister’s treachery.

### 5. Oda castle revisits: the real Oichi’s fate and the shrine maiden

Later visits report that the real Oichi married Katsuie Shibata, then shared his fate when Hideyoshi defeated him. Empty-castle states follow. A shrine maiden also named Oichi eventually approaches the hero. She feels an unexplained familiarity and dreams of a beautiful woman vanishing into a burning castle. She asks the hero to return and promises to wait during the demon campaign. These scenes suggest continuity with the deceased woman without explaining it.

**Groups:** `730b70`–`730be8`.  
**Tone / optional talk:** Optional, state-dependent return conversations: absence, loss, uncanny recognition, and tender attachment. `730b88`–`730b90` repeat the empty-location notice; `730be8` repeats the maiden’s promise. The exact main-quest point at which she appears is **unsure**.

### 6. Sanada lands: Sasuke, Shinano, and the seven magatama

A hostile encounter over the magatama brings Sasuke to the hero’s aid. He joins the journey and explains that a barrier surrounds Shinano, where Yukimura is located. After the hero penetrates the demon ninja defenses, Zanshu retreats and gives his name. Yukimura emerges: he had remained hidden to assess the hero. He explains that Abe no Seimei sealed Netherworld demons across Japan using seven magatama, which the freed demons shattered and scattered. Reassembling all seven should allow another sealing. He reports Mitsuhide’s death and identifies Hideyoshi, the next prospective unifier, as the likely next target.

**Groups:** `730bf8`–`730cb0`; Shimazu’s intelligence comment `730980`.  
**Tone / optional talk:** A rescue develops into companionship; Yukimura’s playful test gives way to major exposition. Sasuke’s joining notice is `730c34`. The seven are 信 **Faith**, 智 **Wisdom**, 天 **Heaven**, 仁 **Mercy**, 忠 **Loyalty**, 考（孝） **Piety**, and 勇 **Courage**. Preserve the glossary’s “Piety” for the script’s 考.

### 7. Toyotomi lands: Owari, the Regent, and Zanshu’s offer

Zanshu offers Hideyoshi help conquering not only Japan but the world, and Hideyoshi agrees to hear him out. When the hero arrives, Zanshu claims his objective is already achieved and summons Hell Centipede. Afterward, Hideyoshi evasively denies knowing what the demons wanted, mentions their next destination as Tokugawa territory, and dismisses the hero. His private relish at world conquest reinforces suspicion, but the bargain’s exact terms remain unstated. Mitsunari subsequently bars access. Meanwhile, Terumoto describes the Mori submission to Hideyoshi and his rise to Regent.

**Groups:** `730d34`–`730dd8`; Sanada warning `730cc0`; political return dialogue `73098c`, `730a28`–`730a44`.  
**Tone / optional talk:** Sly temptation, pompous dismissal, and political unease. `730dc8`–`730dd8` are initial and shortened gatekeeper talk. Shimazu suspects collusion; his suspicion is not proof of possession.

### 8. Tokugawa lands: darkness over Edo

Sasuke notices that daylight has vanished. A terrified local reports Nue and lightning over Edo. The hero defeats the weather demon, restoring safety, and Ieyasu thanks them. He suspects the disruption may serve another person’s aims as well as the demons’ and assigns Hanzo Hattori and the Iga ninja to investigate Hideyoshi. He sends the hero north for the remaining magatama. Later reports find no continuing demon connection, though his concern persists.

**Groups:** `730df8`–`730e74`; Sanada updates `730cd0`–`730cdc`.  
**Tone / optional talk:** Civilian terror, Sasuke’s urgent compassion, then Ieyasu’s measured political suspicion. `730e64`–`730e74` are follow-up investigation talk, not another confrontation.

### 9. Date lands and Oshu: the stolen magatama

Masamune confronts Zanshu after Nue’s defeat. Reports suggest he killed the ninja leader, but Yukimura doubts that account. When the hero arrives with the magatama, “Masamune” demands them under the pretext of sealing the demons. Instead, he breaks the final seal and calls forth the Demon King. Zanshu reveals that he sacrificed his own body to take control of Masamune through Shadow Puppet Dance. The collected magatama have accomplished what Mitsuhide could not. Defeating Shadow Zanshu restores the magatama and frees Masamune, who reveals that the Demon King is in Ezo and has not yet fully recovered his strength.

**Groups:** `730ea0`–`730f80`; Sanada hints `730cec`–`730cf8`; return commentary `7309a0`, `730a54`.  
**Tone / optional talk:** Heroic challenge becomes apparent betrayal, catastrophic revelation, and urgent recovery. Masamune is a controlled victim, not a willing traitor. `730f80` repeats the instruction to go to Ezo. Shimazu’s recruitment offer belongs to the earlier “one magatama remaining” stage.

### 10. Final preparations: the lords mobilize

With the final seal broken, allied lords prepare their armies to resist a nationwide demon invasion while the hero and Sasuke head for Ezo. Yukimura acknowledges that his intelligence did not reveal the incomplete seal, but insists the recovered magatama still offer hope. Terumoto invokes Motonari’s memory. Mitsunari refuses to listen. Ieyasu additionally reports Hideyoshi’s intention to invade Korea and his changed behavior, while explicitly stating that he is not possessed.

**Groups:** `7309b8`, `730a68`, `730d0c`–`730d1c`, `730de4`, `730e7c`; Masamune’s mobilization `730f58`–`730f80`.  
**Tone / optional talk:** These are return-visit responses to the final crisis, not evidence that every region must be revisited. Solidarity and personal concern contrast with the Toyotomi court’s rejection.

### 11. Ezo: the Six Demon Generals and the Demon King

Zanshu returns and explains that the Demon King’s limitless power can revive the generals repeatedly. The hero must overcome the Six Demon Generals to reach their master, with Zanshu threatening his ultimate ninja arts. The Demon King declares his intention to transform the world and reveals a true form. When he boasts that Seimei is gone, the seven magatama shine and merge into a sacred sword. He recognizes Seimei’s protection continuing after death. The hero defeats him; his final cry is disbelief.

**Groups:** `730f90`–`731008`; magatama fusion `730fec`, sword recognition `730ff8`.  
**Tone / optional talk:** Returning enemies and escalating threats give way to a supernatural reversal and victory. The full six-boss roster is **unsure** from the supplied text. The ending says the demons are gone; the precise metaphysical distinction between destruction and resealing is not explained.

### 12. Ending: remembered by allies, absent from history

The demons are gone and Hideyoshi has nominally unified Japan, yet human conflict continues. Ieyasu wonders whether Hideyoshi’s cruelty reveals his original nature; Hideyoshi refuses to acknowledge the hero and remains obsessed with the world. Terumoto recalls Motonari’s lesson that people become strong through cooperation. Shimazu cannot say where the hero has gone and observes that no daimyo could bind such a person. Yukimura’s hoped-for recruitment into the Ten Sanada Braves has also failed, but he vows to remember the hero as Japan’s finest warrior even if history does not.

**Groups:** `731010`–`73106c`.  
**Tone / optional talk:** Bittersweet political irony, gratitude, and the freedom of an unrecorded hero. The opening speaker in `731010` is **unsure** from the unlabelled text. Later speaker assignments follow clear verbal/contextual clues; do not force male pronouns onto the hero from the supplied English.

## Non-story groups

Ranges refer to the supplied group addresses, including only listed groups.

| Groups | Function |
|---|---|
| `7303b8`–`73042c` | Save selection, new game, gender selection, modes, equipment, saving, settings, controls, and reusable shop exchanges. |
| `730474`–`730644` | Armor, sword, spear, bow, and art descriptions. Equipment/help text rather than plot. |
| `73076c` | Character-name labels; the Lady Oichi label alone does not settle which Oichi is speaking in a scene. |
| `73088c`, `730964` | 500-ryo receipt notices embedded in story events. |
| `730894`, `7309cc` | Embedded shopping/training guidance and optional combo/reward advice from Shimazu. |
| `730c34` | Sasuke joining and Ninja Art unlock notice. |
| `730ef8`, `730f50`, `730fec` | Plot-critical system notices: magatama stolen, recovered, and fused. Retain their narrative significance. |
| `731078`–`7310b0` | Barrier obstruction and seven named magatama dispelling barriers. Reusable progression notices. |
| `7310b8`–`73119c` | Historical profiles: Shimazu, Kamiizumi, Motonari, Terumoto, Nobunaga, Oichi, Yukimura, Sasuke, Hideyoshi, Mitsunari, Ieyasu, and Masamune, in that order. Historical/literary commentary, not additional scenes in the adventure. |
| `7311b8`–`7311f8` | Shard pickup, shard assembly, and seven magatama acquisition notices. |
| `733868`–`7338e4` | Link Cable multiplayer setup, connection errors, handicaps, and battle-duration choices. |
| `7341dc`–`7342f8` | Optional Sword Saint advice, mechanics hints, idle jokes, and repeated conversation variants. |
| `734310`–`7343c4` | Interactive combat tutorial, including alternate control configurations. |
| `7469b0` | Battle results, rankings, generated title components, and kanji/kana variants. Not a sequence of narrative dialogue. |

## Page order

Pages display in **pointer order**, exactly as supplied within each group above. `script/*.json` lists strings in **ROM order**, which is the reverse inside each group; use the group’s pointer sequence to reconstruct sentences and emotional progression.

Repeated pointers are intentional references to shared text and must retain their displayed positions. Do not sort page IDs to reconstruct a scene. The event tables also collect later hints and return conversations under recurring speakers, so table order across groups is not a single uninterrupted playthrough chronology.