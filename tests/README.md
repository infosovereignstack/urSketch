# urSketch verification

The native generators exercise game rules, state migration, hint rewards,
codec bounds, snapshot caches, and vector bandwidth:

```hoon
+ursketch!ursketch-rules
+ursketch!ursketch-hints
+ursketch!ursketch-wire
+ursketch!ursketch-bandwidth
```

`browser.py`, `hints-and-settings.py`, `classic-layout.py`,
`tools-and-recovery.py`, and `vector-stream.py` use two isolated ships
(~zod and ~nec) on HTTP ports 18080/18081 and Ames ports 31337/31338.
Each prompts for a hidden JSON object with `host` and `guest` login codes.
`lobby-and-multiplayer.py` uses four ships and its own hidden code prompt.
Never save real ship login codes or cookies in artifacts.

`comet.py` authenticates to the local comet through Lens, checks the served
page and favicon, exercises room creation, search and explicit leave,
and verifies the urSketch tile and Treaty image/version/route. It saves only
public metadata and screenshots in `artifacts/`.

JavaScript syntax: `node --check web/app.js` (also drawing.js/settings.js).
Build: `python3 scripts/build.py`. Python: `python3 -m compileall scripts tests`.

`NOTICE.md` records external artwork sources. Reference-sized Classic tests
retain the supplied drawer and guesser geometry while displaying urSketch.

## 0.6.0 results — October 31, 2026

Passed: all four native generators on the live comet; browser.py,
classic-layout.py, hints-and-settings.py, vector-stream.py on two clean
ships; comet.py before and after publication cutover; source/bundle/mounted
file naming audit; JavaScript/Python syntax and whitespace checks.

The 1,600-command vector test measured 4,463,815 bytes for repeated JSON
snapshots versus 85,583 bytes for deltas (98.08% reduction), with identical
canvas pixels. Full snapshots shrank from 217,765 to 82,698 bytes. These
measure payload bytes, not end-to-end network latency.

Fresh screenshots and public metadata are under artifacts/. No credentials
or real ship session cookies are saved.

## 0.7.0 intro verification

`intro.py` checks the actual ship routes and requires no saved credentials.
Default test URLs are HTTP 18080 and Lens 12322. Set URSKETCH_ORIGIN and
URSKETCH_LENS_URL to check another ship. It verifies authentication, every
asset's SHA-256 and byte length, MIME/cache headers, missing media 404,
actual video playback, frame-matched button targets including edge-on/fade
states, sound/mute/volume persistence, Instructions, reduced motion, mobile
fit, and navigation into the existing lobby.

Native binary import and intro checks passed on both isolated ships. Existing
browser.py multiplayer checks passed with both clients using the new direct
lobby route. The source/shipped video stream hash comparison confirms that
animation packets are identical. The selected wordmark and built-in imagegen
prompt are recorded in artifacts/intro-wordmark-prompt.md.

The final SVG wordmark was checked in the actual intro on the isolated ship.
The media suite verifies both its exact file hash and successful browser decode.

Passed on the live Zuse 408 comet: complete intro suite with final SVG logo,
exact media hashes, saved audio preferences on browser-history restoration,
and existing room/rejoin/tile/favicon/publication smoke checks for 0.7.0.

## 0.7.1 tile update

Visually checked the centred wordmark and exact #9fc1e0 blue in the 512×512
export. Live installed/published image equality and PNG decoding, Treaty
0.7.1, and the existing comet smoke checks passed October 31, 2026.

## 0.7.3 original PNG selection

Verified the canonical PNG SHA-256 equals the exact owner-selected file.
Visual checks confirmed the full original lettering in the intro and tile.
Live intro/media hashes and normal comet room/tile/publication checks passed.
The selection and rendering constraints are recorded in artifacts/logo-selection.json.

## 0.8.0 clean intro and theme settings

The intro suite runs an allowed-autoplay browser and a browser with an initial
audio denial. It holds the video request to prove music starts independently,
then checks first-gesture retry, disabled-song network suppression, quarter/off
settings shared with the game, history restoration, exact 80% scene dimensions,
decoded-video/background colour equality, no bottom controls, phone settings,
reduced motion, target tracking, and entry into the lobby. `URSKETCH_PREVIEW=1`
checks local generated HTML against the live backend before deployment.

Both the intro suite and normal comet smoke suite passed on the deployed
0.8.0 publisher desk after publication.

## 0.8.1 complete logo repair and seamless background

The intro suite checks the underlying canvas independently of the replacement
logo: all repaired pixels outside the antialiased circle edge must equal the
sampled sky or circle colour. It also decodes actual browser screenshots and
compares pixels inside/outside each scene corner across normal and fade frames.
This detects video compositor colour differences that the previous CSS-versus-
decoded-sample check missed. Geometry now expects .72 of the original size.

Live 0.8.1 verification passed after native Clay import and Treaty publication:
intro pixel/geometry/audio checks and the normal room/rejoin/tile/publication
smoke suite. JavaScript/Python syntax and whitespace checks passed.

## 0.8.2 replay regression

The intro suite now lets the footage play naturally through two loop boundaries
and measures the first pass plus two replays. A Web Audio analyser verifies an
actual nonzero audio signal in each pass, alongside synchronized playheads and
full logo brightness. Frame-callback timestamps deliberately continue beyond
the clip duration after each loop; playback must use local video time instead.
The measured replay evidence is saved in artifacts/intro-loops.json.

Live 0.8.2 intro verification passed, including three audible playback passes
with cumulative callback timestamps, plus the normal room/rejoin/tile/publication
checks. Syntax and whitespace checks passed.

## 0.9.0 username and browsing separation

The comet suite checks the separate username route before opening a channel,
exact welcome text, no password input, full @p default, failed connection retry,
custom-name persistence, read-only profile inspection and the normal room flow.
The panel and form match reference coordinates at 1280×720; laptop/phone cases
also assert that page and panel content fit without scrolling. Screenshots are
artifacts/connect-desktop.png and connect-mobile.png. Preview mode now uses the
authoritative build instead of duplicating its HTML/asset substitutions.

The intro suite follows Play now → username → Connect → room browser in normal
and reduced-motion cases and retains the multi-pass audible-loop regression.
Existing browser.py and classic-layout.py now choose names on the separate page.

Live 0.9.0 verification passed after native Clay import and Treaty publication:
username/reference geometry, laptop/phone fit, full-ship/custom profiles, retry,
profile inspection, room search/create/invites/rejoin, tile/publication, and the
full intro suite with three audible playback passes. Syntax and whitespace
checks passed.

## 0.10.0 reference room browser and known-host counts

comet.py checks guide/table reference bounds, logo/version placement, outer-page
fit on laptops/phones, Settings/Instructions, real scroll-rail actions and native
roster JSON on the installed ship. Two simulated remote subscription feeds test
live count changes, distinct-ID deduplication, subscription reuse and filter
independence. The fixture data stays in the test browser and sends no requests
to those ships. Full/empty cases and compact/direct invite compatibility remain
covered while entry controls are hidden. Prior two-/four-ship UI tests select
the retained parser mode programmatically rather than clicking hidden controls.

Screenshots: comet-lobby.png (actual host), room-browser-reference.png (temporary
room fixtures), room-browser-laptop.png and room-browser-mobile.png. The intro
suite uses the new lobby Settings button and retains three audible passes.

Browser previews also passed after applying Classic settings and after a
simulated back/forward-cache restoration. Restored /play pages reload to create
fresh native channels and lobby subscriptions, preserving saved profiles and
room recovery. The updated native agent compiled and is running on the comet.

Live 0.10.0 verification passed after native agent/assets import and Treaty
publication: authenticated native roster IDs, reference browser geometry,
known-host count fixtures, filters, scroll rails, both themes, history refresh,
profile/room/rejoin/invite flows, tile/publication and the full three-pass intro
audio regression. JavaScript/Python syntax and whitespace checks passed.

## 0.11.0 native Global Chat

`global-chat.py` uses isolated ~zod/~nec HTTP 18080/18081 and discovers their Lens
ports from 12322/12323. Their generated frontend points Global Chat at fake ~zod;
production configuration remains the publisher comet. It checks native delivery
both directions, trusted IDs, text escaping, history after refresh, profile
inspection, search independence, draft retention and native input/cooldown bounds.
It never posts to the production chat. The canonical logo response is supplied
from the repository during this fake-only test. Evidence is recorded in
artifacts/global-chat-verification.json and global-chat-fake-ships.png.

An active room on the state-4 backend was retained while loading state 5;
artifacts/global-chat-migration.json records room/profile/score preservation and
new-chat readiness. comet.py verifies the new Global Chat label, v prefix, top
search form, simplified results and live chat readiness without sending messages.

Live 0.11.0 verification passed after native import and Treaty publication:
v prefix, Global Chat readiness, top ship search, simplified room results,
profile/room/rejoin/invite flows, known-host counts and filters, publication,
and three audible intro passes. Live chat was read without posting test messages.
The isolated fake ships were shut down after native delivery/migration checks.
JavaScript/Python syntax and whitespace checks passed.

## Game audio and round timing (0.12.0)

`tests/game-sounds.py` uses isolated `~zod`/`~nec` on HTTP 18080/18081 and
Lens 12322/12323. It checks ship identities before retrieving login codes
in memory. Install the current desk and media on both fake ships, substituting
`~zod` as the Global Chat host in their generated assets only.

The test decodes all nine real MP3 files into Web Audio, exercises actual
cross-ship room events, and checks private close feedback, correct-guess
routing, hint acceptance, warning permissions and public chat, volume/mute,
theme-song independence, snapshot deduplication, and artist rotation. It
measures the native finish deadline and the 250 ms spacing of audio-clock
source starts (80 ticks). It also verifies that refreshing does not replay
historical cues. Results are in `artifacts/game-sounds-verification.json`.

The native `+ursketch!ursketch-rules` generator additionally checks transposed
letters and partial-word guesses, 120-second turns, a full 20-second finish
window even on a late solve, persistent solve order after a correct guesser
leaves, and saved-room migration. `+ursketch!ursketch-hints` and
`+ursketch!ursketch-wire` continue to cover hints, scores and compact vectors.

The audio cleanup report verifies identical decoded input/output sample
counts. Its reference subtraction retains the complete YourTurnToDraw clip;
the tail after reference overlap is unchanged before MP3 encoding.

`tests/audio-clock.py` also checks actual nonzero decoded PCM in an isolated
browser, background turn alerts, scheduling the whole remaining tick window
in advance, and cancellation of future source nodes on mute/leave. Its result
is `artifacts/audio-clock-verification.json`. Live comet smoke checks and the
full intro/media regression passed on 0.12.0 without posting to Global Chat.

## Classic / Blingee and ten-round games (0.13.0)

`themes-and-gameplay.py` exercises two native private ships with the built release
client (`URSKETCH_PREVIEW=1` serves that client directly while retaining native
room traffic). It verifies saved Default-to-Classic migration, hidden old-theme
selection, publisher-first rooms on the guest ship, create-room availability,
Classic menus, the current logo, PNG favicon, and Classic/Blingee canvas bounds
at 1280×720, 1366×768, 1024×600 and 960×560. Actual pointer strokes at all four
corners are replayed and sampled on the guest's canvas. It checks zoom reset
across themes, selected yellow / unselected white chats, identical row spacing,
black-pen reset on a later artist turn, saved Blingee after refresh, HTTP timeout
translation and an actual native hint-rejection explanation.

The sound suite checks NewRound before word choice and no second NewRound on
choosing a word. Ordinary wrong guesses remain public; near guesses are absent
from both ships' shared message arrays and only the guesser receives feedback.
The native rules generator verifies the tenth turn is the last, capacity at
9 versus 10 players, and existing timer/scoring/hint/departure rules.

The cross-host creation check also injects a failed Create request, verifies an
inline error is visible without switching the selected publisher, then retries
successfully and checks ownership on the guest's own ship. Live 0.13.0 smoke
checks and the full intro/media regression passed; no Global Chat test posts
were sent to the publisher. The tile favicon is an exact, content-addressed
local PNG rather than an inline copy in each HTML page.

### 0.14 immediate-round regression

`tests/round-flow.py` runs real native ~zod, ~nec and ~bud at HTTP ports
18080–18082 / Lens 12322–12324, previews the current built client, and routes
local media without posting to real Global Chat. It verifies assigned words,
private exact messages, artist banner dismissal, 20-second partial endings,
immediate all-solved endings, focus and normal tab-close membership cleanup.
`tests/audio-clock.py` also checks clock-divergence/replayed-slot prevention;
`URSKETCH_AUDIO_BASELINE=1` reproduces the previous-release defect.
Older gameplay scripts that expect choosing/reveal phases describe historical
releases; round-flow is the current lifecycle integration regression.

0.14.0 verification passed on three isolated native ships: a partial solve
advanced after 20.13 seconds with 80 ticks; all-solved advanced immediately;
private word/reward/artist prompts, banner, focus and tab-close leave passed.
The prior audio scheduler reproduced an exhausted-window replay (16 ticks
from an eight-tick window); the fixed implementation schedules each slot once.
The installed comet reports 0.14.0 with its Treaty publication and passes the
updated browser/room lifecycle suite.
Installed intro/media verification also passed, including the repaired blue
circle at exclamation/lightbulb frames and three audible loop passes. Native
hints, vector codec and bandwidth generators passed on the comet.

### 0.14.1 full drawing panel

The comet browser suite checks exact Name-page text, Name label and laptop/phone
fit. A browser-only artist fixture intercepts draw writes and sends no fixture
commands to the live room. Real pointer strokes at the top and bottom must
produce vector coordinates and painted pixels near both edges at 1280×720,
1024×600 and 960×560, across Classic/Blingee switches. The native waiting-room
state is restored afterwards. Evidence: `artifacts/canvas-full-panel.png`.

0.14.1 preview and installed-comet suites passed, including real top/bottom
pointer strokes, edge pixels, theme switching, laptop sizes, exact Name copy,
phone fit and published Treaty version. JavaScript/Python syntax and whitespace
checks passed.

### 0.15.0 finale

`tests/finale.py` plays ten native rounds on isolated ~zod/~nec, checks final
scoring, exact bold red Game text, blank timer, black particle canvas, audible
fireworks PCM and mute. It waits the full 40 seconds, rejects early restart,
refreshes the winner during the celebration to verify the saved outcome and
remaining deadline, retains the final drawing and starts a fresh game.
Artifacts: `game-finale.png` and `finale-verification.json`. Native rules also
check tied winners, the 40-second deadline and state-7 private-log migration.

0.15.0 passed ten native rounds on two ships; the measured celebration lasted
40.029 seconds. Final scoring, fireworks PCM/mute, saved winners and
deadlines through refresh, exact bold red Game text, restart lockout, restored
final drawing and fresh-game reset passed. Preview checks also passed tied
winner art, moving particles, laptop resizing and reduced motion. Countdown
audio and native hints/vector/state migration regressions passed.

Installed-comet verification passed after the atomic 0.15.0 import and Treaty
publication: native rules/migration, tied-winner art, animated particles,
reduced motion, laptop canvas edges and the existing name/browser/room flows.
The historical countdown baseline is pinned to tag ursketch-v0.13.0.
