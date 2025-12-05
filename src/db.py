import sqlite3
from flask import g, current_app


def print_query(sql, params=None):
    if params is None:
        params = []
    if current_app.debug:
        print("SQL Query:", sql)
        print("Params:", params)


def get_connection():
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con


def execute(sql, params=None):
    print_query(sql, params)
    if params is None:
        params = []
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()


def execute_many(sql, param_list):
    print_query(sql, param_list)
    con = get_connection()
    con.executemany(sql, param_list)
    con.commit()
    con.close()


def last_insert_id():
    return g.last_insert_id


def query(sql, params=None):
    if params is None:
        params = []
    print_query(sql, params)
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result
