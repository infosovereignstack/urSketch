# GlueWear PR #1 review

Reviewed the source diff for [Add Noltbook and Glurff interactive artifact
support](https://github.com/infosovereignstack/urSketch/pull/1), commit
`a1e1585c185ceecabd485b49b33b50cde9db35a2`, against urSketch 0.12.0 and the
requested 0.13.0 changes. The PR has not been merged or installed.

The embedding feature can coexist with Classic/Blingee, ten-round games, the
ten-player limit, sound timing, private close guesses, and publisher-first room
browsing. The current patch needs changes before release:

1. **An empty shared room can have no authorized starter.** The
   `noltbook-room` action calls `depart(fresh(..., host), host)`, leaving an empty
   room owned by the host ship. Expiry/last-leave also reset ownership to the
   host. The existing join branch appends a player without transferring ownership.
   If a remote ship is the first player, its browser does not offer Start and
   the native Start action rejects it. The host is not a member either, so it
   cannot start until it joins. Assign ownership to the first arriving member
   of an empty room, or explicitly document/enforce a host-present requirement.

2. **Slow embedding handshakes fall back permanently.** The 1.5-second timeout
   calls `startApp(null)` and sets `appStarted`. A later valid `nb:init` records
   its context but `startApp` exits immediately. A note artifact or private tool
   then stays in the ordinary browser. Make late initialization transition safely
   or use an explicit host-ready handshake with a recoverable timeout.

3. **Rebase and regenerate the bundle.** The PR replaces the same startup flow
   changed here for publisher-first browsing. Standalone browsing should default
   to the publisher; explicit embedded artifact host/room must still win. Rebase
   onto 0.13.0 and run `scripts/build.py`; do not resolve generated Hoon HTML by
   selecting the old bundle, which would restore old UI/audio behavior.

4. **Manifest version is hardcoded to 0.12.0.** Generate it from the Docket
   version used by the release builder to avoid immediately stale metadata.

5. **Shared rooms are shared across notes.** Every artifact on one host points
   to `room-noltbook`; drawings, room chat, scores and the ten-player capacity are
   shared across those notes/Glurff spots. This is intentional in the PR, but the
   embedding UI should say so; note boundaries do not isolate games or chats.

6. **Embedding trust and frame geometry need verification.** The bridge checks
   the parent window, protocol and session, but accepts initialization from any
   parent origin and sends messages with `*`. Pin an expected origin or use a
   documented trusted-host handshake before enabling untrusted embedding sites.
   This is a review concern, not a demonstrated credential leak. Test 760×680
   and 1000×760 frames and smaller laptop frames, along with audio permissions.

The author lists syntax/build checks and explicitly says native Hoon compilation
was unavailable. Native room creation, ownership, rejoin, presence expiry and
empty-room reuse need tests on isolated ships before publication. These findings
come from source review, not from running the proposed embedding code.
