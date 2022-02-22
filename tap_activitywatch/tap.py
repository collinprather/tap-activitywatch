"""ActivityWatch tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers
from tap_activitywatch.streams import (
    BucketsStream,
    EventsStream,
)


STREAM_TYPES = [
    BucketsStream,
    EventsStream,
]


class TapActivityWatch(Tap):
    """ActivityWatch tap class."""
    name = "tap-activitywatch"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_url",
            th.StringType,
            default="http://localhost:5600/api",
            description="The url for the API service"
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
