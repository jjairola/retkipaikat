CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE destinations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    municipality TEXT,
    user_id INTEGER REFERENCES users
);


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

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    destination_id INTEGER REFERENCES destinations,
    user_id INTEGER REFERENCES users,
    comment TEXT,
    rating INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);