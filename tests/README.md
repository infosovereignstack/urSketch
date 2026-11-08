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

### 0.16.0 continuous games, tools and removal

The two-ship finale suite now tests owner-only removal (including native
rejection for a non-owner), remaining out until an explicit join, contained
21×22 tool buttons, single selection with mouse/hotkeys, bucket-fill then pen
stroke commands, explicit Rejoin after refresh, empty canvas before fireworks,
and automatic score/canvas reset after the complete 40-second celebration.
Removing a player during an already-started game hides Start and the room
resumes automatically after a deliberate rejoin. Native rules check cleared
final drawings and both automatic restart and one-player waiting/resumption.

0.16.0 passed the complete two-ship suite: single selected/contained tool
buttons, fill-to-pen stroke behavior, owner-only removal and native permission
rejection, explicit refresh rejoin, cleared canvas before fireworks, the full
40-second deadline, automatic new game and paused-room resumption. Preview
checks passed the existing name/lobby/settings/canvas flows. Native rules,
hints and vector codecs passed, including migration of state-8 private logs.

Installed-comet verification passed after atomic 0.16.0 import and Treaty
publication. State-6/7/8 migrations, native round rules, full canvas, Name page,
settings, profile/room lifecycle, tile and published version all passed.

### 0.17.0 character builder

`tests/characters.py` uses private ~zod/~nec to decode and cycle every layer,
check body/face/hat order, draft restoration, distinct non-default character
persistence in a clean browser, catalog insertion and unknown future IDs.
It also checks manual discovery (zero lobby subscriptions on arrival), peer
avatar propagation, and screen fit at 1920×1080 through 320×568. The Connect
checks in comet.py now use the supplied builder composition and explicitly
search after history restoration. Character artwork is served from local
source assets in preview tests.

0.17.0 character checks passed with every supplied layer, a distinct non-default
character saved/restored from the ship in a clean browser, catalog insertion,
unknown future IDs, draft preservation, zero automatic room searches, peer
character propagation and laptop/phone fit. All 25 copied SVG files match the
original artwork byte for byte. The complete continuous-game regression also
passed with character payloads and manual discovery enabled.

Installed-comet verification passed after the atomic 0.17.0 import and Treaty
publication: all 25 native SVG responses have the expected MIME type and exact
source hash; the authenticated character endpoint returns valid data; builder
geometry, phone fit, native rules and existing room/game flows passed. Game-room
character placement remains pending the user's follow-up layout reference.

### 0.20.0 roster, pencil and supplied audio

The comet suite uses a ten-player browser fixture to verify proportional SVG
transforms, local-green/other-black names, red point totals, ten-row panel fit,
stable ordering and pencil movement at desktop/laptop/phone sizes. The native
two-ship finale test also checks stable rows and the marker after real round
rotation, plus continuous MP3 playback beyond its first loop, mute/resume and
rejoin offset. Audio-clock instrumentation now forwards all native start/stop
arguments so scheduled duration and offset behavior is tested faithfully.

0.20.0 preview checks passed ten-row fit, current font/colors, proportional
character transforms, stable roster and moving pencil at 2048×970, 1280×720
and phone size. The native ten-round two-ship suite passed continuous supplied
MP3 playback, mute/resume, refreshed-player offset, score/canvas reset and
automatic next game. Audio-clock tests passed decoded fireworks PCM/looping,
master mute and cancellation alongside the existing fixed-slot countdown.
The MP3 and pencil SVG match the supplied originals byte for byte.

Installed 0.20.0 checks passed after native import and Treaty publication:
proportional ten-player roster, moving pencil/stable order, current font and
name/point colors, native SVG favicon decode and exact pencil/MP3 response
hashes and MIME types, plus existing builder, room and canvas flows.

### 0.20.1 approved word bank

A source audit confirms 100 retained originals plus exactly the 400 reviewed
additions, with 500 unique entries. Native rules passed after installation.
A read-only browser check confirmed the served version and Treaty publication
are 0.20.1. Evidence: `artifacts/word-bank-verification.json`.

### 0.21.0 additional themes

`tests/new-themes.py` verifies all seven new choices, saved theme/audio prefs,
distinct palettes, ten-player proportions and name colors, selected chat
panels, Terminal monospace text, laptop/phone layout and actual pointer strokes
at both canvas edges. Seeded drawing pixels must remain identical after
resizing. Game fixtures stay in the browser and intercept writes; they never
join a real room. Set `URSKETCH_INSTALLED=1` to exercise the installed client
instead of the preview build. Screenshots include `artifacts/theme-gallery.png`;
results are recorded in `artifacts/new-themes-verification.json`.

All seven installed themes passed saved-selection/audio preferences, mid-drawing
Classic/theme switches with identical pixels, full canvas edge strokes,
proportional ten-player roster, chat selection, room-list contrast and
laptop/phone fit. The installed Classic/Blingee comet regression also passed,
including native create/leave, profile/character media, tile and Treaty 0.21.0.
JavaScript/Python syntax and whitespace checks passed.

### 0.22.0 Snoopy, Mountain Dew and M1A1 Abrams

The theme suite now exercises all ten additional themes, including the three
new choices, with saved selection, Classic/theme transitions, full canvas edge
strokes, drawing-pixel identity, room-list contrast, roster colors/proportions
and laptop/phone layouts. All art remains local and self-contained.

0.22.0 preview and installed checks passed across all ten themes. Snoopy and
Woodstock, Mountain Dew and M1A1 Abrams save and restore correctly; tank
controls use monospace text and citrus buttons retain readable dark labels.
The installed Classic/Blingee room/profile/canvas regression and Treaty 0.22.0
checks also passed. All six new SVG assets parse; syntax/whitespace checks pass.

### 0.23.0 settings, audio and resilience

`tests/stability.py` uses isolated native ~zod/~nec with the preview client.
It checks the 85% dialog on laptop and phone screens, desktop sound-left/
appearance-right placement across five themes, and shared intro layout. It
injects two failed room-watch retries and an overdue heartbeat, preserving
room/canvas pixels and recording that no `join` is sent. It deletes a real
Eyre channel and closes its client stream, then verifies restored room, Global
Chat and lobby watches. Owner removal must still remove the player even when
canvas history is out of sync, and cannot trigger an automatic rejoin.
Ordinary guesses/chat/hints must produce zero unrelated lobby broadcasts;
membership changes must still update the restored browser subscription.

`tests/audio-clock.py` checks half fireworks gain, a 20-second scheduled audio
window, silence after a late arrival, decoded PCM, mute/resume and the existing
4 Hz tick scheduling/cancellation regression. `tests/finale.py` retains the
full native ten-round and 40-second visual lifecycle test. These tests do not
establish capacity for 500 concurrent ships; see `docs/SCALING.md`.

0.23.0 verification passed on two native test ships: two failed watch retries,
overdue heartbeat, retained canvas and countdown clock, fresh room snapshots,
no join replay, and authoritative owner removal despite out-of-sync drawing
history. Deleting the native Eyre channel and closing its client EventSource
recovered room/chat/lobby watches. The 85% settings layout passed five themes,
intro, laptop and phone dimensions. Ordinary guess/chat/hint actions generated
zero lobby events while removal still refreshed the room list. Audio-clock
checks passed half gain, a 20-second stop deadline and no late replay. The full
ten-round native finale regression passed the 40-second visuals, mute/resume,
scoring, removal, refreshed winners and automatic next game.

Installed 0.23.0 comet checks passed after atomic agent/UI import and Treaty
publication: Name/profile/character media, full canvas edges, Classic/Blingee
settings, known-host counts/filtering, native search/create/leave, tools, tile
and version metadata. JavaScript/Python syntax and whitespace checks passed.
The isolated test ships were shut down; the real comet remains running.

### 0.24.0 ranked roster and word history

`tests/ranked-roster.py` checks descending scores, stable ties, the artist pencil,
local/solved name colors and end-of-round resets across all 12 themes.
`tests/finale.py` checks score ranking between two native ships after a correct
guess while retaining the full ten-round/finale lifecycle regression.

`+ursketch!ursketch-word-history` runs 2,000 native assignments across game
boundaries, requiring each answer to be outside the preceding 100 assignments.
It checks bounded unique history, serialized room restoration, old-state
migration and selection when only one word remains eligible. The existing
native rules, hints and vector tests also pass with the new room schema.

0.24.0 installed comet verification passed after atomic agent/UI import and
Treaty publication. The native 2,000-round history generator passed again on
the comet. Installed browser checks passed the ranked character roster,
Classic/Blingee layouts, full canvas, room lifecycle and version metadata.
The isolated test ships were shut down; the real comet remains running.

### 0.25.0 Spider-Man theme

Run `URSKETCH_THEMES=spider-man` with `tests/new-themes.py` for focused checks;
add `URSKETCH_INSTALLED=1` to verify the published client. The checks cover saved
selection/audio preferences, artwork and readable fields, full canvas edge
strokes, unchanged pixels through theme switching/resizing, score-ranked roster
colors/proportions, chat selection and laptop/phone fit. Screenshots capture
Connect, the room browser, settings and game. `tests/ranked-roster.py` also checks
the new theme alongside all existing themes.

0.25.0 preview and installed Spider-Man checks passed, including decoding all
three supplied images and comparing installed media hashes. Ranking/color
checks passed all 13 themes. Installed comet checks passed Connect, profiles,
room search/create/leave, full canvas, Classic/Blingee layouts and Treaty 0.25.0
metadata. SVG parsing, JavaScript/Python syntax and whitespace checks passed.

### 0.25.1 matching names and scores

The 13-theme ranked-roster regression checks red after a correct guess,
including the local player's own correct guess, matching name/score colors,
and black/green restoration at round end. Installed roster checks also compare
name and score colors rather than requiring every score to be red.

0.25.1 passed the 13-theme regression and installed comet checks, including
matching roster colors, room lifecycle and Treaty version metadata.

### 0.26.0 room controls, reconnection, banks and mobile

- `+ursketch!ursketch-admin-rules` verifies the 2,000/500/500/500 bank counts,
  excluded default entries, v11 room migration, saved seat/score/solve state,
  difficulty overrides, durations and grouped undo. It also checks that departure
  during the three-second reveal keeps the canvas and selects the right artist.
- `tests/room-admin.py` uses two isolated native ships to check owner permissions,
  timer bounds/reset, a 110-word Markdown upload, room/artist difficulty, whole
  pen-gesture undo, undoing fills/clears with byte-identical peer canvases, the
  three-second reveal, no-expiry reload/reconnect, live round metadata, saved
  score/order, transferred ownership and the most-recent-room banner.
- `tests/audio-clock.py` adds independent wall-clock cutoff, mutual exclusion
  of ticks/fireworks and no repeated replacement of a prematurely ended finale
  voice, alongside its existing decoded PCM and countdown scheduling checks.
- `tests/mobile-and-performance.py` checks genuine mobile user-agent detection,
  mobile-only Send, explicit layout selection, phone/landscape geometry and full
  artist canvas. It compares 60 unchanged metadata renders with the previous
  client and verifies the roster nodes are reused across four themes.
- `tests/finale.py` includes the final three-second artwork interval before the
  40-second finale, and checks automatic new games, scoring, sound, removal and
  explicit refreshed rejoining. The ranked-roster regression still covers all
  13 themes. `scripts/wordlists.py` validates the exact released Markdown banks.

The notebook posting receipt records counts and source hashes, with every note
read back. It contains no credentials or private notebook identifiers.

0.26.0 passed the native agent/rules, 2,000-round history and hint checks,
13-theme roster regression, two-ship admin/undo/reconnect/latest-room test,
full ten-round and 43-second final-round-hold/finale lifecycle, audio clock
regressions and mobile/performance checks. The installed comet passed native
admin rules and browser lifecycle/layout/publication checks. Installed mobile
checks confirm the admin icon stays outside the drawing canvas. Both isolated
test ships are stopped; the real comet remains running.

## 0.26.1 lobby and canvas prompts

`comet.py` checks that invite controls and code parsing are absent and old invite
URLs remain in an unsearched lobby. It checks the yellow host banner's canvas
placement, disabled state with one player, enabled Start action with two,
owner-only visibility, and replacement by the artist prompt. Multiword hint
fixtures check blank word separators both before and after letter reveals.
Multiplayer suites now set up rooms through host search and room selection.

Preview and installed-comet checks passed for 0.26.1 on November 7, 2026,
including the published Treaty version. `artifacts/host-start-banner.png`
records the first-game banner on the installed comet.

## 0.26.2 finite fireworks and silent output

`audio-clock.py` runs in Chromium by default; set
`URSKETCH_AUDIO_BROWSER=webkit` for WebKit. Both browsers check a complete
20-second real-time fireworks playback with frequent room updates, finite PCM,
50% gain, silence/output suspension after expiration, overlapping cues,
next-game wakeup, interruption/resume and frozen performance-clock expiration.
The normal four-Hz countdown and background turn-cue checks remain in place.
Results are saved separately in `artifacts/audio-clock-verification.json` and
`artifacts/audio-clock-verification-webkit.json`. Recording waveform evidence
is in `artifacts/fireworks-noise-analysis.json`; no recording or extracted PCM
is included in the game or repository.

## 0.27.0 social and larger games

`social-and-rooms.py` uses two isolated native ships. It verifies persisted
names/characters (including ship fallback), no automatic browser search,
first-joiner hosting and concurrent shared-room claims, whole-row inspection,
header order, independent bottom chat, hidden/private chat answers, no chat
points, correct-answer audio, and the NewRound cue before the artwork hold.

`friendships.py` verifies native Pals installation/revival, an offline request
remaining unconfirmed, notifications and reload without running Pals, denial,
later acceptance, native mutual records, display names, presence and Groups
DM link targets. It resets only the `~zod`/`~nec` test friendship. Its fake
distributor uses the official Pals source, a public self-contained desk, and
test-only source/coordinator overrides; it never contacts real ships. Fresh
installation and revival of a previously stopped Pals desk are both checked.

`+ursketch!ursketch-social-rules` checks 25-player capacity, peak round counts
through departures/rejoins, final-round detection, next-game minimum reset,
and preserving v12 room state. Mobile/performance and finite audio regressions
also pass. `comet.py` preserves the installed user's chosen name while checking
the served client and Treaty release.

`live-social.py` checks native social readiness, the installed menu/explainer,
manual shared-room entry, phone/laptop dialog bounds and the fact that opening
the menu does not install Pals. It sends no real friendship requests or DMs.

## 0.27.1 targeted Groups composers

`groups-dm.py` exercises the actual DM button and installed Groups frontend,
with page-local friend fixtures. It checks the selected ship's DM route and
visible empty MessageInput for two new targets and a repeated target. It
blocks message-sending commands, checks that none occur, verifies detached
opener access and tests popup-block recovery. Disposable browser contexts keep
pending local conversations out of the user's normal browser storage.

Set `URSKETCH_DM_BROWSER=webkit` to use WebKit and `URSKETCH_DM_MOBILE=1` for
phone layout. Results are recorded by engine/layout under `artifacts/`.
