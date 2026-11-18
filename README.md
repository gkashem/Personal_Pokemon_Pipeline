# Personal_Pokemon_Pipeline

A personal dashboard of every Pokémon team I've built: who I used, how often,
which types, generations and moves, and how my teams overlap.

**Live dashboard:** https://gkashem.github.io/Personal_Pokemon_Pipeline/pokemon_ui.html

## Update the dashboard

After editing `Pokemon.xlsx`, run this in the project folder:

```markdown
https://gkashem.github.io/Personal_Pokemon_Pipeline/pokemon_ui.html

python pokemon_pipeline.py
git add pokemon_ui.html pokemon_pipeline.py pokemon_ui_template.html README.md
git commit -m "Update made"
git push
```

The first line rebuilds `pokemon_ui.html` from the spreadsheet; the git lines
publish it. The live page updates a minute or two after the push.

First time only: `pip install openpyxl`

## How it works

```
Pokemon.xlsx  ──►  pokemon_pipeline.py  ──►  pokemon_ui.html
                         ▲
          pokemon_ui_template.html
```

The script reads the spreadsheet, works out every count and ranking, and puts
the result into the template to make `pokemon_ui.html`. The spreadsheet is
only ever read, never changed.

| File | What it is | Edit it? |
|---|---|---|
| `Pokemon.xlsx` | My teams, preferences and moves | Yes, this is the data |
| `pokemon_pipeline.py` | Reads the spreadsheet and builds the page | Only to change how data is worked out |
| `pokemon_ui_template.html` | The page's layout, styles and behaviour | Only to change how the page looks or works |
| `pokemon_ui.html` | The finished dashboard | No, it's rebuilt every run |
| `pokeapi_pokemon.csv`, `pokeapi_pokemon_species.csv` | PokeAPI's list of Pokémon, used to find sprites | No, downloaded once and cached |
| `pmd_sprites.json` | Which Pokémon have Mystery Dungeon sprites (for the Scene tab) | No, downloaded once and cached |

These cached files don't need to be in the repo. To stop git listing them, add
a `.gitignore` file containing:

```
pokeapi_*.csv
pmd_sprites.json
```

Delete the `pokeapi_*.csv` files to refresh the list after a new game adds
Pokémon, and `pmd_sprites.json` to pick up Mystery Dungeon sprites added since
it was downloaded.

## The spreadsheet

Row 1 of each sheet is the headers.

**Teams**: one row per Pokémon.

| Region | Team | Pokemon | Type | Type | Move ×4 | Generation | Rating |
|---|---|---|---|---|---|---|---|

- A team is a run of rows with the same Region and Team.
- Rating is `MVP`, `HM` (honourable mention) or blank.
- Columns are found by their header name, so their order doesn't matter.
- A team name like `Violet (2)` counts as the same game as `Violet` for
  Games Played.

**Preference**: my preferred order of Pokémon for each type and generation.

| Specialise | Ace | 2 | 3 | … | 10 |
|---|---|---|---|---|---|

- One row per type (`Bug`, `Dark`, …) and per generation (`Gen1`, `Gen2`, …).
- The first 6 names (Ace + 5) are the "Show from Preference" tables.
- The whole row is the tie-breaker whenever Pokémon are tied in a ranking.

**Moves**: every move used on the Teams sheet.

| Move | Type | Split |
|---|---|---|

Split is `Physical`, `Special` or `Status`. A move that's missing here is
listed when the script runs, and shows without a type colour on the page.

## The dashboard

| Tab | What it shows |
|---|---|
| **Teams** | Every team and its Pokémon, with moves, types and rating |
| **Types** | Per type: different Pokémon used (Mons Count) and total uses (Used Count), plus an Ace + 5 table |
| **Generations** | The same as Types, per generation; the Generation filter also has **No Gen 1**, which shows every generation except Gen 1 |
| **Moves** | Moves by type and split, as a chart (Barbell, Back-to-Back or Tiled Bar) and a sortable table |
| **Mons** | Pokémon used more than once, ranked, in three views (see below) |
| **Overlap** | How teams link through shared Pokémon, moves or types |
| **Grid** | Type × generation, showing the Pokémon I've used in each |
| **Scene** | A team of six roaming a pixel-art scene as Mystery Dungeon sprites (see below) |

**Header buttons**
- Sprite style: Pixel Art (default), Idle Animation, Official Static, Soft Static.
- Card view (Teams tab only):

  | View | Looks like |
  |---|---|
  | Trading Card | A trading card with an outline in the two type colours, a light body, the sprite in a window and the four moves; the crown / medal at the bottom right |
  | Trading Card Dark (desktop default) | The same card with a black body |
  | Full Art | A poster split between the two type colours, the name running up the side, and a glass panel with types and moves; MVP / HM corner ribbon |
  | Ring Card (phone default) | Black card, the sprite in a ring of both type colours, the crown / medal beside the Gen, and the four moves underneath |
  | Flip Card | Big sprite on the front; tap (or Enter) to turn it over and see the moves |
  | Pokédex | A Game Boy-style Pokédex with its shell split between the two type colours; the screen shows the name, the sprite in four shades of green, types, Gen with the crown / medal under it, and the four moves, with type icons and the crown / medal in dark green |
  | Classic Pokédex | A black-and-white Gen 1 Pokédex entry |

  Full Art is the only view that spells out MVP / HM; the others show just
  the crown (MVP) or medal (HM).

  On desktop the six cards of a team sit in a row; on phone they're a list,
  with most views turned sideways into a strip. Trading Card, Trading Card
  Dark and Full Art tilt gently towards the mouse (not on touch, and not with
  "reduce motion" on). Your pick is remembered separately for phone and
  desktop view.
- Type badge: changes how type badges look on the Types, Moves and Grid tabs
  (chart labels, tables and the Grid's type names). The other tabs have no
  type badges: Teams and Mons draw their own type icons:

  | Style | Looks like |
  |---|---|
  | Fade (default) | Type colour fading out behind the icon and name |
  | Soft Tint | Faint type-coloured fill with coloured name |
  | Two-Part Tag | Solid icon block joined to a dark tinted name block |

- Phone / desktop view switch. The page opens in phone view.

**Mons tab views**: pick one with the switch at the top left. Leader board
is the default; your pick is remembered separately for phone and desktop view.

| View | What it shows |
|---|---|
| Leader board | The top 6 as larger cards (3 × 2 on desktop, stacked on phone), then everyone else in a ranked list |
| Tier | A band per Used count (3×, 2×, …) filled with sprite tiles; tap a tile to open a panel under its row with its teams, and tap it again to close it (one open at a time) |
| Hall of Fame | A card each: rank, sprite on its two type colours, name, type icons, a small use-count pill, and every team it was on |

Every view shows each team as the team's crown (MVP) or medal (HM), nothing
if unrated, then the team name and its region. Filters work on the uses: with
Region set to Kanto, a Pokémon's count, rank and teams are its Kanto uses
only, and one left with a single use drops out.

**Type icons**: most come from the community set
[duiker101/pokemon-type-svg-icons](https://github.com/duiker101/pokemon-type-svg-icons).
Normal and Fighting are drawn for this dashboard in the Scarlet/Violet style.
All 18 are built into `pokemon_ui_template.html`, so they work offline.

**Searching and filtering**
- Teams and Mons search by Pokémon, team, region, generation (`gen 3`), type
  or move. Several words narrow it down, e.g. `kanto fire`.
- On phone, filters open in a sheet from the bottom. On desktop, they open
  from the Filters button, and active filters show as chips you can click to
  remove.
- Clicking a bar, row or tile in a Moves chart filters to it; clicking it
  again clears the filter.

**Motion**
- The header stats count up from 0 when the page loads and every time you
  switch between phone and desktop view.
- Charts grow in, row by row: barbell dots slide out along their lines,
  Back-to-Back bars grow out from the middle, Moves tiles pop in, and Overlap's arcs draw
  themselves between the teams. This plays every time you:
  - open the Types, Generations, Moves or Overlap tab
  - switch between phone and desktop view
  - switch the Moves chart type, or between merged and split view
  - switch Overlap's "Link by" (Pokémon, Moves, Types)
  - change a chart's sort (Types, Generations, Moves "Sort plots")
  - press Clear Filters on Types, Generations or Moves
- Teams and Mons open with a Poké Ball pop-in: each team block (on Mons, each
  section of the view) fades in, its cards pop in one by one with a small
  bounce, and each Pokémon bursts out of a Poké Ball that wobbles and opens.
  On Mons, "Used 3×" counts up too. This plays on page load, every time you
  open Teams or Mons, when you switch between phone and desktop view or the
  Mons view, and when you change the sprite style.
  Only what's on screen animates; cards further down are already there.
- Changing a filter, sort or search slides cards, team / Pokémon blocks,
  table rows and Ace / Team chips into their new places. Ones that drop out
  fade away and new ones fade in. Search waits for a short pause in typing.
- Sprite, card view and badge style changes redraw instantly, and so do
  charts when a single filter changes.
- All motion is off for anyone with "reduce motion" on in their device
  settings.
- Timings are in one place: the `----- motion -----` block near the top of
  section 5 of the script in `pokemon_ui_template.html` (`COUNT_TIME`,
  `GROW_TIME`, `GROW_WAVE`, `FLIP_TIME`, `SEARCH_PAUSE`, and `POP_TIME`,
  `POP_WAVE`, `POP_BLOCK` for the Poké Ball pop-in).
- It uses [GSAP](https://gsap.com) and its Flip plugin, bundled into the
  template so it works offline.

## How rankings work

**Points per use:** MVP = 3, HM = 1.5, no rating = 0.5.

| Where | Ranked by | Ties go to |
|---|---|---|
| Types / Generations tables ("Show from Data", the default) | Most points | Preference row, then more uses, then first on the Teams sheet |
| Types / Generations tables ("Show from Preference") | The first 6 names of the Preference row | — |
| Teams, Rating sort | The team's total points | Teams sheet order |
| Mons tab | Most uses, then most MVPs, then most HMs | Best Preference position on any of the Pokémon's rows, then first on the Teams sheet |
| Grid | Most points | Type's Preference row, then generation's row, then more uses, then first appearance |

When a Types or Generations filter is on, the tables always rank from data.
On the Generations tab, the chart and table colours follow the Ace's two types.

## Sprites

Sprites come from PokeAPI's sprite collection, and Idle Animation comes from
Pokémon Showdown.

In Pixel Art, Pokémon without a Black/White animated sprite (Gen 6 onwards and
alternate forms) use their still in-game front sprite instead. To keep them
lively, these get a gentle idle bob plus a mini hop every few seconds, each
starting at a random moment so a team doesn't move in step. It's turned off
for anyone with "reduce motion" on in their device settings. The speeds are
`--bob-time` (1.6s) and `--hop-time` (4.2s) in the Sprite styles section of
`pokemon_ui_template.html`.

Names in the sheet are matched to PokeAPI automatically, for example:

| In the sheet | Matched to |
|---|---|
| `Urshifu-RapidStrike` | urshifu-rapid-strike |
| `Tauros-Paldea-Aqua` | tauros-paldea-aqua-breed |
| `Darmanitan-Galar` | darmanitan-galar-standard |
| `Mimikyu` | mimikyu-disguised |

If a name can't be matched, the script prints `No sprite match for: …`. Fix it
by adding the name to `NAME_OVERRIDES` near the top of `pokemon_pipeline.py`:

```python
NAME_OVERRIDES = {"Name As In Sheet": "pokeapi-identifier"}
```

## Scene tab

Pick a team and a scene, and watch the team hang out there. The tab opens on a
random team and a random scene each time; changing one keeps the other.

**Team picker**
- **Top 6**: the six highest-ranked Pokémon on the Mons tab
- **Teams**: every team on the Teams sheet
- **Types** and **Generations**: the Ace + 5 for each, from whichever list
  those tabs are showing (Show from Data or Show from Preference)

**Scene picker**

| Scene | What's there |
|---|---|
| Meadow | Rolling hills, a round tree, wildflowers; grass and flowers bend in a light breeze |
| Forest | Layered pines, sunbeams, mushrooms, drifting leaves and a fallen log |
| Beach | Rolling waves, a glittering sea, a palm tree, towel, bucket, shells and starfish |
| Sunset Hills | A big sun behind layered hills, a windmill with turning sails, a fence line, birds flying home, long grass swaying |
| Night Forest | Stars, a full moon, fireflies and a flickering campfire with rising sparks |
| Snowy Field | Three layers of falling snow, mountains, pines, a frozen pond and a snowman |
| Crystal Cave | Glowing, pulsing crystals, a dripping pool and floating specks of light |
| Port | A wooden pier over clear tropical water: turquoise shallows with light rippling on the sandy bottom, islands and a drifting sailboat on the horizon, a leaping fish, gulls, a life ring and a coil of rope |

**How the Pokémon behave**
- Each picks its own next move at random: walk somewhere (facing the way it
  walks), stand idle, nap (with floating z's) or another action its sprite
  has. Now and then one walks up to another and they face each other. Tap a
  Pokémon to make it react.
- They only go where it makes sense: around the log, palm, pines, snowman,
  pond, campfire, crystals, pool, life ring and rope, never through them. Things they walk
  around are drawn in depth order, so a Pokémon in front of the campfire
  covers it and one behind it is hidden by it.
- No more than two Pokémon gather close together.
- At the Night Forest they often sit round the campfire facing it.
- Naps last 5 to 9 seconds. Each time a Pokémon picks its next move, the
  chance of a nap is set per scene (`sleep:` in the template's scenery list)
  and is never more than 15%. Nobody naps while swimming.
- **Flying types** (from the Teams sheet) sometimes fly across the sky to land
  somewhere else.
- **Water types** can wade into the sea on the Beach and swim out from the
  pier at the Port; everyone else stays on the sand or the pier. Pokémon with
  no legs to walk on land, like Gyarados, stay in the sea (or the sky); they're listed
  in `SEA_ONLY` in the Scene tab section of the template's script.

**How it's drawn**
- Everything is drawn in code on a small 400 × 180 canvas that's scaled up, so
  the scenery is pixel art, needs no image files and the sprites sit on the
  same pixel grid.
- The scenery stays still; only its own details move (clouds, grass, leaves,
  waves, snow, sparks and so on).
- Pixel polish: the steps between sky and ground colours are blended with a
  row of checker pixels; trees, the log, palm, pines, snowman, mountains,
  crystals and other landmarks have a lit and a shaded side and a soft 1 px
  outline; and the ground has a light pixel texture (grass clumps, leaf
  litter, sand ripples, snow sparkle, cave stones). It's all in the
  `----- pixel polish -----` block of the template's script.
- Skies blend smoothly from top to horizon in fine dithered steps, and the
  clouds are shaded pixel art (a few puffs, a lit top and a shadowed
  underside) that drift slowly: white over the Meadow, Forest and Beach,
  gold-lit peach at Sunset Hills, moonlit navy at the Night Forest and soft
  grey over the Snowy Field, with white clouds over the Port too. The
  Crystal Cave's ceiling fades into darkness.
  It's all in the `----- skies -----` block of the template's script.
- The scene is as big as fits on screen, so the tab never scrolls.
- Very big sprites (taller than 64 px, like Gyarados) are drawn at half size.

**Sprites**: Pokémon Mystery Dungeon style, from the community
[PMDCollab SpriteCollab](https://github.com/PMDCollab/SpriteCollab) project
(CC BY-NC 4.0: non-commercial use, with the credit shown under the scene). The
pipeline matches each Pokémon to its sprite, forms included, and the page loads
the sprites from SpriteCollab when you pick a team, so it needs internet.
New teams and Pokémon from the Excel show up after the next pipeline run.

Pokémon without a Mystery Dungeon sprite use their Pixel Art sprite at half
size: animated if it's a Black/White sprite, otherwise still with a hop. The
script lists them when it runs (`No Mystery Dungeon sprite: …`). To pick a
sprite by hand, add the Pokémon's SpriteCollab folder to `PMD_OVERRIDES` near
the top of `pokemon_pipeline.py`:

```python
PMD_OVERRIDES = {"Name As In Sheet": "0025/0014"}
```

The scene only moves while the tab is showing. With "reduce motion" on,
everything is still.

## Troubleshooting

| Message or problem | What to do |
|---|---|
| `No module named openpyxl` | Run `pip install openpyxl` |
| `'Teams' sheet has no '…' column` | Check the header names in row 1 of the Teams sheet |
| `Moves missing from the Moves sheet` | Add those moves to the Moves sheet |
| `No sprite match for` | Add the name to `NAME_OVERRIDES` (see Sprites) |
| `No Mystery Dungeon sprite` | Nothing needed; the Scene uses Pixel Art for them (see Scene tab) |
| A Pokémon got a Mystery Dungeon sprite but the Scene still uses Pixel Art | Delete `pmd_sprites.json` and run the pipeline again |
| `nothing added to commit` | Nothing changed since the last push, so there's nothing to publish |
| `LF will be replaced by CRLF` | A harmless Windows line-ending note, safe to ignore |
| On Mac, `python` or `pip` not found | Use `python3` and `pip3` |