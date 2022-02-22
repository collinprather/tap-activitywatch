"""Stream type classes for tap-activitywatch."""

# from pathlib import Path
from typing import Optional, Any, Dict

from singer_sdk import typing as th  # JSON Schema typing helpers
from singer_sdk.streams import RESTStream


class ActivityWatchStream(RESTStream):
    """ActivityWatch stream class."""

    records_jsonpath = "$[*]"

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config["api_url"]


class BucketsStream(ActivityWatchStream):
    """Define custom stream."""
    name = "buckets"
    path = "/0/buckets"
    records_jsonpath = "$.*"
    primary_keys = ["id"]
    replication_key = None
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("created", th.DateTimeType),
        th.Property("name", th.StringType),
        th.Property("type", th.StringType),
        th.Property("client", th.StringType),
        th.Property("hostname", th.StringType),
        th.Property("last_updated", th.DateTimeType),
    ).to_dict()

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        context = {"bucket_id": record["id"]}
        return context


class EventsStream(ActivityWatchStream):
    """Define custom stream."""
    name = "events"
    path = "/0/buckets/{bucket_id}/events"
    primary_keys = ["id"]
    replication_key = "timestamp"
    parent_stream_type = BucketsStream
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("bucket_id", th.StringType),
        th.Property("timestamp", th.DateTimeType),
        th.Property("duration", th.NumberType),
        th.Property("data", th.ObjectType()),
    ).to_dict()

    def get_url(self, context: Optional[dict]) -> str:
        url = self.url_base + self.path.format(bucket_id=context["bucket_id"])
        return url

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: Stream partition or context dictionary.
            next_page_token: Token, page number or any request argument to request the
                next page of data.

        Returns:
            Dictionary of URL query parameters to use in the request.
        """
        params: dict = {"start": self.get_starting_timestamp(context)}
        return params

    def post_process(self, row: dict, context: Optional[dict] = None) -> Optional[dict]:
        row["bucket_id"] = context["bucket_id"]
        return row
