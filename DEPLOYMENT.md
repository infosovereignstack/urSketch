# urSketch deployment

- Publisher: `~livbec-pitsyd-botryp-hoshec--faltec-lavtel-firrup-marzod`
- Desk and Gall agent: `%ursketch`
- Version: 0.11.0
- Runtime: Vere 4.6 / Zuse 408
- Intro route: `/apps/ursketch`
- Username route: `/apps/ursketch/connect`
- Lobby / direct room route: `/apps/ursketch/play`
- Source: `https://github.com/infosovereignstack/urSketch`

Install on another ship:

```hoon
|install ~livbec-pitsyd-botryp-hoshec--faltec-lavtel-firrup-marzod %ursketch
```

This is an independent desk and publication. Rooms, agent state, subscriptions,
and browser preferences are not imported from other desks. All participating
ships must install urSketch and use new room invitations. The original desk
is kept separately for rollback and is not a dependency of this app.

The source checkout is `urSketch/`. Historical Git revisions and external
source credits are retained; the active source, UI, protocol, installation
instructions, metadata, and browser storage use urSketch.

The comet uses native Hood/Clay imports because filesystem commits are not
reliable on its runtime. `scripts/import-clay.py --batch FILE...` atomically
imports related files; `--remove=FILE` removes a renamed file in that commit.
Standard runtime/mark files are inherited from the desk copy. The installed
bill starts only `%ursketch`.

Third-party Classic artwork provenance is in `NOTICE.md`.

## Release verification — October 31, 2026

urSketch 0.6.0 was installed and publicly published on the comet. Docket and
Treaty show the urSketch name, icon, route, and version. The previous app's
listing and HTTP bindings were removed; its desk/state remain private for
rollback. Only the urSketch game tile remains.

Passed on the live Zuse 408 comet: native game, hint/migration, vector codec,
and bandwidth generators; authenticated room creation, invite search,
refresh/rejoin, departure, favicon decoding, tile and Treaty checks. Native
bandwidth measured 2,210,462 snapshot bytes versus 92,202 delta bytes.

Passed on two clean Zuse 409 ships: source install/compilation, multiplayer
names and private answers, drawing replay/scoring/timers, Default/Classic
layout and palette persistence, hints and settings, and vector-stream pixel
parity, remote writes, reload/proxy/gap recovery, and full-view fallback.
JavaScript syntax, Python compilation, and whitespace checks passed.

Audited the active source, generated bundle, served page, and mounted desk:
no former app names remain. Third-party provenance is isolated in NOTICE.md.
The new repository starts with the renamed source; the original repository
retains the previous project's history and rollback material separately.

## 0.7.0 intro update — October 31, 2026

Landscape's existing route now opens the animated intro; Play now opens the
lobby at `/apps/ursketch/play`. Existing root invite URLs with queries continue
to open the app, and new invite links use the direct lobby route. Game state,
protocol, scoring, and subscriptions are unchanged.

Media files live under `desk/media/`, served after authentication. Custom
binary marks preserve byte lengths. The generated library holds only paths,
MIME types and hashes; it does not compile video data into Hoon source or HTML.
The importer packs binary files in bounded chunks for native Clay imports.
Assets have content-addressed URLs and private immutable cache headers. Eyre
controls transfer framing; the media response deliberately omits Content-Length.

The original video stream's SHA-256 is unchanged. The logo is a transparent
urSketch edit over the original wordmark, with its replacement background
masked to the old letters and its brightness following the source fade.
The control hit targets use all 442 source frames. The audio is stored as
`media/audio/music/theme_song.mp3`; `media/audio/cues/` is reserved for future
sounds. Browser audio policy may require Enable sound. Reduced motion starts
paused, and leaving/hiding the intro stops playback.

Passed on two isolated Zuse 409 ships: native source and binary import,
authenticated media hashes, original video decoding, dynamic hit tracking,
audio/mute/volume, Instructions, reduced motion, phone/laptop fit, and normal
cross-ship gameplay on the new lobby route. JavaScript/Python syntax and
whitespace checks passed. See `tests/intro.py`, fresh intro screenshots, and
`artifacts/intro-source-verification.json`.

The final wordmark uses the selected built-in imagegen lettering with a small
vector correction to the opening u, stored in `media/images/intro-wordmark.svg`.
This keeps its spelling unambiguous while retaining the reference lettering.
Native SVG media delivery and the complete intro suite also passed.

Deployed and published 0.7.0 on the live Zuse 408 comet. The full intro suite
passed against the final wordmark and media files, including restoring mute
and volume after browser-history navigation. Existing live room/rejoin,
Landscape tile, favicon, and Treaty 0.7.0 checks passed as well.

## 0.7.1 app tile — October 31, 2026

The Landscape tile uses the intro's urSketch wordmark centred on its exact
light blue background (#9fc1e0). The visible lettering occupies 80% of the
tile width. A 512×512 PNG export keeps the installed/published image compact;
Docket's color metadata matches the same blue. The header/favicon stay unchanged.
`python3 scripts/export_tile.py` regenerates the tile from the existing SVG
wordmark with Playwright, without re-generating the logo. Normal builds use
`web/tile.png`. Both the Docket file and native importer use the same image
and the Docket color as the source of truth.

Deployed and published October 31, 2026. Live checks passed for installed and
published PNG image equality/decoding, Treaty 0.7.1, favicon, and room/rejoin
flows. The 512×512 tile export was visually checked before deployment.

## 0.7.2 intro logo removal — October 31, 2026

Temporarily removes the intro wordmark image. The original baked-in lettering
stays covered; the cleanup samples the rendered video/poster background colours
so it stays clean through playback and fade-out. The coverage is restricted
to the old lettering, preserving animated artwork elsewhere in that corner.
The tile, favicon, audio, and Play now motion are unchanged. Existing wordmark
assets remain available for the tile and the forthcoming replacement SVG.

Deployed and published 0.7.2 on October 31, 2026. Visual checks confirmed the
logo is absent and background cleanup stays restricted to its old lettering.
The live intro suite passed playback, media integrity, moving controls, audio,
responsive layout, reduced motion, and navigation. Syntax/whitespace checks pass.

## 0.7.3 selected original logo — October 31, 2026

Uses the owner's selected original PNG directly in both the intro and tile.
`media/images/ursketch-logo.png` is copied byte-for-byte from the supplied file;
its SHA-256 match is recorded in artifacts/logo-selection.json. There are no
glyph replacements, vector corrections, or letter clipping in either path.
The intro renders the complete image with object-fit: contain and follows the
source fade. The tile exporter draws the complete PNG at one uniform scale,
centred by its visible bounds on the existing #9fc1e0 background. The original
lettering cleanup stays underneath the separate intro image. Older edited
variants are retained as historical assets but are not used by the intro/tile.

Deployed and published 0.7.3 on October 31, 2026. Visual previews confirmed the
selected image in both placements. Live media-integrity/intro checks and the
installed/published tile, favicon, room/rejoin, and Treaty 0.7.3 checks passed.

## 0.8.0 intro presentation and music — October 31, 2026

Removes the bottom controls and adds an intro Settings gear using the exact
same dialog/source and preference reader as the game. `themeQuiet` applies a
0.25 music gain after master volume; `themeDisabled` stops theme music without
affecting game/test sounds. Old saved settings default both options to false.
Changes apply immediately and survive navigation/history restoration. The
settings dialog also fits narrow phone screens in the normal lobby/game.

Music attempts playback immediately, independently of the video download.
Browser-denied autoplay retries synchronously on a real pointer/key gesture.
No artificial interaction or browser-policy bypass is used. Saved master mute
and audio output are respected; disabled music is not fetched automatically.
Reduced motion pauses visuals independently, and returning from instructions
aligns video to the continuing music instead of restarting the song.

The scene is uniformly scaled by 0.8. Its page background follows sampled
video/poster colours, including fades. Original-letter cleanup coverage is
expanded and a render-only alpha filter suppresses faint halo pixels while
leaving the canonical PNG unchanged and preserving opaque letter artwork.

Preview checks passed for exact media, music starting before held video
requests, quarter/off preferences across intro and game, disabled-music network
suppression, autoplay fallback, colour matching, 80% geometry, responsive
layout, moving controls, reduced motion, navigation, and normal room/rejoin.
JavaScript/Python syntax and whitespace checks passed.

Live verification on the publisher comet passed after the native Clay import
and Treaty publication: exact media, independent immediate audio with first-gesture
fallback, quarter/off settings, matched background, 80% sizing, responsive intro,
and the existing room/rejoin/tile smoke checks. Published version is 0.8.0.

## 0.8.1 complete intro background repair — October 31, 2026

The original logo's complete 940,0–1620,280 rectangle is replaced on every
rendered frame by the sampled sky and reconstructed background circle. This
replaces the incomplete letter-shaped SVG mask. The source video and selected
urSketch PNG remain unchanged.

The visible scene now uses an sRGB canvas rather than the video compositor.
Compression noise in the two flat background blues is normalized before the
repair, and the page uses the same sampled sky colour. This avoids differences
between decoded canvas samples and separately composited video colours. The
new uniform scale is .72, exactly 90% of 0.8.0's .8 scale. Controls and hit areas
continue to track the source animation. No game state or protocol changes.

Preview checks passed for rendered repair pixels (with the replacement logo
excluded), actual screenshot pixels inside/outside all four scene corners,
normal/fade frames, 72% size, responsive layout, and all existing intro music,
settings, navigation and media checks.

Live 0.8.1 verification passed after native Clay import and Treaty publication:
intro pixel/geometry/audio checks and the normal room/rejoin/tile/publication
smoke suite. JavaScript/Python syntax and whitespace checks passed.

## 0.8.2 synchronized intro replay — October 31, 2026

Frame/button tracking, logo brightness and audio synchronization now use the
video element's local currentTime instead of requestVideoFrameCallback's
presentation timestamp. Loop detection explicitly seeks the music back to the
new visual playhead and resumes it if it stopped, respecting all saved music,
mute and volume preferences. This also accounts for the MP3 and video having
slightly different durations. The source animation, media files, original fade,
logo artwork, background repair and scene size are unchanged.

The preview suite passed three natural playback passes with actual Web Audio
signal measurements, full logo brightness at each new pass, and audio/video
drift below 60 ms in the measured windows. The test deliberately makes callback
timestamps cumulative after the first loop: this previously selected the final
dark logo frame and attempted to seek audio past its duration. Regression output
is stored in artifacts/intro-loops.json. The existing media, settings, navigation,
responsive geometry and screenshot pixel checks also passed.

Live 0.8.2 intro verification passed, including three audible playback passes
with cumulative callback timestamps, plus the normal room/rejoin/tile/publication
checks. Syntax and whitespace checks passed.

## 0.9.0 separate username screen — October 31, 2026

Play now and the intro fallback now lead to /apps/ursketch/connect. The existing
authenticated HTML handler serves this route; no Gall state, game rules, native
HTTP routing or protocol changes are required. An early route style prevents a
flash of the room browser before the username view appears.

The page uses the supplied screenshot's silver scanlined gradient, reference
panel/form positions, glass Connect button and a separate gradient urSketch
logo. The white-letter fill uses the canonical PNG's luminance mask and sampled
reference colours; the canonical logo, animation and tile remain unchanged.
There are no people and no password input. Welcome copy matches the request.

The name field defaults to the full @p and validates the existing backend's
96-byte UTF-8 limit. Connect opens the channel and saves the native profile
before navigating to /play; failures preserve the field and allow retry. Direct
invites and /play room recovery retain their existing behavior. The room browser
has a name summary and Change name link instead of the old player editor.
Players' display names and permanent ship IDs can be inspected by click/keyboard.

Preview checks passed for reference geometry, no scrolling at 1280×720,
1024×600, 390×844 and 320×568, full comet IDs, custom names, error/retry behavior,
profile inspection, room creation/search/invites/rejoin, and the full intro
suite including three audible passes with cumulative frame-callback timestamps.
The two-ship browser/Classic test scripts were updated for the new name flow;
they were not rerun because no game protocol or geometry changed.

Live 0.9.0 verification passed after native Clay import and Treaty publication:
username/reference geometry, laptop/phone fit, full-ship/custom profiles, retry,
profile inspection, room search/create/invites/rejoin, tile/publication, and the
full intro suite with three audible playback passes. Syntax and whitespace
checks passed.

## 0.10.0 reference room browser — October 31, 2026

The /play lobby is replaced by the supplied browser reference's geometry and
scale: outer silver frame, compact logo/version, top beveled actions, pale guide,
bottom host input, blue scroll rails and right-hand room table. Studio and
language categories are omitted. Existing game/username/intro layouts remain
separate; Default and Classic game preferences do not replace the lobby design.

The language-tab space contains known-host selection and search progress.
Invite-entry controls are hidden, but code parsing, copied invitations and direct
room URLs are retained. Full/empty filters persist locally and affect visible
rows only. Room names join; phase/capacity and player identities are available
on hover/focus. Version remains small, black and left-aligned under the logo.

Lobby JSON adds a public players array (name/ship) per room. No state migration,
game rules, scoring or drawing payload changes are needed. The browser keeps
live subscriptions to up to 20 remembered hosts and deduplicates IDs across all
reported rooms, independently of filters. A tooltip identifies reachable/known
host scope; disconnected hosts lose their live contribution. Legacy hosts
without rosters produce a ≥ minimum instead of a false exact count.

Preview verification passed: reference coordinates at 1280×720, laptop/mobile
page fit, functional scroll arrows/keys, Settings/Instructions, independent
filters, simulated host subscription updates and distinct-ID aggregation,
subscription reuse, hidden invite parsing, direct invites, room/rejoin/profile
flows and the full three-pass intro audio regression. Multi-host count fixtures
use simulated subscription callbacks; live native-roster verification follows
installation. The prior two-/four-ship suites were updated for hidden invite
entry but are not rerun for this layout release.

Browser previews also passed after applying Classic settings and after a
simulated back/forward-cache restoration. Restored /play pages reload to create
fresh native channels and lobby subscriptions, preserving saved profiles and
room recovery. The updated native agent compiled and is running on the comet.

Live 0.10.0 verification passed after native agent/assets import and Treaty
publication: authenticated native roster IDs, reference browser geometry,
known-host count fixtures, filters, scroll rails, both themes, history refresh,
profile/room/rejoin/invite flows, tile/publication and the full three-pass intro
audio regression. JavaScript/Python syntax and whitespace checks passed.

## 0.11.0 shared chat and search separation — November 1, 2026

The version below the logo reads v followed by the actual release. The left
panel is Global Chat and its bottom form sends messages. The former host
selector area now contains ship search. Results show room rows or None found;
the completed search does not leave a full ship name in the field or status.
Known hosts still feed the independent player total, and hidden invite parsing
and direct invitations remain intact.

All clients use the publisher comet configured in web/chat-config.json for
shared chat, independent of their current room host. Native /global-chat watches
publish a bounded 100-message history; the global-chat action validates message
length/control characters and a one-second identity cooldown. Sender IDs come
from the native source ship rather than JSON claims. Plain-text rendering and
identity inspection are retained. The service has its own ready/retry/send state
and cannot prevent room browsing when unavailable.

State 5 adds the message log without changing room records or game rules.
A state-4 room was kept active through the upgrade on clean fake ~zod; its room,
profiles and scores were checked afterward. Cross-ship tests with fake ~nec
verified both directions, a forged sender field being ignored, search/chat
independence, retained failed drafts, history after refresh, plain-text markup,
message bounds and cooldown. Test posts were confined to local-only fake ships.
The clean tests use Vere 4.6 / Zuse 408, matching the publisher runtime.

The compiler caught an inferred nonempty-list type in the first history trim;
the corrected implementation explicitly types the list before applying scag.
The failing version was never installed on the publisher. Preview page/room
checks passed, including moved search and the v prefix. Native live verification
follows the final import; live checks will read chat without posting test messages.

Live 0.11.0 verification passed after native import and Treaty publication:
v prefix, Global Chat readiness, top ship search, simplified room results,
profile/room/rejoin/invite flows, known-host counts and filters, publication,
and three audible intro passes. Live chat was read without posting test messages.
The isolated fake ships were shut down after native delivery/migration checks.
JavaScript/Python syntax and whitespace checks passed.

## 0.26.1 — November 7, 2026

Installed the generated interface and Docket 0.26.1 together through native
Clay import. The live comet browser suite passed, including public Treaty
version/image/route, host Start banner, artist prompt, space-separated hints,
removed invitation entry/URLs, room search, create/leave, and canvas edge drawing
across laptop sizes and themes. JavaScript/Python syntax, build and whitespace
checks passed. The core room protocol and saved state schema are unchanged.

## 0.26.2 — November 7, 2026

Installed the finite-fireworks audio engine and Docket 0.26.2 through native
Clay import. The live comet suite passed and confirms the served audio source
exactly matches the tested file, plus the published Treaty version/image/route.
Chromium and WebKit passed complete real-time 20-second fireworks playback,
interruption/resume, repeat-update guards, output suspension, unrelated clicks
during silence, and next-game audio wakeup. JavaScript/Python syntax, build and
whitespace checks passed. Supplied media and the room-state schema are unchanged.
The affected physical mobile device still requires confirmation after refresh.

## 0.27.0 — November 8, 2026

Imported room-state 13, the native social agent/configuration, bill, generated
interface, rules generator and Docket 0.27.0 together. Published a final native
social update for presence retry backoff after isolated validation. Existing
room and profile migrations preserve their values.

Two isolated ships passed shared-room first-joiner/concurrent claims, saved
profiles, chat privacy/no chat scoring, correct-answer and end-of-drawing cue
timing, native Pals install/revival, persisted requests without Pals, denial,
acceptance, mutual records, friend names/presence and Groups DM link checks.
Native capacity/peak-round/migration, mobile/performance and finite audio
regressions passed. No friendship tests contacted real identities.

The installed comet passed the full interface/publication suite, native room
rules and 25-player rules, and a read-only Friends-menu smoke test at laptop
and phone sizes. The served client matches the release. Treaty advertises
0.27.0. Pals remained absent on the comet after these checks; installation
requires the player's Request friendship or Become Friends action. The Lounge
button is a placeholder; no public group has been created.
