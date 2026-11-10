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

The two `pokeapi_*.csv` files don't need to be in the repo. To stop git listing
them, add a `.gitignore` file containing `pokeapi_*.csv`. Delete them to
refresh the list after a new game adds Pokémon.

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

**Header buttons**
- Sprite style: Pixel Art (default), Idle Animation, Official Static, Soft Static.
- Card view: Watermark, Split Banner, Spotlight Ring.
- Phone / desktop view switch. The page opens in phone view.

**Searching and filtering**
- Teams and Mons search by Pokémon, team, region, generation (`gen 3`), type
  or move. Several words narrow it down, e.g. `kanto fire`.
- On phone, filters open in a sheet from the bottom. On desktop, they open
  from the Filters button, and active filters show as chips you can click to
  remove.
- Clicking a bar, row or tile in a Moves chart filters to it; clicking it
  again clears the filter.

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

## Troubleshooting

| Message or problem | What to do |
|---|---|
| `No module named openpyxl` | Run `pip install openpyxl` |
| `'Teams' sheet has no '…' column` | Check the header names in row 1 of the Teams sheet |
| `Moves missing from the Moves sheet` | Add those moves to the Moves sheet |
| `No sprite match for` | Add the name to `NAME_OVERRIDES` (see Sprites) |
| `nothing added to commit` | Nothing changed since the last push, so there's nothing to publish |
| `LF will be replaced by CRLF` | A harmless Windows line-ending note, safe to ignore |
| On Mac, `python` or `pip` not found | Use `python3` and `pip3` |