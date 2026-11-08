# reminder - A maubot plugin to remind you about things.
# Copyright (C) 2020 Tulir Asokan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from typing import List, Tuple, Type
from datetime import datetime, timedelta
from html import escape
import asyncio

import pytz

from maubot import MessageEvent, Plugin
from maubot.handlers import command, event
from mautrix.types import (
    EventType,
    Format,
    MessageType,
    ReactionEvent,
    RedactionEvent,
    StateEvent,
    TextMessageEventContent,
    UserID,
)
from mautrix.util import background_task
from mautrix.util.config import BaseProxyConfig

from .db import ReminderDatabase
from .i18n import Lang, build_remind_action, cmd_name, fmt_locales_join, t
from .locales import locales
from .util import Config, DateArgument, ReminderInfo, format_time, parse_timezone


class ReminderBot(Plugin):
    db: ReminderDatabase
    reminder_loop_task: asyncio.Future
    base_command: str
    base_aliases: Tuple[str, ...]
    default_timezone: pytz.timezone

    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config

    async def start(self) -> None:
        self.on_external_config_update()
        self.db = ReminderDatabase(self.database)
        self.reminder_loop_task = asyncio.create_task(self.reminder_loop())

    def on_external_config_update(self) -> None:
        self.config.load_and_update()
        bc = self.config["base_command"]
        self.base_command = bc[0] if isinstance(bc, list) else bc
        self.base_aliases = tuple(bc) if isinstance(bc, list) else (bc,)
        raw_timezone = self.config["default_timezone"]
        try:
            self.default_timezone = pytz.timezone(raw_timezone)
        except pytz.UnknownTimeZoneError:
            self.log.warning(f"Unknown default timezone {raw_timezone}")
            self.default_timezone = pytz.UTC

    async def stop(self) -> None:
        self.reminder_loop_task.cancel()

    def _lang(self, room_id) -> Lang:
        return self.db.get_room_lang(room_id)

    async def reply_l(self, evt: MessageEvent, key: str, **kwargs: str) -> None:
        await evt.reply(t(key, self._lang(evt.room_id), **kwargs))

    async def reminder_loop(self) -> None:
        try:
            self.log.debug("Reminder loop started")
            while True:
                now = datetime.now(tz=pytz.UTC)
                next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
                await asyncio.sleep((next_minute - now).total_seconds())
                await self.schedule_nearby_reminders(next_minute)
        except asyncio.CancelledError:
            self.log.debug("Reminder loop stopped")
        except Exception:
            self.log.exception("Exception in reminder loop")

    async def schedule_nearby_reminders(self, now: datetime) -> None:
        until = now + timedelta(minutes=1)
        for reminder in self.db.all_in_range(now, until):
            background_task.create(self.send_reminder(reminder))

    async def send_reminder(self, reminder: ReminderInfo) -> None:
        try:
            await self._send_reminder(reminder)
        except Exception:
            self.log.exception("Failed to send reminder")

    async def _send_reminder(self, reminder: ReminderInfo) -> None:
        if len(reminder.users) == 0:
            self.log.debug(f"Cancelling reminder {reminder}, no users left to remind")
            return
        wait = (reminder.date - datetime.now(tz=pytz.UTC)).total_seconds()
        if wait > 0:
            self.log.debug(f"Waiting {wait} seconds to send {reminder}")
            await asyncio.sleep(wait)
        else:
            self.log.debug(f"Sending {reminder} immediately")
        users = " ".join(reminder.users)
        users_html = " ".join(
            f"<a href='https://matrix.to/#/{user_id}'>{user_id}</a>" for user_id in reminder.users
        )
        content = TextMessageEventContent(
            msgtype=MessageType.TEXT,
            body=f"{users}: {reminder.message}",
            format=Format.HTML,
            formatted_body=f"{users_html}: {escape(reminder.message)}",
        )
        content["xyz.maubot.reminder"] = {
            "id": reminder.id,
            "message": reminder.message,
            "targets": list(reminder.users),
            "reply_to": reminder.reply_to,
        }
        if reminder.reply_to:
            content.set_reply(await self.client.get_event(reminder.room_id, reminder.reply_to))
        await self.client.send_message(reminder.room_id, content)

    @event.on(EventType.ROOM_MESSAGE)
    async def on_room_message(self, evt: MessageEvent) -> None:
        if evt.sender == self.client.mxid:
            return
        body = evt.content.body or ""
        if body.startswith("!"):
            self.db.touch_room_lang_from_command(evt.room_id, body)
            return
        if evt.content.msgtype == MessageType.TEXT:
            self.db.touch_room_lang_from_message(evt.room_id, body)

    @command.new(
        name=lambda self: self.base_command,
        aliases=lambda self, alias: alias in self.base_aliases,
        help="Create a reminder",
        require_subcommand=False,
        arg_fallthrough=False,
    )
    @DateArgument("date", required=True)
    @command.argument("message", pass_raw=True, required=False)
    async def remind(self, evt: MessageEvent, date: datetime, message: str) -> None:
        date = date.replace(microsecond=0)
        now = datetime.now(tz=pytz.UTC).replace(microsecond=0)
        lang = self._lang(evt.room_id)
        if date < now:
            await self.reply_l(evt, "past_date", date=str(date))
            return
        rem = ReminderInfo(
            date=date,
            room_id=evt.room_id,
            message=message,
            reply_to=evt.content.get_reply_to(),
            users={evt.sender: evt.event_id},
        )
        await self._remind(evt, rem, now)

    @remind.subcommand("for", help="Create a reminder for another user")
    @command.argument("user_id", required=True, matches="@[^:]*:[a-zA-Z0-9.-]{1,255}(?::\d{1,5})?")
    @DateArgument("date", required=True)
    @command.argument("message", pass_raw=True, required=False)
    async def remind_for(
        self, evt: MessageEvent, user_id: UserID, date: datetime, message: str
    ) -> None:
        date = date.replace(microsecond=0)
        now = datetime.now(tz=pytz.UTC).replace(microsecond=0)
        if date < now:
            await self.reply_l(evt, "past_date", date=str(date))
            return
        rem = ReminderInfo(
            date=date,
            room_id=evt.room_id,
            message=message,
            reply_to=evt.event_id,
            users={user_id: evt.event_id},
        )
        await self._remind(evt, rem, now, recipient=user_id.split(":")[0].removeprefix("@"))

    @remind.subcommand("reschedule", help="Reschedule a reminder you got", aliases=("again",))
    @DateArgument("date", required=True)
    async def reschedule(self, evt: MessageEvent, date: datetime) -> None:
        reply_to_id = evt.content.get_reply_to()
        if not reply_to_id:
            await self.reply_l(evt, "reschedule_need_reply")
            return
        date = date.replace(microsecond=0)
        now = datetime.now(tz=pytz.UTC).replace(microsecond=0)
        if date < now:
            await self.reply_l(evt, "past_date", date=str(date))
            return
        reply_to = await self.client.get_event(evt.room_id, reply_to_id)
        try:
            reminder_info = reply_to.content["xyz.maubot.reminder"]
            rem = ReminderInfo(
                date=date,
                room_id=evt.room_id,
                message=reminder_info["message"],
                reply_to=reminder_info["reply_to"],
                users={evt.sender: evt.event_id},
            )
        except KeyError:
            await self.reply_l(evt, "invalid_reminder_event")
            return
        await self._remind(evt, rem, now, again=True)

    async def _remind(
        self,
        evt: MessageEvent,
        rem: ReminderInfo,
        now: datetime,
        again: bool = False,
        recipient: str = "you",
    ) -> None:
        lang = self._lang(evt.room_id)
        if rem.date == now:
            await self.send_reminder(rem)
            return
        if rem.date.year > now.year + 125:
            if recipient == "you":
                recipient = "your descendants"
            else:
                recipient = f"{recipient}'s descendants"
        evt_link = ""
        if rem.reply_to:
            evt_link = f"[event](https://matrix.to/#/{rem.room_id}/{rem.reply_to})"
        action = build_remind_action(
            lang,
            recipient=recipient,
            again=again,
            message=rem.message,
            reply_to=bool(rem.reply_to),
            evt_link=evt_link,
        )
        if not rem.message and not rem.reply_to:
            rem.message = "ping"
        when = self.format_time(evt.sender, rem)
        msg = (
            t("remind_confirm_intro", lang, action=action, when=when)
            + "\n\n"
            + t("remind_confirm_footer", lang)
        )
        rem.event_id = await evt.reply(msg)
        self.db.insert(rem)
        now = datetime.now(tz=pytz.UTC)
        if (rem.date - now).total_seconds() < 60 and now.minute == rem.date.minute:
            self.log.debug(f"Reminder {rem} is in less than a minute, scheduling now...")
            background_task.create(self.send_reminder(rem))

    @remind.subcommand("help", help="Usage instructions")
    async def help(self, evt: MessageEvent) -> None:
        lang = self._lang(evt.room_id)
        cmd = cmd_name(lang, self.base_command)
        await evt.reply(
            t("help_header", lang)
            + t("help_cmd_add", lang, cmd=cmd)
            + t("help_cmd_again", lang, cmd=cmd)
            + t("help_cmd_list", lang, cmd=cmd)
            + t("help_cmd_tz", lang, cmd=cmd)
            + t("help_cmd_locale", lang, cmd=cmd)
            + t("help_cmd_locales", lang, cmd=cmd)
            + t("help_dates", lang)
            + t("help_react", lang)
            + t("help_cancel", lang)
        )

    @remind.subcommand("list", help="List your reminders")
    @command.argument("all", required=False)
    async def list(self, evt: MessageEvent, all: str) -> None:
        lang = self._lang(evt.room_id)
        room_id = evt.room_id
        if "all" in all:
            room_id = None

        def format_rem(rem: ReminderInfo) -> str:
            if rem.reply_to:
                evt_link = f"[event](https://matrix.to/#/{rem.room_id}/{rem.reply_to})"
                if rem.message:
                    return f'"{rem.message}" (replying to {evt_link})'
                return evt_link
            return f'"{rem.message}"'

        reminders_str = "\n".join(
            f"* {format_rem(reminder)} {self.format_time(evt.sender, reminder)}"
            for reminder in self.db.all_for_user(evt.sender, room_id=room_id)
        )
        scope = t("list_scope_base", lang)
        if room_id:
            scope += t("list_scope_room", lang)
        if len(reminders_str) == 0:
            await self.reply_l(evt, "list_empty", scope=scope)
        else:
            await evt.reply(t("list_header", lang, scope=scope, items=reminders_str))

    def format_time(self, sender: UserID, reminder: ReminderInfo, room_id=None) -> str:
        lang = self._lang(room_id or reminder.room_id)
        tz_date = reminder.date.astimezone(self.db.get_timezone(sender))
        return format_time(tz_date, lang=lang)

    @remind.subcommand("locales", help="List available locales")
    async def locales(self, evt: MessageEvent) -> None:
        lang = self._lang(evt.room_id)

        def _format_key(key: str) -> str:
            language, country = key.split("_")
            return f"{language.lower()}_{country.upper()}"

        await evt.reply(
            t("locales_header", lang)
            + "\n".join(
                f"* `{_format_key(key)}` - {locale.name}" for key, locale in locales.items()
            )
        )

    @staticmethod
    def _fmt_locales(locale_ids: List[str], lang: Lang) -> str:
        locale_names = [locales[id].name for id in locale_ids if id in locales]
        return fmt_locales_join(locale_names, lang)

    @remind.subcommand("locale", help="Set your locale")
    @command.argument("locale", required=False, pass_raw=True)
    async def locale(self, evt: MessageEvent, locale: str) -> None:
        lang = self._lang(evt.room_id)
        if not locale:
            names = self._fmt_locales(self.db.get_locales(evt.sender), lang)
            await self.reply_l(evt, "locale_current", names=names)
            return
        locale_ids = [part.strip() for part in locale.lower().split(" ")]
        for locale_id in locale_ids:
            if locale_id not in locales:
                await self.reply_l(evt, "locale_unsupported", locale_id=locale_id)
                return
        self.db.set_locales(evt.sender, locale_ids)
        names = self._fmt_locales(locale_ids, lang)
        await self.reply_l(evt, "locale_set", names=names)

    @remind.subcommand("timezone", help="Set your timezone", aliases=("tz",))
    @command.argument("timezone", parser=parse_timezone, required=False)
    async def timezone(self, evt: MessageEvent, timezone: pytz.timezone) -> None:
        if not timezone:
            await self.reply_l(evt, "tz_current", zone=self.db.get_timezone(evt.sender).zone)
            return
        self.db.set_timezone(evt.sender, timezone)
        await self.reply_l(evt, "tz_set", zone=timezone.zone)

    @command.passive(
        regex=r"(?:\U0001F44D[\U0001F3FB-\U0001F3FF]?)",
        field=lambda evt: evt.content.relates_to.key,
        event_type=EventType.REACTION,
        msgtypes=None,
    )
    async def subscribe_react(self, evt: ReactionEvent, _: Tuple[str]) -> None:
        reminder = self.db.get_by_event_id(evt.content.relates_to.event_id)
        if reminder:
            self.db.add_user(reminder, evt.sender, evt.event_id)

    @event.on(EventType.ROOM_REDACTION)
    async def redact(self, evt: RedactionEvent) -> None:
        self.db.redact_event(evt.redacts)

    @event.on(EventType.ROOM_TOMBSTONE)
    async def tombstone(self, evt: StateEvent) -> None:
        if not evt.content.replacement_room:
            return
        self.db.update_room_id(evt.room_id, evt.content.replacement_room)
