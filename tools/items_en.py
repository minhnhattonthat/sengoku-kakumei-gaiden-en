"""Print id<TAB>English for the system-bank item descriptions (name line + description lines) in a batch."""
import sys

NAMES = {
    "しょうぐんよろい": "Shogun Armor", "だいみょうよろい": "Daimyo Armor", "ぶしょうよろい": "Warlord Armor",
    "さむらいよろい": "Samurai Armor", "あしがるよろい": "Ashigaru Armor", "ぞうひょうよろい": "Footman Armor",
    "みならいよろい": "Trainee Armor",
    "ようとうむらまさ": "Cursed Muramasa", "めいとうまさむね": "Masamune Blade", "きくいちもんじ": "Kiku-Ichimonji",
    "めいとうおさふね": "Osafune Blade", "めいとうかねさだ": "Kanesada Blade", "むめいがたな": "Nameless Sword",
    "かずうちのかたな": "Common Sword",
    "しんそう": "Divine Spear", "とんぼきり": "Tonbogiri", "じゅうもんじやり": "Cross Spear",
    "かたかまやり": "Hook Spear", "てつやり": "Iron Spear", "ながやり": "Long Spear", "たんやり": "Short Spear",
    "はまゆみ": "Evil-Bane Bow", "どきゅう": "Crossbow", "はがねゆみ": "Steel Bow", "てつきゅう": "Iron Bow",
    "おおゆみ": "Great Bow", "もくきゅう": "Wooden Bow", "はんきゅう": "Short Bow",
}
COLORS = {"くろ": "Black", "みどり": "Green", "あお": "Blue", "あか": "Red"}
DIGITS = "０１２３４５６７８９"
PHRASES = {
    "脚力をかなり高める": "Raises speed greatly", "防御力は低め": "Defense is low", "防御力を高める": "Raises defense",
    "脚力を高める": "Raises speed", "攻撃力を高める": "Raises attack", "攻撃力が高い": "High attack power",
    "連撃時間が長いが気力消費": "Long combo, uses spirit", "しばらくとまる矢を発射": "Fires hovering arrows",
    "反射する矢を撃てる": "Fires bouncing arrows", "矢の速度が速い": "Fast arrows",
    "貫通する矢を撃てる": "Fires piercing arrows",
}
ARTS = {
    "きかんのじゅつ": ("Return Art", "Escape this province"),
    "にんじゃのじゅつ": ("Ninja Art", "Summons a ninja"),
    "こんごうだまのじゅつ": ("Diamond Orb Art", "Lasting, ultimate guard"),
    "しろがねだまのじゅつ": ("Silver Orb Art", "Blocks a few attacks"),
    "くろがねだまのじゅつ": ("Iron Orb Art", "Guards from all sides"),
    "がんきょうのじゅつ": ("Sturdy Art", "A stronger body of steel"),
    "くっきょうのじゅつ": ("Brawn Art", "Brawn keeps you standing"),
    "けんきょうのじゅつ": ("Firm Art", "Hard to knock down"),
    "しんそくのじゅつ": ("Godspeed Art", "Ultimate art, lasts long"),
    "はやてのじゅつ": ("Gale Art", "Strong art, lasts longer"),
    "しゅんそくのじゅつ": ("Swift Art", "Strike foes at speed"),
    "かんちのじゅつ": ("Full Cure Art", "Heals nearly all wounds"),
    "ちゆのじゅつ": ("Cure Art", "Restores much health"),
    "いやしのじゅつ": ("Heal Art", "Restores health"),
    "だいじしんのじゅつ": ("Great Quake Art", "A cataclysm fells foes"),
    "じしんのじゅつ": ("Quake Art", "A big quake fells foes"),
    "じひびきのじゅつ": ("Tremor Art", "A tremor trips up foes"),
    "じんらいのじゅつ": ("Thunder God Art", "Thunder God smites foes"),
    "いなずまのじゅつ": ("Lightning Art", "Fierce lightning strikes"),
    "かみなりのじゅつ": ("Thunder Art", "Thunder scatters foes"),
    "こおりあらしのじゅつ": ("Ice Storm Art", "Ice storm wipes out foes"),
    "ふぶきのじゅつ": ("Blizzard Art", "A blizzard freezes foes"),
    "こおりのじゅつ": ("Ice Art", "Freezes foes in place"),
    "かりゅうのじゅつ": ("Fire Dragon Art", "Fire dragon finisher"),
    "かえんのじゅつ": ("Flame Art", "Unleashes fierce flames"),
    "かとんのじゅつ": ("Fire Art", "Attacks foes with fire"),
}


def line(jp):
    if jp in PHRASES:
        return PHRASES[jp]
    if jp.startswith("ため攻撃") and jp.endswith("が使える"):
        return f"Allows Charge Attack {DIGITS.index(jp[4])}"
    if jp.startswith("気力消費　ため攻撃"):
        return f"Uses spirit, Charge {DIGITS.index(jp[-1])}"
    raise KeyError(jp)


def english(jp):
    rows = [r for r in jp.split("|n") if r]
    if rows[0] in ARTS:
        return "|n".join(ARTS[rows[0]])
    for name, en in NAMES.items():
        for color, cen in COLORS.items():
            if rows[0] == name + color:
                return "|n".join([f"{en}, {cen}"] + [line(r) for r in rows[1:]])
    raise KeyError(rows[0])


for path in sys.argv[1:]:
    for row in open(path, encoding="utf-8").read().splitlines():
        cells = row.split("\t")
        if cells[0].startswith("04"):
            try:
                print(f"{cells[0]}\t{english(cells[4])}")
            except KeyError as e:
                print(f"{cells[0]}\tMISSING {e}")
