import sqlite3 as sq

db = sq.connect("/app/database/db/db.db")
cur = db.cursor()


async def db_start():
    cur.execute("CREATE TABLE IF NOT EXISTS users("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "user_id TEXT,"
                "api_id TEXT,"
                "api_hash TEXT,"
                "phone TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS sources("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "user_id TEXT,"
                "title TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS post_info("
                "id TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS parser_info("
                "user_id TEXT,"
                "channel TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS signatures("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "title TEXT,"
                "user_id TEXT,"
                "url TEXT)")

    db.commit()


def get_sources(user_id):
    return cur.execute(
        "SELECT id, user_id, title FROM sources WHERE user_id = '{}'".format(user_id)).fetchall()


def get_source(title):
    return cur.execute(
        "SELECT title FROM sources WHERE title = '{}'".format(title)).fetchone()


def add_source(user_id, title):
    cur.execute(
        "INSERT INTO sources (user_id, title) VALUES ('{}', '{}')".format(user_id, title)
    )
    db.commit()


def del_source(source_id):
    cur.execute("DELETE FROM sources WHERE id = '{}'".format(source_id))

    db.commit()


def select_user(user_id):
    return cur.execute(
        "SELECT api_id, api_hash, phone FROM users WHERE user_id = '{}'".format(user_id)).fetchone()


def add_user(user_id, api_id, api_hash, phone):
    cur.execute(
        "INSERT INTO users (user_id, api_id, api_hash, phone) VALUES ('{}', '{}', '{}', '{}')".format(user_id, api_id,
                                                                                                      api_hash, phone)
    )
    db.commit()


def add_post_info(channel_name, mess_id):
    cur.execute(
        "INSERT INTO post_info (id) VALUES ('{}')".format(f"{channel_name}_{mess_id}")
    )
    db.commit()


def get_post_info(channel_name, mess_id):
    return cur.execute(
        "SELECT id FROM post_info WHERE id = '{}'".format(f"{channel_name}_{mess_id}")).fetchone()


def add_parser_info(user_id, channel):
    cur.execute(
        "INSERT INTO parser_info (user_id, channel) VALUES ('{}', '{}')".format(user_id, channel)
    )
    db.commit()


def get_parser_info(user_id, channel):
    return cur.execute(
        "SELECT user_id, channel FROM parser_info WHERE user_id = '{}' AND channel = '{}'".format(user_id,
                                                                                                  channel)).fetchone()


def get_all_parser_info(user_id):
    return cur.execute(
        "SELECT user_id, channel FROM parser_info WHERE user_id = '{}'".format(user_id)).fetchall()


def delete_parser_info(user_id, channel):
    cur.execute("DELETE FROM parser_info WHERE user_id = '{}' AND channel = '{}'".format(user_id, channel))
    db.commit()


def get_all_signatures(user_id):
    return cur.execute(
        "SELECT id, title FROM signatures WHERE user_id = '{}'".format(user_id)).fetchall()


def get_signature(signature_id):
    return cur.execute(
        "SELECT id, title, url FROM signatures WHERE id = '{}'".format(signature_id)).fetchone()


def get_signature_for_title(title):
    return cur.execute(
        "SELECT url FROM signatures WHERE title = '{}'".format(title)).fetchone()


def delete_signature(signature_id):
    cur.execute("DELETE FROM signatures WHERE id = '{}'".format(signature_id))
    db.commit()


def add_signature(title, user_id, url):
    cur.execute(
        "INSERT INTO signatures (title, user_id, url) VALUES ('{}', '{}', '{}')".format(title, user_id, url)
    )
    db.commit()


def update_signature(title, signature_id):
    cur.execute(
        "UPDATE signatures SET title = '{}' WHERE id = '{}'".format(title, signature_id)
    )
    db.commit()


def update_signature_url(url, signature_id):
    cur.execute(
        "UPDATE signatures SET url = '{}' WHERE id = '{}'".format(url, signature_id)
    )
    db.commit()
