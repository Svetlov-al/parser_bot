import asyncio

from aiogram.utils.markdown import hlink
from pyrogram import Client

from database.clients import clients
from database.db import add_post_info, get_all_parser_info, get_all_signatures, get_post_info, get_sources


def get_all_sources(user_id):
    data = [f"⏩ {hlink(sou[2], url=f'https://t.me/{sou[2]}')}\n" for sou in get_sources(user_id)]
    return "".join(data)


def get_signatures(user_id):
    data = [f"⏩ {sign[1]}" for sign in get_all_signatures(user_id)]
    return "".join(data)


async def check_channel(client: Client, username):
    try:
        await client.get_chat(username)
        return True
    except:
        return False


def get_sources_ids(user_id):
    ids = [sou[0] for sou in get_sources(user_id)]
    return ids


async def parser(user_id):
    client: Client = clients.get(user_id)
    while get_all_parser_info(user_id):
        ids = get_all_parser_info(user_id)
        for user_id, source_id in ids:
            last_post = client.get_chat_history(source_id, limit=1)
            async for mess in last_post:
                if not get_post_info(source_id, mess.id):
                    try:
                        if not mess.media_group_id:
                            await client.copy_message("posts10011", source_id, mess.id)
                        else:
                            await client.copy_media_group("posts10011", source_id, mess.id)
                        add_post_info(source_id, mess.id)
                    except Exception as ex:
                        print(ex)
                        pass

            await asyncio.sleep(10)
