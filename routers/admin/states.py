from aiogram.fsm.state import StatesGroup, State


class AddUser(StatesGroup):
    add = State()


class AddChat(StatesGroup):
    add = State()


class AddChannel(StatesGroup):
    add = State()


class AddSample(StatesGroup):
    add = State()
