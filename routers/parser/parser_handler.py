import asyncio

from aiogram import Router, F, types, flags
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram_media_group import media_group_handler
from pyrogram import Client

from database.clients import clients
from database.db import add_source, del_source, get_sources, get_parser_info, add_parser_info, delete_parser_info, \
    get_all_parser_info, get_source, add_mg_caption, select_chat
from keyboards import settings_parser_kb, get_sources_for_del, back_add_sources, get_started_kb, start_work_kb, \
    start_work_mg_kb
from routers.admin.operations import get_users_id_with_rights, get_id_for_mg
from routers.parser.operations import get_all_sources, check_channel, get_sources_ids, parser, stop_parsers
from routers.parser.states import AddSource
from routers.post.operations import delete_samples_in_text

router = Router()
PHOTO_PARSER = FSInputFile(path="./img/sources.jpg")


@router.callback_query(F.data == "delete_settings")
@flags.authorization(all_rights=True)
async def delete_message_(callback_query: types.CallbackQuery):
    await callback_query.message.delete()


@router.message(F.text == "📰 Источники")
@flags.authorization(all_rights=True)
async def settings_parser(message: types.Message):
    await message.delete()
    sources = get_all_sources()
    if sources:
        await message.answer_photo(caption=sources, reply_markup=settings_parser_kb, photo=PHOTO_PARSER)
    else:
        await message.answer_photo(caption='Источники отсутствуют', reply_markup=settings_parser_kb, photo=PHOTO_PARSER)


@router.message(AddSource.add, F.text)
@flags.authorization(all_rights=True)
async def add_sources(message: types.Message, state: FSMContext):
    data = await state.get_data()
    client = clients.get("client")
    chanel = message.text
    if await check_channel(client=client, username=chanel):
        if not get_source(chanel):
            add_source(title=chanel)
            await state.clear()
            await message.bot.delete_message(chat_id=message.chat.id, message_id=data.get("message_id"))
            await message.answer_photo(caption=get_all_sources(), reply_markup=settings_parser_kb, photo=PHOTO_PARSER)
        else:
            bot_message = await message.answer(text="Такой канал уже есть в источниках")
            await asyncio.sleep(5)
            await bot_message.delete()
        await message.delete()
    else:
        bot_message = await message.answer(text="Канал не найден, попробуйте ещё раз")
        await message.delete()
        await asyncio.sleep(5)
        await bot_message.delete()


@router.callback_query(F.data == "back_add_sources")
@flags.authorization(all_rights=True)
async def back_settings_parser(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    sources = get_all_sources()
    if sources:
        await callback_query.message.edit_caption(caption=sources, reply_markup=settings_parser_kb)
    else:
        await callback_query.message.edit_caption(caption='Источники отсутствуют', reply_markup=settings_parser_kb)


@router.callback_query(AddSource.add)
@flags.authorization(all_rights=True)
async def add_sources_valid(callback_query: types.CallbackQuery):
    await callback_query.answer(text="Ожидаю юзернейм канала")


@router.callback_query(F.data == "del_source")
@flags.authorization(all_rights=True)
async def start_del_sources(callback_query: types.CallbackQuery):
    sources = get_all_sources()
    if sources:
        await callback_query.message.edit_caption(caption='Какой источник удалить?',
                                                  reply_markup=get_sources_for_del())
    else:
        await callback_query.answer("Отсутсвуют источники")


@router.callback_query(F.data == "add_source")
@flags.authorization(all_rights=True)
async def add_sources_(callback_query: types.CallbackQuery, state: FSMContext):
    client = clients.get("client")
    if client:
        await callback_query.message.edit_caption(caption='Введите юзернейм канала, без @',
                                                  reply_markup=back_add_sources)
        await state.set_state(AddSource.add)
        await state.update_data({"message_id": callback_query.message.message_id})
    else:
        await callback_query.answer(text="Установите или перезапустите юзербота")


@router.callback_query(F.data.startswith("source_del_"))
@flags.authorization(all_rights=True)
async def del_sources(callback_query: types.CallbackQuery):
    source_id = callback_query.data.split("source_del_")[-1]
    del_source(source_id)
    delete_parser_info(source_id)
    sources = get_sources()
    if sources:
        await callback_query.message.edit_caption(caption='Какой источник удалить?',
                                                  reply_markup=get_sources_for_del())
    else:
        await callback_query.message.edit_caption(caption='Источники отсутствуют', reply_markup=settings_parser_kb)


@router.callback_query(F.data == "start_parser")
@flags.authorization(all_rights=True)
async def start_parser(callback_query: types.CallbackQuery):
    if not get_sources():
        await callback_query.answer("Отсутсвуют источники")
    elif not clients.get("client"):
        await callback_query.answer(text="Установите или перезапустите юзербота")
    else:
        await callback_query.message.edit_caption(caption='Какой запустить?',
                                                  reply_markup=get_started_kb("start"))


@router.callback_query(F.data == "start_all_parser")
@flags.authorization(all_rights=True)
async def start_all_parsers(callback_query: types.CallbackQuery):
    sources = get_sources()
    parsers = get_all_parser_info()
    if len(sources) == len(parsers):
        await callback_query.answer("Уже все запущены")
    else:
        if not select_chat():
            return await callback_query.answer("Настойте чат в админ панели")
        for _id, title in sources:
            if not get_parser_info(title):
                add_parser_info(title)
        await callback_query.message.edit_caption(caption='Какой запустить?',
                                                  reply_markup=get_started_kb("start"))
        await parser()


@router.callback_query(F.data == "stop_all_parser")
@flags.authorization(all_rights=True)
async def stop_all_parsers(callback_query: types.CallbackQuery):
    sources = get_sources()
    parsers = get_all_parser_info()
    if len(parsers) == 0:
        await callback_query.answer("Уже все остановлены")
    else:
        stop_parsers(sources)
        await callback_query.message.edit_caption(caption='Какой остановить?',
                                                  reply_markup=get_started_kb("stop"))


@router.callback_query(F.data.startswith("start_source_"))
@flags.authorization(all_rights=True)
async def start_parser_for_id(callback_query: types.CallbackQuery):
    title = callback_query.data.split("start_source_")[-1]
    is_started = get_parser_info(title)
    if not is_started:
        add_parser_info(title)
        ids = get_sources_ids()
        client: Client = clients.get("client")
        if not select_chat():
            return await callback_query.answer("Настойте чат в админ панели")
        if ids and client:
            await callback_query.message.edit_caption(caption='Какой запустить?',
                                                      reply_markup=get_started_kb("start"))
            await parser()
    elif is_started:
        await callback_query.answer(text="Уже запущен")


@router.callback_query(F.data == "stop_parser")
@flags.authorization(all_rights=True)
async def stop_parser(callback_query: types.CallbackQuery):
    if not get_sources():
        await callback_query.answer("Отсутсвуют источники")
    else:
        await callback_query.message.edit_caption(caption='Какой остановить?',
                                                  reply_markup=get_started_kb("stop"))


@router.callback_query(F.data.startswith("stop_source_"))
@flags.authorization(all_rights=True)
async def stop_parser_for_id(callback_query: types.CallbackQuery):
    title = callback_query.data.split("stop_source_")[-1]
    is_started = get_parser_info(title)
    if is_started:
        delete_parser_info(title)
        await callback_query.message.edit_caption(caption='Какой остановить?',
                                                  reply_markup=get_started_kb("stop"))
    else:
        await callback_query.answer(text="Уже остановлен")


@router.message(F.media_group_id, F.chat.type == "supergroup", F.chat.title != "🗑")
@media_group_handler
async def media_command(messages: list[types.Message]):
    ids = get_users_id_with_rights()
    media_group = []
    for m in messages:
        if m.photo:
            media_group.append(types.InputMediaPhoto(
                media=m.photo[-1].file_id,
                caption=delete_samples_in_text(m.html_text),
                caption_entities=m.caption_entities,
            ))
        elif m.video:
            media_group.append(types.InputMediaVideo(
                media=m.video.file_id,
                caption=delete_samples_in_text(m.html_text),
                caption_entities=m.caption_entities,
            ))
    for user_id in ids:
        mess = await messages[-1].bot.send_media_group(media=media_group, chat_id=user_id)
        ids = "_".join([str(m.message_id) for m in mess])
        await messages[-1].bot.send_message(chat_id=user_id,
                                            reply_markup=start_work_mg_kb(ids),
                                            disable_notification=True,
                                            text="🔝ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ")  # text="🔝ᅠ ᅠ ᅠ ᅠ ᅠ ᅠ ᅠ ᅠ ᅠ ᅠ ᅠ ᅠ "
        _id = get_id_for_mg(mess[0].message_id, mess[0].chat.id)
        if mess[0].photo:
            file_id = mess[0].photo[-1].file_unique_id
        else:
            file_id = mess[0].video.file_unique_id
        add_mg_caption(_id, delete_samples_in_text(messages[0].html_text), file_id)


@router.message(F.chat.type == "supergroup", F.chat.title != "🗑")
async def channel_post_handler(channel_post: types.Message):
    ids = get_users_id_with_rights()
    try:
        if not channel_post.media_group_id:
            for user_id in ids:
                if channel_post.text:
                    new_text = delete_samples_in_text(channel_post.html_text)
                    await channel_post.bot.send_message(chat_id=user_id, text=new_text, reply_markup=start_work_kb)
                else:
                    new_text = delete_samples_in_text(channel_post.html_text)
                    if channel_post.photo:
                        await channel_post.bot.send_photo(chat_id=user_id, caption=new_text,
                                                          photo=channel_post.photo[-1].file_id,
                                                          reply_markup=start_work_kb)
                    elif channel_post.video:
                        await channel_post.bot.send_video(chat_id=user_id, caption=new_text,
                                                          video=channel_post.video.file_id, reply_markup=start_work_kb)
    except:
        pass
