import re
from typing import Optional, Tuple


HINGLISH_NUMBER_MAP = {
    "ek": 1, "do": 2, "teen": 3, "chaar": 4, "paanch": 5,
    "chhah": 6, "saat": 7, "aath": 8, "nau": 9, "das": 10,
    "gyarah": 11, "baarah": 12, "terah": 13, "chaudah": 14, "pandrah": 15,
    "solah": 16, "satrah": 17, "atharah": 18, "unnis": 19, "bees": 20,
    "adha": 0.5, "aadha": 0.5, "half": 0.5, "paav": 0.25, "pav": 0.25,
    "pauna": 0.75, "dedh": 1.5, "sava": 1.25, "sawa": 1.25,
    "dhai": 2.5, "sadhe": 2.5, "saadhe": 2.5
}

UNIT_NORMALIZATION = {
    "kilo": "kg", "kilogram": "kg", "kilograms": "kg",
    "gram": "g", "grams": "g",
    "litre": "l", "liter": "l", "litres": "l", "liters": "l",
    "ml": "ml", "millilitre": "ml", "milliliter": "ml",
    "piece": "pcs", "pieces": "pcs", "pc": "pcs",
    "dozen": "dozen", "dozens": "dozen",
    "packet": "pack", "packets": "pack", "pack": "pack",
    "bottle": "bottle", "bottles": "bottle",
    "box": "box", "boxes": "box",
    "unit": "pcs", "units": "pcs"
}

ALIAS_MAP = {
    "pyaz": "onion", "pyaaz": "onion", "onions": "onion",
    "tamatar": "tomato", "tomatoes": "tomato",
    "aloo": "potato", "potatoes": "potato",
    "mirch": "chilli", "chillies": "chilli", "chillies": "chilli",
    "doodh": "milk",
    "dahi": "curd", "yogurt": "curd",
    "kela": "banana", "bananas": "banana",
    "seb": "apple", "apples": "apple",
    "aam": "mango", "mangoes": "mango",
    "nariyal": "coconut", "coconuts": "coconut",
    "gajar": "carrot", "carrots": "carrot",
    "bhindi": "okra", "ladyfinger": "okra",
    "karela": "bitter gourd",
    "lauki": "bottle gourd",
    "kaddu": "pumpkin",
    "paneer": "cottage cheese",
    "atta": "wheat flour", "flour": "wheat flour",
    "chawal": "rice", "rice": "rice",
    "dal": "lentils", "lentil": "lentils",
    "tel": "oil", "oil": "oil",
    "namak": "salt", "salt": "salt",
    "cheeni": "sugar", "shakkar": "sugar", "sugar": "sugar",
    "chai": "tea", "tea": "tea",
    "coffee": "coffee",
    "bread": "bread", "pav": "bread",
    "anda": "egg", "eggs": "egg", "ande": "egg"
}

# Gemini can return Hindi speech in Devanagari. The business parser and
# catalog aliases deliberately use Romanized Hinglish, so translate only the
# grocery/order vocabulary we can support deterministically. Unknown Hindi
# text remains untouched instead of being guessed.
DEVANAGARI_HINGLISH_MAP = {
    "भेज देना": " bhej dena ", "भेजना": " bhejna ",
    "आशीर्वाद": " aashirvaad ", "फॉर्च्यून": " fortune ", "अमूल": " amul ",
    "भैया": " bhaiya ", "भाई": " bhai ", "चाहिए": " chahiye ", "देना": " dena ",
    "आधा": " aadha ", "पाव": " paav ", "डेढ़": " dedh ", "सवा": " sawa ", "ढाई": " dhai ",
    "किलो": " kilo ", "किलोग्राम": " kilogram ", "लीटर": " litre ", "ग्राम": " gram ",
    "पैकेट": " packet ", "बोतल": " bottle ", "डिब्बा": " box ", "दर्जन": " dozen ",
    "चीनी": " cheeni ", "शक्कर": " shakkar ", "आटा": " atta ", "चावल": " chawal ",
    "दाल": " dal ", "तेल": " tel ", "नमक": " namak ", "दूध": " doodh ", "दही": " dahi ",
    "मक्खन": " butter ", "ब्रेड": " bread ", "अंडे": " ande ", "अंडा": " anda ",
    "प्याज": " pyaz ", "टमाटर": " tamatar ", "आलू": " aloo ", "मैगी": " maggi ",
    "कल": " kal ", "आज": " aaj ", "सुबह": " subah ", "शाम": " shaam ",
    "घर": " ghar ", "और": " aur ", "भी": " bhi ",
    # Use digits for Hindi numeral words so "do" cannot be confused with
    # the Hinglish instruction "do" (give) by the order parser.
    "एक": " 1 ", "दो": " 2 ", "तीन": " 3 ", "चार": " 4 ", "पांच": " 5 ",
    "छह": " 6 ", "सात": " 7 ", "आठ": " 8 ", "नौ": " 9 ", "दस": " 10 ",
}

ENGLISH_GROCERY_TERMS = {
    "atta": "wheat flour", "chawal": "rice", "dal": "lentils", "tel": "oil",
    "cheeni": "sugar", "shakkar": "sugar", "namak": "salt", "doodh": "milk",
    "dahi": "curd", "pyaz": "onion", "pyaaz": "onion", "tamatar": "tomato",
    "aloo": "potato", "anda": "egg", "ande": "eggs", "aur": "and",
    "kal": "tomorrow", "aaj": "today", "subah": "morning", "shaam": "evening",
    "ghar": "home", "bhej": "send", "bhejna": "send", "dena": "please",
}

ENGLISH_FILLER_WORDS = {"bhaiya", "bhai", "ji", "ka", "ki", "ke", "bhi", "chahiye", "do"}


def normalize_hinglish_text(text: str) -> str:
    """Normalize transcription noise without inventing product names."""
    text = (text or "").lower().strip()
    for hindi, hinglish in sorted(DEVANAGARI_HINGLISH_MAP.items(), key=lambda entry: len(entry[0]), reverse=True):
        text = text.replace(hindi, hinglish)
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"[^\w\s.,!?;:/-]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*([,.!?;:])\s*", r"\1 ", text)
    return text.strip(" ,.!?;:")


def hindi_audio_to_english_text(text: str) -> str:
    """Convert supported Hindi/Hinglish grocery utterances into English text.

    This is intentionally a controlled vocabulary translation, not a free-form
    translation model: only quantities, units, delivery words, and grocery
    terms used by the catalog are changed. Unknown text stays visible.
    """
    normalized = normalize_hinglish_text(text)
    phrase_map = {
        "aadha kilo": "0.5 kg", "adha kilo": "0.5 kg", "half kilo": "0.5 kg",
        "paav kilo": "0.25 kg", "pav kilo": "0.25 kg", "dedh kilo": "1.5 kg",
        "sawa kilo": "1.25 kg", "sava kilo": "1.25 kg", "dhai kilo": "2.5 kg",
        "kal subah": "tomorrow morning", "kal shaam": "tomorrow evening",
        "ghar pe": "home", "ghar par": "home", "bhej dena": "send",
    }
    for phrase, replacement in sorted(phrase_map.items(), key=lambda entry: len(entry[0]), reverse=True):
        normalized = re.sub(rf"\b{re.escape(phrase)}\b", replacement, normalized)

    words = normalized.split()
    translated = []
    for index, word in enumerate(words):
        next_word = words[index + 1] if index + 1 < len(words) else ""
        if word in HINGLISH_NUMBER_MAP and next_word in UNIT_NORMALIZATION:
            translated.append(str(HINGLISH_NUMBER_MAP[word]).rstrip("0").rstrip(".") if isinstance(HINGLISH_NUMBER_MAP[word], float) else str(HINGLISH_NUMBER_MAP[word]))
            continue
        if word in {"kilo", "kilogram", "kilograms"}:
            translated.append("kg")
            continue
        if word in {"litre", "liter", "litres", "liters"}:
            translated.append("l")
            continue
        if word in {"gram", "grams"}:
            translated.append("g")
            continue
        if word in ENGLISH_FILLER_WORDS:
            continue
        translated.append(ENGLISH_GROCERY_TERMS.get(word, word))
    return re.sub(r"\s+", " ", " ".join(translated)).strip(" ,.!?;:")


def normalize_number_word(word: str) -> float:
    return HINGLISH_NUMBER_MAP.get(word.lower().strip(), 1.0)


def normalize_unit(unit: str) -> str:
    return UNIT_NORMALIZATION.get(unit.lower().strip(), unit.lower().strip())


def normalize_product_name(name: str) -> str:
    name = normalize_hinglish_text(name)
    return " ".join(ALIAS_MAP.get(token, token) for token in name.split())


def expand_aliases(text: str) -> str:
    words = text.split()
    expanded = []
    for word in words:
        expanded.append(ALIAS_MAP.get(word.lower(), word))
    return " ".join(expanded)


def normalize_for_matching(text: str) -> str:
    """Create a stable comparison key for catalog and user phrases."""
    text = normalize_hinglish_text(text)
    text = re.sub(r"\b(?:ka|ki|ke|please|dena|do|chahiye|lena|bhi|hai|hain)\b", " ", text)
    text = expand_aliases(text)
    return re.sub(r"\s+", " ", text).strip()


def extract_measurement(text: str) -> Optional[Tuple[float, str, str]]:
    """Return (value, canonical unit, matched phrase) when text has a measure."""
    words = normalize_hinglish_text(text).split()
    for index, word in enumerate(words):
        value: Optional[float] = None
        if re.fullmatch(r"\d+(?:\.\d+)?", word):
            value = float(word)
        elif word in HINGLISH_NUMBER_MAP:
            value = HINGLISH_NUMBER_MAP[word]
        if value is None or index + 1 >= len(words):
            continue
        unit_word = words[index + 1]
        unit = normalize_unit(unit_word)
        if unit == unit_word and unit_word not in UNIT_NORMALIZATION:
            continue
        return value, unit, f"{word} {unit_word}"
    return None
