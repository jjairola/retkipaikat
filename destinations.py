import db


def add_destination(name, description, municipality, user_id, classification_ids):
    sql = """INSERT INTO destinations (name, description, municipality, user_id)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [name, description, municipality, user_id])

    destination_id = db.last_insert_id()

    # TODO: Refactor
    if classification_ids:
        sql = "INSERT INTO destination_classifications (destination_id, classification_id) VALUES (?, ?)"
        for classification_id in classification_ids:
            db.execute(sql, [destination_id, classification_id])


def get_all_classifications():
    sql = "SELECT id, name FROM classifications ORDER BY name"
    return db.query(sql)


def get_destinations():
    sql = """
    SELECT d.id, d.name, d.description, d.municipality, GROUP_CONCAT(c.name) as classifications
    FROM destinations d
    LEFT JOIN destination_classifications dc ON d.id = dc.destination_id
    LEFT JOIN classifications c ON dc.classification_id = c.id
    GROUP BY d.id
    ORDER BY d.id
    """
    return db.query(sql)


def get_destination_by_id(destination_id):
    sql = """
    SELECT d.id, d.name, d.description, d.municipality, u.username, u.id as user_id, GROUP_CONCAT(c.name) as classifications
    FROM destinations d
    LEFT JOIN users u ON d.user_id = u.id
    LEFT JOIN destination_classifications dc ON d.id = dc.destination_id
    LEFT JOIN classifications c ON dc.classification_id = c.id
    WHERE d.id = ?
    GROUP BY d.id
    """
    result = db.query(sql, [destination_id])
    return result[0] if result else None


def search_destinations_by_query(query: str):
    sql = """
    SELECT d.id, d.name, d.description, d.municipality, GROUP_CONCAT(c.name) as classifications
    FROM destinations d
    LEFT JOIN destination_classifications dc ON d.id = dc.destination_id
    LEFT JOIN classifications c ON dc.classification_id = c.id
    WHERE (d.name LIKE ? OR d.description LIKE ?)
    GROUP BY d.id
    """
    return db.query(sql, [f"%{query}%", f"%{query}%"])


def get_destinations_by_classification(classification_id):
    sql = """
    SELECT d.id, d.name, d.description, d.municipality, GROUP_CONCAT(c.name) as classifications
    FROM destinations d
    JOIN destination_classifications dc ON d.id = dc.destination_id
    LEFT JOIN classifications c ON dc.classification_id = c.id
    WHERE dc.classification_id = ?
    GROUP BY d.id
    ORDER BY d.id
    """
    return db.query(sql, [classification_id])


def get_destination_classifications_ids(destination_id):
    sql = """
    SELECT classification_id
    FROM destination_classifications
    WHERE destination_id = ?
    """
    result = db.query(sql, [destination_id])
    return [row["classification_id"] for row in result]


def update_destination(
    destination_id, name, description, municipality, classification_ids
):
    sql = """UPDATE destinations SET name = ?, description = ?, municipality = ? WHERE id = ?"""
    db.execute(sql, [name, description, municipality, destination_id])

    # TODO: Refactor
    sql = "DELETE FROM destination_classifications WHERE destination_id = ?"
    db.execute(sql, [destination_id])

    if classification_ids:
        sql = "INSERT INTO destination_classifications (destination_id, classification_id) VALUES (?, ?)"
        for classification_id in classification_ids:
            db.execute(sql, [destination_id, classification_id])


def delete_destination(destination_id):
    sql = "DELETE FROM destination_classifications WHERE destination_id = ?"
    db.execute(sql, [destination_id])

    sql = "DELETE FROM destinations WHERE id = ?"
    db.execute(sql, [destination_id])
