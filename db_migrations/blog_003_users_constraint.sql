-- depends: blog_002_add_initial_users
ALTER TABLE blog_user
ADD CONSTRAINT unique_name_surname UNIQUE (name,surname)