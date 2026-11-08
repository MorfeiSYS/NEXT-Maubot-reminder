# NEXT-Maubot-reminder

Плагин [maubot](https://github.com/maubot/maubot) для напоминаний в Matrix. Поддерживает русский и английский: команды `!напомни` и `!remind`, автоопределение языка комнаты.

## Использование

Создать напоминание: `!напомни <дата> <текст>` или `!remind <date> <message>`.

Чтобы подписаться на чужое напоминание, поставьте реакцию 👍. Отмена — удалите сообщение или реакцию. После срабатывания можно перенести время: ответьте на событие напоминания и напишите `!напомни снова <дата>` / `!remind again <date>`.

`<дата>` — интервал (например `2 дня 1 час`, `через 30 минут`, `пятница в 15:00`) или абсолютная дата (`2026-03-27 15:00`).

Подписка и отмена возможны до последней минуты до срабатывания.

Часовой пояс: `!напомни tz <timezone>` — IANA (`Europe/Moscow`, `Asia/Yakutsk`) или смещение (`UTC+9`, `GMT+05:30`). В конфиге инстанса то же для `default_timezone` (см. [`base-config.yaml`](base-config.yaml)).

Локаль для разбора дат: `!напомни locale <список>` (для русского чата подойдёт `ru_ru`; список: `!напомни locales`).

Список ваших напоминаний: `!напомни list`.

### Язык в комнате

Бот переключает язык ответов по контексту комнаты:

- команда `!напомни` или сообщения с кириллицей → русский;
- `!remind` / `!reminder` или длинная серия сообщений только латиницей → английский.

## Сборка (Windows)

Идентификатор плагина в Maubot: **NEXT-reminder** (вместо upstream `xyz.maubot.reminder`).

Нужен [maubot-cli](https://docs.mau.fi/maubot/usage/cli/build.html) (`mbc` в PATH). Версия релиза — в файле [`VERSION`](VERSION) (сейчас 1.0.2).

```powershell
.\build\build.ps1
```

Артефакт: `build/NEXT-Maubot-reminder-v1.0.2.mbp` (номер версии из `VERSION`).

Следующий патч-релиз и синхронизация `maubot.yaml`:

```powershell
.\build\build.ps1 -BumpPatch
```

Загрузите `.mbp` в веб-интерфейс maubot.

---

# English

A [maubot](https://github.com/maubot/maubot) plugin to remind you about things. This fork adds Russian UI, `!напомни`, and room language detection.

## Hosted instances (upstream)

* maunium.net: [@reminder:maunium.net](https://matrix.to/#/@reminder:maunium.net).
* t2bot.io: https://t2bot.io/reminderbot/

## Usage

Use `!remind <date> <message>` or `!напомни <дата> <текст>` to set a reminder. To subscribe to a reminder set by someone else,
upvote the message with a 👍 reaction. To cancel a reminder, remove the message or reaction.
After the reminder fires, you can re-schedule it with `!reminder again <date>`.

`<date>` can be a time delta (e.g. `2 days 1.5 hours` or `friday at 15:00`)
or an absolute date (e.g. `2020-03-27 15:00`).

To set the timezone for date parsing and output for your messages, use `!remind tz <timezone>`.
Similarly, use `!remind locale <list of locales>` for parsing (`ru_ru` for Russian). View locales with `!remind locales`.

To list your upcoming reminders, use `!remind list`.

Room language follows Russian/English heuristics (Cyrillic, `!напомни`, `!remind`, etc.).

## Build

Requires `mbc` in PATH. Version is in [`VERSION`](VERSION).

```powershell
.\build\build.ps1
```

Output: `build/NEXT-Maubot-reminder-v<version>.mbp`.
