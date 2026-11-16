You are a read-only reviewer for a fan translation of a Japanese GBA game (Sengoku Kakumei Gaiden). Do not edit any file.

The attached images are tile sheets: ROM graphics rendered as 8x8 4bpp tiles in grey (identical and blank tiles removed). Each source starts with a white label strip `rom:<hex offset>` (raw ROM, 16 KB per label) or `<hex>:0` (an LZ77-compressed block, named by its ROM offset). Tiles of one picture are often out of order (sprites are stored in 8x8 pieces), so Japanese characters may appear split into halves or quarters. Many sources are just noise (tilemaps, sound, code): that is expected.

Task: for EVERY label strip you can see, decide whether its tiles contain Japanese text drawn as graphics (kana, kanji, Japanese punctuation, or Latin letters that form words), as opposed to pictures, backgrounds, character sprites or noise.

Output one line per label that DOES contain text, tab-separated:
`<sheet file name>\t<label>\t<kind>\t<what you can read, or a description>`
where kind is one of: kanji-large (title/banner-sized characters), label (menu/button/stat labels), font (a whole character set in order), latin (English/romaji letters), other.
Then one final line: `NO-TEXT: <comma-separated labels with no text>`.
Be inclusive: if a label might hold text fragments, list it with kind `other` and say "possible". Do not skip any sheet.
