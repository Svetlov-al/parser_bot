import asyncio

from aiogram import Router, F, types, flags
from aiogram.fsm.context import FSMContext

from database.db import del_mg_caption, update_mg_caption, select_mg_caption, get_signature, add_signature, \
    delete_signature, update_signature, select_who_worked, add_who_worked
from keyboards import get_edit_mg_kb, get_main_post_kb_for_media_group, back_edit_mg_kb, \
    set_signature_for_post_mg_kb, get_signatures_mg, back_sign_mg_kb, get_signatures_for_del_mg, \
    get_edit_signature_mg_kb, back_sign_mg_edit_kb, publish_telegram_mg_kb, back_publish_mg_tg
from routers.admin.operations import get_id_for_mg
from routers.post.operations import empty_signature, delete_signature_in_text, publish_post_mg_now, \
    check_format, get_time_sleep, publish_post_mg_on_time
from routers.post.states import AddTextMg, AddMediaMg, AddSignatureMg, AddSignatureTextMg, AddTimePostMg

router = Router()


@router.callback_query(F.data.startswith("mg_back_to_post"))
@flags.authorization(post_rights=True)
async def back_edit_mg_post(callback_query: types.CallbackQuery, state: FSMContext):
    messages_ids = callback_query.data.split("mg_back_to_post")[-1]
    await callback_query.message.edit_reply_markup(reply_markup=get_edit_mg_kb(messages_ids))
    await state.clear()


@router.callback_query(F.data.startswith("mgp_back_telegram_kb"))
@flags.authorization(post_rights=True)
async def back_publish_post_mg_tg(callback_query: types.CallbackQuery, state: FSMContext):
    messages_ids = callback_query.data.split("mgp_back_telegram_kb")[-1]
    data = await state.get_data()
    if data:
        mess_bot = data.get("mess_time")
        await mess_bot.delete()
    await state.clear()
    await callback_query.message.edit_reply_markup(reply_markup=publish_telegram_mg_kb(messages_ids))


@router.callback_query(AddTextMg.add)
@flags.authorization(post_rights=True)
async def edit_post_mg_text_valid(callback_query: types.CallbackQuery):
    await callback_query.answer("Введите текст для поста")


@router.callback_query(AddMediaMg.add)
@flags.authorization(post_rights=True)
async def edit_post_mg_media_valid(callback_query: types.CallbackQuery):
    await callback_query.answer("Пришлите медиа")


@router.callback_query(AddTimePostMg.add)
@flags.authorization(post_rights=True)
async def publish_post_mg_on_time_valid(callback_query: types.CallbackQuery):
    await callback_query.answer("Пришлите время")


@router.callback_query((F.data.startswith("mg_edit_desc")) | (F.data.startswith("mg_back_sign_kb")))
@flags.authorization(all_rights=True)
async def edit_post_mg_desc(callback_query: types.CallbackQuery, state: FSMContext):
    if "mg_edit_desc" in callback_query.data:
        messages_ids = callback_query.data.split("mg_edit_desc")[-1]
    else:
        messages_ids = callback_query.data.split("mg_back_sign_kb")[-1]
    await callback_query.message.edit_reply_markup(
        reply_markup=get_signatures_mg(messages_ids))
    await state.clear()


@router.callback_query(AddSignatureMg.add)
@flags.authorization(post_rights=True)
async def edit_post_add_signature_mg_valid(callback_query: types.CallbackQuery):
    await callback_query.answer(text="Я ожидаю подпись")


@router.callback_query(F.data.startswith("mg_start_work"))
@flags.authorization(post_rights=True)
async def start_to_work_mg(callback_query: types.CallbackQuery):
    messages_ids = callback_query.data.split("mg_start_work")[-1]
    _id = get_id_for_mg(messages_ids.split("_")[0], callback_query.from_user.id)
    caption, file_id = select_mg_caption(_id)
    who_worked = select_who_worked(caption, file_id)
    if not who_worked:
        add_who_worked(callback_query.from_user.id, caption, file_id)
        await callback_query.message.edit_reply_markup(reply_markup=get_main_post_kb_for_media_group(messages_ids))
    elif who_worked and (str(who_worked[0]) == str(callback_query.from_user.id)):
        await callback_query.message.edit_reply_markup(reply_markup=get_main_post_kb_for_media_group(messages_ids))
    else:
        await callback_query.answer("Уже взят другим в работу")


@router.callback_query(F.data.startswith("mg_delete"))
@flags.authorization(post_rights=True)
async def delete_mg_post(callback_query: types.CallbackQuery):
    message_ids = callback_query.data.split("mg_delete")[-1].split("_")
    await callback_query.bot.delete_messages(chat_id=callback_query.from_user.id,
                                             message_ids=[int(_id) for _id in message_ids])
    await callback_query.message.delete()
    _id = get_id_for_mg(message_ids[0], callback_query.from_user.id)
    del_mg_caption(_id)


@router.callback_query(F.data.startswith("mg_edit_kb"))
@flags.authorization(post_rights=True)
async def edit_mg_post(callback_query: types.CallbackQuery):
    messages_ids = callback_query.data.split("mg_edit_kb")[-1]
    await callback_query.message.edit_reply_markup(reply_markup=get_edit_mg_kb(messages_ids))


@router.callback_query(F.data.startswith("mg_back_to_main"))
@flags.authorization(post_rights=True)
async def back_main_mg_post(callback_query: types.CallbackQuery):
    messages_ids = callback_query.data.split("mg_back_to_main")[-1]
    await callback_query.message.edit_reply_markup(reply_markup=get_main_post_kb_for_media_group(messages_ids))


@router.callback_query(F.data.startswith("mg_edit_text"))
@flags.authorization(post_rights=True)
async def edit_post_mg_text_step1(callback_query: types.CallbackQuery, state: FSMContext):
    messages_ids = callback_query.data.split("mg_edit_text")[-1]
    await callback_query.message.edit_reply_markup(reply_markup=back_edit_mg_kb(messages_ids))
    await callback_query.answer("Введите текст")
    await state.set_data({"messages_ids": messages_ids, "call_mess": callback_query.message.message_id})
    await state.set_state(AddTextMg.add)


@router.message(AddTextMg.add, F.text)
@flags.authorization(post_rights=True)
async def edit_post_mg_text_step2(message: types.Message, state: FSMContext):
    text = message.text
    data = await state.get_data()
    messages_ids = data.get("messages_ids")
    call_mess = data.get("call_mess")
    _id = get_id_for_mg(messages_ids.split("_")[0], message.from_user.id)

    await message.bot.edit_message_caption(chat_id=message.chat.id, caption=text, message_id=messages_ids.split("_")[0])
    await message.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=call_mess,
                                                reply_markup=get_edit_mg_kb(messages_ids))
    update_mg_caption(_id, text)
    await message.delete()
    await state.clear()


@router.callback_query(F.data.startswith("mg_edit_media"))
@flags.authorization(post_rights=True)
async def edit_post_mg_media_step1(callback_query: types.CallbackQuery, state: FSMContext):
    mess_bot = await callback_query.message.answer("Пришлите медиа и номер(какое медиа изменить)")
    messages_ids = callback_query.data.split("mg_edit_media")[-1]
    _id = get_id_for_mg(messages_ids.split("_")[0], callback_query.from_user.id)
    await callback_query.message.edit_reply_markup(reply_markup=back_edit_mg_kb(messages_ids))
    await state.set_data({"messages_ids": messages_ids, "call_mess": callback_query.message.message_id, "_id": _id})
    await state.set_state(AddMediaMg.add)
    await asyncio.sleep(2)
    await mess_bot.delete()


@router.message(AddMediaMg.add, F.photo)
@flags.authorization(post_rights=True)
async def edit_post_mg_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    messages_ids = data.get("messages_ids")
    ids = data.get("messages_ids").split("_")
    call_mess = data.get("call_mess")
    _id = data.get("_id")
    number = message.caption
    try:
        number = int(number)
        if int(number) > 0:
            if number == 1:
                caption = select_mg_caption(_id)[0]
            else:
                caption = None
            try:
                media = types.InputMediaPhoto(
                    media=message.photo[-1].file_id,
                    caption=caption,
                )
            except:
                bot_mess = await message.answer("Поставьте другое медиа")
                await message.delete()
                await asyncio.sleep(3)
                return await bot_mess.delete()

            await message.bot.edit_message_media(chat_id=message.chat.id, message_id=ids[number - 1],
                                                 media=media)
            await message.delete()
            await message.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=call_mess,
                                                        reply_markup=get_edit_mg_kb(messages_ids))
            await state.clear()
        else:
            bot_mess = await message.answer("Не могу найти медиа под этим номером")
            await message.delete()
            await asyncio.sleep(3)
            await bot_mess.delete()
    except:
        bot_mess = await message.answer("Нужно ввести число")
        await message.delete()
        await asyncio.sleep(3)
        await bot_mess.delete()


@router.message(AddMediaMg.add, F.video)
@flags.authorization(post_rights=True)
async def edit_post_mg_video(message: types.Message, state: FSMContext):
    data = await state.get_data()
    messages_ids = data.get("messages_ids")
    ids = data.get("messages_ids").split("_")
    call_mess = data.get("call_mess")
    _id = data.get("_id")
    number = message.caption
    try:
        number = int(number)
        if int(number) > 0:
            if number == 1:
                caption = select_mg_caption(_id)[0]
            else:
                caption = None

            try:
                media = types.InputMediaVideo(
                    media=message.video.file_id,
                    caption=caption,
                )
            except Exception as ex:
                print(ex)
                bot_mess = await message.answer("Поставьте другое медиа")
                await message.delete()
                await asyncio.sleep(3)
                return await bot_mess.delete()

            await message.bot.edit_message_media(chat_id=message.chat.id, message_id=ids[number - 1],
                                                 media=media)
            await message.delete()
            await state.clear()
            await message.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=call_mess,
                                                        reply_markup=get_edit_mg_kb(messages_ids))
        else:
            bot_mess = await message.answer("Не могу найти медиа под этим номером")
            await message.delete()
            await asyncio.sleep(3)
            await bot_mess.delete()
    except Exception as ex:
        print(ex)
        bot_mess = await message.answer("Нужно прислать одно сообщение\n медиа с числом")
        await message.delete()
        await asyncio.sleep(3)
        await bot_mess.delete()


@router.callback_query(F.data.startswith("mg_add_desc"))
@flags.authorization(post_rights=True)
async def edit_post_add_desc_mg(callback_query: types.CallbackQuery):
    messages_ids = callback_query.data.split("mg_add_desc")[-1]
    await callback_query.answer("Какую подпись добавить?")
    await callback_query.message.edit_reply_markup(
        reply_markup=set_signature_for_post_mg_kb(messages_ids))


@router.callback_query(F.data.startswith("mg_add_sign_"))
@flags.authorization(post_rights=True)
async def edit_post_add_desc_mg_(callback_query: types.CallbackQuery):
    sign_id, messages_ids = callback_query.data.split("mg_add_sign_")[-1].split("|")
    sign_text = get_signature(sign_id)[1]
    _id = get_id_for_mg(messages_ids.split("_")[0], callback_query.from_user.id)
    mess_text = select_mg_caption(_id)[0]
    if empty_signature(mess_text):
        message_caption = f"{mess_text}\n\n{sign_text}"
    else:
        message_caption = f"{delete_signature_in_text(mess_text, callback_query.from_user.id)}"
    await callback_query.bot.edit_message_caption(chat_id=callback_query.message.chat.id,
                                                  message_id=messages_ids.split("_")[0],
                                                  caption=message_caption)
    update_mg_caption(_id, message_caption)

    await callback_query.message.edit_reply_markup(reply_markup=get_main_post_kb_for_media_group(messages_ids))


@router.callback_query(F.data.startswith("mg_add_signature"))
@flags.authorization(post_rights=True)
async def edit_post_add_signature_mg_step1(callback_query: types.CallbackQuery, state: FSMContext):
    messages_ids = callback_query.data.split("mg_add_signature")[-1]
    await callback_query.answer("Введите текст подписи")
    await callback_query.message.edit_reply_markup(reply_markup=back_sign_mg_kb(messages_ids))
    await state.set_state(AddSignatureMg.add)
    await state.update_data({"message_id": messages_ids, "call_id": callback_query.message.message_id})


@router.message(AddSignatureMg.add, F.text)
@flags.authorization(post_rights=True)
async def edit_post_add_signature_mg_step2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        text = message.html_text
        add_signature(title=text)
        await message.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data.get("call_id"),
                                                    reply_markup=get_signatures_mg(data.get("message_id")))
        await state.clear()
    except:
        bot_message = await message.answer(text="ошибка")
        await asyncio.sleep(3)
        await bot_message.delete()
    await message.delete()


@router.callback_query(F.data.startswith("pmg_delete_signatures"))
@flags.authorization(post_rights=True)
async def edit_post_delete_mg_signatures(callback_query: types.CallbackQuery):
    messages_ids = callback_query.data.split("pmg_delete_signatures")[-1]
    await callback_query.answer("Какую подпись удалить?")
    await callback_query.message.edit_reply_markup(
        reply_markup=get_signatures_for_del_mg(messages_ids))


@router.callback_query(F.data.startswith("mg_signature_del_"))
@flags.authorization(post_rights=True)
async def edit_post_delete_signature_for_id_mg(callback_query: types.CallbackQuery):
    data = callback_query.data.split("mg_signature_del_")[-1].split("|")
    signature_id = data[0]
    messages_ids = data[-1]
    delete_signature(signature_id)
    await callback_query.message.edit_reply_markup(
        reply_markup=get_signatures_for_del_mg(messages_ids))


@router.callback_query(F.data.startswith("mg_edit_signature_") | F.data.startswith("back_mg_to_signatures"))
@flags.authorization(post_rights=True)
async def edit_post_edit_signature_for_mg_id(callback_query: types.CallbackQuery):
    if "mg_edit_signature_" in callback_query.data:
        data = callback_query.data.split("mg_edit_signature_")[-1].split("|")
    else:
        data = callback_query.data.split("back_mg_to_signatures")[-1].split("|")
    signature_id = data[0]
    messages_ids = data[-1]
    await callback_query.message.edit_reply_markup(reply_markup=get_edit_signature_mg_kb(signature_id, messages_ids))


@router.callback_query(F.data.startswith("mg_signature_text_edit_"))
@flags.authorization(post_rights=True)
async def edit_post_edit_signature_mg_text_step1(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data.split("mg_signature_text_edit_")[-1].split("|")
    sign_id = data[0]
    messages_ids = data[-1]
    signature = get_signature(sign_id)
    bot_mess = await callback_query.message.answer(signature[1])
    await callback_query.answer("Скопируйте подпись и измените")
    await callback_query.message.edit_reply_markup(reply_markup=back_sign_mg_edit_kb(sign_id, messages_ids))
    await state.set_state(AddSignatureTextMg.add)
    await state.set_data({"message_id": messages_ids, "sign_id": sign_id, "call_id": callback_query.message.message_id})
    await asyncio.sleep(4)
    await bot_mess.delete()


@router.message(AddSignatureTextMg.add, F.text)
@flags.authorization(post_rights=True)
async def edit_post_edit_signature_mg_text_step2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id, sign_id, call_id = data.get("message_id"), data.get("sign_id"), data.get("call_id")
    text = message.html_text
    update_signature(text, sign_id)
    await message.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=call_id,
                                                reply_markup=get_edit_signature_mg_kb(sign_id, message_id))
    await state.clear()
    await message.delete()


@router.callback_query(F.data.startswith("mg_telegram_kb"))
@flags.authorization(post_rights=True)
async def publish_post_mg_tg(callback_query: types.CallbackQuery):
    messages_ids = callback_query.data.split("mg_telegram_kb")[-1]
    await callback_query.message.edit_reply_markup(reply_markup=publish_telegram_mg_kb(messages_ids))


@router.callback_query(F.data.startswith("mg_publish_now_tg"))
@flags.authorization(post_rights=True)
async def publish_post_mg_tg_now(callback_query: types.CallbackQuery):
    messages_ids = callback_query.data.split("mg_publish_now_tg")[-1]
    await publish_post_mg_now(callback_query, messages_ids)


@router.callback_query(F.data.startswith("mg_set_publish_time_tg"))
@flags.authorization(post_rights=True)
async def publish_post_mg_tg_on_time(callback_query: types.CallbackQuery, state: FSMContext):
    messages_ids = callback_query.data.split("mg_set_publish_time_tg")[-1]
    await callback_query.message.edit_reply_markup(reply_markup=back_publish_mg_tg(messages_ids))
    bot_message = await callback_query.message.answer(
        "Введите дату и время\nПример: 04.12.2024 15:00")
    await state.set_state(AddTimePostMg.add)
    await state.update_data({"message": callback_query.message, "message_ids": messages_ids, "mess_time": bot_message})


@router.message(AddTimePostMg.add, F.text)
@flags.authorization(post_rights=True)
async def publish_post_mg_tg_set_time(message: types.Message, state: FSMContext):
    time_str = message.text
    await message.delete()
    if not check_format(time_str):
        bot_message = await message.answer("Не верный формат, день.месяц.год часы:минуты")
        await asyncio.sleep(3)
        await bot_message.delete()
    else:
        time_sleep = get_time_sleep(time_str)
        if time_sleep:
            data = await state.get_data()
            mess_bot = data.get("mess_time")
            await mess_bot.delete()
            await state.clear()
            await publish_post_mg_on_time(data.get("message"), data.get("message_ids").split("_"), time_sleep)
        else:
            bot_message = await message.answer("Задано прошлое время")
            await asyncio.sleep(3)
            await bot_message.delete()


@router.callback_query(F.data.startswith("mg_vkontakte_kb"))
@flags.authorization(post_rights=True)
async def publish_post_mg_vk(callback_query: types.CallbackQuery):
    await callback_query.answer("Не работает")
