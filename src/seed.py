import random
import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM destinations")
db.execute("DELETE FROM comments")
db.execute("DELETE FROM destination_classes")

USER_COUNT = 50000
DESTINATION_COUNT = 100000
COMMENT_COUNT = 1000000

classes = db.execute("SELECT title, value FROM classes").fetchall()
type_classes = [{"title": c[0], "value": c[1]} for c in classes if c[0] == "Tyyppi"]
muncipality_classes = [
    {"title": c[0], "value": c[1]} for c in classes if c[0] == "Paikkakunta"
]
difficulty_classes = [
    {"title": c[0], "value": c[1]} for c in classes if c[0] == "Vaikeusaste"
]

print("Users")
for i in range(1, USER_COUNT + 1):
    db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        ["user" + str(i), "hash"],
    )

print("Destinations")
for i in range(1, DESTINATION_COUNT + 1):
    user_id = random.randint(1, USER_COUNT)
    result = db.execute(
        "INSERT INTO destinations (name, user_id) VALUES (?, ?)",
        ["destinations" + str(i), user_id],
    )

    destination_id = result.lastrowid

    muncipality = random.choice(muncipality_classes)
    db.execute(
        """INSERT INTO destination_classes (destination_id, title, value)
                  VALUES (?, ?, ?)""",
        [destination_id, muncipality["title"], muncipality["value"]],
    )

    type_class = random.choice(type_classes)
    db.execute(
        """INSERT INTO destination_classes (destination_id, title, value)
                  VALUES (?, ?, ?)""",
        [destination_id, type_class["title"], type_class["value"]],
    )

    difficulty = random.choice(difficulty_classes)
    db.execute(
        """INSERT INTO destination_classes (destination_id, title, value)
                  VALUES (?, ?, ?)""",
        [destination_id, difficulty["title"], difficulty["value"]],
    )

print("Comments")
for i in range(1, COMMENT_COUNT + 1):
    user_id = random.randint(1, USER_COUNT)
    destination_id = random.randint(1, DESTINATION_COUNT)
    rating = random.randint(1, 5)
    db.execute(
        """INSERT INTO comments (comment, user_id, destination_id, rating)
                  VALUES (?, ?, ?, ?)""",
        ["comment" + str(i), user_id, destination_id, rating],
    )

db.commit()
db.close()
