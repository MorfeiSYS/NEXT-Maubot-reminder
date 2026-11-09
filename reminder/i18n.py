from typing import Literal, Optional

Lang = Literal["en", "ru"]

STRINGS = {
    "past_date": {
        "en": "Sorry, {date} is in the past and I don't have a time machine :(",
        "ru": "Извините, {date} уже в прошлом, машины времени у меня нет :(",
    },
    "reschedule_need_reply": {
        "en": "You must reply to a reminder event to reschedule it.",
        "ru": "Ответьте на сообщение с напоминанием, чтобы перенести его.",
    },
    "invalid_reminder_event": {
        "en": "That doesn't look like a valid reminder event.",
        "ru": "Это не похоже на корректное напоминание.",
    },
    "remind_confirm_footer": {
        "en": "(others can \U0001f44d this message to get pinged too)",
        "ru": "(другие могут поставить \U0001f44d на это сообщение, чтобы тоже получить уведомление)",
    },
    "remind_confirm_intro": {
        "en": "I'll {action} {when}.",
        "ru": "Я {action} {when}.",
    },
    "help_header": {
        "en": "Maubot Reminder plugin (NEXT-Maubot-reminder).\n\n",
        "ru": "Плагин напоминаний Maubot (NEXT-Maubot-reminder).\n\n",
    },
    "help_cmd_add": {
        "en": "* !{cmd} <date> <message> - Add a reminder\n",
        "ru": "* !{cmd} <дата> <текст> — создать напоминание\n",
    },
    "help_cmd_again": {
        "en": "* !{cmd} again <date> - Reply to a reminder to reschedule it\n",
        "ru": "* !{cmd} снова <дата> — ответ на напоминание, чтобы перенести\n",
    },
    "help_cmd_list": {
        "en": "* !{cmd} list - Get a list of your reminders\n",
        "ru": "* !{cmd} list — список ваших напоминаний\n",
    },
    "help_cmd_tz": {
        "en": "* !{cmd} tz <timezone> - Set your time zone\n",
        "ru": "* !{cmd} tz <часовой пояс> — задать часовой пояс\n",
    },
    "help_cmd_locale": {
        "en": "* !{cmd} locale <locale> - Set your locale\n",
        "ru": "* !{cmd} locale <локаль> — задать локаль для дат\n",
    },
    "help_cmd_locales": {
        "en": "* !{cmd} locales - List available locales\n\n",
        "ru": "* !{cmd} locales — список доступных локалей\n\n",
    },
    "help_dates": {
        "en": (
            "<date> can be a time delta (e.g. `2 days 1.5 hours` or `friday at 15:00`) "
            "or an absolute date (e.g. `2020-03-27 15:00`)\n\n"
        ),
        "ru": (
            "<дата> — интервал (например `2 дня 1.5 часа` или `пятница в 15:00`) "
            "или абсолютная дата (например `2026-03-27 15:00`)\n\n"
        ),
    },
    "help_react": {
        "en": "To get mentioned by a reminder added by someone else, upvote the message "
        "by reacting with \U0001f44d.\n\n",
        "ru": "Чтобы получать чужое напоминание, поставьте реакцию \U0001f44d на его сообщение.\n\n",
    },
    "help_cancel": {
        "en": "To cancel a reminder, remove the message or reaction.",
        "ru": "Чтобы отменить напоминание, удалите сообщение или реакцию.",
    },
    "list_empty": {
        "en": "You have no {scope} :(",
        "ru": "У вас нет {scope} :(",
    },
    "list_header": {
        "en": "Your {scope}:\n\n{items}",
        "ru": "Ваши {scope}:\n\n{items}",
    },
    "list_scope_base": {
        "en": "upcoming reminders",
        "ru": "предстоящих напоминаний",
    },
    "list_scope_room": {
        "en": " in this room",
        "ru": " в этой комнате",
    },
    "locales_header": {
        "en": "Available locales:\n\n",
        "ru": "Доступные локали:\n\n",
    },
    "locale_current": {
        "en": "Your locale is {names}",
        "ru": "Ваша локаль: {names}",
    },
    "locale_unsupported": {
        "en": "Locale `{locale_id}` is not supported",
        "ru": "Локаль `{locale_id}` не поддерживается",
    },
    "locale_set": {
        "en": "Set your locale to {names}",
        "ru": "Локаль установлена: {names}",
    },
    "locale_unset": {
        "en": "unset",
        "ru": "не задана",
    },
    "locale_join_and": {
        "en": " and ",
        "ru": " и ",
    },
    "locale_join_comma": {
        "en": ", ",
        "ru": ", ",
    },
    "tz_current": {
        "en": "Your time zone is {zone}",
        "ru": "Ваш часовой пояс: {zone}",
    },
    "tz_set": {
        "en": "Set your timezone to {zone}",
        "ru": "Часовой пояс установлен: {zone}",
    },
    "current_time": {
        "en": "Your current time: {clock} ({zone})",
        "ru": "Сейчас у вас: {clock} (пояс {zone})",
    },
    "bad_date": {
        "en": "I couldn't understand the date/time. Try `!{cmd} help` or examples like `2 days` / `friday 15:00`.",
        "ru": "Не удалось разобрать дату/время. Напишите `!{cmd} help` или, например, `2 дня` / `пятница 15:00`.",
    },
    "meta_remind": {
        "en": "Create a reminder",
        "ru": "Создать напоминание",
    },
    "meta_for": {
        "en": "Create a reminder for another user",
        "ru": "Создать напоминание для другого пользователя",
    },
    "meta_reschedule": {
        "en": "Reschedule a reminder you got",
        "ru": "Перенести полученное напоминание",
    },
    "meta_help": {
        "en": "Usage instructions",
        "ru": "Справка по использованию",
    },
    "meta_list": {
        "en": "List your reminders",
        "ru": "Список ваших напоминаний",
    },
    "meta_locales": {
        "en": "List available locales",
        "ru": "Список доступных локалей",
    },
    "meta_locale": {
        "en": "Set your locale",
        "ru": "Задать локаль",
    },
    "meta_timezone": {
        "en": "Set your timezone",
        "ru": "Задать часовой пояс",
    },
}

# Maubot command decorators accept a static help= string only (no per-room locale).
META_LANG: Lang = "ru"


def t(key: str, lang: Lang, **kwargs: str) -> str:
    block = STRINGS[key]
    text = block.get(lang) or block["en"]
    if kwargs:
        return text.format(**kwargs)
    return text


def cmd_meta(key: str) -> str:
    return t(key, META_LANG)


def cmd_name(lang: Lang, base_command: str) -> str:
    return "напомни" if lang == "ru" else base_command


def fmt_locales_join(names: list[str], lang: Lang) -> str:
    if len(names) == 0:
        return t("locale_unset", lang)
    if len(names) == 1:
        return names[0]
    comma = t("locale_join_comma", lang)
    conj = t("locale_join_and", lang)
    return comma.join(names[:-1]) + conj + names[-1]


def build_remind_action(
    lang: Lang,
    *,
    recipient: str,
    again: bool,
    message: Optional[str],
    reply_to: bool,
    evt_link: str,
) -> str:
    if lang == "ru":
        who = {
            "you": "тебе",
            "your descendants": "твоим потомкам",
        }.get(recipient, f"пользователю {recipient}")
        if recipient.endswith("'s descendants"):
            who = f"потомкам {recipient.removesuffix("'s descendants")}"
        if not message and not reply_to:
            base = "отправлю тебе пинг"
        else:
            base = f"напомню {who}"
            if reply_to:
                if message:
                    base += f" про «{message}» (с ответом на {evt_link})"
                else:
                    base += f" про {evt_link}"
            elif message:
                base += f" про «{message}»"
        if again:
            base += " снова"
        return base
    if recipient == "your descendants":
        who = "your descendants"
    elif recipient.endswith("'s descendants"):
        who = recipient
    elif recipient == "you":
        who = "you"
    else:
        who = recipient
    if not message and not reply_to:
        base = "ping you"
    else:
        base = f"remind {who} "
        if reply_to:
            if message:
                base += f"to {message} (replying to that {evt_link})"
            else:
                base += f"about that {evt_link}"
        elif message:
            base += f"to {message}"
    if again:
        base += " again"
    return base
