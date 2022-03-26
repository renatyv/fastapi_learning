-- depends: blog_003_users_constraint
CREATE TABLE blog_post(
    post_id SERIAL,
    user_id INT,
    title VARCHAR(200),
    body VARCHAR(100000),
    PRIMARY KEY (post_id),
    CONSTRAINT fk_user_id
        FOREIGN KEY(user_id)
            REFERENCES blog_user(user_id)
            ON DELETE CASCADE
);