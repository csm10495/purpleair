"""
The purpleair package abstracts working with the purpleair APIs using read/write API keys.
"""
from json import JSONDecodeError
from typing import Optional, List, Union
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
        fields: Optional[Union[List[str], str]] = None,
        read_key: Optional[str] = None,
    ) -> dict:
        """
        Calls /sensors/:sensor_index to get data for the given sensor. Optionally you can give either a list of fields to retrieve
        or a comma delim'd string of those fields. If fields is empty, the API seems to return all data available for the given sensor index.

        read_key is required for some sensor_index(es)... see the api docs for more info
        """
        fields_to_send = (
            fields if (isinstance(fields, str) or fields is None) else ",".join(fields)
        )

        return self._request(
            url=V1_API_ENDPOINT + f"sensors/{sensor_index}",
            method="GET",
            params=dict(
                sensor_index=sensor_index,
                read_key=read_key,
                fields=fields_to_send,
            ),
        ).json()

    @cachedmethod(lambda self: self._cache)
    def get_sensors_data(
        self,
        fields: Union[List[str], str],
        read_keys: Optional[str] = None,
        location_type: Optional[int] = None,
        show_only: Optional[str] = None,
        modified_since: Optional[int] = None,
        max_age: Optional[int] = None,
        nwlng: Optional[float] = None,
        nwlat: Optional[float] = None,
        selng: Optional[float] = None,
        selat: Optional[float] = None,
    ) -> dict:
        """
        Calls /sensors to get data for the given sensors. You give either a list of fields to retrieve
        or a comma delim'd string of those fields. Use the other parameters to shrink down the number of sensors who's data is returned.

        See the API docs for information on the parameters
        """
        fields_to_send = (
            fields if (isinstance(fields, str) or fields is None) else ",".join(fields)
        )

        return self._request(
            url=V1_API_ENDPOINT + "sensors",
            method="GET",
            params=dict(
                fields=fields_to_send,
                read_keys=read_keys,
                location_type=location_type,
                show_only=show_only,
                modified_since=modified_since,
                max_age=max_age,
                nwlng=nwlng,
                nwlat=nwlat,
                selng=selng,
                selat=selat,
            ),
        ).json()
