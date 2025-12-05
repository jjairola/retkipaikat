import random
import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM destinations")
db.execute("DELETE FROM comments")

user_count = 1000
destination_count = 10**5
comment_count = 10**6

classes = db.execute("SELECT title, value FROM classes").fetchall()
types = [{"title": c[0], "value": c[1]} for c in classes if c[0] == "Tyyppi"]
muncipalities = [
    {"title": c[0], "value": c[1]} for c in classes if c[0] == "Paikkakunta"
]
difficulties = [
    {"title": c[0], "value": c[1]} for c in classes if c[0] == "Vaikeusaste"
]

print("Users")
for i in range(1, user_count + 1):
    db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        ["user" + str(i), "hash"],
    )

print("Destinations")
for i in range(1, destination_count + 1):
    user_id = random.randint(1, user_count)
    result = db.execute(
        "INSERT INTO destinations (name, user_id) VALUES (?, ?)",
        ["destinations" + str(i), user_id],
    )

    destination_id = result.lastrowid

    muncipality = random.choice(muncipalities)
    db.execute(
        """INSERT INTO destination_classes (destination_id, title, value)
                  VALUES (?, ?, ?)""",
        [destination_id, muncipality["title"], muncipality["value"]],
    )

    type = random.choice(types)
    db.execute(
        """INSERT INTO destination_classes (destination_id, title, value)
                  VALUES (?, ?, ?)""",
        [destination_id, type["title"], type["value"]],
    )

    difficulty = random.choice(difficulties)
    db.execute(
        """INSERT INTO destination_classes (destination_id, title, value)
                  VALUES (?, ?, ?)""",
        [destination_id, difficulty["title"], difficulty["value"]],
    )

print("Comments")
for i in range(1, comment_count + 1):
    user_id = random.randint(1, user_count)
    destination_id = random.randint(1, destination_count)
    rating = random.randint(1, 5)
    db.execute(
        """INSERT INTO comments (comment, user_id, destination_id, rating)
                  VALUES (?, ?, ?, ?)""",
        ["comment" + str(i), user_id, destination_id, rating],
    )

db.commit()
db.close()
