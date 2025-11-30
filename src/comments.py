import db


def add_comment(destination_id, user_id, comment, rating):
    sql = """INSERT INTO comments (destination_id, user_id, comment, rating)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [destination_id, user_id, comment, rating])


def get_comments(destination_id):
    sql = """SELECT c.created_at, c.comment, c.rating, u.id user_id, u.username
             FROM comments c
             LEFT JOIN users u ON c.user_id = u.id
             WHERE c.destination_id = ?
             ORDER BY c.id DESC"""
    return db.query(sql, [destination_id])


def get_comments_by_user(user_id):
    sql = """SELECT c.comment, c.rating, d.name as destination_name, d.id as destination_id
             FROM comments c
             JOIN destinations d ON c.destination_id = d.id
             WHERE c.user_id = ?
             ORDER BY c.id DESC"""
    return db.query(sql, [user_id])
