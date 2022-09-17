"""
The purpleair package abstracts working with the purpleair APIs using read/write API keys.
"""
from datetime import datetime, timedelta, timezone
from json import JSONDecodeError
from typing import Optional, Set, Union
from requests import HTTPError, Session, Response
from logging import getLogger
from cachetools import TTLCache, cachedmethod

logger = getLogger(__file__)

V1_API_ENDPOINT = "https://api.purpleair.com/v1/"


class PurpleAir:
    """
    An object to help work with the Purple Air V1 APIs. See https://api.purpleair.com for API info.
    """

    def __init__(
        self,
        read_api_key: str,
        write_api_key: Optional[str] = None,
        verify_api_keys: bool = True,
        ttl: float = 60.0,
    ):
        """
        Initiates a PurpleAir object which will be used to work with the purpleair.com api

        Provide at least the read a read_api_key to perform READ calls.
        If you provide a write_api_key, writes may also be available

        If verify_api_keys is True, will verify that the given api keys are valid by checking them via the API.

        The ttl is the cache time for GET calls. To minimize api load, these requests will cache the result locally
        and only allow calling the API after the ttl elapses (otherwise cached responses are returned)

        """
        self.read_api_key = read_api_key
        self.write_api_key = write_api_key
        self.ttl = ttl

        self._cache = TTLCache(256, ttl=self.ttl)

        self._session = Session()

        if verify_api_keys:
            logger.debug(f"Verifying read api key: {self.read_api_key}")
            key_type = self.check_key(api_key=self.read_api_key)["api_key_type"]
            if key_type != "READ":
                raise ValueError(
                    f"The given read key: {self.read_api_key} was not a READ key. It was a: {key_type}."
                )

            if write_api_key is not None:
                logger.debug(f"Verifying write api key: {self.write_api_key}")
                key_type = self.check_key(api_key=self.write_api_key)["api_key_type"]
                if key_type != "WRITE":
                    raise ValueError(
                        f"The given write key: {self.read_api_key} was not a WRITE key. It was a: {key_type}."
                    )
        else:
            logger.debug("Skipping api key verification")

    def _request(
        self,
        url: str,
        method: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        api_key: Optional[str] = None,
    ) -> Response:
        """
        Performs the given request with the given url. Will use the corresponding API key if this is a READ operation vs a WRITE operation.
        Normally we don't provide api_key here as it will be grabbed from self if needed. If it is given, it will be used instead of pulling from self.
        """
        method = method.upper()

        if api_key is None:
            api_key = self.read_api_key if method == "GET" else self.write_api_key

        if api_key is None:
            raise ValueError("The needed api key is None")

        response = self._session.request(
            method=method,
            url=url,
            data=data,
            params=params,
            headers={"X-API-Key": api_key},
        )

        try:
            response.raise_for_status()
        except HTTPError:
            logger.warning(f"Request failed: {url}\nResponse:{response.json()}")
            raise

        try:
            response.json()
        except JSONDecodeError:
            logger.warning(
                f"The request: {url} did not yield json data. \nContent:{response.content}"
            )
            raise

        return response

    def _to_utc_timestamp(
        self, stamp: Optional[Union[int, datetime, timedelta]] = None
    ) -> Optional[int]:
        """
        Helper method to convert a given mechanism of timestamping to either a utc timestamp int or None (if None was given)
        """
        if isinstance(stamp, datetime):
            stamp = int(stamp.replace(tzinfo=timezone.utc).timestamp())
        elif isinstance(stamp, timedelta):
            stamp = int(
                (datetime.utcnow().replace(tzinfo=timezone.utc) - stamp).timestamp()
            )
        elif not isinstance(stamp, type(None)):
            stamp = int(stamp)

        return stamp

    def _to_timedelta_seconds(self, delta) -> Optional[int]:
        """
        Helper method to convert a given mechanism of timedelta to either a int of seconds or None (if None was given)
        """
        if isinstance(delta, timedelta):
            delta = int(delta.total_seconds())
        elif not isinstance(delta, type(None)):
            delta = int(delta)

        return delta

    def _to_fields_string(
        self, fields: Optional[Union[Set[str], str]]
    ) -> Optional[str]:
        """
        Helper method to convert fields from a set of strs (or a str) to a str (or will return None if None was given)
        """
        return (
            fields if (isinstance(fields, str) or fields is None) else ",".join(fields)
        )

    @cachedmethod(lambda self: self._cache)
    def check_key(self, api_key: str) -> dict:
        """
        Calls the /keys API to get info for the given key
        """
        return self._request(
            url=V1_API_ENDPOINT + "keys", method="GET", api_key=api_key
        ).json()

    @cachedmethod(lambda self: self._cache)
    def get_sensor_data(
        self,
        sensor_index: int,
        fields: Optional[Union[Set[str], str]] = None,
        read_key: Optional[str] = None,
    ) -> dict:
        """
        Calls /sensors/:sensor_index to get data for the given sensor. Optionally you can give either a set of fields to retrieve
        or a comma delim'd string of those fields. If fields is empty, the API seems to return all data available for the given sensor index.

        read_key is required for some sensor_index(es)... see the api docs for more info
        """
        return self._request(
            url=V1_API_ENDPOINT + f"sensors/{sensor_index}",
            method="GET",
            params=dict(
                sensor_index=sensor_index,
                read_key=read_key,
                fields=self._to_fields_string(fields),
            ),
        ).json()

    @cachedmethod(lambda self: self._cache)
    def get_sensor_history(
        self,
        sensor_index: int,
        fields: Union[Set[str], str],
        read_key: Optional[str] = None,
        start_timestamp: Optional[Union[int, datetime, timedelta]] = None,
        end_timestamp: Optional[Union[int, datetime, timedelta]] = None,
        average: Optional[Union[int, timedelta]] = None,
    ):
        """
        Calls /sensors/:sensor_index/history to get data history for the given sensor. You give either a set of fields to retrieve
        or a comma delim'd string of those fields. Use the other parameters to shrink down the amount of data returned.

        start_timestamp/end_timestamp allows for any of the following:
            None - (nothing specified for this param)
            int - Directly matches the api docs for start_timestamp/end_timestamp.. (if you give a float, we'll coerce it to int)
            datetime - A specific tz-naive datetime (in utc time) to be coerced to an int to be sent as start_timestamp/end_timestamp per the api docs
            timedelta - Used to subtract an amount of time from utcnow then coerced to an int to be sent as start_timestamp/end_timestamp
                per the api docs

        average allows for any of the following:
            None - (nothing specified for this param)
            int - Directly matches the api docs for average.. (if you give a float, we'll coerce it to int)
            timedelta - Will be coerced to total seconds and then sent as average per the api docs

        See the API docs for information on the parameters

        Note that you may need to request access to this API from Purple Air for your key to work (otherwise you'd get a 403 with ApiDisabledError)

        This function is currently in alpha and not fully tested.. ( I'm waiting to get my API key approved to test it more :) )
        """
        return self._request(
            url=V1_API_ENDPOINT + f"sensors/{sensor_index}/history",
            method="GET",
            params=dict(
                sensor_index=sensor_index,
                read_key=read_key,
                fields=self._to_fields_string(fields),
                start_timestamp=self._to_utc_timestamp(start_timestamp),
                end_timestamp=self._to_utc_timestamp(end_timestamp),
                average=average,
            ),
        ).json()

    @cachedmethod(lambda self: self._cache)
    def get_sensors_data(
        self,
        fields: Union[Set[str], str],
        read_keys: Optional[str] = None,
        location_type: Optional[int] = None,
        show_only: Optional[str] = None,
        modified_since: Optional[Union[int, datetime, timedelta]] = None,
        max_age: Optional[Union[int, timedelta]] = None,
        nwlng: Optional[float] = None,
        nwlat: Optional[float] = None,
        selng: Optional[float] = None,
        selat: Optional[float] = None,
    ) -> dict:
        """
        Calls /sensors to get data for the given sensors. You give either a set of fields to retrieve
        or a comma delim'd string of those fields. Use the other parameters to shrink down the number of sensors who's data is returned.

        modified_since allows for any of the following:
            None - (nothing specified for this param)
            int - Directly matches the api docs for modified_since.. (if you give a float, we'll coerce it to int)
            datetime - A specific tz-naive datetime (in utc time) to be coerced to an int to be sent as modified_since per the api docs
            timedelta - Used to subtract an amount of time from utcnow then coerced to an int to be sent as modified_since
                per the api docs

        max_age allows for any of the following:
            None - (nothing specified for this param)
            int - Directly matches the api docs for max_age.. (if you give a float, we'll coerce it to int)
            timedelta - Will be coerced to total seconds and then sent as max_age per the api docs

        See the API docs for information on the parameters
        """
        return self._request(
            url=V1_API_ENDPOINT + "sensors",
            method="GET",
            params=dict(
                fields=self._to_fields_string(fields),
                read_keys=read_keys,
                location_type=location_type,
                show_only=show_only,
                modified_since=self._to_utc_timestamp(modified_since),
                max_age=self._to_timedelta_seconds(max_age),
                nwlng=nwlng,
                nwlat=nwlat,
                selng=selng,
                selat=selat,
            ),
        ).json()
