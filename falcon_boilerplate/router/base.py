# pylint:disable=E0611

import json
import logging
from typing import Union

from falcon import App, HTTPBadRequest, HTTPInvalidHeader, HTTPMissingHeader, HTTPUnauthorized
from falcon import status_codes

from falcon_boilerplate.strfunc import proper_slash_it


class BaseRouter:
    base_path = "/"
    version = None
    app: App

    def __init__(self, app: App, logger: Union[logging.Logger, None] = None):
        # Set app instance
        self.app = app

        # Init status codes and common exceptions
        self.status = status_codes
        self.bad_request = HTTPBadRequest
        self.invalid_header = HTTPInvalidHeader
        self.missing_header = HTTPMissingHeader
        self.unauthorized = HTTPUnauthorized

        # Add logger, if applicable
        self.logger = logger

    def add_route(self, path: str, **kwargs):
        """
        add a route to the application
        :param path: str
        the path of the URI that will be added
        :param kwargs: key word arguments for the falcon app 'add_route' method
            the options available are 'suffix' and 'compile'
        """
        _version = f"v{self.version}" if self.version is not None else ""
        _route_path = self._validate_path(f"{self.base_path}/{_version}/{path}")
        if self.logger is not None:
            self.logger.debug(f"adding route {_route_path}")
        self.app.add_route(_route_path, self, **kwargs)

    @staticmethod
    def json(body):
        """
        return json dumped string
        :param body: python object, dictionary, set or list. anything serializable by the json library
        :return: str
        """
        return json.dumps(body)

    @staticmethod
    def _validate_path(path: str):
        """
        internal method to ensure paths are well formatted
        :param path: str
        the path to be validated
        :return: str
        the validated path
        """
        return proper_slash_it(path)

    @staticmethod
    def get_param(key: str, params: dict) -> Union[str, None]:
        """
        get the key from request params, if present
        :param key: str
        :param params: dict
        :return: str
        """
        for k, v in params.items():
            if k.lower() == key.lower():
                return v

        return None
