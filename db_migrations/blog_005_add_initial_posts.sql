-- depends: blog_004_create_post_table
INSERT INTO blog_post(user_id, title, body)
VALUES (1, 'Migrations with yoyo', 'Actually work'),
       (2, 'Order #1', 'Invade ukraine!'),
       (2, 'Order #2', 'Wtf is going on'),
       (1, 'Post #2', 'Pha-ha post very long bu useless text');