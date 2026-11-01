/+  *ursketch-types
|%
++  words
  ^-  (list @t)
  ~['airplane' 'anchor' 'apple' 'astronaut' 'avocado' 'backpack' 'banana' 'basketball' 'bathtub' 'beach' 'bear' 'bicycle' 'bird' 'birthday' 'book' 'bridge' 'butterfly' 'cactus' 'camera' 'campfire' 'castle' 'cat' 'caterpillar' 'cheese' 'cherry' 'clock' 'cloud' 'compass' 'crab' 'crown' 'diamond' 'dinosaur' 'dog' 'dolphin' 'donut' 'dragon' 'drum' 'elephant' 'envelope' 'eye' 'fireworks' 'fish' 'flower' 'football' 'frog' 'giraffe' 'guitar' 'hamburger' 'hammer' 'helicopter' 'house' 'ice cream' 'island' 'jellyfish' 'key' 'kite' 'ladder' 'lighthouse' 'lightning' 'lion' 'lobster' 'lollipop' 'moon' 'mountain' 'mushroom' 'octopus' 'owl' 'panda' 'parachute' 'penguin' 'piano' 'pineapple' 'pirate' 'pizza' 'planet' 'popcorn' 'rainbow' 'robot' 'rocket' 'sandcastle' 'scissors' 'shark' 'skateboard' 'snail' 'snowman' 'spider' 'sunflower' 'sword' 'telescope' 'tornado' 'train' 'tree' 'turtle' 'umbrella' 'unicorn' 'volcano' 'watermelon' 'whale' 'windmill' 'wizard']
++  migrate-room
  |=  r=old-room
  ^-  room
  :*  title.r
      owner.r
      players.r
      phase.r
      turn.r
      token.r
      deadline.r
      answer.r
      choices.r
      (turn lines.r |=(l=old-line [color.l width.l x1.l y1.l x2.l y2.l %stroke 100 %.n 0 '']))
      (upgrade-chat chat.r)
      0
      ~
      0
      ~
  ==
++  migrate-v3
  |=  r=room-v3
  ^-  room
  [title.r owner.r players.r phase.r turn.r token.r deadline.r answer.r choices.r lines.r (upgrade-chat chat.r) 0 ~ 0 ~]
++  migrate-v5
  |=  [r=room-v5 now=@da]
  ^-  room
  =/  solves=@ud  (lent (skim players.r |=(p=player solved.p)))
  =/  finishing=?  ?&(?=(%drawing phase.r) (gth solves 0))
  =/  deadline=@da  ?:(finishing (min deadline.r (add now ~s20)) deadline.r)
  [title.r owner.r players.r phase.r turn.r token.r deadline answer.r choices.r lines.r (upgrade-chat chat.r) hints.r revealed.r solves ~]
++  upgrade-chat
  |=  old=(list message-v6)
  ^-  (list message)
  (turn old |=([who=@t text=@t kind=@t] [who text kind ~ ~]))
++  migrate-v6
  |=  r=room-v6
  ^-  room
  =/  records=(list solve)
    (turn (skim players.r |=(p=player solved.p)) |=(p=player [who.p (scot %p who.p) 0]))
  [title.r owner.r players.r phase.r turn.r token.r deadline.r answer.r choices.r lines.r (upgrade-chat chat.r) hints.r revealed.r solves.r records]
++  hint
  |=  [r=room now=@da]
  ^-  room
  ?>  ?&(?=(%drawing phase.r) (lth hints.r 3))
  ?>  ?&(=(solves.r 0) !(lien players.r |=(p=player solved.p)))
  =.  r  r(hints +(hints.r))
  ?:  =(hints.r 1)  r
  =/  letters=(list @tD)  (trip answer.r)
  =/  available=(list @ud)
    %+  skim  (gulf 0 (dec (lent letters)))
    |=  i=@ud
    ?&(!=((snag i letters) ' ') !(~(has in revealed.r) i))
  ?~  available  r
  =/  available=(list @ud)  available
  =/  pick=@ud  (snag (mod (mug [now token.r hints.r revealed.r]) (lent available)) available)
  r(revealed (~(put in revealed.r) pick))
++  hint-mask
  |=  r=room
  ^-  @t
  ?.  ?&(?=(%drawing phase.r) (gth hints.r 0))  ''
  =/  letters=(list @tD)  (trip answer.r)
  %-  crip
  %+  turn  (gulf 0 (dec (lent letters)))
  |=  i=@ud
  =/  c=@tD  (snag i letters)
  ?:  ?|(=(c ' ') (~(has in revealed.r) i))  c
  '_'
++  depart
  |=  [r=room who=@p now=@da]
  ^-  room
  =/  artist=?  ?&(?=(^ players.r) =(who who.i.players.r))
  =/  remaining=(list player)  (skip players.r |=(p=player =(who who.p)))
  ?~  remaining
    r(players ~, phase %waiting, deadline ~2000.1.1, token +(token.r), lines ~, answer '', choices ~, hints 0, revealed ~, solves 0)
  =.  r  r(players remaining, owner ?:(=(who owner.r) who.i.remaining owner.r))
  ?:  (lth (lent remaining) 2)
    r(phase %waiting, deadline ~2000.1.1, token +(token.r), answer '', choices ~, hints 0, revealed ~, solves 0)
  ?:  ?&(artist ?|(?=(%choosing phase.r) ?=(%drawing phase.r) ?=(%reveal phase.r)))
    ?:  (gte +(turn.r) 10)
      r(phase %finished, deadline ~2000.1.1, token +(token.r))
    (choose r(turn +(turn.r)) now)
  r
++  fresh
  |=  [title=@t owner=@p]
  ^-  room
  [title owner ~[[owner 0 %.n]] %waiting 0 0 ~2000.1.1 '' ~ ~ ~ 0 ~ 0 ~]
++  log
  |=  [r=room who=@t text=@t kind=@t audience=(unit @p) actor=(unit @p)]
  ^-  room
  =/  logs=(list message)  [[who text kind audience actor] chat.r]
  r(chat (scag 160 logs))
++  say
  |=  [r=room who=@t text=@t kind=@t]
  ^-  room
  (log r who text kind ~ ~)
++  whisper
  |=  [r=room viewer=@p text=@t kind=@t]
  ^-  room
  (log r '' text kind `viewer ~)
++  all-solved
  |=  r=room
  ^-  ?
  ?&(?=(%drawing phase.r) (gth solves.r 0) (gth (lent players.r) 1) (levy (slag 1 players.r) |=(p=player solved.p)))
++  full
  |=  r=room
  ^-  ?
  (gte (lent players.r) 10)
++  member
  |=  [r=room who=@p]
  ^-  ?
  (lien players.r |=(p=player =(who who.p)))
++  normalize
  |=  text=@t
  ^-  @t
  (crip (skip (cuss (trip text)) |=(c=@tD =(c ' '))))
++  edit-distance
  |=  [left=tape right=tape]
  ^-  @ud
  =/  n=@ud  (lent left)
  =/  m=@ud  (lent right)
  =/  i=@ud  1
  =/  previous=(list @ud)  (gulf 0 m)
  =/  older=(list @ud)  previous
  |-  ^-  @ud
  ?:  (gth i n)  (snag m previous)
  =/  next=(list @ud)
    =/  j=@ud  1
    =/  row=(list @ud)  ~[i]
    |-  ^-  (list @ud)
    ?:  (gth j m)  (flop row)
    =/  cost=@ud  ?:(=((snag (dec i) left) (snag (dec j) right)) 0 1)
    =/  value=@ud
      (min (add cost (snag (dec j) previous)) (min +((snag j previous)) +((snag 0 row))))
    =.  value
      ?:  ?&  (gth i 1)
              (gth j 1)
              =((snag (dec i) left) (snag (sub j 2) right))
              =((snag (sub i 2) left) (snag (dec j) right))
          ==
        (min value +((snag (sub j 2) older)))
      value
    $(j +(j), row [value row])
  $(i +(i), older previous, previous next)
++  close-guess
  |=  [guess=@t answer=@t]
  ^-  ?
  =/  a=tape  (trip (normalize guess))
  =/  b=tape  (trip (normalize answer))
  ?:  =(a b)  %.n
  =/  n=@ud  (lent a)
  =/  m=@ud  (lent b)
  ?.  ?&((gte m 3) (gte n 2))  %.n
  =/  large=@ud  (max n m)
  =/  small=@ud  (min n m)
  =/  allowed=@ud  (max 1 (div large 4))
  ?:  ?&((lte (sub large small) allowed) (lte (edit-distance a b) allowed))  %.y
  =/  span=@ud  (max 3 (max (div +(large) 2) (div (add (mul small 6) 9) 10)))
  ?:  (gth span small)  %.n
  =/  short=tape  ?:(=(small n) a b)
  =/  long=tape  ?:(=(small n) b a)
  %+  lien  (gulf 0 (sub small span))
  |=  offset=@ud
  ?=(^ (find (scag span (slag offset short)) long))
++  finish-window
  |=  [r=room solver=@p now=@da]
  ^-  room
  =/  first=?  =(solves.r 0)
  =.  r  (award r solver)
  ?:(first r(deadline (add now ~s20)) r)
++  guess-points
  |=  previous=@ud
  ^-  @ud
  (sub 10 (min 5 previous))
++  drawer-points
  |=  [previous=@ud hints=@ud]
  ^-  @ud
  ?:(=(0 previous) ?:(=(hints 0) 10 (sub 6 (min hints 3))) 1)
++  award
  |=  [r=room solver=@p]
  ^-  room
  =/  previous=@ud  solves.r
  =/  artist=@p  who:(head players.r)
  %=  r
    solves  +(previous)
    players
      %+  turn  players.r
      |=  p=player
      ?:  =(who.p solver)
        p(score (add score.p (guess-points previous)), solved %.y)
      ?:  =(who.p artist)
        p(score (add score.p (drawer-points previous hints.r)))
      p
  ==
++  solver-names
  |=  records=(list solve)
  ^-  @t
  ?~  records  ''
  ?~  t.records  label.i.records
  (rap 3 ~[label.i.records ', ' $(records t.records)])
++  result-text
  |=  [r=room artist=@t reason=@t]
  ^-  @t
  =/  ending=@t  (rap 3 ~[artist '\27s word: "' answer.r '"'])
  ?:  =(reason 'all')
    (rap 3 ~['All ' (scot %ud solves.r) ' players found ' ending])
  ?:  =(solves.r 0)
    (cat 3 ?:(=(reason 'time') 'Time\27s up! Nobody found ' 'Round ended! Nobody found ') ending)
  (rap 3 ~[?:(=(reason 'time') 'Time has lapsed since the first correct guess. ' 'Round ended. ') (scot %ud solves.r) ' players (' (solver-names solvers.r) ') found ' ending])
++  choose
  |=  [r=room now=@da]
  ^-  room
  =/  seed=@ud  (mod (mug [now token.r turn.r]) (lent words))
  (begin r(players (turn players.r |=(p=player p(solved %.n)))) (snag seed words) now)
++  begin
  |=  [r=room word=@t now=@da]
  ^-  room
  r(phase %drawing, answer word, choices ~, lines ~, token +(token.r), deadline (add now ~s120), hints 0, revealed ~, solves 0, solvers ~)
++  reveal
  |=  [r=room now=@da]
  ^-  room
  (advance r now)
++  advance
  |=  [r=room now=@da]
  ^-  room
  ?:  ?=(%choosing phase.r)  (choose r now)
  ?:  (gte +(turn.r) 10)
    r(phase %finished, deadline ~2000.1.1, token +(token.r))
  (choose r(turn +(turn.r), players (welp (slag 1 players.r) (scag 1 players.r))) now)
--
