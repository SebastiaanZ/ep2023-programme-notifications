"""Domain models related to conference sessions."""
import arrow
import attrs


@attrs.define(frozen=True)
class Session:
    """A conference session."""

    title: str
    speakers: "list[Speaker]"
    abstract: str
    track: str
    start: arrow.Arrow
    duration: int
    room: "Room"


@attrs.define(frozen=True)
class Speaker:
    """A speaker associated with a session."""

    name: str
    avatar: str


@attrs.define(frozen=True)
class Room:
    """A room in which sessions are held."""

    name: str
    livestream_url: str
    discord_channel_id: int | None
