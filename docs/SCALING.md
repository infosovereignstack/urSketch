# Capacity and connection resilience (0.23.0)

## 500 simultaneous players

There is no verified 500-player capacity claim. The current integration tests
use two native ships, and the recorded vector-stream measurements cover 1,600
commands in one room. They do not measure 500 peers, sustained production load,
slow hardware, relayed Ames paths, or mixed network conditions.

Rooms hold 10 players and a host can hold 64 rooms. Thus 500 players require
at least 50 full rooms and fit below the room-count limit on one host. That
limit is a validation boundary, not a performance guarantee. Each room has a
12,000-command drawing limit. Exhausting it still rejects further drawing.

The room host owns game state, timers and fan-out. Its CPU, event-log/disk
latency, memory, upload capacity and each peer's network responsiveness matter.
Existing draw streams send compact incremental vectors; audio/video/character
assets are served from each player's own installed ship. Keeping browsers on
individual ships does not distribute game processing when all rooms are hosted
on the same comet. Room hosting is distributed only when different ships
actually host different rooms; there is no automatic load balancer.

The recorded two-ship vector sample (`artifacts/vector-stream-metrics.json`)
used 85,583 JSON bytes for 40 batches (about 2.1 KB/batch), versus 4,463,815
bytes for the former repeated full snapshots. This is a real payload
measurement, not a throughput benchmark. As an illustrative estimate, 50
rooms × 10 viewers × 2.1 KB × 1–10 batches/second implies roughly 1–11 MB/s of
outbound drawing JSON. Real traffic varies with command count, stroke rate,
legacy clients, Ames encryption/fragmentation/acknowledgements and retries.
CPU or disk can become the bottleneck before the network does.

Shared Global Chat remains centralized on the publisher comet. Each post
currently broadcasts up to 100 retained messages to its subscribers, with a
per-sender one-second rate limit. Five hundred active chat subscribers can
therefore burden that comet even if game rooms are spread over other hosts.
A player count is across known hosts, not a universal directory or exact count
of every person who has installed the app.

Before a 500-person event, distribute rooms across multiple reliable hosts and
run staged native load tests at 50, 100, 250 and 500 concurrent clients/ships.
Measure p50/p95/p99 action-to-visible latency, stream backlog, rejected actions,
recovery time, CPU, memory, disk/event-log latency and upload traffic, including
slow/relayed peers, reconnect storms, room churn and simultaneous finales.
Use the observations to set a tested per-host admission limit. For that scale,
Global Chat deltas/batching and explicit host load/admission controls are the
next changes to assess. A local mock of 500 clients would not prove 500 Ames
peers work well. No such production-scale test has been run in this release.

## Changes in this release

- Browser HTTP requests allow 30 seconds, and host acknowledgements/initial
  room snapshots allow 60 seconds. Timed-out actions are not automatically
  replayed; the UI says they may still arrive. This avoids duplicate guesses,
  scores, chat messages or drawing operations.
- Native EventSource reconnection is retained. A fatally closed Eyre stream
  can reopen with bounded exponential backoff/jitter. Reconnection restores
  room, chat and known-host watches and requests a fresh drawing snapshot.
- A dropped room watch retries at increasing intervals (up to 15 seconds plus
  jitter), keeping the existing room and canvas visible. Only one room-watch
  recovery is in flight. Recovery resubscribes; it never sends `join`.
- A failed heartbeat no longer decides locally that the player was removed.
  The host still owns its existing two-minute presence lease. An exhausted
  local estimate triggers a fresh watch to confirm authoritative membership.
  Explicit leave, owner removal and host expiry still take effect. After a
  real removal, joining again is deliberate; there is no ghost auto-rejoin.
- Membership updates are handled before canvas-history repair, so an out-of-
  sync drawing cannot conceal an owner removal or an expired membership.
- Ordinary chat, wrong guesses and hints no longer broadcast the entire room
  directory. Membership and phase changes still update it. Room-level events
  and game rules are unchanged.

A disconnected browser may show its last drawing while recovering. This is
preservation of context, not an offline game: live input requires a working
connection, and turns continue on the host. A stopped host, prolonged outage,
expired lease or invalidated session still needs recovery/user action.

Urbit's [HTTP API documentation](https://docs.urbit.org/build-on-urbit/tools/js-libs/http-api-guide)
explains channel acknowledgements and deleted-channel recovery. The
[Ames documentation](https://docs.urbit.org/urbit-os/kernel/ames) describes
congestion control, ordering within a flow, and the absence of ordering
across flows. These guarantees do not constitute an application capacity SLA.
