import os

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.markdown import hlink
from pyrogram import Client

from database.clients import clients
from database.db import select_user, add_user
from keyboards import back_settings_user, settings_user, main_kb, settings_user_already

router = Router()


class AddUserData(StatesGroup):
    add = State()
    phone_code = State()


@router.callback_query(F.data == "settings_data")
async def set_userdata(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(
        f"Ознакомьтесь с {hlink(title='инструкцией', url='https://docs.google.com/document/d/1cqG9Kiz0EsoVCOmxNMZ-QLwV2LpczhycTUZ7PU_IjaU/edit?usp=sharing')}, "
        f"далее перейдите по {hlink('ссылке', url='https://my.telegram.org/auth')} и введите нужные данные ниже в формате:\n"
        f"api_id,api_hash,номер_телефона", parse_mode="html", reply_markup=back_settings_user)
    await state.set_state(AddUserData.add)


@router.message(AddUserData.add, F.text)
async def set_data(message: types.Message, state: FSMContext):
    try:
        session_dir = "/app/sessions"
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)

        api_id, api_hash, phone = message.text.split(",")
        session_file = os.path.join(session_dir, api_id)
        client = Client(name=session_file, api_id=api_id, api_hash=api_hash, phone_number=phone)
        await client.connect()
        send_code = await client.send_code(phone)
        await state.update_data(
            {"code": send_code, "client": client, "phone_number": phone, "api_id": api_id, "api_hash": api_hash})
        await state.set_state(AddUserData.phone_code)
        await message.answer(text="Введите код")
    except Exception as ex:
        print(ex)
        await message.answer(text="Данные не верные", reply_markup=main_kb)
        await state.clear()


@router.message(AddUserData.add)
async def set_id_hash_valid(message: types.Message):
    await message.answer(text="Введите api_id,api_hash,номер_телефона", reply_markup=main_kb)


@router.message(AddUserData.phone_code, F.text)
async def set_phone_code(message: types.Message, state: FSMContext):
    phone_code = message.text
    data = await state.get_data()
    client, send_code, phone = data.get("client"), data.get("code"), data.get("phone_number")

    try:
        user = await client.sign_in(phone, send_code.phone_code_hash, phone_code)
        if user:
            add_user(message.from_user.id, data.get("api_id"), data.get("api_hash"), phone)
            await message.answer(text="Данные сохранены", reply_markup=main_kb)
            clients.update({message.from_user.id: client})
    except Exception as ex:
        print(ex)
        await message.answer(text="Данные не верные", reply_markup=main_kb)
        await client.disconnect()
    finally:
        await state.clear()


@router.message(AddUserData.phone_code)
async def set_phone_code_valid(message: types.Message):
    await message.answer(text="Я ожидаю код")


@router.callback_query(AddUserData.add, F.data == "back_settings_data")
async def back_setting_user(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    data = select_user(callback_query.from_user.id)
    if not data:
        await callback_query.message.edit_text(text="Данные отсутствуют", reply_markup=settings_user)
    else:
        await callback_query.message.edit_text(text=f"Телефон: {data[2]}\n"
                                                    f"API_ID: {data[0]}\n"
                                                    f"API_HASH: {data[1]}\n", reply_markup=settings_user_already)


@router.message(F.text == "🤖 Данные юзербота")
async def setting_user(message: types.Message):
    await message.delete()
    data = select_user(message.from_user.id)
    if not data:
        await message.answer(text="Данные отсутствуют", reply_markup=settings_user)
    else:
        await message.answer(text=f"Телефон: {data[2]}\n"
                                  f"API_ID: {data[0]}\n"
                                  f"API_HASH: {data[1]}\n", reply_markup=settings_user_already)


@router.callback_query(F.data == "restart_client")
async def restart_client_user(callback_query: types.CallbackQuery):
    client = clients.get(callback_query.from_user.id)
    user = select_user(callback_query.from_user.id)
    session_dir = "/app/sessions"
    session_file = os.path.join(session_dir, str(user[0]))
    if os.path.exists(f"{session_dir}/{user[0]}.session-journal"):
        try:
            await client.stop()
            await client.start()
            clients[callback_query.from_user.id] = client
        except:
            client = Client(name=session_file, api_id=int(user[0]), api_hash=user[1])
            await client.start()
            clients[callback_query.from_user.id] = client

    elif not client:
        client = Client(name=session_file, api_id=int(user[0]), api_hash=user[1])
        await client.start()
        clients[callback_query.from_user.id] = client

    await callback_query.answer(text="Клиент перезапущен")
