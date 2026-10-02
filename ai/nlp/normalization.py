import re
from typing import Dict


HINGLISH_NUMBER_MAP = {
    "ek": 1, "do": 2, "teen": 3, "chaar": 4, "paanch": 5,
    "chhah": 6, "saat": 7, "aath": 8, "nau": 9, "das": 10,
    "gyarah": 11, "baarah": 12, "terah": 13, "chaudah": 14, "pandrah": 15,
    "solah": 16, "satrah": 17, "atharah": 18, "unnis": 19, "bees": 20,
    "adha": 0.5, "pauna": 0.75, "sava": 1.25, "dhai": 2.5, "sadhe": 2.5
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
    "box": "box", "boxes": "box"
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


def normalize_hinglish_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[,.!?;:]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def normalize_number_word(word: str) -> float:
    return HINGLISH_NUMBER_MAP.get(word.lower(), 1.0)


def normalize_unit(unit: str) -> str:
    return UNIT_NORMALIZATION.get(unit.lower(), unit.lower())


def normalize_product_name(name: str) -> str:
    name = name.lower().strip()
    return ALIAS_MAP.get(name, name)


def expand_aliases(text: str) -> str:
    words = text.split()
    expanded = []
    for word in words:
        expanded.append(ALIAS_MAP.get(word.lower(), word))
    return " ".join(expanded)