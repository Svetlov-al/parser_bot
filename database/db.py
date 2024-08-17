import sqlite3 as sq

db = sq.connect("/app/database/db/db.db")
cur = db.cursor()


async def db_start():
    cur.execute("CREATE TABLE IF NOT EXISTS users("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "api_id TEXT,"
                "api_hash TEXT,"
                "phone TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS sources("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "title TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS post_info("
                "id TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS parser_info("
                "channel TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS signatures("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "title TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS users_with_rights("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "username TEXT,"
                "user_id TEXT,"
                "rights_post BOOLEAN DEFAULT True,"
                "rights_all BOOLEAN DEFAULT False)")

    cur.execute("CREATE TABLE IF NOT EXISTS chat("
                "chat_username TEXT,"
                "chat_id TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS channel_publish("
                "channel_username TEXT,"
                "channel_id TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS who_worked("
                "user_id TEXT,"
                "caption TEXT,"
                "file_id TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS mg_caption("
                "id TEXT,"
                "caption TEXT,"
                "file_id TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS samples("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "text TEXT)")

    db.commit()


def get_sources():
    return cur.execute(
        "SELECT id, title FROM sources").fetchall()


def get_source(title):
    return cur.execute(
        "SELECT title FROM sources WHERE title = '{}'".format(title)).fetchone()


def add_source(title):
    cur.execute(
        "INSERT INTO sources (title) VALUES ('{}')".format(title)
    )
    db.commit()


def del_source(source_id):
    cur.execute("DELETE FROM sources WHERE id = '{}'".format(source_id))

    db.commit()


def select_user():
    return cur.execute(
        "SELECT api_id, api_hash, phone FROM users").fetchone()


def select_user_with_param(api_id):
    return cur.execute(
        "SELECT api_id, api_hash, phone FROM users WHERE api_id = '{}'".format(api_id)).fetchone()


def add_user(api_id, api_hash, phone):
    cur.execute(
        "INSERT INTO users (api_id, api_hash, phone) VALUES ('{}', '{}', '{}')".format(api_id, api_hash, phone)
    )
    db.commit()


# 25860381 d51fab97d193da6c77498f039d3af352 +7 931 974 3864
def update_user(api_id, api_hash, phone):
    cur.execute(
        "DELETE FROM users"
    )
    db.commit()
    cur.execute(
        "INSERT INTO users (api_id, api_hash, phone) VALUES ('{}', '{}', '{}')".format(api_id, api_hash, phone)
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


def add_parser_info(channel):
    cur.execute(
        "INSERT INTO parser_info (channel) VALUES ('{}')".format(channel)
    )
    db.commit()


def get_parser_info(channel):
    return cur.execute(
        "SELECT channel FROM parser_info WHERE channel = '{}'".format(channel)).fetchone()


def get_all_parser_info():
    return cur.execute(
        "SELECT channel FROM parser_info").fetchall()


def delete_parser_info(channel):
    cur.execute("DELETE FROM parser_info WHERE channel = '{}'".format(channel))
    db.commit()


def get_all_signatures():
    return cur.execute(
        "SELECT id, title FROM signatures").fetchall()


def get_signature(signature_id):
    return cur.execute(
        "SELECT id, title FROM signatures WHERE id = '{}'".format(signature_id)).fetchone()


def delete_signature(signature_id):
    cur.execute("DELETE FROM signatures WHERE id = '{}'".format(signature_id))
    db.commit()


def add_signature(title):
    cur.execute(
        "INSERT INTO signatures (title) VALUES ('{}')".format(title)
    )
    db.commit()


def update_signature(title, signature_id):
    cur.execute(
        "UPDATE signatures SET title = '{}' WHERE id = '{}'".format(title, signature_id)
    )
    db.commit()


def get_user_with_rights(user_id):
    return cur.execute(
        "SELECT user_id, username, rights_post, rights_all FROM users_with_rights WHERE user_id = '{}'".format(
            user_id)).fetchone()


def add_users_with_rights_post(username, user_id):
    cur.execute(
        "INSERT INTO users_with_rights (username, user_id) VALUES ('{}', '{}')".format(username, user_id)
    )
    db.commit()


def update_users_with_rights_all(user_id):
    cur.execute(
        "UPDATE users_with_rights SET rights_all = TRUE WHERE user_id = '{}'".format(user_id))
    db.commit()


def update_users_del_rights_all(user_id):
    cur.execute(
        "UPDATE users_with_rights SET rights_all = FALSE WHERE user_id = '{}'".format(user_id))
    db.commit()


def get_users_with_rights():
    return cur.execute(
        "SELECT user_id, username, rights_post, rights_all FROM users_with_rights").fetchall()


def delete_user_with_rights(user_id):
    cur.execute("DELETE FROM users_with_rights WHERE user_id = '{}'".format(user_id))
    db.commit()


def select_chat():
    return cur.execute(
        "SELECT chat_id, chat_username FROM chat").fetchone()


def add_update_chat(username, chat_id):
    if not select_chat():
        cur.execute(
            "INSERT INTO chat (chat_username, chat_id) VALUES ('{}', '{}')".format(username, chat_id)
        )
    else:
        cur.execute(
            "UPDATE chat SET chat_username = '{}', chat_id = '{}'".format(username, chat_id))
    db.commit()


def select_channel_publish(channel_id):
    return cur.execute(
        "SELECT channel_id, channel_username FROM channel_publish WHERE channel_id = '{}'".format(
            channel_id)).fetchone()


def select_channels_publish():
    return cur.execute(
        "SELECT channel_username, channel_id FROM channel_publish").fetchall()


def add_channel_publish(username, channel_id):
    cur.execute(
        "INSERT INTO channel_publish (channel_username, channel_id) VALUES ('{}', '{}')".format(username, channel_id)
    )


def delete_channel_publish(channel_id):
    cur.execute("DELETE FROM channel_publish WHERE channel_id = '{}'".format(channel_id))
    db.commit()


def select_mg_caption(_id):
    return cur.execute(
        "SELECT caption, file_id FROM mg_caption WHERE id = '{}'".format(_id)).fetchone()


def add_mg_caption(_id, caption, file_id):
    cur.execute(
        "INSERT INTO mg_caption (id, caption, file_id) VALUES ('{}', '{}', '{}')".format(_id, caption, file_id)
    )
    db.commit()


def update_mg_caption(_id, caption):
    cur.execute(
        "UPDATE mg_caption SET caption = '{}' WHERE id = '{}'".format(caption, _id))
    db.commit()


def del_mg_caption(_id):
    cur.execute("DELETE FROM mg_caption WHERE id = '{}'".format(_id))
    db.commit()


def add_who_worked(user_id, caption, file_id):
    cur.execute(
        "INSERT INTO who_worked (user_id, caption, file_id) VALUES ('{}', '{}', '{}')".format(user_id,
                                                                                              caption,
                                                                                              file_id)
    )
    db.commit()


def select_who_worked(caption, file_id):
    return cur.execute(
        "SELECT user_id, caption FROM who_worked WHERE caption = '{}' AND file_id = '{}'".format(caption,
                                                                                                 file_id)).fetchone()


def add_sample(text):
    cur.execute(
        "INSERT INTO samples (text) VALUES ('{}')".format(text)
    )
    db.commit()


def delete_sample(sample_id):
    cur.execute("DELETE FROM samples WHERE id = '{}'".format(sample_id))
    db.commit()


def select_samples():
    return cur.execute(
        "SELECT id, text FROM samples").fetchall()


def select_sample(sample_id):
    return cur.execute(
        "SELECT text FROM samples WHERE id = '{}'".format(sample_id)).fetchone()
