/+  *ursketch-types, ursketch-game
:-  %say
|=  *
=/  now=@da  ~2026.11.1
=/  r=room  (fresh:ursketch-game 'Rules' ~zod)
=.  r  r(players ~[[~zod 0 %.n] [~nec 0 %.n] [~bud 0 %.n]])
=.  r  (choose:ursketch-game r now)
?>  ?&(?=(%drawing phase.r) !=('' answer.r) =(~ choices.r) =(deadline.r (add now ~s120)))
=/  word=@t  answer.r
=/  late=room  (finish-window:ursketch-game r ~nec (add now ~s119))
?>  =(deadline.late (add now ~s139))
?>  !(all-solved:ursketch-game late)
=.  late  (finish-window:ursketch-game late ~bud (add now ~s120))
?>  ?&((all-solved:ursketch-game late) =(deadline.late (add now ~s139)))
=/  empty=room  (begin:ursketch-game r 'cat' now)
?>  =((result-text:ursketch-game empty 'Alice' 'time') 'Time\27s up! Nobody found Alice\27s word: "cat"')
=/  ordered=room  empty(solves 2, solvers ~[[~nec 'Zoe' 10] [~bud 'Bob' 9]])
?>  =((result-text:ursketch-game ordered 'Alice' 'time') 'Time has lapsed since the first correct guess. 2 players (Zoe, Bob) found Alice\27s word: "cat"')
?>  =((result-text:ursketch-game ordered 'Alice' 'all') 'All 2 players found Alice\27s word: "cat"')
=/  private=room  (whisper:ursketch-game empty ~nec 'secret' 'found-word')
=/  pm=message  (head chat.private)
?>  =(~nec (need audience.pm))
=/  saved=room-v6
  ['Saved' ~zod ~[[~zod 10 %.n] [~nec 10 %.y] [~bud 0 %.n]] %drawing 2 7 (add now ~s120) 'cat' ~ ~[['#883e31' 4 1 2 3 4 %stroke 100 %.n 0 'saved']] ~[['Room' 'old message' 'system']] 1 ~ 1]
=/  upgraded=room  (migrate-v6:ursketch-game saved)
=/  old-message=message  (head chat.upgraded)
?>  ?&  =('saved' id:(head lines.upgraded))
        =(10 score:(head players.upgraded))
        =(1 solves.upgraded)
        =(1 (lent solvers.upgraded))
        ?=(~ audience.old-message)
    ==
=/  final=room  r(turn 9, lines ~[['#883e31' 4 1 2 3 4 %stroke 100 %.n 0 'last']])
=.  final  (advance:ursketch-game final now)
?>  ?&(?=(%finished phase.final) =('last' id:(head lines.final)))
=/  next=room  (advance:ursketch-game r now)
?>  ?&(?=(%drawing phase.next) =(1 turn.next) =(~nec who:(head players.next)) ?=(~ lines.next) =(deadline.next (add now ~s120)))
=/  rounds=@ud  1
=.  rounds
  =/  current=room  r
  |-  ^-  @ud
  ?:  ?=(%finished phase.current)  rounds
  $(current (advance:ursketch-game current now), rounds ?:(=(turn.current 9) rounds +(rounds)))
?>  =(10 rounds)
?>  (close-guess:ursketch-game 'elehpant' 'elephant')
?>  !(close-guess:ursketch-game 'cat' 'cat')
[%noun 'PASS: immediate assigned words, 120/20 timers, all-solved detection, exact result text/order, private logs, preserved final canvas, ten rounds and state-6 migration']
