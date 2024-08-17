import asyncio

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from database.db import add_users_with_rights_post, get_user_with_rights, \
    get_users_with_rights, update_users_with_rights_all, update_users_del_rights_all, add_update_chat, \
    add_channel_publish, select_channel_publish, delete_channel_publish, select_channels_publish, add_sample, \
    delete_sample, select_sample
from keyboards import admin_panel_kb, admin_panel_edit_users_kb, admin_panel_edit_channel_kb, \
    admin_panel_edit_parser_kb, back_edit_users_kb, delete_users_with_rights, add_all_rights_kb, del_all_rights_kb, \
    back_edit_parser, back_edit_channel_kb, delete_channels_kb, get_samples_kb, back_admin_panel_kb, delete_samples
from routers.admin.operations import is_admin, _get_users_with_rights, delete_user, get_chat, get_channels
from routers.admin.states import AddUser, AddChat, AddChannel, AddSample

router = Router()
PHOTO_ADMIN_PANEL = FSInputFile(path="./img/admin_panel.jpg")


@router.callback_query(F.data == "back_edit_users")
async def admin_panel_add_user_back(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_caption(caption="Раздача прав пользователям\n"
                                                      "✏️ - права только на работу с постами\n"
                                                      "🔓 - полный доступ ко всему функционалу\n\n"
                                                      f"{_get_users_with_rights()}",
                                              reply_markup=admin_panel_edit_users_kb)
    await state.clear()


@router.callback_query(F.data == "back_edit_parser")
async def admin_panel_add_user_back(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_caption(caption="Чат для обмена постами бота и юзербота\n"
                                                      "В этом чате юзербот и этот бот \n"
                                                      "должны быть администраторами\n"
                                                      f"{get_chat()}",
                                              reply_markup=admin_panel_edit_parser_kb)
    await state.clear()


@router.callback_query(F.data == "back_edit_channel")
async def admin_panel_add_channel_back(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_caption(caption="В какие каналы выкладывать посты\n"
                                                      f"{get_channels()}",
                                              reply_markup=admin_panel_edit_channel_kb)
    await state.clear()


@router.callback_query(AddUser.add)
async def admin_panel_add_user_back(callback_query: types.CallbackQuery):
    await callback_query.answer("Ожидаю ID пользователя")


@router.callback_query(AddChat.add)
async def admin_panel_add_user_back(callback_query: types.CallbackQuery):
    await callback_query.answer("Ожидаю username чата")


@router.message(AddSample.add, F.text)
async def admin_panel_edit_sample_delete_add_step2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    mess_id = data.get("mess_id")
    text = message.html_text
    add_sample(text)
    await state.clear()
    await message.delete()
    await message.bot.edit_message_caption(chat_id=message.chat.id,
                                           message_id=mess_id,
                                           caption="Какой текст, сообщение, слова удалять\n"
                                                   "Удаляет только по полному совпадению",
                                           reply_markup=get_samples_kb())


@router.callback_query(AddSample.add)
async def admin_panel_edit_sample_delete_add_valid(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer("Ожидаю шаблон для удаления")


@router.message(F.text == "🅰️ Админ панель")
async def admin_panel(message: types.Message):
    await message.delete()
    if is_admin(message.from_user.id):
        await message.answer_photo(caption="🅰️<b> Админ панель </b>🅰️", reply_markup=admin_panel_kb,
                                   photo=PHOTO_ADMIN_PANEL)


@router.callback_query(F.data == "back_admin_panel")
async def back_admin_panel(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    if is_admin(callback_query.from_user.id):
        await callback_query.message.edit_caption(caption="🅰️<b> Админ панель </b>🅰️", reply_markup=admin_panel_kb)


@router.callback_query(F.data == "delete_admin_panel")
async def admin_panel_delete(callback_query: types.CallbackQuery):
    await callback_query.message.delete()


@router.callback_query(F.data == "edit_users")
async def admin_panel_edit_users(callback_query: types.CallbackQuery):
    await callback_query.message.edit_caption(caption="Раздача прав пользователям\n"
                                                      "✏️ - права только на работу с постами\n"
                                                      "🔓 - полный доступ ко всему функционалу\n\n"
                                                      f"{_get_users_with_rights()}",
                                              reply_markup=admin_panel_edit_users_kb)


@router.callback_query(F.data == "edit_channel")
async def admin_panel_edit_channel(callback_query: types.CallbackQuery):
    await callback_query.message.edit_caption(caption="В какие каналы выкладывать посты\n"
                                                      f"{get_channels()}",
                                              reply_markup=admin_panel_edit_channel_kb)


@router.callback_query(F.data == "edit_parser")
async def admin_panel_edit_parser(callback_query: types.CallbackQuery):
    await callback_query.message.edit_caption(caption="Чат для обмена постами бота и юзербота\n"
                                                      "В этом чате юзербот и этот бот \n"
                                                      "должны быть администраторами\n"
                                                      f"{get_chat()}",
                                              reply_markup=admin_panel_edit_parser_kb)


@router.callback_query(F.data == "edit_users_del")
async def admin_panel_delete_users(callback_query: types.CallbackQuery):
    if get_users_with_rights():
        await callback_query.message.edit_caption(caption="Какому пользователю запретить пользоваться ботом?",
                                                  reply_markup=delete_users_with_rights())
    else:
        await callback_query.answer("Некого удалять")


@router.callback_query(F.data.startswith("rights_delete_"))
async def delete_users_rights(callback_query: types.CallbackQuery):
    user_id = callback_query.data.split("rights_delete_")[-1]
    delete_user(user_id)
    if get_users_with_rights():
        await callback_query.message.edit_caption(caption="Какому пользователю запретить пользоваться ботом?",
                                                  reply_markup=delete_users_with_rights())
    else:
        await callback_query.message.edit_caption(caption="Раздача прав пользователям\n"
                                                          "✏️ - права только на работу с постами\n"
                                                          "🔓 - полный доступ ко всему функционалу\n\n"
                                                          f"{_get_users_with_rights()}",
                                                  reply_markup=admin_panel_edit_users_kb)


@router.callback_query(F.data == "edit_users_add")
async def admin_panel_add_user_step1(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_caption(caption="Введите ID пользователя\n"
                                                      "По умолчанию пользователю даются права на работу с постами",
                                              reply_markup=back_edit_users_kb)
    await state.set_state(AddUser.add)
    await state.update_data({"message_id": callback_query.message.message_id})


@router.message(AddUser.add, F.text)
async def admin_panel_add_user_step2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.text.strip()
    user = get_user_with_rights(user_id)
    if user:
        mess_bot = await message.answer("Такой пользователь уже есть")
        await message.delete()
        await asyncio.sleep(3)
        await mess_bot.delete()
        return
    try:
        chat_with_user = await message.bot.get_chat(chat_id=user_id)
    except:
        chat_with_user = None
    if chat_with_user:
        add_users_with_rights_post(chat_with_user.username, user_id)
        await state.clear()
        await message.delete()
        await message.bot.edit_message_caption(chat_id=message.chat.id,
                                               message_id=data.get("message_id"),
                                               caption="Раздача прав пользователям\n"
                                                       "✏️ - права только на работу с постами\n"
                                                       "🔓 - полный доступ ко всему функционалу\n\n"
                                                       f"{_get_users_with_rights()}",
                                               reply_markup=admin_panel_edit_users_kb)
    else:
        bot_mess = await message.answer("Такого пользователя не существует")
        await message.delete()
        await asyncio.sleep(3)
        await bot_mess.delete()


@router.callback_query(F.data == "add_all_rights")
async def admin_panel_add_user_all_rights(callback_query: types.CallbackQuery):
    await callback_query.message.edit_caption(caption="Какому пользователю дать все права?",
                                              reply_markup=add_all_rights_kb())


@router.callback_query(F.data.startswith("rights_add_all_"))
async def admin_panel_add_user_rights_all(callback_query: types.CallbackQuery):
    user_id = callback_query.data.split("rights_add_all_")[-1]
    if not get_user_with_rights(user_id)[3]:
        update_users_with_rights_all(user_id)
        await callback_query.message.edit_caption(caption="Какому пользователю дать все права?",
                                                  reply_markup=add_all_rights_kb())
    else:
        await callback_query.answer(text="Этот пользователь имеет все права")


# del_all_rights
@router.callback_query(F.data == "del_all_rights")
async def admin_panel_del_user_all_rights(callback_query: types.CallbackQuery):
    await callback_query.message.edit_caption(caption="У какого пользователя забрать права на \n"
                                                      "пользование всем функционалом",
                                              reply_markup=del_all_rights_kb())


@router.callback_query(F.data.startswith("rights_del_all_"))
async def admin_panel_del_user_rights_all(callback_query: types.CallbackQuery):
    user_id = callback_query.data.split("rights_del_all_")[-1]
    if get_user_with_rights(user_id)[3]:
        update_users_del_rights_all(user_id)
        await callback_query.message.edit_caption(caption="У какого пользователя забрать права на \n"
                                                          "пользование всем функционалом",
                                                  reply_markup=del_all_rights_kb())
    else:
        await callback_query.answer(text="Этот пользователь лишен прав")


@router.callback_query(F.data == "edit_edit_parser")
async def admin_panel_edit_edit_chat_step1(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_caption(caption="Введите username чата(без @)",
                                              reply_markup=back_edit_parser)
    await state.set_state(AddChat.add)
    await state.update_data({"message_id": callback_query.message.message_id})


@router.message(AddChat.add, F.text)
async def admin_panel_edit_edit_chat_step2(message: types.Message, state: FSMContext):
    username = message.text.strip()
    data = await state.get_data()
    try:
        chat = await message.bot.get_chat(f"@{username}")
        if chat.type == "supergroup":
            add_update_chat(username, chat.id)
            await message.bot.edit_message_caption(chat_id=message.chat.id,
                                                   message_id=data.get("message_id"),
                                                   caption="Чат для обмена постами бота и юзербота\n"
                                                           "В этом чате юзербот и этот бот \n"
                                                           "должны быть администраторами\n"
                                                           f"{get_chat()}",
                                                   reply_markup=admin_panel_edit_parser_kb)
            await state.clear()
        else:
            bot_mess = await message.answer("Это не чат")
            await asyncio.sleep(3)
            await bot_mess.delete()
    except:
        bot_mess = await message.answer("Чат не найден")
        await asyncio.sleep(3)
        await bot_mess.delete()
    finally:
        await message.delete()


@router.callback_query(F.data == "edit_channel_add")
async def admin_panel_add_channel_step1(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_caption(caption="Пришлите username канала \n"
                                                      "в который хотите публиковать посты.\n"
                                                      "В канале этот бот должен быть администратором",
                                              reply_markup=back_edit_channel_kb)
    await state.set_state(AddChannel.add)
    await state.update_data({"message_id": callback_query.message.message_id})


@router.message(AddChannel.add, F.text)
async def admin_panel_add_channel_step2(message: types.Message, state: FSMContext):
    username = message.text.strip()
    data = await state.get_data()
    try:
        chat = await message.bot.get_chat(f"@{username}")
        if chat and not select_channel_publish(channel_id=chat.id):
            add_channel_publish(username, chat.id)
            await message.bot.edit_message_caption(chat_id=message.chat.id,
                                                   message_id=data.get("message_id"),
                                                   caption="В какие каналы выкладывать посты\n"
                                                           f"{get_channels()}",
                                                   reply_markup=admin_panel_edit_channel_kb)
            await state.clear()
        else:
            bot_mess = await message.answer("Такой канал уже есть")
            await asyncio.sleep(3)
            await bot_mess.delete()

    except:
        bot_mess = await message.answer("Канал не найден")
        await asyncio.sleep(3)
        await bot_mess.delete()
    finally:
        await message.delete()


@router.callback_query(F.data == "edit_channel_del")
async def admin_panel_edit_channel_del(callback_query: types.CallbackQuery):
    if select_channels_publish():
        await callback_query.message.edit_caption(caption="Какой канал удалить?", reply_markup=delete_channels_kb())
    else:
        await callback_query.answer("Удалять нечего")


@router.callback_query(F.data.startswith("channel_del_"))
async def admin_panel_edit_channel_del_for_id(callback_query: types.CallbackQuery):
    channel_id = callback_query.data.split("channel_del_")[-1]
    delete_channel_publish(channel_id)
    if select_channels_publish():
        await callback_query.message.edit_caption(caption="Какой канал удалить?",
                                                  reply_markup=delete_channels_kb())
    else:
        await callback_query.message.edit_caption(caption="В какие каналы выкладывать посты\n"
                                                          f"{get_channels()}",
                                                  reply_markup=admin_panel_edit_channel_kb)


@router.callback_query(F.data == "sample_delete")
async def admin_panel_edit_sample_delete(callback_query: types.CallbackQuery):
    await callback_query.message.edit_caption(caption="Какой текст, сообщения, слова удалять\n"
                                                      "Удаляет только по полному совпадению",
                                              reply_markup=get_samples_kb())


@router.callback_query(F.data == "add_sample")
async def admin_panel_edit_sample_delete_add_step1(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_caption(caption="Введите текст, слово",
                                              reply_markup=back_admin_panel_kb)
    await state.set_state(AddSample.add)
    await state.update_data({"mess_id": callback_query.message.message_id})


@router.callback_query((F.data == "delete_sample") | F.data.startswith("samp_delete_"))
async def admin_panel_edit_sample_delete_del(callback_query: types.CallbackQuery):
    if callback_query.data.startswith("samp_delete_"):
        samp_id = callback_query.data.split("samp_delete_")[-1]
        delete_sample(samp_id)
    await callback_query.message.edit_caption(caption="Какой шаблон удалить",
                                              reply_markup=delete_samples())


@router.callback_query(F.data == "delete_sample")
async def admin_panel_edit_sample_delete_del_for_id(callback_query: types.CallbackQuery):
    await callback_query.message.edit_caption(caption="Какой шаблон удалить",
                                              reply_markup=delete_samples())


@router.callback_query(F.data.startswith("get_sample_"))
async def get_sample_text(callback_query: types.CallbackQuery):
    await callback_query.answer("")
    samp_id = callback_query.data.split("get_sample_")[-1]
    sample = select_sample(samp_id)[0]
    bot_mess = await callback_query.message.answer(text=sample)
    await asyncio.sleep(3)
    await bot_mess.delete()
