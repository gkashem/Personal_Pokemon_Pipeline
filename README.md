# Personal_Pokemon_Pipeline

A personal dashboard of every Pokémon team I've built: who I used, how often,
which types, generations and moves, and how my teams overlap.

**Live dashboard:** https://gkashem.github.io/Personal_Pokemon_Pipeline/pokemon_ui.html

**How it works, step by step:** https://gkashem.github.io/Personal_Pokemon_Pipeline/dashboard_explainer.html
(an interactive guide that follows one spreadsheet row, Gengar, through the
script, the template and every tab; see [The explainer](#the-explainer))

---

## Update the dashboard

1. Edit `Pokemon.xlsx`.
2. In the project folder, run:

   ```bash
   python pokemon_pipeline.py
   git add pokemon_ui.html manifest.json sw.js icons pokemon_pipeline.py pokemon_ui_template.html README.md dashboard_explainer.html
   git commit -m "Update made"
   git push
   ```

   The first line rebuilds the dashboard from the spreadsheet. The git lines
   publish it; the live page updates a minute or two after the push.

First time only: `pip install openpyxl`

---

## Install it as an app

The dashboard can be installed on a phone as an app called **Poké Tracker**,
with a Poké Ball icon. It opens full screen and works without internet. It's
free: it's the same web page, installed from the browser.

- **iPhone:** open the live dashboard in Safari, tap Share, then **Add to Home
  Screen**.
- **Android:** open it in Chrome, tap the ⋮ menu, then **Install app** (or
  **Add to Home screen**).

**Offline:** the app keeps a copy of the page on the phone, and saves each
sprite the first time it's shown. Anything you've already seen works offline;
a sprite you haven't seen yet needs internet once. Up to 1,500 sprites are
kept (`SPRITE_CACHE_MAX` in `pokemon_pipeline.py`).

**Updates:** after you push a new version, the app shows it the next time you
open it with internet. There's nothing to tap.

The script writes the app files next to the page on every run:

| File | What it is |
|---|---|
| `manifest.json` | The app's name, icon and colours |
| `sw.js` | The service worker: saves the page and sprites so the app works offline |
| `icons/` | The Poké Ball icons. Drawn once; delete the folder to redraw them |

To change the app's name, colours or icon, edit `APP_SHORT_NAME`, `APP_NAME`,
`APP_BACKGROUND`, `APP_ACCENT` or `draw_icon()` near the end of
`pokemon_pipeline.py`. The service worker only runs from a web address, so
opening `pokemon_ui.html` straight from your computer works as before.

---

## How it works

```
Pokemon.xlsx  ──►  pokemon_pipeline.py  ──►  pokemon_ui.html
                         ▲                   manifest.json, sw.js, icons/
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
| `manifest.json`, `sw.js`, `icons/` | The app files (see [Install it as an app](#install-it-as-an-app)) | No, written by the script |
| `dashboard_explainer.html` | An interactive guide to how everything works (see [The explainer](#the-explainer)) | Only when the dashboard changes |
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

### The explainer

`dashboard_explainer.html` is a separate, interactive page that explains the
whole project in plain English. It follows one spreadsheet row (Gengar, MVP on
Yellow Legacy) from start to finish:

- **Part 1, the whole dashboard:** the files, an eight-step animation from the
  spreadsheet to the browser, how the files connect, the phone app, a tour of
  every tab, and how the order of Pokémon is set.
- **Part 2, the Python script:** each function in the order it runs, with its
  real code and what Gengar looks like at that point.
- **Part 3, the HTML template:** what HTML, CSS and JavaScript each do, a map
  of the template file, and step-through walks of the code for common actions.

It's a single file with no sprites, so it opens from your computer as well as
from the live link. The script doesn't touch it: its numbers (counts and line
numbers) are as of the date at the bottom of the page, so update it when the
dashboard changes in a big way.

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
- The first 6 names (Ace + 5) are the "Show from Preference" lineups.
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
| **Types** | Per type: how many different Pokémon I used (Mons) and how many times (Used), as a Lineup or a Chart (see below) |
| **Generations** | The same as Types, per generation. The Generation filter also has **No Gen 1** |
| **Moves** | Every move as a List (open a row to see who used it) or a Chart by type and split (see below) |
| **Mons** | Pokémon I used more than once, ranked |
| **Overlap** | How teams link through the Pokémon they share |
| **Grid** | Type × generation, showing the Pokémon I've used in each |
| **Scene** | A team of six roaming a pixel-art scene (see [Scene tab](#scene-tab)) |

### Header buttons

- **Sprite style:** Pixel Art (default), Idle Animation, Official Static.
- **Type badge:** how type badges look on the Types, Moves and Grid tabs.
  Teams and Mons draw their own type icons, so it doesn't change them.

  | Style | Looks like |
  |---|---|
  | Fade (default) | Type colour fading out behind the icon and name |
  | Soft Tint | Faint type-coloured fill with a coloured name |
  | Two-Part Tag | Solid icon block joined to a dark tinted name block |

- **Phone / desktop view.** In desktop view this button stays in the top-right
  corner, even on a narrow screen such as an upright phone, so you can always
  switch back.

### Teams tab

**Card view:** pick one with the switch at the top left. Your pick is
remembered separately for phone and desktop view. Hover a button for the full
name.

| Button | View | Looks like |
|---|---|---|
| Card 1 | Trading Card (default) | A trading card outlined in the two type colours, with a light body, the sprite in a window and the four moves |
| Card 2 | Trading Card Dark | The same card with a black body |
| Full | Full Art | A black poster with a glow in the two type colours behind the sprite, the name outlined up the side, and a glass panel with types and moves |
| Flip | Flip Card | Big sprite on a black front with a diagonal band in the two type colours; tap (or press Enter) to turn it over and see the moves. It turns sideways on desktop and top-to-bottom on phone |
| Dex 1 | Pokédex | A Game Boy-style Pokédex with its shell split between the two type colours, and everything on the green screen |
| Dex 2 | Classic Pokédex | A black-and-white Gen 1 Pokédex entry |

- Ratings show as a crown (MVP) or medal (HM). Full Art also spells out MVP or
  HM on a corner ribbon.
- On desktop a team's six cards sit in a row; on phone they're a list.
- Card 1, Card 2 and Full tilt gently towards the mouse.

**Dex 1 buttons:** the d-pad and A / B on a Dex 1 card press down and light an
LED (d-pad yellow, A green, B red). Tap, click or touch only; keyboard keys do
nothing.

| Button | Tap | Hold |
|---|---|---|
| A | The sprite hops | It squats lower the longer you hold (up to 1 second), then jumps higher when you let go |
| B | The sprite gives a little shake | It trembles harder and harder (up to 1 second), then shakes hard when you let go |
| ◀ ▶ (phone only) | Previous / next Pokémon on that team | — |
| ▲ ▼ (phone only) | Previous / next team | — |

On phone, Dex 1 shows one card per team at a time, with dots for which one.
◀ ▶ and ▲ ▼ wrap round at the ends. With search or filters on, ◀ ▶ step
through the matching Pokémon only, and every team goes back to its first
match when the filters change. On phone the buttons are also bigger, to be
easy to tap.

**Sort:**

| Option | Order |
|---|---|
| Chronological (Latest-Oldest) | The Teams sheet's order (default) |
| Chronological (Oldest-Latest) | The Teams sheet's order reversed |
| Alphabetical (A-Z) / (Z-A) | By team name |
| Region | Kanto, Johto, Hoenn, Sinnoh, Unova, Kalos, Alola, Galar, Paldea, then any other region A-Z |
| Rating (Most-Least) / (Least-Most) | By the team's total points (see [Rankings](#rankings)) |

Teams that tie stay in latest-first order.

### Types and Generations tabs

Pick a view with the switch at the top left. Lineup is the default, and your
pick is remembered separately for phone and desktop view.

| View | What it shows |
|---|---|
| Lineup | A card per type or generation: its Mons and Used counts, the Ace (large) and the next 5 Pokémon, with names |
| Chart | A barbell per type or generation: the hollow dot is Mons, the solid dot is Used, each labelled (e.g. "19 Mons", "26 Used", or "14 Mons = Used" when they match) |

- **Show from Preference / Show from Data** (Lineup only) switches the Ace + 5
  between my Preference sheet and what I actually used.
- On Generations, the card and chart colours follow the Ace's two types.
- The Type, Generation, Region and Rating filters recount everything from the
  matching uses.

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

### Moves tab

Pick a view with the switch at the top left. List is the default, and your
pick is remembered separately for phone and desktop view.

| View | What it shows |
|---|---|
| List | Every move with its type, split and Count Used. Click a column heading to sort (again to reverse); Count Used high-low is the default. Tap a row to open it and see which Pokémon used the move, and on how many teams (×2); tap it again to close it |
| Chart | A barbell per type and split. The dots are labelled "12 Moves" (different moves) and "45 Uses" (times used), or "3 Moves = Uses" when they match. In split view the dots are the split icons: hollow = Moves, filled = Uses. On phone, split view shows just the numbers |

- **Expand all / Collapse all** (List only) opens or closes every row shown.
- **Show Merged Totals / Show Split View** (Chart only) shows one barbell per
  type, or one per type and split.
- Search and the Type, Split and Moves Count filters narrow both views. Sort
  orders the chart.
- On phone, the Split column shows just the split icon so the table fits.

### Overlap tab

Each dot is a team, in Teams-sheet order. An arc joins two teams that used the
same Pokémon. Pick a team (dropdown, or tap its dot) to highlight its arcs and
list its shared Pokémon below.

### Search and filters

- Teams and Mons search by Pokémon, team, region, generation (`gen 3`), type
  or move. Several words narrow it down, e.g. `kanto fire`.
- On phone, filters open in a sheet from the bottom. On desktop, they open
  from the Filters button, and active filters show as chips you can click to
  remove.
- Tapping a Moves barbell opens the List, filtered to that barbell's type and
  split (just the type in merged view, or when you tap the Type badge). Search
  and Moves Count stay as they are, and the filters stay on if you go back to
  Chart; Clear Filters resets them.

### Rankings

**Points per use:** MVP = 3, HM = 1.5, no rating = 0.5.

| Where | Ranked by | Ties go to |
|---|---|---|
| Types / Generations Lineup, "Show from Data" (default) | Most points | Preference row, then more uses, then first on the Teams sheet |
| Types / Generations Lineup, "Show from Preference" | The first 6 names of the Preference row | — |
| Teams, Rating sort | The team's total points | Latest team first |
| Mons tab | Most uses, then most MVPs, then the best average Preference position across the Pokémon's type and generation rows, then most HMs | First on the Teams sheet |
| Grid | The same as the Mons tab: most uses, then most MVPs, then the best average Preference position, then most HMs | First on the Teams sheet |

When a Types or Generations filter is on, the Lineup always ranks from data.

**Average Preference position (Mons and Grid tabs):** the Pokémon's position on each of
its type rows and its generation row (1 = Ace), averaged. A row it isn't on
counts as 11th. Example: Venusaur is 1st on Grass, 2nd on Poison and 7th on
Gen1, so its average is 3.33; Gengar is 1st on Ghost, Poison and Gen1, so its
average is 1 and it ranks higher.

### Motion

- **Header stats** count up from 0 when the page loads and when you switch
  between phone and desktop view.
- **Charts grow in**, row by row, when you open a tab showing a chart
  (Types, Generations or Moves in Chart view, Overlap), switch to Chart,
  switch phone / desktop view, change a chart's type, view or sort, or press
  Clear Filters.
- **Teams and Mons** open with a Poké Ball pop-in: each Pokémon bursts out of
  a ball that wobbles and opens, and on Mons "Used 3×" counts up. It plays
  when you open the tab, switch phone / desktop view or the Mons view, or
  change the sprite style. Only what's on screen animates.
- **Filter, sort and search changes** slide cards (including the Lineup
  cards), rows and chips into their new places.
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

In the Full and Flip card views, Pixel Art sprites show at 1.5× their own size
(`--pixel-card-scale` in the template) and Idle Animation sprites at their own
size; both are shrunk to fit their box if needed.

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
| Beach | Rolling waves, a palm tree, towel, bucket, shells and starfish, plus a beach ball |
| Hills | A big sun behind layered hills, a windmill, a fence line, birds flying home and swaying grass |
| Camp | Stars, a full moon, fireflies and a flickering campfire in a night forest |
| Snow | Falling snow, mountains, pines, a frozen pond and a snowman, plus the little snowmen the Pokémon build |
| Cave | Glowing crystals, a dripping pool and floating specks of light |
| Port | A wooden pier over clear tropical water, with islands, a sailboat, gulls, a life ring and rope |
| Volcano | A night eruption: lava bombs from the crater and three vents, two lava pools and clusters of basalt columns |
| Rain | A woodland pond in the rain, with puddles and rain rings on the water |
| Arena | An indoor dojo with a raised tatami ring, a crowd in silhouette on two balconies, camera flashes and paper lanterns |
| Graveyard | A moonlit churchyard: a dirt path winds in through the gate past a weeping willow and an old well, between gravestones and lanterns |
| Peak | A summit above a sea of clouds, with broken columns round a steaming crater, an island dais, a dragon pillar and two blue braziers |
| Swamp | Murky bog water under a hazy sky, a boardwalk out to a hut on stilts, cattails and drifting mist |
| Shrine | A clearing at the roots of a giant roped tree, with a moss-roofed stone shrine, stone lanterns, a bell, and shafts of light |
| Quarry | A timber-framed mine tunnel in a grassy hillside, with a hanging lamp, a spoil heap, a loaded cart and three boulders |

**How the Pokémon behave**
- Each picks its next move at random: walk, stand, nap (with floating z's) or
  another action its sprite has. Now and then two face each other. Tap a
  Pokémon to make it react.
- They walk around things (log, palm, pines, snowman, pond, campfire,
  crystals, pool, life ring, rope, basalt columns, vents), never
  through them. They keep their distance from each other and mostly avoid
  walking through each other's paths.
- At the Camp they often sit round the campfire.
- **Footprints:** in the Snow and on the Beach sand, every Pokémon leaves a
  trail of prints that fades after about 12 seconds (none in the water or
  while flying). Ice types' prints in the snow glitter blue.
- In the Snow, every 15 to 20 seconds one Pokémon pushes a snowball across
  the field. It grows as it rolls and leaves a track, then becomes a small
  snowman where it stops. Two stand at most; when a third is built the
  oldest melts away.
- **Beach activity:** every 20 to 30 seconds two Pokémon on the sand bat a beach ball back and forth six times, each playing its
  attack animation, then one misses and the ball bounces away.
- **Cave activity:** every 12 to 18 seconds one Pokémon taps at a crystal
  cluster. Chips fly, the crystal flares, and a small glowing shard drops to
  the floor and glimmers for 20 seconds (six at most).
- **Fire types breathe fire in the Volcano:** every 8 to 12 seconds one
  breathes a long flamethrower across the ground, leaving scorch marks that
  cool and fade. Every 20 to 30 seconds two face off and breathe at each
  other; where the jets meet they flare into a burst of sparks, then both hop
  back.
- **Meadow:** every 20 to 30 seconds one Pokémon runs across pulling a kite
  that climbs on its string, hangs in the breeze, then drifts down. Grass
  types leave flowers in their footsteps that sprout, nod and wilt after
  about 10 seconds.
- **Forest:** every 15 to 25 seconds a Bug type spins a web beside one of
  the big trunks, spokes then spiral; it glistens for 20 seconds.
- **Hills:** every 12 to 18 seconds a Flying type beats its wings and a gust
  rolls across: the long grass bends flat, petals whirl up and the windmill
  spins fast for a few seconds.
- **Camp:** every 12 to 18 seconds one Pokémon fetches a stick from the edge
  of the woods and tosses it on the fire, which flares up with a fountain of
  sparks; a small woodpile builds up beside it.
- **Rain:** every 10 to 15 seconds one Pokémon takes a run-up and jumps into
  a puddle: a crown of droplets, a ripple and splash marks that soak away.
- These activities are run by each scene's `tick()`, using the
  `----- activity kit -----` block of the template's script. A Pokémon busy
  with one can't be tapped or pulled away.
- **Ice types** skate on the Snow's frozen pond (no one else goes on it):
  they speed up, then coast to a stop, leaving skate marks, and now and then
  spin on the spot.
- In the Arena, every few seconds two of them rush into the ring and spar:
  they take turns playing their attack animation while the other plays its
  hurt one, with a flash and dust on each blow. Then they step back out and
  the next pair goes in. Only the two fighting may stand in the ring; the
  rest wait at ringside, facing it. On each blow a scattered handful of the
  crowd throw their arms up and cameras flash. The bouts are run by the
  scene's `tick()` in the template's scenery list.
- Naps: the chance is set per scene (`sleep:` in the template's scenery list,
  never more than 15%). Snorlax naps at that chance for 5 to 9 seconds. Any
  other Pokémon naps at a quarter of it, for 2.5 to 4.5 seconds, and only
  while no other one (Snorlax aside) is asleep. Nobody naps while swimming.
- **Flying types** sometimes fly across the sky to land somewhere else.
- **Water types** can wade into the sea at the Beach and swim from the pier at
  the Port, and swim in the pond in the Rain. Pokémon that can't walk on land,
  like Gyarados, stay in the water at the Beach and Port (or the sky); they're
  listed in `SEA_ONLY` in the template's Scene section.
- **Fire types** can swim in the lava pools in the Volcano. **Ground and
  Rock types** can also stand on the cooled crust round each pool. **Ice
  types** keep well away from the pools. Everyone else keeps to open ground. The rules are in the `----- volcano kit -----`
  block of the template's script.
- **Type activities in the first eleven scenes** take turns: at most one runs
  in a scene at a time, and the scenes' own activities carry on as before. They
  are in the `type activities` block of the template's script (`TACT`).
  - **Meadow:** a Normal type spreads a picnic blanket and two friends sit
    round it; Bug types pollinate flowers so new ones bloom; a Fairy type
    dances a ring of toadstools into the grass.
  - **Forest:** a Grass type plants a sapling that grows into a small tree
    (two at most); a Fighting type kicks one of the big trunks, raining
    leaves and a berry; a Dark type hides in a trunk's shadow with only its
    eyes showing while the others search, then leaps out beside one of them.
  - **Beach:** a Normal type draws a heart, star or spiral in the sand; an
    Ice type carves an ice sculpture that melts away.
  - **Hills:** a Rock type stacks a cairn (three at most).
  - **Camp:** Bug types glow, with fireflies swirling round them.
  - **Cave:** an Electric type charges a crystal and bolts leap between them
    all, lighting up the cave; a Poison type stomps up clouds of glowing
    spores; a Dragon type carries shards to a hoard and naps on it.
  - **Port:** a Psychic type floats crates out of thin air into stacks.
  - **Rain:** Grass types hold a leaf over their heads and friends shelter
    under it; an Electric type calls down lightning; an Ice type freezes a
    puddle and slides across it (others spin on it); a Ground type rolls in a
    mud bath and comes out spotted.
  - **Arena:** a Fighting type chops through a stack of boards.
- **The newer scenes** (Graveyard, Peak, Swamp, Shrine, Quarry) are
  drawn in canvas pixels on a 400 × 180 plan. On a wider screen the plan's
  outer strips are mirrored out to the sides, and walking there works as at the
  mirrored spot. Their art and activities are in the `newer scenes` blocks of
  the template's script (`ART`, `ACT`, `planScene`).
- **Graveyard:** Ghost types hover, trailing blue wisps. Every few seconds one
  fades out, floats straight through the gravestones and fades back in
  somewhere else. A Dark type creeps up to a lantern: it goes out and darkness
  pools round it until only its red eyes show, then the lantern relights.
- **Peak:** a Dragon type climbs the bridge onto the island dais and roars.
  Shockwaves ring out, pebbles fall, the clouds below are pushed back and
  everyone else jumps.
- **Swamp:** Water types wade in the bog and Ghost types hover over it. A
  Ghost type drifts out over the water and pale marsh lights blink on round
  it while up to three others watch from the bank. A Poison type oozes a pool
  of purple sludge onto the bank. It bubbles and seeps away after 22 seconds,
  three at most, and everyone walks round it.
- **Shrine:** a Psychic type makes pebbles lift, circle it and settle
  in a ring. A Steel type swings into the bell: it rings in waves, petals
  drift down and everyone turns to look. A Fairy type twirls in sparkles:
  flowers bloom round it, the stone lanterns glow pink and a rainbow arcs
  over.
- **Quarry:** a Ground type digs down and a bulge races under the floor,
  leaving a ridge, until it bursts up somewhere else. A Rock type headbutts a
  boulder three times until it shatters (it's back 10 seconds later). A Steel
  type lays a mine-cart track one length at a time, then a cart of ore rolls
  along it and the track is cleared.

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
page loads them from SpriteCollab, so a team needs internet the first time it's
shown in the Scene; the installed app keeps them after that.

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
| The installed app still shows an old version | Open it once with internet, close it fully and open it again |