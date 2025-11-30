CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE
    password_hash TEXT
);

CREATE TABLE destinations (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    municipality TEXT,
    user_id INTEGER REFERENCES users
);

CREATE TABLE classifications (
    id INTEGER PRIMARY KEY,
    name TEXT
);

CREATE TABLE destination_classifications (
    id INTEGER PRIMARY KEY,
    destination_id INTEGER REFERENCES destinations,
    classification_id INTEGER REFERENCES classifications,
    UNIQUE(destination_id, classification_id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    destination_id INTEGER REFERENCES destinations,
    user_id INTEGER REFERENCES users,
    comment TEXT,
    rating INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);