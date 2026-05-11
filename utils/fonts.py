"""
Custom Unicode font converters for premium Telegram text.

These produce styled text using Unicode Mathematical Alphanumeric Symbols,
which render natively in Telegram without HTML/Markdown.
"""

# ── Sans-Serif Bold: 𝗔-𝗭 𝗮-𝘇 𝟬-𝟵 ───────────────────────────────────────────────
_BOLD_UPPER = {chr(c): chr(c - 0x41 + 0x1D5D4) for c in range(0x41, 0x5B)}
_BOLD_LOWER = {chr(c): chr(c - 0x61 + 0x1D5EE) for c in range(0x61, 0x7B)}
_BOLD_DIGIT = {chr(c): chr(c - 0x30 + 0x1D7EC) for c in range(0x30, 0x3A)}
_BOLD_MAP = {**_BOLD_UPPER, **_BOLD_LOWER, **_BOLD_DIGIT}

# ── Sans-Serif Bold Italic: 𝙰-𝚉 𝙖-𝙯 ─────────────────────────────────────────
_BOLDITALIC_UPPER = {chr(c): chr(c - 0x41 + 0x1D63C) for c in range(0x41, 0x5B)}
_BOLDITALIC_LOWER = {chr(c): chr(c - 0x61 + 0x1D656) for c in range(0x61, 0x7B)}
_BOLDITALIC_MAP = {**_BOLDITALIC_UPPER, **_BOLDITALIC_LOWER, **_BOLD_DIGIT}

# ── Monospace: 𝙰-𝚉 𝚊-𝚣 𝟶-𝟿 ───────────────────────────────────────────────────
_MONO_UPPER = {chr(c): chr(c - 0x41 + 0x1D670) for c in range(0x41, 0x5B)}
_MONO_LOWER = {chr(c): chr(c - 0x61 + 0x1D68A) for c in range(0x61, 0x7B)}
_MONO_DIGIT = {chr(c): chr(c - 0x30 + 0x1D7F6) for c in range(0x30, 0x3A)}
_MONO_MAP = {**_MONO_UPPER, **_MONO_LOWER, **_MONO_DIGIT}

# ── Double-Struck (Outline): 𝔸-ℤ 𝕒-𝕫 𝟘-𝟡 ────────────────────────────────────
_DS_UPPER = {chr(c): chr(c - 0x41 + 0x1D538) for c in range(0x41, 0x5B)}
_DS_LOWER = {chr(c): chr(c - 0x61 + 0x1D552) for c in range(0x61, 0x7B)}
_DS_DIGIT = {chr(c): chr(c - 0x30 + 0x1D7D8) for c in range(0x30, 0x3A)}
_DS_MAP = {**_DS_UPPER, **_DS_LOWER, **_DS_DIGIT}

# ── Small Caps (approximate with Unicode subscript letters) ─────────────────
_SMALLCAPS_MAP = {
    'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ',
    'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ',
    'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ',
    's': 'ꜱ', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x',
    'y': 'ʏ', 'z': 'ᴢ',
}

# ── Circled letters: Ⓐ-Ⓩ ⓐ-ⓩ ①-⑨ ─────────────────────────────────────────
_CIRCLED_UPPER = {chr(c): chr(c - 0x41 + 0x24B6) for c in range(0x41, 0x5B)}
_CIRCLED_LOWER = {chr(c): chr(c - 0x61 + 0x24D0) for c in range(0x61, 0x7B)}
_CIRCLED_DIGIT = {str(i): chr(0x2460 + i - 1) for i in range(1, 10)}
_CIRCLED_DIGIT['0'] = '⓪'
_CIRCLED_MAP = {**_CIRCLED_UPPER, **_CIRCLED_LOWER, **_CIRCLED_DIGIT}


def _apply(text: str, mapping: dict) -> str:
    return "".join(mapping.get(c, c) for c in text)


def bold_sans(text: str) -> str:
    """𝗕𝗼𝗹𝗱 𝗦𝗮𝗻𝘀-𝗦𝗲𝗿𝗶𝗳"""
    return _apply(text, _BOLD_MAP)


def bold_italic(text: str) -> str:
    """𝘽𝙤𝙡𝙙 𝙄𝙩𝙖𝙡𝙞𝙘 𝙎𝙖𝙣𝙨"""
    return _apply(text, _BOLDITALIC_MAP)


def mono(text: str) -> str:
    """𝙼𝚘𝚗𝚘𝚜𝚙𝚊𝚌𝚎"""
    return _apply(text, _MONO_MAP)


def outline(text: str) -> str:
    """𝔻𝕠𝕦𝕓𝕝𝕖-𝕊𝕥𝕣𝕦𝕔𝕜"""
    return _apply(text, _DS_MAP)


def smallcaps(text: str) -> str:
    """sᴍᴀʟʟ ᴄᴀᴘꜱ"""
    return _apply(text.lower(), _SMALLCAPS_MAP)


def circled(text: str) -> str:
    """Ⓒⓘⓡⓒⓛⓔⓓ"""
    return _apply(text, _CIRCLED_MAP)
