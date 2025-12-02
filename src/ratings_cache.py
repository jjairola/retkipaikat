import db


def update_cache(destination_id):
    sql = """
    INSERT OR REPLACE INTO ratings_cache (destination_id, average_rating)
    SELECT
        ?,
        ROUND(COALESCE(AVG(c.rating), 0), 1) AS average_rating
    FROM comments c
    WHERE c.destination_id = ?
    """
    db.execute(sql, [destination_id, destination_id])


if __name__ == "__main__":
    from app import app

    with app.app_context():
        sql = """
        SELECT d.id AS destination_id, ROUND(COALESCE(AVG(c.rating), 0), 1) AS average_rating
        FROM destinations d
        LEFT JOIN comments c ON c.destination_id = d.id
        GROUP BY d.id
        """
        destinations = db.query(sql)

        print("Updating ratings cache for", len(destinations), "destinations")
        data = [
            (destination_id, average_rating)
            for destination_id, average_rating in destinations
        ]

        sql_insert = """
        INSERT OR REPLACE INTO ratings_cache (destination_id, average_rating)
        VALUES (?, ?)
        """
        db.execute_many(sql_insert, data)

        print("Ratings cache updated.")
