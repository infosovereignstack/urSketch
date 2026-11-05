/+  *ursketch-types, ursketch-game
:-  %say
|=  *
=/  now=@da  ~2026.11.4
=/  r=room  (fresh:ursketch-game 'History' ~zod)
=.  r  r(players ~[[~zod 0 %.n] [~nec 0 %.n]])
=/  legacy=room-v10
  [title.r owner.r players.r %drawing 3 10 now 'apple' ~ ~ chat.r 0 ~ 0 ~ ~ %.y]
=/  migrated=room  (migrate-v10:ursketch-game legacy)
?>  ?&(=(recent.migrated ~['apple']) =(answer.migrated 'apple') =(players.migrated players.r) started.migrated)
=/  picked=room  (choose:ursketch-game migrated now)
?>  !=(answer.picked 'apple')
:: A deliberately full exclusion list cannot be bypassed by a random seed.
=/  used=(list @t)  (scag 100 words:ursketch-game)
=/  excluded=room  (choose:ursketch-game r(recent used) now)
?>  !(lien used |=(w=@t =(w answer.excluded)))
:: One eligible word must always be selected, even with every other word barred.
=/  only=room  (choose:ursketch-game r(recent (slag 1 words:ursketch-game)) now)
?>  =(answer.only (head words:ursketch-game))
=/  i=@ud  0
|-  ^-  (pair term @t)
?:  =(i 2.000)
  [%noun 'PASS: 2000 native rounds, last-100 exclusion, bounded history, game boundaries, serialized restoration, old-room migration and one-candidate selection']
=/  before=(list @t)  recent.r
=/  next=room
  ?:  =(0 (mod i 10))  (new-game:ursketch-game r now)
  (advance:ursketch-game r now)
?>  ?=(%drawing phase.next)
?>  !(lien before |=(w=@t =(w answer.next)))
=/  expected=(list @t)  [answer.next before]
?>  =(recent.next (scag 100 expected))
?>  (lte (lent recent.next) 100)
=/  unique=(list @t)  ~(tap in (silt recent.next))
?>  =((lent recent.next) (lent unique))
:: Same noun persistence used for saved state; the full room must survive.
=/  saved=vase  !>(next)
=/  restored=room  !<(room [p.saved (cue (jam q.saved))])
?>  =(restored next)
$(i +(i), r restored)
