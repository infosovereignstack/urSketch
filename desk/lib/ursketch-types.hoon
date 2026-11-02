|%
+$  player  [who=@p score=@ud solved=?]
+$  old-line  [color=@t width=@ud x1=@ud y1=@ud x2=@ud y2=@ud]
+$  draw-kind  ?(%stroke %brush %eraser %spray %rectangle %ellipse %fill %clear)
+$  line  [color=@t width=@ud x1=@ud y1=@ud x2=@ud y2=@ud kind=draw-kind opacity=@ud filled=? seed=@ud id=@t]
+$  message-v6  [who=@t text=@t kind=@t]
+$  message  [who=@t text=@t kind=@t audience=(unit @p) actor=(unit @p)]
+$  avatar  [body=@t face=@t hat=@t]
+$  solve  [who=@p label=@t points=@ud]
+$  room
  $:  title=@t
      owner=@p
      players=(list player)
      phase=?(%waiting %choosing %drawing %reveal %finished)
      turn=@ud
      token=@ud
      deadline=@da
      answer=@t
      choices=(list @t)
      lines=(list line)
      chat=(list message)
      hints=@ud
      revealed=(set @ud)
      solves=@ud
      solvers=(list solve)
      outcome=(unit [label=@t score=@ud])
      started=?
  ==
+$  room-v8
  $:  title=@t
      owner=@p
      players=(list player)
      phase=?(%waiting %choosing %drawing %reveal %finished)
      turn=@ud
      token=@ud
      deadline=@da
      answer=@t
      choices=(list @t)
      lines=(list line)
      chat=(list message)
      hints=@ud
      revealed=(set @ud)
      solves=@ud
      solvers=(list solve)
      outcome=(unit [label=@t score=@ud])
  ==
+$  room-v7
  $:  title=@t
      owner=@p
      players=(list player)
      phase=?(%waiting %choosing %drawing %reveal %finished)
      turn=@ud
      token=@ud
      deadline=@da
      answer=@t
      choices=(list @t)
      lines=(list line)
      chat=(list message)
      hints=@ud
      revealed=(set @ud)
      solves=@ud
      solvers=(list solve)
  ==
+$  room-v6
  $:  title=@t
      owner=@p
      players=(list player)
      phase=?(%waiting %choosing %drawing %reveal %finished)
      turn=@ud
      token=@ud
      deadline=@da
      answer=@t
      choices=(list @t)
      lines=(list line)
      chat=(list message-v6)
      hints=@ud
      revealed=(set @ud)
      solves=@ud
  ==
+$  room-v5
  $:  title=@t
      owner=@p
      players=(list player)
      phase=?(%waiting %choosing %drawing %reveal %finished)
      turn=@ud
      token=@ud
      deadline=@da
      answer=@t
      choices=(list @t)
      lines=(list line)
      chat=(list message-v6)
      hints=@ud
      revealed=(set @ud)
  ==
+$  room-v3
  $:  title=@t
      owner=@p
      players=(list player)
      phase=?(%waiting %choosing %drawing %reveal %finished)
      turn=@ud
      token=@ud
      deadline=@da
      answer=@t
      choices=(list @t)
      lines=(list line)
      chat=(list message-v6)
  ==
+$  old-room
  $:  title=@t
      owner=@p
      players=(list player)
      phase=?(%waiting %choosing %drawing %reveal %finished)
      turn=@ud
      token=@ud
      deadline=@da
      answer=@t
      choices=(list @t)
      lines=(list old-line)
      chat=(list message-v6)
  ==
+$  lease-key  [rid=@t who=@p]
--
