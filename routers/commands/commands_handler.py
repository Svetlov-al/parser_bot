import asyncio

from aiogram import Router, types
from aiogram.filters import CommandStart

from keyboards import main_kb

router = Router()


@router.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer(text="Бот запущен", reply_markup=main_kb)
