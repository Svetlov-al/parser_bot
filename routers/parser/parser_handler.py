import asyncio

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram_media_group import media_group_handler
from pyrogram import Client

from database.clients import clients
from database.db import add_source, del_source, get_sources, get_parser_info, add_parser_info, delete_parser_info, \
    get_all_parser_info, get_source
from keyboards import settings_parser_kb, get_sources_for_del, back_add_sources, get_main_post_kb, get_started_kb
from routers.parser.operations import get_all_sources, check_channel, get_sources_ids, parser
from routers.parser.states import AddSource

router = Router()


@router.callback_query(F.data == "delete_settings")
async def delete_message_(callback_query: types.CallbackQuery):
    await callback_query.message.delete()


@router.message(F.text == "📰 Источники")
async def settings_parser(message: types.Message):
    await message.delete()
    sources = get_all_sources(message.from_user.id)
    if sources:
        await message.answer(text=sources, reply_markup=settings_parser_kb)
    else:
        await message.answer(text='Источники отсутствуют', reply_markup=settings_parser_kb)


@router.message(AddSource.add, F.text)
async def add_sources(message: types.Message, state: FSMContext):
    data = await state.get_data()
    client = clients.get(message.from_user.id)
    chanel = message.text
    if await check_channel(client=client, username=chanel):
        if not get_source(chanel):
            add_source(user_id=message.from_user.id, title=chanel)
            await state.clear()
            await message.bot.delete_message(chat_id=message.chat.id, message_id=data.get("message_id"))
            await message.answer(text=get_all_sources(message.from_user.id), reply_markup=settings_parser_kb)
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
async def back_settings_parser(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    sources = get_all_sources(callback_query.from_user.id)
    if sources:
        await callback_query.message.edit_text(text=sources, reply_markup=settings_parser_kb)
    else:
        await callback_query.message.edit_text(text='Источники отсутствуют', reply_markup=settings_parser_kb)


@router.callback_query(AddSource.add)
async def add_sources_valid(callback_query: types.CallbackQuery):
    await callback_query.answer(text="Ожидаю юзернейм канала")


@router.callback_query(F.data == "del_source")
async def start_del_sources(callback_query: types.CallbackQuery):
    sources = get_all_sources(callback_query.from_user.id)
    if sources:
        await callback_query.message.edit_text(text='Какой источник удалить?',
                                               reply_markup=get_sources_for_del(callback_query.from_user.id))
    else:
        await callback_query.answer("Отсутсвуют источники")


@router.callback_query(F.data == "add_source")
async def add_sources_(callback_query: types.CallbackQuery, state: FSMContext):
    client = clients.get(callback_query.from_user.id)
    if client:
        await callback_query.message.edit_text(text='Введите юзернейм канала, без @', reply_markup=back_add_sources)
        await state.set_state(AddSource.add)
        await state.update_data({"message_id": callback_query.message.message_id})
    else:
        await callback_query.answer(text="Установите или перезапустите юзербота")


@router.callback_query(F.data.startswith("source_del_"))
async def del_sources(callback_query: types.CallbackQuery):
    source_id = callback_query.data.split("source_del_")[-1]
    del_source(source_id)
    delete_parser_info(callback_query.from_user.id, source_id)
    sources = get_sources(callback_query.from_user.id)
    if sources:
        await callback_query.message.edit_text(text='Какой источник удалить?',
                                               reply_markup=get_sources_for_del(callback_query.from_user.id))
    else:
        await callback_query.message.edit_text(text='Источники отсутствуют', reply_markup=settings_parser_kb)


@router.callback_query(F.data == "start_parser")
async def start_parser(callback_query: types.CallbackQuery):
    if not get_sources(callback_query.from_user.id):
        await callback_query.answer("Отсутсвуют источники")
    elif not clients.get(callback_query.from_user.id):
        await callback_query.answer(text="Установите или перезапустите юзербота")
    else:
        await callback_query.message.edit_text(text='Какой запустить?',
                                               reply_markup=get_started_kb(callback_query.from_user.id, "start"))


@router.callback_query(F.data == "start_all_parser")
async def start_all_parsers(callback_query: types.CallbackQuery):
    sources = get_sources(callback_query.from_user.id)
    parsers = get_all_parser_info(callback_query.from_user.id)
    if len(sources) == len(parsers):
        await callback_query.answer("Уже все запущены")
    else:
        for _id, user_id, title in sources:
            if not get_parser_info(user_id, title):
                add_parser_info(user_id, title)
        await callback_query.message.edit_text(text='Какой запустить?',
                                               reply_markup=get_started_kb(callback_query.from_user.id, "start"))
        await parser(callback_query.from_user.id)


@router.callback_query(F.data == "stop_all_parser")
async def stop_all_parsers(callback_query: types.CallbackQuery):
    sources = get_sources(callback_query.from_user.id)
    parsers = get_all_parser_info(callback_query.from_user.id)
    if len(parsers) == 0:
        await callback_query.answer("Уже все остановлены")
    else:
        for _id, user_id, title in sources:
            if get_parser_info(user_id, title):
                delete_parser_info(user_id, title)
        await callback_query.message.edit_text(text='Какой остановить?',
                                               reply_markup=get_started_kb(callback_query.from_user.id, "stop"))


@router.callback_query(F.data.startswith("start_source_"))
async def start_parser_for_id(callback_query: types.CallbackQuery):
    title = callback_query.data.split("start_source_")[-1]
    is_started = get_parser_info(callback_query.from_user.id, title)
    if not is_started:
        add_parser_info(callback_query.from_user.id, title)
        ids = get_sources_ids(callback_query.from_user.id)
        client: Client = clients.get(callback_query.from_user.id)
        if ids and client:
            await callback_query.message.edit_text(text='Какой запустить?',
                                                   reply_markup=get_started_kb(callback_query.from_user.id, "start"))
            await parser(callback_query.from_user.id)
    elif is_started:
        await callback_query.answer(text="Уже запущен")


@router.callback_query(F.data == "stop_parser")
async def stop_parser(callback_query: types.CallbackQuery):
    if not get_sources(callback_query.from_user.id):
        await callback_query.answer("Отсутсвуют источники")
    elif not clients.get(callback_query.from_user.id):
        await callback_query.answer(text="Установите или перезапустите юзербота")
    else:
        await callback_query.message.edit_text(text='Какой остановить?',
                                               reply_markup=get_started_kb(callback_query.from_user.id, "stop"))


@router.callback_query(F.data.startswith("stop_source_"))
async def stop_parser_for_id(callback_query: types.CallbackQuery):
    title = callback_query.data.split("stop_source_")[-1]
    is_started = get_parser_info(callback_query.from_user.id, title)
    if is_started:
        delete_parser_info(callback_query.from_user.id, title)
        await callback_query.message.edit_text(text='Какой остановить?',
                                               reply_markup=get_started_kb(callback_query.from_user.id, "stop"))
    else:
        await callback_query.answer(text="Уже остановлен")


@router.message(F.media_group_id, F.chat.type == "supergroup")
@media_group_handler
async def media_command(messages: list[types.Message]):
    media_group = []
    for m in messages:
        if m.photo:
            media_group.append(types.InputMediaPhoto(
                media=m.photo[-1].file_id,
                caption=m.caption,
                caption_entities=m.caption_entities,
            ))
        elif m.video:
            media_group.append(types.InputMediaVideo(
                media=m.video.file_id,
                caption=m.caption,
                caption_entities=m.caption_entities,
            ))
    await messages[-1].bot.send_media_group(media=media_group, chat_id='585028070')


@router.message(F.chat.type == "supergroup")
async def channel_post_handler(channel_post: types.Message):
    try:
        if not channel_post.media_group_id:
            await channel_post.send_copy(chat_id='585028070', reply_markup=get_main_post_kb())  # 585028070, i-763197387
        else:
            print(channel_post.message_id, "медиа группа")
    except:
        pass
