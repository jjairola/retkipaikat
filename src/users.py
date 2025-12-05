import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
import db


class UserError(Exception):
    pass


class UserAlreadyExists(Exception):
    pass


def get_user(user_id):
    sql = """
    SELECT u.id, u.username
    FROM users u
    WHERE u.id = ?
    """
    result = db.query(sql, [user_id])
    return result[0] if result else None


def add_user(username, password):
    try:
        password_hash = generate_password_hash(password, method="pbkdf2:sha256")
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError as error:
        raise UserAlreadyExists(error) from error
    except Exception as error:
        raise UserError(error) from error


def check_login(username, password):
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if not result:
        return None

    user_id = result[0]["id"]
    password_hash = result[0]["password_hash"]
    if check_password_hash(password_hash, password):
        return user_id
    else:
        return None
