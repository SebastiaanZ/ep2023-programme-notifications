"""Tests for the domain logic converting a session into an embed."""
from collections.abc import Callable

import arrow
import attrs
import pytest

from programme_notifier.domain import conference, discord


def test_creates_embed_from_session() -> None:
    """An embed can be created from a session instance."""
    # GIVEN a session
    session = conference.Session(
        title="How to return values from functions",
        abstract=(
            "Did you ever struggle to get a value out of a function? Did you ever"
            " have to resort to hacks with `global` just to be able to use the result"
            " of a function? Learn how you can do that and more without having to"
            " resort to hacks using Python's `return` statement."
        ),
        track="Education, Teaching & Training",
        start=arrow.get("2023-07-20T14:05:00+02:00"),
        duration=30,
        room=conference.Room(
            name="South Hall 2A",
            livestream_url="https://www.youtube.com/watch?v=k8MT5liCQ7g",
            discord_channel_id=1122150822168502312,
        ),
        speakers=[
            conference.Speaker(
                name="John Speaker",
                avatar="https://pretalx.com/media/avatars/OMOTOLA_Picture_YdYRpKd.png",
            )
        ],
    )

    # WHEN the session is converted to an embed payload
    payload = discord.Embed.from_session(session)

    # THEN the payload is equal to the expected embed
    assert payload == discord.Embed(
        title="How to return values from functions",
        description=session.abstract,
        author=discord.EmbedAuthor(
            name=session.speakers[0].name,
            icon_url=session.speakers[0].avatar,
        ),
        fields=[
            discord.EmbedField(
                name="Start Time", value="<t:1689854700:f>", inline=True
            ),
            discord.EmbedField(name="Room", value="South Hall 2A", inline=True),
            discord.EmbedField(
                name="Track", value="Education, Teaching & Training", inline=True
            ),
            discord.EmbedField(name="Length", value="30 minutes", inline=True),
            discord.EmbedField(
                name="Livestream",
                value="[YouTube](https://www.youtube.com/watch?v=k8MT5liCQ7g)",
                inline=True,
            ),
            discord.EmbedField(
                name="Discord Channel",
                value="<#1122150822168502312>",
                inline=True,
            ),
        ],
        footer=discord.EmbedFooter(
            text="This session starts at 14:05:00 (local conference time)"
        ),
    )

    as_dict = attrs.asdict(payload)
    print(as_dict)


@pytest.mark.parametrize(
    ("session_field", "session_value", "embed_field", "embed_value"),
    [
        pytest.param(
            "title",
            (
                "This talk has a very long title that needs to be truncated to fit the"
                " embed that we want to display to prevent unreadable embeds or API"
                " errors."
            ),
            "title",
            (
                "This talk has a very long title that needs to be truncated to fit the"
                " embed that we want to [...]"
            ),
            id="session.title -> embed.title",
        ),
        pytest.param(
            "abstract",
            (
                "In this abstract, I will introduce you to the topic of my talk to"
                " give you an idea of what you'll hear when attending this session. As"
                " noted in the title, my session will give you valuable insights in"
                " keeping your talks succinct and to the point by removing unnecessary "
                " and redundant phrases that just repeat what has already been said in"
                " some other way.\n"
                "In specific, I will help you identify which parts of your presentation"
                " you can skip without removing information that you want to convey to"
                " your audience."
            ),
            "description",
            (
                "In this abstract, I will introduce you to the topic of my talk to"
                " give you an idea of what you'll hear when attending this session. As"
                " noted in the title, my session will give you valuable insights in"
                " keeping your talks succinct and to the point by removing unnecessary"
                " and redundant phrases [...]"
            ),
            id="session.abstract -> embed.description",
        ),
    ],
)
def test_embed_truncates_long_values(
    session_factory: Callable[..., conference.Session],
    session_field: str,
    session_value: str,
    embed_field: str,
    embed_value: str,
) -> None:
    """Defined embed field lengths are respected."""
    # GIVEN a session with a field value that's too long
    session = session_factory(**{session_field: session_value})

    # WHEN an embed is created from that session
    embed = discord.Embed.from_session(session)

    # THEN the associated embed field is truncated
    assert getattr(embed, embed_field) == embed_value


@pytest.mark.parametrize(
    ("speakers", "expected_author"),
    [
        pytest.param([], None, id="No speakers"),
        pytest.param(
            [
                conference.Speaker(
                    name="Ada Lovelace",
                    avatar="https://ada.lovelace.edu/avatar.png",
                ),
            ],
            discord.EmbedAuthor(
                name="Ada Lovelace",
                icon_url="https://ada.lovelace.edu/avatar.png",
            ),
            id="One speaker",
        ),
        pytest.param(
            [
                conference.Speaker(
                    name="Ada Lovelace",
                    avatar="https://ada.lovelace.edu/avatar.png",
                ),
                conference.Speaker(
                    name="Alan Turing",
                    avatar="https://turing.machine/bombe.png",
                ),
            ],
            discord.EmbedAuthor(
                name="Ada Lovelace & Alan Turing",
                icon_url="https://ada.lovelace.edu/avatar.png",
            ),
            id="Two speakers, both with avatar URL",
        ),
        pytest.param(
            [
                conference.Speaker(
                    name="Ada Lovelace",
                    avatar="",
                ),
                conference.Speaker(
                    name="Alan Turing",
                    avatar="https://turing.machine/bombe.png",
                ),
            ],
            discord.EmbedAuthor(
                name="Ada Lovelace & Alan Turing",
                icon_url="https://turing.machine/bombe.png",
            ),
            id="Two speakers, only second has avatar url",
        ),
        pytest.param(
            [
                conference.Speaker(
                    name="Ada Lovelace",
                    avatar="",
                ),
                conference.Speaker(
                    name="Alan Turing",
                    avatar="",
                ),
            ],
            discord.EmbedAuthor(
                name="Ada Lovelace & Alan Turing",
                icon_url=None,
            ),
            id="Two speakers, no avatar url",
        ),
        pytest.param(
            [
                conference.Speaker(
                    name="Ada Lovelace",
                    avatar="",
                ),
                conference.Speaker(
                    name="Alan Turing",
                    avatar="",
                ),
                conference.Speaker(
                    name="Barbara Liskov",
                    avatar="https://barbara.liskov.avatar/",
                ),
            ],
            discord.EmbedAuthor(
                name="Ada Lovelace, Alan Turing, & Barbara Liskov",
                icon_url="https://barbara.liskov.avatar/",
            ),
            id="More than two speakers",
        ),
        pytest.param(
            [
                conference.Speaker(
                    name="Ada Lovelace Ada Lovelace Ada Lovelace Ada Lovelace Ada",
                    avatar="",
                ),
                conference.Speaker(
                    name="Alan Turing Alan Turing Alan Turing Alan Turing Alan Turing",
                    avatar="",
                ),
                conference.Speaker(
                    name="Barbara Liskov Barbara Liskov Barbara Liskov Barbara Liskov",
                    avatar="https://barbara.liskov.avatar/",
                ),
                conference.Speaker(
                    name="Guido van Rossum Guido van Rossum Guido van Rossum Guido",
                    avatar="",
                ),
                conference.Speaker(
                    name="Annie Jean Easley Annie Jean Easley Annie Jean Easley Annie",
                    avatar="",
                ),
            ],
            discord.EmbedAuthor(
                name=(
                    "Ada Lovelace Ada Lovelace Ada Lovelace Ada Lovelace Ada, Alan"
                    " Turing Alan Turing Alan Turing Alan Turing Alan Turing, Barbara"
                    " Liskov Barbara Liskov Barbara Liskov Barbara Liskov, Guido van"
                    " Rossum Guido van Rossum Guido van Rossum Guido, & Annie Jean"
                    " [...]"
                ),
                icon_url="https://barbara.liskov.avatar/",
            ),
            id="Very long combined author name truncated",
        ),
    ],
)
def test_speakers_are_converted_to_single_embed_author(
    session_factory: Callable[..., conference.Session],
    speakers: list[conference.Speaker],
    expected_author: discord.EmbedAuthor | None,
) -> None:
    """Multiple speakers need to be collapsed in one author."""
    # GIVEN a session with multiple speakers
    session = session_factory(speakers=speakers)

    # WHEN an embed is created from that session
    embed = discord.Embed.from_session(session)

    # THEN the speakers are combined in one author
    assert embed.author == expected_author


def test_embed_fields_use_empty_char_if_field_value_is_empty(
    session_factory: Callable[..., conference.Session]
) -> None:
    """Use a user-friendly filler value if no value was provided."""
    # GIVEN a session with empty values for embed field values
    session = session_factory(
        start=arrow.get("2023-07-20T14:05:00+02:00"),
        room=conference.Room(
            name="",
            livestream_url="",
            discord_channel_id=None,
        ),
        duration=0,
        track="",
    )

    # WHEN an embed is created from that session
    embed = discord.Embed.from_session(session=session)

    # THEN the embed field values use a user-friendly empty value
    assert embed.fields == [
        discord.EmbedField(name="Start Time", value="<t:1689854700:f>", inline=True),
        discord.EmbedField(name="Room", value="—", inline=True),
        discord.EmbedField(name="Track", value="—", inline=True),
        discord.EmbedField(name="Length", value="—", inline=True),
        discord.EmbedField(name="Livestream", value="—", inline=True),
        discord.EmbedField(name="Discord Channel", value="—", inline=True),
    ]
