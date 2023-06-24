"""Fixtures for the test suite."""
import functools
from collections.abc import Callable
from typing import Any

import arrow
import pytest

from programme_notifier.domain import conference


@pytest.fixture
def session_factory() -> Callable[..., conference.Session]:
    """Get a conference session factory.

    :return: A callable factory to create a `conference.Session`
    """
    defaults = {
        "title": "How to return values from functions",
        "abstract": (
            "Did you ever struggle to get a value out of a function? Did you ever"
            " have to resort to hacks with `global` just to be able to use the result"
            " of a function? Learn how you can do that and more without having to"
            " resort to hacks using Python's `return` statement."
        ),
        "track": "Education, Teaching & Training",
        "start": arrow.get("2023-07-20T14:05:00+02:00"),
        "duration": 30,
        "room": conference.Room(
            name="South Hall 2A",
            livestream_url="https://www.youtube.com/watch?v=k8MT5liCQ7g",
            discord_channel_id=1122150822168502312,
        ),
        "speakers": [
            conference.Speaker(
                name="John Speaker",
                avatar="https://pretalx.com/media/avatars/OMOTOLA_Picture_YdYRpKd.png",
            )
        ],
    }
    return functools.partial(_session_factory, defaults=defaults)


def _session_factory(*, defaults: dict[str, Any], **kwargs: Any) -> conference.Session:
    """Create a Session instance by merging the defaults with kwargs.

    :param defaults: The default values to use
    :param kwargs: The kwargs to use
    :return: A Session instance from the merged attributes
    """
    session_kwargs = defaults | kwargs
    return conference.Session(**session_kwargs)
