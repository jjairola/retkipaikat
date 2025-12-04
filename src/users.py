from werkzeug.security import check_password_hash, generate_password_hash
import db


class UserError(Exception):
    pass


def get_user(user_id):
    sql = """
    SELECT u.id, u.username, ui.image IS NOT NULL AS has_image
    FROM users u
    LEFT JOIN user_images ui ON u.id = ui.user_id
    WHERE u.id = ?
    """
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_image(user_id):
    sql = "SELECT image FROM user_images WHERE user_id = ?"
    result = db.query(sql, [user_id])
    return result[0]["image"] if result else None

def update_image(user_id, image):
    # Replace changes primary key, but it doesn't matter here.
    sql = "INSERT OR REPLACE INTO user_images (user_id, image) VALUES (?, ?)"
    db.execute(sql, [user_id, image])

def add_user(username, password):
    try:
        password_hash = generate_password_hash(password, method="pbkdf2:sha256")
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except Exception as e:
        raise UserError(e)


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
