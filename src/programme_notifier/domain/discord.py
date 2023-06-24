"""Domain models for Discord webhook messages."""
import textwrap
from collections.abc import Sequence
from typing import Any, Final

import attrs
from attrs import validators

from programme_notifier.domain import conference

_EMTPY_CHAR: Final = "—"

# Discord limits that cannot be exceeded
_MAX_LEN: Final[dict[str, Any]] = {
    "title": validators.max_len(256),
    "description": validators.max_len(2000),
    "field_name": validators.max_len(256),
    "field_value": validators.max_len(1024),
    "fields": validators.max_len(25),
    "footer": validators.max_len(2048),
    "author_name": validators.max_len(256),
}

# Width preferences for the embed
_WIDTH: Final = {
    "title": 100,
    "description": 300,
    "field_value": 64,
    "footer": 128,
    "author_name": 256,
}


@attrs.define(frozen=True)
class Embed:
    """A Discord embed."""

    title: str = attrs.field(validator=_MAX_LEN["title"])
    author: "EmbedAuthor | None"
    description: str | None = attrs.field(validator=_MAX_LEN["description"])
    fields: "list[EmbedField] | None" = attrs.field(validator=_MAX_LEN["fields"])
    footer: "EmbedFooter | None"

    @classmethod
    def from_session(cls, session: conference.Session) -> "Embed":
        """Create an embed from a conference session.

        :param session: The session providing the information
        :return: An embed with information about the session
        """
        return cls(
            title=textwrap.shorten(session.title, width=_WIDTH["title"]),
            author=EmbedAuthor.from_speakers(session.speakers),
            description=textwrap.shorten(session.abstract, width=_WIDTH["description"]),
            fields=EmbedField.fields_from_session(session=session),
            footer=EmbedFooter.from_session(session=session),
        )


@attrs.define(frozen=True)
class EmbedField:
    """A field for a Discord embed."""

    name: str = attrs.field(validator=_MAX_LEN["field_name"])
    value: str = attrs.field(validator=_MAX_LEN["field_value"])
    inline: bool

    @classmethod
    def fields_from_session(cls, session: conference.Session) -> "list[EmbedField]":
        """Create a list of EmbedFields representing the session.

        :param session: The session providing the information
        :return: a list of EmbedFields representing the session
        """
        start_time = f"<t:{session.start.int_timestamp}:f>"
        room = session.room.name or _EMTPY_CHAR
        track = session.track or _EMTPY_CHAR
        length = f"{session.duration} minutes" if session.duration else _EMTPY_CHAR
        livestream = (
            f"[YouTube]({session.room.livestream_url})"
            if session.room.livestream_url
            else _EMTPY_CHAR
        )
        discord_channel = (
            f"<#{session.room.discord_channel_id}>"
            if session.room.discord_channel_id
            else _EMTPY_CHAR
        )
        return [
            EmbedField(name="Start Time", value=start_time, inline=True),
            EmbedField(name="Room", value=room, inline=True),
            EmbedField(name="Track", value=track, inline=True),
            EmbedField(name="Length", value=length, inline=True),
            EmbedField(name="Livestream", value=livestream, inline=True),
            EmbedField(name="Discord Channel", value=discord_channel, inline=True),
        ]


@attrs.define(frozen=True)
class EmbedFooter:
    """A field for a Discord embed."""

    text: str = attrs.field(validator=_MAX_LEN["footer"])

    @classmethod
    def from_session(cls, session: conference.Session) -> "EmbedFooter":
        """Create an EmbedFooter instance from a session instance.

        :param session: The session instance providing the information
        :return: An instance of EmbedFooter
        """
        local_start_time = session.start.format("HH:mm:ss")
        footer = f"This session starts at {local_start_time} (local conference time)"
        return cls(text=textwrap.shorten(footer, width=_WIDTH["footer"]))


@attrs.define(frozen=True)
class EmbedAuthor:
    """A field for a Discord embed."""

    name: str = attrs.field(validator=_MAX_LEN["author_name"])
    icon_url: str | None = None

    @classmethod
    def from_speakers(
        cls, speakers: Sequence[conference.Speaker]
    ) -> "EmbedAuthor | None":
        """Create an embed author from a list of speakers.

        :param speakers: A list of speakers
        :return: An instance of EmbedAuthor
        """
        match speakers:
            case [speaker]:
                name = speaker.name
            case [speaker_one, speaker_two]:
                name = f"{speaker_one.name} & {speaker_two.name}"
            case [*first, last_speaker]:
                first_speakers = ", ".join(speaker.name for speaker in first)
                name = f"{first_speakers}, & {last_speaker.name}"
            case _:
                return None

        # Since an embed only supports one author icon, the avatar of
        # the first speaker with an avatar is used as the author icon.
        icon_url = next(
            (speaker.avatar for speaker in speakers if speaker.avatar), None
        )
        return cls(
            name=textwrap.shorten(name, width=_WIDTH["author_name"]), icon_url=icon_url
        )
