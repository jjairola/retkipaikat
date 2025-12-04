CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_users_username
    ON users(username);

CREATE TABLE destinations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    user_id INTEGER REFERENCES users
);


CREATE TABLE ratings_cache (
    destination_id INTEGER PRIMARY KEY REFERENCES destinations
        ON DELETE CASCADE,
    average_rating REAL
);

CREATE INDEX idx_ratings_cache_avgerage
    ON ratings_cache(average_rating DESC);


CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);


CREATE TABLE destination_classes (
    id INTEGER PRIMARY KEY,
    destination_id INTEGER REFERENCES destinations,
    title TEXT,
    value TEXT
);

CREATE INDEX IF NOT EXISTS idx_destination_classes_destination_id
    ON destination_classes(destination_id);


CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    destination_id INTEGER REFERENCES destinations,
    user_id INTEGER REFERENCES users,
    comment TEXT,
    rating INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_comments_destination
    ON comments(destination_id);