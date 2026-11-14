/+  *ursketch-social-config
|%
+$  card  card:agent:gall
+$  contact
  [name=@t avatar=json incoming=? outgoing=? stage=@t mode=@t error=@t op=@ud at=@da probe=@da presence=json]
+$  shared-room
  [host=@p room=@t ready=? count=@ud round=@ud rounds=@ud until=@da]
+$  state-0  [%0 peers=(map @p contact) label=@t portrait=json title=@t room-host=@p room-id=@t presence-until=@da install-at=(unit @da) next=@ud tick-at=@da shared=(unit shared-room) waiters=(map @p @t) destination=json claim-at=(unit @da) hosting=(unit @t) hosting-ready=? lobby=json sent-at=@da]
+$  state-1  [%1 tags=(map @p (set @ta)) peers=(map @p contact) label=@t portrait=json title=@t room-host=@p room-id=@t presence-until=@da install-at=(unit @da) next=@ud tick-at=@da shared=(unit shared-room) waiters=(map @p @t) destination=json claim-at=(unit @da) hosting=(unit @t) hosting-ready=? lobby=json sent-at=@da]
+$  pals-records  [outgoing=(map @p (set @ta)) incoming=(set @p) receipts=(map @p ?)]
--
=|  state-1
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
    =/  current=(unit state-1)  (mole |.(!<(state-1 old)))
    =.  state
      ?^  current  u.current
      =/  previous=state-0  !<(state-0 old)
      [%1 ~ +.previous]
    on-init
  ++  on-poke
    |=  [=mark =vase]
    ?>  =(mark %json)
    =^  cards  state  (poke:cor !<(json vase))
    [cards this]
  ++  on-watch
    |=  =path
    =^  cards  state  (watch:cor path)
    [cards this]
  ++  on-leave  |=(path [~ this])
  ++  on-peek  |=(path ~)
  ++  on-agent
    |=  [=wire =sign:agent:gall]
    =^  cards  state  (agent:cor wire sign)
    [cards this]
  ++  on-arvo
    |=  [=wire =sign-arvo]
    ?.  ?&(?=([%tick @ ~] wire) ?=([%behn %wake *] sign-arvo))  [~ this]
    ?.  =((slav %da i.t.wire) tick-at)  [~ this]
    =^  cards  state  work:cor
    =^  timer  state  arm:cor
    [(welp cards timer) this]
  ++  on-fail
    |=  [=term =tang]
    ~&  tang
    ?:  (gth tick-at now.bowl)  [~ this]
    =^  cards  state  arm:cor
    [cards this]
--
|_  =bowl:gall
++  obj
  |=  xs=(list [@t json])
  ^-  json
  [%o (malt xs)]
++  text
  |=  [j=json k=@t]
  ^-  @t
  ?>  ?=(%o -.j)
  (so:dejs:format (need (~(get by p.j) k)))
++  optional
  |=  [j=json k=@t]
  ^-  @t
  ?>  ?=(%o -.j)
  =/  got=(unit json)  (~(get by p.j) k)
  ?~  got  ''
  (so:dejs:format u.got)
++  numb
  |=  n=@ud
  ^-  json
  (numb:enjs:format n)
++  number
  |=  [j=json k=@t]
  ^-  @ud
  ?>  ?=(%o -.j)
  (ni:dejs:format (need (~(get by p.j) k)))
++  json-field
  |=  [j=json k=@t]
  ^-  json
  ?>  ?=(%o -.j)
  (~(gut by p.j) k ~)
++  empty-contact
  |=  who=@p
  ^-  contact
  [(scot %p who) ~ %.n %.n '' 'request' '' 0 now.bowl ~2000.1.1 ~]
++  contact-for
  |=  who=@p
  ^-  contact
  (~(gut by peers) who (empty-contact who))
++  safe-label
  |=  value=@t
  ^-  @t
  ?>  ?&((gth (met 3 value) 0) (lte (met 3 value) 96))
  ?>  (levy (trip value) |=(c=@tD (gte c 32)))
  value
++  part
  |=  value=@t
  ^-  @t
  ?>  ?&((gth (met 3 value) 0) (lte (met 3 value) 40))
  ?>  (levy (trip value) |=(c=@tD ?|(?&((gte c 'a') (lte c 'z')) ?&((gte c '0') (lte c '9')) =(c '-'))))
  value
++  safe-avatar
  |=  a=json
  ^-  json
  ?~  a  ~
  (obj ~[['body' s+(part (text a 'body'))] ['face' s+(part (text a 'face'))] ['hat' s+(part (text a 'hat'))]])
++  send
  |=  [who=@p way=wire payload=json]
  ^-  card
  [%pass way %agent [who %ursketch-social] %poke %json !>(payload)]
++  pals-up
  ^-  ?
  .^(? %gu /[(scot %p our.bowl)]/pals/[(scot %da now.bowl)]/$)
++  pals-on-disk
  ^-  ?
  ?.  (~(has in .^((set desk) %cd /[(scot %p our.bowl)]//[(scot %da now.bowl)])) %pals)  %.n
  .^(? %cu /[(scot %p our.bowl)]/pals/[(scot %da now.bowl)]/desk/bill)
++  presence-json
  ^-  json
  =/  live=?  ?&(!=('' title) (gth presence-until now.bowl))
  =/  expires=@ud  ?:(!live 0 (div (mul 1.000 (sub presence-until ~1970.1.1)) ~s1))
  (obj ~[['ship' s+(scot %p our.bowl)] ['name' s+?:(=('' label) (scot %p our.bowl) label)] ['avatar' portrait] ['title' s+?:(live title '')] ['host' s+(scot %p room-host)] ['room' s+?:(live room-id '')] ['expires' (numb expires)]])
++  presence-cards
  ^-  (list card)
  =/  paths=(list path)
    %+  murn  ~(tap by sup.bowl)
    |=  [d=duct who=ship p=path]
    ?.  ?=([%presence @ ~] p)  ~
    =/  c=contact  (contact-for who)
    ?.  ?|(=(who our.bowl) =(stage.c 'friend') ?&(outgoing.c incoming.c))  ~
    `p
  ?~  paths  ~
  ~[[%give %fact paths %json !>(presence-json)]]
++  shared-json
  ^-  json
  ?~  shared  ~
  =/  r=shared-room  u.shared
  (obj ~[['host' s+(scot %p host.r)] ['room' s+room.r] ['ready' b+ready.r] ['count' (numb count.r)] ['round' (numb round.r)] ['rounds' (numb rounds.r)]])
++  shared-card
  ^-  card
  [%give %fact ~[/slate] %json !>(shared-json)]
++  friends-card
  ^-  card
  =/  rows=(list json)
    %+  turn  ~(tap by peers)
    |=  [who=@p p=contact]
    (obj ~[['ship' s+(scot %p who)] ['name' s+name.p] ['avatar' avatar.p] ['incoming' b+incoming.p] ['outgoing' b+outgoing.p] ['stage' s+stage.p] ['mode' s+mode.p] ['error' s+error.p] ['presence' presence.p] ['tags' a+(turn ~(tap in (~(gut by tags) who ~)) |=(tag=@ta [%s tag]))]])
  [%give %fact ~[/friends] %json !>((obj ~[['kind' s+'friends'] ['palsReady' b+pals-up] ['peers' a+rows] ['slate' shared-json] ['destination' destination]]))]
++  arm
  ^-  (quip card state-1)
  =.  tick-at  (add now.bowl ~s5)
  [~[[%pass /tick/[(scot %da tick-at)] %arvo %b %wait tick-at]] state]
++  init
  ^-  (quip card state-1)
  =^  cards  state  arm
  =.  cards  ?:((~(has by wex.bowl) [/lobby our.bowl %ursketch]) cards (snoc cards [%pass /lobby %agent [our.bowl %ursketch] %watch /lobby]))
  =.  cards  ?:((~(has by wex.bowl) [/slate coordinator %ursketch-social]) cards (snoc cards [%pass /slate %agent [coordinator %ursketch-social] %watch /slate]))
  [cards state]
++  work
  ^-  (quip card state-1)
  =|  cards=(list card)
  =/  before=(map @p contact)  peers
  =/  before-tags=(map @p (set @ta))  tags
  =/  records=(unit pals-records)
    ?:  pals-up  `.^(pals-records %gx /[(scot %p our.bowl)]/pals/[(scot %da now.bowl)]/noun)
    ~
  =.  tags  ?~(records tags outgoing.u.records)
  =.  install-at  ?:(pals-up ~ install-at)
  =/  pending-claim=(unit @da)  claim-at
  =/  claim-expired=?  ?~(pending-claim %.n (gth now.bowl (add u.pending-claim ~m2)))
  =.  destination  ?:(claim-expired (obj ~[['nonce' s+(text destination 'nonce')] ['error' s+'The shared-room directory did not respond. Please retry.']]) destination)
  =.  claim-at  ?:(claim-expired ~ claim-at)
  =.  cards  ?:(claim-expired (snoc cards friends-card) cards)
  =.  peers
    ?~  records  peers
    =/  r=pals-records  u.records
    =/  ships=(set @p)  (~(uni in ~(key by peers)) (~(uni in incoming.r) ~(key by outgoing.r)))
    %+  roll  ~(tap in ships)
    |=  [who=@p acc=(map @p contact)]
    ?:  ?|(=(who our.bowl) ?&(!(~(has by acc) who) (gte ~(wyt by acc) 512)))  acc
    =/  p=contact  (~(gut by before) who (empty-contact who))
    =/  out=?  (~(has by outgoing.r) who)
    =/  in=?  (~(has in incoming.r) who)
    ?:  ?&(!in !(~(has by before) who))  acc
    ?:  ?&(in out)
      (~(put by acc) who p(stage 'friend', outgoing %.y, incoming in, error '', at ?:(=(stage.p 'friend') at.p now.bowl)))
    ?:  =(stage.p 'friend')
      (~(put by acc) who p(stage ?:(out 'pending' ?:(in '' 'denied')), outgoing out, incoming in))
    ?:  =(stage.p 'denied')  (~(put by acc) who p)
    (~(put by acc) who p(incoming ?|(in incoming.p), outgoing ?|(out outgoing.p), stage ?:(!=('' stage.p) stage.p ?:(out 'pending' ''))))
  =/  all=(list [who=@p value=contact])  ~(tap by peers)
  |-  ^-  (quip card state-1)
  ?~  all
    =^  more  state  maintain-slate
    =.  cards  (welp cards more)
    =.  cards  ?:(!=([before before-tags] [peers tags]) (welp cards (snoc presence-cards friends-card)) cards)
    [cards state]
  =/  who=@p  who.i.all
  =/  p=contact  value.i.all
  ::  Backfill previously unindexed urSketch friendships once. Respect later
  ::  manual tag removal in Pals; unrelated imported Pals stay untagged.
  =/  tag-friend=?
    ?&(pals-up =(stage.p 'friend') (gth op.p 0) !(~(has by before-tags) who) !(~(has in (~(gut by tags) who ~)) 'urSketch'))
  =.  cards
    ?:  !tag-friend  cards
    (snoc cards [%pass /tag/[(scot %p who)] %agent [our.bowl %pals] %poke %pals-command !>([%meet who (silt ~['urSketch'])])])
  =/  watch-peer=?  ?&(=(stage.p 'friend') (lte probe.p now.bowl) !(~(has by wex.bowl) [/friend/[(scot %p who)] who %ursketch-social]))
  =.  peers  ?:(watch-peer (~(put by peers) who p(probe (add now.bowl ~m1))) peers)
  =.  cards  ?:(watch-peer (snoc cards [%pass /friend/[(scot %p who)] %agent [who %ursketch-social] %watch /presence/[(scot %p our.bowl)]]) cards)
  ?.  ?|(=(stage.p 'checking') =(stage.p 'installing'))
    ?:  ?&(?|(=(stage.p 'pals') =(stage.p 'delivering') =(stage.p 'confirming')) (gth now.bowl (add at.p ~m20)))
      =.  peers  (~(put by peers) who p(stage 'error', error 'The request is taking too long. Retry when both ships are online.'))
      $(all t.all)
    $(all t.all)
  ?:  pals-up
    =.  peers  (~(put by peers) who p(stage 'pals'))
    =.  cards  (snoc cards [%pass /pals/[(scot %p who)]/[(scot %ud op.p)] %agent [our.bowl %pals] %poke %pals-command !>([%meet who (silt ~['urSketch'])])])
    $(all t.all)
  ?:  (gth now.bowl (add at.p ~m20))
    =.  peers  (~(put by peers) who p(stage 'error', error 'Pals could not finish installing. Check Landscape and retry.'))
    $(all t.all)
  =.  peers  (~(put by peers) who p(stage 'installing'))
  ?:  pals-on-disk
    ?:  (gth probe.p now.bowl)  $(all t.all)
    =.  peers  (~(put by peers) who p(stage 'installing', probe (add now.bowl ~s30)))
    =.  cards  (snoc cards [%pass /install %agent [our.bowl %hood] %poke %kiln-revive !>(%pals)])
    $(all t.all)
  =/  installing=(unit @da)  install-at
  ?^  installing  $(all t.all)
  =.  install-at  `now.bowl
  =.  cards  (snoc cards [%pass /install %agent [our.bowl %hood] %poke %kiln-install !>([%pals pals-source %pals])])
  $(all t.all)
++  poke
  |=  j=json
  ^-  (quip card state-1)
  ?>  ?=(%o -.j)
  =/  action=@t  (text j 'action')
  ?:  ?|(=(action 'profile') =(action 'presence'))
    ?>  =(src.bowl our.bowl)
    =.  label  (safe-label (text j 'name'))
    =.  portrait  (safe-avatar (json-field j 'avatar'))
    ?:  =(action 'profile')  [(snoc presence-cards friends-card) state]
    =.  title  (optional j 'title')
    ?>  (lte (met 3 title) 192)
    =.  room-id  (optional j 'room')
    =.  room-host  (slav %p (text j 'host'))
    =.  presence-until  (add now.bowl ~m2)
    [presence-cards state]
  ?:  =(action 'clean-slate')
    ?>  =(src.bowl our.bowl)
    =/  nonce=@t  (text j 'nonce')
    ?>  (lte (met 3 nonce) 80)
    =.  destination  (obj ~[['nonce' s+nonce] ['error' s+'']])
    =.  claim-at  `now.bowl
    [~[(send coordinator /claim (obj ~[['action' s+'slate-claim'] ['nonce' s+nonce]]))] state]
  ?:  =(action 'slate-claim')  (claim (text j 'nonce'))
  ?:  =(action 'slate-assigned')
    ?>  =(src.bowl coordinator)
    =/  rid=@t  (text j 'room')
    =.  hosting  `rid
    =.  hosting-ready  %.n
    =/  payload=json  (obj ~[['action' s+'create'] ['host' s+(scot %p our.bowl)] ['room' s+rid] ['title' s+'A Clean Slate'] ['name' s+?:(=('' label) (scot %p our.bowl) label)] ['avatar' portrait]])
    [~[[%pass /create-slate %agent [our.bowl %ursketch] %poke %json !>(payload)]] state]
  ?:  =(action 'slate-destination')
    ?>  =(src.bowl coordinator)
    ?>  ?=(%o -.destination)
    ?.  =((text destination 'nonce') (text j 'nonce'))  [~ state]
    =.  claim-at  ~
    =.  destination  j
    [~[friends-card] state]
  ?:  ?|(=(action 'slate-heartbeat') =(action 'slate-release') =(action 'slate-failed'))
    ?>  =(our.bowl coordinator)
    ?~  shared  [~ state]
    ?>  ?&(=(src.bowl host.u.shared) =((text j 'room') room.u.shared))
    ?:  ?|(=(action 'slate-release') =(action 'slate-failed'))
      (close-slate 'The shared room closed. Click A Clean Slate to open a new one.')
    =.  shared  `u.shared(ready %.y, count (number j 'count'), round (number j 'round'), rounds (number j 'rounds'), until (add now.bowl ~m2))
    deliver-slate
  ?:  ?|(=(action 'request') =(action 'accept') =(action 'deny'))
    ?>  =(src.bowl our.bowl)
    =/  who=@p  (slav %p (text j 'ship'))
    ?>  !=(who our.bowl)
    ?>  ?|((~(has by peers) who) (lth ~(wyt by peers) 512))
    =/  p=contact  (contact-for who)
    ?:  =(action 'deny')
      ?>  ?&(incoming.p !=(stage.p 'friend'))
      =.  peers  (~(put by peers) who p(incoming %.n, stage 'denied', error ''))
      [~[friends-card (send who /deny (obj ~[['action' s+'friend-denied']]))] state]
    ?>  ?|(=(action 'request') incoming.p)
    =.  label  (safe-label (text j 'name'))
    =.  portrait  (safe-avatar (json-field j 'avatar'))
    =.  next  +(next)
    =.  p  p(name (safe-label (text j 'peerName')), avatar (safe-avatar (json-field j 'peerAvatar')), outgoing %.y, mode action, stage 'checking', error '', op next, at now.bowl)
    =.  peers  (~(put by peers) who p)
    =.  install-at
      ?~  install-at  ~
      ?:  (gth now.bowl (add u.install-at ~m20))  ~
      install-at
    =^  cards  state  work
    [(snoc cards friends-card) state]
  ?>  ?|(=(action 'friend-request') =(action 'friend-accepted') =(action 'friend-denied'))
  ?>  !=(src.bowl our.bowl)
  =/  who=@p  src.bowl
  ?>  ?|((~(has by peers) who) (lth ~(wyt by peers) 512))
  =/  p=contact  (contact-for who)
  ?:  =(action 'friend-denied')
    ?.  outgoing.p  [~ state]
    =.  peers  (~(put by peers) who p(stage 'denied', incoming %.n, error 'Friendship declined.'))
    [~[friends-card] state]
  =.  p  p(name (safe-label (text j 'name')), avatar (safe-avatar (json-field j 'avatar')))
  ?:  =(action 'friend-request')
    =.  peers  (~(put by peers) who p(incoming %.y, stage ?:(=(stage.p 'friend') 'friend' ?:(outgoing.p stage.p ''))))
    [~[friends-card] state]
  ?>  outgoing.p
  =.  peers  (~(put by peers) who p(incoming %.y))
  ::  The first Pals hey may have been nacked before their installation.
  ::  Replay our own authenticated gesture without removing their other tags.
  [~[[%pass /replay/[(scot %p who)] %agent [who %pals] %poke %pals-gesture !>([%hey ~])] friends-card] state]
++  watch
  |=  =path
  ^-  (quip card state-1)
  ?:  =(path /friends)
    ?>  =(src.bowl our.bowl)
    =^  cards  state  work
    [(snoc cards friends-card) state]
  ?:  =(path /slate)
    ?>  =(our.bowl coordinator)
    [~[shared-card] state]
  ?:  ?=([%presence @ ~] path)
    ?>  =((slav %p i.t.path) src.bowl)
    =/  p=contact  (contact-for src.bowl)
    ?>  ?|(=(src.bowl our.bowl) =(stage.p 'friend') ?&(outgoing.p incoming.p))
    [~[[%give %fact ~[path] %json !>(presence-json)]] state]
  [~ state]
++  agent
  |=  [=wire =sign:agent:gall]
  ^-  (quip card state-1)
  ?:  =(wire /lobby)
    ?.  ?=(%fact -.sign)  [~ state]
    =.  lobby  !<(json q.cage.sign)
    =.  sent-at  ~2000.1.1
    maintain-slate
  ?:  =(wire /slate)
    ?:  =(our.bowl coordinator)  [~ state]
    ?.  ?=(%fact -.sign)  [~ state]
    =/  data=json  !<(json q.cage.sign)
    =.  shared
      ?:  ?=(~ data)  ~
      `[(slav %p (text data 'host')) (text data 'room') (bo:dejs:format (json-field data 'ready')) (number data 'count') (number data 'round') (number data 'rounds') (add now.bowl ~m2)]
    [~[friends-card] state]
  ?:  ?=([%friend @ ~] wire)
    =/  who=@p  (slav %p i.t.wire)
    ?.  ?=(%fact -.sign)
      ?.  ?|(?=(%kick -.sign) ?&(?=(%watch-ack -.sign) ?=(^ p.sign)))  [~ state]
      =/  p=contact  (contact-for who)
      =.  peers  (~(put by peers) who p(probe (add now.bowl ?:((gth now.bowl (add at.p ~s20)) ~m1 ~s5))))
      [~[[%pass wire %agent [who %ursketch-social] %leave ~]] state]
    =/  data=json  !<(json q.cage.sign)
    =/  p=contact  (contact-for who)
    =.  peers  (~(put by peers) who p(name (safe-label (text data 'name')), avatar (safe-avatar (json-field data 'avatar')), presence data))
    [~[friends-card] state]
  ?:  =(wire /claim)
    =/  pending=?  ?=(^ claim-at)
    ?.  ?&(?=(%poke-ack -.sign) ?=(^ p.sign) pending)  [~ state]
    =.  destination  (obj ~[['nonce' s+(text destination 'nonce')] ['error' s+'The shared-room directory is unavailable. Please retry.']])
    =.  claim-at  ~
    [~[friends-card] state]
  ?:  =(wire /install)
    ?.  ?&(?=(%poke-ack -.sign) ?=(^ p.sign))  [~ state]
    =.  peers  (~(run by peers) |=(p=contact ?:(=(stage.p 'installing') p(stage 'error', error 'Pals could not install. Check Landscape and retry.') p)))
    =.  install-at  ~
    [~[friends-card] state]
  ?:  =(wire /create-slate)
    ?.  ?=(%poke-ack -.sign)  [~ state]
    ?~  p.sign  [~ state]
    =/  created=(unit @t)  hosting
    ?~  created  [~ state]
    =/  rid=@t  u.created
    =.  hosting  ~
    [~[(send coordinator /release (obj ~[['action' s+'slate-failed'] ['room' s+rid]]))] state]
  ?.  ?=([?(%pals %delivered) @ @ ~] wire)  [~ state]
  ?.  ?=(%poke-ack -.sign)  [~ state]
  =/  who=@p  (slav %p i.t.wire)
  =/  p=contact  (contact-for who)
  ?:  ?|(=(stage.p 'friend') =(stage.p 'denied'))  [~ state]
  ?.  =(op.p (slav %ud i.t.t.wire))  [~ state]
  ?^  p.sign
    =.  peers  (~(put by peers) who p(stage 'error', error 'Could not deliver the request. Check the connection and retry.'))
    [~[friends-card] state]
  ?:  =(%delivered i.wire)
    =.  peers  (~(put by peers) who p(stage ?:(=(mode.p 'accept') 'confirming' 'pending')))
    [~[friends-card] state]
  =.  peers  (~(put by peers) who p(stage 'delivering'))
  =/  payload=json  (obj ~[['action' s+?:(=(mode.p 'accept') 'friend-accepted' 'friend-request')] ['name' s+label] ['avatar' portrait]])
  [~[(send who /delivered/[(scot %p who)]/[(scot %ud op.p)] payload) friends-card] state]
++  claim
  |=  nonce=@t
  ^-  (quip card state-1)
  ?>  =(our.bowl coordinator)
  ?>  (lte (met 3 nonce) 80)
  ?>  ?|((~(has by waiters) src.bowl) (lth ~(wyt by waiters) 128))
  =.  waiters  (~(put by waiters) src.bowl nonce)
  =/  current=(unit shared-room)  shared
  ?^  current
    ?:  (gth until.u.current now.bowl)  deliver-slate
    =.  shared  ~
    (claim nonce)
  =/  suffix=@t  (crip (skip (trip (scot %ud (mug [src.bowl now.bowl eny.bowl]))) |=(c=@tD =(c '.'))))
  =/  rid=@t  (cat 3 'clean-slate-' suffix)
  =.  shared  `[src.bowl rid %.n 0 1 10 (add now.bowl ~m2)]
  [~[(send src.bowl /assign (obj ~[['action' s+'slate-assigned'] ['room' s+rid]])) shared-card friends-card] state]
++  deliver-slate
  ^-  (quip card state-1)
  ?~  shared  [~ state]
  ?.  ready.u.shared  [~[shared-card friends-card] state]
  =/  cards=(list card)
    %+  turn  ~(tap by waiters)
    |=  [who=@p nonce=@t]
    (send who /destination (obj ~[['action' s+'slate-destination'] ['nonce' s+nonce] ['host' s+(scot %p host.u.shared)] ['room' s+room.u.shared] ['error' s+'']]))
  =.  waiters  ~
  [(welp cards ~[shared-card friends-card]) state]
++  close-slate
  |=  issue=@t
  ^-  (quip card state-1)
  =.  shared  ~
  =/  cards=(list card)
    %+  turn  ~(tap by waiters)
    |=  [who=@p nonce=@t]
    (send who /destination (obj ~[['action' s+'slate-destination'] ['nonce' s+nonce] ['error' s+issue]]))
  =.  waiters  ~
  [(welp cards ~[shared-card friends-card]) state]
++  maintain-slate
  ^-  (quip card state-1)
  =|  cards=(list card)
  =/  expired=?  ?&(!=('' title) (lte presence-until now.bowl))
  =.  title  ?:(expired '' title)
  =.  cards  ?:(expired presence-cards cards)
  ?:  ?&(?=(^ shared) =(our.bowl coordinator) (lte until.u.shared now.bowl))
    (close-slate 'The shared room host is unavailable. Click A Clean Slate to retry.')
  =/  active-room=(unit @t)  hosting
  ?~  active-room  [cards state]
  ?>  ?=(%o -.lobby)
  =/  values=json  (~(gut by p.lobby) 'rooms' [%a ~])
  ?>  ?=(%a -.values)
  =/  matches=(list json)  (skim p.values |=(r=json =((text r 'id') u.active-room)))
  ?~  matches
    ?.  hosting-ready  [cards state]
    =/  rid=@t  u.active-room
    =.  hosting  ~
    [(snoc cards (send coordinator /release (obj ~[['action' s+'slate-release'] ['room' s+rid]]))) state]
  =.  hosting-ready  %.y
  ?:  (gth (add sent-at ~s20) now.bowl)  [cards state]
  =.  sent-at  now.bowl
  =/  r=json  i.matches
  [(snoc cards (send coordinator /heartbeat (obj ~[['action' s+'slate-heartbeat'] ['room' s+u.active-room] ['count' (json-field r 'count')] ['round' (json-field r 'round')] ['rounds' (json-field r 'rounds')]]))) state]
--
