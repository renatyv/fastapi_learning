ALTER TABLE blog_user
DROP COLUMN password_hash,
DROP COLUMN email,
DROP COLUMN username,
ADD CONSTRAINT unique_name_surname UNIQUE (name, surname);