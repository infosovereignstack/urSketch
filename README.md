# urSketch for Urbit

A multiplayer drawing game hosted on Urbit ships. One Gall agent owns rooms,
checks guesses, awards points, and synchronizes vector drawings over Ames.
The browser uses Eyre channels directly, with no npm dependencies or external
services. All browser assets are embedded and served by the ship.

## Install from the publisher

urSketch 0.13.0 is published from
`~livbec-pitsyd-botryp-hoshec--faltec-lavtel-firrup-marzod`.
On another ship, run:

```hoon
|install ~livbec-pitsyd-botryp-hoshec--faltec-lavtel-firrup-marzod %ursketch
```

You can also browse that ship in Landscape’s app discovery and select urSketch.
After installation, open its tile or `/apps/ursketch` for the animated intro.
Choose **Play now** to enter the username screen at `/apps/ursketch/connect`.
Choose a display name and press **Connect** to enter the room browser at
`/apps/ursketch/play`. The
publisher must be online for a new ship to download the desk and updates.
The published desk currently targets Zuse 408.

## Install from source

Use a **new dedicated desk** on each participating ship. In the Dojo:

```hoon
|new-desk %ursketch, =gall &
|mount %ursketch
```

In your computer’s terminal, from this directory:

```sh
python3 scripts/build.py
python3 scripts/install.py /absolute/path/to/your/pier/ursketch
```

Back in the Dojo:

```hoon
|commit %ursketch
|install our %ursketch
```

Log into the ship’s web interface, then open `/apps/ursketch` on that same origin.
The installer preserves the runtime version and standard mark files created by
`|new-desk`, so it does not copy a stale kernel version from another project.

To update source later, rerun the two Python commands and `|commit %ursketch`.

The desk and agent are both `%ursketch`. `/apps/ursketch` is the animated intro;
`/apps/ursketch/play` opens the lobby directly.
Install this desk on every participating ship. Existing rooms and browser
preferences from another app are separate; create new rooms and invitations.

## Play

- The room search box switches between **Browse a host ship** and
  **Room invite code**, using one input and **Search →** button. Each mode
  remembers its input when you switch.
- Save or select a display name in **Who’s playing?** on the landing page.
  Profiles stay in your browser, while names in a room are synchronized by its
  host. Urbit ship identity still authenticates actions.
- The game fits laptop viewports; the players and game log are on the left,
  conversation is below, and the canvas is on the right. The timer uses a grey dial that turns red for the final 20 seconds.
- Create a room on your own ship. It supports 2–10 players.
- Friends install urSketch on their ships, open their own `/apps/ursketch/play`, and
  enter your ship in the search box above the room list.
  Search and join each show progress until the host responds.
- Invite URLs carry `host` and `room` and still open the game directly on the
  player’s own ship. The invite-code parser and compact codes such as
  `~sampel-palnet/room-abcd1234` are retained; invite-entry controls are currently
  hidden from the browser. No one needs to log into another player’s ship.
- The owner starts the game. Each artist is assigned a word and immediately has 120 seconds to draw. The first correct guess starts a full 20-second finish window. Guessers use the input under the Game log.
- Correct guesses earn 10, 9, 8, 7, 6, then 5 points each. The drawer earns
  10 points for the first solve and 1 for each additional solve. Hints reduce
  that initial artist reward to 5, then 4, then 3 points. No solves means
  no drawer points. A turn ends when everyone guesses,
  time expires, or the artist passes. The result is logged and the next artist starts immediately.
- Before anyone guesses correctly, the drawer can press **Give hint** at most
  three times. The first shows the word's letter count and blanks. The next
  two reveal one random, previously hidden letter position each. Spaces stay
  visible, and revealed letters last through the turn and refresh/rejoin.
  Give hint closes after the first correct guess; Skip becomes Done.
- Open the game screen's **⚙ Settings** for volume, mute, audio output,
  a test sound, theme, reduced motion, and larger chat text. Preferences are
  saved in this browser. Classic is the default; Blingee adds pink glitter, hearts and black velvet chrome. The previous Default theme is hidden. Classic uses the supplied drawer/
  guesser layouts, floating palettes, compact panes, and original control sprites. Grubbery
  Theme is a coming-soon placeholder. Game effects honor the same master volume, mute, and output device.
  Output selection depends on [browser support](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/setSinkId);
  unsupported browsers use system default. Microphone permission is not requested.
- A game contains exactly 10 drawing turns total, one artist per round. The owner can start another game afterward.
- The drawer has Pen (**P**), Brush (**B**), Spray (**Y**), Eraser (**E**),
  Rectangle (**S**), Circle (**C**), Line (**L**), Fill, Zoom (**Z**), and Clear,
  following the reference drawing controls.
  Brush is translucent; selecting a shape again toggles filled/outline.
  Shift constrains shapes; Shift+Clear clears with the selected color.
- Use **1–8**, **9**, **0** for widths 1–8, 16, 32; left/right arrows adjust
  width and up/down arrows adjust brightness. **D** toggles black/white,
  **Alt+click** samples a color, **Space+drag** pans, and **+ / −** zoom.
  Space+Alt+click zooms in; Space+Command+click or Shift+Zoom zooms out.
  Double-click Zoom to reset zoom and pan. **Tab** switches between Game and Chat inputs.
- There are 24 reference colors including browns, an advanced color picker,
  width preview, and palettes whose grip allows rearrangement or double-click
  rotation. Their placement is saved in your browser.
- After a refresh or interrupted connection, the lobby offers **Rejoin** and
  **Leave room**. Your identity and score are held for up to two minutes while
  disconnected. Connected players renew their place automatically. Temporary heartbeat failures
  retry within that window instead of immediately returning you to the lobby.
  Recovery state is synchronized between tabs. An expired lobby recovery card
  never sends a leave request for a game active in another tab. Departure
  messages distinguish leaving from a two-minute disconnect timeout.

One identity per ship prevents a browser from claiming another ship’s score or
artist permissions. Correct guesses are replaced with a success message.
The game log and conversation are separate. Chat messages containing the
answer are rejected during a drawing turn. Guessers receive no word length or letters until the drawer gives a hint.
The full answer remains private until the turn is revealed.
Returning to a room restores the authoritative drawing and scores.

## Source and checks

```text
desk/app/ursketch.hoon       Gall, HTTP, private per-ship views, JSON actions
desk/lib/ursketch-game.hoon      Pure turn and timer rules; 100 drawing prompts
desk/lib/ursketch-types.hoon     Versioned state’s shared data types
desk/lib/ursketch-wire.hoon      Compact vector codec and stream proxy cache
desk/lib/ursketch-assets.hoon    Generated browser bundle
desk/gen/ursketch-rules.hoon Rules regression checks
desk/gen/ursketch-wire.hoon  Codec, bounds, and snapshot cache checks
desk/gen/ursketch-bandwidth.hoon Encoded-payload benchmark
web/drawing.js             Drawing tools and deterministic command replay
web/settings.js            Local audio, theme, and accessibility preferences
web/logo.svg               Header logo and browser favicon
web/tile.png               Centred intro wordmark on the light blue app tile
web/                       HTML, CSS, and JavaScript source
scripts/                   Asset builder and dedicated-desk installer
tests/                     Browser integration checks
```

Run the Hoon rules checks from a Dojo with the urSketch desk selected:

```hoon
=dir /=ursketch=
+ursketch-rules
```

`python3 scripts/build.py` regenerates the embedded browser bundle. JavaScript
can be checked with `node --check web/app.js` and `node --check web/drawing.js` and `node --check web/settings.js`. See `tests/README.md` for the
browser integration checks and verification record.

## Current scope

Rooms live on the host ship; browse a known host to find its rooms. There is no
global directory, password room, spectator role, moderation panel, or imported
external word list. urSketch code and branding are original. Third-party Classic
control graphics are credited in [NOTICE.md](NOTICE.md).

Drawings travel as lossless vector commands, with up to 12,000 commands per
turn and 80 commands per batch. Updated clients use compact numeric tuples
and indexed drawing deltas. Ordinary drawing updates send only new commands;
chat, guesses, scores, and other room metadata do not resend drawing history.
Joining, reload, and recovery use complete snapshots. Missing deltas trigger
an automatic snapshot request; duplicates are ignored. Proxy ships maintain
a complete cached view for additional local tabs.

## Animated introduction and audio

Landscape opens the supplied animation with the selected original PNG wordmark.
The original video stream is preserved rather than recreated. The real Play
now target follows its button frame by frame; Instructions opens the rules.
Play now opens the separate username screen; Connect saves the display name
and opens the room browser. Direct invitations still open the game.

The music is `desk/media/audio/music/theme_song.mp3`. Game cue files live
in `desk/media/audio/cues/` and play from confirmed room events. The theme starts
immediately without waiting for video loading, subject to browser autoplay
permissions and saved mute preferences. If autoplay is blocked, the first real
click or key retries it; there is no bottom control bar.

The intro's top-right gear opens the same Settings menu as the game. **Theme
song at 25% volume** applies one quarter of its normal level after master volume;
**Disable theme song** stops only the music. Both are saved in this browser.
Master mute, volume, and selected audio output still apply. Each animation loop
resets the song to the video’s local playhead so music, logo brightness and moving
buttons repeat together. Reduced motion
pauses visuals independently of music. Leaving or hiding the intro pauses audio.

The animation displays at 90% of the 0.8.0 size (72% of its original size).
Decoded footage is rendered on one sRGB canvas, with compression noise in the
two flat blues normalized to the sampled colours. Screenshot pixels at the
scene boundary match the page, including fades. The entire original-logo
rectangle is rebuilt from the blue background and circle, removing all baked
lettering beneath the new logo.
The selected PNG stays unchanged; rendering removes faint low-alpha halo pixels
while preserving the opaque lettering. See `desk/media/README.md` for media
storage/build details and `NOTICE.md` for source credits.

## Username screen

`/apps/ursketch/connect` follows the supplied silver login reference, without
people or a password field. The welcome text is owner-supplied. Username is
prefilled with the full authenticated ship's @p, including comet names, and can
be replaced with a display name. Connect opens the native ship channel, saves
the profile, then navigates to the room browser. A failed connection leaves the
form available for retry. No room browsing starts until Connect is pressed.

The old player editor is replaced in the room browser with the current name
and a Change name link. Saved player names remain local to this browser/ship.
Native profile validation allows at most 96 UTF-8 bytes; the form uses the same
limit instead of truncating long ship IDs. Select a player's name in a room by
click or keyboard to inspect their display name and permanent Urbit ID.

`web/connect-logo.svg` is a separate silver-gradient variant of the canonical
logo, using sampled colours from the reference. The original PNG, intro logo
and Landscape tile are unchanged. `web/connect.css` keeps the desktop reference
geometry and stacks the form for small screens.

## Classic room browser

The /play lobby follows the owner's 1280×720 reference: compact urSketch logo
with a v-prefixed version in small black text below it, beveled controls, pale welcome
panel, blue scroll rails and a right-hand room table. Instructions, Settings and
Create Room remain functional. There is no Studio or language selector. The
bottom field sends Global Chat messages. Ship search is above the
room list; successful searches clear the field and show room names, or None found.
Known hosts remain remembered for the player count without a ship-name dropdown. The existing game-screen theme and drawing layout are independent.

The room heading counts distinct Urbit IDs across reachable known host ships,
including players in rooms hidden by either filter. Known hosts are stored per
browser/ship (up to 20) and watched for live lobby updates. A ship in multiple
rooms or hosts counts once. The title tooltip reports reachable/known scope.
Older hosts without player IDs contribute a conservative minimum, marked ≥.
Unreachable hosts are excluded rather than presenting stale counts as live.

Full means 10 players; empty means zero. The two filters are independent and
saved locally. Point to a room name for its phase/capacity, or its player count
for names and ship IDs. Click a room name to join. Rejoin/Leave recovery remains
in the welcome panel. Direct invite URLs and the hidden code parser are retained.

## Global Chat

The room browser uses one shared native chat hosted on the publisher comet,
independently of the ship being searched. `web/chat-config.json` supplies that
host at build time. Each browser connects through its own ship's authenticated
Eyre channel; the existing native relay/proxy carries chat to the shared host.
Room searching, player counts and room chat remain separate.

The host stores the latest 100 messages, with the actual sender's Urbit ID,
display name and timestamp. Message text is rendered as plain text, and sender
names open the identity inspector. The host accepts up to 240 UTF-8 bytes per
message and one message per sender per second. Failed sends retain the draft;
unavailable/disconnected chat offers Retry and does not block room browsing.
The service is public to ships using the app; chat readers are not added to
the room-player total unless they are in a room.

Agent state 5 adds chat history. Migration copies existing rooms, drawing data,
profiles, proxy caches and presence leases from state 4; older migrations remain
supported. The upgrade was verified with a room active on an isolated ship.

## Game sounds (0.12.0)

The nine provided cues cover joining, new drawing turns, your turn to draw,
private close guesses, your correct guess, another player’s correct guess,
accepted hints, player rules reminders, and the finish timer. The player menu
offers **Warn about game rules**; reminders appear in the bottom room Chat.

Close guesses are checked on the host using normalized edit distance (including
transposed letters) and substantial contiguous matches. Only the sender receives
the “guess is close!” response; the answer stays on the host.

Drawing turns last 120 seconds. The first solve starts a full 20-second finish
window; later solves do not reset it. When everyone has solved, the round ends immediately. Solve order and the finish window survive a correct guesser leaving. Saved
rooms upgrade to state 7 while preserving drawings, scores, names, hints, and
shared chat. Four ticks per
second are scheduled on the Web Audio clock. Leaving, muting,
or ending the turn stops scheduled ticks. The remaining ticks are scheduled
in advance so background-tab timer throttling cannot change their tempo;
turn alerts can also sound while the game is in a background tab. Snapshot history does not replay cues.
A browser interaction enables game audio; browsers enforce this autoplay rule.

`scripts/clean_turn_audio.py` subtracts the aligned SomeoneElseGotTheWord reference
from YourTurnToDraw using fractional delay and a smoothly varying gain. It keeps
all 92,160 stereo samples (44.1 kHz) and does not crop the clip. The original is
kept in `assets/audio-originals/`; the reproducible report is
`artifacts/turn-audio-cleanup.json`. Rerunning requires NumPy, SciPy, and ffmpeg.

## Classic and Blingee update (0.13.0)

Classic is selected for fresh browsers and replaces any saved former Default
selection. Both Classic and Blingee share the full 1000×700 drawing surface,
fit without cropping. The display fills the entire drawing panel, mapping pointer coordinates to the shared vector surface. Changing themes
resets zoom while retaining drawing commands. Every new drawing turn resets
the artist to a black pen. Create-room and word-choice menus use Classic
controls, and the room header uses the current urSketch wordmark. The browser
favicon uses the blue app tile.

Connecting after name selection automatically browses the publisher comet
(`~livbec_marzod` is its shorthand; the full ship ID remains in chat-config.json).
Explicit host/invite URLs still override this default. Creating a room on your
own ship remains available while browsing the publisher.

NewRound plays when the automatically assigned drawing turn begins. Close guesses never enter the public room log and only their
sender receives the close feedback. Select Game or Chat by clicking its title,
log or input; the selected log is yellow and the other is white.

A signal timeout is the browser request deadline (15 seconds), distinct from
the host-action acknowledgement deadline (20 seconds). A timed-out action may
still have reached the ship; mutations are not retried automatically. Host
rejections mean a native rule/permission check failed; action-specific messages
now describe likely causes. The old acknowledgement contains no detailed error,
so these explanations do not identify a past incident's exact cause.

[GlueWear PR #1 source review](docs/gluewear-pr-1-review.md) records compatibility
issues and recommended fixes. The embedding PR has not been merged.

## Immediate rounds update (0.14.0)

Words are assigned automatically with no prep or reveal pause. Artists see a
yellow word/rules banner until their first mark. The canvas clears between
rounds and remains visible after the tenth round. Game logs retain ordered
results, with private artist prompts and private solver word/score messages.
The guessing field receives focus on joining and after drawing.

A normal tab close sends a room leave immediately; refreshing or navigating
away does too. Crashes, offline devices and browsers that discard the final
request still use the existing two-minute presence timeout.

Countdown ticks have fixed, unique slots per turn, preventing an exhausted
audio queue from re-arming after clock divergence. The intro circle repair
uses its measured blue palette instead of sampling a pixel obscured by the
animated exclamation mark and lightbulb.

## Canvas and name-page update (0.14.1)

The canvas fills the drawing panel in both themes, including its top and
bottom edges, instead of leaving letterbox bands. Shared 1000×700 vector
coordinates and zoom/pan remain compatible with existing drawings. The Name
page now explains permanent Urbit IDs and editable display names; its text
panel expands to contain the longer copy.
