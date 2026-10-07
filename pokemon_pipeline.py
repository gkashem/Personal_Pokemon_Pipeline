"""
pokemon_pipeline.py

Reads Pokemon.xlsx and rebuilds pokemon_ui.html by injecting the parsed data
into pokemon_ui_template.html. The workbook is only ever read, never written.

Keep these files in the same folder:
  Pokemon.xlsx              <- your spreadsheet (edit this)
  pokemon_ui_template.html  <- page skeleton (don't edit unless changing layout)
  pokemon_pipeline.py       <- this script
  pokemon_ui.html           <- generated, open this in a browser

USAGE
-----
    python pokemon_pipeline.py

Re-run it after every change to Pokemon.xlsx (new teams, Pokemon, moves...).

Requires: pip install openpyxl

WORKBOOK LAYOUT (row 1 = headers)
---------------------------------
  Teams : Region | Team | Pokemon | Type | Type | Move x4 | Generation | Rating
          One row per Pokemon. A team is a run of consecutive rows with the
          same Region + Team. Rating is MVP, HM or blank.
  Type  : Type       | Ace | Team | Team2 | ... (the Pokemon picked for that type)
  Gen   : Generation | Ace | Team | Team2 | ...
  Moves : Move | Type | Split   (every move used on the Teams sheet)

Columns on the Teams sheet are found by their header text, so they can be
reordered. Every count on the dashboard (Mons/Used Count, move usage, the
Moves pivots, the header stats, the Grid pools, STAB) is worked out here
from the raw rows - the workbook holds no formulas for them.

SPRITES
-------
Every sprite style comes from PokeAPI's sprite repository by Pokedex id,
except Idle Animation, which comes from Pokemon Showdown by name. Names are
matched to PokeAPI's Pokemon list (pokeapi_pokemon.csv / pokeapi_species.csv,
downloaded once and cached next to this script - delete them to refresh after
a new game adds Pokemon). The sheet's spelling is converted automatically:
  "Urshifu-RapidStrike" -> urshifu-rapid-strike   (capital letters split words)
  "Tauros-Paldea-Aqua"  -> tauros-paldea-aqua-breed (unique longer match)
  "Mimikyu"             -> mimikyu-disguised        (species' default form)
Anything that still doesn't match is listed when the script runs; add it to
NAME_OVERRIDES as {"Name As In Sheet": "pokeapi-identifier"}.
"""

import csv
import io
import json
import re
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
SOURCE_FILE = HERE / "Pokemon.xlsx"
TEMPLATE_FILE = HERE / "pokemon_ui_template.html"
HTML_OUTPUT_FILE = HERE / "pokemon_ui.html"

RATING_STARS = {"MVP": "mvp", "HM": "hm"}

# "Violet (2)" and "Violet" are the same game for the Games Played count
GAME_SUFFIX = re.compile(r"\s*\(\d+\)\s*$")


# ===========================================================================
# Sprites
# ===========================================================================

POKEAPI_CSV = "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/{}.csv"
POKEAPI_SPRITES = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon"
SHOWDOWN_ANIMATED = "https://play.pokemonshowdown.com/sprites/ani/{}.gif"
# Black/White animated pixel sprites only exist for the 649 Pokemon of
# Gens 1-5 (default forms); everything else uses the Front Static sprite.
BW_ANIMATED_MAX_ID = 649

# {"Name As In Sheet": "pokeapi-identifier"} for names the automatic matching misses
NAME_OVERRIDES = {}
# {"pokeapi-identifier": "showdown-file-name"} where Showdown's spelling differs
SHOWDOWN_OVERRIDES = {
    "tauros-paldea-combat-breed": "tauros-paldeacombat",
    "tauros-paldea-blaze-breed": "tauros-paldeablaze",
    "tauros-paldea-aqua-breed": "tauros-paldeaaqua",
}


def _cached_csv(name):
    path = HERE / f"pokeapi_{name}.csv"
    if not path.exists():
        with urllib.request.urlopen(POKEAPI_CSV.format(name), timeout=30) as r:
            path.write_bytes(r.read())
    return list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8"))))


class SpriteResolver:
    def __init__(self):
        try:
            pokemon = _cached_csv("pokemon")
            species = _cached_csv("pokemon_species")
        except Exception as e:  # offline and no cache: Showdown-only sprites
            print(f"      Couldn't download PokeAPI's Pokemon list ({e}); using Showdown sprites only.")
            pokemon, species = [], []
        species_name = {int(s["id"]): s["identifier"] for s in species}
        self.rows = {}
        for p in pokemon:
            sid = int(p["species_id"])
            self.rows[p["identifier"]] = {
                "id": int(p["id"]),
                "identifier": p["identifier"],
                "species": species_name.get(sid, p["identifier"]),
                "is_default": p["is_default"] == "1",
            }
        self.cache = {}
        self.unmatched = set()

    @staticmethod
    def slug(name):
        n = re.sub(r"(?<=[a-z])(?=[A-Z])", "-", str(name).strip())  # RapidStrike -> Rapid-Strike
        n = n.lower().replace("♀", "-f").replace("♂", "-m")
        n = re.sub(r"[.'’:é]", lambda m: "e" if m.group() == "é" else "", n)
        return re.sub(r"[^a-z0-9]+", "-", n).strip("-")

    def match(self, name):
        if name in NAME_OVERRIDES:
            return self.rows.get(NAME_OVERRIDES[name])
        s = self.slug(name)
        if s in self.rows:
            return self.rows[s]
        longer = [r for k, r in self.rows.items() if k.startswith(s + "-")]
        for r in longer:  # bare species name -> its default form ("Mimikyu")
            if r["is_default"]:
                return r
        if len(longer) == 1:  # unique longer form ("Tauros-Paldea-Aqua")
            return longer[0]
        return None

    def fields(self, name):
        if name in self.cache:
            return self.cache[name]
        r = self.match(name)
        if r:
            pid = r["id"]
            if r["identifier"] in SHOWDOWN_OVERRIDES:
                sd = SHOWDOWN_OVERRIDES[r["identifier"]]
            else:
                sd = r["species"].replace("-", "")
                forme = r["identifier"][len(r["species"]):].strip("-")
                if not r["is_default"] and forme:
                    sd += "-" + forme.replace("-", "")
            front = f"{POKEAPI_SPRITES}/{pid}.png"
            f = {
                "sprite": f"{POKEAPI_SPRITES}/other/home/{pid}.png",
                "spriteAnimated": SHOWDOWN_ANIMATED.format(sd),
                "spriteOfficial": f"{POKEAPI_SPRITES}/other/official-artwork/{pid}.png",
                "spriteFront": front,
                "spritePixel": (f"{POKEAPI_SPRITES}/versions/generation-v/black-white/animated/{pid}.gif"
                                if r["is_default"] and pid <= BW_ANIMATED_MAX_ID else front),
            }
        else:
            self.unmatched.add(name)
            guess = SHOWDOWN_ANIMATED.format(self.slug(name).replace("-", ""))
            f = {"sprite": guess, "spriteAnimated": guess, "spriteOfficial": None,
                 "spriteFront": None, "spritePixel": None}
        self.cache[name] = f
        return f


# ===========================================================================
# Workbook
# ===========================================================================

def _clean(v):
    if v is None:
        return None
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    v = str(v).strip()
    return v or None


def _header_columns(ws):
    """{lower-case header: [column indexes]} for row 1."""
    cols = defaultdict(list)
    for i, c in enumerate(ws[1]):
        h = _clean(c.value)
        if h:
            cols[h.lower()].append(i)
    return cols


def _need(cols, name, sheet):
    if name not in cols:
        raise SystemExit(f"'{sheet}' sheet has no '{name.title()}' column in row 1.")
    return cols[name]


def read_teams(wb, sprites):
    ws = wb["Teams"]
    cols = _header_columns(ws)
    c_region, c_team, c_mon = (_need(cols, h, "Teams")[0] for h in ("region", "team", "pokemon"))
    c_types = _need(cols, "type", "Teams")
    c_moves = _need(cols, "move", "Teams")
    c_gen = _need(cols, "generation", "Teams")[0]
    c_rating = _need(cols, "rating", "Teams")[0]

    teams = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        name = _clean(row[c_mon])
        if not name:
            continue
        region, team = _clean(row[c_region]), _clean(row[c_team])
        if not teams or (teams[-1]["region"], teams[-1]["team"]) != (region, team):
            teams.append({"region": region, "team": team, "pokemons": []})
        teams[-1]["pokemons"].append({
            "pokemon": name,
            **sprites.fields(name),
            "types": [t for t in (_clean(row[c]) for c in c_types) if t],
            "moves": [m for m in (_clean(row[c]) for c in c_moves) if m],
            "generation": _clean(row[c_gen]),
            "star": RATING_STARS.get((_clean(row[c_rating]) or "").upper()),
        })
    return teams


def read_moves(wb):
    ws = wb["Moves"]
    catalog = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        name = _clean(row[0])
        if name:
            catalog.append({"move": name, "type": _clean(row[1]), "split": _clean(row[2])})
    return catalog


def read_picks(wb, sheet):
    """Type / Gen sheets: column A = type or generation, B = Ace, C.. = team."""
    picks = []
    for row in wb[sheet].iter_rows(min_row=2, values_only=True):
        key = _clean(row[0])
        if key:
            picks.append((key, _clean(row[1]), [m for m in (_clean(v) for v in row[2:]) if m]))
    return picks


# ===========================================================================
# Derived data
# ===========================================================================

def add_stab(teams, catalog):
    """A move is STAB when its type (from the Moves sheet) is one of the Pokemon's types."""
    move_type = {m["move"].lower(): m["type"] for m in catalog}
    missing = set()
    for t in teams:
        for p in t["pokemons"]:
            out = []
            for m in p["moves"]:
                mt = move_type.get(m.lower())
                if mt is None:
                    missing.add(m)
                out.append({"name": m, "stab": mt in p["types"]})
            p["moves"] = out
    if missing:
        print("      Moves missing from the Moves sheet (no type/split/STAB): " + ", ".join(sorted(missing)))


def usage_rows(picks, label_key, mons, sprites, key_of):
    """Mons Count (unique Pokemon) / Used Count (times used) per type or generation,
    plus the Ace and team picked on the Type / Gen sheet. Values used on the Teams
    sheet but missing from the pick sheet still get a row (with no Ace/team)."""
    used, unique = Counter(), defaultdict(set)
    for p in mons:
        for k in key_of(p):
            used[k] += 1
            unique[k].add(p["pokemon"])
    ref = lambda n: {"name": n, **sprites.fields(n)} if n else None
    rows, seen = [], set()
    for key, ace, team in picks:
        seen.add(key)
        rows.append({label_key: key, "mons_count": len(unique[key]), "used_count": used[key],
                     "ace": ref(ace), "team": [ref(m) for m in team]})
    for key in used:
        if key not in seen:
            rows.append({label_key: key, "mons_count": len(unique[key]), "used_count": used[key],
                         "ace": None, "team": []})
    return rows


def gen_type_matrix(mons, sprites):
    """Grid tab: for every type x generation, every Pokemon used with that type
    (either slot) and generation. Ordered MVP ratings first, then times used,
    then first appearance - the first one is what a cell shows before shuffling."""
    mvp, used, first = Counter(), Counter(), {}
    for i, p in enumerate(mons):
        n = p["pokemon"]
        used[n] += 1
        mvp[n] += p["star"] == "mvp"
        first.setdefault(n, i)
    pools = defaultdict(list)
    for p in mons:
        for t in p["types"]:
            k = f"{t}|{p['generation']}"
            if p["pokemon"] not in pools[k]:
                pools[k].append(p["pokemon"])
    out = {}
    for k, names in pools.items():
        names.sort(key=lambda n: (-mvp[n], -used[n], first[n]))
        out[k] = [{"name": n, **sprites.fields(n)} for n in names]
    gens = sorted({p["generation"] for p in mons if p["generation"]},
                  key=lambda g: (not g.isdigit(), int(g) if g.isdigit() else 0, g))
    types = sorted({t for p in mons for t in p["types"]})
    return {"generations": gens, "types": types, "pools": out}


def moves_data(catalog, mons):
    count = Counter(m["name"].lower() for p in mons for m in p["moves"])
    moves = [{**m, "count": count.get(m["move"].lower(), 0)} for m in catalog]
    types = sorted({m["type"] for m in catalog if m["type"]})
    splits = sorted({m["split"] for m in catalog if m["split"]})

    def pivot(value):
        acc = Counter()
        for m in moves:
            if m["type"] and m["split"]:
                acc[(m["type"], m["split"])] += value(m)
        rows = []
        for t in types:
            row = {"type": t, **{s: acc[(t, s)] for s in splits}}
            row["total"] = sum(row[s] for s in splits)
            rows.append(row)
        return {"splits": splits, "rows": rows}

    return moves, {"sumOfCount": pivot(lambda m: m["count"]),
                   "countOfMoves": pivot(lambda m: 1)}


def build_data():
    wb = openpyxl.load_workbook(SOURCE_FILE, read_only=True, data_only=True)
    sprites = SpriteResolver()
    teams = read_teams(wb, sprites)
    catalog = read_moves(wb)
    add_stab(teams, catalog)
    mons = [p for t in teams for p in t["pokemons"]]
    moves, pivots = moves_data(catalog, mons)
    data = {
        "teams": teams,
        "summary": {
            "pokemons_used": len({p["pokemon"] for p in mons}),
            "teams_used": len(teams),
            "games_played": len({GAME_SUFFIX.sub("", t["team"] or "") for t in teams}),
        },
        "typeUsage": usage_rows(read_picks(wb, "Type"), "type", mons, sprites, lambda p: p["types"]),
        "genUsage": usage_rows(read_picks(wb, "Gen"), "generation", mons, sprites,
                               lambda p: [p["generation"]] if p["generation"] else []),
        "genTypeMatrix": gen_type_matrix(mons, sprites),
        "moves": moves,
        "movesPivots": pivots,
    }
    wb.close()
    print(f"[1/2] Parsed {len(teams)} teams, {len(mons)} Pokemon rows, "
          f"{len(data['typeUsage'])} types, {len(data['genUsage'])} gens, {len(moves)} moves")
    if sprites.unmatched:
        print("      No sprite match for (add to NAME_OVERRIDES): " + ", ".join(sorted(sprites.unmatched)))
    return data


def build_html(data):
    if not TEMPLATE_FILE.exists():
        raise SystemExit(f"{TEMPLATE_FILE.name} not found next to this script.")
    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    # "</" is escaped so a name can never close the page's <script> tag early
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    HTML_OUTPUT_FILE.write_text(template.replace("__DATA_JSON__", payload), encoding="utf-8")
    print(f"[2/2] Wrote {HTML_OUTPUT_FILE.name} - open this in your browser")


def main():
    build_html(build_data())


if __name__ == "__main__":
    main()