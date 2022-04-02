-- depends: blog_003_users_constraint
ALTER TABLE blog_user
DROP CONSTRAINT unique_name_surname;

ALTER TABLE blog_user
ADD COLUMN password_hash VARCHAR(300),
ADD COLUMN email VARCHAR(254),
ADD COLUMN username VARCHAR(100) UNIQUE;

-- provide unique usernames for NULL values
UPDATE blog_user
SET username=CAST(user_id AS VARCHAR)
WHERE username IS NULL;

-- use hash of 'user_id'+'username' as a password for NULL values
UPDATE blog_user
SET password_hash=crypt(CONCAT(CAST(user_id AS VARCHAR), username),gen_salt('md5'))
WHERE password_hash IS NULL;

-- make username unique
ALTER TABLE blog_user
ALTER COLUMN username SET NOT NULL,
ALTER COLUMN password_hash SET NOT NULL,
ADD CONSTRAINT unique_username UNIQUE (username);