"""
Pokemon Champions - Data Generator
Run this script to pull/refresh data from PokeAPI.
Output: data/pokemon.json, data/moves.json, data/items.json
"""

import json
import time
import os
import requests
from pathlib import Path

BASE_URL = "https://pokeapi.co/api/v2"
OUT_DIR = Path("data")
OUT_DIR.mkdir(exist_ok=True)

# Full confirmed Champions roster from Serebii / launch sources
# Format: (pokedex_id, api_name, display_name, mega_forms)
# Roster sourced from Serebii: https://www.serebii.net/pokemonchampions/pokemon.shtml
CHAMPIONS_ROSTER = [
    (3,   "venusaur",          "Venusaur",           ["venusaur-mega"]),
    (6,   "charizard",         "Charizard",           ["charizard-mega"]),   # one mega entry
    (9,   "blastoise",         "Blastoise",           ["blastoise-mega"]),
    (15,  "beedrill",          "Beedrill",            ["beedrill-mega"]),
    (18,  "pidgeot",           "Pidgeot",             ["pidgeot-mega"]),
    (24,  "arbok",             "Arbok",               []),
    (25,  "pikachu",           "Pikachu",             []),
    (26,  "raichu",            "Raichu",              []),
    (26,  "raichu-alola",      "Raichu-Alola",        []),
    (36,  "clefable",          "Clefable",            ["clefable-mega"]),
    (38,  "ninetales",         "Ninetales",           []),
    (38,  "ninetales-alola",   "Ninetales-Alola",     []),
    (59,  "arcanine",          "Arcanine",            []),
    (59,  "arcanine-hisui",    "Arcanine-Hisui",      []),
    (65,  "alakazam",          "Alakazam",            ["alakazam-mega"]),
    (68,  "machamp",           "Machamp",             []),
    (71,  "victreebel",        "Victreebel",          ["victreebel-mega"]),
    (80,  "slowbro",           "Slowbro",             ["slowbro-mega"]),
    (80,  "slowbro-galar",     "Slowbro-Galar",       []),
    (94,  "gengar",            "Gengar",              ["gengar-mega"]),
    (115, "kangaskhan",        "Kangaskhan",          ["kangaskhan-mega"]),
    (121, "starmie",           "Starmie",             ["starmie-mega"]),
    (127, "pinsir",            "Pinsir",              ["pinsir-mega"]),
    (128, "tauros",            "Tauros",              []),
    (128, "tauros-paldea",     "Tauros-Paldea",       []),
    (130, "gyarados",          "Gyarados",            ["gyarados-mega"]),
    (132, "ditto",             "Ditto",               []),
    (134, "vaporeon",          "Vaporeon",            []),
    (135, "jolteon",           "Jolteon",             []),
    (136, "flareon",           "Flareon",             []),
    (142, "aerodactyl",        "Aerodactyl",          ["aerodactyl-mega"]),
    (143, "snorlax",           "Snorlax",             []),
    (149, "dragonite",         "Dragonite",           ["dragonite-mega"]),
    (154, "meganium",          "Meganium",            ["meganium-mega"]),
    (157, "typhlosion",        "Typhlosion",          []),
    (157, "typhlosion-hisui",  "Typhlosion-Hisui",    []),
    (160, "feraligatr",        "Feraligatr",          ["feraligatr-mega"]),
    (168, "ariados",           "Ariados",             []),
    (181, "ampharos",          "Ampharos",            ["ampharos-mega"]),
    (184, "azumarill",         "Azumarill",           []),
    (186, "politoed",          "Politoed",            []),
    (196, "espeon",            "Espeon",              []),
    (197, "umbreon",           "Umbreon",             []),
    (199, "slowking",          "Slowking",            []),
    (199, "slowking-galar",    "Slowking-Galar",       []),
    (205, "forretress",        "Forretress",          []),
    (208, "steelix",           "Steelix",             ["steelix-mega"]),
    (212, "scizor",            "Scizor",              ["scizor-mega"]),
    (214, "heracross",         "Heracross",           ["heracross-mega"]),
    (227, "skarmory",          "Skarmory",            ["skarmory-mega"]),
    (229, "houndoom",          "Houndoom",            ["houndoom-mega"]),
    (248, "tyranitar",         "Tyranitar",           ["tyranitar-mega"]),
    (279, "pelipper",          "Pelipper",            []),
    (282, "gardevoir",         "Gardevoir",           ["gardevoir-mega"]),
    (302, "sableye",           "Sableye",             ["sableye-mega"]),
    (306, "aggron",            "Aggron",              ["aggron-mega"]),
    (308, "medicham",          "Medicham",            ["medicham-mega"]),
    (310, "manectric",         "Manectric",           ["manectric-mega"]),
    (319, "sharpedo",          "Sharpedo",            ["sharpedo-mega"]),
    (323, "camerupt",          "Camerupt",            ["camerupt-mega"]),
    (324, "torkoal",           "Torkoal",             []),
    (334, "altaria",           "Altaria",             ["altaria-mega"]),
    (350, "milotic",           "Milotic",             []),
    (351, "castform",          "Castform",            []),
    (354, "banette",           "Banette",             ["banette-mega"]),
    (358, "chimecho",          "Chimecho",            ["chimecho-mega"]),
    (359, "absol",             "Absol",               ["absol-mega"]),
    (362, "glalie",            "Glalie",              ["glalie-mega"]),
    (389, "torterra",          "Torterra",            []),
    (392, "infernape",         "Infernape",           []),
    (395, "empoleon",          "Empoleon",            []),
    (405, "luxray",            "Luxray",              []),
    (407, "roserade",          "Roserade",            []),
    (409, "rampardos",         "Rampardos",           []),
    (411, "bastiodon",         "Bastiodon",           []),
    (428, "lopunny",           "Lopunny",             ["lopunny-mega"]),
    (442, "spiritomb",         "Spiritomb",           []),
    (445, "garchomp",          "Garchomp",            ["garchomp-mega"]),
    (448, "lucario",           "Lucario",             ["lucario-mega"]),
    (450, "hippowdon",         "Hippowdon",           []),
    (454, "toxicroak",         "Toxicroak",           []),
    (460, "abomasnow",         "Abomasnow",           ["abomasnow-mega"]),
    (461, "weavile",           "Weavile",             []),
    (464, "rhyperior",         "Rhyperior",           []),
    (470, "leafeon",           "Leafeon",             []),
    (471, "glaceon",           "Glaceon",             []),
    (472, "gliscor",           "Gliscor",             []),
    (473, "mamoswine",         "Mamoswine",           []),
    (475, "gallade",           "Gallade",             ["gallade-mega"]),
    (478, "froslass",          "Froslass",            ["froslass-mega"]),
    (479, "rotom",             "Rotom",               []),              # only base Rotom
    (497, "serperior",         "Serperior",           []),
    (500, "emboar",            "Emboar",              ["emboar-mega"]),
    (503, "samurott",          "Samurott",            []),
    (503, "samurott-hisui",    "Samurott-Hisui",      []),
    (505, "watchog",           "Watchog",             []),
    (510, "liepard",           "Liepard",             []),
    (512, "simisage",          "Simisage",            []),
    (514, "simisear",          "Simisear",            []),
    (516, "simipour",          "Simipour",            []),
    (530, "excadrill",         "Excadrill",           ["excadrill-mega"]),
    (531, "audino",            "Audino",              ["audino-mega"]),
    (534, "conkeldurr",        "Conkeldurr",          []),
    (547, "whimsicott",        "Whimsicott",          []),
    (553, "krookodile",        "Krookodile",          []),
    (563, "cofagrigus",        "Cofagrigus",          []),
    (569, "garbodor",          "Garbodor",            []),
    (571, "zoroark",           "Zoroark",             []),
    (571, "zoroark-hisui",     "Zoroark-Hisui",       []),
    (579, "reuniclus",         "Reuniclus",           []),
    (584, "vanilluxe",         "Vanilluxe",           []),
    (587, "emolga",            "Emolga",              []),
    (609, "chandelure",        "Chandelure",          ["chandelure-mega"]),
    (614, "beartic",           "Beartic",             []),
    (618, "stunfisk",          "Stunfisk",            []),
    (618, "stunfisk-galar",    "Stunfisk-Galar",      []),
    (623, "golurk",            "Golurk",              ["golurk-mega"]),
    (635, "hydreigon",         "Hydreigon",           []),
    (637, "volcarona",         "Volcarona",           []),
    (652, "chesnaught",        "Chesnaught",          ["chesnaught-mega"]),
    (655, "delphox",           "Delphox",             ["delphox-mega"]),
    (658, "greninja",          "Greninja",            ["greninja-mega"]),
    (660, "diggersby",         "Diggersby",           []),
    (663, "talonflame",        "Talonflame",          []),
    (666, "vivillon",          "Vivillon",            []),
    (670, "floette",           "Floette",             ["floette-mega"]),
    (671, "florges",           "Florges",             []),
    (675, "pangoro",           "Pangoro",             []),
    (676, "furfrou",           "Furfrou",             []),
    (678, "meowstic",          "Meowstic",            ["meowstic-mega"]),
    (681, "aegislash",         "Aegislash",           []),
    (683, "aromatisse",        "Aromatisse",          []),
    (685, "slurpuff",          "Slurpuff",            []),
    (693, "clawitzer",         "Clawitzer",           []),
    (695, "heliolisk",         "Heliolisk",           []),
    (697, "tyrantrum",         "Tyrantrum",           []),
    (699, "aurorus",           "Aurorus",             []),
    (700, "sylveon",           "Sylveon",             []),
    (701, "hawlucha",          "Hawlucha",            ["hawlucha-mega"]),
    (702, "dedenne",           "Dedenne",             []),
    (706, "goodra",            "Goodra",              []),
    (706, "goodra-hisui",      "Goodra-Hisui",        []),
    (707, "klefki",            "Klefki",              []),
    (709, "trevenant",         "Trevenant",           []),
    (711, "gourgeist",         "Gourgeist",           []),
    (713, "avalugg",           "Avalugg",             []),
    (713, "avalugg-hisui",     "Avalugg-Hisui",       []),
    (715, "noivern",           "Noivern",             []),
    (724, "decidueye",         "Decidueye",           []),
    (724, "decidueye-hisui",   "Decidueye-Hisui",     []),
    (727, "incineroar",        "Incineroar",          []),
    (730, "primarina",         "Primarina",           []),
    (733, "toucannon",         "Toucannon",           []),
    (740, "crabominable",      "Crabominable",        ["crabominable-mega"]),
    (745, "lycanroc",          "Lycanroc",            []),
    (748, "toxapex",           "Toxapex",             []),
    (750, "mudsdale",          "Mudsdale",            []),
    (752, "araquanid",         "Araquanid",           []),
    (758, "salazzle",          "Salazzle",            []),
    (763, "tsareena",          "Tsareena",            []),
    (765, "oranguru",          "Oranguru",            []),
    (766, "passimian",         "Passimian",           []),
    (778, "mimikyu",           "Mimikyu",             []),
    (780, "drampa",            "Drampa",              ["drampa-mega"]),
    (784, "kommo-o",           "Kommo-o",             []),
    (823, "corviknight",       "Corviknight",         []),
    (841, "flapple",           "Flapple",             []),
    (842, "appletun",          "Appletun",            []),
    (844, "sandaconda",        "Sandaconda",          []),
    (855, "polteageist",       "Polteageist",         []),
    (858, "hatterene",         "Hatterene",           []),
    (866, "mr-rime",           "Mr. Rime",            []),
    (867, "runerigus",         "Runerigus",           []),
    (869, "alcremie",          "Alcremie",            []),
    (877, "morpeko",           "Morpeko",             []),
    (887, "dragapult",         "Dragapult",           []),
    (899, "wyrdeer",           "Wyrdeer",             []),
    (900, "kleavor",           "Kleavor",             []),
    (902, "basculegion",       "Basculegion",         []),
    (903, "sneasler",          "Sneasler",            []),
    (908, "meowscarada",       "Meowscarada",         []),
    (911, "skeledirge",        "Skeledirge",          []),
    (914, "quaquaval",         "Quaquaval",           []),
    (925, "maushold",          "Maushold",            []),
    (934, "garganacl",         "Garganacl",           []),
    (936, "armarouge",         "Armarouge",           []),
    (937, "ceruledge",         "Ceruledge",           []),
    (939, "bellibolt",         "Bellibolt",           []),
    (952, "scovillain",        "Scovillain",          ["scovillain-mega"]),
    (956, "espathra",          "Espathra",            []),
    (959, "tinkaton",          "Tinkaton",            []),
    (964, "palafin",           "Palafin",             []),
    (968, "orthworm",          "Orthworm",            []),
    (970, "glimmora",          "Glimmora",            ["glimmora-mega"]),
    (981, "farigiraf",         "Farigiraf",           []),
    (983, "kingambit",         "Kingambit",           []),
    (1013,"sinistcha",         "Sinistcha",           []),
    (1018,"archaludon",        "Archaludon",          []),
    (1019,"hydrapple",         "Hydrapple",           []),
]

# Held items relevant to damage calc (defensive or offensive)
HELD_ITEMS = [
    "leftovers", "black-sludge", "assault-vest", "rocky-helmet",
    "choice-band", "choice-specs", "choice-scarf", "life-orb",
    "expert-belt", "muscle-band", "wise-glasses", "focus-sash",
    "eviolite", "sitrus-berry", "lum-berry", "weakness-policy",
    "booster-energy", "clear-amulet", "covert-cloak", "mirror-herb",
    "loaded-dice", "punching-glove", "protective-pads",
    "flame-orb", "toxic-orb", "iron-ball", "ring-target",
    "safety-goggles", "shed-shell", "white-herb",
    # Type-boosting plates/items (+20%)
    "charcoal", "mystic-water", "miracle-seed", "magnet",
    "never-melt-ice", "black-belt", "poison-barb", "soft-sand",
    "sharp-beak", "twisted-spoon", "silverpowder", "hard-stone",
    "spell-tag", "dragon-fang", "black-glasses", "metal-coat",
    "silk-scarf", "fairy-feather",
]

NATURES = [
    {"name": "Hardy",   "boost": None,    "drop": None},
    {"name": "Lonely",  "boost": "attack","drop": "defense"},
    {"name": "Brave",   "boost": "attack","drop": "speed"},
    {"name": "Adamant", "boost": "attack","drop": "special-attack"},
    {"name": "Naughty", "boost": "attack","drop": "special-defense"},
    {"name": "Bold",    "boost": "defense","drop": "attack"},
    {"name": "Docile",  "boost": None,    "drop": None},
    {"name": "Relaxed", "boost": "defense","drop": "speed"},
    {"name": "Impish",  "boost": "defense","drop": "special-attack"},
    {"name": "Lax",     "boost": "defense","drop": "special-defense"},
    {"name": "Timid",   "boost": "speed", "drop": "attack"},
    {"name": "Hasty",   "boost": "speed", "drop": "defense"},
    {"name": "Serious", "boost": None,    "drop": None},
    {"name": "Jolly",   "boost": "speed", "drop": "special-attack"},
    {"name": "Naive",   "boost": "speed", "drop": "special-defense"},
    {"name": "Modest",  "boost": "special-attack","drop": "attack"},
    {"name": "Mild",    "boost": "special-attack","drop": "defense"},
    {"name": "Quiet",   "boost": "special-attack","drop": "speed"},
    {"name": "Bashful", "boost": None,    "drop": None},
    {"name": "Rash",    "boost": "special-attack","drop": "special-defense"},
    {"name": "Calm",    "boost": "special-defense","drop": "attack"},
    {"name": "Gentle",  "boost": "special-defense","drop": "defense"},
    {"name": "Sassy",   "boost": "special-defense","drop": "speed"},
    {"name": "Careful", "boost": "special-defense","drop": "special-attack"},
    {"name": "Quirky",  "boost": None,    "drop": None},
]

TYPE_CHART = {
    "normal":   {"rock":0.5,"steel":0.5,"ghost":0},
    "fire":     {"fire":0.5,"water":0.5,"rock":0.5,"dragon":0.5,"grass":2,"ice":2,"bug":2,"steel":2},
    "water":    {"water":0.5,"grass":0.5,"dragon":0.5,"fire":2,"ground":2,"rock":2},
    "electric": {"electric":0.5,"grass":0.5,"dragon":0.5,"ground":0,"flying":2,"water":2},
    "grass":    {"fire":0.5,"grass":0.5,"poison":0.5,"flying":0.5,"bug":0.5,"dragon":0.5,"steel":0.5,"water":2,"ground":2,"rock":2},
    "ice":      {"water":0.5,"ice":0.5,"steel":0.5,"fire":0.5,"grass":2,"ground":2,"flying":2,"dragon":2},
    "fighting": {"poison":0.5,"flying":0.5,"psychic":0.5,"bug":0.5,"fairy":0.5,"ghost":0,"normal":2,"ice":2,"rock":2,"dark":2,"steel":2},
    "poison":   {"poison":0.5,"ground":0.5,"rock":0.5,"ghost":0.5,"steel":0,"grass":2,"fairy":2},
    "ground":   {"grass":0.5,"bug":0.5,"flying":0,"fire":2,"electric":2,"poison":2,"rock":2,"steel":2},
    "flying":   {"electric":0.5,"rock":0.5,"steel":0.5,"grass":2,"fighting":2,"bug":2},
    "psychic":  {"psychic":0.5,"steel":0.5,"dark":0,"fighting":2,"poison":2},
    "bug":      {"fire":0.5,"fighting":0.5,"flying":0.5,"ghost":0.5,"steel":0.5,"fairy":0.5,"grass":2,"psychic":2,"dark":2},
    "rock":     {"fighting":0.5,"ground":0.5,"steel":0.5,"fire":2,"ice":2,"flying":2,"bug":2},
    "ghost":    {"normal":0,"dark":0.5,"ghost":2,"psychic":2},
    "dragon":   {"steel":0.5,"fairy":0,"dragon":2},
    "dark":     {"fighting":0.5,"dark":0.5,"fairy":0.5,"ghost":2,"psychic":2},
    "steel":    {"fire":0.5,"water":0.5,"electric":0.5,"steel":0.5,"ice":2,"rock":2,"fairy":2},
    "fairy":    {"fire":0.5,"poison":0.5,"steel":0.5,"fighting":2,"dragon":2,"dark":2},
}

def get(url, retries=3):
    for i in range(retries):
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 404:
                return None
        except Exception as e:
            if i == retries - 1:
                print(f"  FAILED: {url} — {e}")
                return None
            time.sleep(1)
    return None

def fetch_pokemon(api_name_or_id):
    data = get(f"{BASE_URL}/pokemon/{api_name_or_id}")
    if not data:
        return None

    stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
    types = [t["type"]["name"] for t in data["types"]]
    abilities = [a["ability"]["name"] for a in data["abilities"]]

    moves = []
    for m in data["moves"]:
        for vg in m["version_group_details"]:
            if vg["version_group"]["name"] in ("scarlet-violet", "sword-shield", "sun-moon", "ultra-sun-ultra-moon", "brilliant-diamond-and-shining-pearl", "the-indigo-disk", "the-teal-mask"):
                moves.append(m["move"]["name"])
                break

    sprite = data["sprites"].get("front_default") or ""
    official = ""
    if data["sprites"].get("other") and data["sprites"]["other"].get("official-artwork"):
        official = data["sprites"]["other"]["official-artwork"].get("front_default", "")

    return {
        "name": data["name"],
        "stats": stats,
        "types": types,
        "abilities": abilities,
        "moves": list(set(moves)),
        "sprite": sprite,
        "artwork": official,
        "weight": data.get("weight", 0),
    }

def fetch_move(move_name):
    data = get(f"{BASE_URL}/move/{move_name}")
    if not data:
        return None
    if not data.get("power"):
        return None

    entries = data.get("effect_entries") or []
    en_effect = next((e.get("short_effect","") for e in entries if e.get("language",{}).get("name") == "en"), "")
    effect_chance = data.get("effect_chance")
    if effect_chance and "$effect_chance" in en_effect:
        en_effect = en_effect.replace("$effect_chance", str(effect_chance))

    return {
        "name": move_name,
        "display": move_name.replace("-", " ").title(),
        "type": data["type"]["name"],
        "category": data["damage_class"]["name"],
        "power": data["power"],
        "accuracy": data["accuracy"],
        "pp": data["pp"],
        "priority": data.get("priority", 0),
        "effect": en_effect,
    }

def fetch_item(item_name):
    data = get(f"{BASE_URL}/item/{item_name}")
    if not data:
        return None
    return {
        "name": item_name,
        "display": item_name.replace("-", " ").title(),
        "effect": (data.get("effect_entries") or [{}])[0].get("short_effect", ""),
        "category": data.get("category", {}).get("name", ""),
    }

def run():
    print("=== Pokemon Champions Data Generator ===\n")

    # --- Pokemon ---
    print(f"Fetching {len(CHAMPIONS_ROSTER)} base Pokemon + mega forms...")
    pokemon_data = {}
    all_move_names = set()

    base_entries = {}
    seen_dex_ids = set()
    for entry in CHAMPIONS_ROSTER:
        dex_id, api_name, display, megas = entry
        if api_name in base_entries:
            continue
        base_entries[api_name] = (dex_id, display, megas)

    for api_name, (dex_id, display, megas) in base_entries.items():
        # If this dex_id has already been used, it's a regional/alternate form — use name
        lookup = dex_id if dex_id not in seen_dex_ids else api_name
        seen_dex_ids.add(dex_id)
        print(f"  {display} (#{dex_id})...", end=" ", flush=True)
        poke = fetch_pokemon(lookup)
        if poke:
            poke["name"] = api_name
            poke["display"] = display
            poke["dex_id"] = dex_id
            poke["is_mega"] = False
            poke["base_form"] = api_name
            all_move_names.update(poke["moves"])
            pokemon_data[api_name] = poke
            print("ok")
        else:
            print("not found, skipping")
        time.sleep(0.3)

        for mega_name in megas:
            print(f"    {mega_name}...", end=" ", flush=True)
            mega = fetch_pokemon(mega_name)
            if mega:
                mega["display"] = mega_name.replace("-", " ").title()
                mega["dex_id"] = dex_id
                mega["is_mega"] = True
                mega["base_form"] = api_name
                mega["moves"] = poke["moves"] if poke else []
                pokemon_data[mega_name] = mega
                print("ok")
            else:
                print("not found")
            time.sleep(0.3)

    # --- Moves --- fetch ALL moves from PokeAPI, not just roster learnsets
    print(f"\nFetching full move list from PokeAPI...")
    move_index = get(f"{BASE_URL}/move?limit=2000")
    all_api_moves = [m["name"] for m in (move_index or {}).get("results", [])]
    print(f"  {len(all_api_moves)} moves found. Fetching damaging ones...")

    move_data = {}
    chunk = 0
    for move_name in all_api_moves:
        chunk += 1
        if chunk % 100 == 0:
            print(f"  {chunk}/{len(all_api_moves)} checked, {len(move_data)} damaging so far...")
        m = fetch_move(move_name)
        if m:
            move_data[move_name] = m
        time.sleep(0.1)

    print(f"  Done. {len(move_data)} damaging moves collected.")

    # --- Items ---
    print(f"\nFetching {len(HELD_ITEMS)} held items...")
    item_data = {}
    for item_name in HELD_ITEMS:
        print(f"  {item_name}...", end=" ", flush=True)
        it = fetch_item(item_name)
        if it:
            item_data[item_name] = it
            print("ok")
        else:
            print("not found")
        time.sleep(0.2)

    # --- Save ---
    out_pokemon = {
        "version": 1,
        "generated": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "count": len(pokemon_data),
        "pokemon": pokemon_data,
    }
    out_moves = {
        "version": 1,
        "generated": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "count": len(move_data),
        "moves": move_data,
    }
    out_items = {
        "version": 1,
        "generated": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "natures": NATURES,
        "type_chart": TYPE_CHART,
        "items": item_data,
    }

    (OUT_DIR / "pokemon.json").write_text(json.dumps(out_pokemon, indent=2))
    (OUT_DIR / "moves.json").write_text(json.dumps(out_moves, indent=2))
    (OUT_DIR / "meta.json").write_text(json.dumps(out_items, indent=2))

    print(f"\n=== Done ===")
    print(f"  data/pokemon.json — {len(pokemon_data)} entries")
    print(f"  data/moves.json   — {len(move_data)} entries")
    print(f"  data/meta.json    — natures, type chart, {len(item_data)} items")

if __name__ == "__main__":
    run()
