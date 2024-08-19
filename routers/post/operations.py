import asyncio
import copy
import re
from datetime import datetime, timedelta

from aiogram import types
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pytz import timezone

from database.db import get_all_signatures, select_samples, add_published_post, update_published_post
from keyboards import publish_post_now_kb, publish_post_with_time, publish_post_mg_now_kb, publish_post_mg_with_time_kb
from routers.admin.operations import get_channels_ids


def end_publish_post(time_publish=None):
    builder = InlineKeyboardBuilder()
    if time_publish:
        builder.row(
            InlineKeyboardButton(text=f"Пост будет опубликован через {time_publish}",
                                 callback_data="_blank_"))
    else:
        builder.row(InlineKeyboardButton(text=f"Пост ✅ опубликован", callback_data="_blank_"))
    builder.row(InlineKeyboardButton(text="❌ Удалить", callback_data="post_delete"))
    return builder.as_markup()


def empty_signature(mess_text):
    signatures = get_all_signatures()
    for sign in signatures:
        if sign[1] in mess_text:
            return False
    return True


def delete_signature_in_text(mess_text, new_sign):
    signatures = get_all_signatures()
    for sign in signatures:
        if sign[1] in mess_text:
            text = mess_text.replace(sign[1], new_sign)
            return text
    return mess_text


def get_time_sleep(time_str):
    tz = timezone("Europe/Moscow")
    time_me = datetime.strptime(time_str, "%d.%m.%Y %H:%M")
    time_now_str = datetime.now(tz=tz).strftime("%d.%m.%Y %H:%M")
    time_now = datetime.strptime(time_now_str, "%d.%m.%Y %H:%M")
    time_ = time_me - time_now
    total_sec = int(time_.total_seconds())
    if total_sec < 0:
        return None
    else:
        return total_sec


def check_format(time_str):
    try:
        datetime.strptime(time_str, "%d.%m.%Y %H:%M")
        return True
    except:
        return False


async def publish_post_now(callback_query: types.CallbackQuery):
    chat_ids = get_channels_ids()
    if chat_ids:
        for chat_id in chat_ids:
            if callback_query.message.photo:
                await callback_query.bot.send_photo(chat_id=chat_id, caption=callback_query.message.html_text,
                                                    photo=callback_query.message.photo[-1].file_id)
            elif callback_query.message.video:
                await callback_query.bot.send_video(chat_id=chat_id,
                                                    caption=callback_query.message.html_text,
                                                    video=callback_query.message.video.file_id)
            elif callback_query.message.text:

                await callback_query.bot.send_message(chat_id=chat_id,
                                                      text=callback_query.message.html_text)
        add_published_post(callback_query.message.message_id, "tg")
        await callback_query.message.edit_reply_markup(
            reply_markup=publish_post_now_kb(callback_query.message.message_id))
    else:
        await callback_query.answer("Канал для публикации не настроен")


async def publish_post_mg_now(callback_query: types.CallbackQuery, messages_ids):
    chat_ids = get_channels_ids()
    if chat_ids:
        for chat_id in chat_ids:
            await callback_query.bot.copy_messages(chat_id=chat_id, from_chat_id=callback_query.message.chat.id,
                                                   message_ids=[int(mess) for mess in messages_ids.split("_")])
        add_published_post(messages_ids, "tg")
        await callback_query.answer("Пост сейчас появится в канале")
        await callback_query.message.edit_reply_markup(
            reply_markup=publish_post_mg_now_kb(messages_ids))
    else:
        await callback_query.answer("Канал для публикации не настроен")


async def publish_post_mg_on_time(message: types.Message, messages_ids, time_sleep, time_str):
    chat_ids = get_channels_ids()
    if chat_ids:
        bot_message = await message.answer("Пост появиться в канале в указанное время")
        add_published_post("_".join(messages_ids), "tg", time_str)
        await message.edit_reply_markup(reply_markup=publish_post_mg_with_time_kb("_".join(messages_ids)))
        await asyncio.sleep(3)
        await bot_message.delete()

        await asyncio.sleep(time_sleep)
        update_published_post("_".join(messages_ids), "tg")
        for chat_id in chat_ids:
            await message.bot.copy_messages(chat_id=chat_id, message_ids=[int(mess) for mess in messages_ids],
                                            from_chat_id=message.chat.id)
    else:
        bot_mess = await message.answer("Канал для публикации не настроен")
        await asyncio.sleep(3)
        await bot_mess.delete()


async def publish_post_on_time(message: types.Message, time_sleep, time_str):
    chat_ids = get_channels_ids()
    if chat_ids:
        bot_message = await message.answer("Пост появиться в канале в указанное время")
        add_published_post(message.message_id, "tg", time_str)
        await message.edit_reply_markup(reply_markup=publish_post_with_time(message.message_id))
        await asyncio.sleep(3)
        await bot_message.delete()
        if message.photo:
            await asyncio.sleep(time_sleep)
            update_published_post(message.message_id, "tg")
            for chat_id in chat_ids:
                await message.bot.send_photo(chat_id=chat_id, caption=message.html_text,
                                             photo=message.photo[-1].file_id)
        elif message.video:
            await asyncio.sleep(time_sleep)
            update_published_post(message.message_id, "tg")
            for chat_id in chat_ids:
                await message.bot.send_video(chat_id=chat_id, caption=message.html_text,
                                             video=message.video.file_id)
        elif message.text:
            await asyncio.sleep(time_sleep)
            update_published_post(message.message_id, "tg")
            for chat_id in chat_ids:
                await message.bot.send_message(chat_id=chat_id, text=message.html_text)

    else:
        bot_mess = await message.answer("Канал для публикации не настроен")
        await asyncio.sleep(3)
        await bot_mess.delete()


def clean_html(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def get_unique_file_id(message: types.Message):
    if message.photo:
        return message.photo[-1].file_unique_id
    elif message.video:
        return message.video.file_unique_id
    else:
        return None


def delete_samples_in_text(mess_text):
    if mess_text:
        new_text = copy.copy(mess_text)
        samples = select_samples()
        for sample in samples:
            if sample[1] in new_text:
                new_text = new_text.replace(sample[1], " ")
        return new_text
