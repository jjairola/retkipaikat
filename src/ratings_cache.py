import db


def update_cache(destination_id):
    sql = """
    SELECT ROUND(COALESCE(AVG(c.rating), 0), 1) AS average_rating
    FROM comments c
    WHERE c.destination_id = ?
    """

    result = db.query(sql, [destination_id])
    average = result[0]["average_rating"] if result else 0

    sql_update = """
    INSERT OR REPLACE INTO ratings_cache (destination_id, average_rating)
    VALUES (?, ?)
    """
    db.execute(sql_update, [destination_id, average])


if __name__ == "__main__":
    from app import app

    with app.app_context():
        SQL = """
        SELECT d.id AS destination_id, ROUND(COALESCE(AVG(c.rating), 0), 1) AS average_rating
        FROM destinations d
        LEFT JOIN comments c ON c.destination_id = d.id
        GROUP BY d.id
        """
        destinations = db.query(SQL)

        print("Updating ratings cache for", len(destinations), "destinations")
        data = [
            (destination_id, average_rating)
            for destination_id, average_rating in destinations
        ]

        SQL_INSERT = """
        INSERT OR REPLACE INTO ratings_cache (destination_id, average_rating)
        VALUES (?, ?)
        """
        db.execute_many(SQL_INSERT, data)

        print("Ratings cache updated.")
