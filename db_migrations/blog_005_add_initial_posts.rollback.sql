DELETE FROM blog_post
WHERE
      (user_id, title, body) = (1, 'Migrations with yoyo', 'Actually work')
   OR (user_id, title, body) = (2, 'Order #1', 'Invade ukraine!')
   OR (user_id, title, body) = (2, 'Order #2', 'Wtf is going on')
   OR (user_id, title, body) = (1, 'Post #2', 'Pha-ha post very long bu useless text');