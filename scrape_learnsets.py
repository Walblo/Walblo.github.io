"""
Serebii Learnset Scraper for Pokemon Champions Calc
Scrapes move data from Serebii's Champions Pokedex pages.
Run after generate_data.py — updates pokemon.json with correct learnsets.

Usage:
    python scrape_learnsets.py

Requires: requests, beautifulsoup4
Install:  pip install requests beautifulsoup4
"""

import json
import time
import re
import sys
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run:")
    print("  pip install requests beautifulsoup4")
    sys.exit(1)

DATA_DIR = Path("data")
POKEMON_FILE = DATA_DIR / "pokemon.json"
MOVES_FILE   = DATA_DIR / "moves.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Champions Pokedex has per-pokemon learnsets specific to this game
SEREBII_BASE = "https://www.serebii.net/pokedex-champions"

# Map our api_name keys to Serebii Champions URL names
# Most are just the lowercase name; regional forms need special handling
API_TO_SEREBII_NAME = {
    "raichu-alola":      "raichu",       # Serebii uses same page, form listed within
    "ninetales-alola":   "ninetales",
    "arcanine-hisui":    "arcanine",
    "slowbro-galar":     "slowbro",
    "slowking-galar":    "slowking",
    "tauros-paldea":     "tauros",
    "typhlosion-hisui":  "typhlosion",
    "samurott-hisui":    "samurott",
    "zoroark-hisui":     "zoroark",
    "stunfisk-galar":    "stunfisk",
    "goodra-hisui":      "goodra",
    "avalugg-hisui":     "avalugg",
    "decidueye-hisui":   "decidueye",
    "mr-rime":           "mr.rime",
    "kommo-o":           "kommo-o",
    # Megas use the base Pokemon page
    "venusaur-mega":     "venusaur",
    "charizard-mega":    "charizard",
    "blastoise-mega":    "blastoise",
    "beedrill-mega":     "beedrill",
    "pidgeot-mega":      "pidgeot",
    "clefable-mega":     "clefable",
    "alakazam-mega":     "alakazam",
    "victreebel-mega":   "victreebel",
    "slowbro-mega":      "slowbro",
    "gengar-mega":       "gengar",
    "kangaskhan-mega":   "kangaskhan",
    "starmie-mega":      "starmie",
    "pinsir-mega":       "pinsir",
    "gyarados-mega":     "gyarados",
    "aerodactyl-mega":   "aerodactyl",
    "dragonite-mega":    "dragonite",
    "meganium-mega":     "meganium",
    "feraligatr-mega":   "feraligatr",
    "ampharos-mega":     "ampharos",
    "steelix-mega":      "steelix",
    "scizor-mega":       "scizor",
    "heracross-mega":    "heracross",
    "skarmory-mega":     "skarmory",
    "houndoom-mega":     "houndoom",
    "tyranitar-mega":    "tyranitar",
    "gardevoir-mega":    "gardevoir",
    "sableye-mega":      "sableye",
    "aggron-mega":       "aggron",
    "medicham-mega":     "medicham",
    "manectric-mega":    "manectric",
    "sharpedo-mega":     "sharpedo",
    "camerupt-mega":     "camerupt",
    "altaria-mega":      "altaria",
    "banette-mega":      "banette",
    "chimecho-mega":     "chimecho",
    "absol-mega":        "absol",
    "glalie-mega":       "glalie",
    "lopunny-mega":      "lopunny",
    "garchomp-mega":     "garchomp",
    "lucario-mega":      "lucario",
    "abomasnow-mega":    "abomasnow",
    "gallade-mega":      "gallade",
    "froslass-mega":     "froslass",
    "emboar-mega":       "emboar",
    "excadrill-mega":    "excadrill",
    "audino-mega":       "audino",
    "chandelure-mega":   "chandelure",
    "golurk-mega":       "golurk",
    "chesnaught-mega":   "chesnaught",
    "delphox-mega":      "delphox",
    "greninja-mega":     "greninja",
    "floette-mega":      "floette",
    "meowstic-mega":     "meowstic",
    "hawlucha-mega":     "hawlucha",
    "crabominable-mega": "crabominable",
    "drampa-mega":       "drampa",
    "scovillain-mega":   "scovillain",
    "glimmora-mega":     "glimmora",
}

def normalize_move_name(name):
    """Convert display name to our internal key format."""
    return name.lower().strip().replace(" ", "-").replace("'", "").replace(".", "").replace(",","")

def fetch_champions_moves(api_name, display_name):
    """
    Fetch all moves a Pokemon can learn from Serebii Champions Pokedex.
    Returns a list of normalized move name strings, or None on failure.
    """
    # Determine the Serebii URL name
    serebii_name = API_TO_SEREBII_NAME.get(api_name)
    if not serebii_name:
        # Default: lowercase, strip trailing -mega etc if not caught above
        serebii_name = api_name.lower().replace("_", "-")

    url = f"{SEREBII_BASE}/{serebii_name}/"

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            # Try without trailing slash
            r = requests.get(url.rstrip("/") + ".shtml", headers=HEADERS, timeout=15)
            if r.status_code != 200:
                print(f"    HTTP {r.status_code} for {url}")
                return None
    except Exception as e:
        print(f"    Error fetching {url}: {e}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    moves = set()

    # Champions Pokedex links moves as /attackdex-champions/movename.shtml
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/attackdex-champions/" in href:
            move_name = href.split("/attackdex-champions/")[-1].replace(".shtml", "")
            if move_name and move_name not in ("", "normal", "fire", "water", "electric",
                "grass", "ice", "fighting", "poison", "ground", "flying", "psychic",
                "bug", "rock", "ghost", "dragon", "dark", "steel", "fairy"):
                moves.add(normalize_move_name(move_name))

    return list(moves) if moves else None


ATTACKDEX_BASE = "https://www.serebii.net/attackdex-champions"

TYPE_NAMES = {"normal","fire","water","electric","grass","ice","fighting","poison",
              "ground","flying","psychic","bug","rock","ghost","dragon","dark","steel","fairy"}

def fetch_move_data(move_key):
    """
    Fetch move data from Serebii Champions Attackdex.
    Returns a dict with type, category, power, accuracy, pp, effect, or None on failure.
    """
    url = f"{ATTACKDEX_BASE}/{move_key}.shtml"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None
    except Exception as e:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # Display name: grab from page title or h1
    display = move_key.replace("-", " ").title()
    title_tag = soup.find("title")
    if title_tag:
        t = title_tag.text.strip()
        if " - " in t:
            display = t.split(" - ")[0].strip()

    # Find the main move data table — look for cells with type/cat/power/acc
    move_type = "normal"
    category = "status"
    power = 0
    accuracy = 100
    pp = 10
    effect = ""

    # Type: look for attackdex-champions type image links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/attackdex-champions/" in href:
            candidate = href.split("/attackdex-champions/")[-1].replace(".shtml","").lower()
            if candidate in TYPE_NAMES:
                move_type = candidate
                break

    # Scan table cells for numeric values and category
    tables = soup.find_all("table")
    for table in tables:
        cells = [td.get_text(strip=True) for td in table.find_all("td")]
        for i, cell in enumerate(cells):
            cl = cell.lower()
            if cl in ("physical", "special", "other", "status"):
                category = "physical" if cl == "physical" else ("special" if cl == "special" else "status")
            # Power: a number in the range 1-250 that's not accuracy-like
            if cell.isdigit():
                val = int(cell)
                if 1 <= val <= 250 and power == 0:
                    power = val
                elif 30 <= val <= 101 and accuracy == 100:
                    accuracy = val if val <= 100 else 0
                elif 1 <= val <= 64 and pp == 10:
                    pp = val

    # Effect: longest plain text paragraph on the page
    for p in soup.find_all("td"):
        text = p.get_text(strip=True)
        if len(text) > 40 and not text.startswith("©") and "serebii" not in text.lower():
            effect = text[:300]
            break

    return {
        "name": move_key,
        "display": display,
        "type": move_type,
        "category": category,
        "power": power,
        "accuracy": accuracy if accuracy <= 100 else 0,
        "pp": pp,
        "priority": 0,
        "effect": effect
    }


def run():
    print("=== Serebii Learnset Scraper ===\n")

    if not POKEMON_FILE.exists():
        print(f"ERROR: {POKEMON_FILE} not found. Run generate_data.py first.")
        sys.exit(1)

    with open(POKEMON_FILE) as f:
        poke_data = json.load(f)

    with open(MOVES_FILE) as f:
        move_data = json.load(f)

    known_moves = set(move_data["moves"].keys())
    pokemon = poke_data["pokemon"]
    total = len(pokemon)
    updated = 0
    failed = 0

    # Cache by serebii URL name so megas don't re-fetch the same page
    seen_url = {}

    for api_name, poke in pokemon.items():
        display = poke.get("display", api_name)
        serebii_name = API_TO_SEREBII_NAME.get(api_name, api_name.lower())

        if serebii_name in seen_url:
            poke["moves"] = seen_url[serebii_name]
            print(f"  {display}: cached ({len(poke['moves'])} moves)")
            updated += 1
            continue

        print(f"  {display} ({api_name})...", end=" ", flush=True)
        moves = fetch_champions_moves(api_name, display)

        if moves:
            poke["moves"] = moves
            seen_url[serebii_name] = moves
            print(f"{len(moves)} moves")
            updated += 1
        else:
            print("FAILED — keeping existing learnset")
            failed += 1

        time.sleep(0.5)  # be polite to Serebii

    # Save pokemon.json
    poke_data["pokemon"] = pokemon
    poke_data["generated"] = __import__("datetime").datetime.utcnow().isoformat() + "Z"
    with open(POKEMON_FILE, "w") as f:
        json.dump(poke_data, f, indent=2)

    print(f"\n=== Done ===")
    print(f"  Updated: {updated}/{total}")
    print(f"  Failed:  {failed}/{total}")
    print(f"  Saved to {POKEMON_FILE}")

    # ── Second pass: fetch data for any moves missing from moves.json ──
    all_learnset_moves = set()
    for poke in pokemon.values():
        all_learnset_moves.update(poke.get("moves", []))

    missing_moves = all_learnset_moves - set(move_data["moves"].keys())
    if missing_moves:
        print(f"\n=== Fetching {len(missing_moves)} missing moves from Champions Attackdex ===\n")
        moves_added = 0
        for move_key in sorted(missing_moves):
            print(f"  {move_key}...", end=" ", flush=True)
            data = fetch_move_data(move_key)
            if data:
                move_data["moves"][move_key] = data
                moves_added += 1
                print(f"ok ({data['type']}, {data['category']}, {data['power']}bp)")
            else:
                print("FAILED")
            time.sleep(0.4)

        move_data["generated"] = __import__("datetime").datetime.utcnow().isoformat() + "Z"
        with open(MOVES_FILE, "w") as f:
            json.dump(move_data, f, indent=2)
        print(f"\n  Added {moves_added}/{len(missing_moves)} moves to {MOVES_FILE}")
    else:
        print("\n  moves.json already up to date.")


if __name__ == "__main__":
    run()
