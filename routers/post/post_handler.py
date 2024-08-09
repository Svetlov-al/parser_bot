import asyncio

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hlink

from database.db import add_signature, delete_signature, get_signature, update_signature, update_signature_url
from keyboards import back_edit_kb, back_sign_edit_kb, back_sign_kb, get_edit_signature_kb, get_main_post_kb, \
    get_signatures, get_signatures_for_del, publish_telegram_kb, restore_post_kb, set_signature_for_post_kb
from routers.post.operations import delete_signature_in_text, empty_signature, get_text_and_signature_title_url
from routers.post.states import AddMedia, AddSignature, AddSignatureText, AddSignatureUrl, AddText

router = Router()


@router.callback_query(F.data == "back_to_edit")
async def edit_post_back(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=restore_post_kb)
    await state.clear()


@router.callback_query(AddText.add)
async def edit_post_text_valid(callback_query: types.CallbackQuery):
    await callback_query.answer("Ожидаю текст для другого поста")


@router.callback_query(AddMedia.add_photo)
async def edit_post_media_photo_valid(callback_query: types.CallbackQuery):
    await callback_query.answer("Ожидаю медиа для другого поста")


@router.callback_query(F.data == "back_to_sign_kb")
async def edit_post_back_sign(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=get_signatures(callback_query.from_user.id))
    await state.clear()


@router.message(AddSignature.add, F.text)
async def edit_post_add_signature_step2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        text, url = message.text.split("|")
        add_signature(title=text, user_id=message.from_user.id, url=url)
        await message.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data.get("message_id"),
                                                    reply_markup=get_signatures(message.from_user.id))
        await state.clear()
    except:
        bot_message = await message.answer(text="Не верный формат")
        await asyncio.sleep(3)
        await bot_message.delete()
    await message.delete()


@router.callback_query(AddSignature.add)
async def edit_post_back_valid(callback_query: types.CallbackQuery):
    await callback_query.answer(text="Я ожидаю подпись")


@router.callback_query(F.data == "post_delete")
async def delete_post(callback_query: types.CallbackQuery):
    await callback_query.message.delete()


@router.callback_query(F.data == "edit_kb")
async def edit_post(callback_query: types.CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=restore_post_kb)


@router.callback_query(F.data == "edit_text")
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
async def edit_post_text_write(message: types.Message, state: FSMContext):
    text = message.text
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
async def edit_post_media(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer("Пришлите медиа")
    await callback_query.message.edit_reply_markup(reply_markup=back_edit_kb)
    await state.set_state(AddMedia.add_photo)
    if callback_query.message.caption:
        await state.update_data(
            {"message_id": callback_query.message.message_id, "text": callback_query.message.caption})
    elif callback_query.message.text:
        await state.update_data(
            {"message_id": callback_query.message.message_id, "text": callback_query.message.text})
    else:
        await state.update_data(
            {"message_id": callback_query.message.message_id, "text": ""})


@router.message(AddMedia.add_photo, F.photo)
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
async def edit_post_add_desc(callback_query: types.CallbackQuery):
    await callback_query.answer("Какую подпись добавить?")
    await callback_query.message.edit_reply_markup(
        reply_markup=set_signature_for_post_kb(callback_query.from_user.id, callback_query.message.message_id))


@router.callback_query(F.data.startswith("add_sign_"))
async def edit_post_add_desc_(callback_query: types.CallbackQuery):
    sign_id, message_id = callback_query.data.split("add_sign_")[-1].split("|")
    sign_text, url = get_signature(sign_id)[1:]
    if callback_query.message.caption:
        if empty_signature(callback_query.message.caption):
            message_caption = f"{callback_query.message.caption}\n\n{hlink(title=sign_text, url=url)}"
        else:
            message_caption = f"{delete_signature_in_text(callback_query.message.caption)}\n\n{hlink(title=sign_text, url=url)}"
        await callback_query.bot.edit_message_caption(chat_id=callback_query.message.chat.id, message_id=message_id,
                                                      caption=message_caption)
    elif callback_query.message.text:
        if empty_signature(callback_query.message.text):
            message_text = f"{callback_query.message.text}\n\n{hlink(title=sign_text, url=url)}"
        else:
            message_text = f"{delete_signature_in_text(callback_query.message.text)}\n\n{hlink(title=sign_text, url=url)}"
        await callback_query.bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=message_id,
                                                   text=message_text)
    else:
        await callback_query.answer("У поста нет текста")
    await callback_query.message.edit_reply_markup(reply_markup=get_main_post_kb())


@router.callback_query((F.data == "edit_desc") | (F.data == "back_to_signatures"))
async def edit_post_desc(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=get_signatures(callback_query.from_user.id))
    await state.clear()


@router.callback_query(F.data == "add_signature")
async def edit_post_add_signature_step1(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer("Введите в формате -> текст:ссылка")
    await callback_query.message.edit_reply_markup(reply_markup=back_sign_kb)
    await state.set_state(AddSignature.add)
    await state.update_data({"message_id": callback_query.message.message_id})


@router.callback_query(F.data == "delete_signatures")
async def edit_post_delete_signatures(callback_query: types.CallbackQuery):
    await callback_query.answer("Какую подпись удалить?")
    await callback_query.message.edit_reply_markup(reply_markup=get_signatures_for_del(callback_query.from_user.id))


@router.callback_query(F.data.startswith("signature_del_"))
async def edit_post_delete_signature_for_id(callback_query: types.CallbackQuery):
    signature_id = callback_query.data.split("signature_del_")[-1]
    delete_signature(signature_id)
    await callback_query.message.edit_reply_markup(reply_markup=get_signatures_for_del(callback_query.from_user.id))


@router.callback_query(F.data.startswith("edit_signature_"))
async def edit_post_edit_signature_for_id(callback_query: types.CallbackQuery):
    signature_id = callback_query.data.split("edit_signature_")[-1]
    await callback_query.message.edit_reply_markup(reply_markup=get_edit_signature_kb(signature_id))


@router.callback_query(F.data == "back_to_main")
async def edit_post_back_to_main(callback_query: types.CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=get_main_post_kb())


@router.callback_query(F.data.startswith("signature_text_edit_"))
async def edit_post_edit_signature_text_step1(callback_query: types.CallbackQuery, state: FSMContext):
    sign_id = callback_query.data.split("signature_text_edit_")[-1]
    await callback_query.answer("Введите текст")
    await callback_query.message.edit_reply_markup(reply_markup=back_sign_edit_kb)
    await state.set_state(AddSignatureText.add)
    await state.set_data({"message_id": callback_query.message.message_id, "sign_id": sign_id})


@router.message(AddSignatureText.add, F.text)
async def edit_post_edit_signature_text_step2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id, sign_id = data.get("message_id"), data.get("sign_id")
    text = message.text
    update_signature(text, sign_id)
    await message.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message_id,
                                                reply_markup=get_edit_signature_kb(sign_id))
    await state.clear()
    await message.delete()


@router.callback_query(F.data.startswith("url_edit_signature_"))
async def edit_post_edit_signature_url_step1(callback_query: types.CallbackQuery, state: FSMContext):
    sign_id = callback_query.data.split("url_edit_signature_")[-1]
    await callback_query.answer("Введите ссылку")
    await callback_query.message.edit_reply_markup(reply_markup=back_sign_edit_kb)
    await state.set_state(AddSignatureUrl.add)
    await state.set_data({"message_id": callback_query.message.message_id, "sign_id": sign_id})


@router.message(AddSignatureUrl.add, F.text)
async def edit_post_edit_signature_url_step2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id, sign_id = data.get("message_id"), data.get("sign_id")
    url = message.text
    update_signature_url(url, sign_id)
    await message.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message_id,
                                                reply_markup=get_edit_signature_kb(sign_id))
    await state.clear()
    await message.delete()


@router.callback_query(F.data == "telegram_kb")
async def publish_post_tg(callback_query: types.CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=publish_telegram_kb)


# asdzxcasdzxcqwer
@router.callback_query(F.data == "publish_now_tg")
async def publish_post_tg_now(callback_query: types.CallbackQuery):
    chat_id = "-1002194713697"
    if callback_query.message.photo:
        text, sign_title, sign_url = get_text_and_signature_title_url(callback_query.message.caption)
        print(sign_url, sign_title)
        await callback_query.bot.send_photo(chat_id=chat_id, caption=f"{text}\n\n{hlink(sign_title, sign_url)}",
                                            photo=callback_query.message.photo[-1].file_id)
    elif callback_query.message.video:
        text, sign_title, sign_url = get_text_and_signature_title_url(callback_query.message.caption)
        await callback_query.bot.send_video(chat_id=chat_id, caption=f"{text}\n\n{hlink(sign_title, sign_url)}",
                                            video=callback_query.message.video.file_id)
    elif callback_query.message.text:
        text, sign_title, sign_url = get_text_and_signature_title_url(callback_query.message.text)
        await callback_query.bot.send_message(chat_id=chat_id, text=f"{text}\n\n{hlink(sign_title, sign_url)}")

    await callback_query.answer("Пост сейчас появится в канале")


@router.callback_query(F.data == "set_publish_time_tg")
async def publish_post_tg_on_time(callback_query: types.CallbackQuery):
    await callback_query.answer("Выберите время")


@router.callback_query(F.data == "vkontakte_kb")
async def publish_post_vk(callback_query: types.CallbackQuery):
    await callback_query.answer("Не работает")
