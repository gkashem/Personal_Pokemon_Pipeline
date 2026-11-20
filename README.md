# Personal_Pokemon_Pipeline

A personal dashboard of every Pokémon team I've built: who I used, how often,
which types, generations and moves, and how my teams overlap.

**Live dashboard:** https://gkashem.github.io/Personal_Pokemon_Pipeline/pokemon_ui.html

---

## Update the dashboard

1. Edit `Pokemon.xlsx`.
2. In the project folder, run:

   ```bash
   python pokemon_pipeline.py
   git add pokemon_ui.html pokemon_pipeline.py pokemon_ui_template.html README.md
   git commit -m "Update made"
   git push
   ```

   The first line rebuilds the dashboard from the spreadsheet. The git lines
   publish it; the live page updates a minute or two after the push.

First time only: `pip install openpyxl`

---

## How it works

```
Pokemon.xlsx  ──►  pokemon_pipeline.py  ──►  pokemon_ui.html
                         ▲
          pokemon_ui_template.html
```

The script reads the spreadsheet, works out every count and ranking, and puts
the result into the template to make `pokemon_ui.html`. It never changes the
spreadsheet.

| File | What it is | Edit it? |
|---|---|---|
| `Pokemon.xlsx` | My teams, preferences and moves | Yes, this is the data |
| `pokemon_pipeline.py` | Reads the spreadsheet and builds the page | Only to change how the data is worked out |
| `pokemon_ui_template.html` | The page's layout, styles and behaviour | Only to change how the page looks or works |
| `pokemon_ui.html` | The finished dashboard | No, it's rebuilt on every run |
| `pokeapi_pokemon.csv`, `pokeapi_pokemon_species.csv` | PokeAPI's list of Pokémon, used to find sprites | No, downloaded once and kept |
| `pmd_sprites.json` | Which Pokémon have Mystery Dungeon sprites (Scene tab) | No, downloaded once and kept |

The downloaded files don't need to be in the repo. To stop git listing them,
add a `.gitignore` file containing:

```
pokeapi_*.csv
pmd_sprites.json
```

Delete them to download fresh copies on the next run: the `pokeapi_*.csv`
files after a new game adds Pokémon, `pmd_sprites.json` to pick up new
Mystery Dungeon sprites.

---

## The spreadsheet

Row 1 of each sheet holds the headers.

### Teams: one row per Pokémon

| Region | Team | Pokemon | Type | Type | Move ×4 | Generation | Rating |
|---|---|---|---|---|---|---|---|

- Put the **latest team first**. The dashboard's default order follows the
  sheet.
- A team is a run of rows with the same Region and Team.
- Rating is `MVP`, `HM` (honourable mention) or blank.
- Columns are found by their header name, so their order doesn't matter.
- `Violet (2)` counts as the same game as `Violet` for Games Played.

### Preference: my favourite order for each type and generation

| Specialise | Ace | 2 | 3 | … | 10 |
|---|---|---|---|---|---|

- One row per type (`Bug`, `Dark`, …) and per generation (`Gen1`, `Gen2`, …).
- The first 6 names (Ace + 5) are the "Show from Preference" tables.
- The whole row breaks ties whenever Pokémon are level in a ranking.

### Moves: every move used on the Teams sheet

| Move | Type | Split |
|---|---|---|

Split is `Physical`, `Special` or `Status`. A move missing from this sheet is
listed when the script runs, and shows without a type colour on the page.

---

## Using the dashboard

The page opens in phone view. Switch to desktop view with the button at the
top right.

### Tabs

| Tab | What it shows |
|---|---|
| **Teams** | Every team and its Pokémon, with types, moves and ratings |
| **Types** | Per type: how many different Pokémon I used (Mons Count) and how many times (Used Count), plus an Ace + 5 table |
| **Generations** | The same as Types, per generation. The Generation filter also has **No Gen 1** |
| **Moves** | Moves by type and split, as a chart (Barbell, Back-to-Back or Tiled Bar) and a sortable table |
| **Mons** | Pokémon I used more than once, ranked |
| **Overlap** | How teams link through shared Pokémon, moves or types |
| **Grid** | Type × generation, showing the Pokémon I've used in each |
| **Scene** | A team of six roaming a pixel-art scene (see [Scene tab](#scene-tab)) |

### Header buttons

- **Sprite style:** Pixel Art (default), Idle Animation, Official Static, Soft
  Static.
- **Type badge:** how type badges look on the Types, Moves and Grid tabs.
  Teams and Mons draw their own type icons, so it doesn't change them.

  | Style | Looks like |
  |---|---|
  | Fade (default) | Type colour fading out behind the icon and name |
  | Soft Tint | Faint type-coloured fill with a coloured name |
  | Two-Part Tag | Solid icon block joined to a dark tinted name block |

- **Phone / desktop view.**

### Teams tab

**Card view:** pick one with the switch at the top left. Your pick is
remembered separately for phone and desktop view. Hover a button for the full
name.

| Button | View | Looks like |
|---|---|---|
| Card 1 | Trading Card | A trading card outlined in the two type colours, with a light body, the sprite in a window and the four moves |
| Card 2 | Trading Card Dark (desktop default) | The same card with a black body |
| Full | Full Art | A poster split between the two type colours, the name running up the side, and a glass panel with types and moves |
| Ring | Ring Card (phone default) | A black card with the sprite in a ring of both type colours and the four moves underneath |
| Flip | Flip Card | Big sprite on the front; tap (or press Enter) to turn it over and see the moves. It turns sideways on desktop and top-to-bottom on phone |
| Dex 1 | Pokédex | A Game Boy-style Pokédex with its shell split between the two type colours, and everything on the green screen |
| Dex 2 | Classic Pokédex | A black-and-white Gen 1 Pokédex entry |

- Ratings show as a crown (MVP) or medal (HM). Full Art also spells out MVP or
  HM on a corner ribbon.
- On desktop a team's six cards sit in a row; on phone they're a list.
- Card 1, Card 2 and Full tilt gently towards the mouse.

**Sort:**

| Option | Order |
|---|---|
| Chronological (Latest-Oldest) | The Teams sheet's order (default) |
| Chronological (Oldest-Latest) | The Teams sheet's order reversed |
| Alphabetical (A-Z) / (Z-A) | By team name |
| Region | Kanto, Johto, Hoenn, Sinnoh, Unova, Kalos, Alola, Galar, Paldea, then any other region A-Z |
| Rating (Most-Least) / (Least-Most) | By the team's total points (see [Rankings](#rankings)) |

Teams that tie stay in latest-first order.

### Mons tab

Pick a view with the switch at the top left. Leader board is the default, and
your pick is remembered separately for phone and desktop view.

| View | What it shows |
|---|---|
| Leader board | The top 6 as larger cards, then everyone else in a ranked list |
| Tier | A band per Used count (3×, 2×, …) of sprite tiles. Tap a tile to see its teams; tap it again to close |

Each team shows as its crown (MVP) or medal (HM), the team name and its
region. Filters count only matching uses: with Region set to Kanto, a
Pokémon's count, rank and teams are its Kanto uses, and one left with a single
use drops out.

### Search and filters

- Teams and Mons search by Pokémon, team, region, generation (`gen 3`), type
  or move. Several words narrow it down, e.g. `kanto fire`.
- On phone, filters open in a sheet from the bottom. On desktop, they open
  from the Filters button, and active filters show as chips you can click to
  remove.
- Clicking a bar, row or tile in a Moves chart filters to it; click it again
  to clear the filter.

### Rankings

**Points per use:** MVP = 3, HM = 1.5, no rating = 0.5.

| Where | Ranked by | Ties go to |
|---|---|---|
| Types / Generations tables, "Show from Data" (default) | Most points | Preference row, then more uses, then first on the Teams sheet |
| Types / Generations tables, "Show from Preference" | The first 6 names of the Preference row | — |
| Teams, Rating sort | The team's total points | Latest team first |
| Mons tab | Most uses, then most MVPs, then most HMs | Best Preference position on any of the Pokémon's rows, then first on the Teams sheet |
| Grid | Most points | The type's Preference row, then the generation's row, then more uses, then first appearance |

When a Types or Generations filter is on, the tables always rank from data.
On the Generations tab, the chart and table colours follow the Ace's two types.

### Motion

- **Header stats** count up from 0 when the page loads and when you switch
  between phone and desktop view.
- **Charts grow in**, row by row, when you open the Types, Generations, Moves
  or Overlap tab, switch phone / desktop view, change a chart's type, view or
  sort, or press Clear Filters.
- **Teams and Mons** open with a Poké Ball pop-in: each Pokémon bursts out of
  a ball that wobbles and opens, and on Mons "Used 3×" counts up. It plays
  when you open the tab, switch phone / desktop view or the Mons view, or
  change the sprite style. Only what's on screen animates.
- **Filter, sort and search changes** slide cards, rows and chips into their
  new places.
- **"Reduce motion"** in your device settings turns all motion off.
- Timings are in the `----- motion -----` block near the top of section 5 of
  the script in `pokemon_ui_template.html`. Motion uses
  [GSAP](https://gsap.com) and its Flip plugin, built into the template so it
  works offline.

### Type icons

Most come from the community set
[duiker101/pokemon-type-svg-icons](https://github.com/duiker101/pokemon-type-svg-icons);
Normal and Fighting were drawn for this dashboard in the Scarlet/Violet style.
All 18 are built into the template, so they work offline.

---

## Sprites

Sprites come from PokeAPI's sprite collection; Idle Animation comes from
Pokémon Showdown.

In Pixel Art, Pokémon without a Black/White animated sprite (Gen 6 onwards and
alternate forms) use their still front sprite, with a gentle bob and a small
hop every few seconds. The speeds are `--bob-time` (1.6s) and `--hop-time`
(4.2s) in the Sprite styles section of the template.

Names in the sheet are matched to PokeAPI automatically, for example:

| In the sheet | Matched to |
|---|---|
| `Urshifu-RapidStrike` | urshifu-rapid-strike |
| `Tauros-Paldea-Aqua` | tauros-paldea-aqua-breed |
| `Darmanitan-Galar` | darmanitan-galar-standard |
| `Mimikyu` | mimikyu-disguised |

If a name can't be matched, the script prints `No sprite match for: …`. Add
the name to `NAME_OVERRIDES` near the top of `pokemon_pipeline.py`:

```python
NAME_OVERRIDES = {"Name As In Sheet": "pokeapi-identifier"}
```

---

## Scene tab

Pick a team and a scene, and watch the team hang out there. The tab opens on a
random team and scene; changing one keeps the other.

**Teams to pick from**
- **Top 6:** the six highest-ranked Pokémon on the Mons tab
- **Teams:** every team on the Teams sheet
- **Types** and **Generations:** the Ace + 5 for each, from whichever list
  those tabs are showing

**Scenes**

| Scene | What's there |
|---|---|
| Meadow | Rolling hills, a round tree and wildflowers bending in the breeze |
| Forest | Layered pines, sunbeams, mushrooms, drifting leaves and a fallen log |
| Beach | Rolling waves, a palm tree, towel, bucket, shells and starfish |
| Sunset Hills | A big sun behind layered hills, a windmill, a fence line, birds flying home and swaying grass |
| Night Forest | Stars, a full moon, fireflies and a flickering campfire |
| Snowy Field | Falling snow, mountains, pines, a frozen pond and a snowman |
| Crystal Cave | Glowing crystals, a dripping pool and floating specks of light |
| Port | A wooden pier over clear tropical water, with islands, a sailboat, a leaping fish, gulls, a life ring and rope |

**How the Pokémon behave**
- Each picks its next move at random: walk, stand, nap (with floating z's) or
  another action its sprite has. Now and then two face each other. Tap a
  Pokémon to make it react.
- They walk around things (log, palm, pines, snowman, pond, campfire,
  crystals, pool, life ring, rope), never through them, and no more than two
  gather close together.
- At the Night Forest they often sit round the campfire.
- Naps last 5 to 9 seconds. The chance of a nap is set per scene (`sleep:` in
  the template's scenery list) and is never more than 15%. Nobody naps while
  swimming.
- **Flying types** sometimes fly across the sky to land somewhere else.
- **Water types** can wade into the sea at the Beach and swim from the pier at
  the Port. Pokémon that can't walk on land, like Gyarados, stay in the water
  (or the sky); they're listed in `SEA_ONLY` in the template's Scene section.

**How it's drawn**
- Everything is drawn in code on a small 400 × 180 canvas that's scaled up, so
  the scenery is pixel art and needs no image files.
- The scenery stays still; only its details move (clouds, grass, waves, snow,
  sparks and so on).
- Shading, outlines and ground texture are in the `----- pixel polish -----`
  block of the template's script; skies and clouds are in the
  `----- skies -----` block.
- The scene fits the screen, so the tab never scrolls. Very big sprites (over
  64 px tall, like Gyarados) are drawn at half size.
- It only moves while the tab is showing, and stays still with "reduce
  motion" on.

**Sprites:** Pokémon Mystery Dungeon style, from the community
[PMDCollab SpriteCollab](https://github.com/PMDCollab/SpriteCollab) project
(CC BY-NC 4.0: non-commercial use, with the credit shown under the scene). The
page loads them from SpriteCollab, so the Scene needs internet.

Pokémon without a Mystery Dungeon sprite use their Pixel Art sprite at half
size. The script lists them when it runs (`No Mystery Dungeon sprite: …`). To
pick one by hand, add its SpriteCollab folder to `PMD_OVERRIDES` near the top
of `pokemon_pipeline.py`:

```python
PMD_OVERRIDES = {"Name As In Sheet": "0025/0014"}
```

---

## Troubleshooting

| Message or problem | What to do |
|---|---|
| `No module named openpyxl` | Run `pip install openpyxl` |
| `'Teams' sheet has no '…' column` | Check the header names in row 1 of the Teams sheet |
| `Moves missing from the Moves sheet` | Add those moves to the Moves sheet |
| `No sprite match for` | Add the name to `NAME_OVERRIDES` (see [Sprites](#sprites)) |
| `No Mystery Dungeon sprite` | Nothing needed; the Scene uses Pixel Art for them |
| A Pokémon now has a Mystery Dungeon sprite but the Scene still uses Pixel Art | Delete `pmd_sprites.json` and run the script again |
| `nothing added to commit` | Nothing changed since the last push |
| `LF will be replaced by CRLF` | A harmless Windows line-ending note |
| On Mac, `python` or `pip` not found | Use `python3` and `pip3` |