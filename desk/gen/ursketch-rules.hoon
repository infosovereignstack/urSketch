/+  *ursketch-types, ursketch-game
:-  %say
|=  *
=/  now=@da  ~2026.10.25
=/  r=room  (fresh:ursketch-game 'Rules test' ~zod)
=.  r  r(players ~[[~zod 0 %.n] [~nec 0 %.n]])
?>  =((normalize:ursketch-game 'Ice Cream') (normalize:ursketch-game ' ICECREAM '))
=.  r  (choose:ursketch-game r now)
?>  ?&(?=(%choosing phase.r) =(3 (lent choices.r)) =(1 token.r))
?>  =(deadline.r (add now ~s15))
=/  r=room  r
=.  r  (advance:ursketch-game r deadline.r)
?>  ?&(?=(%drawing phase.r) !=('' answer.r) =(2 token.r))
?>  =(deadline.r (add now ~s135))
=/  finishing=room  (finish-window:ursketch-game r ~nec (add now ~s134))
?>  =(deadline.finishing (add now ~s154))
?>  ?=(%drawing phase.finishing)
?>  =(token.finishing token.r)
=/  crew=room  r(players ~[[~zod 0 %.n] [~nec 0 %.n] [~bud 0 %.n] [~wes 0 %.n]])
=.  crew  (finish-window:ursketch-game crew ~nec (add now ~s20))
=.  crew  (depart:ursketch-game crew ~nec (add now ~s21))
?>  =(1 solves.crew)
?>  ?=(~ (mole |.((hint:ursketch-game crew now))))
=.  crew  (finish-window:ursketch-game crew ~bud (add now ~s24))
?>  =(deadline.crew (add now ~s40))
?>  =((turn players.crew |=(p=player score.p)) ~[11 9 0])
=/  saved=room-v5
  ['Version five' ~zod ~[[~zod 10 %.n] [~nec 10 %.y] [~bud 0 %.n]] %drawing 2 7 (add now ~s120) 'cat' ~ ~ ~ 1 ~]
=/  upgraded=room  (migrate-v5:ursketch-game saved now)
?>  ?&(=(1 solves.upgraded) =(deadline.upgraded (add now ~s20)) =(1 hints.upgraded))
?>  (close-guess:ursketch-game 'stairway' 'staircase')
?>  (close-guess:ursketch-game 'stairs' 'staircase')
?>  (close-guess:ursketch-game 'elehpant' 'elephant')
?>  (close-guess:ursketch-game 'airplan' 'airplane')
?>  (close-guess:ursketch-game 'ct' 'cat')
?>  !(close-guess:ursketch-game 'a' 'airplane')
?>  !(close-guess:ursketch-game 'cat' 'cat')
?>  !(close-guess:ursketch-game 'potato' 'airplane')
=/  r=room  r
=.  r  (advance:ursketch-game r deadline.r)
?>  ?&(?=(%reveal phase.r) =(3 token.r))
=/  r=room  r
=.  r  (advance:ursketch-game r deadline.r)
?>  ?&(?=(%choosing phase.r) =(1 turn.r) =(~nec who:(head players.r)))
=/  r=room  r
=.  r
  |-  ^-  room
  ?:  ?=(%finished phase.r)  r
  $(r (advance:ursketch-game r deadline.r))
?>  =(9 turn.r)
?>  (levy players.r |=(p=player =(0 score.p)))
=/  scoring=room  (fresh:ursketch-game 'Scoring test' ~zod)
=.  scoring
  scoring(players ~[[~zod 0 %.n] [~nec 0 %.n] [~bud 0 %.n] [~wes 0 %.n] [~sev 0 %.n] [~per 0 %.n] [~sut 0 %.n] [~let 0 %.n] [~ful 0 %.n] [~pen 0 %.n] [~syt 0 %.n] [~dur 0 %.n]])
?>  (full:ursketch-game scoring(players (scag 10 players.scoring)))
?>  !(full:ursketch-game scoring(players (scag 9 players.scoring)))
=/  solvers=(list player)  (slag 1 players.scoring)
=.  scoring
  |-  ^-  room
  ?~  solvers  scoring
  $(scoring (award:ursketch-game scoring who.i.solvers), solvers t.solvers)
?>  =((turn players.scoring |=(p=player score.p)) ~[20 10 9 8 7 6 5 5 5 5 5 5])
=/  legacy=old-room
  ['Saved room' ~zod ~[[~zod 12 %.n] [~nec 9 %.n]] %drawing 2 7 (add now ~s80) 'cat' ~ ~[['#883e31' 4 1 2 3 4]] ~]
=/  migrated=room  (migrate-room:ursketch-game legacy)
?>  ?&  =(12 score:(head players.migrated))
        =('cat' answer.migrated)
        =(7 token.migrated)
        =('#883e31' color:(head lines.migrated))
        =(%stroke kind:(head lines.migrated))
        =(100 opacity:(head lines.migrated))
    ==
=/  lone=room  (depart:ursketch-game migrated ~nec now)
?>  ?&(?=(%waiting phase.lone) =(1 (lent players.lone)) =(~zod owner.lone))
=/  empty=room  (depart:ursketch-game lone ~zod now)
?>  ?=(~ players.empty)
=/  reassigned=room  (depart:ursketch-game migrated ~zod now)
?>  ?&(?=(%waiting phase.reassigned) =(~nec owner.reassigned))
[%noun 'PASS: ten total rounds, close guesses, 120/20 timers, departure-safe solve order, saved rooms and scoring']
