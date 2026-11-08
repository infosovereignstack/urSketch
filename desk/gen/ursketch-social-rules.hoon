/+  *ursketch-types, ursketch-game
:-  %say
|=  *
=/  now=@da  ~2026.11.8
=/  r=room  (fresh:ursketch-game 'Capacity' ~zod)
=/  next=@p  ~nec
=.  r
  |-  ^-  room
  ?:  =(next 25)  r
  $(r (rejoin:ursketch-game r next), next (add next 1))
?>  ?&((full:ursketch-game r) =(25 (lent players.r)) =(25 rounds.r))
=.  r  (new-game:ursketch-game r now)
?>  ?&(?=(%drawing phase.r) =(25 rounds.r))
=/  smaller=room  (depart:ursketch-game r ~nec now)
?>  ?&(!(full:ursketch-game smaller) =(25 rounds.smaller))
=/  returning=room  (rejoin:ursketch-game smaller ~nec)
?>  ?&((full:ursketch-game returning) =(25 rounds.returning) =(order.r order.returning))
=/  final=room  (advance:ursketch-game r(turn 24) now)
?>  ?=(%finished phase.final)
=/  joined=room  (rejoin:ursketch-game final(players (slag 1 players.final)) (add 100 0))
?>  =(25 rounds.joined)
=/  reduced=room  (new-game:ursketch-game final(players (slag 20 players.final)) now)
?>  ?&(?=(%drawing phase.reduced) =(10 rounds.reduced))
=/  grown=room  (rejoin:ursketch-game reduced (add 100 0))
?>  =(10 rounds.grown)
=/  legacy=room-v12
  [title.r owner.r players.r phase.r turn.r token.r deadline.r answer.r choices.r lines.r chat.r hints.r revealed.r solves.r solvers.r outcome.r started.r recent.r settings.r absent.r order.r finish-clock.r artist.r]
=/  upgraded=room  (upgrade-v12:ursketch-game legacy)
?>  ?&((full:ursketch-game upgraded) =(25 rounds.upgraded) =(answer.r answer.upgraded) =(players.r players.upgraded) =(recent.r recent.upgraded) =(settings.r settings.upgraded))
[%noun 'PASS: 25-player capacity, peak rounds survive departures and rejoins, 25-round finale, next-game minimum reset and lossless v12 upgrade']
