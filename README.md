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
| **Generations** | The same as Types, per generation |
| **Moves** | Moves by type and split, as charts and a sortable table |
| **Mons** | Pokémon used more than once, with every team they were on |
| **Overlap** | How teams link through shared Pokémon, moves or types |
| **Grid** | Type × generation, showing the Pokémon I've used in each |
| **Scene** | A team of six roaming on a patch of grass as Mystery Dungeon sprites (see below) |

**Header buttons**
- Sprite style: Pixel Art (default), Idle Animation, Official Static, Soft Static.
- Card view: Watermark, Split Banner, Spotlight Ring.
- Type badge: changes how every type badge looks (cards, tables, chart labels,
  Grid, Overlap):

  | Style | Looks like |
  |---|---|
  | Outline (default) | Coloured border, icon and name |
  | Soft Tint | Faint type-coloured fill with coloured name |
  | Icon Disc & Name | Icon in a coloured circle, name in plain text |
  | Two-Part Tag | Solid icon block joined to a dark tinted name block |
  | Merged Dual Pill | A Pokémon's two types joined into one split pill (shown as two pills if there isn't room) |
  | Icons Only | Just the icon in a coloured circle; hover for the name |
  | Fade | Type colour fading out behind the icon and name |

- Phone / desktop view switch. The page opens in phone view.

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
- Charts grow in, row by row: barbell dots slide out along their lines, bars
  grow from their base, Moves tiles pop in, and Overlap's arcs draw
  themselves between the teams. This plays every time you:
  - open the Types, Generations, Moves or Overlap tab
  - switch between phone and desktop view
  - switch Bar / Barbell on Types or Generations
  - switch the Moves chart type, or between merged and split view
  - switch Overlap's "Link by" (Pokémon, Moves, Types)
  - change a chart's sort (Types, Generations, Moves "Sort plots")
  - press Clear Filters on Types, Generations or Moves
- Changing a filter, sort or search slides cards, team / Pokémon blocks,
  table rows and Ace / Team chips into their new places. Ones that drop out
  fade away and new ones fade in. Search waits for a short pause in typing.
- Sprite, card view and badge style changes redraw instantly, and so do
  charts when a single filter changes.
- All motion is off for anyone with "reduce motion" on in their device
  settings.
- Timings are in one place: the `----- motion -----` block near the top of
  section 5 of the script in `pokemon_ui_template.html` (`COUNT_TIME`,
  `GROW_TIME`, `GROW_WAVE`, `FLIP_TIME`, `SEARCH_PAUSE`).
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

Pick a team and watch it hang out on the grass. The picker has:

- **Top 6**: the six highest-ranked Pokémon on the Mons tab
- **Teams**: every team on the Teams sheet
- **Types** and **Generations**: the Ace + 5 for each, from whichever list
  those tabs are showing (Show from Data or Show from Preference)

The tab opens on a random team each time. Each Pokémon picks its own next
move at random: walk somewhere (facing the way it walks), stand idle, hop, nap
(with floating z's) or any other action its sprite has. Now and then one walks
up to another and they face each other. Tap a Pokémon to make it turn and
react. Ones further back are drawn smaller, and sizes come from the sprites,
so big Pokémon stay big.

The sprites are Pokémon Mystery Dungeon style, from the community
[PMDCollab SpriteCollab](https://github.com/PMDCollab/SpriteCollab) project
(CC BY-NC 4.0: non-commercial use, with the credit shown under the scene). The
pipeline matches each Pokémon to its sprite, forms included, and the page loads
the sprites from SpriteCollab when you pick a team, so it needs internet.
New teams and Pokémon from the Excel show up after the next pipeline run.

Pokémon without a Mystery Dungeon sprite use their Pixel Art sprite with a
hop. The script lists them when it runs (`No Mystery Dungeon sprite: …`). To
pick a sprite by hand, add the Pokémon's SpriteCollab folder to
`PMD_OVERRIDES` near the top of `pokemon_pipeline.py`:

```python
PMD_OVERRIDES = {"Name As In Sheet": "0025/0014"}
```

With "reduce motion" on, the Pokémon stand still.

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