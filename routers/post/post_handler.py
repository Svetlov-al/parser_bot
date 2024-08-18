import asyncio

from aiogram import Router, F, types, flags
from aiogram.fsm.context import FSMContext

from database.db import get_signature, add_signature, delete_signature, update_signature, \
    add_who_worked, select_who_worked
from keyboards import restore_post_kb, get_main_post_kb, publish_telegram_kb, back_edit_kb, get_signatures, \
    back_sign_kb, get_signatures_for_del, get_edit_signature_kb, back_sign_edit_kb, \
    set_signature_for_post_kb, back_publish_tg
from routers.post.operations import empty_signature, delete_signature_in_text, \
    check_format, publish_post_now, get_time_sleep, publish_post_on_time, get_unique_file_id
from routers.post.states import AddText, AddMedia, AddSignature, AddSignatureText, AddTimePost

router = Router()


@router.callback_query(F.data == "back_to_edit")
@flags.authorization(post_rights=True)
async def edit_post_back(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=restore_post_kb)
    await state.clear()


@router.callback_query(AddText.add)
@flags.authorization(post_rights=True)
async def edit_post_text_valid(callback_query: types.CallbackQuery):
    await callback_query.answer("Ожидаю текст для другого поста")


@router.callback_query(AddMedia.add_photo)
@flags.authorization(post_rights=True)
async def edit_post_media_photo_valid(callback_query: types.CallbackQuery):
    await callback_query.answer("Ожидаю медиа для другого поста")


@router.callback_query(F.data == "back_to_sign_kb")
@flags.authorization(post_rights=True)
async def edit_post_back_sign(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=get_signatures())
    await state.clear()


@router.message(AddSignature.add, F.text)
@flags.authorization(post_rights=True)
async def edit_post_add_signature_step2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        text = message.html_text
        add_signature(title=text)
        await message.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data.get("message_id"),
                                                    reply_markup=get_signatures())
        await state.clear()
    except:
        bot_message = await message.answer(text="ошибка")
        await asyncio.sleep(3)
        await bot_message.delete()
    await message.delete()


@router.callback_query(AddSignature.add)
@flags.authorization(post_rights=True)
async def edit_post_back_valid(callback_query: types.CallbackQuery):
    await callback_query.answer(text="Я ожидаю подпись")


@router.callback_query(F.data == "start_work")
@flags.authorization(post_rights=True)
async def start_work_with_post(callback_query: types.CallbackQuery):
    file_id = get_unique_file_id(callback_query.message)
    who_worked = select_who_worked(callback_query.message.html_text, file_id)
    if not who_worked:
        add_who_worked(callback_query.from_user.id, callback_query.message.html_text, file_id)
        await callback_query.message.edit_reply_markup(reply_markup=get_main_post_kb())
    elif who_worked and (str(who_worked[0]) == str(callback_query.from_user.id)):
        await callback_query.message.edit_reply_markup(reply_markup=get_main_post_kb())
    else:
        await callback_query.answer("Уже взят другим в работу")


@router.callback_query(F.data == "post_delete")
@flags.authorization(post_rights=True)
async def delete_post(callback_query: types.CallbackQuery):
    await callback_query.message.delete()


@router.callback_query(F.data == "edit_kb")
@flags.authorization(post_rights=True)
async def edit_post(callback_query: types.CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=restore_post_kb)


@router.callback_query(F.data == "edit_text")
@flags.authorization(post_rights=True)
async def edit_post_text(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=back_edit_kb)
    await callback_query.answer("Введите текст")
    if callback_query.message.caption:
        await state.set_data({"message_id": callback_query.message.message_id, "type": "caption"})
    elif callback_query.message.text:
        await state.set_data({"message_id": callback_query.message.message_id, "type": "text"})
    else:
        await state.set_data({"message_id": callback_query.message.message_id, "type": "none"})
    await state.set_state(AddText.add)


@router.message(AddText.add, F.text)
@flags.authorization(post_rights=True)
async def edit_post_text_write(message: types.Message, state: FSMContext):
    text = message.html_text
    data = await state.get_data()
    message_id = data.get("message_id")
    type_text = data.get("type")
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if type_text == "caption":
        await message.bot.edit_message_caption(chat_id=message.chat.id, caption=text, message_id=message_id,
                                               reply_markup=restore_post_kb)
    elif type_text == "text":
        await message.bot.edit_message_text(chat_id=message.chat.id, text=text, message_id=message_id,
                                            reply_markup=restore_post_kb)
    else:
        await message.bot.edit_message_caption(chat_id=message.chat.id, caption=text, message_id=message_id,
                                               reply_markup=restore_post_kb)
    await state.clear()


@router.callback_query(F.data == "edit_media")
@flags.authorization(post_rights=True)
async def edit_post_media(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer("Пришлите медиа")
    await callback_query.message.edit_reply_markup(reply_markup=back_edit_kb)
    await state.set_state(AddMedia.add_photo)
    if callback_query.message.caption:
        await state.update_data(
            {"message_id": callback_query.message.message_id, "text": callback_query.message.html_text})
    elif callback_query.message.text:
        await state.update_data(
            {"message_id": callback_query.message.message_id, "text": callback_query.message.html_text})
    else:
        await state.update_data(
            {"message_id": callback_query.message.message_id, "text": ""})


@router.message(AddMedia.add_photo, F.photo)
@flags.authorization(post_rights=True)
async def edit_post_media_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = int(data.get("message_id"))
    caption = data.get("text")
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.bot.send_photo(photo=message.photo[-1].file_id, caption=caption, reply_markup=restore_post_kb,
                                 chat_id=message.chat.id)
    await state.clear()


@router.message(AddMedia.add_photo, F.video)
@flags.authorization(post_rights=True)
async def edit_post_media_video(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = int(data.get("message_id"))
    caption = data.get("text")
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.bot.send_video(video=message.video.file_id, caption=caption, reply_markup=restore_post_kb,
                                 chat_id=message.chat.id)
    await state.clear()


@router.callback_query(F.data == "add_desc")
@flags.authorization(post_rights=True)
async def edit_post_add_desc(callback_query: types.CallbackQuery):
    await callback_query.answer("Какую подпись добавить?")
    await callback_query.message.edit_reply_markup(
        reply_markup=set_signature_for_post_kb(callback_query.message.message_id))


@router.callback_query(F.data.startswith("add_sign_"))
@flags.authorization(post_rights=True)
async def edit_post_add_desc_(callback_query: types.CallbackQuery):
    sign_id, message_id = callback_query.data.split("add_sign_")[-1].split("|")
    sign_text = get_signature(sign_id)[1]
    if callback_query.message.caption:
        if empty_signature(callback_query.message.html_text):
            message_caption = f"{callback_query.message.html_text}\n\n{sign_text}"
        else:
            message_caption = f"{delete_signature_in_text(callback_query.message.html_text, sign_text)}"
        await callback_query.bot.edit_message_caption(chat_id=callback_query.message.chat.id, message_id=message_id,
                                                      caption=message_caption)
    elif callback_query.message.text:
        if empty_signature(callback_query.message.html_text):
            message_text = f"{callback_query.message.html_text}\n\n{sign_text}"
        else:
            message_text = f"{delete_signature_in_text(callback_query.message.html_text, sign_text)}"
        await callback_query.bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=message_id,
                                                   text=message_text)
    else:
        await callback_query.answer("У поста нет текста")
    await callback_query.message.edit_reply_markup(reply_markup=get_main_post_kb())


@router.callback_query((F.data == "edit_desc") | (F.data == "back_to_signatures"))
@flags.authorization(all_rights=True)
async def edit_post_desc(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=get_signatures())
    await state.clear()


@router.callback_query(F.data == "add_signature")
@flags.authorization(post_rights=True)
async def edit_post_add_signature_step1(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer("Введите текст подписи")
    await callback_query.message.edit_reply_markup(reply_markup=back_sign_kb)
    await state.set_state(AddSignature.add)
    await state.update_data({"message_id": callback_query.message.message_id})


@router.callback_query(F.data == "delete_signatures")
@flags.authorization(post_rights=True)
async def edit_post_delete_signatures(callback_query: types.CallbackQuery):
    await callback_query.answer("Какую подпись удалить?")
    await callback_query.message.edit_reply_markup(reply_markup=get_signatures_for_del())


@router.callback_query(F.data.startswith("signature_del_"))
@flags.authorization(post_rights=True)
async def edit_post_delete_signature_for_id(callback_query: types.CallbackQuery):
    signature_id = callback_query.data.split("signature_del_")[-1]
    delete_signature(signature_id)
    await callback_query.message.edit_reply_markup(reply_markup=get_signatures_for_del())


@router.callback_query(F.data.startswith("edit_signature_"))
@flags.authorization(post_rights=True)
async def edit_post_edit_signature_for_id(callback_query: types.CallbackQuery):
    signature_id = callback_query.data.split("edit_signature_")[-1]
    await callback_query.message.edit_reply_markup(reply_markup=get_edit_signature_kb(signature_id))


@router.callback_query(F.data == "back_to_main")
@flags.authorization(post_rights=True)
async def edit_post_back_to_main(callback_query: types.CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=get_main_post_kb())


@router.callback_query(F.data.startswith("signature_text_edit_"))
@flags.authorization(post_rights=True)
async def edit_post_edit_signature_text_step1(callback_query: types.CallbackQuery, state: FSMContext):
    sign_id = callback_query.data.split("signature_text_edit_")[-1]
    signature = get_signature(sign_id)
    bot_mess = await callback_query.message.answer(signature[1])
    await callback_query.answer("Скопируйте подпись и измените")
    await callback_query.message.edit_reply_markup(reply_markup=back_sign_edit_kb)
    await state.set_state(AddSignatureText.add)
    await state.set_data({"message_id": callback_query.message.message_id, "sign_id": sign_id})
    await asyncio.sleep(4)
    await bot_mess.delete()


@router.message(AddSignatureText.add, F.text)
@flags.authorization(post_rights=True)
async def edit_post_edit_signature_text_step2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id, sign_id = data.get("message_id"), data.get("sign_id")
    text = message.html_text
    update_signature(text, sign_id)
    await message.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message_id,
                                                reply_markup=get_edit_signature_kb(sign_id))
    await state.clear()
    await message.delete()


@router.callback_query((F.data == "telegram_kb") | (F.data == "back_telegram_kb"))
@flags.authorization(post_rights=True)
async def publish_post_tg(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data:
        mess_bot = data.get("mess_time")
        await mess_bot.delete()
    await state.clear()
    await callback_query.message.edit_reply_markup(reply_markup=publish_telegram_kb)


@router.callback_query(F.data == "publish_now_tg")
@flags.authorization(post_rights=True)
async def publish_post_tg_now(callback_query: types.CallbackQuery):
    await publish_post_now(callback_query)


@router.callback_query(F.data == "set_publish_time_tg")
@flags.authorization(post_rights=True)
async def publish_post_tg_on_time(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=back_publish_tg)
    bot_message = await callback_query.message.answer(
        "Введите дату и время\nПример: 04.12.2024 15:00")
    await state.set_state(AddTimePost.add)
    await state.update_data({"message": callback_query.message, "mess_time": bot_message})


@router.message(AddTimePost.add, F.text)
@flags.authorization(post_rights=True)
async def publish_post_tg_set_time(message: types.Message, state: FSMContext):
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
            await publish_post_on_time(data.get("message"), time_sleep)
        else:
            bot_message = await message.answer("Задано прошлое время")
            await asyncio.sleep(3)
            await bot_message.delete()


@router.callback_query(F.data == "vkontakte_kb")
@flags.authorization(post_rights=True)
async def publish_post_vk(callback_query: types.CallbackQuery):
    await callback_query.answer("Не работает")
