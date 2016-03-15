# -*- coding: utf-8 -*-
#
# This file is part of DataCite.
#
# Copyright (C) 2015 CERN.
#
# DataCite is free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Module for making requests to the DataCite MDS API."""

from __future__ import absolute_import, unicode_literals, print_function


import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
import ssl

from ._compat import text_type, string_types
from .errors import HttpError


class DataCiteRequest(object):
    """Helper class for making requests.

    :param base_url: Base URL for all requests.
    :param username: HTTP Basic Authentication Username
    :param password: HTTP Basic Authentication Passsword
    :param default_params: A key/value-mapping which will be converted into a
        query string on all requests.
    :param timeout: Connect and read timeout in seconds. Specify a tuple
        (connect, read) to specify each timeout individually.
    """

    def __init__(self, base_url=None, username=None, password=None,
                 default_params={}, timeout=None):
        """Initialize request object."""
        self.base_url = base_url
        self.username = username
        self.password = password
        self.default_params = default_params
        self.timeout = timeout

    def request(self, url, method='GET', body=None, params={}, headers={}):
        """Make a request.

        If the request was successful (i.e no exceptions), you can find the
        HTTP response code in self.code and the response body in self.value.

        :param url: Request URL (relative to base_url if set)
        :param method: Request method (GET, POST, DELETE) supported
        :param body: Request body
        :param params: Request parameters
        :param headers: Request headers
        """
        self.data = None
        self.code = None

        if self.default_params:
            params.update(self.default_params)

        if self.base_url:
            url = self.base_url + url

        if body and isinstance(body, text_type):
            body = body.encode('utf-8')

        request_func = getattr(requests, method.lower())
        kwargs = dict(
            auth=HTTPBasicAuth(self.username, self.password),
            params=params,
            headers=headers,
        )

        if method == 'POST':
            kwargs['data'] = body
        if self.timeout is not None:
            kwargs['timeout'] = self.timeout

        try:
            res = request_func(url, **kwargs)
            self.code = res.status_code
            self.data = res.content
            if not isinstance(body, string_types):
                self.data = self.data.decode('utf8')
        except RequestException as e:
            raise HttpError(e)
        except ssl.SSLError as e:
            raise HttpError(e)

    def get(self, url, params={}, headers={}):
        """Make a GET request."""
        return self.request(url, params=params, headers=headers)

    def post(self, url, body=None, params={}, headers={}):
        """Make a POST request."""
        return self.request(url, method="POST", body=body, params=params,
                            headers=headers)

    def delete(self, url, params={}, headers={}):
        """Make a DELETE request."""
        return self.request(url, method="DELETE", params=params,
                            headers=headers)