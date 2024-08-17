from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import get_sources, get_all_signatures, get_parser_info, get_users_with_rights, \
    select_channels_publish, select_samples
from routers.admin.operations import is_admin
from routers.post.operations import clean_html


def main_kb(user_id):
    kb_list = [
        [KeyboardButton(text="📰 Источники"), KeyboardButton(text="🤖 Данные юзербота")]
    ]
    if is_admin(user_id):
        kb_list.append([KeyboardButton(text="🅰️ Админ панель"), ])
    kb = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=False)
    return kb


def start_work_mg_kb(message_id):
    _kb = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="✅ Начать", callback_data=f"mg_start_work{message_id}"),
            ],
            [
                InlineKeyboardButton(text="❌ Удалить", callback_data=f"mg_delete{message_id}"),
            ]
        ]
    )
    return _kb


start_work_kb = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="✅ Начать", callback_data=f"start_work"),
        ],
        [
            InlineKeyboardButton(text="❌ Удалить", callback_data=f"post_delete"),
        ]
    ]
)

settings_user = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="📝 Добавить данные", callback_data="settings_data"),
        ],
        [
            InlineKeyboardButton(text="⛔ Закрыть", callback_data="delete_settings"),
        ]
    ]
)

settings_user_already = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="📝 Изменить данные", callback_data="settings_data"),
        ],
        [
            InlineKeyboardButton(text="🔁 Перезапустить клиент", callback_data="restart_client"),
        ],
        [
            InlineKeyboardButton(text="⛔ Закрыть", callback_data="delete_settings"),
        ]
    ]
)

settings_parser_kb = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="➕ Добавить", callback_data="add_source"),
            InlineKeyboardButton(text="➖ Удалить", callback_data="del_source"),
        ],
        [
            InlineKeyboardButton(text="✔️ Запустить", callback_data="start_parser"),
        ],
        [
            InlineKeyboardButton(text="❌ Остановить", callback_data="stop_parser"),
        ],
        [
            InlineKeyboardButton(text="⛔ Закрыть", callback_data="delete_settings"),
        ]
    ]
)

back_settings_user = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="back_settings_data"),
        ],
    ]
)

back_add_sources = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="back_add_sources"),
        ],
    ]
)


def get_main_post_kb():
    post_kb = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="💎 Пост в телеграмм", callback_data=f"telegram_kb"),
            ],
            [
                InlineKeyboardButton(text="▶️ Пост в вконтакте", callback_data=f"vkontakte_kb"),
            ],
            [
                InlineKeyboardButton(text="📃 Добавить описание", callback_data=f"add_desc"),
            ],
            [
                InlineKeyboardButton(text="✍️ Изменить", callback_data=f"edit_kb"),
                InlineKeyboardButton(text="❌ Удалить", callback_data=f"post_delete"),
            ],
        ]
    )
    return post_kb


def get_main_post_kb_for_media_group(message_id):
    post_kb = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="💎 Пост в телеграмм", callback_data=f"mg_telegram_kb{message_id}"),
            ],
            [
                InlineKeyboardButton(text="▶️ Пост в вконтакте", callback_data=f"mg_vkontakte_kb{message_id}"),
            ],
            [
                InlineKeyboardButton(text="📃 Добавить описание", callback_data=f"mg_add_desc{message_id}"),
            ],
            [
                InlineKeyboardButton(text="✍️ Изменить", callback_data=f"mg_edit_kb{message_id}"),
                InlineKeyboardButton(text="❌ Удалить", callback_data=f"mg_delete{message_id}"),
            ],
        ]
    )
    return post_kb


def get_edit_mg_kb(message_id):
    _kb = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="📝 Изменить текст", callback_data=f"mg_edit_text{message_id}"),
            ],
            [
                InlineKeyboardButton(text="🖼️ Изменить медиа", callback_data=f"mg_edit_media{message_id}"),
            ],
            [
                InlineKeyboardButton(text="📑 Изменить описание", callback_data=f"mg_edit_desc{message_id}"),
                InlineKeyboardButton(text="⏪ Назад", callback_data=f"mg_back_to_main{message_id}"),
            ]
        ]
    )
    return _kb


def back_edit_mg_kb(message_id):
    _kb = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="⏪ Назад", callback_data=f"mg_back_to_post{message_id}"),
            ]
        ]
    )
    return _kb


restore_post_kb = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="📝 Изменить текст", callback_data="edit_text"),
        ],
        [
            InlineKeyboardButton(text="🖼️ Изменить медиа", callback_data="edit_media"),
        ],
        [
            InlineKeyboardButton(text="📑 Изменить описание", callback_data="edit_desc"),
            InlineKeyboardButton(text="⏪ Назад", callback_data="back_to_main"),
        ]
    ]
)

publish_telegram_kb = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="✅ Отправить сейчас", callback_data="publish_now_tg"),
        ],
        [
            InlineKeyboardButton(text="⏳ Отправка по времени", callback_data="set_publish_time_tg"),
        ],
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="back_to_main"),
        ]
    ]
)


def publish_telegram_mg_kb(message_id):
    _kb = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="✅ Отправить сейчас", callback_data=f"mg_publish_now_tg{message_id}"),
            ],
            [
                InlineKeyboardButton(text="⏳ Отправка по времени", callback_data=f"mg_set_publish_time_tg{message_id}"),
            ],
            [
                InlineKeyboardButton(text="⏪ Назад", callback_data=f"mg_back_to_main{message_id}"),
            ]
        ]
    )
    return _kb


back_publish_tg = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="back_telegram_kb"),
        ]
    ]
)


def back_publish_mg_tg(messages_ids):
    _kb = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="⏪ Назад", callback_data=f"mgp_back_telegram_kb{messages_ids}"),
            ]
        ]
    )
    return _kb


back_edit_kb = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="back_to_edit"),
        ]
    ]
)

back_main_kb = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="back_to_main"),
        ]
    ]
)

back_sign_kb = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="back_to_sign_kb"),
        ]
    ]
)


def back_sign_mg_kb(message_id):
    _kb = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="⏪ Назад", callback_data=f"mg_back_sign_kb{message_id}"),
            ]
        ]
    )
    return _kb


back_sign_edit_kb = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="back_to_signatures"),
        ]
    ]
)


def back_sign_mg_edit_kb(sign_id, message_id):
    _kb = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="⏪ Назад", callback_data=f"back_mg_to_signatures{sign_id}|{message_id}"),
            ]
        ]
    )
    return _kb


admin_panel_kb = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="👨‍👨‍👦‍👦 Настройка пользователей", callback_data="edit_users"),
        ],
        [
            InlineKeyboardButton(text="📲 Настройка канала", callback_data="edit_channel"),
        ],
        [
            InlineKeyboardButton(text="⛔ Настройка шаблонов удаления", callback_data="sample_delete"),
        ],
        [
            InlineKeyboardButton(text="🕹️ Настройка чата", callback_data="edit_parser"),
            InlineKeyboardButton(text="❌ Закрыть", callback_data="delete_admin_panel"),
        ]
    ]
)

admin_panel_edit_users_kb = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="➕ Добавить", callback_data="edit_users_add"),
            InlineKeyboardButton(text="➖ Удалить", callback_data="edit_users_del"),
        ],
        [
            InlineKeyboardButton(text="⬆️ Повысить", callback_data="add_all_rights"),
            InlineKeyboardButton(text="⬇️ Понизить", callback_data="del_all_rights"),
        ],
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="back_admin_panel"),
        ],
    ]
)

back_edit_users_kb = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="back_edit_users"),
        ],
    ]
)

back_edit_channel_kb = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="back_edit_channel"),
        ],
    ]
)

admin_panel_edit_channel_kb = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="➕ Добавить", callback_data="edit_channel_add"),
            InlineKeyboardButton(text="➖ Удалить", callback_data="edit_channel_del"),
        ],
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="back_admin_panel"),
        ],
    ]
)

admin_panel_edit_parser_kb = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="📑 Изменить", callback_data="edit_edit_parser"),
        ],
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="back_admin_panel"),
        ],
    ]
)

back_edit_parser = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="back_edit_parser"),
        ],
    ]
)

back_admin_panel_kb = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="back_admin_panel"),
        ],
    ]
)


def get_sources_for_del():
    builder = InlineKeyboardBuilder()
    sources = get_sources()
    for _id, title in sources:
        builder.row(InlineKeyboardButton(text=f"🚫 {title}", callback_data=f"source_del_{_id}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data=f"back_add_sources"))
    return builder.as_markup()


def get_edit_signature_kb(signature_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Изменить подпись", callback_data=f"signature_text_edit_{signature_id}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data=f"back_to_signatures"))
    return builder.as_markup()


def get_edit_signature_mg_kb(signature_id, messages_ids):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Изменить подпись",
                             callback_data=f"mg_signature_text_edit_{signature_id}|{messages_ids}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data=f"mg_back_sign_kb{messages_ids}"))
    return builder.as_markup()


def get_signatures():
    builder = InlineKeyboardBuilder()
    signatures = get_all_signatures()
    for _id, title in signatures:
        builder.row(InlineKeyboardButton(text=clean_html(title), callback_data=f"edit_signature_{_id}"))
    builder.row(InlineKeyboardButton(text="➕ Добавить", callback_data=f"add_signature"),
                InlineKeyboardButton(text="➖ Удалить", callback_data=f"delete_signatures"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data=f"back_to_edit"))
    return builder.as_markup()


def get_signatures_mg(message_id):
    builder = InlineKeyboardBuilder()
    signatures = get_all_signatures()
    for _id, title in signatures:
        builder.row(InlineKeyboardButton(text=clean_html(title), callback_data=f"mg_edit_signature_{_id}|{message_id}"))
    builder.row(InlineKeyboardButton(text="➕ Добавить", callback_data=f"mg_add_signature{message_id}"),
                InlineKeyboardButton(text="➖ Удалить", callback_data=f"pmg_delete_signatures{message_id}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data=f"mg_back_to_post{message_id}"))
    return builder.as_markup()


def get_signatures_for_del():
    builder = InlineKeyboardBuilder()
    signatures = get_all_signatures()
    for _id, title in signatures:
        builder.row(InlineKeyboardButton(text=f"🚫 {clean_html(title)}", callback_data=f"signature_del_{_id}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data=f"back_to_sign_kb"))
    return builder.as_markup()


def get_signatures_for_del_mg(message_id):
    builder = InlineKeyboardBuilder()
    signatures = get_all_signatures()
    for _id, title in signatures:
        builder.row(
            InlineKeyboardButton(text=f"🚫 {clean_html(title)}", callback_data=f"mg_signature_del_{_id}|{message_id}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data=f"mg_back_sign_kb{message_id}"))
    return builder.as_markup()


def get_started_kb(_type):
    builder = InlineKeyboardBuilder()
    parsers = get_sources()
    for _id, title in parsers:
        if get_parser_info(title):
            builder.row(InlineKeyboardButton(text=f"✅ {title}", callback_data=f"{_type}_source_{title}"))
        else:
            builder.row(InlineKeyboardButton(text=f"❌ {title}", callback_data=f"{_type}_source_{title}"))
    if _type == "start":
        builder.row(InlineKeyboardButton(text="✅ Запустить все ✅", callback_data=f"start_all_parser"))
    else:
        builder.row(InlineKeyboardButton(text="❌ Остановить все ❌", callback_data=f"stop_all_parser"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data=f"back_add_sources"))
    return builder.as_markup()


def set_signature_for_post_kb(message_id):
    builder = InlineKeyboardBuilder()
    signatures = get_all_signatures()
    for _id, title in signatures:
        builder.row(InlineKeyboardButton(text=f"  {clean_html(title)}  ", callback_data=f"add_sign_{_id}|{message_id}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data=f"back_to_main"))
    return builder.as_markup()


def set_signature_for_post_mg_kb(message_id):
    builder = InlineKeyboardBuilder()
    signatures = get_all_signatures()
    for _id, title in signatures:
        builder.row(
            InlineKeyboardButton(text=f"  {clean_html(title)}  ", callback_data=f"mg_add_sign_{_id}|{message_id}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data=f"mg_back_to_main{message_id}"))
    return builder.as_markup()


def delete_users_with_rights():
    builder = InlineKeyboardBuilder()
    users = get_users_with_rights()
    for user_id, username, rights_post, rights_all in users:
        if rights_post and not rights_all:
            builder.row(InlineKeyboardButton(text=f"✏️ {username} {user_id}", callback_data=f"rights_delete_{user_id}"))
        else:
            builder.row(InlineKeyboardButton(text=f"🔓 {username} {user_id}", callback_data=f"rights_delete_{user_id}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data="back_edit_users"))
    return builder.as_markup()


def add_all_rights_kb():
    builder = InlineKeyboardBuilder()
    users = get_users_with_rights()
    for user_id, username, rights_post, rights_all in users:
        if rights_post and not rights_all:
            builder.row(
                InlineKeyboardButton(text=f"✏️ {username} {user_id}", callback_data=f"rights_add_all_{user_id}"))
        else:
            builder.row(InlineKeyboardButton(text=f"🔓 {username} {user_id}", callback_data=f"rights_add_all_{user_id}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data="back_edit_users"))
    return builder.as_markup()


def del_all_rights_kb():
    builder = InlineKeyboardBuilder()
    users = get_users_with_rights()
    for user_id, username, rights_post, rights_all in users:
        if rights_post and not rights_all:
            builder.row(
                InlineKeyboardButton(text=f"✏️ {username} {user_id}", callback_data=f"rights_del_all_{user_id}"))
        else:
            builder.row(InlineKeyboardButton(text=f"🔓 {username} {user_id}", callback_data=f"rights_del_all_{user_id}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data="back_edit_users"))
    return builder.as_markup()


def delete_channels_kb():
    builder = InlineKeyboardBuilder()
    channels = select_channels_publish()
    for channel_username, channel_id in channels:
        builder.row(InlineKeyboardButton(text=f"{channel_username}", callback_data=f"channel_del_{channel_id}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data="back_edit_channel"))
    return builder.as_markup()


def get_samples_kb():
    builder = InlineKeyboardBuilder()
    samples = select_samples()
    for _id, text in samples:
        builder.row(InlineKeyboardButton(text=f"{clean_html(text)}", callback_data=f"get_sample_{_id}"))
    builder.row(InlineKeyboardButton(text="➕ Добавить", callback_data=f"add_sample"),
                InlineKeyboardButton(text="➖ Удалить", callback_data=f"delete_sample"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data="back_admin_panel"))
    return builder.as_markup()


def delete_samples():
    builder = InlineKeyboardBuilder()
    samples = select_samples()
    for _id, text in samples:
        builder.row(InlineKeyboardButton(text=f"🚫 {clean_html(text)}", callback_data=f"samp_delete_{_id}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data="back_admin_panel"))
    return builder.as_markup()
