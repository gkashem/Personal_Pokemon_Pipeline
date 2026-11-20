"""
pokemon_pipeline.py

Reads Pokemon.xlsx and rebuilds pokemon_ui.html by injecting the parsed data
into pokemon_ui_template.html. The workbook is only ever read, never written.

Keep these files in the same folder:
  Pokemon.xlsx              <- your spreadsheet (edit this)
  pokemon_ui_template.html  <- page skeleton (don't edit unless changing layout)
  pokemon_pipeline.py       <- this script
  pokemon_ui.html           <- generated, open this in a browser
  manifest.json, sw.js, icons/  <- generated, make the page installable as
                               an app ("Poke Tracker") that works offline

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
  Preference : Specialise | Ace | 2 | 3 | ... | 10
          One row per type ("Bug", "Dark", ...) and per generation ("Gen1",
          "Gen2", ...), listing that row's Pokemon in order of preference.
          The first 6 (Ace + 5) are the "Show from Preference" tables on the
          Types / Generations tabs; the whole row is the tie-breaker wherever
          the dashboard ranks tied Pokemon.
  Moves : Move | Type | Split   (every move used on the Teams sheet)

Columns on the Teams sheet are found by their header text, so they can be
reordered. Every count on the dashboard (Mons/Used Count, move usage, the
Moves pivots, the header stats, the Grid pools, STAB) is worked out here
from the raw rows - the workbook holds no formulas for them.

SPRITES
-------
Every sprite style comes from PokeAPI's sprite repository by Pokedex id,
except Idle Animation, which comes from Pokemon Showdown by name. Names are
matched to PokeAPI's Pokemon list (pokeapi_pokemon.csv and
pokeapi_pokemon_species.csv, downloaded once and cached next to this script -
delete them to refresh after a new game adds Pokemon). The sheet's spelling
is converted automatically:
  "Urshifu-RapidStrike" -> urshifu-rapid-strike   (capital letters split words)
  "Tauros-Paldea-Aqua"  -> tauros-paldea-aqua-breed (unique longer match)
  "Darmanitan-Galar"    -> darmanitan-galar-standard (first of several forms)
  "Mimikyu"             -> mimikyu-disguised        (species' default form)
Anything that still doesn't match is listed when the script runs; add it to
NAME_OVERRIDES as {"Name As In Sheet": "pokeapi-identifier"}.

The Scene tab uses Pokemon Mystery Dungeon sprites from the community
PMDCollab SpriteCollab project (CC BY-NC 4.0: non-commercial, with credit).
Each Pokemon is matched to its sprite folder there by Pokedex number and form,
using a slim copy of SpriteCollab's index (pmd_sprites.json, downloaded once
and cached next to this script - delete it to pick up sprites added since).
The page then loads the sprites from SpriteCollab itself. Pokemon without
one are listed when the script runs and use their Pixel Art sprite in the
Scene; to pick a folder by hand, add it to PMD_OVERRIDES.
"""

import csv
import hashlib
import io
import json
import math
import re
import struct
import urllib.request
import zlib
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
SOURCE_FILE = HERE / "Pokemon.xlsx"
TEMPLATE_FILE = HERE / "pokemon_ui_template.html"
HTML_OUTPUT_FILE = HERE / "pokemon_ui.html"
MANIFEST_FILE = HERE / "manifest.json"
SERVICE_WORKER_FILE = HERE / "sw.js"
ICON_DIR = HERE / "icons"

RATING_STARS = {"MVP": "mvp", "HM": "hm"}
# points per use when ranking (the Grid; the dashboard uses the same values)
POINTS = {"mvp": 3, "hm": 1.5}   # any other (unrated) use scores 0.5

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
    "darmanitan-galar-standard": "darmanitan-galar",
}

PMD_INDEX = "https://raw.githubusercontent.com/PMDCollab/SpriteCollab/master/tracker.json"
PMD_INDEX_FILE = HERE / "pmd_sprites.json"
# {"Name As In Sheet": "dex/form folder"} to pick a Mystery Dungeon sprite by hand,
# e.g. {"Pikachu-Partner": "0025/0014"}; None means "use Pixel Art"
PMD_OVERRIDES = {}


def _cached_csv(name):
    path = HERE / f"pokeapi_{name}.csv"
    if not path.exists():
        with urllib.request.urlopen(POKEAPI_CSV.format(name), timeout=30) as r:
            path.write_bytes(r.read())
    return list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8"))))


def _pmd_key(name):
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def _pmd_index():
    """{"0094": {"sprite": True, "forms": {"alola": ["0001", True], ...}}, ...}:
    which Pokedex numbers and forms have a Mystery Dungeon sprite. Built from
    SpriteCollab's full index (about 10 MB) and cached in this slim form."""
    if not PMD_INDEX_FILE.exists():
        with urllib.request.urlopen(PMD_INDEX, timeout=60) as r:
            full = json.loads(r.read())
        has = lambda node: bool(node.get("sprite_files")) and node.get("sprite_complete", 0) > 0
        slim = {dex: {"sprite": has(node),
                      "forms": {_pmd_key(f["name"]): [key, has(f)]
                                for key, f in node.get("subgroups", {}).items() if f.get("name")}}
                for dex, node in full.items()}
        PMD_INDEX_FILE.write_text(json.dumps(slim, separators=(",", ":")), encoding="utf-8")
    return json.loads(PMD_INDEX_FILE.read_text(encoding="utf-8"))


class PmdSprites:
    """Finds each Pokemon's Mystery Dungeon sprite folder ("0094", "0038/0001")."""

    def __init__(self):
        try:
            self.index = _pmd_index()
        except Exception as e:  # offline and no cache: the Scene uses Pixel Art
            print(f"      Couldn't download the Mystery Dungeon sprite index ({e}); the Scene will use Pixel Art.")
            self.index = {}
        self.missing = set()

    def folder(self, name, row):
        if name in PMD_OVERRIDES:
            return PMD_OVERRIDES[name]
        dex = f"{row['species_id']:04d}" if row else None
        node = self.index.get(dex)
        found = None
        if node:
            form = _pmd_key(row["identifier"][len(row["species"]):]) if not row["is_default"] else ""
            # the form's own folder (exact name, else one name starting with the other) ...
            match = (node["forms"].get(form) if form else None) or next(
                (v for k, v in node["forms"].items() if form and k and (form.startswith(k) or k.startswith(form))), None)
            if match:
                found = f"{dex}/{match[0]}" if match[1] else None
            elif node["sprite"]:   # ... or the species' own when the form has no folder
                found = dex
        if not found and self.index:
            self.missing.add(name)
        return found


class SpriteResolver:
    """Works out every sprite URL for a Pokemon name from the Teams sheet."""

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
                "species_id": sid,
                "identifier": p["identifier"],
                "species": species_name.get(sid, p["identifier"]),
                "is_default": p["is_default"] == "1",
            }
        self.cache = {}
        self.unmatched = set()
        self.pmd = PmdSprites()

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
        if longer:  # unique longer form ("Tauros-Paldea-Aqua"), or the first of
            # several, which is the form's standard version
            # ("Darmanitan-Galar" -> darmanitan-galar-standard, not -zen)
            return min(longer, key=lambda r: r["id"])
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
                "spritePmd": self.pmd.folder(name, r),   # Scene tab; None = use Pixel Art
            }
        else:
            self.unmatched.add(name)
            guess = SHOWDOWN_ANIMATED.format(self.slug(name).replace("-", ""))
            f = {"sprite": guess, "spriteAnimated": guess, "spriteOfficial": None,
                 "spriteFront": None, "spritePixel": None, "spritePmd": self.pmd.folder(name, None)}
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
    c_region, c_team, c_mon, c_gen, c_rating = (
        _need(cols, h, "Teams")[0] for h in ("region", "team", "pokemon", "generation", "rating"))
    c_types = _need(cols, "type", "Teams")
    c_moves = _need(cols, "move", "Teams")

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
    catalog = []
    for row in wb["Moves"].iter_rows(min_row=2, values_only=True):
        name = _clean(row[0])
        if name:
            catalog.append({"move": name, "type": _clean(row[1]), "split": _clean(row[2])})
    return catalog


GEN_KEY = re.compile(r"^gen(?:eration)?\s*(\d+)$", re.I)


def read_preference(wb):
    """Preference sheet: column A = a type ("Bug") or a generation ("Gen1"),
    then that row's Pokemon in order (Ace first). Returns two dicts of full
    ordered lists: {type: [...]}, {generation number as text: [...]}."""
    types, gens = {}, {}
    for row in wb["Preference"].iter_rows(min_row=2, values_only=True):
        key = _clean(row[0])
        if not key:
            continue
        names = [m for m in (_clean(v) for v in row[1:]) if m]
        g = GEN_KEY.match(key)
        (gens if g else types)[g.group(1) if g else key] = names
    return types, gens


def picks_from(pref, top=6):
    """The "Show from Preference" rows: (key, Ace, next 5) from each Preference row."""
    return [(key, names[0] if names else None, names[1:top]) for key, names in pref.items()]


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
    plus the Ace and team from the Preference sheet. Values used on the Teams
    sheet but missing from the Preference sheet still get a row (with no Ace/team)."""
    used, unique = Counter(), defaultdict(set)
    for p in mons:
        for k in key_of(p):
            used[k] += 1
            unique[k].add(p["pokemon"])
    ref = lambda n: {"name": n, **sprites.fields(n)} if n else None
    picked = {key for key, _, _ in picks}
    picks = list(picks) + [(key, None, []) for key in used if key not in picked]
    return [{label_key: key, "mons_count": len(unique[key]), "used_count": used[key],
             "ace": ref(ace), "team": [ref(m) for m in team]}
            for key, ace, team in picks]


def gen_type_matrix(mons, sprites, pref_types, pref_gens):
    """Grid tab: for every type x generation, every Pokemon used with that type
    (either slot) and generation. Ordered by points (each use: MVP 3, HM 1.5,
    unrated 0.5); ties go to the type's Preference row, then the generation's
    row, then more uses, then first appearance. The first one is what a cell
    shows before shuffling."""
    points, used, first = Counter(), Counter(), {}
    for i, p in enumerate(mons):
        n = p["pokemon"]
        used[n] += 1
        points[n] += POINTS.get(p["star"], 0.5)
        first.setdefault(n, i)

    def rank(lst, n):
        return lst.index(n) if n in lst else len(lst) + 1000

    pools = defaultdict(list)
    for p in mons:
        for t in p["types"]:
            k = f"{t}|{p['generation']}"
            if p["pokemon"] not in pools[k]:
                pools[k].append(p["pokemon"])
    out = {}
    for k, names in pools.items():
        t, g = k.split("|", 1)
        names.sort(key=lambda n: (-points[n], rank(pref_types.get(t, []), n),
                                  rank(pref_gens.get(g, []), n), -used[n], first[n]))
        out[k] = [{"name": n, **sprites.fields(n)} for n in names]
    gens = sorted({p["generation"] for p in mons if p["generation"]},
                  key=lambda g: (not g.isdigit(), int(g) if g.isdigit() else 0, g))
    types = sorted({t for p in mons for t in p["types"]})
    return {"generations": gens, "types": types, "pools": out}


def moves_data(catalog, mons):
    """Every move with its times used, plus the Moves tab's pivots per type
    and split: Sum of Count (times used) and Count of Moves (distinct moves)."""
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
    pref_types, pref_gens = read_preference(wb)
    data = {
        "teams": teams,
        "summary": {
            "pokemons_used": len({p["pokemon"] for p in mons}),
            "teams_used": len(teams),
            "games_played": len({GAME_SUFFIX.sub("", t["team"] or "") for t in teams}),
        },
        "typeUsage": usage_rows(picks_from(pref_types), "type", mons, sprites, lambda p: p["types"]),
        "genUsage": usage_rows(picks_from(pref_gens), "generation", mons, sprites,
                               lambda p: [p["generation"]] if p["generation"] else []),
        "genTypeMatrix": gen_type_matrix(mons, sprites, pref_types, pref_gens),
        # full Preference rows (up to 10 each), the dashboard's tie-breaker
        "preference": {"types": pref_types, "gens": pref_gens},
        "moves": moves,
        "movesPivots": pivots,
    }
    wb.close()
    print(f"[1/2] Parsed {len(teams)} teams, {len(mons)} Pokemon rows, "
          f"{len(data['typeUsage'])} types, {len(data['genUsage'])} gens, {len(moves)} moves")
    if sprites.unmatched:
        print("      No sprite match for (add to NAME_OVERRIDES): " + ", ".join(sorted(sprites.unmatched)))
    if sprites.pmd.missing:
        print("      No Mystery Dungeon sprite (the Scene uses Pixel Art): " + ", ".join(sorted(sprites.pmd.missing)))
    return data


def build_html(data):
    if not TEMPLATE_FILE.exists():
        raise SystemExit(f"{TEMPLATE_FILE.name} not found next to this script.")
    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    # "</" is escaped so a name can never close the page's <script> tag early
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = template.replace("__DATA_JSON__", payload)
    HTML_OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"[2/2] Wrote {HTML_OUTPUT_FILE.name} - open this in your browser")
    build_app_files(html)


# ===========================================================================
# App files (Progressive Web App)
# ===========================================================================
# These let a phone install the dashboard from the browser ("Add to Home
# Screen") as an app called "Poke Tracker" that opens full screen and works
# without internet:
#   manifest.json  the app's name, icons and colours
#   sw.js          the service worker: keeps a copy of the page and of each
#                  sprite the first time it's seen, so the app opens offline
#   icons/         Poke Ball icons, drawn by draw_icon() below
# manifest.json and sw.js are rewritten on every run (only when their content
# changes); the icons are drawn once - delete icons/ to redraw them. sw.js
# carries a version taken from the finished page, so each new build replaces
# the old copy on the phone the next time the app is opened online, with no
# prompt.

APP_NAME = "My Pokémon Tracker"
APP_SHORT_NAME = "Poké Tracker"   # shown under the home-screen icon
APP_BACKGROUND = "#000000"        # the page's --bg
APP_ACCENT = (0xFF, 0xCB, 0x05)   # the page's --accent (yellow)
# (file, size in px, maskable): maskable icons keep the ball inside the middle
# 80% because Android may crop them to a circle or squircle
ICONS = [("icon-192.png", 192, False), ("icon-512.png", 512, False),
         ("icon-maskable-512.png", 512, True), ("apple-touch-icon.png", 180, False)]
# Sprites kept on the phone at most (oldest dropped first)
SPRITE_CACHE_MAX = 1500

SERVICE_WORKER = """// Poke Tracker service worker - written by pokemon_pipeline.py on every run;
// edit it there (SERVICE_WORKER), not here.
//  - The page and app files: fetched fresh whenever there's internet (so a
//    new build shows the next time the app opens), with the saved copy used
//    when offline or if the network takes longer than 4 seconds.
//  - Sprites: saved the first time they're shown, then loaded from the phone.
const VERSION = '__VERSION__';
const PAGE_CACHE = 'page-' + VERSION;
const SPRITE_CACHE = 'sprites-v1';
const SPRITE_MAX = __SPRITE_MAX__;
const SPRITE_HOSTS = ['raw.githubusercontent.com', 'play.pokemonshowdown.com'];
const APP_FILES = ['./pokemon_ui.html', './manifest.json',
  './icons/icon-192.png', './icons/icon-512.png', './icons/apple-touch-icon.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(PAGE_CACHE).then(c => c.addAll(APP_FILES.map(u => new Request(u, {cache: 'reload'}))))
    .then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('page-') && k !== PAGE_CACHE).map(k => caches.delete(k))))
    .then(trimSprites).then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if(req.method !== 'GET') return;
  const url = new URL(req.url);
  if(url.origin === location.origin) e.respondWith(networkFirst(req));
  else if(SPRITE_HOSTS.includes(url.hostname)) e.respondWith(spriteFirst(req));
});

async function networkFirst(req){
  const cache = await caches.open(PAGE_CACHE);
  const fresh = fetch(req, {cache: 'no-cache'}).then(res => {
    if(res.ok) cache.put(req, res.clone());
    return res;
  });
  const timeout = new Promise(res => setTimeout(res, 4000));
  try{
    const res = await Promise.race([fresh, timeout]);
    if(res) return res;
  }catch(err){ /* offline: use the saved copy */ }
  const saved = await cache.match(req, {ignoreSearch: true})
    || (req.mode === 'navigate' && await cache.match('./pokemon_ui.html'));
  return saved || fresh;
}

let puts = 0;
async function spriteFirst(req){
  const cache = await caches.open(SPRITE_CACHE);
  const saved = await cache.match(req.url);
  if(saved) return saved;
  try{
    // a CORS copy can be saved at its real size (and read by the page's canvas)
    const res = await fetch(req.url, {mode: 'cors', credentials: 'omit'});
    if(res.ok){
      await cache.put(req.url, res.clone());
      if(++puts % 50 === 0) trimSprites();
    }
    return res;
  }catch(err){
    return fetch(req);   // the host refused CORS: load it as normal, unsaved
  }
}

async function trimSprites(){
  const cache = await caches.open(SPRITE_CACHE);
  const keys = await cache.keys();
  await Promise.all(keys.slice(0, Math.max(0, keys.length - SPRITE_MAX)).map(k => cache.delete(k)));
}
"""


def _png(size, pixels):
    """RGB pixel rows -> PNG bytes (no image library needed)."""
    raw = b"".join(b"\x00" + bytes(row) for row in pixels)
    chunk = lambda tag, data: (struct.pack(">I", len(data)) + tag + data
                               + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def draw_icon(size, maskable=False):
    """A Poke Ball on the page's black: yellow top, light bottom, black band
    and a white centre button. Edges are smoothed by measuring how far each
    pixel is from each shape's edge."""
    bg = tuple(int(APP_BACKGROUND[i:i + 2], 16) for i in (1, 3, 5))
    top, bottom, band_c, white = APP_ACCENT, (0xEE, 0xF0, 0xF6), (0x10, 0x11, 0x16), (0xFF, 0xFF, 0xFF)
    c = size / 2
    R = size * (0.30 if maskable else 0.38)      # ball radius
    band = R * 0.09                               # half the band's height
    ring, button = R * 0.34, R * 0.21             # centre button: black ring, white middle
    cover = lambda d: min(1.0, max(0.0, 0.5 - d))  # signed distance -> pixel coverage
    mix = lambda a, b, t: tuple(round(a[k] + (b[k] - a[k]) * t) for k in range(3))
    rows = []
    for y in range(size):
        row = []
        py = y + 0.5 - c
        for x in range(size):
            px = x + 0.5 - c
            r = math.hypot(px, py)
            col = bg
            ball = cover(r - R)
            if ball > 0:
                half = mix(bottom, top, cover(py))           # top half where py < 0
                inside = mix(half, band_c, cover(abs(py) - band))
                inside = mix(inside, band_c, cover(r - ring))
                inside = mix(inside, white, cover(r - button))
                col = mix(bg, inside, ball)
            row.extend(col)
        rows.append(row)
    return _png(size, rows)


def _write_if_changed(path, data):
    data = data.encode("utf-8") if isinstance(data, str) else data
    if not path.exists() or path.read_bytes() != data:
        path.write_bytes(data)


def build_app_files(html):
    ICON_DIR.mkdir(exist_ok=True)
    for name, size, maskable in ICONS:
        path = ICON_DIR / name
        if not path.exists():          # drawn once; delete icons/ to redraw
            path.write_bytes(draw_icon(size, maskable))
    manifest = {
        "name": APP_NAME,
        "short_name": APP_SHORT_NAME,
        "description": "Every Pokémon team I've built: who I used, how often, and how my teams overlap.",
        "start_url": "./pokemon_ui.html",
        "scope": "./",
        "display": "standalone",
        "background_color": APP_BACKGROUND,
        "theme_color": APP_BACKGROUND,
        "icons": [{"src": f"icons/{name}", "sizes": f"{size}x{size}", "type": "image/png",
                   **({"purpose": "maskable"} if maskable else {})}
                  for name, size, maskable in ICONS if name != "apple-touch-icon.png"],
    }
    _write_if_changed(MANIFEST_FILE, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    version = hashlib.sha256(html.encode("utf-8")).hexdigest()[:12]
    _write_if_changed(SERVICE_WORKER_FILE, SERVICE_WORKER.replace("__VERSION__", version)
                      .replace("__SPRITE_MAX__", str(SPRITE_CACHE_MAX)))
    print(f"      Wrote the app files: {MANIFEST_FILE.name}, {SERVICE_WORKER_FILE.name}, {ICON_DIR.name}/")


def main():
    build_html(build_data())


if __name__ == "__main__":
    main()