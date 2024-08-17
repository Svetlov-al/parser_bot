from aiogram.fsm.state import State, StatesGroup


class AddText(StatesGroup):
    add = State()


class AddMedia(StatesGroup):
    add_photo = State()


class AddSignature(StatesGroup):
    add = State()


class AddSignatureText(StatesGroup):
    add = State()


class AddSignatureUrl(StatesGroup):
    add = State()


class AddTimePost(StatesGroup):
    add = State()


class AddTextMg(StatesGroup):
    add = State()


class AddMediaMg(StatesGroup):
    add = State()


class AddSignatureMg(StatesGroup):
    add = State()


class AddSignatureTextMg(StatesGroup):
    add = State()


class AddSignatureUrlMg(StatesGroup):
    add = State()


class AddTimePostMg(StatesGroup):
    add = State()
