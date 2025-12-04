import random
import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM destinations")
db.execute("DELETE FROM comments")

user_count = 1000
destination_count = 10**5
comment_count = 10**6

print("Users")
for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
               ["user" + str(i), "hash"])

print("Destinations")
for i in range(1, destination_count + 1):
    user_id = random.randint(1, user_count)
    db.execute("INSERT INTO destinations (name, user_id) VALUES (?, ?)",
               ["destinations" + str(i), user_id])

print("Comments")
for i in range(1, comment_count + 1):
    user_id = random.randint(1, user_count)
    destination_id = random.randint(1, destination_count)
    rating = random.randint(1,5)
    db.execute("""INSERT INTO comments (comment, user_id, destination_id, rating)
                  VALUES (?, ?, ?, ?)""",
               ["comment" + str(i), user_id, destination_id, rating])

db.commit()
db.close()