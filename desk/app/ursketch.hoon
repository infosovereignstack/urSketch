/+  *ursketch-types, ursketch-game, ursketch-assets, ursketch-wire, ursketch-media
|%
+$  card  card:agent:gall
+$  state-0  [%0 rooms=(map @t old-room)]
+$  state-1  [%1 rooms=(map @t old-room) proxies=(map path json)]
+$  state-2  [%2 rooms=(map @t old-room) proxies=(map path json) names=(map @p @t)]
+$  state-3  [%3 rooms=(map @t room-v3) proxies=(map path json) names=(map @p @t) leases=(map lease-key @da)]
+$  state-4  [%4 rooms=(map @t room-v5) proxies=(map path json) names=(map @p @t) leases=(map lease-key @da)]
+$  global-message  [who=@p label=@t text=@t at=@da]
+$  state-5  [%5 rooms=(map @t room-v5) proxies=(map path json) names=(map @p @t) leases=(map lease-key @da) global-chat=(list global-message)]
+$  state-6  [%6 rooms=(map @t room-v6) proxies=(map path json) names=(map @p @t) leases=(map lease-key @da) global-chat=(list global-message)]
+$  state-7  [%7 rooms=(map @t room-v7) proxies=(map path json) names=(map @p @t) leases=(map lease-key @da) global-chat=(list global-message)]
+$  state-8  [%8 rooms=(map @t room-v8) proxies=(map path json) names=(map @p @t) leases=(map lease-key @da) global-chat=(list global-message)]
+$  state-9  [%9 rooms=(map @t room) proxies=(map path json) names=(map @p @t) leases=(map lease-key @da) global-chat=(list global-message)]
+$  state-10  [%10 rooms=(map @t room) proxies=(map path json) names=(map @p @t) leases=(map lease-key @da) global-chat=(list global-message) avatars=(map @p avatar)]
--
=|  state-10
=*  state  -
^-  agent:gall
=<
|_  =bowl:gall
  +*  this  .
      cor  ~(. +> bowl)
  ++  on-init
    =^  cards  state  init:cor
    [cards this]
  ++  on-save  !>(state)
  ++  on-load
    |=  old=vase
    =/  v10=(unit state-10)  (mole |.(!<(state-10 old)))
    =/  v9=(unit state-9)  (mole |.(!<(state-9 old)))
    =/  v8=(unit state-8)  (mole |.(!<(state-8 old)))
    =/  v7=(unit state-7)  (mole |.(!<(state-7 old)))
    =/  v6=(unit state-6)  (mole |.(!<(state-6 old)))
    =/  v5=(unit state-5)  (mole |.(!<(state-5 old)))
    =/  v4=(unit state-4)  (mole |.(!<(state-4 old)))
    =/  v3=(unit state-3)  (mole |.(!<(state-3 old)))
    =/  v2=(unit state-2)  (mole |.(!<(state-2 old)))
    =/  v1=(unit state-1)  (mole |.(!<(state-1 old)))
    =.  state
      ?^  v10  u.v10
      ?^  v9  [%10 rooms.u.v9 proxies.u.v9 names.u.v9 leases.u.v9 global-chat.u.v9 ~]
      ?^  v8  [%10 (~(run by rooms.u.v8) migrate-v8:ursketch-game) proxies.u.v8 names.u.v8 leases.u.v8 global-chat.u.v8 ~]
      ?^  v7  [%10 (~(run by rooms.u.v7) migrate-v7:ursketch-game) proxies.u.v7 names.u.v7 leases.u.v7 global-chat.u.v7 ~]
      ?^  v6  [%10 (~(run by rooms.u.v6) migrate-v6:ursketch-game) proxies.u.v6 names.u.v6 leases.u.v6 global-chat.u.v6 ~]
      ?^  v5  [%10 (~(run by rooms.u.v5) |=(r=room-v5 (migrate-v5:ursketch-game r now.bowl))) proxies.u.v5 names.u.v5 leases.u.v5 global-chat.u.v5 ~]
      ?^  v4  [%10 (~(run by rooms.u.v4) |=(r=room-v5 (migrate-v5:ursketch-game r now.bowl))) proxies.u.v4 names.u.v4 leases.u.v4 ~ ~]
      ?^  v3  [%10 (~(run by rooms.u.v3) migrate-v3:ursketch-game) proxies.u.v3 names.u.v3 leases.u.v3 ~ ~]
      ?^  v2  [%10 (~(run by rooms.u.v2) migrate-room:ursketch-game) proxies.u.v2 names.u.v2 ~ ~ ~]
      ?^  v1  [%10 (~(run by rooms.u.v1) migrate-room:ursketch-game) proxies.u.v1 ~ ~ ~ ~]
      =/  previous=state-0  !<(state-0 old)
      [%10 (~(run by rooms.previous) migrate-room:ursketch-game) ~ ~ ~ ~ ~]
    on-init
  ++  on-poke
    |=  [=mark =vase]
    =^  cards  state  (poke:cor mark vase)
    [cards this]
  ++  on-watch
    |=  =path
    =^  cards  state  (watch:cor path)
    [cards this]
  ++  on-leave
    |=  =path
    =^  cards  state  (leave:cor path)
    [cards this]
  ++  on-peek
    |=  =path
    ^-  (unit (unit cage))
    ~
  ++  on-agent
    |=  [=wire =sign:agent:gall]
    =^  cards  state  (agent:cor wire sign)
    [cards this]
  ++  on-arvo
    |=  [=wire =sign-arvo]
    =^  cards  state  (arvo:cor wire sign-arvo)
    [cards this]
  ++  on-fail
    |=  [=term =tang]
    ~&  tang
    [~ this]
--
|_  =bowl:gall
++  init
  ^-  (quip card state-10)
  =.  rooms  (~(run by rooms) resume-turn)
  =/  keys=(list lease-key)
    %-  zing
    %+  turn  ~(tap by rooms)
    |=  [rid=@t r=room]
    (turn players.r |=(p=player [rid who.p]))
  =.  leases
    %+  roll  keys
    |=  [key=lease-key acc=(map lease-key @da)]
    ?:  (~(has by acc) key)  acc
    (~(put by acc) key (add now.bowl ~m2))
  =/  turns=(list card)
    %-  zing
    %+  turn  ~(tap by rooms)
    |=  [rid=@t r=room]
    ^-  (list card)
    ?:  ?&(?|(?=(%choosing phase.r) ?=(%drawing phase.r) ?=(%reveal phase.r) ?=(%finished phase.r)) (gth deadline.r now.bowl))
      ~[(timer rid r)]
    ~
  =/  presence=(list card)
    %+  turn  ~(tap by leases)
    |=  [key=lease-key until=@da]
    (lease-timer rid.key who.key until)
  =/  views=(list card)
    %-  zing
    %+  turn  ~(tap by rooms)
    |=  [rid=@t r=room]
    (publish rid)
  :_  state
  (welp ~[[%pass /bind %arvo %e %connect [~ /apps/ursketch] %ursketch]] (welp views (welp turns presence)))
++  poke
  |=  [=mark =vase]
  ^-  (quip card state-10)
  ?+  mark  ~|('unsupported mark' !!)
    %handle-http-request
      =/  req  !<([id=@ta req=inbound-request:eyre] vase)
      ?.  authenticated.req.req
        (respond id.req 303 'text/plain' 'Log into your ship first.')
      ?:  =(url.request.req.req '/apps/ursketch/character')
        (respond id.req 200 'application/json; charset=utf-8' (avatar-body our.bowl))
      =/  asset  (lookup:ursketch-media url.request.req.req)
      ?^  asset
        =/  location=path
          (weld /[(scot %p our.bowl)]/ursketch/[(scot %da now.bowl)] file.u.asset)
        =/  data=octs  .^(octs %cx location)
        (respond-media id.req mime.u.asset etag.u.asset data)
      ?:  =((cut 3 [0 21] url.request.req.req) '/apps/ursketch/media/')
        (respond id.req 404 'text/plain' 'Media not found.')
      ?:  ?|
            =(url.request.req.req '/apps/ursketch')
            =(url.request.req.req '/apps/ursketch/')
          ==
        (respond id.req 200 'text/html; charset=utf-8' intro:ursketch-assets)
      (respond id.req 200 'text/html; charset=utf-8' (index:ursketch-assets our.bowl))
    %json
      =/  j=json  !<(json vase)
      ?>  ?=(%o -.j)
      =/  target=@p  (slav %p (text j 'host'))
      ?:  !=(target our.bowl)
        ?>  =(src.bowl our.bowl)
        =/  request=@t  (text j 'request')
        [~[[%pass /relay/[request] %agent [target %ursketch] %poke %json !>(j)]] state]
      =/  act=@t  (text j 'action')
      =/  provided=(unit json)  (~(get by p.j) 'name')
      =.  names
        ?~  provided  names
        =/  label=@t  (so:dejs:format u.provided)
        ?>  (lte (met 3 label) 96)
        ?>  (levy (trip label) |=(c=@tD (gte c 32)))
        (~(put by names) src.bowl label)
      =/  provided-avatar=(unit json)  (~(get by p.j) 'avatar')
      =.  avatars
        ?~  provided-avatar  avatars
        =/  a=json  u.provided-avatar
        ?>  ?=(%o -.a)
        =/  selected=avatar  [(text a 'body') (text a 'face') (text a 'hat')]
        ?>  ?&((valid-part body.selected) (valid-part face.selected) (valid-part hat.selected))
        (~(put by avatars) src.bowl selected)
      ?:  =(act 'global-chat')
        =/  body=@t  (text j 'text')
        ?>  ?&((gth (met 3 body) 0) (lte (met 3 body) 240))
        ?>  (levy (trip body) |=(c=@tD ?|(?&((gte c 32) (lte c 126)) (gte c 128))))
        ?>  !(lien global-chat |=(m=global-message ?&(=(who.m src.bowl) (gth (add at.m ~s1) now.bowl))))
        =/  messages=(list global-message)
          [[src.bowl (player-name src.bowl) body now.bowl] global-chat]
        =.  global-chat  (scag 100 messages)
        [~[global-chat-card] state]
      ?:  =(act 'profile')
        ?>  =(src.bowl our.bowl)
        [~[lobby-card] state]
      =/  rid=@t  (text j 'room')
      ?>  ?&((gth (lent (trip rid)) 0) (lte (lent (trip rid)) 40))
      ?>  (levy (trip rid) |=(c=@tD ?|(?&((gte c 'a') (lte c 'z')) ?&((gte c '0') (lte c '9')) =(c '-'))))
      ?:  =(act 'create')
        ?>  =(src.bowl our.bowl)
        ?>  (lth ~(wyt by rooms) 64)
        ?>  !(~(has by rooms) rid)
        =/  title=@t  (crip (scag 48 (trip (text j 'title'))))
        =.  rooms  (~(put by rooms) rid (fresh:ursketch-game title src.bowl))
        =^  presence  state  (touch rid src.bowl)
        [(welp presence (snoc (publish rid) lobby-card)) state]
      =/  r=room  (~(got by rooms) rid)
      ?:  =(act 'join')
        ?:  (member:ursketch-game r src.bowl)
          =^  presence  state  (touch rid src.bowl)
          [(welp presence (publish rid)) state]
        ?>  !(full:ursketch-game r)
        =.  r  r(players (snoc players.r [src.bowl 0 %.n]))
        =/  old-token=@ud  token.r
        =.  r  (say:ursketch-game r (player-name src.bowl) 'joined the room' 'system')
        =.  r  (resume:ursketch-game r now.bowl)
        =.  r  ?:(!=(old-token token.r) (announce r) r)
        =.  rooms  (~(put by rooms) rid r)
        =^  presence  state  (touch rid src.bowl)
        =/  cards=(list card)  (welp presence (snoc (publish rid) lobby-card))
        ?:  ?&(!=(old-token token.r) (gth deadline.r now.bowl))
          [(snoc cards (timer rid r)) state]
        [cards state]
      ?>  (member:ursketch-game r src.bowl)
      =^  presence  state
        ?:  =(act 'leave')  [~ state]
        (touch rid src.bowl)
      ?:  ?|(=(act 'heartbeat') =(act 'away'))  [presence state]
      ?:  =(act 'sync')
        [(welp presence ~[(stream-card rid src.bowl %.y)]) state]
      ?:  =(act 'draw')
        ?>  ?&(?=(%drawing phase.r) =(src.bowl who:(head players.r)) =(token.r (number j 'token')))
        =/  raw=(list json)  (array j 'lines')
        ?>  ?&((gth (lent raw) 0) (lte (lent raw) 80))
        =/  start=@ud  (lent lines.r)
        ?>  (lte (add (lent raw) start) 12.000)
        =/  batch=(list line)  (turn raw decode:ursketch-wire)
        =.  r  r(lines (welp (flop batch) lines.r))
        =.  rooms  (~(put by rooms) rid r)
        [(welp presence (draw-cards rid r start batch)) state]
      =/  drawer=@p  ?~(players.r ~zod who.i.players.r)
      =/  old-token=@ud  token.r
      =/  old-deadline=@da  deadline.r
      =/  is-drawer=?  =(src.bowl drawer)
      =/  guess-text=@t  ?:(!=(act 'guess') '' (crip (scag 160 (trip (text j 'text')))))
      =/  close=?  ?:(!=(act 'guess') %.n (close-guess:ursketch-game guess-text answer.r))
      =.  r
        ?+  act  ~|('unknown action' !!)
          %start
            ?>  =(src.bowl owner.r)
            ?>  ?&(?=(%waiting phase.r) !started.r)
            ?>  (gte (lent players.r) 2)
            ?>  !(gth deadline.r now.bowl)
            (new-game:ursketch-game r now.bowl)
          %hint
            ?>  ?&(?=(%drawing phase.r) is-drawer =(token.r (number j 'token')))
            (hint:ursketch-game r now.bowl)
          %clear
            ?>  ?&(?=(%drawing phase.r) is-drawer =(token.r (number j 'token')))
            r(lines ~)
          %skip
            ?>  ?&(?=(%drawing phase.r) is-drawer)
            ?>  =(token.r (number j 'token'))
            (end-round r 'skip')
          %guess
            ?>  ?&(?=(%drawing phase.r) !is-drawer)
            ?>  =(token.r (number j 'token'))
            =/  r=room  r
            =/  p=player  (need (find-player players.r src.bowl))
            ?>  !solved.p
            =/  guess=@t  (crip (scag 160 (trip (text j 'text'))))
            ?:  =((normalize:ursketch-game guess) (normalize:ursketch-game answer.r))
              =/  first=?  =(solves.r 0)
              =/  points=@ud  (guess-points:ursketch-game solves.r)
              =/  artist=@t  (player-name drawer)
              =.  r  (finish-window:ursketch-game r src.bowl now.bowl)
              =.  r  r(solvers (snoc solvers.r [src.bowl (player-name src.bowl) points]))
              =.  r
                ?:  !first  r
                (say:ursketch-game r '' 'The word has been found! The round will end in 20 seconds!' 'announcement')
              =.  r  (whisper:ursketch-game r src.bowl (rap 3 ~['You found the word: ' answer.r '!']) 'found-word')
              =.  r  (whisper:ursketch-game r src.bowl (rap 3 ~['You found ' artist '\27s word and get ' (scot %ud points) ' points!']) 'reward')
              =.  r  (log:ursketch-game r (player-name src.bowl) 'guessed the word!' 'correct' ~ `src.bowl)
              ?:  (all-solved:ursketch-game r)  (end-round r 'all')
              r
            ?:  close  r
            (say:ursketch-game r (player-name src.bowl) guess 'guess')
          %warn
            =/  target=@p  (slav %p (text j 'player'))
            ?>  ?&(!=(target src.bowl) (member:ursketch-game r target))
            (say:ursketch-game r (player-name src.bowl) (cat 3 'reminds ' (cat 3 (player-name target) ' not to violate drawing rules.')) 'warning')
          %chat
            =/  msg=@t  (crip (scag 240 (trip (text j 'text'))))
            ::  Keep the answer out of the separate conversation panel.
            ?>  ?|  !?=(%drawing phase.r)
                    ?=(~ (find (trip (normalize:ursketch-game answer.r)) (trip (normalize:ursketch-game msg))))
                ==
            (say:ursketch-game r (player-name src.bowl) msg 'chat')
          %kick
            ?>  =(src.bowl owner.r)
            =/  target=@p  (slav %p (text j 'player'))
            ?>  ?&(!=(target src.bowl) (member:ursketch-game r target))
            =.  r  (log:ursketch-game r (player-name src.bowl) (cat 3 'removed ' (cat 3 (player-name target) ' from the room.')) 'kick' ~ `target)
            (leave-room r target 'left the room')
          %leave
            (leave-room r src.bowl 'left the room')
        ==
      =.  r
        ?:  ?&(?=(%drawing phase.r) !=(old-token token.r))  (announce r)
        r
      =.  rooms
        ?:  =(0 (lent players.r))
          (~(del by rooms) rid)
        (~(put by rooms) rid r)
      =.  leases
        ?:  =(act 'kick')  (~(del by leases) [rid (slav %p (text j 'player'))])
        ?:  =(act 'leave')  (~(del by leases) [rid src.bowl])
        leases
      =/  cards=(list card)  (welp presence (publish rid))
      =.  cards
        ?:  ?&(?|(!=(old-token token.r) !=(old-deadline deadline.r)) (gth deadline.r now.bowl))
          (snoc cards (timer rid r))
        cards
      =.  cards
        ?:  !close  cards
        (welp cards (close-cards rid src.bowl token.r (text j 'request') (cat 3 guess-text ' is close!')))
      [(snoc cards lobby-card) state]
  ==
++  watch
  |=  =path
  ^-  (quip card state-10)
  ?:  ?=([%http-response *] path)  [~ state]
  ?:  ?=([%proxy @ *] path)
    ?>  =(src.bowl our.bowl)
    =/  target=@p  (slav %p i.t.path)
    ?>  !=(target our.bowl)
    =/  cached=(unit json)  (~(get by proxies) path)
    =/  cards=(list card)
      ?~  cached  ~
      ~[[%give %fact ~[path] %json !>(u.cached)]]
    ?:  (~(has by wex.bowl) [path target %ursketch])  [cards state]
    [(snoc cards [%pass path %agent [target %ursketch] %watch t.t.path]) state]
  ?:  =(path /relay)
    ?>  =(src.bowl our.bowl)
    [~ state]
  ?:  =(path /global-chat)  [~[global-chat-card] state]
  ?:  =(path /lobby)  [~[lobby-card] state]
  ?:  ?=([%stream @ @ ~] path)
    =/  rid=@t  i.t.path
    =/  viewer=@p  (slav %p i.t.t.path)
    ?>  =(src.bowl viewer)
    [~[(stream-card rid viewer %.y)] state]
  ?>  ?=([%room @ @ ~] path)
  =/  rid=@t  i.t.path
  =/  viewer=@p  (slav %p i.t.t.path)
  ?>  =(src.bowl viewer)
  [~[(view-card rid viewer)] state]
++  leave
  |=  =path
  ^-  (quip card state-10)
  ?.  ?=([%proxy @ *] path)  [~ state]
  ?:  (lien ~(tap by sup.bowl) |=([d=duct who=ship p=(list @ta)] =(p path)))
    [~ state]
  =/  target=@p  (slav %p i.t.path)
  =.  proxies  (~(del by proxies) path)
  [~[[%pass path %agent [target %ursketch] %leave ~]] state]
++  peek
  |=  =path
  ^-  (unit (unit cage))
  ~
++  agent
  |=  [=wire =sign:agent:gall]
  ^-  (quip card state-10)
  ?:  ?=([%proxy @ *] wire)
    ?+  -.sign  [~ state]
      %fact
        =/  payload=json  !<(json q.cage.sign)
        ?:  =('feedback' (text payload 'kind'))
          [~[[%give %fact ~[wire] %json !>(payload)]] state]
        =/  cached=(unit json)
          ?:  ?=([%proxy @ %stream @ @ ~] wire)
            (merge:ursketch-wire (~(get by proxies) wire) payload)
          `payload
        =.  proxies
          ?~  cached  (~(del by proxies) wire)
          (~(put by proxies) wire u.cached)
        [~[[%give %fact ~[wire] %json !>(payload)]] state]
      %kick
        =.  proxies  (~(del by proxies) wire)
        [~[[%give %kick ~[wire] ~]] state]
      %watch-ack
        ?~  p.sign  [~ state]
        [~[[%give %kick ~[wire] ~]] state]
    ==
  ?.  ?=([%relay @ ~] wire)  [~ state]
  ?.  ?=(%poke-ack -.sign)  [~ state]
  =/  ok=?  ?=(~ p.sign)
  =/  payload=json  (obj ~[['kind' s+'ack'] ['request' s+i.t.wire] ['ok' b+ok]])
  [~[[%give %fact ~[/relay] %json !>(payload)]] state]
++  arvo
  |=  [=wire =sign-arvo]
  ^-  (quip card state-10)
  ?:  ?=([%presence @ @ ~] wire)
    ?.  ?=([%behn %wake *] sign-arvo)  [~ state]
    (expire i.t.wire (slav %p i.t.t.wire))
  ?.  ?=([%turn @ @ ~] wire)  [~ state]
  ?.  ?=([%behn %wake *] sign-arvo)  [~ state]
  =/  rid=@t  i.t.wire
  =/  found=(unit room)  (~(get by rooms) rid)
  ?~  found  [~ state]
  =/  r=room  u.found
  ?.  =((slav %ud i.t.t.wire) token.r)  [~ state]
  ?:  (gth deadline.r now.bowl)  [~ state]
  =.  r
    ?:  ?=(%finished phase.r)  (new-game:ursketch-game r now.bowl)
    ?:  ?=(%drawing phase.r)  (end-round r 'time')
    (advance:ursketch-game r now.bowl)
  =.  r  (announce r)
  =.  rooms  (~(put by rooms) rid r)
  =/  cards=(list card)  (snoc (publish rid) lobby-card)
  ?:  (gth deadline.r now.bowl)
    [(snoc cards (timer rid r)) state]
  [cards state]
++  fail
  |=  [=term =tang]
  ^-  (quip card state-10)
  ~&  tang
  [~ state]
++  text
  |=  [j=json key=@t]
  ^-  @t
  ?>  ?=(%o -.j)
  (so:dejs:format (need (~(get by p.j) key)))
++  number
  |=  [j=json key=@t]
  ^-  @ud
  ?>  ?=(%o -.j)
  (ni:dejs:format (need (~(get by p.j) key)))
++  array
  |=  [j=json key=@t]
  ^-  (list json)
  ?>  ?=(%o -.j)
  =/  value=json  (need (~(get by p.j) key))
  ?>  ?=(%a -.value)
  p.value
++  touch
  |=  [rid=@t who=@p]
  ^-  (quip card state-10)
  =/  exists=?  (~(has by leases) [rid who])
  =/  until=@da  (add now.bowl ~m2)
  =.  leases  (~(put by leases) [rid who] until)
  :-  ?:  exists  ~
        ~[(lease-timer rid who until)]
  state
++  lease-timer
  |=  [rid=@t who=@p until=@da]
  ^-  card
  [%pass /presence/[rid]/[(scot %p who)] %arvo %b %wait (max until (add now.bowl ~s1))]
++  expire
  |=  [rid=@t who=@p]
  ^-  (quip card state-10)
  =/  until=(unit @da)  (~(get by leases) [rid who])
  ?~  until  [~ state]
  ?:  (gth u.until now.bowl)
    [~[(lease-timer rid who u.until)] state]
  =.  leases  (~(del by leases) [rid who])
  =/  found=(unit room)  (~(get by rooms) rid)
  ?~  found  [~ state]
  =/  old-token=@ud  token.u.found
  ~&  [%ursketch-presence-expired rid who]
  =/  r=room
    (leave-room u.found who 'disconnected (two-minute timeout)')
  =.  r  ?:(!=(old-token token.r) (announce r) r)
  =.  rooms
    ?~  players.r  (~(del by rooms) rid)
    (~(put by rooms) rid r)
  =/  cards=(list card)  (snoc (publish rid) lobby-card)
  ?:  ?&(!=(old-token token.r) (gth deadline.r now.bowl))
    [(snoc cards (timer rid r)) state]
  [cards state]
++  find-player
  |=  [ps=(list player) who=@p]
  ^-  (unit player)
  ?~  ps  ~
  ?:  =(who who.i.ps)  `i.ps
  $(ps t.ps)
++  timer
  |=  [rid=@t r=room]
  ^-  card
  [%pass /turn/[rid]/[(scot %ud token.r)] %arvo %b %wait deadline.r]
++  respond
  |=  [id=@ta code=@ud mime=@t body=@t]
  ^-  (quip card state-10)
  =/  headers=(list [@t @t])
    ~[['Content-Type' mime] ['Cache-Control' 'no-store'] ['X-Content-Type-Options' 'nosniff']]
  =.  headers
    ?:  =(303 code)  [['Location' '/~/login?redirect=/apps/ursketch'] headers]
    headers
  :_  state
  :~  [%give %fact ~[/http-response/[id]] %http-response-header !>([code headers])]
      [%give %fact ~[/http-response/[id]] %http-response-data !>(`[(met 3 body) body])]
      [%give %kick ~[/http-response/[id]] ~]
  ==
++  respond-media
  |=  [id=@ta mime=@t etag=@t body=octs]
  ^-  (quip card state-10)
  =/  headers=(list [@t @t])
    :~  ['Content-Type' mime]
        ['Cache-Control' 'private, max-age=31536000, immutable']
        ['ETag' etag]
        ['Accept-Ranges' 'none']
        ['X-Content-Type-Options' 'nosniff']
    ==
  :_  state
  :~  [%give %fact ~[/http-response/[id]] %http-response-header !>([200 headers])]
      [%give %fact ~[/http-response/[id]] %http-response-data !>(`body)]
      [%give %kick ~[/http-response/[id]] ~]
  ==
++  obj
  |=  pairs=(list [@t json])
  ^-  json
  [%o (~(gas by *(map @t json)) pairs)]
++  global-chat-card
  ^-  card
  =/  items=(list json)
    %+  turn  (flop global-chat)
    |=  m=global-message
    (obj ~[['id' s+(cat 3 (scot %p who.m) (scot %da at.m))] ['ship' s+(scot %p who.m)] ['name' s+label.m] ['text' s+text.m] ['at' s+(scot %da at.m)]])
  [%give %fact ~[/global-chat] %json !>((obj ~[['kind' s+'global-chat'] ['messages' a+items]]))]
++  lobby-card
  ^-  card
  =/  items=(list json)
    %+  turn  ~(tap by rooms)
    |=  [rid=@t r=room]
    =/  people=(list json)
      %+  turn  players.r
      |=  p=player
      (obj ~[['ship' s+(scot %p who.p)] ['name' s+(player-name who.p)] ['avatar' (avatar-json who.p)]])
    (obj ~[['id' s+rid] ['title' s+title.r] ['count' (numb (lent players.r))] ['phase' s+phase.r] ['players' a+people]])
  [%give %fact ~[/lobby] %json !>((obj ~[['kind' s+'lobby'] ['rooms' a+items]]))]
++  numb
  |=  n=@ud
  ^-  json
  (numb:enjs:format n)
++  close-cards
  |=  [rid=@t who=@p token=@ud request=@t text=@t]
  ^-  (list card)
  =/  payload=json
    (obj ~[['kind' s+'feedback'] ['feedback' s+'close'] ['id' s+request] ['room' s+rid] ['token' (numb token)] ['text' s+text]])
  %-  zing
  %+  turn  watched
  |=  p=path
  ?.  ?=([@ @ @ ~] p)  ~
  ?.  ?|(=(%stream i.p) =(%room i.p))  ~
  ?.  ?&(=(rid i.t.p) =((slav %p i.t.t.p) who))  ~
  ~[[%give %fact ~[p] %json !>(payload)]]
++  view-card
  |=  [rid=@t viewer=@p]
  ^-  card
  =/  r=(unit room)  (~(get by rooms) rid)
  =/  view=json
    ?~  r
      (obj ~[['kind' s+'removed']])
    (view-json u.r viewer %legacy)
  [%give %fact ~[/room/[rid]/[(scot %p viewer)]] %json !>(view)]
++  stream-card
  |=  [rid=@t viewer=@p snapshot=?]
  ^-  card
  =/  found=(unit room)  (~(get by rooms) rid)
  =/  view=json
    ?~  found  (obj ~[['kind' s+'removed']])
    (view-json u.found viewer ?:(snapshot %snapshot %state))
  [%give %fact ~[/stream/[rid]/[(scot %p viewer)]] %json !>(view)]
++  watched
  ^-  (list path)
  ~(tap in (silt (turn ~(tap by sup.bowl) |=([d=duct who=ship p=path] p))))
++  publish
  |=  rid=@t
  ^-  (list card)
  %-  zing
  %+  turn  watched
  |=  p=path
  ?:  ?=([%stream @ @ ~] p)
    ?.  =(rid i.t.p)  ~
    ~[(stream-card rid (slav %p i.t.t.p) %.n)]
  ?.  ?=([%room @ @ ~] p)  ~
  ?.  =(rid i.t.p)  ~
  ~[(view-card rid (slav %p i.t.t.p))]
++  draw-cards
  |=  [rid=@t r=room start=@ud batch=(list line)]
  ^-  (list card)
  =/  seconds=@ud  ?:((gth deadline.r now.bowl) (div (sub deadline.r now.bowl) ~s1) 0)
  =/  payload=json
    %-  obj
    :~  ['kind' s+'draw']
        ['encoding' (numb 1)]
        ['token' (numb token.r)]
        ['from' (numb start)]
        ['count' (numb (lent lines.r))]
        ['seconds' (numb seconds)]
        ['remainingMs' (numb ?:((gth deadline.r now.bowl) (div (mul 1.000 (sub deadline.r now.bowl)) ~s1) 0))]
        ['lines' a+(turn batch pack:ursketch-wire)]
    ==
  %-  zing
  %+  turn  watched
  |=  p=path
  ?:  ?=([%stream @ @ ~] p)
    ?.  =(rid i.t.p)  ~
    ~[[%give %fact ~[p] %json !>(payload)]]
  ?.  ?=([%room @ @ ~] p)  ~
  ?.  =(rid i.t.p)  ~
  ~[(view-card rid (slav %p i.t.t.p))]
++  view-json
  |=  [r=room viewer=@p mode=?(%legacy %snapshot %state)]
  ^-  json
  =/  drawing=?  ?=(%drawing phase.r)
  =/  private=?  ?&(?=(^ players.r) =(viewer who.i.players.r))
  =/  visible=?  ?|(?=(%reveal phase.r) ?=(%finished phase.r) private)
  =/  answer=@t
    ?:  visible  answer.r
    ''
  =/  ps=(list json)
    %+  turn  players.r
    |=  p=player
    (obj ~[['ship' s+(scot %p who.p)] ['name' s+(player-name who.p)] ['avatar' (avatar-json who.p)] ['score' (numb score.p)] ['solved' b+solved.p]])
  =/  ls=(list json)
    ?:  ?=(%state mode)  ~
    %+  turn  (flop lines.r)
    |=  l=line
    ?.  ?=(%legacy mode)  (pack:ursketch-wire l)
    (obj ~[['color' s+color.l] ['width' (numb width.l)] ['x1' (numb x1.l)] ['y1' (numb y1.l)] ['x2' (numb x2.l)] ['y2' (numb y2.l)] ['kind' s+kind.l] ['opacity' (numb opacity.l)] ['filled' b+filled.l] ['seed' (numb seed.l)] ['id' s+id.l]])
  =/  ms=(list json)
    %+  turn  (flop (skim chat.r |=(m=message ?~(audience.m %.y =(viewer u.audience.m)))))
    |=  m=message
    (obj ~[['who' s+who.m] ['text' s+text.m] ['kind' s+kind.m] ['ship' s+?~(actor.m '' (scot %p u.actor.m))]])
  =/  choices=(list json)
    ?:  private  (turn choices.r |=(w=@t [%s w]))
    ~
  =/  seconds=@ud
    ?:  (gth deadline.r now.bowl)  (div (sub deadline.r now.bowl) ~s1)
    0
  %-  obj
  :~  ['kind' s+?:(?=(%state mode) 'state' 'room')]
      ['encoding' (numb ?:(?=(%legacy mode) 0 1))]
      ['count' (numb (lent lines.r))]
      ['title' s+title.r]
      ['owner' s+(scot %p owner.r)]
      ['phase' s+phase.r]
      ['started' b+started.r]
      ['turn' (numb turn.r)]
      ['token' (numb token.r)]
      ['seconds' (numb seconds)]
      ['remainingMs' (numb ?:((gth deadline.r now.bowl) (div (mul 1.000 (sub deadline.r now.bowl)) ~s1) 0))]
      ['celebrating' b+?&(?=(%finished phase.r) (gth deadline.r now.bowl))]
      ['winner' ?~(outcome.r ~ (obj ~[['name' s+label.u.outcome.r] ['score' (numb score.u.outcome.r)]]))]
      ['finishing' b+?&(drawing (gth solves.r 0))]
      ['duration' (numb ?:(drawing ?:((gth solves.r 0) 20 120) 120))]
      ['value' (numb (guess-points:ursketch-game solves.r))]
      ['hintCount' (numb hints.r)]
      ['hint' s+(hint-mask:ursketch-game r)]
      ['artistValue' (numb (drawer-points:ursketch-game 0 hints.r))]
      ['answer' s+answer]
      ['choices' a+choices]
      ['players' a+ps]
      ['lines' a+ls]
      ['messages' a+ms]
  ==
++  resume-turn
  |=  r=room
  ^-  room
  ?:  ?&(?=(%finished phase.r) !(gth deadline.r now.bowl))
    (announce (new-game:ursketch-game r now.bowl))
  ?:  ?&(?=(%waiting phase.r) started.r (gte (lent players.r) 2))
    (announce (resume:ursketch-game r now.bowl))
  ?:  ?=(%choosing phase.r)  (announce (choose:ursketch-game r now.bowl))
  ?:  ?=(%reveal phase.r)  (announce (advance:ursketch-game r now.bowl))
  r
++  announce
  |=  r=room
  ^-  room
  ?:  ?=(%finished phase.r)  (complete r)
  ?.  ?&(?=(%drawing phase.r) ?=(^ players.r))  r
  =/  artist=@p  who.i.players.r
  =/  r=room  r
  =.  r  (whisper:ursketch-game r artist (cat 3 'You\27re up next to draw! Your word is: ' answer.r) 'artist-word')
  (say:ursketch-game r '' (rap 3 ~[(player-name artist) ' drawing round ' (scot %ud +(turn.r))]) 'round')
++  result
  |=  [r=room reason=@t]
  ^-  room
  ?.  ?&(?=(%drawing phase.r) ?=(^ players.r))  r
  (say:ursketch-game r '' (result-text:ursketch-game r (player-name who.i.players.r) reason) 'round-result')
++  end-round
  |=  [r=room reason=@t]
  ^-  room
  (complete (advance:ursketch-game (result r reason) now.bowl))
++  complete
  |=  r=room
  ^-  room
  ?.  ?&(?=(%finished phase.r) ?=(~ outcome.r) (gth deadline.r now.bowl))  r
  =/  r=room  r
  =/  winners=(list player)  (winners:ursketch-game players.r)
  ?~  winners  r
  =/  score=@ud  score.i.winners
  =/  winners=(list player)  winners
  =/  labels=(list @t)  (turn winners |=(p=player (player-name who.p)))
  =/  label=@t
    =/  names=(list @t)  labels
    |-  ^-  @t
    ?~  names  ''
    ?~  t.names  i.names
    (cat 3 i.names (cat 3 ' & ' $(names t.names)))
  =.  r  r(outcome `[label score], lines ~)
  (say:ursketch-game r '' (rap 3 ~['That was the last round. The winner is ' label ' with a score of ' (scot %ud score) ' points!']) 'game-result')
++  leave-room
  |=  [r=room who=@p text=@t]
  ^-  room
  =/  artist=?  ?&(?=(%drawing phase.r) ?|(?&(?=(^ players.r) =(who who.i.players.r)) (lte (lent players.r) 2)))
  =.  r  ?:(!artist r ?:(=(turn.r 9) (end-round r 'left') (result r 'left')))
  =.  r  (depart:ursketch-game (say:ursketch-game r (player-name who) text 'system') who now.bowl)
  ?:  (all-solved:ursketch-game r)  (end-round r 'all')
  r
++  valid-part
  |=  value=@t
  ^-  ?
  ?&((gth (met 3 value) 0) (lte (met 3 value) 40) (levy (trip value) |=(c=@tD ?|(?&((gte c 'a') (lte c 'z')) ?&((gte c '0') (lte c '9')) =(c '-')))))
++  avatar-json
  |=  who=@p
  ^-  json
  =/  saved=(unit avatar)  (~(get by avatars) who)
  ?~  saved  ~
  (obj ~[['body' s+body.u.saved] ['face' s+face.u.saved] ['hat' s+hat.u.saved]])
++  avatar-body
  |=  who=@p
  ^-  @t
  =/  saved=(unit avatar)  (~(get by avatars) who)
  ?~  saved  'null'
  ::  IDs contain only the characters accepted by valid-part; no JSON escapes.
  (rap 3 ~['{"body":"' body.u.saved '","face":"' face.u.saved '","hat":"' hat.u.saved '"}'])
++  player-name
  |=  who=@p
  ^-  @t
  =/  label=@t  (~(gut by names) who '')
  ?:  =('' label)  (scot %p who)
  label
--
