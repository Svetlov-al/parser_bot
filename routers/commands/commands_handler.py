import asyncio

from aiogram import types, Router, F
from aiogram.filters import CommandStart
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_media_group import media_group_handler

from keyboards import main_kb

router = Router()


@router.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer(text="Бот запущен", reply_markup=main_kb(message.from_user.id))
    await asyncio.sleep(3)
    await message.delete()
